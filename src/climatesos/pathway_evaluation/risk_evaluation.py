"""Net overall system-risk evaluation and invariant enforcement."""

from collections.abc import Callable
from dataclasses import dataclass
from typing import TypeVar

from .models import (
    ContributionFinding,
    NetOverallSystemContribution,
    NetOverallSystemRiskResult,
    OpaqueReference,
    PathwayRelationship,
    ProductPathway,
    ScaleDiagnosticResult,
    ScaleFinding,
    SourceReference,
    SystemRiskFinding,
    TransitionPathway,
)

T = TypeVar("T")

SystemRiskFindingFunction = Callable[
    [
        TransitionPathway,
        TransitionPathway,
        OpaqueReference | None,
        OpaqueReference | None,
        tuple[str, ...],
        tuple[str, ...],
        tuple[SourceReference, ...],
        tuple[SourceReference, ...],
        str,
        str,
        str,
    ],
    tuple[SystemRiskFinding, ...],
]


class NetOverallSystemRiskEvaluationInvariantError(ValueError):
    """Raised when risk-evaluation inputs or output are structurally incoherent."""


def _contains_reference(values: tuple[object, ...], candidate: object) -> bool:
    return any(value is candidate for value in values)


def _require_tuple_of(
    value: object,
    expected_type: type[T],
    description: str,
) -> tuple[T, ...]:
    if not isinstance(value, tuple) or not all(
        isinstance(item, expected_type) for item in value
    ):
        raise NetOverallSystemRiskEvaluationInvariantError(
            f"{description} must be a tuple of {expected_type.__name__} objects"
        )
    return value


@dataclass(frozen=True, slots=True)
class NetOverallSystemRiskEvaluator:
    """Evaluate candidate transition risk and construct one completed result."""

    candidate_reference_risk_function: SystemRiskFindingFunction
    system_interaction_risk_function: SystemRiskFindingFunction
    transition_delivery_risk_function: SystemRiskFindingFunction
    timing_sequencing_risk_function: SystemRiskFindingFunction
    bottleneck_failure_risk_function: SystemRiskFindingFunction
    fossil_persistence_fallback_risk_function: SystemRiskFindingFunction
    dependency_propagation_risk_function: SystemRiskFindingFunction
    biosphere_climate_risk_function: SystemRiskFindingFunction
    charter_unresolved_risk_function: SystemRiskFindingFunction
    evaluator_version: str
    rule_set_version: str

    def evaluate(
        self,
        candidate_transition_pathway: TransitionPathway,
        authoritative_transition_pathway: TransitionPathway,
        transition_context: OpaqueReference | None,
        system_context: OpaqueReference | None,
        assumptions: tuple[str, ...],
        uncertainties: tuple[str, ...],
        evidence_references: tuple[SourceReference, ...],
        provenance: tuple[SourceReference, ...],
        user_id: str,
        pathway_id: str,
        evaluation_run_id: str,
    ) -> NetOverallSystemRiskResult:
        """Evaluate the candidate and return one immutable risk result."""

        self._validate_inputs(
            candidate_transition_pathway,
            authoritative_transition_pathway,
            transition_context,
            system_context,
            assumptions,
            uncertainties,
            evidence_references,
            provenance,
            user_id,
            pathway_id,
            evaluation_run_id,
        )

        arguments = (
            candidate_transition_pathway,
            authoritative_transition_pathway,
            transition_context,
            system_context,
            assumptions,
            uncertainties,
            evidence_references,
            provenance,
            user_id,
            pathway_id,
            evaluation_run_id,
        )

        # These functions perform sibling risk analyses over the same
        # authoritative candidate context. Runtime scheduling is not part of
        # the architectural contract. Each output is validated independently
        # before its findings are admitted to the completed result.
        rule_outputs = (
            (
                "Candidate-reference risk findings",
                self.candidate_reference_risk_function(*arguments),
            ),
            (
                "System-interaction risk findings",
                self.system_interaction_risk_function(*arguments),
            ),
            (
                "Transition-delivery risk findings",
                self.transition_delivery_risk_function(*arguments),
            ),
            (
                "Timing and sequencing risk findings",
                self.timing_sequencing_risk_function(*arguments),
            ),
            (
                "Bottleneck and failure risk findings",
                self.bottleneck_failure_risk_function(*arguments),
            ),
            (
                "Fossil persistence and fallback risk findings",
                self.fossil_persistence_fallback_risk_function(*arguments),
            ),
            (
                "Dependency-propagation risk findings",
                self.dependency_propagation_risk_function(*arguments),
            ),
            (
                "Biosphere and climate risk findings",
                self.biosphere_climate_risk_function(*arguments),
            ),
            (
                "Charter and unresolved risk findings",
                self.charter_unresolved_risk_function(*arguments),
            ),
        )

        validated_outputs = tuple(
            _require_tuple_of(output, SystemRiskFinding, description)
            for description, output in rule_outputs
        )
        risk_findings = tuple(
            finding for findings in validated_outputs for finding in findings
        )

        result = NetOverallSystemRiskResult(
            candidate_transition_pathway=candidate_transition_pathway,
            authoritative_transition_pathway=authoritative_transition_pathway,
            risk_findings=risk_findings,
            evaluation_run_id=evaluation_run_id,
            user_id=user_id,
            pathway_id=pathway_id,
            evaluator_version=self.evaluator_version,
            rule_set_version=self.rule_set_version,
            assumptions=assumptions,
            uncertainties=uncertainties,
            evidence_references=evidence_references,
            provenance=provenance,
        )

        self._validate_result(
            result,
            candidate_transition_pathway,
            authoritative_transition_pathway,
            evaluation_run_id,
            user_id,
            pathway_id,
        )
        return result

    @staticmethod
    def _validate_inputs(
        candidate: TransitionPathway,
        authoritative: TransitionPathway,
        transition_context: OpaqueReference | None,
        system_context: OpaqueReference | None,
        assumptions: tuple[str, ...],
        uncertainties: tuple[str, ...],
        evidence_references: tuple[SourceReference, ...],
        provenance: tuple[SourceReference, ...],
        user_id: str,
        pathway_id: str,
        evaluation_run_id: str,
    ) -> None:
        if type(candidate) is not TransitionPathway:
            raise NetOverallSystemRiskEvaluationInvariantError(
                "Risk evaluation requires exactly candidate TransitionPathway"
            )
        if type(authoritative) is not TransitionPathway:
            raise NetOverallSystemRiskEvaluationInvariantError(
                "Risk evaluation requires exactly authoritative TransitionPathway"
            )
        if candidate is authoritative:
            raise NetOverallSystemRiskEvaluationInvariantError(
                "Candidate must be distinct from authoritative TransitionPathway"
            )
        if candidate.authoritative_transition_pathway is not authoritative:
            raise NetOverallSystemRiskEvaluationInvariantError(
                "Candidate must preserve the authoritative TransitionPathway"
            )
        if any(
            context is not None and not isinstance(context, OpaqueReference)
            for context in (transition_context, system_context)
        ):
            raise NetOverallSystemRiskEvaluationInvariantError(
                "Transition and system context must be OpaqueReference or None"
            )
        _require_tuple_of(assumptions, str, "Risk assumptions")
        _require_tuple_of(uncertainties, str, "Risk uncertainties")
        _require_tuple_of(
            evidence_references,
            SourceReference,
            "Risk evidence references",
        )
        _require_tuple_of(provenance, SourceReference, "Risk provenance")
        if not all(
            isinstance(value, str) for value in (evaluation_run_id, user_id, pathway_id)
        ):
            raise NetOverallSystemRiskEvaluationInvariantError(
                "Risk attribution values must be strings"
            )

        product_pathway = candidate.product_pathway
        contribution = candidate.net_overall_system_contribution
        scale_result = candidate.scale_diagnostic_result
        if type(product_pathway) is not ProductPathway:
            raise NetOverallSystemRiskEvaluationInvariantError(
                "Candidate must preserve exactly ProductPathway"
            )
        if type(contribution) is not NetOverallSystemContribution:
            raise NetOverallSystemRiskEvaluationInvariantError(
                "Candidate must preserve exactly NetOverallSystemContribution"
            )
        if type(scale_result) is not ScaleDiagnosticResult:
            raise NetOverallSystemRiskEvaluationInvariantError(
                "Candidate must preserve exactly ScaleDiagnosticResult"
            )
        if contribution.product_pathway is not product_pathway:
            raise NetOverallSystemRiskEvaluationInvariantError(
                "Contribution must preserve candidate ProductPathway"
            )
        if contribution.transition_pathway is not authoritative:
            raise NetOverallSystemRiskEvaluationInvariantError(
                "Contribution must preserve authoritative TransitionPathway"
            )
        if scale_result.product_pathway is not product_pathway:
            raise NetOverallSystemRiskEvaluationInvariantError(
                "Scale result must preserve candidate ProductPathway"
            )
        if scale_result.net_overall_system_contribution is not contribution:
            raise NetOverallSystemRiskEvaluationInvariantError(
                "Scale result must preserve candidate contribution"
            )
        if scale_result.transition_pathway is not authoritative:
            raise NetOverallSystemRiskEvaluationInvariantError(
                "Scale result must preserve authoritative TransitionPathway"
            )

        current_artifacts = (candidate, product_pathway, contribution, scale_result)
        if any(
            artifact.evaluation_run_id != evaluation_run_id
            for artifact in current_artifacts
        ):
            raise NetOverallSystemRiskEvaluationInvariantError(
                "Current risk inputs must share evaluation_run_id"
            )
        if any(artifact.user_id != user_id for artifact in current_artifacts):
            raise NetOverallSystemRiskEvaluationInvariantError(
                "Current risk inputs must share user_id"
            )
        if any(artifact.pathway_id != pathway_id for artifact in current_artifacts):
            raise NetOverallSystemRiskEvaluationInvariantError(
                "Current risk inputs must share pathway_id"
            )
        if candidate.identity_token is None:
            raise NetOverallSystemRiskEvaluationInvariantError(
                "Candidate must preserve current evaluation lineage"
            )
        token_id = candidate.identity_token.token_id
        if (
            product_pathway.identity_token.token_id != token_id
            or contribution.pathway_engine_result.identity_token.token_id != token_id
        ):
            raise NetOverallSystemRiskEvaluationInvariantError(
                "Current risk inputs must share evaluation lineage"
            )

        _require_tuple_of(
            candidate.affected_relationships,
            PathwayRelationship,
            "Candidate affected relationships",
        )
        _require_tuple_of(
            candidate.dependencies,
            OpaqueReference,
            "Candidate dependencies",
        )
        _require_tuple_of(candidate.conditions, str, "Candidate conditions")
        _require_tuple_of(
            candidate.unresolved_conditions,
            str,
            "Candidate unresolved conditions",
        )
        _require_tuple_of(
            candidate.evidence_references,
            SourceReference,
            "Candidate evidence references",
        )
        _require_tuple_of(
            candidate.provenance,
            SourceReference,
            "Candidate provenance",
        )
        _require_tuple_of(
            contribution.contribution_findings,
            ContributionFinding,
            "Contribution findings",
        )
        _require_tuple_of(scale_result.scale_findings, ScaleFinding, "Scale findings")

    @classmethod
    def _validate_result(
        cls,
        result: NetOverallSystemRiskResult,
        candidate: TransitionPathway,
        authoritative: TransitionPathway,
        evaluation_run_id: str,
        user_id: str,
        pathway_id: str,
    ) -> None:
        if result.candidate_transition_pathway is not candidate:
            raise NetOverallSystemRiskEvaluationInvariantError(
                "Risk result must preserve exact candidate TransitionPathway"
            )
        if result.authoritative_transition_pathway is not authoritative:
            raise NetOverallSystemRiskEvaluationInvariantError(
                "Risk result must preserve exact authoritative TransitionPathway"
            )
        if result.evaluation_run_id != evaluation_run_id:
            raise NetOverallSystemRiskEvaluationInvariantError(
                "Risk result must preserve evaluation_run_id"
            )
        if result.user_id != user_id:
            raise NetOverallSystemRiskEvaluationInvariantError(
                "Risk result must preserve user_id"
            )
        if result.pathway_id != pathway_id:
            raise NetOverallSystemRiskEvaluationInvariantError(
                "Risk result must preserve pathway_id"
            )
        if not isinstance(result.evaluator_version, str) or not isinstance(
            result.rule_set_version,
            str,
        ):
            raise NetOverallSystemRiskEvaluationInvariantError(
                "Risk evaluator and rule-set versions must be strings"
            )
        findings = _require_tuple_of(
            result.risk_findings,
            SystemRiskFinding,
            "System risk findings",
        )
        _require_tuple_of(result.assumptions, str, "Risk result assumptions")
        _require_tuple_of(result.uncertainties, str, "Risk result uncertainties")
        _require_tuple_of(
            result.evidence_references,
            SourceReference,
            "Risk result evidence references",
        )
        _require_tuple_of(
            result.provenance,
            SourceReference,
            "Risk result provenance",
        )
        for finding in findings:
            cls._validate_finding(finding, candidate)

    @staticmethod
    def _validate_finding(
        finding: SystemRiskFinding,
        candidate: TransitionPathway,
    ) -> None:
        if not isinstance(finding.finding_id, str) or not isinstance(
            finding.description,
            str,
        ):
            raise NetOverallSystemRiskEvaluationInvariantError(
                "Risk finding identity and description must be strings"
            )
        if any(
            value is not None and not isinstance(value, str)
            for value in (finding.risk_scope, finding.risk_type)
        ):
            raise NetOverallSystemRiskEvaluationInvariantError(
                "Risk finding scope and type must be strings or None"
            )
        text_collections = (
            finding.risk_states,
            finding.causes,
            finding.timeline_effects,
            finding.sequencing_effects,
            finding.bottlenecks,
            finding.pitfalls,
            finding.failure_modes,
            finding.fossil_fallback_risks,
            finding.fossil_persistence_risks,
            finding.infrastructure_constraints,
            finding.finance_constraints,
            finding.workforce_constraints,
            finding.adequacy_constraints,
            finding.delivery_constraints,
            finding.supply_chain_constraints,
            finding.other_transition_constraints,
            finding.charter_style_findings,
            finding.conditions,
            finding.unresolved_conditions,
        )
        if any(
            not isinstance(values, tuple)
            or not all(isinstance(value, str) for value in values)
            for values in text_collections
        ):
            raise NetOverallSystemRiskEvaluationInvariantError(
                "Risk finding text collections must be tuples of strings"
            )
        _require_tuple_of(
            finding.transition_function_references,
            OpaqueReference,
            "Risk transition function references",
        )
        _require_tuple_of(
            finding.transition_relationships,
            PathwayRelationship,
            "Risk transition relationships",
        )
        _require_tuple_of(
            finding.propagation_relationships,
            PathwayRelationship,
            "Risk propagation relationships",
        )

        contribution = candidate.net_overall_system_contribution
        scale_result = candidate.scale_diagnostic_result
        assert contribution is not None
        assert scale_result is not None
        contribution_findings = _require_tuple_of(
            finding.supporting_contribution_findings,
            ContributionFinding,
            "Risk supporting contribution findings",
        )
        if any(
            not _contains_reference(
                contribution.contribution_findings,
                contribution_finding,
            )
            for contribution_finding in contribution_findings
        ):
            raise NetOverallSystemRiskEvaluationInvariantError(
                "Risk contribution support must come from candidate contribution"
            )
        scale_findings = _require_tuple_of(
            finding.supporting_scale_findings,
            ScaleFinding,
            "Risk supporting scale findings",
        )
        if any(
            not _contains_reference(scale_result.scale_findings, scale_finding)
            for scale_finding in scale_findings
        ):
            raise NetOverallSystemRiskEvaluationInvariantError(
                "Risk scale support must come from candidate scale result"
            )
        _require_tuple_of(
            finding.supporting_system_references,
            OpaqueReference,
            "Risk supporting system references",
        )
        _require_tuple_of(
            finding.evidence_references,
            SourceReference,
            "Risk finding evidence references",
        )
        _require_tuple_of(
            finding.provenance,
            SourceReference,
            "Risk finding provenance",
        )
