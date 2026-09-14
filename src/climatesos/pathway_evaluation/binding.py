"""Validated Section 17 binding boundary without state determination logic."""

from dataclasses import dataclass

from .enums import BoundState, DeterminedBoundState
from .final_pathway_assembly import (
    FinalPathwayAssemblyInvariantError,
    ValidatedFinalPathwayAssembly,
)
from .models import (
    ApplicableBoundState,
    BoundPathway,
    EvaluationTrace,
    FinalPathwayResult,
    IdentityToken,
)

_BOUND_STATE_MAP = {
    DeterminedBoundState.CLEAN_BOUND: BoundState.CLEAN_BOUND,
    DeterminedBoundState.MIXED_BOUND: BoundState.MIXED_BOUND,
    DeterminedBoundState.FOSSIL_BOUND: BoundState.FOSSIL_BOUND,
    DeterminedBoundState.UNBOUND: BoundState.UNBOUND,
    DeterminedBoundState.HARM_BOUND: BoundState.HARM_BOUND,
    DeterminedBoundState.BOUNDARY_STRESS: BoundState.BOUNDARY_STRESS,
    DeterminedBoundState.BIO_BOUND: BoundState.BIO_BOUND,
    DeterminedBoundState.RESTORATION_BOUND: BoundState.RESTORATION_BOUND,
}


class BindingInvariantError(ValueError):
    """Raised for programmer-level or completed-pathway binding violations."""


class BoundPathwayProgressionError(ValueError):
    """Raised when a bound result cannot enter ordinary downstream flow."""


def _require_nonempty_string(value: object, description: str) -> str:
    if not isinstance(value, str) or not value:
        raise BindingInvariantError(f"{description} must be a non-empty string")
    return value


def _validate_final_pathway(
    result: FinalPathwayResult,
    identity_token: IdentityToken,
    evaluation_run_id: str,
    user_id: str,
    pathway_id: str,
) -> None:
    if type(result) is not FinalPathwayResult:
        raise BindingInvariantError(
            "Binding requires exactly FinalPathwayResult"
        )
    if type(identity_token) is not IdentityToken:
        raise BindingInvariantError("Binding requires exactly IdentityToken")
    try:
        if type(result.evaluation_trace) is not EvaluationTrace:
            raise BindingInvariantError(
                "FinalPathwayResult must preserve exactly EvaluationTrace"
            )
        trace = result.evaluation_trace
        ValidatedFinalPathwayAssembly._validate_inputs(
            result.product_pathway,
            result.authoritative_transition_pathway,
            result.candidate_transition_pathway,
            result.net_overall_system_risk_result,
            trace.initial_charter_result,
            trace.pathway_engine_result,
            trace.integrated_charter_result,
            trace.net_overall_system_contribution,
            trace.scale_diagnostic_result,
            identity_token,
            evaluation_run_id,
            user_id,
            pathway_id,
        )
        ValidatedFinalPathwayAssembly._validate_result(
            result,
            result.product_pathway,
            result.authoritative_transition_pathway,
            result.candidate_transition_pathway,
            result.net_overall_system_risk_result,
            trace.initial_charter_result,
            trace.pathway_engine_result,
            trace.integrated_charter_result,
            trace.net_overall_system_contribution,
            trace.scale_diagnostic_result,
            identity_token,
            evaluation_run_id,
            user_id,
            pathway_id,
        )
    except (AttributeError, FinalPathwayAssemblyInvariantError) as error:
        raise BindingInvariantError(
            "Binding requires a structurally valid current FinalPathwayResult"
        ) from error


def _bound_pathway(
    final_pathway_result: FinalPathwayResult,
    bound_state: BoundState,
    determination: ApplicableBoundState | None,
    identity_token: IdentityToken,
    evaluation_run_id: str,
    user_id: str,
    pathway_id: str,
    binding_mechanism_id: str,
    binding_mechanism_version: str,
) -> BoundPathway:
    return BoundPathway(
        final_pathway_result=final_pathway_result,
        bound_state=bound_state,
        bound_state_determination=determination,
        identity_token=identity_token,
        evaluation_run_id=evaluation_run_id,
        user_id=user_id,
        pathway_id=pathway_id,
        binding_mechanism_id=binding_mechanism_id,
        binding_mechanism_version=binding_mechanism_version,
    )


@dataclass(frozen=True, slots=True)
class ValidatedBindingHandler:
    """Attach a valid supplied state or emit the handler-owned NoAck fallback."""

    def bind(
        self,
        final_pathway_result: FinalPathwayResult,
        applicable_bound_state: ApplicableBoundState | None,
        identity_token: IdentityToken,
        evaluation_run_id: str,
        user_id: str,
        pathway_id: str,
        binding_mechanism_id: str,
        binding_mechanism_version: str,
    ) -> BoundPathway:
        """Produce one immutable binding result without re-evaluating state."""

        _require_nonempty_string(evaluation_run_id, "evaluation_run_id")
        _require_nonempty_string(user_id, "user_id")
        _require_nonempty_string(pathway_id, "pathway_id")
        _require_nonempty_string(binding_mechanism_id, "Binding mechanism identity")
        _require_nonempty_string(
            binding_mechanism_version,
            "Binding mechanism version",
        )
        _validate_final_pathway(
            final_pathway_result,
            identity_token,
            evaluation_run_id,
            user_id,
            pathway_id,
        )
        if applicable_bound_state is None:
            return _bound_pathway(
                final_pathway_result,
                BoundState.NO_ACK,
                None,
                identity_token,
                evaluation_run_id,
                user_id,
                pathway_id,
                binding_mechanism_id,
                binding_mechanism_version,
            )
        if type(applicable_bound_state) is not ApplicableBoundState:
            raise BindingInvariantError(
                "Binding determination must be ApplicableBoundState or None"
            )
        try:
            determination_is_usable = (
                type(applicable_bound_state.state) is DeterminedBoundState
                and type(applicable_bound_state.identity_token) is IdentityToken
                and applicable_bound_state.identity_token.token_id
                == identity_token.token_id
                and applicable_bound_state.evaluation_run_id == evaluation_run_id
            )
        except AttributeError:
            determination_is_usable = False
        if not determination_is_usable:
            return _bound_pathway(
                final_pathway_result,
                BoundState.NO_ACK,
                None,
                identity_token,
                evaluation_run_id,
                user_id,
                pathway_id,
                binding_mechanism_id,
                binding_mechanism_version,
            )
        return _bound_pathway(
            final_pathway_result,
            _BOUND_STATE_MAP[applicable_bound_state.state],
            applicable_bound_state,
            identity_token,
            evaluation_run_id,
            user_id,
            pathway_id,
            binding_mechanism_id,
            binding_mechanism_version,
        )


@dataclass(frozen=True, slots=True)
class BoundPathwayProgressionPrecondition:
    """Prevent handler-owned NoAck from entering ordinary downstream flow."""

    def require(self, result: BoundPathway) -> BoundPathway:
        """Return the exact ordinary result and reject NoAck."""

        if type(result) is not BoundPathway:
            raise BoundPathwayProgressionError(
                "Bound pathway progression requires exactly BoundPathway"
            )
        if result.bound_state is BoundState.NO_ACK:
            raise BoundPathwayProgressionError(
                "NoAck BoundPathway cannot enter ordinary downstream progression"
            )
        return result
