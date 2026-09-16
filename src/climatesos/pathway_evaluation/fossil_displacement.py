"""Composable fossil-displacement and persistence-closure rule boundary."""

from collections.abc import Callable
from dataclasses import dataclass

from .models import (
    ContributionFinding,
    IntegratedCharterResult,
    PathwayEngineResult,
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

    def __call__(
        self,
        pathway_engine_result: PathwayEngineResult,
        integrated_charter_result: IntegratedCharterResult,
    ) -> tuple[ContributionFinding, ...]:
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
        return (
            displacement_findings
            + function_closure_findings
            + persistence_closure_findings
        )
