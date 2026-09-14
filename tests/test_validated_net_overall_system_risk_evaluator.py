from collections.abc import Callable
from dataclasses import FrozenInstanceError, fields, replace
from typing import TypeVar

import pytest

from climatesos.pathway_evaluation import (
    ContributionFinding,
    IdentityToken,
    IntegratedCharterResult,
    NetOverallSystemContribution,
    NetOverallSystemRiskEvaluationInvariantError,
    NetOverallSystemRiskResult,
    OpaqueReference,
    PathwayEngineResult,
    PathwayRelationship,
    ProductPathway,
    ScaleDiagnosticResult,
    ScaleFinding,
    SourceReference,
    SystemRiskFinding,
    TransitionPathway,
    ValidatedNetOverallSystemRiskEvaluator,
)

T = TypeVar("T")


def _record(record_type: type[T], **values: object) -> T:
    record = object.__new__(record_type)
    for name, value in values.items():
        object.__setattr__(record, name, value)
    return record


class _Context:
    def __init__(self) -> None:
        self.identity_token = _record(IdentityToken, token_id="lineage-1")
        self.product_pathway = _record(
            ProductPathway,
            identity_token=self.identity_token,
            evaluation_run_id="run-1",
            user_id="user-1",
            pathway_id="pathway-1",
        )
        self.authoritative = TransitionPathway(
            reference_id="authoritative",
            identity_token=_record(IdentityToken, token_id="older-lineage"),
            evaluation_run_id="older-run",
            user_id="global-user",
            pathway_id="global-pathway",
        )
        self.contribution_finding = ContributionFinding(
            finding_id="contribution-1",
            effect_description="Supported contribution",
        )
        engine_result = _record(
            PathwayEngineResult,
            identity_token=self.identity_token,
        )
        self.contribution = NetOverallSystemContribution(
            product_pathway=self.product_pathway,
            pathway_engine_result=engine_result,
            integrated_charter_result=_record(IntegratedCharterResult),
            transition_pathway=self.authoritative,
            contribution_findings=(self.contribution_finding,),
            evaluation_run_id="run-1",
            user_id="user-1",
            pathway_id="pathway-1",
            evaluator_version="contribution-v1",
            rule_set_version="contribution-rules-v1",
        )
        self.scale_finding = ScaleFinding(
            finding_id="scale-1",
            description="Supported scale condition",
        )
        self.scale_result = ScaleDiagnosticResult(
            product_pathway=self.product_pathway,
            net_overall_system_contribution=self.contribution,
            transition_pathway=self.authoritative,
            scale_findings=(self.scale_finding,),
            evaluation_run_id="run-1",
            user_id="user-1",
            pathway_id="pathway-1",
            evaluator_version="scale-v1",
            rule_set_version="scale-rules-v1",
        )
        self.relationship = _record(PathwayRelationship)
        self.dependency = _record(OpaqueReference)
        self.evidence = _record(SourceReference)
        self.provenance = _record(SourceReference)
        self.candidate = TransitionPathway(
            reference_id="candidate",
            provenance=(self.provenance,),
            identity_token=self.identity_token,
            evaluation_run_id="run-1",
            user_id="user-1",
            pathway_id="pathway-1",
            authoritative_transition_pathway=self.authoritative,
            product_pathway=self.product_pathway,
            net_overall_system_contribution=self.contribution,
            scale_diagnostic_result=self.scale_result,
            affected_relationships=(self.relationship,),
            dependencies=(self.dependency,),
            conditions=("candidate condition",),
            unresolved_conditions=("candidate uncertainty",),
            evidence_references=(self.evidence,),
            compiler_version="compiler-v1",
            model_version="transition-v1",
            rule_set_version="compiler-rules-v1",
        )

    def finding(self, **overrides: object) -> SystemRiskFinding:
        values: dict[str, object] = {
            "finding_id": "risk-1",
            "description": "Completed adverse and unresolved risk",
            "risk_states": ("increased", "unresolved"),
            "transition_relationships": (self.relationship,),
            "propagation_relationships": (self.relationship,),
            "supporting_contribution_findings": (self.contribution_finding,),
            "supporting_scale_findings": (self.scale_finding,),
            "supporting_system_references": (self.dependency,),
            "evidence_references": (self.evidence,),
            "provenance": (self.provenance,),
        }
        values.update(overrides)
        return SystemRiskFinding(**values)  # type: ignore[arg-type]

    def result(self, **overrides: object) -> NetOverallSystemRiskResult:
        values: dict[str, object] = {
            "candidate_transition_pathway": self.candidate,
            "authoritative_transition_pathway": self.authoritative,
            "risk_findings": (self.finding(),),
            "evaluation_run_id": "run-1",
            "user_id": "user-1",
            "pathway_id": "pathway-1",
            "evaluator_version": "risk-v1",
            "rule_set_version": "risk-rules-v1",
            "assumptions": ("risk assumption",),
            "uncertainties": ("risk uncertainty",),
            "evidence_references": (self.evidence,),
            "provenance": (self.provenance,),
        }
        values.update(overrides)
        return NetOverallSystemRiskResult(**values)  # type: ignore[arg-type]


def _evaluate(
    context: _Context,
    function: Callable[..., object],
    *,
    candidate: TransitionPathway | None = None,
    authoritative: TransitionPathway | None = None,
    evaluation_run_id: str = "run-1",
    user_id: str = "user-1",
    pathway_id: str = "pathway-1",
) -> NetOverallSystemRiskResult:
    return ValidatedNetOverallSystemRiskEvaluator(function).evaluate(
        candidate or context.candidate,
        authoritative or context.authoritative,
        None,
        None,
        ("risk assumption",),
        ("risk uncertainty",),
        (context.evidence,),
        (context.provenance,),
        user_id,
        pathway_id,
        evaluation_run_id,
    )


def test_valid_inputs_invoke_once_and_preserve_exact_upstream_context() -> None:
    context = _Context()
    expected = context.result()
    calls = 0

    def risk_function(*args: object) -> object:
        nonlocal calls
        calls += 1
        assert args[0] is context.candidate
        assert args[1] is context.authoritative
        return expected

    result = _evaluate(context, risk_function)

    assert calls == 1
    assert result is expected
    assert result.candidate_transition_pathway is context.candidate
    assert result.authoritative_transition_pathway is context.authoritative
    assert context.candidate.product_pathway is context.product_pathway
    assert context.candidate.net_overall_system_contribution is context.contribution
    assert context.candidate.scale_diagnostic_result is context.scale_result
    assert result.evaluation_run_id == "run-1"
    assert result.user_id == "user-1"
    assert result.pathway_id == "pathway-1"


def test_authoritative_pathway_may_retain_older_lineage_and_run() -> None:
    context = _Context()

    assert context.authoritative.identity_token is not context.identity_token
    assert context.authoritative.evaluation_run_id == "older-run"
    assert _evaluate(context, lambda *args: context.result()).risk_findings


@pytest.mark.parametrize(
    ("field", "replacement_factory"),
    [
        ("candidate_transition_pathway", lambda: TransitionPathway("candidate")),
        (
            "authoritative_transition_pathway",
            lambda: TransitionPathway("authoritative"),
        ),
    ],
)
def test_reconstructed_result_upstream_references_reject(
    field: str,
    replacement_factory: Callable[[], object],
) -> None:
    context = _Context()
    invalid = context.result(**{field: replacement_factory()})

    with pytest.raises(NetOverallSystemRiskEvaluationInvariantError):
        _evaluate(context, lambda *args: invalid)


@pytest.mark.parametrize(
    ("candidate_field", "replacement_factory"),
    [
        ("product_pathway", lambda: _record(ProductPathway)),
        (
            "net_overall_system_contribution",
            lambda: _record(NetOverallSystemContribution),
        ),
        ("scale_diagnostic_result", lambda: _record(ScaleDiagnosticResult)),
        (
            "authoritative_transition_pathway",
            lambda: TransitionPathway("authoritative"),
        ),
    ],
)
def test_reconstructed_candidate_upstream_references_reject_before_execution(
    candidate_field: str,
    replacement_factory: Callable[[], object],
) -> None:
    context = _Context()
    candidate = replace(context.candidate)
    if candidate_field == "net_overall_system_contribution":
        replacement_value: object = replace(context.contribution)
    elif candidate_field == "scale_diagnostic_result":
        replacement_value = replace(
            context.scale_result,
            net_overall_system_contribution=replace(context.contribution),
        )
    else:
        replacement_value = replacement_factory()
    object.__setattr__(candidate, candidate_field, replacement_value)
    calls = 0

    def risk_function(*args: object) -> object:
        nonlocal calls
        calls += 1
        return context.result()

    with pytest.raises(NetOverallSystemRiskEvaluationInvariantError):
        _evaluate(context, risk_function, candidate=candidate)

    assert calls == 0


@pytest.mark.parametrize(
    ("attribute", "value"),
    [
        ("evaluation_run_id", "other-run"),
        ("user_id", "other-user"),
        ("pathway_id", "other-pathway"),
    ],
)
def test_input_attribution_mismatches_reject_before_execution(
    attribute: str,
    value: str,
) -> None:
    context = _Context()
    calls = 0

    def risk_function(*args: object) -> object:
        nonlocal calls
        calls += 1
        return context.result()

    with pytest.raises(NetOverallSystemRiskEvaluationInvariantError):
        if attribute == "evaluation_run_id":
            _evaluate(context, risk_function, evaluation_run_id=value)
        elif attribute == "user_id":
            _evaluate(context, risk_function, user_id=value)
        else:
            _evaluate(context, risk_function, pathway_id=value)

    assert calls == 0


def test_incorrect_current_lineage_rejects_before_execution() -> None:
    context = _Context()
    candidate = replace(
        context.candidate,
        identity_token=_record(IdentityToken, token_id="other-lineage"),
    )
    calls = 0

    def risk_function(*args: object) -> object:
        nonlocal calls
        calls += 1
        return context.result()

    with pytest.raises(NetOverallSystemRiskEvaluationInvariantError):
        _evaluate(context, risk_function, candidate=candidate)

    assert calls == 0


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("evaluation_run_id", "other-run"),
        ("user_id", "other-user"),
        ("pathway_id", "other-pathway"),
    ],
)
def test_result_attribution_mismatches_reject(field: str, value: object) -> None:
    context = _Context()
    invalid = context.result(**{field: value})

    with pytest.raises(NetOverallSystemRiskEvaluationInvariantError):
        _evaluate(context, lambda *args: invalid)


def test_non_risk_result_return_rejects() -> None:
    context = _Context()

    with pytest.raises(NetOverallSystemRiskEvaluationInvariantError):
        _evaluate(context, lambda *args: object())


def test_invalid_finding_element_type_rejects() -> None:
    context = _Context()
    invalid = context.result(risk_findings=(object(),))

    with pytest.raises(NetOverallSystemRiskEvaluationInvariantError):
        _evaluate(context, lambda *args: invalid)


@pytest.mark.parametrize("support_kind", ["type", "contribution", "scale"])
def test_invalid_finding_material_support_rejects(support_kind: str) -> None:
    context = _Context()
    if support_kind == "type":
        finding = context.finding(
            supporting_contribution_findings=(object(),),
        )
    elif support_kind == "contribution":
        finding = context.finding(
            supporting_contribution_findings=(
                replace(context.contribution_finding),
            ),
        )
    else:
        finding = context.finding(
            supporting_scale_findings=(replace(context.scale_finding),),
        )
    invalid = context.result(risk_findings=(finding,))

    with pytest.raises(NetOverallSystemRiskEvaluationInvariantError):
        _evaluate(context, lambda *args: invalid)


def test_evaluator_exception_propagates_unchanged() -> None:
    context = _Context()
    failure = RuntimeError("risk evaluator failed")

    def risk_function(*args: object) -> object:
        raise failure

    with pytest.raises(RuntimeError) as caught:
        _evaluate(context, risk_function)

    assert caught.value is failure


def test_validated_evaluator_is_immutable() -> None:
    context = _Context()
    evaluator = ValidatedNetOverallSystemRiskEvaluator(
        lambda *args: context.result()
    )

    with pytest.raises(FrozenInstanceError):
        evaluator.risk_evaluation_function = lambda *args: object()  # type: ignore[misc]


def test_boundary_adds_no_downstream_or_scalar_operations() -> None:
    field_names = {
        field.name for field in fields(ValidatedNetOverallSystemRiskEvaluator)
    }

    assert field_names == {"risk_evaluation_function"}
    forbidden = (
        "final_assembly",
        "authoritative_promotion",
        "validator",
        "binding",
        "score",
        "rank",
        "weight",
        "vote",
        "optimization",
        "scalar_aggregation",
    )
    assert all(
        not hasattr(ValidatedNetOverallSystemRiskEvaluator, name)
        for name in forbidden
    )
