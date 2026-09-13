from collections.abc import Callable
from dataclasses import dataclass, replace
from typing import TypeVar, cast

import pytest

from climatesos.pathway_evaluation import (
    ComparisonFinding,
    ContributionFinding,
    DocumentationFinding,
    FabricEvaluatorResult,
    NetOverallSystemContribution,
    PathwayEngineResult,
    PathwayObject,
    ProductPathway,
    QueueEvaluatorResult,
    ScaleDiagnosticEvaluationInvariantError,
    ScaleDiagnosticResult,
    ScaleFinding,
    TransitionPathway,
    ValidatedScaleDiagnosticEvaluator,
)

T = TypeVar("T")


def _record(record_type: type[T], **values: object) -> T:
    record = object.__new__(record_type)
    for name, value in values.items():
        object.__setattr__(record, name, value)
    return record


@dataclass(frozen=True)
class _Context:
    contribution: NetOverallSystemContribution
    product_pathway: ProductPathway
    transition_pathway: TransitionPathway
    contribution_finding: ContributionFinding
    pathway_output: PathwayObject
    comparison_finding: ComparisonFinding
    queue_result: QueueEvaluatorResult
    fabric_result: FabricEvaluatorResult
    documentation_finding: DocumentationFinding


def _context() -> _Context:
    pathway_output = _record(PathwayObject)
    comparison_finding = _record(ComparisonFinding)
    queue_result = _record(QueueEvaluatorResult)
    fabric_result = _record(FabricEvaluatorResult)
    documentation_finding = _record(DocumentationFinding)
    contribution_finding = ContributionFinding(
        finding_id="contribution-1",
        effect_description="Supported system contribution",
        supporting_queue_results=(queue_result,),
    )
    product_pathway = _record(
        ProductPathway,
        evaluation_run_id="run-1",
        user_id="user-1",
        pathway_id="pathway-1",
        objects=(pathway_output,),
    )
    transition_pathway = _record(TransitionPathway)
    pathway_engine_result = _record(
        PathwayEngineResult,
        direct_comparison_findings=(comparison_finding,),
        substitution_combination_findings=(),
        downstream_propagation_findings=(),
        queue_results=(queue_result,),
        fabric_results=(fabric_result,),
        documentation_findings=(documentation_finding,),
    )
    contribution = _record(
        NetOverallSystemContribution,
        product_pathway=product_pathway,
        transition_pathway=transition_pathway,
        pathway_engine_result=pathway_engine_result,
        contribution_findings=(contribution_finding,),
        evaluation_run_id="run-1",
        user_id="user-1",
        pathway_id="pathway-1",
    )
    return _Context(
        contribution=contribution,
        product_pathway=product_pathway,
        transition_pathway=transition_pathway,
        contribution_finding=contribution_finding,
        pathway_output=pathway_output,
        comparison_finding=comparison_finding,
        queue_result=queue_result,
        fabric_result=fabric_result,
        documentation_finding=documentation_finding,
    )


def _result(
    context: _Context,
    findings: tuple[ScaleFinding, ...] = (),
) -> ScaleDiagnosticResult:
    return ScaleDiagnosticResult(
        product_pathway=context.product_pathway,
        net_overall_system_contribution=context.contribution,
        transition_pathway=context.transition_pathway,
        scale_findings=findings,
        evaluation_run_id="run-1",
        user_id="user-1",
        pathway_id="pathway-1",
        evaluator_version="scale-test-v1",
        rule_set_version="rules-test-v1",
    )


def _evaluate(
    context: _Context,
    function: Callable[..., object],
    *,
    product_pathway: ProductPathway | None = None,
    transition_pathway: TransitionPathway | None = None,
    user_id: str = "user-1",
    pathway_id: str = "pathway-1",
    evaluation_run_id: str = "run-1",
) -> ScaleDiagnosticResult:
    evaluator = ValidatedScaleDiagnosticEvaluator(function)
    return evaluator.evaluate(
        context.contribution,
        product_pathway or context.product_pathway,
        transition_pathway or context.transition_pathway,
        None,
        (),
        (),
        (),
        (),
        user_id,
        pathway_id,
        evaluation_run_id,
    )


def test_valid_inputs_execute_once_and_preserve_exact_upstream_artifacts() -> None:
    context = _context()
    expected = _result(context)
    calls = 0

    def scale_function(*args: object) -> object:
        nonlocal calls
        calls += 1
        assert args[:3] == (
            context.contribution,
            context.product_pathway,
            context.transition_pathway,
        )
        return expected

    actual = _evaluate(context, scale_function)

    assert calls == 1
    assert actual is expected
    assert actual.product_pathway is context.product_pathway
    assert actual.net_overall_system_contribution is context.contribution
    assert actual.transition_pathway is context.transition_pathway


@pytest.mark.parametrize(
    ("overrides", "replacement"),
    [
        ({"evaluation_run_id": "other-run"}, None),
        ({"user_id": "other-user"}, None),
        ({"pathway_id": "other-pathway"}, None),
        ({}, "product"),
        ({}, "transition"),
    ],
)
def test_input_context_mismatches_reject_before_execution(
    overrides: dict[str, str],
    replacement: str | None,
) -> None:
    context = _context()
    calls = 0

    def scale_function(*args: object) -> object:
        nonlocal calls
        calls += 1
        return _result(context)

    product_pathway = (
        _record(
            ProductPathway,
            evaluation_run_id="run-1",
            user_id="user-1",
            pathway_id="pathway-1",
            objects=(),
        )
        if replacement == "product"
        else None
    )
    transition_pathway = (
        _record(TransitionPathway) if replacement == "transition" else None
    )

    with pytest.raises(ScaleDiagnosticEvaluationInvariantError):
        _evaluate(
            context,
            scale_function,
            product_pathway=product_pathway,
            transition_pathway=transition_pathway,
            **overrides,
        )

    assert calls == 0


def test_non_scale_result_rejects() -> None:
    context = _context()

    with pytest.raises(ScaleDiagnosticEvaluationInvariantError):
        _evaluate(context, lambda *args: object())


@pytest.mark.parametrize(
    ("field", "replacement"),
    [
        ("product_pathway", _record(ProductPathway)),
        (
            "net_overall_system_contribution",
            _record(NetOverallSystemContribution),
        ),
        ("transition_pathway", _record(TransitionPathway)),
        ("evaluation_run_id", "other-run"),
        ("user_id", "other-user"),
        ("pathway_id", "other-pathway"),
    ],
)
def test_returned_reference_and_attribution_mismatches_reject(
    field: str,
    replacement: object,
) -> None:
    context = _context()
    invalid = _result(context)
    object.__setattr__(invalid, field, replacement)

    with pytest.raises(ScaleDiagnosticEvaluationInvariantError):
        _evaluate(context, lambda *args: invalid)


@pytest.mark.parametrize("support_kind", ["contribution", "queue"])
def test_equal_or_reconstructed_material_support_rejects(
    support_kind: str,
) -> None:
    context = _context()
    if support_kind == "contribution":
        finding = ScaleFinding(
            "scale-1",
            "Reconstructed contribution support",
            contribution_findings=(replace(context.contribution_finding),),
        )
    else:
        finding = ScaleFinding(
            "scale-1",
            "Reconstructed queue support",
            supporting_queue_results=(_record(QueueEvaluatorResult),),
        )

    with pytest.raises(ScaleDiagnosticEvaluationInvariantError):
        _evaluate(context, lambda *args: _result(context, (finding,)))


def test_actual_material_support_records_are_accepted() -> None:
    context = _context()
    finding = ScaleFinding(
        "scale-1",
        "Traceable scale support",
        contribution_findings=(context.contribution_finding,),
        supporting_pathway_outputs=(context.pathway_output,),
        supporting_comparison_findings=(context.comparison_finding,),
        supporting_queue_results=(context.queue_result,),
        supporting_fabric_results=(context.fabric_result,),
        supporting_documentation_findings=(context.documentation_finding,),
    )
    expected = _result(context, (finding,))

    assert _evaluate(context, lambda *args: expected) is expected


def test_findings_may_use_different_support_subsets() -> None:
    context = _context()
    findings = (
        ScaleFinding(
            "scale-1",
            "Contribution-specific support",
            contribution_findings=(context.contribution_finding,),
        ),
        ScaleFinding(
            "scale-2",
            "Queue-specific support",
            supporting_queue_results=(context.queue_result,),
        ),
    )
    expected = _result(context, findings)

    assert _evaluate(context, lambda *args: expected) is expected


def test_scale_finding_need_not_inherit_contribution_finding_support() -> None:
    context = _context()
    assert context.contribution_finding.supporting_queue_results == (
        context.queue_result,
    )
    finding = ScaleFinding(
        "scale-1",
        "Contribution support without transitive closure",
        contribution_findings=(context.contribution_finding,),
    )
    expected = _result(context, (finding,))

    assert _evaluate(context, lambda *args: expected) is expected


def test_substantive_adverse_and_unresolved_findings_are_valid_results() -> None:
    context = _context()
    finding = ScaleFinding(
        "scale-1",
        "Local success is stale and broader scale remains unresolved",
        finding_type="limited-local-contribution",
        statuses=("stale-success", "constrained-scale"),
        bottlenecks=("deployment bottleneck",),
        unresolved_conditions=("broader replication is unresolved",),
    )
    expected = _result(context, (finding,))

    assert _evaluate(context, lambda *args: expected) is expected


def test_underlying_function_exception_propagates_unchanged() -> None:
    context = _context()
    failure = RuntimeError("scale function failed")

    def scale_function(*args: object) -> object:
        raise failure

    with pytest.raises(RuntimeError) as caught:
        _evaluate(context, scale_function)

    assert caught.value is failure


def test_validated_evaluator_is_immutable() -> None:
    context = _context()
    evaluator = ValidatedScaleDiagnosticEvaluator(
        cast(Callable[..., object], lambda *args: _result(context))
    )

    with pytest.raises((AttributeError, TypeError)):
        evaluator.scale_diagnostic_function = lambda *args: object()  # type: ignore[misc]
