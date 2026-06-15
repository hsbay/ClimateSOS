"""Alignment-switch evaluator for the ClimateSOS v0.7 toy runtime."""

from .models import EvaluationResult, IdentityToken, ScenarioState
from .states import (
    GuardrailResolution,
    QueueStatus,
    RemedyBusStatus,
    RemedyEligibility,
    ResultingState,
)

_ACCEPTABLE_STATES = {ResultingState.CLEAN_BOUND}
_VALID_GUARDRAILS = {
    GuardrailResolution.PASS,
    GuardrailResolution.CONDITIONAL_PASS,
}


def evaluate_token(scenario: ScenarioState, token: IdentityToken) -> EvaluationResult:
    """Evaluate one identity token against the v0.7 data-center semantics.

    This is intentionally small. It is not a calibrated model or a policy
    recommendation system. It only tests the runtime seams defined by the
    v0.7 OS spec: queues, fossil fallback, guardrail resolution, RemedyBus,
    resulting state, and explanation trace.
    """

    trace: list[str] = [f"Evaluating token: {token.name}"]
    guardrail = token.guardrail_resolution

    blocking_queues = _blocking_required_queues(scenario, token)
    closed_queues = tuple(
        name
        for name in token.required_queues
        if scenario.queues[name].status == QueueStatus.CLOSED
    )

    if blocking_queues:
        trace.append(f"Blocking required queues: {', '.join(blocking_queues)}")
    else:
        trace.append("All required queues cleared or are only constrained.")

    if closed_queues:
        trace.append(f"Closed required queues: {', '.join(closed_queues)}")

    fabric_blockers = _blocking_required_fabrics(scenario, token)
    if fabric_blockers:
        trace.append(f"Blocking required fabrics: {', '.join(fabric_blockers)}")

    if _remedy_accepted_for_re_evaluation(scenario):
        trace.append("RemedyBus accepted corrective evidence and triggered re-evaluation.")
        if scenario.remedy_bus.conditions_verified:
            guardrail = GuardrailResolution.CONDITIONAL_PASS
            trace.append("Guardrail resolution updated to ConditionalPass after verified remedy.")
        else:
            guardrail = GuardrailResolution.UNRESOLVED
            trace.append("RemedyBus accepted process, but conditions are not verified; remains Unresolved.")

    if guardrail == GuardrailResolution.INVALID:
        return _handle_invalid_guardrail(
            scenario=scenario,
            token=token,
            trace=trace,
            bottlenecks=blocking_queues + fabric_blockers,
            closed_queues=closed_queues,
        )

    if blocking_queues or fabric_blockers:
        if scenario.fossil_fallback_available:
            trace.append(
                "Required clean pathway did not clear while fossil fallback remained available."
            )
            return _result(
                state=ResultingState.FOSSIL_BOUND,
                guardrail=guardrail,
                bottlenecks=blocking_queues + fabric_blockers,
                closed_queues=closed_queues,
                remedy_status=scenario.remedy_bus.status,
                trace=trace,
            )

        trace.append("Required clean pathway did not clear and fossil fallback is unavailable.")
        return _result(
            state=ResultingState.NO_ACK,
            guardrail=guardrail,
            bottlenecks=blocking_queues + fabric_blockers,
            closed_queues=closed_queues,
            remedy_status=scenario.remedy_bus.status,
            trace=trace,
        )

    if guardrail == GuardrailResolution.UNRESOLVED:
        trace.append(
            "Technical synchronization cleared, but guardrail conditions remain Unresolved."
        )
        return _result(
            state=ResultingState.CLEAN_BOUND,
            guardrail=guardrail,
            bottlenecks=(),
            closed_queues=closed_queues,
            remedy_status=scenario.remedy_bus.status,
            trace=trace,
        )

    if guardrail == GuardrailResolution.CONDITIONAL_PASS:
        if scenario.remedy_bus.status != RemedyBusStatus.NOT_APPLICABLE and not scenario.remedy_bus.conditions_verified:
            trace.append("ConditionalPass exists, but required conditions are not verified.")
            return _result(
                state=ResultingState.BOUNDARY_STRESS,
                guardrail=guardrail,
                bottlenecks=(),
                closed_queues=closed_queues,
                remedy_status=scenario.remedy_bus.status,
                trace=trace,
            )
        trace.append("Technical synchronization cleared with ConditionalPass guardrails.")
        return _result(
            state=ResultingState.CLEAN_BOUND,
            guardrail=guardrail,
            bottlenecks=(),
            closed_queues=closed_queues,
            remedy_status=scenario.remedy_bus.status,
            trace=trace,
        )

    trace.append("Technical synchronization cleared with Pass guardrails.")
    return _result(
        state=ResultingState.CLEAN_BOUND,
        guardrail=guardrail,
        bottlenecks=(),
        closed_queues=closed_queues,
        remedy_status=scenario.remedy_bus.status,
        trace=trace,
    )


def _blocking_required_queues(scenario: ScenarioState, token: IdentityToken) -> tuple[str, ...]:
    blockers: list[str] = []
    for queue_name in token.required_queues:
        if queue_name not in scenario.queues:
            raise KeyError(f"Required queue not found in scenario: {queue_name}")
        if scenario.queues[queue_name].is_blocking:
            blockers.append(queue_name)
    return tuple(blockers)


def _blocking_required_fabrics(scenario: ScenarioState, token: IdentityToken) -> tuple[str, ...]:
    blockers: list[str] = []
    for fabric_name in token.required_fabrics:
        if fabric_name not in scenario.fabrics:
            raise KeyError(f"Required fabric not found in scenario: {fabric_name}")
        if scenario.fabrics[fabric_name].is_blocking:
            blockers.append(fabric_name)
    return tuple(blockers)


def _remedy_accepted_for_re_evaluation(scenario: ScenarioState) -> bool:
    return scenario.remedy_bus.status in {
        RemedyBusStatus.REMEDY_ACCEPTED,
        RemedyBusStatus.REMEDY_CONDITIONED,
        RemedyBusStatus.RE_EVALUATION_EVENT,
    }


def _handle_invalid_guardrail(
    scenario: ScenarioState,
    token: IdentityToken,
    trace: list[str],
    bottlenecks: tuple[str, ...],
    closed_queues: tuple[str, ...],
) -> EvaluationResult:
    if token.remedy_eligibility == RemedyEligibility.REMEDIABLE:
        trace.append(
            "Guardrail is Invalid under current design; token may enter RemedyBus for corrective action only."
        )
        return _result(
            state=ResultingState.HARM_BOUND,
            guardrail=GuardrailResolution.INVALID,
            bottlenecks=bottlenecks,
            closed_queues=closed_queues,
            remedy_status=RemedyBusStatus.REMEDY_REQUIRED,
            trace=trace,
        )

    trace.append("Guardrail is Invalid and not marked remediable under current design.")
    return _result(
        state=ResultingState.HARM_BOUND,
        guardrail=GuardrailResolution.INVALID,
        bottlenecks=bottlenecks,
        closed_queues=closed_queues,
        remedy_status=scenario.remedy_bus.status,
        trace=trace,
    )


def _result(
    state: ResultingState,
    guardrail: GuardrailResolution,
    bottlenecks: tuple[str, ...],
    closed_queues: tuple[str, ...],
    remedy_status: RemedyBusStatus,
    trace: list[str],
) -> EvaluationResult:
    validity = state in _ACCEPTABLE_STATES and guardrail in _VALID_GUARDRAILS
    if validity:
        trace.append("Validity: true under v0.7 toy runtime rule.")
    else:
        trace.append("Validity: false under v0.7 toy runtime rule.")

    return EvaluationResult(
        resulting_state=state,
        guardrail_resolution=guardrail,
        validity=validity,
        bottlenecks=bottlenecks,
        closed_queues=closed_queues,
        remedy_bus_status=remedy_status,
        explanation_trace=tuple(trace),
    )
