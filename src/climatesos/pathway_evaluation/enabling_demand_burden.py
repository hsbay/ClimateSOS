"""Composable enabling, dependency, demand, and transition-burden rules."""

from collections.abc import Callable
from dataclasses import dataclass

from .models import ContributionFinding, IntegratedCharterResult, PathwayEngineResult

TransitionEnablingCapacityRuleFunction = Callable[
    [PathwayEngineResult, IntegratedCharterResult],
    tuple[ContributionFinding, ...],
]
DependencyBottleneckRuleFunction = Callable[
    [PathwayEngineResult, IntegratedCharterResult],
    tuple[ContributionFinding, ...],
]
TransitionDemandEffectRuleFunction = Callable[
    [PathwayEngineResult, IntegratedCharterResult],
    tuple[ContributionFinding, ...],
]
TransitionBurdenRuleFunction = Callable[
    [PathwayEngineResult, IntegratedCharterResult],
    tuple[ContributionFinding, ...],
]


class EnablingDemandBurdenEvaluationInvariantError(ValueError):
    """Raised when a required enabling, demand, or burden rule is malformed."""


def _validate_rule_findings(
    value: object,
    rule_description: str,
) -> tuple[ContributionFinding, ...]:
    if not isinstance(value, tuple) or not all(
        isinstance(finding, ContributionFinding) for finding in value
    ):
        raise EnablingDemandBurdenEvaluationInvariantError(
            f"{rule_description} must return a tuple of ContributionFinding objects"
        )
    return value


@dataclass(frozen=True, slots=True)
class EnablingDemandBurdenFindingFunction:
    """Compose explicit enabling, dependency, demand, and burden findings only."""

    enabling_capacity_rule: TransitionEnablingCapacityRuleFunction
    dependency_bottleneck_rule: DependencyBottleneckRuleFunction
    demand_effect_rule: TransitionDemandEffectRuleFunction
    transition_burden_rule: TransitionBurdenRuleFunction

    def __call__(
        self,
        pathway_engine_result: PathwayEngineResult,
        integrated_charter_result: IntegratedCharterResult,
    ) -> tuple[ContributionFinding, ...]:
        """Run each semantic rule once and preserve its findings in rule order."""

        enabling_findings = _validate_rule_findings(
            self.enabling_capacity_rule(
                pathway_engine_result,
                integrated_charter_result,
            ),
            "Transition-enabling capacity rule",
        )
        dependency_findings = _validate_rule_findings(
            self.dependency_bottleneck_rule(
                pathway_engine_result,
                integrated_charter_result,
            ),
            "Dependency and bottleneck rule",
        )
        demand_findings = _validate_rule_findings(
            self.demand_effect_rule(
                pathway_engine_result,
                integrated_charter_result,
            ),
            "Transition demand-effect rule",
        )
        burden_findings = _validate_rule_findings(
            self.transition_burden_rule(
                pathway_engine_result,
                integrated_charter_result,
            ),
            "Transition-burden rule",
        )
        return (
            enabling_findings
            + dependency_findings
            + demand_findings
            + burden_findings
        )
