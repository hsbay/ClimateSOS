import inspect
from dataclasses import FrozenInstanceError, fields
from typing import TypeVar, get_type_hints

import pytest

from climatesos.pathway_evaluation import (
    CharterCheckResult,
    CharterCheckStatus,
    CharterEvaluator,
    FinalCharterResult,
    FinalPathwayResult,
    IdentityToken,
    InitialCharterResult,
    IntegratedCharterResult,
)

T = TypeVar("T")


def _record(record_type: type[T], **values: object) -> T:
    record = object.__new__(record_type)
    for name, value in values.items():
        object.__setattr__(record, name, value)
    return record


def _final_charter_result(
    check_results: tuple[CharterCheckResult, ...],
    *,
    status: str = "COMPLETE",
) -> FinalCharterResult:
    identity_token = IdentityToken("lineage-1")
    initial = _record(InitialCharterResult)
    integrated = _record(IntegratedCharterResult)
    final_pathway = _record(FinalPathwayResult)
    return FinalCharterResult(
        identity_token=identity_token,
        evaluation_run_id="run-1",
        final_pathway_result=final_pathway,
        initial_charter_result=initial,
        integrated_charter_result=integrated,
        check_results=check_results,
        evaluator_version="final-charter-v1",
        rule_set_version="charter-rules-v1",
        status=status,
    )


def test_final_charter_result_is_immutable_and_preserves_exact_references() -> None:
    result = _final_charter_result(())
    final_pathway = result.final_pathway_result
    initial = result.initial_charter_result
    integrated = result.integrated_charter_result

    assert result.final_pathway_result is final_pathway
    assert result.initial_charter_result is initial
    assert result.integrated_charter_result is integrated
    assert result.identity_token.token_id == "lineage-1"
    assert result.evaluation_run_id == "run-1"

    with pytest.raises(FrozenInstanceError):
        result.status = "CHANGED"  # type: ignore[misc]


def test_final_stage_checks_remain_individual_ordered_and_duplicable() -> None:
    first = CharterCheckResult("check-1", CharterCheckStatus.FAIL)
    duplicate = CharterCheckResult("check-1", CharterCheckStatus.UNRESOLVED)
    third = CharterCheckResult("check-2", CharterCheckStatus.NOT_APPLICABLE)

    result = _final_charter_result((first, duplicate, third))

    assert result.check_results == (first, duplicate, third)
    assert result.check_results[0] is first
    assert result.check_results[1] is duplicate
    assert result.check_results[2] is third


@pytest.mark.parametrize(
    "check_status",
    [
        CharterCheckStatus.FAIL,
        CharterCheckStatus.UNRESOLVED,
        CharterCheckStatus.NOT_APPLICABLE,
    ],
)
def test_substantive_non_passing_check_states_remain_representable(
    check_status: CharterCheckStatus,
) -> None:
    check = CharterCheckResult("check-1", check_status)

    result = _final_charter_result((check,), status=check_status.value)

    assert result.check_results[0].status is check_status
    assert result.status == check_status.value


@pytest.mark.parametrize(
    "integrity_status",
    [
        CharterCheckStatus.ERROR,
        CharterCheckStatus.MISSING,
        CharterCheckStatus.NULL,
        CharterCheckStatus.NOACK,
    ],
)
def test_integrity_failure_states_remain_distinct(
    integrity_status: CharterCheckStatus,
) -> None:
    check = CharterCheckResult("check-1", integrity_status)

    result = _final_charter_result((check,), status="ERROR")

    assert result.check_results[0].status is integrity_status
    assert result.status == "ERROR"


def test_final_evaluator_protocol_exposes_fresh_final_stage_boundary() -> None:
    signature = inspect.signature(CharterEvaluator.evaluate_final)
    hints = get_type_hints(CharterEvaluator.evaluate_final)

    assert tuple(signature.parameters) == (
        "self",
        "final_pathway_result",
        "context",
    )
    assert hints["final_pathway_result"] is FinalPathwayResult
    assert hints["return"] is FinalCharterResult


def test_final_result_does_not_reuse_prior_stage_check_results() -> None:
    prior_check = CharterCheckResult("check-1", CharterCheckStatus.PASS)
    final_check = CharterCheckResult("check-1", CharterCheckStatus.FAIL)
    initial = _record(InitialCharterResult, check_results=(prior_check,))
    integrated = _record(IntegratedCharterResult, check_results=(prior_check,))
    result = FinalCharterResult(
        identity_token=IdentityToken("lineage-1"),
        evaluation_run_id="run-1",
        final_pathway_result=_record(FinalPathwayResult),
        initial_charter_result=initial,
        integrated_charter_result=integrated,
        check_results=(final_check,),
        evaluator_version="final-charter-v1",
        rule_set_version="charter-rules-v1",
        status="FAIL",
    )

    assert result.check_results == (final_check,)
    assert result.check_results[0] is not prior_check
    assert result.check_results[0].status is CharterCheckStatus.FAIL


def test_final_charter_foundation_has_no_section_17_or_scalar_surfaces() -> None:
    field_names = {field.name.lower() for field in fields(FinalCharterResult)}
    forbidden = {
        "cleanbound",
        "mixedbound",
        "fossilbound",
        "harmbound",
        "boundarystress",
        "biobound",
        "restorationbound",
        "unbound",
        "boundpathway",
        "pathwayassessment",
        "transitionpathwayvalidator",
        "authoritative_transition_commitment",
        "score",
        "rank",
        "weight",
        "vote",
        "optimization",
    }

    assert field_names.isdisjoint(forbidden)
