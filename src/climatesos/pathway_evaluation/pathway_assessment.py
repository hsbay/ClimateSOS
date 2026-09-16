"""Concrete Section 18 final pathway-assessment boundary."""

from collections.abc import Callable
from dataclasses import dataclass

from .enums import BoundState
from .models import (
    BoundPathway,
    ComparisonFinding,
    FinalCharterResult,
    IdentityToken,
    InitialCharterResult,
    IntegratedCharterResult,
    OpaqueReference,
    PathwayAssessment,
    ProductEvaluationContext,
    ProductPathway,
    TransitionPathway,
)


@dataclass(frozen=True, slots=True)
class _PathwayAssessmentDetermination:
    """Private substantive determinations used to construct PathwayAssessment."""

    assessment_outcome: str
    replacement_fitness: bool | None
    material_comparative_findings: tuple[ComparisonFinding, ...]
    material_improvements: tuple[ComparisonFinding, ...]
    material_regressions: tuple[ComparisonFinding, ...]
    progression_preventing_findings: tuple[OpaqueReference, ...]
    upstream_result_references: tuple[OpaqueReference, ...]
    correctable: bool | None
    corrective_requirement: str | None
    corrective_justification: str | None
    successor_evaluation_conditions: tuple[str, ...]


_PathwayAssessmentDeterminationFunction = Callable[
    [BoundPathway, FinalCharterResult],
    _PathwayAssessmentDetermination,
]


class PathwayAssessmentInvariantError(ValueError):
    """Raised when Section 18 input or output integrity is invalid."""


def _require_nonempty_string(value: object, description: str) -> str:
    if not isinstance(value, str) or not value:
        raise PathwayAssessmentInvariantError(
            f"{description} must be a non-empty string"
        )
    return value


def _require_reference_tuple(
    value: object,
    description: str,
) -> tuple[OpaqueReference, ...]:
    if not isinstance(value, tuple) or not all(
        type(item) is OpaqueReference for item in value
    ):
        raise PathwayAssessmentInvariantError(
            f"{description} must be a tuple of OpaqueReference objects"
        )
    return value


def _require_comparison_finding_tuple(
    value: object,
    description: str,
) -> tuple[ComparisonFinding, ...]:
    if not isinstance(value, tuple) or not all(
        type(item) is ComparisonFinding for item in value
    ):
        raise PathwayAssessmentInvariantError(
            f"{description} must be a tuple of ComparisonFinding objects"
        )
    return value


def _validate_inputs(
    product_pathway: ProductPathway,
    initial_charter_result: InitialCharterResult,
    integrated_charter_result: IntegratedCharterResult,
    final_charter_result: FinalCharterResult,
    bound_pathway: BoundPathway,
    product_evaluation_context: ProductEvaluationContext,
    candidate_transition_pathway: TransitionPathway,
    authoritative_transition_pathway: TransitionPathway,
    identity_token: IdentityToken,
    evaluation_run_id: str,
    user_id: str,
    pathway_id: str,
    pathway_assessment_id: str,
) -> None:
    _require_nonempty_string(evaluation_run_id, "evaluation_run_id")
    _require_nonempty_string(user_id, "user_id")
    _require_nonempty_string(pathway_id, "pathway_id")
    _require_nonempty_string(pathway_assessment_id, "pathway_assessment_id")

    if type(product_pathway) is not ProductPathway:
        raise PathwayAssessmentInvariantError(
            "Assessment requires exactly ProductPathway"
        )
    if type(initial_charter_result) is not InitialCharterResult:
        raise PathwayAssessmentInvariantError(
            "Assessment requires exactly InitialCharterResult"
        )
    if type(integrated_charter_result) is not IntegratedCharterResult:
        raise PathwayAssessmentInvariantError(
            "Assessment requires exactly IntegratedCharterResult"
        )
    if type(final_charter_result) is not FinalCharterResult:
        raise PathwayAssessmentInvariantError(
            "Assessment requires exactly FinalCharterResult"
        )
    if type(bound_pathway) is not BoundPathway:
        raise PathwayAssessmentInvariantError(
            "Assessment requires exactly BoundPathway"
        )
    if type(product_evaluation_context) is not ProductEvaluationContext:
        raise PathwayAssessmentInvariantError(
            "Assessment requires exactly ProductEvaluationContext"
        )
    if type(candidate_transition_pathway) is not TransitionPathway:
        raise PathwayAssessmentInvariantError(
            "Assessment requires exactly candidate TransitionPathway"
        )
    if type(authoritative_transition_pathway) is not TransitionPathway:
        raise PathwayAssessmentInvariantError(
            "Assessment requires exactly authoritative TransitionPathway"
        )
    if type(identity_token) is not IdentityToken:
        raise PathwayAssessmentInvariantError(
            "Assessment requires exactly IdentityToken"
        )

    try:
        final_pathway = bound_pathway.final_pathway_result
        trace = final_pathway.evaluation_trace

        if not isinstance(bound_pathway.bound_state, BoundState):
            raise PathwayAssessmentInvariantError(
                "BoundPathway must carry BoundState"
            )
        if bound_pathway.bound_state is BoundState.NO_ACK:
            raise PathwayAssessmentInvariantError(
                "NoAck BoundPathway cannot enter PathwayAssessment evaluation"
            )

        if final_charter_result.final_pathway_result is not final_pathway:
            raise PathwayAssessmentInvariantError(
                "FinalCharterResult must preserve the assessed FinalPathwayResult"
            )

        if final_pathway.product_pathway is not product_pathway:
            raise PathwayAssessmentInvariantError(
                "Supplied ProductPathway must be the completed evaluated pathway"
            )
        if trace.initial_charter_result is not initial_charter_result:
            raise PathwayAssessmentInvariantError(
                "Supplied InitialCharterResult must be the traced initial result"
            )
        if trace.integrated_charter_result is not integrated_charter_result:
            raise PathwayAssessmentInvariantError(
                "Supplied IntegratedCharterResult must be the traced integrated result"
            )
        if final_pathway.candidate_transition_pathway is not (
            candidate_transition_pathway
        ):
            raise PathwayAssessmentInvariantError(
                "Supplied candidate TransitionPathway must be the completed candidate"
            )
        if final_pathway.authoritative_transition_pathway is not (
            authoritative_transition_pathway
        ):
            raise PathwayAssessmentInvariantError(
                "Supplied authoritative TransitionPathway must be "
                "the evaluation reference"
            )
        if candidate_transition_pathway.product_pathway is not product_pathway:
            raise PathwayAssessmentInvariantError(
                "Candidate TransitionPathway must preserve the ProductPathway"
            )
        if candidate_transition_pathway.authoritative_transition_pathway is not (
            authoritative_transition_pathway
        ):
            raise PathwayAssessmentInvariantError(
                "Candidate must preserve the authoritative TransitionPathway"
            )

        if bound_pathway.identity_token.token_id != identity_token.token_id:
            raise PathwayAssessmentInvariantError(
                "BoundPathway must preserve the canonical IdentityToken lineage"
            )
        if final_charter_result.identity_token.token_id != identity_token.token_id:
            raise PathwayAssessmentInvariantError(
                "FinalCharterResult must preserve the canonical IdentityToken lineage"
            )
        if final_pathway.identity_token.token_id != identity_token.token_id:
            raise PathwayAssessmentInvariantError(
                "FinalPathwayResult must preserve the canonical IdentityToken lineage"
            )
        if product_pathway.identity_token.token_id != identity_token.token_id:
            raise PathwayAssessmentInvariantError(
                "ProductPathway must preserve the canonical IdentityToken lineage"
            )

        if any(
            value != evaluation_run_id
            for value in (
                bound_pathway.evaluation_run_id,
                final_charter_result.evaluation_run_id,
                final_pathway.evaluation_run_id,
                product_pathway.evaluation_run_id,
            )
        ):
            raise PathwayAssessmentInvariantError(
                "Assessment inputs must share one evaluation_run_id"
            )

        if any(
            value != user_id
            for value in (
                bound_pathway.user_id,
                final_pathway.user_id,
                product_pathway.user_id,
            )
        ):
            raise PathwayAssessmentInvariantError(
                "Assessment inputs must share one user_id"
            )

        if any(
            value != pathway_id
            for value in (
                bound_pathway.pathway_id,
                final_pathway.pathway_id,
                product_pathway.pathway_id,
            )
        ):
            raise PathwayAssessmentInvariantError(
                "Assessment inputs must share one pathway_id"
            )

        if (
            final_charter_result.initial_charter_result
            is not initial_charter_result
        ):
            raise PathwayAssessmentInvariantError(
                "FinalCharterResult must preserve the traced InitialCharterResult"
            )

        if (
            final_charter_result.integrated_charter_result
            is not integrated_charter_result
        ):
            raise PathwayAssessmentInvariantError(
                "FinalCharterResult must preserve the traced IntegratedCharterResult"
            )

    except AttributeError as error:
        raise PathwayAssessmentInvariantError(
            "Assessment requires structurally complete upstream results"
        ) from error


def _validate_determination(
    result: object,
) -> _PathwayAssessmentDetermination:
    if type(result) is not _PathwayAssessmentDetermination:
        raise PathwayAssessmentInvariantError(
            "Assessment determination function must return exactly "
            "_PathwayAssessmentDetermination"
        )

    _require_nonempty_string(result.assessment_outcome, "assessment_outcome")

    if result.replacement_fitness is not None and not isinstance(
        result.replacement_fitness,
        bool,
    ):
        raise PathwayAssessmentInvariantError(
            "replacement_fitness must be bool or None"
        )

    for value, description in (
        (result.material_comparative_findings, "material comparative findings"),
        (result.material_improvements, "material improvements"),
        (result.material_regressions, "material regressions"),
    ):
        _require_comparison_finding_tuple(value, description)

    for value, description in (
        (
            result.progression_preventing_findings,
            "progression-preventing findings",
        ),
        (result.upstream_result_references, "upstream result references"),
    ):
        _require_reference_tuple(value, description)

    if result.correctable is not None and not isinstance(result.correctable, bool):
        raise PathwayAssessmentInvariantError(
            "correctable must be bool or None"
        )

    if result.corrective_requirement is not None:
        _require_nonempty_string(
            result.corrective_requirement,
            "corrective_requirement",
        )
        _require_nonempty_string(
            result.corrective_justification,
            "corrective_justification",
        )
    elif result.corrective_justification is not None:
        raise PathwayAssessmentInvariantError(
            "corrective_justification requires a corrective_requirement"
        )

    if not isinstance(result.successor_evaluation_conditions, tuple) or not all(
        isinstance(condition, str) and condition
        for condition in result.successor_evaluation_conditions
    ):
        raise PathwayAssessmentInvariantError(
            "successor_evaluation_conditions must be non-empty strings"
        )

    return result


def _validate_result(
    result: PathwayAssessment,
    product_pathway: ProductPathway,
    initial_charter_result: InitialCharterResult,
    integrated_charter_result: IntegratedCharterResult,
    bound_pathway: BoundPathway,
    final_charter_result: FinalCharterResult,
    product_evaluation_context: ProductEvaluationContext,
    authoritative_transition_pathway: TransitionPathway,
    identity_token: IdentityToken,
    evaluation_run_id: str,
    user_id: str,
    pathway_assessment_id: str,
) -> None:
    if type(result) is not PathwayAssessment:
        raise PathwayAssessmentInvariantError(
            "PathwayAssessmentEvaluator must produce exactly PathwayAssessment"
        )

    try:
        if result.bound_pathway is not bound_pathway:
            raise PathwayAssessmentInvariantError(
                "PathwayAssessment must preserve the exact BoundPathway"
            )

        if result.final_charter_result is not final_charter_result:
            raise PathwayAssessmentInvariantError(
                "PathwayAssessment must preserve the exact FinalCharterResult"
            )

        if result.product_evaluation_context is not product_evaluation_context:
            raise PathwayAssessmentInvariantError(
                "PathwayAssessment must preserve the exact ProductEvaluationContext"
            )

        if result.identity_token.token_id != identity_token.token_id:
            raise PathwayAssessmentInvariantError(
                "PathwayAssessment must preserve the canonical IdentityToken lineage"
            )

        if result.product_pathway is not product_pathway:
            raise PathwayAssessmentInvariantError(
                "PathwayAssessment must preserve the exact ProductPathway"
            )

        if result.initial_charter_result is not initial_charter_result:
            raise PathwayAssessmentInvariantError(
                "PathwayAssessment must preserve the exact InitialCharterResult"
            )

        if result.integrated_charter_result is not integrated_charter_result:
            raise PathwayAssessmentInvariantError(
                "PathwayAssessment must preserve the exact IntegratedCharterResult"
            )

        if result.reference_transition_pathway is not authoritative_transition_pathway:
            raise PathwayAssessmentInvariantError(
                "PathwayAssessment must preserve the reference TransitionPathway"
            )

        if result.evaluation_run_id != evaluation_run_id:
            raise PathwayAssessmentInvariantError(
                "PathwayAssessment must preserve evaluation_run_id"
            )

        if result.user_id != user_id:
            raise PathwayAssessmentInvariantError(
                "PathwayAssessment must preserve user_id"
            )

        if result.pathway_assessment_id != pathway_assessment_id:
            raise PathwayAssessmentInvariantError(
                "PathwayAssessment must preserve pathway_assessment_id"
            )

    except AttributeError as error:
        raise PathwayAssessmentInvariantError(
            "PathwayAssessmentEvaluator produced an incomplete PathwayAssessment"
        ) from error


@dataclass(frozen=True, slots=True)
class PathwayAssessmentEvaluator:
    """Produce and validate one final assessment without revising upstream state."""

    determination_function: _PathwayAssessmentDeterminationFunction

    def evaluate(
        self,
        product_pathway: ProductPathway,
        initial_charter_result: InitialCharterResult,
        integrated_charter_result: IntegratedCharterResult,
        final_charter_result: FinalCharterResult,
        bound_pathway: BoundPathway,
        product_evaluation_context: ProductEvaluationContext,
        candidate_transition_pathway: TransitionPathway,
        authoritative_transition_pathway: TransitionPathway,
        identity_token: IdentityToken,
        evaluation_run_id: str,
        user_id: str,
        pathway_id: str,
        pathway_assessment_id: str,
    ) -> PathwayAssessment:
        """Evaluate one successfully bound pathway run."""

        _validate_inputs(
            product_pathway,
            initial_charter_result,
            integrated_charter_result,
            final_charter_result,
            bound_pathway,
            product_evaluation_context,
            candidate_transition_pathway,
            authoritative_transition_pathway,
            identity_token,
            evaluation_run_id,
            user_id,
            pathway_id,
            pathway_assessment_id,
        )

        determination = _validate_determination(
            self.determination_function(
                bound_pathway,
                final_charter_result,
            )
        )

        result = PathwayAssessment(
            identity_token=identity_token,
            evaluation_run_id=evaluation_run_id,
            pathway_assessment_id=pathway_assessment_id,
            user_id=user_id,
            product_pathway=product_pathway,
            initial_charter_result=initial_charter_result,
            integrated_charter_result=integrated_charter_result,
            final_charter_result=final_charter_result,
            bound_pathway=bound_pathway,
            product_evaluation_context=product_evaluation_context,
            assessment_outcome=determination.assessment_outcome,
            replacement_fitness=determination.replacement_fitness,
            material_comparative_findings=(
                determination.material_comparative_findings
            ),
            material_improvements=determination.material_improvements,
            material_regressions=determination.material_regressions,
            progression_preventing_findings=(
                determination.progression_preventing_findings
            ),
            upstream_result_references=(
                determination.upstream_result_references
            ),
            correctable=determination.correctable,
            corrective_requirement=determination.corrective_requirement,
            corrective_justification=determination.corrective_justification,
            successor_evaluation_conditions=(
                determination.successor_evaluation_conditions
            ),
            reference_transition_pathway=authoritative_transition_pathway,
        )

        _validate_result(
            result,
            product_pathway,
            initial_charter_result,
            integrated_charter_result,
            bound_pathway,
            final_charter_result,
            product_evaluation_context,
            authoritative_transition_pathway,
            identity_token,
            evaluation_run_id,
            user_id,
            pathway_assessment_id,
        )

        return result
