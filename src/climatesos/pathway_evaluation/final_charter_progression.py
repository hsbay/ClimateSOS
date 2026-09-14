"""Fail-closed handoff precondition for a completed Final Charter result."""

from collections.abc import Callable
from dataclasses import dataclass

from .charter_evaluation import (
    _INTEGRITY_FAILURE_STATUSES,
    _malformed_result_error,
)
from .models import (
    CharterCheckResult,
    EvaluationTrace,
    FinalCharterResult,
    FinalPathwayResult,
    IdentityToken,
    InitialCharterResult,
    IntegratedCharterResult,
    PathwayEngineResult,
)

FinalCharterProgressionRuleFunction = Callable[[FinalCharterResult], bool]


class FinalCharterProgressionError(ValueError):
    """Base failure preserving the Final Charter diagnostic result."""

    def __init__(self, message: str, final_charter_result: FinalCharterResult) -> None:
        super().__init__(message)
        self.final_charter_result = final_charter_result


class FinalCharterIntegrityFailure(FinalCharterProgressionError):
    """Raised when Final Charter execution or result integrity failed."""


class FinalCharterProgressionProhibited(FinalCharterProgressionError):
    """Raised when the applicable Charter rule prohibits progression."""


def _validate_completed_result(result: FinalCharterResult) -> None:
    if type(result) is not FinalCharterResult:
        raise TypeError("Final Charter handoff requires exactly FinalCharterResult")
    final_pathway = result.final_pathway_result
    if type(final_pathway) is not FinalPathwayResult:
        raise FinalCharterIntegrityFailure(
            "Final Charter result must preserve exactly FinalPathwayResult",
            result,
        )
    trace = final_pathway.evaluation_trace
    if type(trace) is not EvaluationTrace:
        raise FinalCharterIntegrityFailure(
            "Final Charter pathway must preserve exactly EvaluationTrace",
            result,
        )
    initial = result.initial_charter_result
    integrated = result.integrated_charter_result
    engine = trace.pathway_engine_result
    if (
        type(initial) is not InitialCharterResult
        or type(integrated) is not IntegratedCharterResult
        or type(engine) is not PathwayEngineResult
        or initial is not trace.initial_charter_result
        or integrated is not trace.integrated_charter_result
        or integrated.initial_charter_result is not initial
        or integrated.pathway_engine_result is not engine
        or engine.initial_charter_result is not initial
    ):
        raise FinalCharterIntegrityFailure(
            "Final Charter result must preserve exact evaluation-lineage references",
            result,
        )
    if type(result.identity_token) is not IdentityToken:
        raise FinalCharterIntegrityFailure(
            "Final Charter result must preserve IdentityToken",
            result,
        )
    token_id = result.identity_token.token_id
    lineage_tokens = (
        final_pathway.identity_token,
        initial.identity_token,
        integrated.identity_token,
        engine.identity_token,
    )
    if not isinstance(token_id, str) or any(
        type(token) is not IdentityToken or token.token_id != token_id
        for token in lineage_tokens
    ):
        raise FinalCharterIntegrityFailure(
            "Final Charter result must preserve current IdentityToken lineage",
            result,
        )
    run_id = result.evaluation_run_id
    if not isinstance(run_id, str) or any(
        artifact.evaluation_run_id != run_id
        for artifact in (final_pathway, initial, integrated, engine)
    ):
        raise FinalCharterIntegrityFailure(
            "Final Charter result must preserve current evaluation_run_id",
            result,
        )
    metadata_is_valid = all(
        isinstance(value, str)
        for value in (result.evaluator_version, result.rule_set_version, result.status)
    ) and (result.execution_error is None or isinstance(result.execution_error, str))
    if not metadata_is_valid:
        raise FinalCharterIntegrityFailure(
            "Final Charter result metadata is malformed",
            result,
        )
    if not isinstance(result.check_results, tuple) or not result.check_results:
        raise FinalCharterIntegrityFailure(
            "Final Charter result must preserve every required check",
            result,
        )
    check_ids: list[str] = []
    for check in result.check_results:
        if type(check) is not CharterCheckResult or not isinstance(check.check_id, str):
            raise FinalCharterIntegrityFailure(
                "Final Charter result contains a malformed check",
                result,
            )
        malformed_error = _malformed_result_error(check, check.check_id)
        if malformed_error is not None:
            raise FinalCharterIntegrityFailure(malformed_error, result)
        check_ids.append(check.check_id)
    if len(set(check_ids)) != len(check_ids):
        raise FinalCharterIntegrityFailure(
            "Final Charter result must contain one result per required check",
            result,
        )


@dataclass(frozen=True, slots=True)
class FinalCharterProgressionPrecondition:
    """Require explicit Charter-rule permission for the next controlled stage."""

    progression_rule: FinalCharterProgressionRuleFunction

    def require(self, result: FinalCharterResult) -> FinalCharterResult:
        """Return the exact result only when integrity and Charter permission hold."""

        _validate_completed_result(result)
        integrity_checks = tuple(
            check
            for check in result.check_results
            if check.status in _INTEGRITY_FAILURE_STATUSES
        )
        has_integrity_failure = (
            result.status == "ERROR"
            or result.execution_error is not None
            or bool(integrity_checks)
        )
        if has_integrity_failure:
            raise FinalCharterIntegrityFailure(
                "Final Charter evaluator-integrity failure prevents progression",
                result,
            )
        permitted = self.progression_rule(result)
        if type(permitted) is not bool:
            raise FinalCharterProgressionError(
                "Final Charter progression rule must return bool",
                result,
            )
        if not permitted:
            raise FinalCharterProgressionProhibited(
                "Applicable Charter rule prohibits progression",
                result,
            )
        return result
