"""Validated boundary for caller-supplied scale-diagnostic evaluation."""

from collections.abc import Callable
from dataclasses import dataclass
from typing import TypeVar

from .models import (
    ComparisonFinding,
    ContributionFinding,
    DocumentationFinding,
    FabricEvaluatorResult,
    NetOverallSystemContribution,
    OpaqueReference,
    PathwayObject,
    ProductPathway,
    QueueEvaluatorResult,
    ScaleDiagnosticResult,
    ScaleFinding,
    SourceReference,
    TransitionPathway,
)

ScaleDiagnosticEvaluationFunction = Callable[
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
    object,
]

T = TypeVar("T")


class ScaleDiagnosticEvaluationInvariantError(ValueError):
    """Raised when scale-diagnostic inputs or output are structurally incoherent."""


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
        raise ScaleDiagnosticEvaluationInvariantError(
            f"{description} must be a tuple of {expected_type.__name__} objects"
        )
    return value


@dataclass(frozen=True, slots=True)
class ValidatedScaleDiagnosticEvaluator:
    """Validate inputs and caller-supplied scale-diagnostic results."""

    scale_diagnostic_function: ScaleDiagnosticEvaluationFunction

    def evaluate(
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
        """Invoke scale diagnosis without supplying substantive scale rules."""

        self._validate_inputs(
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
        raw_result = self.scale_diagnostic_function(
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
        if not isinstance(raw_result, ScaleDiagnosticResult):
            raise ScaleDiagnosticEvaluationInvariantError(
                "Scale diagnosis must return ScaleDiagnosticResult"
            )
        self._validate_result(
            raw_result,
            net_overall_system_contribution,
            product_pathway,
            transition_pathway,
            evaluation_run_id,
            user_id,
            pathway_id,
        )
        return raw_result

    @staticmethod
    def _validate_inputs(
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
    ) -> None:
        if type(net_overall_system_contribution) is not NetOverallSystemContribution:
            raise ScaleDiagnosticEvaluationInvariantError(
                "Scale diagnosis requires exactly NetOverallSystemContribution"
            )
        if type(product_pathway) is not ProductPathway:
            raise ScaleDiagnosticEvaluationInvariantError(
                "Scale diagnosis requires exactly ProductPathway"
            )
        if type(transition_pathway) is not TransitionPathway:
            raise ScaleDiagnosticEvaluationInvariantError(
                "Scale diagnosis requires exactly TransitionPathway"
            )
        if system_context is not None and not isinstance(
            system_context, OpaqueReference
        ):
            raise ScaleDiagnosticEvaluationInvariantError(
                "Scale system context must be an OpaqueReference or None"
            )
        _require_tuple_of(assumptions, str, "Scale assumptions")
        _require_tuple_of(uncertainties, str, "Scale uncertainties")
        _require_tuple_of(
            evidence_references,
            SourceReference,
            "Scale evidence references",
        )
        _require_tuple_of(provenance, SourceReference, "Scale provenance")
        if not all(
            isinstance(value, str)
            for value in (user_id, pathway_id, evaluation_run_id)
        ):
            raise ScaleDiagnosticEvaluationInvariantError(
                "Scale attribution values must be strings"
            )
        if net_overall_system_contribution.product_pathway is not product_pathway:
            raise ScaleDiagnosticEvaluationInvariantError(
                "Contribution must preserve the supplied ProductPathway"
            )
        if (
            net_overall_system_contribution.transition_pathway
            is not transition_pathway
        ):
            raise ScaleDiagnosticEvaluationInvariantError(
                "Contribution must preserve the supplied TransitionPathway"
            )
        if (
            net_overall_system_contribution.evaluation_run_id != evaluation_run_id
            or product_pathway.evaluation_run_id != evaluation_run_id
        ):
            raise ScaleDiagnosticEvaluationInvariantError(
                "Scale inputs must share the supplied evaluation_run_id"
            )
        if (
            net_overall_system_contribution.user_id != user_id
            or product_pathway.user_id != user_id
        ):
            raise ScaleDiagnosticEvaluationInvariantError(
                "Scale inputs must share the supplied user_id"
            )
        if (
            net_overall_system_contribution.pathway_id != pathway_id
            or product_pathway.pathway_id != pathway_id
        ):
            raise ScaleDiagnosticEvaluationInvariantError(
                "Scale inputs must share the supplied pathway_id"
            )

    @classmethod
    def _validate_result(
        cls,
        result: ScaleDiagnosticResult,
        net_overall_system_contribution: NetOverallSystemContribution,
        product_pathway: ProductPathway,
        transition_pathway: TransitionPathway,
        evaluation_run_id: str,
        user_id: str,
        pathway_id: str,
    ) -> None:
        if result.product_pathway is not product_pathway:
            raise ScaleDiagnosticEvaluationInvariantError(
                "Scale result must preserve ProductPathway"
            )
        if (
            result.net_overall_system_contribution
            is not net_overall_system_contribution
        ):
            raise ScaleDiagnosticEvaluationInvariantError(
                "Scale result must preserve NetOverallSystemContribution"
            )
        if result.transition_pathway is not transition_pathway:
            raise ScaleDiagnosticEvaluationInvariantError(
                "Scale result must preserve authoritative TransitionPathway"
            )
        if result.evaluation_run_id != evaluation_run_id:
            raise ScaleDiagnosticEvaluationInvariantError(
                "Scale result must preserve evaluation_run_id"
            )
        if result.user_id != user_id:
            raise ScaleDiagnosticEvaluationInvariantError(
                "Scale result must preserve user_id"
            )
        if result.pathway_id != pathway_id:
            raise ScaleDiagnosticEvaluationInvariantError(
                "Scale result must preserve pathway_id"
            )
        if not isinstance(result.evaluator_version, str) or not isinstance(
            result.rule_set_version,
            str,
        ):
            raise ScaleDiagnosticEvaluationInvariantError(
                "Evaluator and rule-set versions must be strings"
            )

        findings = _require_tuple_of(
            result.scale_findings,
            ScaleFinding,
            "Scale findings",
        )
        _require_tuple_of(result.assumptions, str, "Scale result assumptions")
        _require_tuple_of(result.uncertainties, str, "Scale result uncertainties")
        _require_tuple_of(
            result.evidence_references,
            SourceReference,
            "Scale result evidence references",
        )
        _require_tuple_of(
            result.provenance,
            SourceReference,
            "Scale result provenance",
        )
        for finding in findings:
            cls._validate_finding(finding, net_overall_system_contribution)

    @staticmethod
    def _validate_finding(
        finding: ScaleFinding,
        contribution: NetOverallSystemContribution,
    ) -> None:
        if not isinstance(finding.finding_id, str) or not isinstance(
            finding.description,
            str,
        ):
            raise ScaleDiagnosticEvaluationInvariantError(
                "Scale finding identity and description must be strings"
            )
        optional_strings = (
            finding.scale_scope,
            finding.finding_type,
            finding.geographic_scope,
            finding.system_scope,
        )
        if any(
            value is not None and not isinstance(value, str)
            for value in optional_strings
        ):
            raise ScaleDiagnosticEvaluationInvariantError(
                "Scale finding scopes and type must be strings or None"
            )
        text_collections = (
            finding.statuses,
            finding.quantity_findings,
            finding.capacity_findings,
            finding.throughput_findings,
            finding.coverage_findings,
            finding.replication_findings,
            finding.deployment_findings,
            finding.scale_progression_findings,
            finding.timing_conditions,
            finding.sequencing_conditions,
            finding.constraints,
            finding.bottlenecks,
            finding.scale_increases,
            finding.unblocks,
            finding.constraint_mitigations,
            finding.workarounds,
            finding.resolution_conditions,
            finding.scale_dependent_effects,
            finding.unresolved_conditions,
        )
        if any(
            not isinstance(values, tuple)
            or not all(isinstance(value, str) for value in values)
            for values in text_collections
        ):
            raise ScaleDiagnosticEvaluationInvariantError(
                "Scale finding text collections must be tuples of strings"
            )

        contribution_findings = _require_tuple_of(
            finding.contribution_findings,
            ContributionFinding,
            "Scale contribution findings",
        )
        if any(
            not _contains_reference(
                contribution.contribution_findings,
                contribution_finding,
            )
            for contribution_finding in contribution_findings
        ):
            raise ScaleDiagnosticEvaluationInvariantError(
                "Scale contribution findings must come from the completed "
                "contribution"
            )

        pathway_engine_result = contribution.pathway_engine_result
        pathway_outputs = _require_tuple_of(
            finding.supporting_pathway_outputs,
            PathwayObject,
            "Scale supporting pathway outputs",
        )
        if any(
            not _contains_reference(contribution.product_pathway.objects, output)
            for output in pathway_outputs
        ):
            raise ScaleDiagnosticEvaluationInvariantError(
                "Scale pathway outputs must preserve ProductPathway objects"
            )

        comparison_findings = _require_tuple_of(
            finding.supporting_comparison_findings,
            ComparisonFinding,
            "Scale supporting comparison findings",
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
            raise ScaleDiagnosticEvaluationInvariantError(
                "Scale comparison findings must come from PathwayEngineResult"
            )

        queue_results = _require_tuple_of(
            finding.supporting_queue_results,
            QueueEvaluatorResult,
            "Scale supporting queue results",
        )
        if any(
            not _contains_reference(pathway_engine_result.queue_results, queue_result)
            for queue_result in queue_results
        ):
            raise ScaleDiagnosticEvaluationInvariantError(
                "Scale queue results must come from PathwayEngineResult"
            )

        fabric_results = _require_tuple_of(
            finding.supporting_fabric_results,
            FabricEvaluatorResult,
            "Scale supporting fabric results",
        )
        if any(
            not _contains_reference(
                pathway_engine_result.fabric_results,
                fabric_result,
            )
            for fabric_result in fabric_results
        ):
            raise ScaleDiagnosticEvaluationInvariantError(
                "Scale fabric results must come from PathwayEngineResult"
            )

        documentation_findings = _require_tuple_of(
            finding.supporting_documentation_findings,
            DocumentationFinding,
            "Scale supporting documentation findings",
        )
        if any(
            not _contains_reference(
                pathway_engine_result.documentation_findings,
                documentation,
            )
            for documentation in documentation_findings
        ):
            raise ScaleDiagnosticEvaluationInvariantError(
                "Scale documentation findings must come from PathwayEngineResult"
            )

        _require_tuple_of(
            finding.transition_function_references,
            OpaqueReference,
            "Scale transition function references",
        )
        _require_tuple_of(
            finding.supporting_system_references,
            OpaqueReference,
            "Scale supporting system references",
        )
        _require_tuple_of(
            finding.evidence_references,
            SourceReference,
            "Scale finding evidence references",
        )
        _require_tuple_of(
            finding.provenance,
            SourceReference,
            "Scale finding provenance",
        )
