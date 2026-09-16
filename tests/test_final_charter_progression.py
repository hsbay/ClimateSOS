import inspect
from dataclasses import replace
from typing import TypeVar, cast

import pytest

from climatesos.pathway_evaluation import (
    CharterCheckResult,
    CharterCheckStatus,
    CharterStatus,
    EvaluationTrace,
    FinalCharterIntegrityFailure,
    FinalCharterProgressionError,
    FinalCharterProgressionPrecondition,
    FinalCharterProgressionProhibited,
    FinalCharterResult,
    FinalPathwayResult,
    IdentityToken,
    InitialCharterResult,
    IntegratedCharterResult,
    NetOverallSystemContribution,
    PathwayEngineResult,
    ScaleDiagnosticResult,
    SourceReference,
)

T = TypeVar("T")


def _record(record_type: type[T], **values: object) -> T:
    record = object.__new__(record_type)
    for name, value in values.items():
        object.__setattr__(record, name, value)
    return record


def _result(
    check_results: tuple[CharterCheckResult, ...],
    *,
    status: str,
    execution_error: str | None = None,
    earlier_status: str = "PASS",
) -> FinalCharterResult:
    token = IdentityToken("lineage-1")
    initial = _record(
        InitialCharterResult,
        identity_token=token,
        evaluation_run_id="run-1",
        check_results=(CharterCheckResult("earlier-1", CharterCheckStatus.PASS),),
        status=earlier_status,
    )
    engine = _record(
        PathwayEngineResult,
        identity_token=token,
        evaluation_run_id="run-1",
        initial_charter_result=initial,
    )
    integrated = _record(
        IntegratedCharterResult,
        identity_token=token,
        evaluation_run_id="run-1",
        initial_charter_result=initial,
        pathway_engine_result=engine,
        check_results=(
            CharterCheckResult("earlier-1", CharterCheckStatus.PASS),
        ),
        status=earlier_status,
    )
    trace = EvaluationTrace(
        initial_charter_result=initial,
        pathway_engine_result=engine,
        integrated_charter_result=integrated,
        net_overall_system_contribution=_record(NetOverallSystemContribution),
        scale_diagnostic_result=_record(ScaleDiagnosticResult),
    )
    final_pathway = _record(
        FinalPathwayResult,
        identity_token=token,
        evaluation_run_id="run-1",
        evaluation_trace=trace,
    )
    return FinalCharterResult(
        identity_token=token,
        evaluation_run_id="run-1",
        final_pathway_result=final_pathway,
        initial_charter_result=initial,
        integrated_charter_result=integrated,
        check_results=check_results,
        evaluator_version="final-v1",
        rule_set_version="final-rules-v1",
        status=status,
        execution_error=execution_error,
    )


def test_final_error_blocks_but_preserves_inspectable_result() -> None:
    result = _result(
        (CharterCheckResult("check-1", CharterCheckStatus.PASS),),
        status="ERROR",
        execution_error="status composition failed",
    )

    with pytest.raises(FinalCharterIntegrityFailure) as raised:
        FinalCharterProgressionPrecondition(lambda value: True).require(result)

    assert raised.value.final_charter_result is result
    assert raised.value.final_charter_result.status == "ERROR"
    assert result.check_results[0].status is CharterCheckStatus.PASS


@pytest.mark.parametrize(
    "integrity_status",
    [
        CharterCheckStatus.ERROR,
        CharterCheckStatus.MISSING,
        CharterCheckStatus.NULL,
        CharterCheckStatus.NOACK,
    ],
)
def test_any_integrity_check_blocks_before_progression_rule(
    integrity_status: CharterCheckStatus,
) -> None:
    result = _result(
        (CharterCheckResult("check-1", integrity_status),),
        status="ERROR",
    )
    rule_called = False

    def rule(value: FinalCharterResult) -> bool:
        nonlocal rule_called
        rule_called = True
        return True

    with pytest.raises(FinalCharterIntegrityFailure) as raised:
        FinalCharterProgressionPrecondition(rule).require(result)

    assert rule_called is False
    assert raised.value.final_charter_result is result
    assert result.check_results[0].status is integrity_status


def test_structural_validity_and_absence_of_adverse_finding_do_not_permit() -> None:
    result = _result(
        (
            CharterCheckResult(
                "check-1",
                CharterCheckStatus.NOT_APPLICABLE,
                findings=(),
            ),
        ),
        status="NOT_APPLICABLE",
    )
    calls = 0

    def applicable_rule(value: FinalCharterResult) -> bool:
        nonlocal calls
        calls += 1
        assert value is result
        return False

    with pytest.raises(FinalCharterProgressionProhibited) as raised:
        FinalCharterProgressionPrecondition(applicable_rule).require(result)

    assert calls == 1
    assert raised.value.final_charter_result is result
    assert result.status != "PASS"
    assert result.check_results[0].status is CharterCheckStatus.NOT_APPLICABLE


def test_unresolved_does_not_automatically_permit_progression() -> None:
    evidence = SourceReference("evidence-1")
    result = _result(
        (
            CharterCheckResult(
                "check-1",
                CharterCheckStatus.UNRESOLVED,
                findings=("positive validity not established",),
                evidence_references=(evidence,),
                provenance=(evidence,),
            ),
        ),
        status="UNRESOLVED",
    )

    with pytest.raises(FinalCharterProgressionProhibited):
        FinalCharterProgressionPrecondition(lambda value: False).require(result)

    assert result.check_results[0].status is CharterCheckStatus.UNRESOLVED
    assert result.check_results[0].evidence_references == (evidence,)


def test_substantive_fail_is_completed_and_rule_governed_not_error() -> None:
    finding = CharterStatus("PROHIBITION", findings=("guardrail failed",))
    failed_check = CharterCheckResult(
        "check-1",
        CharterCheckStatus.FAIL,
        findings=("failed substantive condition",),
        charter_statuses=(finding,),
    )
    result = _result((failed_check,), status="FAIL")

    with pytest.raises(FinalCharterProgressionProhibited) as raised:
        FinalCharterProgressionPrecondition(
            lambda value: not any(
                check.status is CharterCheckStatus.FAIL
                for check in value.check_results
            )
        ).require(result)

    assert raised.value.final_charter_result is result
    assert result.status == "FAIL"
    assert result.execution_error is None
    assert result.check_results[0] is failed_check
    assert result.check_results[0].charter_statuses == (finding,)


def test_pass_sibling_cannot_cancel_fail_under_applicable_rule() -> None:
    passed = CharterCheckResult("check-1", CharterCheckStatus.PASS)
    failed = CharterCheckResult("check-2", CharterCheckStatus.FAIL)
    result = _result((passed, failed), status="FAIL")

    with pytest.raises(FinalCharterProgressionProhibited):
        FinalCharterProgressionPrecondition(
            lambda value: all(
                check.status is CharterCheckStatus.PASS
                for check in value.check_results
            )
        ).require(result)

    assert result.check_results == (passed, failed)
    assert result.check_results[0] is passed
    assert result.check_results[1] is failed


def test_earlier_pass_does_not_grant_final_permission() -> None:
    unresolved = CharterCheckResult("check-1", CharterCheckStatus.UNRESOLVED)
    result = _result((unresolved,), status="UNRESOLVED", earlier_status="PASS")

    with pytest.raises(FinalCharterProgressionProhibited):
        FinalCharterProgressionPrecondition(lambda value: False).require(result)

    assert result.initial_charter_result.status == "PASS"
    assert result.integrated_charter_result.status == "PASS"
    assert result.status == "UNRESOLVED"


def test_explicitly_permitted_result_passes_as_exact_reference() -> None:
    checks = (
        CharterCheckResult("check-1", CharterCheckStatus.PASS),
        CharterCheckResult("check-2", CharterCheckStatus.NOT_APPLICABLE),
    )
    result = _result(checks, status="PASS")
    observed: list[FinalCharterResult] = []

    def applicable_rule(value: FinalCharterResult) -> bool:
        observed.append(value)
        return True

    handed_off = FinalCharterProgressionPrecondition(applicable_rule).require(result)

    assert handed_off is result
    assert observed == [result]
    assert handed_off.check_results == checks


@pytest.mark.parametrize("malformation", ["lineage", "references", "checks"])
def test_malformed_final_result_uses_integrity_path_and_preserves_reference(
    malformation: str,
) -> None:
    result = _result(
        (CharterCheckResult("check-1", CharterCheckStatus.PASS),),
        status="PASS",
    )
    if malformation == "lineage":
        malformed = replace(result, identity_token=IdentityToken("other-lineage"))
    elif malformation == "references":
        malformed = replace(
            result,
            integrated_charter_result=_record(IntegratedCharterResult),
        )
    else:
        malformed = replace(result, check_results=())

    with pytest.raises(FinalCharterIntegrityFailure) as raised:
        FinalCharterProgressionPrecondition(lambda value: True).require(malformed)

    assert raised.value.final_charter_result is malformed


def test_malformed_progression_rule_result_fails_closed() -> None:
    result = _result(
        (CharterCheckResult("check-1", CharterCheckStatus.PASS),),
        status="PASS",
    )

    with pytest.raises(FinalCharterProgressionError) as raised:
        FinalCharterProgressionPrecondition(
            lambda value: cast(bool, "yes")
        ).require(result)

    assert raised.value.final_charter_result is result


def test_progression_precondition_introduces_no_later_stage_objects() -> None:
    source = inspect.getsource(FinalCharterProgressionPrecondition).lower()
    forbidden = (
        "cleanbound",
        "mixedbound",
        "fossilbound",
        "harmbound",
        "boundarystress",
        "biobound",
        "restorationbound",
        "unbound",
        "boundpathway",
        "bindinghandler",
        "transitionpathwayvalidator",
        "scoring",
        "ranking",
        "weighting",
        "voting",
        "optimization",
    )

    assert all(term not in source for term in forbidden)
