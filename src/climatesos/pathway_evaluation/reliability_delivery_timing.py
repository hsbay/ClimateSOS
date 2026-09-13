"""Composable reliability, deliverability, and transition-timing rule boundary."""

from collections.abc import Callable
from dataclasses import dataclass

from .models import ContributionFinding, IntegratedCharterResult, PathwayEngineResult

ReliabilityAdequacyRuleFunction = Callable[
    [PathwayEngineResult, IntegratedCharterResult],
    tuple[ContributionFinding, ...],
]
DeliverabilitySynchronizationRuleFunction = Callable[
    [PathwayEngineResult, IntegratedCharterResult],
    tuple[ContributionFinding, ...],
]
TransitionTimingRuleFunction = Callable[
    [PathwayEngineResult, IntegratedCharterResult],
    tuple[ContributionFinding, ...],
]


class ReliabilityDeliveryTimingEvaluationInvariantError(ValueError):
    """Raised when a required reliability, delivery, or timing rule is malformed."""


def _validate_rule_findings(
    value: object,
    rule_description: str,
) -> tuple[ContributionFinding, ...]:
    if not isinstance(value, tuple) or not all(
        isinstance(finding, ContributionFinding) for finding in value
    ):
        raise ReliabilityDeliveryTimingEvaluationInvariantError(
            f"{rule_description} must return a tuple of ContributionFinding objects"
        )
    return value


@dataclass(frozen=True, slots=True)
class ReliabilityDeliveryTimingFindingFunction:
    """Compose explicit reliability, delivery, and timing findings only."""

    reliability_adequacy_rule: ReliabilityAdequacyRuleFunction
    deliverability_synchronization_rule: DeliverabilitySynchronizationRuleFunction
    transition_timing_rule: TransitionTimingRuleFunction

    def __call__(
        self,
        pathway_engine_result: PathwayEngineResult,
        integrated_charter_result: IntegratedCharterResult,
    ) -> tuple[ContributionFinding, ...]:
        """Run each semantic rule once and preserve its findings in rule order."""

        reliability_findings = _validate_rule_findings(
            self.reliability_adequacy_rule(
                pathway_engine_result,
                integrated_charter_result,
            ),
            "Reliability and adequacy rule",
        )
        deliverability_findings = _validate_rule_findings(
            self.deliverability_synchronization_rule(
                pathway_engine_result,
                integrated_charter_result,
            ),
            "Deliverability and synchronization rule",
        )
        timing_findings = _validate_rule_findings(
            self.transition_timing_rule(
                pathway_engine_result,
                integrated_charter_result,
            ),
            "Transition timing rule",
        )
        return reliability_findings + deliverability_findings + timing_findings
