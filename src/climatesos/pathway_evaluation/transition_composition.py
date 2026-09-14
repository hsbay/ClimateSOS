"""Deterministic composition of caller-supplied candidate transition content."""

from collections.abc import Callable
from dataclasses import dataclass
from typing import TypeVar

from .models import (
    IdentityToken,
    NetOverallSystemContribution,
    OpaqueReference,
    PathwayRelationship,
    ProductPathway,
    ScaleDiagnosticResult,
    SourceReference,
    TransitionPathway,
)

T = TypeVar("T")

CandidateTransitionRuleFunction = Callable[
    [
        ProductPathway,
        NetOverallSystemContribution,
        ScaleDiagnosticResult,
        TransitionPathway,
        OpaqueReference | None,
        OpaqueReference | None,
        tuple[str, ...],
        tuple[OpaqueReference, ...],
        tuple[str, ...],
        tuple[str, ...],
        tuple[SourceReference, ...],
        tuple[SourceReference, ...],
        IdentityToken,
        str,
        str,
        str,
    ],
    tuple[T, ...],
]


@dataclass(frozen=True, slots=True)
class CompleteTransitionPathwayCompilationFunction:
    """Compose Section 13 rule outputs into one non-authoritative candidate."""

    incorporated_transition_function: CandidateTransitionRuleFunction[
        OpaqueReference
    ]
    affected_relationship_function: CandidateTransitionRuleFunction[
        PathwayRelationship
    ]
    dependency_function: CandidateTransitionRuleFunction[OpaqueReference]
    condition_function: CandidateTransitionRuleFunction[str]
    timing_condition_function: CandidateTransitionRuleFunction[str]
    sequencing_condition_function: CandidateTransitionRuleFunction[str]
    contribution_condition_function: CandidateTransitionRuleFunction[str]
    scale_condition_function: CandidateTransitionRuleFunction[str]
    unchanged_transition_function: CandidateTransitionRuleFunction[OpaqueReference]
    unresolved_condition_function: CandidateTransitionRuleFunction[str]
    reference_id: str
    compiler_version: str
    model_version: str
    rule_set_version: str

    def __call__(
        self,
        product_pathway: ProductPathway,
        net_overall_system_contribution: NetOverallSystemContribution,
        scale_diagnostic_result: ScaleDiagnosticResult,
        authoritative_transition_pathway: TransitionPathway,
        transition_context: OpaqueReference | None,
        system_context: OpaqueReference | None,
        conditions: tuple[str, ...],
        dependencies: tuple[OpaqueReference, ...],
        assumptions: tuple[str, ...],
        uncertainties: tuple[str, ...],
        evidence_references: tuple[SourceReference, ...],
        provenance: tuple[SourceReference, ...],
        identity_token: IdentityToken,
        evaluation_run_id: str,
        user_id: str,
        pathway_id: str,
    ) -> TransitionPathway:
        """Execute each rule once and preserve caller-supplied ordering."""

        arguments = (
            product_pathway,
            net_overall_system_contribution,
            scale_diagnostic_result,
            authoritative_transition_pathway,
            transition_context,
            system_context,
            conditions,
            dependencies,
            assumptions,
            uncertainties,
            evidence_references,
            provenance,
            identity_token,
            evaluation_run_id,
            user_id,
            pathway_id,
        )
        incorporated_transition_references = self.incorporated_transition_function(
            *arguments
        )
        affected_relationships = self.affected_relationship_function(*arguments)
        compiled_dependencies = self.dependency_function(*arguments)
        compiled_conditions = self.condition_function(*arguments)
        timing_conditions = self.timing_condition_function(*arguments)
        sequencing_conditions = self.sequencing_condition_function(*arguments)
        contribution_conditions = self.contribution_condition_function(*arguments)
        scale_conditions = self.scale_condition_function(*arguments)
        unchanged_transition_references = self.unchanged_transition_function(
            *arguments
        )
        unresolved_conditions = self.unresolved_condition_function(*arguments)

        return TransitionPathway(
            reference_id=self.reference_id,
            provenance=provenance,
            identity_token=identity_token,
            evaluation_run_id=evaluation_run_id,
            user_id=user_id,
            pathway_id=pathway_id,
            authoritative_transition_pathway=authoritative_transition_pathway,
            product_pathway=product_pathway,
            net_overall_system_contribution=net_overall_system_contribution,
            scale_diagnostic_result=scale_diagnostic_result,
            incorporated_transition_references=incorporated_transition_references,
            affected_relationships=affected_relationships,
            dependencies=dependencies + compiled_dependencies,
            conditions=conditions + compiled_conditions,
            timing_conditions=timing_conditions,
            sequencing_conditions=sequencing_conditions,
            contribution_conditions=contribution_conditions,
            scale_conditions=scale_conditions,
            unchanged_transition_references=unchanged_transition_references,
            unresolved_conditions=unresolved_conditions,
            assumptions=assumptions,
            uncertainties=uncertainties,
            evidence_references=evidence_references,
            compiler_version=self.compiler_version,
            model_version=self.model_version,
            rule_set_version=self.rule_set_version,
        )
