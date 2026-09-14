import inspect
from dataclasses import FrozenInstanceError, fields
from typing import TypeVar, get_args, get_type_hints

import pytest

from climatesos.pathway_evaluation import (
    ApplicableBoundState,
    BindingHandler,
    BoundPathway,
    BoundState,
    BoundStateDeterminationResult,
    BoundStateDeterminer,
    DeterminedBoundState,
    FinalCharterResult,
    FinalPathwayResult,
    IdentityToken,
)

T = TypeVar("T")


def _record(record_type: type[T], **values: object) -> T:
    record = object.__new__(record_type)
    for name, value in values.items():
        object.__setattr__(record, name, value)
    return record


def _applicable_state(state: DeterminedBoundState) -> ApplicableBoundState:
    return ApplicableBoundState(
        state=state,
        identity_token=IdentityToken("lineage-1"),
        evaluation_run_id="run-1",
        determination_rule_id="bound-state-rule",
        determination_rule_version="bound-state-rule-v1",
    )


def _bound_pathway(
    state: BoundState,
    determination: ApplicableBoundState | None,
) -> BoundPathway:
    return BoundPathway(
        final_pathway_result=_record(FinalPathwayResult),
        bound_state=state,
        bound_state_determination=determination,
        identity_token=(
            determination.identity_token
            if determination is not None
            else IdentityToken("lineage-1")
        ),
        evaluation_run_id="run-1",
        user_id="user-1",
        pathway_id="pathway-1",
        binding_mechanism_id="binding-rule",
        binding_mechanism_version="binding-rule-v1",
    )


def test_every_implemented_bound_state_is_independently_representable() -> None:
    expected = {
        "CleanBound",
        "MixedBound",
        "FossilBound",
        "NoAck",
        "Unbound",
        "HarmBound",
        "BoundaryStress",
        "BioBound",
        "RestorationBound",
    }

    assert {state.value for state in BoundState} == expected
    represented = tuple(_bound_pathway(state, None) for state in BoundState)
    assert tuple(item.bound_state for item in represented) == tuple(BoundState)


def test_implemented_bound_states_remain_materially_distinct() -> None:
    states = tuple(BoundState)
    distinct_pairs = (
        (BoundState.FOSSIL_BOUND, BoundState.MIXED_BOUND),
        (BoundState.HARM_BOUND, BoundState.BOUNDARY_STRESS),
        (BoundState.BIO_BOUND, BoundState.RESTORATION_BOUND),
    )

    assert len(states) == len(set(states)) == 9
    assert all(left.value != right.value for left, right in distinct_pairs)
    assert isinstance(BoundState.CLEAN_BOUND, BoundState)


def test_reserved_names_are_not_constructible_runtime_states() -> None:
    assert "CDRBound" not in {state.value for state in BoundState}
    assert "WaterBound" not in {state.value for state in BoundState}

    with pytest.raises(ValueError):
        BoundState("CDRBound")
    with pytest.raises(ValueError):
        BoundState("WaterBound")
    with pytest.raises(ValueError):
        DeterminedBoundState("CDRBound")
    with pytest.raises(ValueError):
        DeterminedBoundState("WaterBound")


def test_no_ack_and_unbound_are_distinct_immutable_states() -> None:
    no_ack = _bound_pathway(BoundState.NO_ACK, None)
    unbound_determination = _applicable_state(DeterminedBoundState.UNBOUND)
    unbound = _bound_pathway(BoundState.UNBOUND, unbound_determination)

    assert no_ack.bound_state is not unbound.bound_state
    assert no_ack.bound_state is BoundState.NO_ACK
    assert no_ack.bound_state_determination is None
    assert unbound.bound_state is BoundState.UNBOUND
    assert unbound.bound_state_determination is unbound_determination

    with pytest.raises(FrozenInstanceError):
        no_ack.bound_state = BoundState.UNBOUND  # type: ignore[misc]


def test_successful_determiner_output_cannot_represent_no_ack() -> None:
    assert "NoAck" not in {state.value for state in DeterminedBoundState}

    with pytest.raises(ValueError):
        DeterminedBoundState("NoAck")

    unbound = _applicable_state(DeterminedBoundState.UNBOUND)
    assert unbound.state is DeterminedBoundState.UNBOUND


def test_bound_pathway_is_immutable_and_preserves_exact_references() -> None:
    final_pathway = _record(FinalPathwayResult)
    applicable_state = _applicable_state(DeterminedBoundState.BOUNDARY_STRESS)
    identity_token = applicable_state.identity_token
    bound_pathway = BoundPathway(
        final_pathway_result=final_pathway,
        bound_state=BoundState.BOUNDARY_STRESS,
        bound_state_determination=applicable_state,
        identity_token=identity_token,
        evaluation_run_id="run-1",
        user_id="user-1",
        pathway_id="pathway-1",
        binding_mechanism_id="binding-rule",
        binding_mechanism_version="binding-rule-v1",
    )

    assert bound_pathway.final_pathway_result is final_pathway
    assert bound_pathway.bound_state is BoundState.BOUNDARY_STRESS
    assert bound_pathway.bound_state_determination is applicable_state
    assert bound_pathway.identity_token is identity_token
    assert bound_pathway.evaluation_run_id == "run-1"
    assert bound_pathway.user_id == "user-1"
    assert bound_pathway.pathway_id == "pathway-1"
    assert bound_pathway.binding_mechanism_id == "binding-rule"
    assert bound_pathway.binding_mechanism_version == "binding-rule-v1"

    with pytest.raises(FrozenInstanceError):
        bound_pathway.pathway_id = "changed"  # type: ignore[misc]


def test_determination_and_binding_protocols_keep_separate_ownership() -> None:
    determine_signature = inspect.signature(BoundStateDeterminer.determine)
    bind_signature = inspect.signature(BindingHandler.bind)
    determine_hints = get_type_hints(BoundStateDeterminer.determine)
    bind_hints = get_type_hints(BindingHandler.bind)

    assert tuple(determine_signature.parameters) == (
        "self",
        "final_charter_result",
    )
    assert determine_hints["final_charter_result"] is FinalCharterResult
    assert set(get_args(determine_hints["return"])) == {
        ApplicableBoundState,
        type(None),
    }
    assert tuple(bind_signature.parameters) == (
        "self",
        "final_pathway_result",
        "applicable_bound_state",
        "identity_token",
        "evaluation_run_id",
        "user_id",
        "pathway_id",
        "binding_mechanism_id",
        "binding_mechanism_version",
    )
    assert set(get_args(bind_hints["applicable_bound_state"])) == {
        ApplicableBoundState,
        type(None),
    }
    assert bind_hints["return"] is BoundPathway
    assert "determine" not in BindingHandler.__dict__


def test_binding_input_represents_usable_or_unusable_runtime_determination() -> None:
    usable: BoundStateDeterminationResult = _applicable_state(
        DeterminedBoundState.CLEAN_BOUND
    )
    unusable: BoundStateDeterminationResult = None

    assert isinstance(usable, ApplicableBoundState)
    assert usable.state is DeterminedBoundState.CLEAN_BOUND
    assert unusable is None


def test_foundation_contains_no_determination_or_later_assessment_surface() -> None:
    state_fields = {field.name for field in fields(ApplicableBoundState)}
    bound_fields = {field.name for field in fields(BoundPathway)}
    forbidden = {
        "pathway_assessment",
        "assessment_result",
        "replacement_fitness",
        "score",
        "rank",
        "weight",
        "vote",
        "optimization",
    }

    assert state_fields == {
        "state",
        "identity_token",
        "evaluation_run_id",
        "determination_rule_id",
        "determination_rule_version",
    }
    assert bound_fields == {
        "final_pathway_result",
        "bound_state",
        "bound_state_determination",
        "identity_token",
        "evaluation_run_id",
        "user_id",
        "pathway_id",
        "binding_mechanism_id",
        "binding_mechanism_version",
    }
    assert state_fields.isdisjoint(forbidden)
    assert bound_fields.isdisjoint(forbidden)
