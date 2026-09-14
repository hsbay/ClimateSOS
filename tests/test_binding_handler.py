import inspect
from dataclasses import fields
from typing import cast

import pytest

from climatesos.pathway_evaluation import (
    BindingHandler,
    BindingInvariantError,
    BoundPathway,
    BoundState,
    EvaluationTrace,
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
)


def _final_pathway() -> FinalPathwayResult:
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
        status="PASS",
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
        status="PASS",
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
    return FinalPathwayResult(
        product_pathway=product,
        authoritative_transition_pathway=authoritative,
        candidate_transition_pathway=candidate,
        net_overall_system_risk_result=risk,
        evaluation_trace=EvaluationTrace(
            initial_charter_result=initial,
            pathway_engine_result=engine,
            integrated_charter_result=integrated,
            net_overall_system_contribution=contribution,
            scale_diagnostic_result=scale,
        ),
        identity_token=token,
        evaluation_run_id="run-1",
        user_id="user-1",
        pathway_id="pathway-1",
        assembly_version="assembly-v1",
        assembly_rule_version="assembly-rules-v1",
    )


def _bind(
    final_pathway: FinalPathwayResult,
    state: BoundState | None,
) -> BoundPathway:
    return BindingHandler().bind(
        final_pathway,
        state,
        final_pathway.identity_token,
        "run-1",
        "user-1",
        "pathway-1",
        "binding-mechanism",
        "binding-mechanism-v1",
    )


@pytest.mark.parametrize(
    "state",
    [
        BoundState.CLEAN_BOUND,
        BoundState.MIXED_BOUND,
        BoundState.FOSSIL_BOUND,
        BoundState.UNBOUND,
        BoundState.HARM_BOUND,
        BoundState.BOUNDARY_STRESS,
        BoundState.BIO_BOUND,
        BoundState.RESTORATION_BOUND,
    ],
)
def test_each_ordinary_runtime_state_is_preserved_exactly(state: BoundState) -> None:
    final_pathway = _final_pathway()

    result = _bind(final_pathway, state)

    assert result.bound_state is state
    assert result.final_pathway_result is final_pathway


def test_none_produces_handler_owned_no_ack() -> None:
    final_pathway = _final_pathway()

    result = _bind(final_pathway, None)

    assert result.bound_state is BoundState.NO_ACK
    assert result.final_pathway_result is final_pathway
    assert result.identity_token is final_pathway.identity_token
    assert result.evaluation_run_id == "run-1"
    assert result.user_id == "user-1"
    assert result.pathway_id == "pathway-1"
    assert result.binding_mechanism_id == "binding-mechanism"
    assert result.binding_mechanism_version == "binding-mechanism-v1"


def test_direct_runtime_no_ack_remains_handler_owned_no_ack() -> None:
    final_pathway = _final_pathway()

    result = _bind(final_pathway, BoundState.NO_ACK)

    assert result.bound_state is BoundState.NO_ACK
    assert result.final_pathway_result is final_pathway


def test_valid_unbound_remains_runtime_selected_unbound() -> None:
    final_pathway = _final_pathway()

    result = _bind(final_pathway, BoundState.UNBOUND)

    assert result.bound_state is BoundState.UNBOUND


@pytest.mark.parametrize("invalid_state", [object(), "CleanBound", 1])
def test_wrong_type_runtime_state_fails_closed_to_no_ack(
    invalid_state: object,
) -> None:
    final_pathway = _final_pathway()

    result = _bind(final_pathway, cast(BoundState, invalid_state))

    assert result.bound_state is BoundState.NO_ACK


@pytest.mark.parametrize("mismatch", ["lineage", "run", "user", "pathway"])
def test_invalid_final_pathway_binding_input_rejects_before_binding(
    mismatch: str,
) -> None:
    final_pathway = _final_pathway()
    token = final_pathway.identity_token
    run_id = "run-1"
    user_id = "user-1"
    pathway_id = "pathway-1"
    if mismatch == "lineage":
        token = IdentityToken("other-lineage")
    elif mismatch == "run":
        run_id = "other-run"
    elif mismatch == "user":
        user_id = "other-user"
    else:
        pathway_id = "other-pathway"

    with pytest.raises(BindingInvariantError):
        BindingHandler().bind(
            final_pathway,
            None,
            token,
            run_id,
            user_id,
            pathway_id,
            "binding-mechanism",
            "binding-mechanism-v1",
        )


def test_handler_has_no_determiner_or_evaluator_callback_and_no_later_logic() -> None:
    handler_fields = {field.name for field in fields(BindingHandler)}
    source = inspect.getsource(BindingHandler).lower()

    assert handler_fields == set()
    assert "boundstatedeterminer" not in source
    assert all(
        term not in source
        for term in (
            "pathwayassessment",
            "assessment",
            "ranking",
            "scoring",
            "weighting",
            "voting",
            "optimization",
        )
    )
