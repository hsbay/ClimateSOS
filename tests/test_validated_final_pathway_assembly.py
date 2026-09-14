import inspect
from dataclasses import FrozenInstanceError, dataclass, replace
from pathlib import Path
from typing import Any, cast

import pytest

from climatesos.pathway_evaluation import (
    EvaluationTrace,
    FinalPathwayAssemblyInvariantError,
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
        status="COMPLETE",
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
    )
    integrated = IntegratedCharterResult(
        identity_token=token,
        evaluation_run_id="run-1",
        pathway_engine_result=engine,
        initial_charter_result=initial,
        check_results=(),
        evaluator_version="integrated-v1",
        rule_set_version="integrated-rules-v1",
        status="COMPLETE",
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
        compiler_version="compiler-v1",
        model_version="model-v1",
        rule_set_version="compiler-rules-v1",
    )
    risk = NetOverallSystemRiskResult(
        candidate_transition_pathway=candidate,
        authoritative_transition_pathway=authoritative,
        risk_findings=(),
        evaluation_run_id="run-1",
        user_id="user-1",
        pathway_id="pathway-1",
        evaluator_version="risk-v1",
        rule_set_version="risk-rules-v1",
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


def _result(artifacts: _Artifacts) -> FinalPathwayResult:
    return FinalPathwayResult(
        product_pathway=artifacts.product,
        authoritative_transition_pathway=artifacts.authoritative,
        candidate_transition_pathway=artifacts.candidate,
        net_overall_system_risk_result=artifacts.risk,
        evaluation_trace=EvaluationTrace(
            initial_charter_result=artifacts.initial,
            pathway_engine_result=artifacts.engine,
            integrated_charter_result=artifacts.integrated,
            net_overall_system_contribution=artifacts.contribution,
            scale_diagnostic_result=artifacts.scale,
        ),
        identity_token=artifacts.token,
        evaluation_run_id="run-1",
        user_id="user-1",
        pathway_id="pathway-1",
        assembly_version="assembly-v1",
        assembly_rule_version="assembly-rules-v1",
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


def test_valid_inputs_invoke_once_and_preserve_every_exact_reference() -> None:
    artifacts = _artifacts()
    expected = _result(artifacts)
    calls = 0

    def assemble(*args: object) -> object:
        nonlocal calls
        calls += 1
        assert args == _args(artifacts)
        return expected

    result = ValidatedFinalPathwayAssembly(assemble).assemble(*_args(artifacts))

    assert calls == 1
    assert result is expected
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
    assert result.identity_token.token_id == artifacts.token.token_id
    assert (result.evaluation_run_id, result.user_id, result.pathway_id) == (
        "run-1",
        "user-1",
        "pathway-1",
    )


def test_authoritative_pathway_may_have_older_lineage_and_attribution() -> None:
    artifacts = _artifacts()

    result = ValidatedFinalPathwayAssembly(lambda *args: _result(artifacts)).assemble(
        *_args(artifacts)
    )

    assert result.authoritative_transition_pathway.evaluation_run_id == "older-run"
    assert result.authoritative_transition_pathway.identity_token is not artifacts.token


@pytest.mark.parametrize("reference", ["product", "candidate", "risk", "engine"])
def test_reconstructed_exact_required_output_reference_rejects(reference: str) -> None:
    artifacts = _artifacts()
    result = _result(artifacts)
    if reference == "product":
        result = replace(result, product_pathway=replace(artifacts.product))
    elif reference == "candidate":
        result = replace(
            result,
            candidate_transition_pathway=replace(artifacts.candidate),
        )
    elif reference == "risk":
        result = replace(result, net_overall_system_risk_result=replace(artifacts.risk))
    else:
        result = replace(
            result,
            evaluation_trace=replace(
                result.evaluation_trace,
                pathway_engine_result=replace(artifacts.engine),
            ),
        )

    with pytest.raises(FinalPathwayAssemblyInvariantError):
        ValidatedFinalPathwayAssembly(lambda *args: result).assemble(*_args(artifacts))


def test_input_attribution_mismatch_rejects_before_execution() -> None:
    artifacts = _artifacts()
    calls = 0

    def assemble(*args: object) -> object:
        nonlocal calls
        calls += 1
        return _result(artifacts)

    bad_args = list(_args(artifacts))
    bad_args[3] = replace(artifacts.risk, user_id="other-user")

    with pytest.raises(FinalPathwayAssemblyInvariantError):
        ValidatedFinalPathwayAssembly(assemble).assemble(*bad_args)
    assert calls == 0


def test_incorrect_current_lineage_rejects_before_execution() -> None:
    artifacts = _artifacts()
    calls = 0

    def assemble(*args: object) -> object:
        nonlocal calls
        calls += 1
        return _result(artifacts)

    bad_args = list(_args(artifacts))
    bad_args[9] = IdentityToken("different-lineage")

    with pytest.raises(FinalPathwayAssemblyInvariantError):
        ValidatedFinalPathwayAssembly(assemble).assemble(*bad_args)
    assert calls == 0


def test_non_final_pathway_result_rejects() -> None:
    artifacts = _artifacts()

    with pytest.raises(FinalPathwayAssemblyInvariantError):
        ValidatedFinalPathwayAssembly(lambda *args: object()).assemble(
            *_args(artifacts)
        )


@pytest.mark.parametrize("field", ["assembly_version", "assembly_rule_version"])
def test_invalid_returned_structural_field_rejects(field: str) -> None:
    artifacts = _artifacts()
    if field == "assembly_version":
        result = replace(_result(artifacts), assembly_version=cast(str, None))
    else:
        result = replace(_result(artifacts), assembly_rule_version=cast(str, None))

    with pytest.raises(FinalPathwayAssemblyInvariantError):
        ValidatedFinalPathwayAssembly(lambda *args: result).assemble(*_args(artifacts))


def test_assembly_exception_propagates_unchanged() -> None:
    artifacts = _artifacts()
    failure = RuntimeError("assembly failed")

    def assemble(*args: object) -> object:
        raise failure

    with pytest.raises(RuntimeError) as raised:
        ValidatedFinalPathwayAssembly(assemble).assemble(*_args(artifacts))
    assert raised.value is failure


def test_validated_assembly_is_immutable() -> None:
    validated = ValidatedFinalPathwayAssembly(lambda *args: object())

    with pytest.raises(FrozenInstanceError):
        validated.assembly_function = lambda *args: object()  # type: ignore[misc]


def test_boundary_introduces_no_downstream_or_scalar_semantics() -> None:
    source = inspect.getsource(ValidatedFinalPathwayAssembly).lower()
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
    assert Path(inspect.getfile(ValidatedFinalPathwayAssembly)).name == (
        "final_pathway_assembly.py"
    )
