from dataclasses import dataclass, replace
from typing import TypeVar, cast

import pytest

from climatesos.pathway_evaluation import (
    ComparisonFinding,
    ContributionFinding,
    DocumentationFinding,
    FabricEvaluatorResult,
    NetOverallSystemContribution,
    OpaqueReference,
    PathwayEngineResult,
    PathwayObject,
    ProductPathway,
    QueueEvaluatorResult,
    ScaleDiagnosticEvaluationInvariantError,
    ScaleDiagnosticEvaluator,
    ScaleDiagnosticFindingFunction,
    ScaleDiagnosticResult,
    ScaleFinding,
    SourceReference,
    TransitionPathway,
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
    system_context: OpaqueReference
    evidence: SourceReference
    provenance: SourceReference


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
        system_context=OpaqueReference("system-1"),
        evidence=SourceReference("evidence-1"),
        provenance=SourceReference("provenance-1"),
    )


class _RecordingRule:
    def __init__(self, output: object = ()) -> None:
        self.output = output
        self.calls: list[tuple[object, ...]] = []

    def __call__(self, *args: object) -> object:
        self.calls.append(args)
        return self.output


@dataclass(frozen=True)
class _RuleSet:
    material: _RecordingRule
    dimensions: _RecordingRule
    progression: _RecordingRule
    timing: _RecordingRule
    constraints: _RecordingRule
    response: _RecordingRule
    effects: _RecordingRule
    limited: _RecordingRule
    stale: _RecordingRule
    unresolved: _RecordingRule

    @property
    def all(self) -> tuple[_RecordingRule, ...]:
        return (
            self.material,
            self.dimensions,
            self.progression,
            self.timing,
            self.constraints,
            self.response,
            self.effects,
            self.limited,
            self.stale,
            self.unresolved,
        )


def _evaluator(
    *,
    material: object = (),
    dimensions: object = (),
    progression: object = (),
    timing: object = (),
    constraints: object = (),
    response: object = (),
    effects: object = (),
    limited: object = (),
    stale: object = (),
    unresolved: object = (),
) -> tuple[ScaleDiagnosticEvaluator, _RuleSet]:
    rules = _RuleSet(
        material=_RecordingRule(material),
        dimensions=_RecordingRule(dimensions),
        progression=_RecordingRule(progression),
        timing=_RecordingRule(timing),
        constraints=_RecordingRule(constraints),
        response=_RecordingRule(response),
        effects=_RecordingRule(effects),
        limited=_RecordingRule(limited),
        stale=_RecordingRule(stale),
        unresolved=_RecordingRule(unresolved),
    )
    evaluator = ScaleDiagnosticEvaluator(
        material_scale_function=cast(ScaleDiagnosticFindingFunction, rules.material),
        scale_dimensions_function=cast(
            ScaleDiagnosticFindingFunction, rules.dimensions
        ),
        scale_progression_function=cast(
            ScaleDiagnosticFindingFunction,
            rules.progression,
        ),
        timing_sequencing_function=cast(ScaleDiagnosticFindingFunction, rules.timing),
        constraint_bottleneck_function=cast(
            ScaleDiagnosticFindingFunction,
            rules.constraints,
        ),
        response_condition_function=cast(
            ScaleDiagnosticFindingFunction, rules.response
        ),
        scale_dependent_effect_function=cast(
            ScaleDiagnosticFindingFunction,
            rules.effects,
        ),
        limited_local_function=cast(ScaleDiagnosticFindingFunction, rules.limited),
        stale_success_function=cast(ScaleDiagnosticFindingFunction, rules.stale),
        unresolved_scale_function=cast(
            ScaleDiagnosticFindingFunction,
            rules.unresolved,
        ),
        evaluator_version="scale-test-v1",
        rule_set_version="rules-test-v1",
    )
    return evaluator, rules


def _evaluate(
    context: _Context,
    evaluator: ScaleDiagnosticEvaluator,
    *,
    product_pathway: ProductPathway | None = None,
    transition_pathway: TransitionPathway | None = None,
    user_id: str = "user-1",
    pathway_id: str = "pathway-1",
    evaluation_run_id: str = "run-1",
) -> ScaleDiagnosticResult:
    return evaluator.evaluate(
        context.contribution,
        product_pathway or context.product_pathway,
        transition_pathway or context.transition_pathway,
        context.system_context,
        ("scale assumption",),
        ("scale uncertainty",),
        (context.evidence,),
        (context.provenance,),
        user_id,
        pathway_id,
        evaluation_run_id,
    )


def test_evaluator_constructs_result_and_preserves_exact_upstream_artifacts() -> None:
    context = _context()
    evaluator, rules = _evaluator()

    actual = _evaluate(context, evaluator)

    assert actual.product_pathway is context.product_pathway
    assert actual.net_overall_system_contribution is context.contribution
    assert actual.transition_pathway is context.transition_pathway
    assert actual.scale_findings == ()
    assert actual.evaluation_run_id == "run-1"
    assert actual.user_id == "user-1"
    assert actual.pathway_id == "pathway-1"
    assert actual.evaluator_version == "scale-test-v1"
    assert actual.rule_set_version == "rules-test-v1"
    assert actual.assumptions == ("scale assumption",)
    assert actual.uncertainties == ("scale uncertainty",)
    assert actual.evidence_references == (context.evidence,)
    assert actual.provenance == (context.provenance,)
    assert all(len(rule.calls) == 1 for rule in rules.all)


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
def test_input_context_mismatches_reject_before_scale_checks(
    overrides: dict[str, str],
    replacement: str | None,
) -> None:
    context = _context()
    evaluator, rules = _evaluator()

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
            evaluator,
            product_pathway=product_pathway,
            transition_pathway=transition_pathway,
            **overrides,
        )

    assert all(rule.calls == [] for rule in rules.all)


@pytest.mark.parametrize(
    "domain",
    (
        "material",
        "dimensions",
        "progression",
        "timing",
        "constraints",
        "response",
        "effects",
        "limited",
        "stale",
        "unresolved",
    ),
)
def test_each_scale_check_requires_tuple_of_scale_findings(domain: str) -> None:
    context = _context()
    kwargs = {domain: ("not-a-scale-finding",)}
    evaluator, _ = _evaluator(**kwargs)

    with pytest.raises(ScaleDiagnosticEvaluationInvariantError):
        _evaluate(context, evaluator)


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

    evaluator, _ = _evaluator(material=(finding,))

    with pytest.raises(ScaleDiagnosticEvaluationInvariantError):
        _evaluate(context, evaluator)


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
    evaluator, _ = _evaluator(material=(finding,))

    result = _evaluate(context, evaluator)

    assert result.scale_findings == (finding,)
    assert result.scale_findings[0] is finding


def test_findings_may_use_different_support_subsets() -> None:
    context = _context()
    contribution_only = ScaleFinding(
        "scale-1",
        "Contribution-specific support",
        contribution_findings=(context.contribution_finding,),
    )
    queue_only = ScaleFinding(
        "scale-2",
        "Queue-specific support",
        supporting_queue_results=(context.queue_result,),
    )
    evaluator, _ = _evaluator(
        material=(contribution_only,),
        constraints=(queue_only,),
    )

    result = _evaluate(context, evaluator)

    assert result.scale_findings == (contribution_only, queue_only)
    assert result.scale_findings[0] is contribution_only
    assert result.scale_findings[1] is queue_only


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
    evaluator, _ = _evaluator(material=(finding,))

    result = _evaluate(context, evaluator)

    assert result.scale_findings == (finding,)
    assert finding.supporting_queue_results == ()


def test_substantive_adverse_and_unresolved_findings_are_valid() -> None:
    context = _context()
    finding = ScaleFinding(
        "scale-1",
        "Local success is stale and broader scale remains unresolved",
        finding_type="limited-local-contribution",
        statuses=("stale-success", "constrained-scale"),
        bottlenecks=("deployment bottleneck",),
        unresolved_conditions=("broader replication is unresolved",),
    )
    evaluator, _ = _evaluator(unresolved=(finding,))

    result = _evaluate(context, evaluator)

    assert result.scale_findings == (finding,)


def test_check_exception_propagates_without_becoming_a_scale_finding() -> None:
    context = _context()
    failure = RuntimeError("scale check failed")

    def fail(*_args: object) -> tuple[ScaleFinding, ...]:
        raise failure

    evaluator, _ = _evaluator()
    object.__setattr__(
        evaluator,
        "material_scale_function",
        cast(ScaleDiagnosticFindingFunction, fail),
    )

    with pytest.raises(RuntimeError) as caught:
        _evaluate(context, evaluator)

    assert caught.value is failure


def test_evaluator_is_immutable() -> None:
    evaluator, _ = _evaluator()

    with pytest.raises((AttributeError, TypeError)):
        evaluator.evaluator_version = "changed"  # type: ignore[misc]


def test_evaluator_introduces_no_downstream_or_scalar_semantics() -> None:
    evaluator_fields = set(ScaleDiagnosticEvaluator.__dataclass_fields__)

    assert {
        "score",
        "rank",
        "ranking",
        "weight",
        "vote",
        "voting",
        "candidate_transition_pathway",
        "net_overall_system_risk",
    }.isdisjoint(evaluator_fields)
