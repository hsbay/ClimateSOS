import inspect
from dataclasses import dataclass, replace

import pytest

from climatesos.pathway_evaluation import (
    CharterCheckResult,
    CharterCheckStatus,
    CharterEvaluationContext,
    CharterEvaluationInvariantError,
    CharterEvaluator,
    EvaluationTrace,
    FinalCharterResult,
    FinalPathwayResult,
    IdentityToken,
    InitialCharterResult,
    IntegratedCharterResult,
    NetOverallSystemContribution,
    NetOverallSystemRiskResult,
    OpaqueReference,
    PathwayEngineResult,
    ProductAdapterResult,
    ProductPathway,
    ScaleDiagnosticResult,
    TransitionPathway,
)


@dataclass(frozen=True)
class _FinalFixture:
    final_pathway: FinalPathwayResult
    initial: InitialCharterResult
    integrated: IntegratedCharterResult
    authoritative: TransitionPathway


def _fixture() -> _FinalFixture:
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
        check_results=(
            CharterCheckResult("check-1", CharterCheckStatus.PASS),
            CharterCheckResult("check-2", CharterCheckStatus.PASS),
        ),
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
        check_results=(
            CharterCheckResult("check-1", CharterCheckStatus.PASS),
            CharterCheckResult("check-2", CharterCheckStatus.UNRESOLVED),
        ),
        evaluator_version="integrated-v1",
        rule_set_version="integrated-rules-v1",
        status="UNRESOLVED",
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
    final_pathway = FinalPathwayResult(
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
    return _FinalFixture(final_pathway, initial, integrated, authoritative)


def _context() -> CharterEvaluationContext:
    return CharterEvaluationContext(
        foundational_charter=OpaqueReference("charter"),
        applicable_check_definitions=(
            OpaqueReference("check-1"),
            OpaqueReference("check-2"),
        ),
        evaluator_version="final-v1",
        rule_set_version="final-rules-v1",
        required_check_ids=("check-1", "check-2"),
    )


def _evaluator(
    final_check: object,
    final_status: object,
) -> CharterEvaluator:
    return CharterEvaluator(
        lambda artifact, definition, context: CharterCheckResult(
            definition.reference_id, CharterCheckStatus.PASS
        ),
        lambda artifact, definition, context: CharterCheckResult(
            definition.reference_id, CharterCheckStatus.PASS
        ),
        lambda artifact, results, context: "PASS",
        lambda artifact, results, context: "PASS",
        final_check,  # type: ignore[arg-type]
        final_status,  # type: ignore[arg-type]
    )


def test_final_pass_reruns_every_check_and_can_change_prior_states() -> None:
    fixture = _fixture()
    context = _context()
    calls: list[str] = []

    def final_check(
        artifact: FinalPathwayResult,
        definition: OpaqueReference,
        received_context: CharterEvaluationContext,
    ) -> CharterCheckResult:
        assert artifact is fixture.final_pathway
        assert received_context is context
        calls.append(definition.reference_id)
        status = (
            CharterCheckStatus.FAIL
            if definition.reference_id == "check-1"
            else CharterCheckStatus.PASS
        )
        return CharterCheckResult(definition.reference_id, status)

    evaluator = _evaluator(final_check, lambda artifact, results, context: "FAIL")

    result = evaluator.evaluate_final(fixture.final_pathway, context)

    assert calls == ["check-1", "check-2"]
    assert tuple(check.status for check in result.check_results) == (
        CharterCheckStatus.FAIL,
        CharterCheckStatus.PASS,
    )
    assert fixture.integrated.check_results[0].status is CharterCheckStatus.PASS
    assert fixture.integrated.check_results[1].status is CharterCheckStatus.UNRESOLVED


def test_final_result_preserves_exact_upstream_references_and_older_authority() -> None:
    fixture = _fixture()
    evaluator = _evaluator(
        lambda artifact, definition, context: CharterCheckResult(
            definition.reference_id, CharterCheckStatus.UNRESOLVED
        ),
        lambda artifact, results, context: "UNRESOLVED",
    )

    result = evaluator.evaluate_final(fixture.final_pathway, _context())

    assert type(result) is FinalCharterResult
    assert result.final_pathway_result is fixture.final_pathway
    assert result.initial_charter_result is fixture.initial
    assert result.integrated_charter_result is fixture.integrated
    assert result.identity_token is fixture.final_pathway.identity_token
    assert result.evaluation_run_id == "run-1"
    assert fixture.authoritative.evaluation_run_id == "older-run"
    assert fixture.authoritative.identity_token != result.identity_token
    assert all(
        check.status is CharterCheckStatus.UNRESOLVED
        for check in result.check_results
    )


def test_wrong_or_missing_required_check_result_fails_closed() -> None:
    fixture = _fixture()
    status_called = False

    def final_status(*args: object) -> str:
        nonlocal status_called
        status_called = True
        return "PASS"

    evaluator = _evaluator(
        lambda artifact, definition, context: CharterCheckResult(
            "wrong-check-id", CharterCheckStatus.PASS
        ),
        final_status,
    )

    result = evaluator.evaluate_final(fixture.final_pathway, _context())

    assert result.status == "ERROR"
    assert status_called is False
    assert tuple(check.check_id for check in result.check_results) == (
        "check-1",
        "check-2",
    )
    assert all(
        check.status is CharterCheckStatus.ERROR for check in result.check_results
    )


@pytest.mark.parametrize(
    "integrity_status",
    [
        CharterCheckStatus.ERROR,
        CharterCheckStatus.MISSING,
        CharterCheckStatus.NULL,
        CharterCheckStatus.NOACK,
    ],
)
def test_final_integrity_states_force_enclosing_error(
    integrity_status: CharterCheckStatus,
) -> None:
    fixture = _fixture()
    evaluator = _evaluator(
        lambda artifact, definition, context: CharterCheckResult(
            definition.reference_id, integrity_status
        ),
        lambda artifact, results, context: "PASS",
    )

    result = evaluator.evaluate_final(fixture.final_pathway, _context())

    assert result.status == "ERROR"
    assert all(check.status is integrity_status for check in result.check_results)
    assert result.execution_error is not None


@pytest.mark.parametrize(
    "substantive_status",
    [
        CharterCheckStatus.FAIL,
        CharterCheckStatus.UNRESOLVED,
        CharterCheckStatus.NOT_APPLICABLE,
    ],
)
def test_substantive_nonpassing_states_are_completed_results(
    substantive_status: CharterCheckStatus,
) -> None:
    fixture = _fixture()
    evaluator = _evaluator(
        lambda artifact, definition, context: CharterCheckResult(
            definition.reference_id, substantive_status
        ),
        lambda artifact, results, context: substantive_status.value,
    )

    result = evaluator.evaluate_final(fixture.final_pathway, _context())

    assert result.status == substantive_status.value
    assert result.execution_error is None
    assert all(check.status is substantive_status for check in result.check_results)


@pytest.mark.parametrize("mismatch", ["identity", "run"])
def test_current_lineage_mismatch_rejects_before_check_execution(
    mismatch: str,
) -> None:
    fixture = _fixture()
    calls = 0

    def final_check(*args: object) -> CharterCheckResult:
        nonlocal calls
        calls += 1
        return CharterCheckResult("check-1", CharterCheckStatus.PASS)

    if mismatch == "identity":
        final_pathway = replace(
            fixture.final_pathway,
            identity_token=IdentityToken("different-lineage"),
        )
    else:
        final_pathway = replace(fixture.final_pathway, evaluation_run_id="other-run")

    with pytest.raises(CharterEvaluationInvariantError):
        _evaluator(final_check, lambda *args: "PASS").evaluate_final(
            final_pathway, _context()
        )
    assert calls == 0


def test_prior_check_object_cannot_substitute_for_fresh_final_result() -> None:
    fixture = _fixture()
    prior = fixture.integrated.check_results[0]
    evaluator = _evaluator(
        lambda artifact, definition, context: (
            prior
            if definition.reference_id == "check-1"
            else CharterCheckResult("check-2", CharterCheckStatus.PASS)
        ),
        lambda artifact, results, context: "PASS",
    )

    result = evaluator.evaluate_final(fixture.final_pathway, _context())

    assert result.status == "ERROR"
    assert result.check_results[0] is not prior
    assert result.check_results[0].status is CharterCheckStatus.ERROR


def test_structural_validation_does_not_generate_pass_or_downstream_state() -> None:
    fixture = _fixture()
    check_calls = 0

    def unresolved_check(
        artifact: FinalPathwayResult,
        definition: OpaqueReference,
        context: CharterEvaluationContext,
    ) -> CharterCheckResult:
        nonlocal check_calls
        check_calls += 1
        return CharterCheckResult(
            definition.reference_id, CharterCheckStatus.UNRESOLVED
        )

    evaluator = _evaluator(
        unresolved_check,
        lambda artifact, results, context: "UNRESOLVED",
    )
    result = evaluator.evaluate_final(fixture.final_pathway, _context())
    source = inspect.getsource(CharterEvaluator.evaluate_final).lower()

    assert check_calls == 2
    assert result.status == "UNRESOLVED"
    assert all(
        check.status is not CharterCheckStatus.PASS
        for check in result.check_results
    )
    assert all(
        term not in source
        for term in (
            "cleanbound",
            "mixedbound",
            "fossilbound",
            "harmbound",
            "bindinghandler",
            "boundpathway",
            "promotion",
            "scoring",
            "ranking",
            "weighting",
            "voting",
            "optimization",
        )
    )
