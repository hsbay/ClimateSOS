"""Complete deterministic composition of contribution-domain findings."""

from dataclasses import dataclass

from .emissions_cdr_biosphere import EmissionsCdrBiosphereFindingFunction
from .enabling_demand_burden import EnablingDemandBurdenFindingFunction
from .fossil_displacement import FossilDisplacementContributionFunction
from .models import (
    IntegratedCharterResult,
    NetOverallSystemContribution,
    PathwayEngineResult,
    SourceReference,
)
from .reliability_delivery_timing import ReliabilityDeliveryTimingFindingFunction


@dataclass(frozen=True, slots=True)
class CompleteNetOverallSystemContributionFunction:
    """Compose every implemented contribution domain into one final result."""

    fossil_contribution_function: FossilDisplacementContributionFunction
    reliability_delivery_timing_function: ReliabilityDeliveryTimingFindingFunction
    enabling_demand_burden_function: EnablingDemandBurdenFindingFunction
    emissions_cdr_biosphere_function: EmissionsCdrBiosphereFindingFunction
    evaluator_version: str
    rule_set_version: str
    assumptions: tuple[str, ...] = ()
    uncertainties: tuple[str, ...] = ()
    evidence_references: tuple[SourceReference, ...] = ()
    provenance: tuple[SourceReference, ...] = ()

    def __call__(
        self,
        pathway_engine_result: PathwayEngineResult,
        integrated_charter_result: IntegratedCharterResult,
    ) -> NetOverallSystemContribution:
        """Execute each domain once and preserve findings in domain order."""

        fossil_result = self.fossil_contribution_function(
            pathway_engine_result,
            integrated_charter_result,
        )
        reliability_findings = self.reliability_delivery_timing_function(
            pathway_engine_result,
            integrated_charter_result,
        )
        enabling_findings = self.enabling_demand_burden_function(
            pathway_engine_result,
            integrated_charter_result,
        )
        emissions_findings = self.emissions_cdr_biosphere_function(
            pathway_engine_result,
            integrated_charter_result,
        )
        return NetOverallSystemContribution(
            product_pathway=pathway_engine_result.product_pathway,
            pathway_engine_result=pathway_engine_result,
            integrated_charter_result=integrated_charter_result,
            transition_pathway=pathway_engine_result.transition_pathway,
            contribution_findings=(
                fossil_result.contribution_findings
                + reliability_findings
                + enabling_findings
                + emissions_findings
            ),
            evaluation_run_id=pathway_engine_result.evaluation_run_id,
            user_id=pathway_engine_result.user_id,
            pathway_id=pathway_engine_result.pathway_id,
            evaluator_version=self.evaluator_version,
            rule_set_version=self.rule_set_version,
            assumptions=self.assumptions,
            uncertainties=self.uncertainties,
            evidence_references=self.evidence_references,
            provenance=self.provenance,
        )
