from climatesos import (
    GuardrailResolution,
    IdentityToken,
    Queue,
    QueueStatus,
    RemedyBus,
    RemedyBusStatus,
    ResultingState,
    ScenarioState,
    evaluate_token,
)

REQUIRED_QUEUES = (
    "Clean Supply Queue",
    "Deliverability Queue",
    "Adequacy Queue",
    "Project Finance Queue",
    "Permitting / Authorization Queue",
)


def _datacenter_token(
    guardrail_resolution: GuardrailResolution = GuardrailResolution.PASS,
    resulting_state: ResultingState | None = None,
) -> IdentityToken:
    return IdentityToken(
        name="DataCenterLoadToken",
        created_year=2026,
        ttl_years=3,
        required_queues=REQUIRED_QUEUES,
        guardrail_resolution=guardrail_resolution,
        resulting_state=resulting_state,
    )


def _queues(**overrides: QueueStatus) -> dict[str, Queue]:
    statuses = {
        "Clean Supply Queue": QueueStatus.CLEAR,
        "Deliverability Queue": QueueStatus.CLEAR,
        "Adequacy Queue": QueueStatus.CLEAR,
        "Project Finance Queue": QueueStatus.CLEAR,
        "Permitting / Authorization Queue": QueueStatus.CLEAR,
    }
    statuses.update(overrides)
    return {name: Queue(name=name, status=status) for name, status in statuses.items()}


def test_datacenter_case_a_blocks_bind_to_fallback() -> None:
    scenario = ScenarioState(
        current_year=2027,
        queues=_queues(
            **{
                "Deliverability Queue": QueueStatus.BLOCKED,
                "Adequacy Queue": QueueStatus.BLOCKED,
            }
        ),
        fossil_fallback_available=True,
    )

    result = evaluate_token(scenario, _datacenter_token())

    assert result.resulting_state == ResultingState.FOSSIL_BOUND
    assert result.guardrail_resolution == GuardrailResolution.PASS
    assert result.validity is False
    assert result.bottlenecks == ("Deliverability Queue", "Adequacy Queue")
    assert result.remedy_bus_status == RemedyBusStatus.NOT_APPLICABLE


def test_datacenter_case_b_cleanbound_but_unresolved_is_not_valid() -> None:
    scenario = ScenarioState(
        current_year=2027,
        queues=_queues(),
        fossil_fallback_available=False,
    )

    result = evaluate_token(
        scenario,
        _datacenter_token(guardrail_resolution=GuardrailResolution.UNRESOLVED),
    )

    assert result.resulting_state == ResultingState.CLEAN_BOUND
    assert result.guardrail_resolution == GuardrailResolution.UNRESOLVED
    assert result.validity is False
    assert result.bottlenecks == ()


def test_datacenter_case_c_remedybus_acceptance_re_evaluates_to_conditional_pass() -> None:
    scenario = ScenarioState(
        current_year=2027,
        queues=_queues(),
        fossil_fallback_available=False,
        remedy_bus=RemedyBus(
            status=RemedyBusStatus.REMEDY_ACCEPTED,
            conditions_verified=True,
        ),
    )

    result = evaluate_token(
        scenario,
        _datacenter_token(
            guardrail_resolution=GuardrailResolution.UNRESOLVED,
            resulting_state=ResultingState.HARM_BOUND,
        ),
    )

    assert result.resulting_state == ResultingState.CLEAN_BOUND
    assert result.guardrail_resolution == GuardrailResolution.CONDITIONAL_PASS
    assert result.validity is True
    assert result.remedy_bus_status == RemedyBusStatus.REMEDY_ACCEPTED
