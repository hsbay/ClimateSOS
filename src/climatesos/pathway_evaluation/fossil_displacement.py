"""Composable fossil-displacement and persistence-closure rule boundary."""

from collections.abc import Callable
from dataclasses import dataclass

from .models import (
    ContributionFinding,
    IntegratedCharterResult,
    NetOverallSystemContribution,
    PathwayEngineResult,
    SourceReference,
)

FossilDisplacementRuleFunction = Callable[
    [PathwayEngineResult, IntegratedCharterResult],
    tuple[ContributionFinding, ...],
]
FossilFunctionClosureRuleFunction = Callable[
    [PathwayEngineResult, IntegratedCharterResult],
    tuple[ContributionFinding, ...],
]
FossilPersistenceClosureRuleFunction = Callable[
    [PathwayEngineResult, IntegratedCharterResult],
    tuple[ContributionFinding, ...],
]


class FossilDisplacementEvaluationInvariantError(ValueError):
    """Raised when a required fossil-displacement rule returns malformed data."""


def _validate_rule_findings(
    value: object,
    rule_description: str,
) -> tuple[ContributionFinding, ...]:
    if not isinstance(value, tuple) or not all(
        isinstance(finding, ContributionFinding) for finding in value
    ):
        raise FossilDisplacementEvaluationInvariantError(
            f"{rule_description} must return a tuple of ContributionFinding objects"
        )
    return value


@dataclass(frozen=True, slots=True)
class FossilDisplacementContributionFunction:
    """Compose explicit fossil-displacement rule findings without inference."""

    displacement_rule: FossilDisplacementRuleFunction
    function_closure_rule: FossilFunctionClosureRuleFunction
    persistence_closure_rule: FossilPersistenceClosureRuleFunction
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
        """Run each semantic rule once and preserve its findings in rule order."""

        displacement_findings = _validate_rule_findings(
            self.displacement_rule(
                pathway_engine_result,
                integrated_charter_result,
            ),
            "Fossil displacement rule",
        )
        function_closure_findings = _validate_rule_findings(
            self.function_closure_rule(
                pathway_engine_result,
                integrated_charter_result,
            ),
            "Fossil function-closure rule",
        )
        persistence_closure_findings = _validate_rule_findings(
            self.persistence_closure_rule(
                pathway_engine_result,
                integrated_charter_result,
            ),
            "Fossil persistence-closure rule",
        )
        return NetOverallSystemContribution(
            product_pathway=pathway_engine_result.product_pathway,
            pathway_engine_result=pathway_engine_result,
            integrated_charter_result=integrated_charter_result,
            transition_pathway=pathway_engine_result.transition_pathway,
            contribution_findings=(
                displacement_findings
                + function_closure_findings
                + persistence_closure_findings
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
