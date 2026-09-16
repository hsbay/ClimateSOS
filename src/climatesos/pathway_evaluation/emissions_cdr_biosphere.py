"""Composable source-emissions, carbon-removal, and biosphere rules."""

from collections.abc import Callable
from dataclasses import dataclass

from .models import ContributionFinding, IntegratedCharterResult, PathwayEngineResult

SourceEmissionsRuleFunction = Callable[
    [PathwayEngineResult, IntegratedCharterResult],
    tuple[ContributionFinding, ...],
]
CarbonRemovalRuleFunction = Callable[
    [PathwayEngineResult, IntegratedCharterResult],
    tuple[ContributionFinding, ...],
]
BiosphereContributionRuleFunction = Callable[
    [PathwayEngineResult, IntegratedCharterResult],
    tuple[ContributionFinding, ...],
]


class EmissionsCdrBiosphereEvaluationInvariantError(ValueError):
    """Raised when a required emissions, removal, or biosphere rule is malformed."""


def _validate_rule_findings(
    value: object,
    rule_description: str,
) -> tuple[ContributionFinding, ...]:
    if not isinstance(value, tuple) or not all(
        isinstance(finding, ContributionFinding) for finding in value
    ):
        raise EmissionsCdrBiosphereEvaluationInvariantError(
            f"{rule_description} must return a tuple of ContributionFinding objects"
        )
    return value


@dataclass(frozen=True, slots=True)
class EmissionsCdrBiosphereFindingFunction:
    """Compose explicit emissions, removal, and biosphere findings only."""

    source_emissions_rule: SourceEmissionsRuleFunction
    carbon_removal_rule: CarbonRemovalRuleFunction
    biosphere_contribution_rule: BiosphereContributionRuleFunction

    def __call__(
        self,
        pathway_engine_result: PathwayEngineResult,
        integrated_charter_result: IntegratedCharterResult,
    ) -> tuple[ContributionFinding, ...]:
        """Run each semantic rule once and preserve its findings in rule order."""

        source_emissions_findings = _validate_rule_findings(
            self.source_emissions_rule(
                pathway_engine_result,
                integrated_charter_result,
            ),
            "Source-emissions rule",
        )
        carbon_removal_findings = _validate_rule_findings(
            self.carbon_removal_rule(
                pathway_engine_result,
                integrated_charter_result,
            ),
            "Carbon-removal rule",
        )
        biosphere_findings = _validate_rule_findings(
            self.biosphere_contribution_rule(
                pathway_engine_result,
                integrated_charter_result,
            ),
            "Biosphere-contribution rule",
        )
        return source_emissions_findings + carbon_removal_findings + biosphere_findings
