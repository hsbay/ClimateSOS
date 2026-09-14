import inspect
from dataclasses import dataclass
from typing import Any

from climatesos.pathway_evaluation import (
    CompleteFinalPathwayAssemblyFunction,
    FinalPathwayResult,
    IdentityToken,
    InitialCharterResult,
    IntegratedCharterResult,
    NetOverallSystemContribution,
    NetOverallSystemRiskResult,
    PathwayEngineResult,
    ProductAdapterResult,
    ProductPathway,
    ScaleDiagnosticResult,
    SystemRiskFinding,
    TransitionPathway,
    ValidatedFinalPathwayAssembly,
)


@dataclass(frozen=True)
class _Artifacts:
    product: ProductPathway
    authoritative: TransitionPathway
    candidate: TransitionPathway
    risk: NetOverallSystemRiskResult
    initial: InitialCharterResult
    engine: PathwayEngineResult
    integrated: IntegratedCharterResult
    contribution: NetOverallSystemContribution
    scale: ScaleDiagnosticResult
    token: IdentityToken


def _artifacts() -> _Artifacts:
    token = IdentityToken("lineage-1")
    product = ProductPathway(
        identity_token=token,
        evaluation_run_id="run-1",
        user_id="user-1",
        pathway_id="pathway-1",
        pathway_type="test",
        time_window=None,
        geographic_scope=None,
        system_scope=None,
        objects=(),
        relationships=(),
        assumptions=("ordered-first", "duplicate", "duplicate"),
    )
    authoritative = TransitionPathway(
        reference_id="authoritative",
        identity_token=IdentityToken("older-lineage"),
        evaluation_run_id="older-run",
        user_id="older-user",
        pathway_id="older-pathway",
    )
    adapter_result = object.__new__(ProductAdapterResult)
    object.__setattr__(adapter_result, "product_pathway", product)
    initial = InitialCharterResult(
        identity_token=token,
        evaluation_run_id="run-1",
        adapter_result=adapter_result,
        check_results=(),
        evaluator_version="initial-v1",
        rule_set_version="initial-rules-v1",
        status="CONDITIONAL",
    )
    engine = PathwayEngineResult(
        identity_token=token,
        product_pathway=product,
        transition_pathway=authoritative,
        initial_charter_result=initial,
        direct_comparison_findings=(),
        substitution_combination_findings=(),
        downstream_propagation_findings=(),
        queue_results=(),
        fabric_results=(),
        documentation_findings=(),
        evaluation_run_id="run-1",
        system_context=None,
        evaluator_versions=(),
        rule_set_versions=(),
        user_id="user-1",
        pathway_id="pathway-1",
        unresolved_conditions=("unresolved",),
    )
    integrated = IntegratedCharterResult(
        identity_token=token,
        evaluation_run_id="run-1",
        pathway_engine_result=engine,
        initial_charter_result=initial,
        check_results=(),
        evaluator_version="integrated-v1",
        rule_set_version="integrated-rules-v1",
        status="LIMITED",
    )
    contribution = NetOverallSystemContribution(
        product_pathway=product,
        pathway_engine_result=engine,
        integrated_charter_result=integrated,
        transition_pathway=authoritative,
        contribution_findings=(),
        evaluation_run_id="run-1",
        user_id="user-1",
        pathway_id="pathway-1",
        evaluator_version="contribution-v1",
        rule_set_version="contribution-rules-v1",
        assumptions=("duplicate", "duplicate"),
    )
    scale = ScaleDiagnosticResult(
        product_pathway=product,
        net_overall_system_contribution=contribution,
        transition_pathway=authoritative,
        scale_findings=(),
        evaluation_run_id="run-1",
        user_id="user-1",
        pathway_id="pathway-1",
        evaluator_version="scale-v1",
        rule_set_version="scale-rules-v1",
        uncertainties=("limited",),
    )
    candidate = TransitionPathway(
        reference_id="candidate",
        identity_token=token,
        evaluation_run_id="run-1",
        user_id="user-1",
        pathway_id="pathway-1",
        authoritative_transition_pathway=authoritative,
        product_pathway=product,
        net_overall_system_contribution=contribution,
        scale_diagnostic_result=scale,
        conditions=("conditional", "conditional"),
        unresolved_conditions=("unresolved",),
        compiler_version="compiler-v1",
        model_version="model-v1",
        rule_set_version="compiler-rules-v1",
    )
    adverse_finding = SystemRiskFinding(
        finding_id="risk-1",
        description="Adverse state remains unresolved",
        risk_states=("adverse",),
        unresolved_conditions=("unresolved",),
    )
    risk = NetOverallSystemRiskResult(
        candidate_transition_pathway=candidate,
        authoritative_transition_pathway=authoritative,
        risk_findings=(adverse_finding,),
        evaluation_run_id="run-1",
        user_id="user-1",
        pathway_id="pathway-1",
        evaluator_version="risk-v1",
        rule_set_version="risk-rules-v1",
        assumptions=("duplicate", "duplicate"),
    )
    return _Artifacts(
        product,
        authoritative,
        candidate,
        risk,
        initial,
        engine,
        integrated,
        contribution,
        scale,
        token,
    )


def _args(artifacts: _Artifacts) -> tuple[Any, ...]:
    return (
        artifacts.product,
        artifacts.authoritative,
        artifacts.candidate,
        artifacts.risk,
        artifacts.initial,
        artifacts.engine,
        artifacts.integrated,
        artifacts.contribution,
        artifacts.scale,
        artifacts.token,
        "run-1",
        "user-1",
        "pathway-1",
    )


def test_composes_one_result_from_each_explicit_rule_exactly_once() -> None:
    artifacts = _artifacts()
    expected_args = _args(artifacts)
    calls: list[str] = []

    def assembly_version(*args: object) -> str:
        calls.append("assembly")
        assert args == expected_args
        return "assembly-v1"

    def assembly_rule_version(*args: object) -> str:
        calls.append("rule-set")
        assert args == expected_args
        return "assembly-rules-v1"

    result = CompleteFinalPathwayAssemblyFunction(
        assembly_version,
        assembly_rule_version,
    )(*expected_args)

    assert type(result) is FinalPathwayResult
    assert calls == ["assembly", "rule-set"]
    assert result.assembly_version == "assembly-v1"
    assert result.assembly_rule_version == "assembly-rules-v1"


def test_preserves_exact_primary_trace_and_current_attribution_references() -> None:
    artifacts = _artifacts()
    composer = CompleteFinalPathwayAssemblyFunction(
        lambda *args: "assembly-v1",
        lambda *args: "assembly-rules-v1",
    )

    result = composer(*_args(artifacts))

    assert result.product_pathway is artifacts.product
    assert result.authoritative_transition_pathway is artifacts.authoritative
    assert result.candidate_transition_pathway is artifacts.candidate
    assert result.net_overall_system_risk_result is artifacts.risk
    assert result.evaluation_trace.initial_charter_result is artifacts.initial
    assert result.evaluation_trace.pathway_engine_result is artifacts.engine
    assert result.evaluation_trace.integrated_charter_result is artifacts.integrated
    assert (
        result.evaluation_trace.net_overall_system_contribution
        is artifacts.contribution
    )
    assert result.evaluation_trace.scale_diagnostic_result is artifacts.scale
    assert result.identity_token is artifacts.token
    assert (result.evaluation_run_id, result.user_id, result.pathway_id) == (
        "run-1",
        "user-1",
        "pathway-1",
    )


def test_preserves_order_duplicates_and_adverse_unresolved_upstream_state() -> None:
    artifacts = _artifacts()
    composer = CompleteFinalPathwayAssemblyFunction(
        lambda *args: "assembly-v1",
        lambda *args: "assembly-rules-v1",
    )

    result = composer(*_args(artifacts))

    assert result.product_pathway.assumptions == (
        "ordered-first",
        "duplicate",
        "duplicate",
    )
    assert result.candidate_transition_pathway.conditions == (
        "conditional",
        "conditional",
    )
    assert result.net_overall_system_risk_result.assumptions == (
        "duplicate",
        "duplicate",
    )
    finding = result.net_overall_system_risk_result.risk_findings[0]
    assert finding.risk_states == ("adverse",)
    assert finding.unresolved_conditions == ("unresolved",)


def test_result_passes_validated_boundary_without_mutating_transitions() -> None:
    artifacts = _artifacts()
    candidate_before = artifacts.candidate
    authoritative_before = artifacts.authoritative
    composer = CompleteFinalPathwayAssemblyFunction(
        lambda *args: "assembly-v1",
        lambda *args: "assembly-rules-v1",
    )

    result = ValidatedFinalPathwayAssembly(composer).assemble(*_args(artifacts))

    assert result.candidate_transition_pathway is candidate_before
    assert result.authoritative_transition_pathway is authoritative_before
    assert artifacts.candidate == candidate_before
    assert artifacts.authoritative == authoritative_before
    assert artifacts.authoritative.evaluation_run_id == "older-run"
    assert artifacts.authoritative.identity_token != artifacts.token


def test_composer_introduces_no_downstream_or_scalar_semantics() -> None:
    source = inspect.getsource(CompleteFinalPathwayAssemblyFunction).lower()
    forbidden = (
        "final charter",
        "validator",
        "promotion",
        "binding",
        "pathwayassessment",
        "scoring",
        "ranking",
        "weighting",
        "voting",
        "optimization",
        "scalar aggregation",
    )

    assert all(term not in source for term in forbidden)
