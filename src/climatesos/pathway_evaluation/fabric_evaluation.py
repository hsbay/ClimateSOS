"""Structural boundary for caller-supplied fabric evaluation."""

from collections.abc import Callable
from dataclasses import dataclass

from .models import (
    ComparisonFinding,
    FabricEvaluatorResult,
    OpaqueReference,
    ProductFabric,
    QueueEvaluatorResult,
    TransitionPathway,
)

FabricEvaluationFunction = Callable[
    [
        ProductFabric,
        tuple[QueueEvaluatorResult, ...],
        tuple[ComparisonFinding, ...],
        tuple[ComparisonFinding, ...],
        TransitionPathway,
        OpaqueReference | None,
        str,
    ],
    FabricEvaluatorResult,
]


class FabricEvaluationInvariantError(ValueError):
    """Raised when a fabric result violates structural integrity."""


def _same_references(left: tuple[object, ...], right: tuple[object, ...]) -> bool:
    return len(left) == len(right) and all(
        left_item is right_item
        for left_item, right_item in zip(left, right, strict=True)
    )


@dataclass(frozen=True, slots=True)
class ValidatedFabricEvaluator:
    """Route fabric context and validate caller-supplied coordination output."""

    evaluation_function: FabricEvaluationFunction

    def evaluate(
        self,
        fabric: ProductFabric,
        queue_results: tuple[QueueEvaluatorResult, ...],
        pathway_comparison_findings: tuple[ComparisonFinding, ...],
        downstream_propagation_findings: tuple[ComparisonFinding, ...],
        transition_pathway: TransitionPathway,
        system_context: OpaqueReference | None,
        evaluation_run_id: str,
    ) -> FabricEvaluatorResult:
        """Execute evaluation without defining coordination-condition semantics."""

        self._validate_inputs(fabric, queue_results, evaluation_run_id)
        result = self.evaluation_function(
            fabric,
            queue_results,
            pathway_comparison_findings,
            downstream_propagation_findings,
            transition_pathway,
            system_context,
            evaluation_run_id,
        )
        if not isinstance(result, FabricEvaluatorResult):
            raise FabricEvaluationInvariantError(
                "Fabric evaluation must return FabricEvaluatorResult"
            )
        token = fabric.product_pathway.identity_token
        if result.product_fabric is not fabric:
            raise FabricEvaluationInvariantError(
                "FabricEvaluatorResult must preserve the ProductFabric reference"
            )
        if not _same_references(result.queue_results, queue_results):
            raise FabricEvaluationInvariantError(
                "FabricEvaluatorResult must preserve applicable queue results"
            )
        if not _same_references(
            result.pathway_comparison_findings,
            pathway_comparison_findings,
        ):
            raise FabricEvaluationInvariantError(
                "FabricEvaluatorResult must preserve pathway comparison findings"
            )
        if not _same_references(
            result.downstream_propagation_findings,
            downstream_propagation_findings,
        ):
            raise FabricEvaluationInvariantError(
                "FabricEvaluatorResult must preserve downstream propagation findings"
            )
        if result.transition_pathway is not transition_pathway:
            raise FabricEvaluationInvariantError(
                "FabricEvaluatorResult must preserve TransitionPathway context"
            )
        if result.system_context is not system_context:
            raise FabricEvaluationInvariantError(
                "FabricEvaluatorResult must preserve system context"
            )
        if result.evaluation_run_id != evaluation_run_id:
            raise FabricEvaluationInvariantError(
                "FabricEvaluatorResult must preserve the evaluation run identity"
            )
        if result.user_id != token.user_id or result.pathway_id != token.pathway_id:
            raise FabricEvaluationInvariantError(
                "FabricEvaluatorResult attribution must match the ProductPathway"
            )
        return result

    @staticmethod
    def _validate_inputs(
        fabric: ProductFabric,
        queue_results: tuple[QueueEvaluatorResult, ...],
        evaluation_run_id: str,
    ) -> None:
        token = fabric.product_pathway.identity_token
        if len(queue_results) != len(fabric.queue_bundles):
            raise FabricEvaluationInvariantError(
                "Fabric evaluation requires one result per participating queue bundle"
            )
        remaining_bundles = list(fabric.queue_bundles)
        for queue_result in queue_results:
            matching_index = next(
                (
                    index
                    for index, bundle in enumerate(remaining_bundles)
                    if queue_result.evaluated_queue is bundle
                ),
                None,
            )
            if matching_index is None:
                raise FabricEvaluationInvariantError(
                    "Queue result must evaluate a participating queue bundle"
                )
            remaining_bundles.pop(matching_index)
            if queue_result.evaluation_run_id != evaluation_run_id:
                raise FabricEvaluationInvariantError(
                    "Queue and fabric results must share an evaluation run"
                )
            if (
                queue_result.user_id != token.user_id
                or queue_result.pathway_id != token.pathway_id
            ):
                raise FabricEvaluationInvariantError(
                    "Queue result attribution must match the ProductFabric pathway"
                )
