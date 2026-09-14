"""Deterministic composition of caller-supplied system-risk findings."""

from collections.abc import Callable
from dataclasses import dataclass

from .models import (
    NetOverallSystemRiskResult,
    OpaqueReference,
    SourceReference,
    SystemRiskFinding,
    TransitionPathway,
)

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


@dataclass(frozen=True, slots=True)
class CompleteNetOverallSystemRiskFunction:
    """Compose every Section 14 risk domain into one completed result."""

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

    def __call__(
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
        """Execute each rule once and preserve findings in domain order."""

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
        risk_findings = (
            self.candidate_reference_risk_function(*arguments)
            + self.system_interaction_risk_function(*arguments)
            + self.transition_delivery_risk_function(*arguments)
            + self.timing_sequencing_risk_function(*arguments)
            + self.bottleneck_failure_risk_function(*arguments)
            + self.fossil_persistence_fallback_risk_function(*arguments)
            + self.dependency_propagation_risk_function(*arguments)
            + self.biosphere_climate_risk_function(*arguments)
            + self.charter_unresolved_risk_function(*arguments)
        )
        return NetOverallSystemRiskResult(
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
