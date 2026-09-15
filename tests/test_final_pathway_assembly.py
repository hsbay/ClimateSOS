import inspect
from dataclasses import FrozenInstanceError, dataclass, replace
from pathlib import Path
from typing import Any, cast

import pytest

from climatesos.pathway_evaluation import (
    EvaluationTrace,
    FinalPathwayAssembly,
    FinalPathwayAssemblyInvariantError,
    FinalPathwayResult,
    FinalPathwayVersionFunction,
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


def _args(
    artifacts: _Artifacts,
    *,
    identity_token: IdentityToken | None = None,
    evaluation_run_id: str = "run-1",
    user_id: str = "user-1",
    pathway_id: str = "pathway-1",
) -> tuple[Any, ...]:
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
        identity_token or artifacts.token,
        evaluation_run_id,
        user_id,
        pathway_id,
    )


class _VersionRule:
    def __init__(self, value: object) -> None:
        self.value = value
        self.calls: list[tuple[object, ...]] = []

    def __call__(self, *args: object) -> object:
        self.calls.append(args)
        return self.value


def _assembly(
    *,
    assembly_version: object = "assembly-v1",
    assembly_rule_version: object = "assembly-rules-v1",
) -> tuple[FinalPathwayAssembly, _VersionRule, _VersionRule]:
    version_rule = _VersionRule(assembly_version)
    rule_version_rule = _VersionRule(assembly_rule_version)

    assembly = FinalPathwayAssembly(
        assembly_version_function=cast(
            FinalPathwayVersionFunction,
            version_rule,
        ),
        assembly_rule_version_function=cast(
            FinalPathwayVersionFunction,
            rule_version_rule,
        ),
    )
    return assembly, version_rule, rule_version_rule


def test_assembly_constructs_result_and_preserves_every_exact_reference() -> None:
    artifacts = _artifacts()
    assembly, version_rule, rule_version_rule = _assembly()
    expected_args = _args(artifacts)

    result = assembly.assemble(*expected_args)

    assert type(result) is FinalPathwayResult
    assert result.product_pathway is artifacts.product
    assert result.authoritative_transition_pathway is artifacts.authoritative
    assert result.candidate_transition_pathway is artifacts.candidate
    assert result.net_overall_system_risk_result is artifacts.risk
    assert type(result.evaluation_trace) is EvaluationTrace
    assert result.evaluation_trace.initial_charter_result is artifacts.initial
    assert result.evaluation_trace.pathway_engine_result is artifacts.engine
    assert result.evaluation_trace.integrated_charter_result is artifacts.integrated
    assert (
        result.evaluation_trace.net_overall_system_contribution
        is artifacts.contribution
    )
    assert result.evaluation_trace.scale_diagnostic_result is artifacts.scale
    assert result.identity_token is artifacts.token
    assert result.evaluation_run_id == "run-1"
    assert result.user_id == "user-1"
    assert result.pathway_id == "pathway-1"
    assert result.assembly_version == "assembly-v1"
    assert result.assembly_rule_version == "assembly-rules-v1"

    assert version_rule.calls == [expected_args]
    assert rule_version_rule.calls == [expected_args]


def test_authoritative_pathway_may_have_older_lineage_and_attribution() -> None:
    artifacts = _artifacts()
    assembly, _, _ = _assembly()

    result = assembly.assemble(*_args(artifacts))

    assert result.authoritative_transition_pathway is artifacts.authoritative
    assert artifacts.authoritative.evaluation_run_id == "older-run"
    assert artifacts.authoritative.identity_token is not artifacts.token
    assert artifacts.authoritative.identity_token.token_id == "older-lineage"


def test_equivalent_identity_token_instance_preserves_same_canonical_lineage() -> None:
    artifacts = _artifacts()
    reconstructed_token = IdentityToken(artifacts.token.token_id)
    assembly, _, _ = _assembly()

    result = assembly.assemble(*_args(artifacts, identity_token=reconstructed_token))

    assert result.identity_token is reconstructed_token
    assert result.identity_token is not artifacts.token
    assert result.identity_token.token_id == artifacts.token.token_id


@pytest.mark.parametrize(
    ("position", "replacement"),
    [
        (3, "risk-user"),
        (5, "engine-user"),
        (7, "contribution-user"),
        (8, "scale-user"),
    ],
)
def test_current_artifact_attribution_mismatch_rejects_before_version_rules(
    position: int,
    replacement: str,
) -> None:
    artifacts = _artifacts()
    assembly, version_rule, rule_version_rule = _assembly()
    bad_args = list(_args(artifacts))

    if position == 3:
        bad_args[position] = replace(artifacts.risk, user_id=replacement)
    elif position == 5:
        bad_args[position] = replace(artifacts.engine, user_id=replacement)
    elif position == 7:
        bad_args[position] = replace(artifacts.contribution, user_id=replacement)
    else:
        bad_args[position] = replace(artifacts.scale, user_id=replacement)

    with pytest.raises(FinalPathwayAssemblyInvariantError):
        assembly.assemble(*bad_args)

    assert version_rule.calls == []
    assert rule_version_rule.calls == []


def test_incorrect_current_lineage_rejects_before_version_rules() -> None:
    artifacts = _artifacts()
    assembly, version_rule, rule_version_rule = _assembly()

    with pytest.raises(FinalPathwayAssemblyInvariantError):
        assembly.assemble(
            *_args(
                artifacts,
                identity_token=IdentityToken("different-lineage"),
            )
        )

    assert version_rule.calls == []
    assert rule_version_rule.calls == []


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("assembly_version", None),
        ("assembly_rule_version", None),
    ],
)
def test_version_rules_must_return_strings(field: str, value: object) -> None:
    artifacts = _artifacts()

    if field == "assembly_version":
        assembly, _, _ = _assembly(assembly_version=value)
    else:
        assembly, _, _ = _assembly(assembly_rule_version=value)

    with pytest.raises(FinalPathwayAssemblyInvariantError):
        assembly.assemble(*_args(artifacts))


def test_version_rule_exception_propagates_unchanged() -> None:
    artifacts = _artifacts()
    failure = RuntimeError("assembly version failed")

    def fail(*_args: object) -> str:
        raise failure

    assembly, _, _ = _assembly()
    assembly = FinalPathwayAssembly(
        assembly_version_function=fail,
        assembly_rule_version_function=assembly.assembly_rule_version_function,
    )

    with pytest.raises(RuntimeError) as raised:
        assembly.assemble(*_args(artifacts))

    assert raised.value is failure


def test_preserves_order_duplicates_and_adverse_unresolved_upstream_state() -> None:
    artifacts = _artifacts()
    assembly, _, _ = _assembly()

    result = assembly.assemble(*_args(artifacts))

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


def test_assembly_does_not_mutate_transition_states() -> None:
    artifacts = _artifacts()
    candidate_before = artifacts.candidate
    authoritative_before = artifacts.authoritative
    assembly, _, _ = _assembly()

    result = assembly.assemble(*_args(artifacts))

    assert result.candidate_transition_pathway is candidate_before
    assert result.authoritative_transition_pathway is authoritative_before
    assert artifacts.candidate == candidate_before
    assert artifacts.authoritative == authoritative_before
    assert artifacts.authoritative.evaluation_run_id == "older-run"


def test_assembly_is_immutable() -> None:
    assembly, _, _ = _assembly()

    with pytest.raises(FrozenInstanceError):
        assembly.assembly_version_function = lambda *args: "changed"  # type: ignore[misc]


def test_assembly_introduces_no_downstream_or_scalar_semantics() -> None:
    source = inspect.getsource(FinalPathwayAssembly).lower()
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
    assert Path(inspect.getfile(FinalPathwayAssembly)).name == (
        "final_pathway_assembly.py"
    )
