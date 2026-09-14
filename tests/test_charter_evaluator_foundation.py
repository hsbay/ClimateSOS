"""Focused tests for Initial and Integrated Charter execution boundaries."""

from dataclasses import FrozenInstanceError, replace

import pytest

from climatesos.pathway_evaluation import (
    Attribute,
    CharterCheckResult,
    CharterCheckStatus,
    CharterEvaluationContext,
    CharterEvaluationInvariantError,
    CharterEvaluator,
    CharterStatus,
    EvaluationRun,
    IdentityToken,
    IntakeArtifact,
    OpaqueReference,
    PathwayEngineResult,
    PathwayObject,
    ProductAdapterResult,
    ProductIntakeBundle,
    ProductPathway,
    SourceReference,
    TransitionPathway,
)


def _adapter_result() -> ProductAdapterResult:
    token = IdentityToken("token-1")
    evaluation_run = EvaluationRun("run-1", token.token_id)
    source = SourceReference("source-1")
    pathway_object = PathwayObject(
        object_id="object-1",
        object_type="represented-function",
        user_id="user-1",
        pathway_id="pathway-1",
        source_references=(source,),
    )
    pathway = ProductPathway(
        identity_token=token,
        evaluation_run_id=evaluation_run.evaluation_run_id,
        user_id="user-1",
        pathway_id="pathway-1",
        pathway_type="test",
        time_window=None,
        geographic_scope=None,
        system_scope=None,
        objects=(pathway_object,),
        relationships=(),
        evidence_references=(source,),
    )
    intake = ProductIntakeBundle(
        identity_token=token,
        evaluation_run=evaluation_run,
        materials=(
            IntakeArtifact(
                artifact_id="artifact-1",
                media_type="text/plain",
                content="preserved intake",
                provenance=(source,),
            ),
        ),
        provenance=(source,),
    )
    return ProductAdapterResult(pathway, intake, evaluation_run)


def _context() -> CharterEvaluationContext:
    return CharterEvaluationContext(
        foundational_charter=OpaqueReference("foundational-charter-v1"),
        applicable_check_definitions=(
            OpaqueReference("check-1"),
            OpaqueReference("check-2"),
            OpaqueReference("check-3"),
        ),
        evaluator_version="charter-evaluator-v1",
        rule_set_version="charter-rules-v1",
        required_check_ids=("check-1", "check-2", "check-3"),
        runtime_configuration=(Attribute("mode", "test"),),
    )


def _engine_result(
    adapter_result: ProductAdapterResult,
    evaluator: CharterEvaluator,
    context: CharterEvaluationContext,
) -> PathwayEngineResult:
    initial = evaluator.evaluate_initial(adapter_result, context)
    pathway = adapter_result.product_pathway
    return PathwayEngineResult(
        identity_token=pathway.identity_token,
        product_pathway=pathway,
        transition_pathway=TransitionPathway("transition-1"),
        initial_charter_result=initial,
        direct_comparison_findings=(),
        substitution_combination_findings=(),
        downstream_propagation_findings=(),
        queue_results=(),
        fabric_results=(),
        documentation_findings=(),
        evaluation_run_id="run-1",
        system_context=OpaqueReference("system-context-1"),
        evaluator_versions=(),
        rule_set_versions=(),
        user_id=pathway.user_id,
        pathway_id=pathway.pathway_id,
    )


def _evaluator(
    calls: list[tuple[str, object, OpaqueReference, CharterEvaluationContext]],
) -> CharterEvaluator:
    def initial_check(
        artifact: ProductAdapterResult,
        definition: OpaqueReference,
        context: CharterEvaluationContext,
    ) -> CharterCheckResult:
        calls.append(("initial", artifact, definition, context))
        if definition.reference_id == "check-1":
            return CharterCheckResult(
                definition.reference_id,
                CharterCheckStatus.FAIL,
                charter_statuses=(
                    CharterStatus("HARM", findings=("established harm",)),
                ),
            )
        return CharterCheckResult(definition.reference_id, CharterCheckStatus.PASS)

    def integrated_check(
        artifact: PathwayEngineResult,
        definition: OpaqueReference,
        context: CharterEvaluationContext,
    ) -> CharterCheckResult:
        calls.append(("integrated", artifact, definition, context))
        status = (
            CharterCheckStatus.UNRESOLVED
            if definition.reference_id == "check-2"
            else CharterCheckStatus.PASS
        )
        return CharterCheckResult(definition.reference_id, status)

    def initial_status(
        artifact: ProductAdapterResult,
        results: tuple[CharterCheckResult, ...],
        context: CharterEvaluationContext,
    ) -> str:
        calls.append(("initial-status", artifact, OpaqueReference("status"), context))
        assert (
            tuple(result.check_id for result in results) == context.required_check_ids
        )
        return "CALLER-DEFINED-INITIAL"

    def integrated_status(
        artifact: PathwayEngineResult,
        results: tuple[CharterCheckResult, ...],
        context: CharterEvaluationContext,
    ) -> str:
        calls.append(
            ("integrated-status", artifact, OpaqueReference("status"), context)
        )
        assert (
            tuple(result.check_id for result in results) == context.required_check_ids
        )
        return "CALLER-DEFINED-INTEGRATED"

    return CharterEvaluator(
        initial_check,
        integrated_check,
        initial_status,
        integrated_status,
    )


def test_initial_executes_every_check_and_preserves_context_and_artifact() -> None:
    calls: list[tuple[str, object, OpaqueReference, CharterEvaluationContext]] = []
    evaluator = _evaluator(calls)
    adapter_result = _adapter_result()
    context = _context()

    result = evaluator.evaluate_initial(adapter_result, context)

    check_calls = [call for call in calls if call[0] == "initial"]
    assert [call[2] for call in check_calls] == list(
        context.applicable_check_definitions
    )
    assert all(call[1] is adapter_result and call[3] is context for call in check_calls)
    assert tuple(check.status for check in result.check_results) == (
        CharterCheckStatus.FAIL,
        CharterCheckStatus.PASS,
        CharterCheckStatus.PASS,
    )
    assert result.check_results[0].charter_statuses == (
        CharterStatus("HARM", findings=("established harm",)),
    )
    assert result.adapter_result is adapter_result
    assert result.identity_token is adapter_result.product_pathway.identity_token
    assert result.evaluation_run_id == adapter_result.evaluation_run.evaluation_run_id
    assert result.evaluator_version is context.evaluator_version
    assert result.rule_set_version is context.rule_set_version
    assert result.status == "CALLER-DEFINED-INITIAL"
    assert result.execution_error is None
    with pytest.raises(FrozenInstanceError):
        result.status = "rewritten"  # type: ignore[misc]


def test_integrated_reruns_complete_set_without_reusing_initial_checks() -> None:
    calls: list[tuple[str, object, OpaqueReference, CharterEvaluationContext]] = []
    evaluator = _evaluator(calls)
    adapter_result = _adapter_result()
    context = _context()
    engine_result = _engine_result(adapter_result, evaluator, context)
    initial_result = engine_result.initial_charter_result
    calls.clear()

    result = evaluator.evaluate_integrated(engine_result, context)

    check_calls = [call for call in calls if call[0] == "integrated"]
    assert [call[2] for call in check_calls] == list(
        context.applicable_check_definitions
    )
    assert all(call[1] is engine_result and call[3] is context for call in check_calls)
    assert result.pathway_engine_result is engine_result
    assert result.initial_charter_result is initial_result
    assert result.identity_token is engine_result.identity_token
    assert result.evaluation_run_id == engine_result.evaluation_run_id
    assert result.evaluator_version is context.evaluator_version
    assert result.rule_set_version is context.rule_set_version
    assert result.status == "CALLER-DEFINED-INTEGRATED"
    assert tuple(check.status for check in result.check_results) == (
        CharterCheckStatus.PASS,
        CharterCheckStatus.UNRESOLVED,
        CharterCheckStatus.PASS,
    )
    assert all(
        integrated is not initial
        for integrated, initial in zip(
            result.check_results,
            initial_result.check_results,
            strict=True,
        )
    )


def test_context_must_define_exactly_the_complete_required_check_set() -> None:
    calls: list[tuple[str, object, OpaqueReference, CharterEvaluationContext]] = []
    evaluator = _evaluator(calls)
    adapter_result = _adapter_result()
    context = _context()
    missing_definition = replace(
        context,
        applicable_check_definitions=context.applicable_check_definitions[:-1],
    )

    with pytest.raises(CharterEvaluationInvariantError, match="missing required"):
        evaluator.evaluate_initial(adapter_result, missing_definition)
    assert calls == []

    duplicate_required_id = replace(
        context,
        required_check_ids=("check-1", "check-1", "check-3"),
    )
    with pytest.raises(CharterEvaluationInvariantError, match="must be unique"):
        evaluator.evaluate_initial(adapter_result, duplicate_required_id)
    assert calls == []

    empty_context = replace(
        context,
        applicable_check_definitions=(),
        required_check_ids=(),
    )
    with pytest.raises(CharterEvaluationInvariantError, match="at least one"):
        evaluator.evaluate_initial(adapter_result, empty_context)
    assert calls == []


@pytest.mark.parametrize("invalid_status", ["CLEAR", "ADVERSE"])
def test_arbitrary_charter_check_status_is_structurally_rejected(
    invalid_status: str,
) -> None:
    adapter_result = _adapter_result()
    context = _context()
    aggregate_status_called = False

    def invalid_check(
        _artifact: ProductAdapterResult,
        definition: OpaqueReference,
        _context: CharterEvaluationContext,
    ) -> CharterCheckResult:
        return CharterCheckResult(
            definition.reference_id,
            invalid_status,  # type: ignore[arg-type]
        )

    def aggregate_status(
        _artifact: ProductAdapterResult,
        _results: tuple[CharterCheckResult, ...],
        _context: CharterEvaluationContext,
    ) -> str:
        nonlocal aggregate_status_called
        aggregate_status_called = True
        return "SHOULD-NOT-BE-USED"

    evaluator = CharterEvaluator(
        invalid_check,
        lambda _artifact, definition, _context: CharterCheckResult(
            definition.reference_id,
            CharterCheckStatus.PASS,
        ),
        aggregate_status,
        lambda _artifact, _results, _context: "INTEGRATED",
    )

    result = evaluator.evaluate_initial(adapter_result, context)

    assert all(
        check.status is CharterCheckStatus.ERROR for check in result.check_results
    )
    assert all(
        check.execution_error is not None
        and "malformed status" in check.execution_error
        for check in result.check_results
    )
    assert aggregate_status_called is False


def test_exception_null_and_malformed_outputs_remain_distinct_and_ordered() -> None:
    adapter_result = _adapter_result()
    context = _context()
    executed_ids: list[str] = []
    aggregate_status_called = False

    def mixed_failures(
        _artifact: ProductAdapterResult,
        definition: OpaqueReference,
        _context: CharterEvaluationContext,
    ) -> CharterCheckResult:
        executed_ids.append(definition.reference_id)
        if definition.reference_id == "check-1":
            raise RuntimeError("check execution failed")
        if definition.reference_id == "check-2":
            return None  # type: ignore[return-value]
        return object()  # type: ignore[return-value]

    def aggregate_status(
        _artifact: ProductAdapterResult,
        _results: tuple[CharterCheckResult, ...],
        _context: CharterEvaluationContext,
    ) -> str:
        nonlocal aggregate_status_called
        aggregate_status_called = True
        return "SHOULD-NOT-BE-USED"

    evaluator = CharterEvaluator(
        mixed_failures,
        lambda _artifact, definition, _context: CharterCheckResult(
            definition.reference_id,
            CharterCheckStatus.PASS,
        ),
        aggregate_status,
        lambda _artifact, _results, _context: "INTEGRATED",
    )

    result = evaluator.evaluate_initial(adapter_result, context)

    assert executed_ids == list(context.required_check_ids)
    assert tuple(check.check_id for check in result.check_results) == (
        context.required_check_ids
    )
    assert tuple(check.status for check in result.check_results) == (
        CharterCheckStatus.ERROR,
        CharterCheckStatus.NULL,
        CharterCheckStatus.ERROR,
    )
    assert "RuntimeError: check execution failed" in (
        result.check_results[0].execution_error or ""
    )
    assert "returned null" in (result.check_results[1].execution_error or "")
    assert "no valid result" in (result.check_results[2].execution_error or "")
    assert result.status == "ERROR"
    assert result.execution_error is not None
    assert aggregate_status_called is False


def test_malformed_charter_status_payload_becomes_error() -> None:
    adapter_result = _adapter_result()
    context = _context()
    executed_ids: list[str] = []
    aggregate_status_called = False

    def malformed_status_payload(
        _artifact: ProductAdapterResult,
        definition: OpaqueReference,
        _context: CharterEvaluationContext,
    ) -> CharterCheckResult:
        executed_ids.append(definition.reference_id)
        if definition.reference_id == "check-1":
            malformed_status = CharterStatus(
                "HARM",
                findings=("valid finding", 1),  # type: ignore[arg-type]
            )
            return CharterCheckResult(
                definition.reference_id,
                CharterCheckStatus.FAIL,
                charter_statuses=(malformed_status,),
            )
        return CharterCheckResult(definition.reference_id, CharterCheckStatus.PASS)

    def aggregate_status(
        _artifact: ProductAdapterResult,
        _results: tuple[CharterCheckResult, ...],
        _context: CharterEvaluationContext,
    ) -> str:
        nonlocal aggregate_status_called
        aggregate_status_called = True
        return "SHOULD-NOT-BE-USED"

    evaluator = CharterEvaluator(
        malformed_status_payload,
        lambda _artifact, definition, _context: CharterCheckResult(
            definition.reference_id,
            CharterCheckStatus.PASS,
        ),
        aggregate_status,
        lambda _artifact, _results, _context: "INTEGRATED",
    )

    result = evaluator.evaluate_initial(adapter_result, context)

    assert executed_ids == list(context.required_check_ids)
    assert tuple(check.status for check in result.check_results) == (
        CharterCheckStatus.ERROR,
        CharterCheckStatus.PASS,
        CharterCheckStatus.PASS,
    )
    assert result.check_results[0].charter_statuses == ()
    assert "malformed Charter statuses" in (
        result.check_results[0].execution_error or ""
    )
    assert result.status == "ERROR"
    assert aggregate_status_called is False


@pytest.mark.parametrize(
    "integrity_status",
    [
        CharterCheckStatus.ERROR,
        CharterCheckStatus.MISSING,
        CharterCheckStatus.NULL,
        CharterCheckStatus.NOACK,
    ],
)
def test_returned_integrity_status_is_preserved_and_bypasses_aggregate(
    integrity_status: CharterCheckStatus,
) -> None:
    adapter_result = _adapter_result()
    context = _context()
    executed_ids: list[str] = []
    aggregate_status_called = False

    def integrity_result(
        _artifact: ProductAdapterResult,
        definition: OpaqueReference,
        _context: CharterEvaluationContext,
    ) -> CharterCheckResult:
        executed_ids.append(definition.reference_id)
        return CharterCheckResult(
            definition.reference_id,
            integrity_status,
            execution_error=f"{integrity_status.value} diagnostic",
        )

    def aggregate_status(
        _artifact: ProductAdapterResult,
        _results: tuple[CharterCheckResult, ...],
        _context: CharterEvaluationContext,
    ) -> str:
        nonlocal aggregate_status_called
        aggregate_status_called = True
        return "SHOULD-NOT-BE-USED"

    evaluator = CharterEvaluator(
        integrity_result,
        lambda _artifact, definition, _context: CharterCheckResult(
            definition.reference_id,
            CharterCheckStatus.PASS,
        ),
        aggregate_status,
        lambda _artifact, _results, _context: "INTEGRATED",
    )

    result = evaluator.evaluate_initial(adapter_result, context)

    assert executed_ids == list(context.required_check_ids)
    assert all(check.status is integrity_status for check in result.check_results)
    assert result.status == "ERROR"
    assert result.execution_error is not None
    assert integrity_status.value in result.execution_error
    assert aggregate_status_called is False


@pytest.mark.parametrize(
    "substantive_status",
    [
        CharterCheckStatus.PASS,
        CharterCheckStatus.FAIL,
        CharterCheckStatus.UNRESOLVED,
        CharterCheckStatus.NOT_APPLICABLE,
    ],
)
def test_substantive_outcomes_are_not_integrity_failures(
    substantive_status: CharterCheckStatus,
) -> None:
    adapter_result = _adapter_result()
    context = _context()
    aggregate_status_called = False

    def completed_check(
        _artifact: ProductAdapterResult,
        definition: OpaqueReference,
        _context: CharterEvaluationContext,
    ) -> CharterCheckResult:
        charter_statuses = (
            (CharterStatus("HARM", findings=("established harm",)),)
            if substantive_status is CharterCheckStatus.FAIL
            else ()
        )
        return CharterCheckResult(
            definition.reference_id,
            substantive_status,
            charter_statuses=charter_statuses,
        )

    def aggregate_status(
        _artifact: ProductAdapterResult,
        _results: tuple[CharterCheckResult, ...],
        _context: CharterEvaluationContext,
    ) -> str:
        nonlocal aggregate_status_called
        aggregate_status_called = True
        return "AGGREGATED"

    evaluator = CharterEvaluator(
        completed_check,
        lambda _artifact, definition, _context: CharterCheckResult(
            definition.reference_id,
            CharterCheckStatus.PASS,
        ),
        aggregate_status,
        lambda _artifact, _results, _context: "INTEGRATED",
    )

    result = evaluator.evaluate_initial(adapter_result, context)

    assert all(check.status is substantive_status for check in result.check_results)
    assert result.status == "AGGREGATED"
    assert result.execution_error is None
    assert aggregate_status_called is True


def test_initial_null_result_is_recorded_as_null_integrity_failure() -> None:
    adapter_result = _adapter_result()
    context = _context()
    executed_ids: list[str] = []

    def malformed_check(
        _artifact: ProductAdapterResult,
        definition: OpaqueReference,
        _context: CharterEvaluationContext,
    ) -> CharterCheckResult:
        executed_ids.append(definition.reference_id)
        if definition.reference_id == "check-1":
            return None  # type: ignore[return-value]
        return CharterCheckResult(definition.reference_id, CharterCheckStatus.PASS)

    evaluator = CharterEvaluator(
        malformed_check,
        lambda _artifact, definition, _context: CharterCheckResult(
            definition.reference_id,
            CharterCheckStatus.PASS,
        ),
        lambda _artifact, _results, _context: "INITIAL",
        lambda _artifact, _results, _context: "INTEGRATED",
    )

    result = evaluator.evaluate_initial(adapter_result, context)

    assert executed_ids == list(context.required_check_ids)
    assert tuple(check.status for check in result.check_results) == (
        CharterCheckStatus.NULL,
        CharterCheckStatus.PASS,
        CharterCheckStatus.PASS,
    )
    null_result = result.check_results[0]
    assert null_result.check_id == "check-1"
    assert null_result.execution_error is not None
    assert "returned null" in null_result.execution_error
    assert result.status == "ERROR"
    assert result.execution_error == null_result.execution_error


def test_substantive_status_with_execution_error_becomes_attributed_error() -> None:
    adapter_result = _adapter_result()
    context = _context()
    evidence = adapter_result.intake_bundle.provenance[0]
    supporting = OpaqueReference("supporting-finding-1")

    def incoherent_check(
        _artifact: ProductAdapterResult,
        definition: OpaqueReference,
        _context: CharterEvaluationContext,
    ) -> CharterCheckResult:
        if definition.reference_id == "check-1":
            return CharterCheckResult(
                check_id=definition.reference_id,
                status=CharterCheckStatus.PASS,
                findings=("diagnostic finding",),
                supporting_evaluation_findings=(supporting,),
                evidence_references=(evidence,),
                provenance=(evidence,),
                execution_error="caller-reported execution failure",
            )
        return CharterCheckResult(definition.reference_id, CharterCheckStatus.PASS)

    evaluator = CharterEvaluator(
        incoherent_check,
        lambda _artifact, definition, _context: CharterCheckResult(
            definition.reference_id,
            CharterCheckStatus.PASS,
        ),
        lambda _artifact, _results, _context: "INITIAL",
        lambda _artifact, _results, _context: "INTEGRATED",
    )

    result = evaluator.evaluate_initial(adapter_result, context)

    error_result = result.check_results[0]
    assert error_result.status is CharterCheckStatus.ERROR
    assert error_result.findings == ("diagnostic finding",)
    assert error_result.supporting_evaluation_findings == (supporting,)
    assert error_result.evidence_references == (evidence,)
    assert error_result.provenance == (evidence,)
    assert error_result.execution_error is not None
    assert "caller-reported execution failure" in error_result.execution_error
    assert result.status == "ERROR"
    assert result.execution_error == error_result.execution_error


def test_wrong_check_identities_become_error_integrity_results() -> None:
    adapter_result = _adapter_result()
    context = _context()
    calls: list[str] = []

    def duplicate_check(
        _artifact: ProductAdapterResult,
        definition: OpaqueReference,
        _context: CharterEvaluationContext,
    ) -> CharterCheckResult:
        calls.append(definition.reference_id)
        return CharterCheckResult(
            "check-1",
            CharterCheckStatus.PASS,
            findings=("wrongly attributed diagnostic",),
            evidence_references=(adapter_result.intake_bundle.provenance[0],),
        )

    evaluator = CharterEvaluator(
        duplicate_check,
        lambda _artifact, definition, _context: CharterCheckResult(
            definition.reference_id,
            CharterCheckStatus.PASS,
        ),
        lambda _artifact, _results, _context: "INITIAL",
        lambda _artifact, _results, _context: "INTEGRATED",
    )

    result = evaluator.evaluate_initial(adapter_result, context)

    assert calls == list(context.required_check_ids)
    assert tuple(check.check_id for check in result.check_results) == (
        "check-1",
        "check-2",
        "check-3",
    )
    assert tuple(check.status for check in result.check_results) == (
        CharterCheckStatus.PASS,
        CharterCheckStatus.ERROR,
        CharterCheckStatus.ERROR,
    )
    assert result.status == "ERROR"
    assert result.execution_error is not None
    assert "check-2" in result.execution_error
    assert "check-3" in result.execution_error
    assert result.check_results[1].findings == ()
    assert result.check_results[1].evidence_references == ()
    assert result.check_results[2].findings == ()
    assert result.check_results[2].evidence_references == ()


def test_integrated_malformed_result_is_recorded_as_error() -> None:
    adapter_result = _adapter_result()
    context = _context()
    engine_result = _engine_result(adapter_result, _evaluator([]), context)
    executed_ids: list[str] = []
    aggregate_status_called = False

    def malformed_integrated_check(
        _artifact: PathwayEngineResult,
        definition: OpaqueReference,
        _context: CharterEvaluationContext,
    ) -> CharterCheckResult:
        executed_ids.append(definition.reference_id)
        if definition.reference_id == "check-2":
            return CharterCheckResult(
                check_id=definition.reference_id,
                status=None,  # type: ignore[arg-type]
                findings=("integrated diagnostic",),
                supporting_system_findings=(OpaqueReference("system-finding-1"),),
                evidence_references=(adapter_result.intake_bundle.provenance[0],),
            )
        return CharterCheckResult(definition.reference_id, CharterCheckStatus.PASS)

    def integrated_status(
        _artifact: PathwayEngineResult,
        _results: tuple[CharterCheckResult, ...],
        _context: CharterEvaluationContext,
    ) -> str:
        nonlocal aggregate_status_called
        aggregate_status_called = True
        return "SHOULD-NOT-BE-USED"

    evaluator = CharterEvaluator(
        lambda _artifact, definition, _context: CharterCheckResult(
            definition.reference_id,
            CharterCheckStatus.PASS,
        ),
        malformed_integrated_check,
        lambda _artifact, _results, _context: "INITIAL",
        integrated_status,
    )

    result = evaluator.evaluate_integrated(engine_result, context)

    assert executed_ids == list(context.required_check_ids)
    assert tuple(check.status for check in result.check_results) == (
        CharterCheckStatus.PASS,
        CharterCheckStatus.ERROR,
        CharterCheckStatus.PASS,
    )
    error_result = result.check_results[1]
    assert error_result.check_id == "check-2"
    assert error_result.execution_error is not None
    assert "malformed status" in error_result.execution_error
    assert error_result.findings == ("integrated diagnostic",)
    assert error_result.supporting_system_findings == (
        OpaqueReference("system-finding-1"),
    )
    assert error_result.evidence_references == adapter_result.intake_bundle.provenance
    assert result.status == "ERROR"
    assert result.execution_error == error_result.execution_error
    assert aggregate_status_called is False


def test_stage_status_failures_return_error_results_with_completed_checks() -> None:
    adapter_result = _adapter_result()
    context = _context()
    check_calls: list[str] = []

    def initial_check(
        _artifact: ProductAdapterResult,
        definition: OpaqueReference,
        _context: CharterEvaluationContext,
    ) -> CharterCheckResult:
        check_calls.append(definition.reference_id)
        return CharterCheckResult(definition.reference_id, CharterCheckStatus.PASS)

    evaluator = CharterEvaluator(
        initial_check,
        lambda _artifact, definition, _context: CharterCheckResult(
            definition.reference_id,
            CharterCheckStatus.PASS,
        ),
        lambda _artifact, _results, _context: None,  # type: ignore[arg-type,return-value]
        lambda _artifact, _results, _context: "INTEGRATED",
    )

    initial_result = evaluator.evaluate_initial(adapter_result, context)

    assert check_calls == list(context.required_check_ids)
    assert tuple(check.status for check in initial_result.check_results) == (
        CharterCheckStatus.PASS,
        CharterCheckStatus.PASS,
        CharterCheckStatus.PASS,
    )
    assert initial_result.status == "ERROR"
    assert initial_result.execution_error is not None
    assert "returned malformed status" in initial_result.execution_error

    engine_result = replace(
        _engine_result(adapter_result, _evaluator([]), context),
        initial_charter_result=replace(
            initial_result,
            status="CALLER-DEFINED-INITIAL",
            execution_error=None,
        ),
    )

    def raise_integrated_status(
        _artifact: PathwayEngineResult,
        _results: tuple[CharterCheckResult, ...],
        _context: CharterEvaluationContext,
    ) -> str:
        raise RuntimeError("aggregate status unavailable")

    integrated_evaluator = replace(
        evaluator,
        integrated_status_function=raise_integrated_status,
    )
    integrated_result = integrated_evaluator.evaluate_integrated(
        engine_result,
        context,
    )

    assert tuple(check.status for check in integrated_result.check_results) == (
        CharterCheckStatus.PASS,
        CharterCheckStatus.PASS,
        CharterCheckStatus.PASS,
    )
    assert integrated_result.status == "ERROR"
    assert integrated_result.execution_error is not None
    assert "RuntimeError: aggregate status unavailable" in (
        integrated_result.execution_error
    )


@pytest.mark.parametrize(
    "failure_kind",
    [
        "stage-status",
        "execution-error",
        CharterCheckStatus.ERROR,
        CharterCheckStatus.MISSING,
        CharterCheckStatus.NULL,
        CharterCheckStatus.NOACK,
    ],
)
def test_integrated_rejects_initial_integrity_failure_before_callbacks(
    failure_kind: str | CharterCheckStatus,
) -> None:
    calls: list[tuple[str, object, OpaqueReference, CharterEvaluationContext]] = []
    evaluator = _evaluator(calls)
    adapter_result = _adapter_result()
    context = _context()
    engine_result = _engine_result(adapter_result, evaluator, context)
    initial_result = engine_result.initial_charter_result
    if isinstance(failure_kind, CharterCheckStatus):
        integrity_error_initial = replace(
            initial_result,
            status="CALLER-DEFINED-INITIAL",
            execution_error=None,
            check_results=(CharterCheckResult("check-1", failure_kind),),
        )
    elif failure_kind == "stage-status":
        integrity_error_initial = replace(
            initial_result,
            status="ERROR",
            execution_error=None,
        )
    else:
        integrity_error_initial = replace(
            initial_result,
            status="CALLER-DEFINED-INITIAL",
            execution_error="Initial Charter execution failed",
        )
    ineligible_engine_result = replace(
        engine_result,
        initial_charter_result=integrity_error_initial,
    )
    calls.clear()

    with pytest.raises(CharterEvaluationInvariantError, match="integrity failure"):
        evaluator.evaluate_integrated(ineligible_engine_result, context)
    assert calls == []


@pytest.mark.parametrize(
    "check_status",
    [
        CharterCheckStatus.PASS,
        CharterCheckStatus.FAIL,
        CharterCheckStatus.UNRESOLVED,
        CharterCheckStatus.NOT_APPLICABLE,
    ],
)
def test_integrated_accepts_completed_substantive_initial_outcomes(
    check_status: CharterCheckStatus,
) -> None:
    calls: list[tuple[str, object, OpaqueReference, CharterEvaluationContext]] = []
    evaluator = _evaluator(calls)
    adapter_result = _adapter_result()
    context = _context()
    engine_result = _engine_result(adapter_result, evaluator, context)
    charter_statuses = (
        (CharterStatus("HARM", findings=("established harm",)),)
        if check_status is CharterCheckStatus.FAIL
        else ()
    )
    check_result = CharterCheckResult(
        "check-1",
        check_status,
        charter_statuses=charter_statuses,
    )
    initial_result = replace(
        engine_result.initial_charter_result,
        check_results=(check_result,),
    )
    eligible_engine_result = replace(
        engine_result,
        initial_charter_result=initial_result,
    )
    calls.clear()

    result = evaluator.evaluate_integrated(eligible_engine_result, context)

    assert result.initial_charter_result is initial_result
    assert result.initial_charter_result.check_results[0] is check_result
    assert result.initial_charter_result.check_results[0].charter_statuses is (
        charter_statuses
    )
    assert [call[0] for call in calls] == [
        "integrated",
        "integrated",
        "integrated",
        "integrated-status",
    ]


def test_charter_identity_validation_uses_durable_token_id() -> None:
    calls: list[tuple[str, object, OpaqueReference, CharterEvaluationContext]] = []
    evaluator = _evaluator(calls)
    adapter_result = _adapter_result()
    context = _context()
    reconstructed_token = IdentityToken(
        adapter_result.product_pathway.identity_token.token_id
    )
    reconstructed_adapter = replace(
        adapter_result,
        intake_bundle=replace(
            adapter_result.intake_bundle,
            identity_token=reconstructed_token,
        ),
    )

    assert reconstructed_token is not adapter_result.product_pathway.identity_token
    evaluator.evaluate_initial(reconstructed_adapter, context)
    engine_result = _engine_result(reconstructed_adapter, evaluator, context)
    evaluator.evaluate_integrated(engine_result, context)

    different_token_initial = replace(
        engine_result.initial_charter_result,
        adapter_result=replace(
            reconstructed_adapter,
            intake_bundle=replace(
                reconstructed_adapter.intake_bundle,
                identity_token=IdentityToken("token-2"),
            ),
        ),
    )
    different_token_engine_result = replace(
        engine_result,
        initial_charter_result=different_token_initial,
    )
    calls.clear()
    with pytest.raises(CharterEvaluationInvariantError, match="attribution"):
        evaluator.evaluate_integrated(different_token_engine_result, context)
    assert calls == []


def test_initial_and_integrated_reject_mismatched_lineage_or_run() -> None:
    calls: list[tuple[str, object, OpaqueReference, CharterEvaluationContext]] = []
    evaluator = _evaluator(calls)
    adapter_result = _adapter_result()
    context = _context()
    mismatched_run_adapter = replace(
        adapter_result,
        evaluation_run=replace(
            adapter_result.evaluation_run,
            identity_token_id="token-2",
        ),
    )

    with pytest.raises(CharterEvaluationInvariantError, match="IdentityToken"):
        evaluator.evaluate_initial(mismatched_run_adapter, context)
    with pytest.raises(CharterEvaluationInvariantError, match="EvaluationRun"):
        evaluator.evaluate_initial(
            replace(
                adapter_result,
                evaluation_run=replace(
                    adapter_result.evaluation_run,
                    evaluation_run_id="run-2",
                ),
            ),
            context,
        )

    engine_result = _engine_result(adapter_result, evaluator, context)
    calls.clear()
    with pytest.raises(CharterEvaluationInvariantError, match="attribution"):
        evaluator.evaluate_integrated(
            replace(engine_result, identity_token=IdentityToken("token-2")),
            context,
        )
    with pytest.raises(CharterEvaluationInvariantError, match="attribution"):
        evaluator.evaluate_integrated(
            replace(
                engine_result,
                initial_charter_result=replace(
                    engine_result.initial_charter_result,
                    identity_token=IdentityToken("token-2"),
                ),
            ),
            context,
        )
    with pytest.raises(CharterEvaluationInvariantError, match="EvaluationRun"):
        evaluator.evaluate_integrated(
            replace(engine_result, evaluation_run_id="run-2"),
            context,
        )
    with pytest.raises(CharterEvaluationInvariantError, match="EvaluationRun"):
        evaluator.evaluate_integrated(
            replace(
                engine_result,
                initial_charter_result=replace(
                    engine_result.initial_charter_result,
                    evaluation_run_id="run-2",
                ),
            ),
            context,
        )
    assert calls == []


def test_integrated_rejects_preserved_adapter_evaluation_run_mismatch() -> None:
    calls: list[tuple[str, object, OpaqueReference, CharterEvaluationContext]] = []
    evaluator = _evaluator(calls)
    adapter_result = _adapter_result()
    context = _context()
    engine_result = _engine_result(adapter_result, evaluator, context)

    calls.clear()
    mismatched_token_run = replace(
        adapter_result.evaluation_run,
        identity_token_id="token-2",
    )
    mismatched_token_initial = replace(
        engine_result.initial_charter_result,
        adapter_result=replace(
            adapter_result,
            intake_bundle=replace(
                adapter_result.intake_bundle,
                evaluation_run=mismatched_token_run,
            ),
            evaluation_run=mismatched_token_run,
        ),
    )
    with pytest.raises(CharterEvaluationInvariantError, match="attribution"):
        evaluator.evaluate_integrated(
            replace(
                engine_result,
                initial_charter_result=mismatched_token_initial,
            ),
            context,
        )

    mismatched_evaluation_run = replace(
        adapter_result.evaluation_run,
        evaluation_run_id="run-2",
    )
    mismatched_run_initial = replace(
        engine_result.initial_charter_result,
        adapter_result=replace(
            adapter_result,
            intake_bundle=replace(
                adapter_result.intake_bundle,
                evaluation_run=mismatched_evaluation_run,
            ),
            evaluation_run=mismatched_evaluation_run,
        ),
    )
    with pytest.raises(CharterEvaluationInvariantError, match="EvaluationRun"):
        evaluator.evaluate_integrated(
            replace(
                engine_result,
                initial_charter_result=mismatched_run_initial,
            ),
            context,
        )
    assert calls == []


def test_integrated_enforces_exact_upstream_artifact_references() -> None:
    calls: list[tuple[str, object, OpaqueReference, CharterEvaluationContext]] = []
    evaluator = _evaluator(calls)
    adapter_result = _adapter_result()
    context = _context()
    engine_result = _engine_result(adapter_result, evaluator, context)
    initial_result = engine_result.initial_charter_result
    calls.clear()

    reconstructed_run_initial = replace(
        initial_result,
        adapter_result=replace(
            adapter_result,
            intake_bundle=replace(
                adapter_result.intake_bundle,
                evaluation_run=replace(adapter_result.evaluation_run),
            ),
        ),
    )
    with pytest.raises(CharterEvaluationInvariantError, match="reference"):
        evaluator.evaluate_integrated(
            replace(
                engine_result,
                initial_charter_result=reconstructed_run_initial,
            ),
            context,
        )

    reconstructed_pathway_initial = replace(
        initial_result,
        adapter_result=replace(
            adapter_result,
            product_pathway=replace(adapter_result.product_pathway),
        ),
    )
    with pytest.raises(CharterEvaluationInvariantError, match="pathway reference"):
        evaluator.evaluate_integrated(
            replace(
                engine_result,
                initial_charter_result=reconstructed_pathway_initial,
            ),
            context,
        )
    assert calls == []
