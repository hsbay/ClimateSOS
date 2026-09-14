"""Deterministic composition of caller-supplied Scale Diagnostic findings."""

from collections.abc import Callable
from dataclasses import dataclass

from .models import (
    NetOverallSystemContribution,
    OpaqueReference,
    ProductPathway,
    ScaleDiagnosticResult,
    ScaleFinding,
    SourceReference,
    TransitionPathway,
)

ScaleDiagnosticFindingFunction = Callable[
    [
        NetOverallSystemContribution,
        ProductPathway,
        TransitionPathway,
        OpaqueReference | None,
        tuple[str, ...],
        tuple[str, ...],
        tuple[SourceReference, ...],
        tuple[SourceReference, ...],
        str,
        str,
        str,
    ],
    tuple[ScaleFinding, ...],
]


@dataclass(frozen=True, slots=True)
class CompleteScaleDiagnosticFunction:
    """Compose every Section 12 semantic surface into one scale result."""

    material_scale_function: ScaleDiagnosticFindingFunction
    scale_dimensions_function: ScaleDiagnosticFindingFunction
    scale_progression_function: ScaleDiagnosticFindingFunction
    timing_sequencing_function: ScaleDiagnosticFindingFunction
    constraint_bottleneck_function: ScaleDiagnosticFindingFunction
    response_condition_function: ScaleDiagnosticFindingFunction
    scale_dependent_effect_function: ScaleDiagnosticFindingFunction
    limited_local_function: ScaleDiagnosticFindingFunction
    stale_success_function: ScaleDiagnosticFindingFunction
    unresolved_scale_function: ScaleDiagnosticFindingFunction
    evaluator_version: str
    rule_set_version: str

    def __call__(
        self,
        net_overall_system_contribution: NetOverallSystemContribution,
        product_pathway: ProductPathway,
        transition_pathway: TransitionPathway,
        system_context: OpaqueReference | None,
        assumptions: tuple[str, ...],
        uncertainties: tuple[str, ...],
        evidence_references: tuple[SourceReference, ...],
        provenance: tuple[SourceReference, ...],
        user_id: str,
        pathway_id: str,
        evaluation_run_id: str,
    ) -> ScaleDiagnosticResult:
        """Execute each rule once and preserve its findings in domain order."""

        arguments = (
            net_overall_system_contribution,
            product_pathway,
            transition_pathway,
            system_context,
            assumptions,
            uncertainties,
            evidence_references,
            provenance,
            user_id,
            pathway_id,
            evaluation_run_id,
        )
        scale_findings = (
            self.material_scale_function(*arguments)
            + self.scale_dimensions_function(*arguments)
            + self.scale_progression_function(*arguments)
            + self.timing_sequencing_function(*arguments)
            + self.constraint_bottleneck_function(*arguments)
            + self.response_condition_function(*arguments)
            + self.scale_dependent_effect_function(*arguments)
            + self.limited_local_function(*arguments)
            + self.stale_success_function(*arguments)
            + self.unresolved_scale_function(*arguments)
        )
        return ScaleDiagnosticResult(
            product_pathway=product_pathway,
            net_overall_system_contribution=net_overall_system_contribution,
            transition_pathway=transition_pathway,
            scale_findings=scale_findings,
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
