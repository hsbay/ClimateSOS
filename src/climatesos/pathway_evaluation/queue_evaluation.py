"""Structural execution boundary for caller-supplied queue evaluation."""

from collections.abc import Callable
from dataclasses import dataclass

from .models import (
    ComparisonFinding,
    OpaqueReference,
    ProductPathway,
    ProductQueueBundle,
    QueueElement,
    QueueEvaluationFailure,
    QueueEvaluatorResult,
    QueueProgressRecord,
    QueueSubject,
    TransitionPathway,
)

QueueEvaluationFunction = Callable[
    [
        QueueSubject,
        ProductPathway,
        tuple[ComparisonFinding, ...],
        tuple[ComparisonFinding, ...],
        TransitionPathway,
        OpaqueReference | None,
        str,
    ],
    QueueEvaluatorResult | QueueEvaluationFailure,
]


class QueueEvaluationInvariantError(ValueError):
    """Raised when a queue evaluation output violates structural integrity."""


def _contains_reference(values: tuple[object, ...], candidate: object) -> bool:
    return any(value is candidate for value in values)


@dataclass(frozen=True, slots=True)
class ValidatedQueueEvaluator:
    """Route queue context and validate caller-supplied evaluation output."""

    evaluation_function: QueueEvaluationFunction

    def evaluate(
        self,
        queue: QueueSubject,
        pathway: ProductPathway,
        pathway_comparison_findings: tuple[ComparisonFinding, ...],
        downstream_propagation_findings: tuple[ComparisonFinding, ...],
        transition_pathway: TransitionPathway,
        system_context: OpaqueReference | None,
        evaluation_run_id: str,
    ) -> QueueEvaluatorResult | QueueEvaluationFailure:
        """Execute one attempt without supplying queue-domain conclusions."""

        self._validate_subject(queue, pathway)
        output = self.evaluation_function(
            queue,
            pathway,
            pathway_comparison_findings,
            downstream_propagation_findings,
            transition_pathway,
            system_context,
            evaluation_run_id,
        )
        if isinstance(output, QueueEvaluationFailure):
            self._validate_common(output, queue, pathway, evaluation_run_id)
            return output
        if not isinstance(output, QueueEvaluatorResult):
            raise QueueEvaluationInvariantError(
                "Queue evaluation must return a completed result or failure"
            )

        self._validate_common(output, queue, pathway, evaluation_run_id)
        if output.transition_pathway is not transition_pathway:
            raise QueueEvaluationInvariantError(
                "QueueEvaluatorResult must preserve TransitionPathway context"
            )

        execution = output.execution_result
        self._validate_common(execution, queue, pathway, evaluation_run_id)
        if (
            execution.transition_pathway is not None
            and execution.transition_pathway is not transition_pathway
        ):
            raise QueueEvaluationInvariantError(
                "QueueExecutionResult contains a different TransitionPathway"
            )
        if (
            execution.system_context is not None
            and execution.system_context is not system_context
        ):
            raise QueueEvaluationInvariantError(
                "QueueExecutionResult contains a different system context"
            )
        self._validate_progress(
            output.progress_records,
            queue,
            pathway,
            evaluation_run_id,
        )
        self._validate_progress(
            execution.progress_records,
            queue,
            pathway,
            evaluation_run_id,
        )
        return output

    @staticmethod
    def _validate_subject(queue: QueueSubject, pathway: ProductPathway) -> None:
        if isinstance(queue, QueueElement):
            if not _contains_reference(pathway.queue_elements, queue):
                raise QueueEvaluationInvariantError(
                    "QueueElement must belong to the evaluated ProductPathway"
                )
        elif isinstance(queue, ProductQueueBundle):
            if queue.product_pathway is not pathway:
                raise QueueEvaluationInvariantError(
                    "ProductQueueBundle must belong to the evaluated ProductPathway"
                )
        else:
            raise QueueEvaluationInvariantError("Unsupported queue subject")

    @staticmethod
    def _validate_common(
        record: QueueEvaluatorResult | QueueEvaluationFailure | object,
        queue: QueueSubject,
        pathway: ProductPathway,
        evaluation_run_id: str,
    ) -> None:
        token = pathway.identity_token
        if getattr(record, "evaluated_queue", None) is not queue:
            raise QueueEvaluationInvariantError(
                "Queue result must preserve the evaluated queue reference"
            )
        if getattr(record, "evaluation_run_id", None) != evaluation_run_id:
            raise QueueEvaluationInvariantError(
                "Queue result must preserve the evaluation run identity"
            )
        if (
            getattr(record, "user_id", None) != token.user_id
            or getattr(record, "pathway_id", None) != token.pathway_id
        ):
            raise QueueEvaluationInvariantError(
                "Queue result attribution must match the ProductPathway"
            )

    @staticmethod
    def _validate_progress(
        records: tuple[QueueProgressRecord, ...],
        queue: QueueSubject,
        pathway: ProductPathway,
        evaluation_run_id: str,
    ) -> None:
        token = pathway.identity_token
        for record in records:
            if record.evaluated_queue is not queue:
                raise QueueEvaluationInvariantError(
                    "QueueProgressRecord must preserve the evaluated queue reference"
                )
            if record.evaluation_run_id != evaluation_run_id:
                raise QueueEvaluationInvariantError(
                    "QueueProgressRecord must preserve the evaluation run identity"
                )
            if record.user_id != token.user_id or record.pathway_id != token.pathway_id:
                raise QueueEvaluationInvariantError(
                    "QueueProgressRecord attribution must match the ProductPathway"
                )
