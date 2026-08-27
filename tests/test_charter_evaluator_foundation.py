"""Focused tests for Initial and Integrated Charter execution boundaries."""

from dataclasses import FrozenInstanceError, replace

import pytest

from climatesos.pathway_evaluation import (
    Attribute,
    CharterCheckResult,
    CharterEvaluationContext,
    CharterEvaluationInvariantError,
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
    ValidatedCharterEvaluator,
)


def _adapter_result() -> ProductAdapterResult:
    token = IdentityToken("user-1", "pathway-1")
    source = SourceReference("source-1")
    pathway_object = PathwayObject(
        object_id="object-1",
        object_type="represented-function",
        user_id=token.user_id,
        pathway_id=token.pathway_id,
        source_references=(source,),
    )
    pathway = ProductPathway(
        identity_token=token,
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
    return ProductAdapterResult(pathway, intake)


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
    evaluator: ValidatedCharterEvaluator,
    context: CharterEvaluationContext,
) -> PathwayEngineResult:
    initial = evaluator.evaluate_initial(adapter_result, context)
    pathway = adapter_result.product_pathway
    token = pathway.identity_token
    return PathwayEngineResult(
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
        user_id=token.user_id,
        pathway_id=token.pathway_id,
    )


def _evaluator(
    calls: list[tuple[str, object, OpaqueReference, CharterEvaluationContext]],
) -> ValidatedCharterEvaluator:
    def initial_check(
        artifact: ProductAdapterResult,
        definition: OpaqueReference,
        context: CharterEvaluationContext,
    ) -> CharterCheckResult:
        calls.append(("initial", artifact, definition, context))
        status = "ADVERSE" if definition.reference_id == "check-1" else "CLEAR"
        return CharterCheckResult(definition.reference_id, status)

    def integrated_check(
        artifact: PathwayEngineResult,
        definition: OpaqueReference,
        context: CharterEvaluationContext,
    ) -> CharterCheckResult:
        calls.append(("integrated", artifact, definition, context))
        status = "UNRESOLVED" if definition.reference_id == "check-2" else "CLEAR"
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

    return ValidatedCharterEvaluator(
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
        "ADVERSE",
        "CLEAR",
        "CLEAR",
    )
    assert result.adapter_result is adapter_result
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
    assert result.evaluator_version is context.evaluator_version
    assert result.rule_set_version is context.rule_set_version
    assert result.status == "CALLER-DEFINED-INTEGRATED"
    assert tuple(check.status for check in result.check_results) == (
        "CLEAR",
        "UNRESOLVED",
        "CLEAR",
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


def test_initial_malformed_result_is_recorded_as_missing_and_error() -> None:
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
        return CharterCheckResult(definition.reference_id, "CLEAR")

    evaluator = ValidatedCharterEvaluator(
        malformed_check,
        lambda _artifact, definition, _context: CharterCheckResult(
            definition.reference_id,
            "CLEAR",
        ),
        lambda _artifact, _results, _context: "INITIAL",
        lambda _artifact, _results, _context: "INTEGRATED",
    )

    result = evaluator.evaluate_initial(adapter_result, context)

    assert executed_ids == list(context.required_check_ids)
    assert tuple(check.status for check in result.check_results) == (
        "MISSING",
        "CLEAR",
        "CLEAR",
    )
    missing = result.check_results[0]
    assert missing.check_id == "check-1"
    assert missing.execution_error is not None
    assert "no valid result" in missing.execution_error
    assert result.status == "ERROR"
    assert result.execution_error == missing.execution_error


def test_nonmissing_status_with_execution_error_becomes_attributed_missing() -> None:
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
                status="CLEAR",
                findings=("diagnostic finding",),
                supporting_evaluation_findings=(supporting,),
                evidence_references=(evidence,),
                provenance=(evidence,),
                execution_error="caller-reported execution failure",
            )
        return CharterCheckResult(definition.reference_id, "CLEAR")

    evaluator = ValidatedCharterEvaluator(
        incoherent_check,
        lambda _artifact, definition, _context: CharterCheckResult(
            definition.reference_id,
            "CLEAR",
        ),
        lambda _artifact, _results, _context: "INITIAL",
        lambda _artifact, _results, _context: "INTEGRATED",
    )

    result = evaluator.evaluate_initial(adapter_result, context)

    missing = result.check_results[0]
    assert missing.status == "MISSING"
    assert missing.findings == ("diagnostic finding",)
    assert missing.supporting_evaluation_findings == (supporting,)
    assert missing.evidence_references == (evidence,)
    assert missing.provenance == (evidence,)
    assert missing.execution_error is not None
    assert "caller-reported execution failure" in missing.execution_error
    assert result.status == "ERROR"
    assert result.execution_error == missing.execution_error


def test_wrong_check_identities_become_missing_integrity_results() -> None:
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
            "CLEAR",
            findings=("wrongly attributed diagnostic",),
            evidence_references=(adapter_result.intake_bundle.provenance[0],),
        )

    evaluator = ValidatedCharterEvaluator(
        duplicate_check,
        lambda _artifact, definition, _context: CharterCheckResult(
            definition.reference_id,
            "CLEAR",
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
        "CLEAR",
        "MISSING",
        "MISSING",
    )
    assert result.status == "ERROR"
    assert result.execution_error is not None
    assert "check-2" in result.execution_error
    assert "check-3" in result.execution_error
    assert result.check_results[1].findings == ()
    assert result.check_results[1].evidence_references == ()
    assert result.check_results[2].findings == ()
    assert result.check_results[2].evidence_references == ()


def test_integrated_malformed_result_is_recorded_as_missing_and_error() -> None:
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
        return CharterCheckResult(definition.reference_id, "CLEAR")

    def integrated_status(
        _artifact: PathwayEngineResult,
        _results: tuple[CharterCheckResult, ...],
        _context: CharterEvaluationContext,
    ) -> str:
        nonlocal aggregate_status_called
        aggregate_status_called = True
        return "SHOULD-NOT-BE-USED"

    evaluator = ValidatedCharterEvaluator(
        lambda _artifact, definition, _context: CharterCheckResult(
            definition.reference_id,
            "CLEAR",
        ),
        malformed_integrated_check,
        lambda _artifact, _results, _context: "INITIAL",
        integrated_status,
    )

    result = evaluator.evaluate_integrated(engine_result, context)

    assert executed_ids == list(context.required_check_ids)
    assert tuple(check.status for check in result.check_results) == (
        "CLEAR",
        "MISSING",
        "CLEAR",
    )
    missing = result.check_results[1]
    assert missing.check_id == "check-2"
    assert missing.execution_error is not None
    assert "malformed status" in missing.execution_error
    assert missing.findings == ("integrated diagnostic",)
    assert missing.supporting_system_findings == (OpaqueReference("system-finding-1"),)
    assert missing.evidence_references == adapter_result.intake_bundle.provenance
    assert result.status == "ERROR"
    assert result.execution_error == missing.execution_error
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
        return CharterCheckResult(definition.reference_id, "CLEAR")

    evaluator = ValidatedCharterEvaluator(
        initial_check,
        lambda _artifact, definition, _context: CharterCheckResult(
            definition.reference_id,
            "CLEAR",
        ),
        lambda _artifact, _results, _context: None,  # type: ignore[arg-type,return-value]
        lambda _artifact, _results, _context: "INTEGRATED",
    )

    initial_result = evaluator.evaluate_initial(adapter_result, context)

    assert check_calls == list(context.required_check_ids)
    assert tuple(check.status for check in initial_result.check_results) == (
        "CLEAR",
        "CLEAR",
        "CLEAR",
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
        "CLEAR",
        "CLEAR",
        "CLEAR",
    )
    assert integrated_result.status == "ERROR"
    assert integrated_result.execution_error is not None
    assert "RuntimeError: aggregate status unavailable" in (
        integrated_result.execution_error
    )


def test_integrated_rejects_initial_evaluator_integrity_error() -> None:
    calls: list[tuple[str, object, OpaqueReference, CharterEvaluationContext]] = []
    evaluator = _evaluator(calls)
    adapter_result = _adapter_result()
    context = _context()
    engine_result = _engine_result(adapter_result, evaluator, context)
    integrity_error_initial = replace(
        engine_result.initial_charter_result,
        status="ERROR",
        execution_error="required check was MISSING",
    )
    ineligible_engine_result = replace(
        engine_result,
        initial_charter_result=integrity_error_initial,
    )
    calls.clear()

    with pytest.raises(CharterEvaluationInvariantError, match="integrity ERROR"):
        evaluator.evaluate_integrated(ineligible_engine_result, context)
    assert calls == []


def test_initial_and_integrated_artifact_coherence_is_required() -> None:
    calls: list[tuple[str, object, OpaqueReference, CharterEvaluationContext]] = []
    evaluator = _evaluator(calls)
    adapter_result = _adapter_result()
    context = _context()
    other_token = IdentityToken("user-1", "pathway-1")
    incoherent_adapter = replace(
        adapter_result,
        intake_bundle=replace(adapter_result.intake_bundle, identity_token=other_token),
    )

    with pytest.raises(CharterEvaluationInvariantError, match="IdentityToken"):
        evaluator.evaluate_initial(incoherent_adapter, context)

    engine_result = _engine_result(adapter_result, evaluator, context)
    calls.clear()
    misattributed_engine_result = replace(engine_result, user_id="other-user")
    with pytest.raises(CharterEvaluationInvariantError, match="attribution"):
        evaluator.evaluate_integrated(misattributed_engine_result, context)
    assert calls == []
