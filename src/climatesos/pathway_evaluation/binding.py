"""Concrete Section 17 binding boundary without state determination logic."""

from dataclasses import dataclass

from .enums import BoundState
from .final_pathway_assembly import (
    FinalPathwayAssembly,
    FinalPathwayAssemblyInvariantError,
)
from .models import (
    BoundPathway,
    EvaluationTrace,
    FinalPathwayResult,
    IdentityToken,
)


class BindingInvariantError(ValueError):
    """Raised for programmer-level or completed-pathway binding violations."""


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
        raise BindingInvariantError("Binding requires exactly FinalPathwayResult")
    if type(identity_token) is not IdentityToken:
        raise BindingInvariantError("Binding requires exactly IdentityToken")
    try:
        if type(result.evaluation_trace) is not EvaluationTrace:
            raise BindingInvariantError(
                "FinalPathwayResult must preserve exactly EvaluationTrace"
            )
        trace = result.evaluation_trace
        FinalPathwayAssembly._validate_inputs(
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
        FinalPathwayAssembly._validate_result(
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
        identity_token=identity_token,
        evaluation_run_id=evaluation_run_id,
        user_id=user_id,
        pathway_id=pathway_id,
        binding_mechanism_id=binding_mechanism_id,
        binding_mechanism_version=binding_mechanism_version,
    )


@dataclass(frozen=True, slots=True)
class BindingHandler:
    """Attach a valid supplied state or emit the handler-owned NoAck fallback."""

    def bind(
        self,
        final_pathway_result: FinalPathwayResult,
        applicable_bound_state: BoundState | None,
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
                identity_token,
                evaluation_run_id,
                user_id,
                pathway_id,
                binding_mechanism_id,
                binding_mechanism_version,
            )
        if (
            type(applicable_bound_state) is not BoundState
            or applicable_bound_state is BoundState.NO_ACK
        ):
            return _bound_pathway(
                final_pathway_result,
                BoundState.NO_ACK,
                identity_token,
                evaluation_run_id,
                user_id,
                pathway_id,
                binding_mechanism_id,
                binding_mechanism_version,
            )
        return _bound_pathway(
            final_pathway_result,
            applicable_bound_state,
            identity_token,
            evaluation_run_id,
            user_id,
            pathway_id,
            binding_mechanism_id,
            binding_mechanism_version,
        )
