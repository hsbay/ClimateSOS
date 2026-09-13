"""Structural boundary for caller-supplied documentation evaluation."""

from collections.abc import Callable
from dataclasses import dataclass

from .comparison import ComparisonInvariantError, validate_comparison_findings
from .models import (
    ComparisonFinding,
    DocumentationFinding,
    FabricEvaluatorResult,
    ProductAdapterResult,
    ProductQueueBundle,
    QueueElement,
    QueueEvaluatorResult,
    SourceReference,
)

DocumentationEvaluationFunction = Callable[
    [
        ProductAdapterResult,
        tuple[QueueEvaluatorResult, ...],
        tuple[FabricEvaluatorResult, ...],
        tuple[ComparisonFinding, ...],
    ],
    tuple[DocumentationFinding, ...],
]


class DocumentationEvaluationInvariantError(ValueError):
    """Raised when documentation inputs or findings are incoherent."""


def _same_reference_in(values: tuple[object, ...], candidate: object) -> bool:
    return any(value is candidate for value in values)


@dataclass(frozen=True, slots=True)
class ValidatedDocumentationEvaluator:
    """Route existing artifacts without defining documentation policy."""

    evaluation_function: DocumentationEvaluationFunction

    def evaluate(
        self,
        adapter_result: ProductAdapterResult,
        queue_results: tuple[QueueEvaluatorResult, ...],
        fabric_results: tuple[FabricEvaluatorResult, ...],
        comparison_findings: tuple[ComparisonFinding, ...],
    ) -> tuple[DocumentationFinding, ...]:
        """Validate artifacts, invoke the caller, and validate neutral findings."""

        self._validate_inputs(
            adapter_result,
            queue_results,
            fabric_results,
            comparison_findings,
        )
        findings = self.evaluation_function(
            adapter_result,
            queue_results,
            fabric_results,
            comparison_findings,
        )
        if not isinstance(findings, tuple) or not all(
            isinstance(finding, DocumentationFinding) for finding in findings
        ):
            raise DocumentationEvaluationInvariantError(
                "Documentation findings must be a tuple of DocumentationFinding objects"
            )
        for finding in findings:
            if not isinstance(finding.evidence_references, tuple) or not all(
                isinstance(reference, SourceReference)
                for reference in finding.evidence_references
            ):
                raise DocumentationEvaluationInvariantError(
                    "Documentation evidence references must be SourceReference objects"
                )
        return findings

    @staticmethod
    def _validate_inputs(
        adapter_result: ProductAdapterResult,
        queue_results: tuple[QueueEvaluatorResult, ...],
        fabric_results: tuple[FabricEvaluatorResult, ...],
        comparison_findings: tuple[ComparisonFinding, ...],
    ) -> None:
        if not isinstance(adapter_result, ProductAdapterResult):
            raise DocumentationEvaluationInvariantError(
                "Documentation evaluation requires ProductAdapterResult"
            )
        pathway = adapter_result.product_pathway
        if adapter_result.intake_bundle.identity_token != pathway.identity_token:
            raise DocumentationEvaluationInvariantError(
                "ProductIntakeBundle attribution must match the ProductPathway"
            )
        if not isinstance(queue_results, tuple) or not all(
            isinstance(result, QueueEvaluatorResult) for result in queue_results
        ):
            raise DocumentationEvaluationInvariantError(
                "Queue results must be a tuple of completed "
                "QueueEvaluatorResult objects"
            )
        for result in queue_results:
            subject = result.evaluated_queue
            if isinstance(subject, QueueElement):
                belongs_to_pathway = _same_reference_in(pathway.queue_elements, subject)
            elif isinstance(subject, ProductQueueBundle):
                belongs_to_pathway = subject.product_pathway is pathway
            else:
                belongs_to_pathway = False  # type: ignore[unreachable]
            if not belongs_to_pathway:
                raise DocumentationEvaluationInvariantError(
                    "Queue result must belong to the adapter ProductPathway"
                )
            if (
                result.user_id != pathway.user_id
                or result.pathway_id != pathway.pathway_id
            ):
                raise DocumentationEvaluationInvariantError(
                    "Queue result attribution must match the ProductPathway"
                )

        if not isinstance(fabric_results, tuple) or not all(
            isinstance(result, FabricEvaluatorResult) for result in fabric_results
        ):
            raise DocumentationEvaluationInvariantError(
                "Fabric results must be a tuple of FabricEvaluatorResult objects"
            )
        for fabric_result in fabric_results:
            if fabric_result.product_fabric.product_pathway is not pathway:
                raise DocumentationEvaluationInvariantError(
                    "Fabric result must belong to the adapter ProductPathway"
                )
            if (
                fabric_result.user_id != pathway.user_id
                or fabric_result.pathway_id != pathway.pathway_id
            ):
                raise DocumentationEvaluationInvariantError(
                    "Fabric result attribution must match the ProductPathway"
                )
            if any(
                not _same_reference_in(queue_results, queue_result)
                for queue_result in fabric_result.queue_results
            ):
                raise DocumentationEvaluationInvariantError(
                    "Fabric result must preserve supplied queue result references"
                )

        try:
            validate_comparison_findings(
                comparison_findings,
                pathway,
                "Comparison findings",
            )
        except ComparisonInvariantError as error:
            raise DocumentationEvaluationInvariantError(str(error)) from error
