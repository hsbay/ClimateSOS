"""Concrete Section 18 final pathway-assessment boundary."""

from collections.abc import Callable
from dataclasses import dataclass

from .enums import BoundState, ProductEvaluationContextMode
from .models import (
    BoundPathway,
    CharterCheckResult,
    ComparisonFinding,
    ContributionFinding,
    DocumentationFinding,
    FabricEvaluatorResult,
    FinalCharterResult,
    IdentityToken,
    InitialCharterResult,
    IntegratedCharterResult,
    NetOverallSystemContribution,
    NetOverallSystemRiskResult,
    OpaqueReference,
    PathwayAssessment,
    PathwayEngineResult,
    ProductEvaluationContext,
    ProductPathway,
    QueueEvaluatorResult,
    ScaleDiagnosticResult,
    ScaleFinding,
    SystemRiskFinding,
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


@dataclass(frozen=True, slots=True)
class _PathwayAssessmentLineage:
    """Material evaluator-owned conclusions retained at their summary boundary."""

    initial_charter_checks: tuple[CharterCheckResult, ...]
    integrated_charter_checks: tuple[CharterCheckResult, ...]
    final_charter_checks: tuple[CharterCheckResult, ...]
    supported_comparison_findings: tuple[ComparisonFinding, ...]
    queue_results: tuple[QueueEvaluatorResult, ...]
    fabric_results: tuple[FabricEvaluatorResult, ...]
    documentation_findings: tuple[DocumentationFinding, ...]
    contribution_findings: tuple[ContributionFinding, ...]
    scale_findings: tuple[ScaleFinding, ...]
    risk_findings: tuple[SystemRiskFinding, ...]
    candidate_conditions: tuple[str, ...]


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


def _require_exact_tuple(
    value: object,
    expected_type: type[object],
    description: str,
) -> None:
    if not isinstance(value, tuple) or not all(
        type(item) is expected_type for item in value
    ):
        raise PathwayAssessmentInvariantError(
            f"{description} must be a tuple of {expected_type.__name__} objects"
        )


def _collect_material_lineage(
    bound_pathway: BoundPathway,
    initial_charter_result: InitialCharterResult,
    integrated_charter_result: IntegratedCharterResult,
    final_charter_result: FinalCharterResult,
    candidate_transition_pathway: TransitionPathway,
) -> _PathwayAssessmentLineage:
    """Follow the concrete Section 18 spine without flattening subordinates."""

    final_pathway = bound_pathway.final_pathway_result
    trace = final_pathway.evaluation_trace
    engine = trace.pathway_engine_result
    contribution = trace.net_overall_system_contribution
    scale = trace.scale_diagnostic_result
    risk = final_pathway.net_overall_system_risk_result

    exact_results = (
        (engine, PathwayEngineResult, "Pathway engine result"),
        (
            contribution,
            NetOverallSystemContribution,
            "Net overall system contribution",
        ),
        (scale, ScaleDiagnosticResult, "Scale diagnostic result"),
        (risk, NetOverallSystemRiskResult, "Net overall system risk result"),
    )
    for exact_result, exact_type, exact_description in exact_results:
        if type(exact_result) is not exact_type:
            raise PathwayAssessmentInvariantError(
                f"{exact_description} must preserve exactly {exact_type.__name__}"
            )

    exact_relationships = (
        (engine.initial_charter_result is initial_charter_result, "engine/initial"),
        (
            integrated_charter_result.pathway_engine_result is engine,
            "integrated Charter/engine",
        ),
        (
            contribution.pathway_engine_result is engine,
            "contribution/engine",
        ),
        (
            contribution.integrated_charter_result is integrated_charter_result,
            "contribution/integrated Charter",
        ),
        (
            scale.net_overall_system_contribution is contribution,
            "scale/contribution",
        ),
        (
            candidate_transition_pathway.net_overall_system_contribution
            is contribution,
            "candidate/contribution",
        ),
        (
            candidate_transition_pathway.scale_diagnostic_result is scale,
            "candidate/scale",
        ),
        (
            risk.candidate_transition_pathway is candidate_transition_pathway,
            "risk/candidate",
        ),
        (
            risk.authoritative_transition_pathway
            is final_pathway.authoritative_transition_pathway,
            "risk/authoritative transition",
        ),
    )
    for is_exact, relationship in exact_relationships:
        if not is_exact:
            raise PathwayAssessmentInvariantError(
                f"Assessment lineage must preserve the exact {relationship} reference"
            )

    tuple_results = (
        (
            initial_charter_result.check_results,
            CharterCheckResult,
            "Initial Charter checks",
        ),
        (
            integrated_charter_result.check_results,
            CharterCheckResult,
            "Integrated Charter checks",
        ),
        (
            final_charter_result.check_results,
            CharterCheckResult,
            "Final Charter checks",
        ),
        (
            engine.direct_comparison_findings,
            ComparisonFinding,
            "Direct comparison findings",
        ),
        (
            engine.substitution_combination_findings,
            ComparisonFinding,
            "Substitution-combination findings",
        ),
        (
            engine.downstream_propagation_findings,
            ComparisonFinding,
            "Downstream propagation findings",
        ),
        (engine.queue_results, QueueEvaluatorResult, "Queue evaluator results"),
        (engine.fabric_results, FabricEvaluatorResult, "Fabric evaluator results"),
        (
            engine.documentation_findings,
            DocumentationFinding,
            "Documentation findings",
        ),
        (
            contribution.contribution_findings,
            ContributionFinding,
            "Contribution findings",
        ),
        (scale.scale_findings, ScaleFinding, "Scale findings"),
        (risk.risk_findings, SystemRiskFinding, "System risk findings"),
    )
    for tuple_values, tuple_type, tuple_description in tuple_results:
        _require_exact_tuple(tuple_values, tuple_type, tuple_description)

    available_comparison_findings = (
        engine.direct_comparison_findings
        + engine.substitution_combination_findings
        + engine.downstream_propagation_findings
    )
    supported_comparison_findings: list[ComparisonFinding] = []
    for owner, description in (
        *(
            (finding, "Contribution supporting comparison findings")
            for finding in contribution.contribution_findings
        ),
        *(
            (finding, "Scale supporting comparison findings")
            for finding in scale.scale_findings
        ),
    ):
        support_references = owner.supporting_comparison_findings
        _require_exact_tuple(support_references, ComparisonFinding, description)
        if any(
            not any(
                support_reference is available_finding
                for available_finding in available_comparison_findings
            )
            for support_reference in support_references
        ):
            raise PathwayAssessmentInvariantError(
                f"{description} must preserve PathwayEngineResult references"
            )
        supported_comparison_findings.extend(support_references)

    candidate_condition_groups = (
        candidate_transition_pathway.conditions,
        candidate_transition_pathway.timing_conditions,
        candidate_transition_pathway.sequencing_conditions,
        candidate_transition_pathway.contribution_conditions,
        candidate_transition_pathway.scale_conditions,
        candidate_transition_pathway.unresolved_conditions,
    )
    for condition_group in candidate_condition_groups:
        _require_exact_tuple(condition_group, str, "Candidate transition conditions")

    # Subordinate details remain on their owning evaluator conclusions.
    return _PathwayAssessmentLineage(
        initial_charter_checks=initial_charter_result.check_results,
        integrated_charter_checks=integrated_charter_result.check_results,
        final_charter_checks=final_charter_result.check_results,
        supported_comparison_findings=tuple(supported_comparison_findings),
        queue_results=engine.queue_results,
        fabric_results=engine.fabric_results,
        documentation_findings=engine.documentation_findings,
        contribution_findings=contribution.contribution_findings,
        scale_findings=scale.scale_findings,
        risk_findings=risk.risk_findings,
        candidate_conditions=tuple(
            condition
            for condition_group in candidate_condition_groups
            for condition in condition_group
        ),
    )


def _assessment_outcome(bound_state: BoundState) -> str:
    """Apply only the progression semantics explicitly defined for bound states."""

    if bound_state is BoundState.CLEAN_BOUND:
        return "successful"
    if bound_state is BoundState.MIXED_BOUND:
        return "restricted"
    if bound_state in {BoundState.FOSSIL_BOUND, BoundState.HARM_BOUND}:
        return "failed"
    if bound_state is BoundState.UNBOUND:
        return "unresolved"
    if bound_state in {
        BoundState.BOUNDARY_STRESS,
        BoundState.BIO_BOUND,
        BoundState.RESTORATION_BOUND,
    }:
        return bound_state.value
    raise PathwayAssessmentInvariantError(
        "Bound state does not establish a PathwayAssessment outcome"
    )


def _determine_assessment(
    bound_pathway: BoundPathway,
    initial_charter_result: InitialCharterResult,
    integrated_charter_result: IntegratedCharterResult,
    final_charter_result: FinalCharterResult,
    product_evaluation_context: ProductEvaluationContext,
    candidate_transition_pathway: TransitionPathway,
) -> _PathwayAssessmentDetermination:
    """Determine the conservative MVP assessment from the completed lineage."""

    _collect_material_lineage(
        bound_pathway,
        initial_charter_result,
        integrated_charter_result,
        final_charter_result,
        candidate_transition_pathway,
    )

    # ComparisonFinding has no structured improvement/regression discriminator,
    # and the completed models establish neither correction nor replacement
    # fitness semantics. Preserve those unknowns instead of parsing open prose.
    del product_evaluation_context
    return _PathwayAssessmentDetermination(
        assessment_outcome=_assessment_outcome(bound_pathway.bound_state),
        replacement_fitness=None,
        material_comparative_findings=(),
        material_improvements=(),
        material_regressions=(),
        progression_preventing_findings=(),
        upstream_result_references=(),
        correctable=None,
        corrective_requirement=None,
        corrective_justification=None,
        successor_evaluation_conditions=(),
    )


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
    if not isinstance(
        product_evaluation_context.context_mode,
        ProductEvaluationContextMode,
    ):
        raise PathwayAssessmentInvariantError(
            "ProductEvaluationContext must carry ProductEvaluationContextMode"
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
            raise PathwayAssessmentInvariantError("BoundPathway must carry BoundState")
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

        if final_charter_result.initial_charter_result is not initial_charter_result:
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

    for comparison_value, comparison_description in (
        (result.material_comparative_findings, "material comparative findings"),
        (result.material_improvements, "material improvements"),
        (result.material_regressions, "material regressions"),
    ):
        _require_comparison_finding_tuple(comparison_value, comparison_description)

    for reference_value, reference_description in (
        (
            result.progression_preventing_findings,
            "progression-preventing findings",
        ),
        (result.upstream_result_references, "upstream result references"),
    ):
        _require_reference_tuple(reference_value, reference_description)

    if result.correctable is not None and not isinstance(result.correctable, bool):
        raise PathwayAssessmentInvariantError("correctable must be bool or None")

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

    determination_function: _PathwayAssessmentDeterminationFunction | None = None

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

        if self.determination_function is None:
            raw_determination: object = _determine_assessment(
                bound_pathway,
                initial_charter_result,
                integrated_charter_result,
                final_charter_result,
                product_evaluation_context,
                candidate_transition_pathway,
            )
        else:
            raw_determination = self.determination_function(
                bound_pathway,
                final_charter_result,
            )
        determination = _validate_determination(raw_determination)

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
            material_comparative_findings=(determination.material_comparative_findings),
            material_improvements=determination.material_improvements,
            material_regressions=determination.material_regressions,
            progression_preventing_findings=(
                determination.progression_preventing_findings
            ),
            upstream_result_references=(determination.upstream_result_references),
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
