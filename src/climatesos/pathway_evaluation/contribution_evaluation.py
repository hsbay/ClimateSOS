"""Validated boundary for caller-supplied system-contribution evaluation."""

from collections.abc import Callable
from dataclasses import dataclass
from typing import TypeVar

from .enums import CharterCheckStatus
from .models import (
    ComparisonFinding,
    ContributionFinding,
    DocumentationFinding,
    FabricEvaluatorResult,
    IntegratedCharterResult,
    NetOverallSystemContribution,
    OpaqueReference,
    PathwayEngineResult,
    PathwayObject,
    QueueEvaluatorResult,
    SourceReference,
)

ContributionEvaluationFunction = Callable[
    [PathwayEngineResult, IntegratedCharterResult],
    object,
]

T = TypeVar("T")

_INTEGRATED_CHARTER_INTEGRITY_FAILURES = frozenset(
    {
        CharterCheckStatus.ERROR,
        CharterCheckStatus.MISSING,
        CharterCheckStatus.NULL,
        CharterCheckStatus.NOACK,
    }
)


class ContributionEvaluationInvariantError(ValueError):
    """Raised when contribution inputs or output are structurally incoherent."""


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
        raise ContributionEvaluationInvariantError(
            f"{description} must be a tuple of {expected_type.__name__} objects"
        )
    return value


@dataclass(frozen=True, slots=True)
class ValidatedNetOverallSystemContributionEvaluator:
    """Validate progression and caller-supplied contribution results."""

    contribution_function: ContributionEvaluationFunction

    def evaluate(
        self,
        pathway_engine_result: PathwayEngineResult,
        integrated_charter_result: IntegratedCharterResult,
    ) -> NetOverallSystemContribution:
        """Invoke contribution evaluation without supplying substantive rules."""

        self._validate_inputs(pathway_engine_result, integrated_charter_result)
        raw_result = self.contribution_function(
            pathway_engine_result,
            integrated_charter_result,
        )
        if not isinstance(raw_result, NetOverallSystemContribution):
            raise ContributionEvaluationInvariantError(
                "Contribution evaluation must return NetOverallSystemContribution"
            )
        self._validate_result(
            raw_result,
            pathway_engine_result,
            integrated_charter_result,
        )
        return raw_result

    @staticmethod
    def _validate_inputs(
        pathway_engine_result: PathwayEngineResult,
        integrated_charter_result: IntegratedCharterResult,
    ) -> None:
        if type(pathway_engine_result) is not PathwayEngineResult:
            raise ContributionEvaluationInvariantError(
                "Contribution evaluation requires exactly PathwayEngineResult"
            )
        if type(integrated_charter_result) is not IntegratedCharterResult:
            raise ContributionEvaluationInvariantError(
                "Contribution evaluation requires exactly IntegratedCharterResult"
            )
        if (
            integrated_charter_result.status == "ERROR"
            or integrated_charter_result.execution_error is not None
            or any(
                check.status in _INTEGRATED_CHARTER_INTEGRITY_FAILURES
                for check in integrated_charter_result.check_results
            )
        ):
            raise ContributionEvaluationInvariantError(
                "Contribution evaluation requires an IntegratedCharterResult "
                "without execution-integrity failure"
            )
        if (
            integrated_charter_result.pathway_engine_result
            is not pathway_engine_result
        ):
            raise ContributionEvaluationInvariantError(
                "IntegratedCharterResult must preserve PathwayEngineResult"
            )
        if (
            integrated_charter_result.initial_charter_result
            is not pathway_engine_result.initial_charter_result
        ):
            raise ContributionEvaluationInvariantError(
                "Integrated and engine results must preserve the same "
                "InitialCharterResult"
            )

        pathway = pathway_engine_result.product_pathway
        token_id = pathway.identity_token.token_id
        if (
            pathway_engine_result.identity_token.token_id != token_id
            or integrated_charter_result.identity_token.token_id != token_id
        ):
            raise ContributionEvaluationInvariantError(
                "Contribution inputs must share the ProductPathway IdentityToken"
            )
        if (
            pathway_engine_result.evaluation_run_id != pathway.evaluation_run_id
            or integrated_charter_result.evaluation_run_id
            != pathway.evaluation_run_id
        ):
            raise ContributionEvaluationInvariantError(
                "Contribution inputs must share the ProductPathway EvaluationRun"
            )
        if (
            pathway_engine_result.user_id != pathway.user_id
            or pathway_engine_result.pathway_id != pathway.pathway_id
        ):
            raise ContributionEvaluationInvariantError(
                "PathwayEngineResult attribution must match ProductPathway"
            )

    @classmethod
    def _validate_result(
        cls,
        result: NetOverallSystemContribution,
        pathway_engine_result: PathwayEngineResult,
        integrated_charter_result: IntegratedCharterResult,
    ) -> None:
        if result.pathway_engine_result is not pathway_engine_result:
            raise ContributionEvaluationInvariantError(
                "Contribution result must preserve PathwayEngineResult"
            )
        if result.integrated_charter_result is not integrated_charter_result:
            raise ContributionEvaluationInvariantError(
                "Contribution result must preserve IntegratedCharterResult"
            )
        if result.product_pathway is not pathway_engine_result.product_pathway:
            raise ContributionEvaluationInvariantError(
                "Contribution result must preserve ProductPathway"
            )
        if result.transition_pathway is not pathway_engine_result.transition_pathway:
            raise ContributionEvaluationInvariantError(
                "Contribution result must preserve authoritative TransitionPathway"
            )
        if result.evaluation_run_id != pathway_engine_result.evaluation_run_id:
            raise ContributionEvaluationInvariantError(
                "Contribution result must preserve evaluation_run_id"
            )
        if result.user_id != pathway_engine_result.user_id:
            raise ContributionEvaluationInvariantError(
                "Contribution result must preserve user_id"
            )
        if result.pathway_id != pathway_engine_result.pathway_id:
            raise ContributionEvaluationInvariantError(
                "Contribution result must preserve pathway_id"
            )
        if not isinstance(result.evaluator_version, str) or not isinstance(
            result.rule_set_version,
            str,
        ):
            raise ContributionEvaluationInvariantError(
                "Evaluator and rule-set versions must be strings"
            )

        findings = _require_tuple_of(
            result.contribution_findings,
            ContributionFinding,
            "Contribution findings",
        )
        _require_tuple_of(result.assumptions, str, "Contribution assumptions")
        _require_tuple_of(result.uncertainties, str, "Contribution uncertainties")
        _require_tuple_of(
            result.evidence_references,
            SourceReference,
            "Contribution evidence references",
        )
        _require_tuple_of(
            result.provenance,
            SourceReference,
            "Contribution provenance",
        )
        for finding in findings:
            cls._validate_finding(finding, pathway_engine_result)

    @staticmethod
    def _validate_finding(
        finding: ContributionFinding,
        pathway_engine_result: PathwayEngineResult,
    ) -> None:
        if not isinstance(finding.finding_id, str) or not isinstance(
            finding.effect_description,
            str,
        ):
            raise ContributionEvaluationInvariantError(
                "Contribution finding identity and effect must be strings"
            )
        optional_strings = (
            finding.contribution_scope,
            finding.contribution_type,
            finding.contribution_mechanism,
        )
        if any(
            value is not None and not isinstance(value, str)
            for value in optional_strings
        ):
            raise ContributionEvaluationInvariantError(
                "Contribution scope, type, and mechanism must be strings or None"
            )
        string_collections = (
            finding.contribution_statuses,
            finding.net_zero_transition_effects,
            finding.system_effects,
            finding.timing_effects,
            finding.dependencies,
            finding.conditions,
        )
        if any(
            not isinstance(values, tuple)
            or not all(isinstance(value, str) for value in values)
            for values in string_collections
        ):
            raise ContributionEvaluationInvariantError(
                "Contribution finding text collections must be tuples of strings"
            )

        pathway_outputs = _require_tuple_of(
            finding.pathway_output_references,
            PathwayObject,
            "Pathway output references",
        )
        if any(
            not _contains_reference(
                pathway_engine_result.product_pathway.objects,
                output,
            )
            for output in pathway_outputs
        ):
            raise ContributionEvaluationInvariantError(
                "Pathway output references must preserve ProductPathway objects"
            )

        comparison_findings = _require_tuple_of(
            finding.supporting_comparison_findings,
            ComparisonFinding,
            "Supporting comparison findings",
        )
        available_comparisons = (
            pathway_engine_result.direct_comparison_findings
            + pathway_engine_result.substitution_combination_findings
            + pathway_engine_result.downstream_propagation_findings
        )
        if any(
            not _contains_reference(available_comparisons, comparison)
            for comparison in comparison_findings
        ):
            raise ContributionEvaluationInvariantError(
                "Supporting comparison findings must come from PathwayEngineResult"
            )

        queue_results = _require_tuple_of(
            finding.supporting_queue_results,
            QueueEvaluatorResult,
            "Supporting queue results",
        )
        if any(
            not _contains_reference(pathway_engine_result.queue_results, queue_result)
            for queue_result in queue_results
        ):
            raise ContributionEvaluationInvariantError(
                "Supporting queue results must come from PathwayEngineResult"
            )

        fabric_results = _require_tuple_of(
            finding.supporting_fabric_results,
            FabricEvaluatorResult,
            "Supporting fabric results",
        )
        if any(
            not _contains_reference(pathway_engine_result.fabric_results, fabric_result)
            for fabric_result in fabric_results
        ):
            raise ContributionEvaluationInvariantError(
                "Supporting fabric results must come from PathwayEngineResult"
            )

        documentation_findings = _require_tuple_of(
            finding.supporting_documentation_findings,
            DocumentationFinding,
            "Supporting documentation findings",
        )
        if any(
            not _contains_reference(
                pathway_engine_result.documentation_findings,
                documentation,
            )
            for documentation in documentation_findings
        ):
            raise ContributionEvaluationInvariantError(
                "Supporting documentation findings must come from "
                "PathwayEngineResult"
            )

        _require_tuple_of(
            finding.transition_function_references,
            OpaqueReference,
            "Transition function references",
        )
        _require_tuple_of(
            finding.supporting_system_references,
            OpaqueReference,
            "Supporting system references",
        )
        _require_tuple_of(
            finding.evidence_references,
            SourceReference,
            "Contribution finding evidence references",
        )
        _require_tuple_of(
            finding.provenance,
            SourceReference,
            "Contribution finding provenance",
        )
