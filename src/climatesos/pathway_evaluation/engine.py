"""Structural orchestration for the pathway-evaluation engine boundary."""

from dataclasses import dataclass
from typing import TypeVar

from .comparison import ComparisonInvariantError, validate_comparison_findings
from .interfaces import (
    DocumentationEvaluator,
    FabricEvaluator,
    PathwayComparator,
    QueueEvaluator,
)
from .models import (
    Attribute,
    ComparisonFinding,
    DocumentationFinding,
    FabricEvaluatorResult,
    InitialCharterResult,
    OpaqueReference,
    PathwayEngineResult,
    ProductAdapterResult,
    ProductFabric,
    ProductPathway,
    ProductQueueBundle,
    QueueEvaluationFailure,
    QueueEvaluatorResult,
    SourceReference,
    TransitionPathway,
)

T = TypeVar("T")


class PathwayEvaluationInvariantError(ValueError):
    """Raised when engine input or evaluator output is structurally incoherent."""


class PathwayEvaluationIncompleteError(PathwayEvaluationInvariantError):
    """Raised when a required queue evaluation did not complete."""

    def __init__(self, failure: QueueEvaluationFailure) -> None:
        super().__init__("A required queue evaluation did not complete")
        self.failure = failure


def _contains_reference(values: tuple[object, ...], candidate: object) -> bool:
    return any(value is candidate for value in values)


def _same_references(left: tuple[object, ...], right: tuple[object, ...]) -> bool:
    return len(left) == len(right) and all(
        left_item is right_item
        for left_item, right_item in zip(left, right, strict=True)
    )


def _require_tuple_of(
    value: object,
    expected_type: type[T],
    description: str,
) -> tuple[T, ...]:
    if not isinstance(value, tuple) or not all(
        isinstance(item, expected_type) for item in value
    ):
        raise PathwayEvaluationInvariantError(
            f"{description} must be a tuple of {expected_type.__name__} objects"
        )
    return value


@dataclass(frozen=True, slots=True)
class StructuralPathwayEvaluationEngine:
    """Coordinate caller-supplied evaluators without adding conclusions."""

    comparator: PathwayComparator
    queue_evaluator: QueueEvaluator
    fabric_evaluator: FabricEvaluator
    documentation_evaluator: DocumentationEvaluator
    evaluator_versions: tuple[Attribute, ...] = ()
    rule_set_versions: tuple[Attribute, ...] = ()

    def evaluate(
        self,
        adapter_result: ProductAdapterResult,
        initial_charter_result: InitialCharterResult,
        queue_bundles: tuple[ProductQueueBundle, ...],
        fabrics: tuple[ProductFabric, ...],
        transition_pathway: TransitionPathway,
        system_context: OpaqueReference | None,
        evaluation_run_id: str,
    ) -> PathwayEngineResult:
        """Execute specified routing and consolidate validated outputs."""

        pathway = adapter_result.product_pathway
        self._validate_inputs(
            adapter_result,
            initial_charter_result,
            queue_bundles,
            fabrics,
        )
        direct = self._validate_comparison_findings(
            self.comparator.compare_direct(
                pathway,
                transition_pathway,
                system_context,
            ),
            pathway,
            "Direct comparison findings",
        )
        substitution = self._validate_comparison_findings(
            self.comparator.evaluate_substitution_and_combination(
                pathway,
                transition_pathway,
                system_context,
            ),
            pathway,
            "Substitution and combination findings",
        )
        pathway_findings = direct + substitution
        downstream = self._validate_comparison_findings(
            self.comparator.propagate_downstream(
                pathway,
                transition_pathway,
                pathway_findings,
                system_context,
            ),
            pathway,
            "Downstream propagation findings",
        )

        queue_results: list[QueueEvaluatorResult] = []
        for queue in queue_bundles:
            queue_output = self.queue_evaluator.evaluate(
                queue,
                pathway,
                pathway_findings,
                downstream,
                transition_pathway,
                system_context,
                evaluation_run_id,
            )
            if isinstance(queue_output, QueueEvaluationFailure):
                self._validate_queue_record(
                    queue_output,
                    queue,
                    pathway,
                    evaluation_run_id,
                )
                raise PathwayEvaluationIncompleteError(queue_output)
            if not isinstance(queue_output, QueueEvaluatorResult):
                raise PathwayEvaluationInvariantError(
                    "Queue evaluation must return a completed result or failure"
                )
            self._validate_queue_result(
                queue_output,
                queue,
                pathway,
                transition_pathway,
                system_context,
                evaluation_run_id,
            )
            queue_results.append(queue_output)
        completed_queue_results = tuple(queue_results)

        fabric_results: list[FabricEvaluatorResult] = []
        for fabric in fabrics:
            applicable_results = tuple(
                result
                for bundle in fabric.queue_bundles
                for result in completed_queue_results
                if result.evaluated_queue is bundle
            )
            fabric_result = self.fabric_evaluator.evaluate(
                fabric,
                applicable_results,
                pathway_findings,
                downstream,
                transition_pathway,
                system_context,
                evaluation_run_id,
            )
            self._validate_fabric_result(
                fabric_result,
                fabric,
                applicable_results,
                pathway_findings,
                downstream,
                transition_pathway,
                system_context,
                evaluation_run_id,
            )
            fabric_results.append(fabric_result)
        completed_fabric_results = tuple(fabric_results)

        all_comparison_findings = pathway_findings + downstream
        documentation_findings = _require_tuple_of(
            self.documentation_evaluator.evaluate(
                adapter_result,
                completed_queue_results,
                completed_fabric_results,
                all_comparison_findings,
            ),
            DocumentationFinding,
            "Documentation findings",
        )
        token = pathway.identity_token
        return PathwayEngineResult(
            product_pathway=pathway,
            transition_pathway=transition_pathway,
            initial_charter_result=initial_charter_result,
            direct_comparison_findings=direct,
            substitution_combination_findings=substitution,
            downstream_propagation_findings=downstream,
            queue_results=completed_queue_results,
            fabric_results=completed_fabric_results,
            documentation_findings=documentation_findings,
            evaluation_run_id=evaluation_run_id,
            system_context=system_context,
            evaluator_versions=self.evaluator_versions,
            rule_set_versions=self.rule_set_versions,
            user_id=token.user_id,
            pathway_id=token.pathway_id,
            assumptions=self._collect_assumptions(
                pathway,
                completed_queue_results,
                completed_fabric_results,
            ),
            uncertainties=self._collect_uncertainties(
                pathway,
                completed_queue_results,
                completed_fabric_results,
            ),
            evidence_references=self._collect_evidence(
                pathway,
                direct,
                substitution,
                downstream,
                completed_queue_results,
                completed_fabric_results,
                documentation_findings,
            ),
            provenance=adapter_result.intake_bundle.provenance,
        )

    @staticmethod
    def _validate_comparison_findings(
        findings: object,
        pathway: ProductPathway,
        description: str,
    ) -> tuple[ComparisonFinding, ...]:
        try:
            return validate_comparison_findings(findings, pathway, description)
        except ComparisonInvariantError as error:
            raise PathwayEvaluationInvariantError(str(error)) from error

    @staticmethod
    def _validate_inputs(
        adapter_result: ProductAdapterResult,
        initial_charter_result: InitialCharterResult,
        queue_bundles: tuple[ProductQueueBundle, ...],
        fabrics: tuple[ProductFabric, ...],
    ) -> None:
        if initial_charter_result.adapter_result is not adapter_result:
            raise PathwayEvaluationInvariantError(
                "InitialCharterResult must preserve the ProductAdapterResult reference"
            )
        pathway = adapter_result.product_pathway
        if adapter_result.intake_bundle.identity_token != pathway.identity_token:
            raise PathwayEvaluationInvariantError(
                "ProductIntakeBundle attribution must match the ProductPathway"
            )
        _require_tuple_of(queue_bundles, ProductQueueBundle, "Queue bundles")
        _require_tuple_of(fabrics, ProductFabric, "Fabrics")
        for bundle in queue_bundles:
            if bundle.product_pathway is not pathway:
                raise PathwayEvaluationInvariantError(
                    "ProductQueueBundle must preserve ProductPathway ownership"
                )
            for element in bundle.queue_elements:
                if not _contains_reference(pathway.queue_elements, element):
                    raise PathwayEvaluationInvariantError(
                        "ProductQueueBundle may contain only pathway queue elements"
                    )
        for fabric in fabrics:
            if fabric.product_pathway is not pathway:
                raise PathwayEvaluationInvariantError(
                    "ProductFabric must preserve ProductPathway ownership"
                )
            if any(
                not _contains_reference(queue_bundles, bundle)
                for bundle in fabric.queue_bundles
            ):
                raise PathwayEvaluationInvariantError(
                    "ProductFabric may reference only supplied queue bundles"
                )

    @staticmethod
    def _validate_queue_record(
        record: QueueEvaluatorResult | QueueEvaluationFailure | object,
        queue: ProductQueueBundle,
        pathway: ProductPathway,
        evaluation_run_id: str,
    ) -> None:
        token = pathway.identity_token
        if getattr(record, "evaluated_queue", None) is not queue:
            raise PathwayEvaluationInvariantError(
                "Queue result must preserve the evaluated queue reference"
            )
        if getattr(record, "evaluation_run_id", None) != evaluation_run_id:
            raise PathwayEvaluationInvariantError(
                "Queue result must preserve the evaluation run identity"
            )
        if (
            getattr(record, "user_id", None) != token.user_id
            or getattr(record, "pathway_id", None) != token.pathway_id
        ):
            raise PathwayEvaluationInvariantError(
                "Queue result attribution must match the ProductPathway"
            )

    @classmethod
    def _validate_queue_result(
        cls,
        result: QueueEvaluatorResult,
        queue: ProductQueueBundle,
        pathway: ProductPathway,
        transition_pathway: TransitionPathway,
        system_context: OpaqueReference | None,
        evaluation_run_id: str,
    ) -> None:
        cls._validate_queue_record(result, queue, pathway, evaluation_run_id)
        if result.transition_pathway is not transition_pathway:
            raise PathwayEvaluationInvariantError(
                "QueueEvaluatorResult must preserve TransitionPathway context"
            )
        execution = result.execution_result
        cls._validate_queue_record(execution, queue, pathway, evaluation_run_id)
        if (
            execution.transition_pathway is not None
            and execution.transition_pathway is not transition_pathway
        ):
            raise PathwayEvaluationInvariantError(
                "QueueExecutionResult contains a different TransitionPathway"
            )
        if (
            execution.system_context is not None
            and execution.system_context is not system_context
        ):
            raise PathwayEvaluationInvariantError(
                "QueueExecutionResult contains a different system context"
            )
        for records in (result.progress_records, execution.progress_records):
            for record in records:
                cls._validate_queue_record(
                    record,
                    queue,
                    pathway,
                    evaluation_run_id,
                )

    @staticmethod
    def _validate_fabric_result(
        result: object,
        fabric: ProductFabric,
        queue_results: tuple[QueueEvaluatorResult, ...],
        pathway_findings: tuple[ComparisonFinding, ...],
        downstream: tuple[ComparisonFinding, ...],
        transition_pathway: TransitionPathway,
        system_context: OpaqueReference | None,
        evaluation_run_id: str,
    ) -> None:
        if not isinstance(result, FabricEvaluatorResult):
            raise PathwayEvaluationInvariantError(
                "Fabric evaluation must return FabricEvaluatorResult"
            )
        token = fabric.product_pathway.identity_token
        if result.product_fabric is not fabric:
            raise PathwayEvaluationInvariantError(
                "FabricEvaluatorResult must preserve the ProductFabric reference"
            )
        if not _same_references(result.queue_results, queue_results):
            raise PathwayEvaluationInvariantError(
                "FabricEvaluatorResult must preserve applicable queue results"
            )
        if not _same_references(
            result.pathway_comparison_findings,
            pathway_findings,
        ):
            raise PathwayEvaluationInvariantError(
                "FabricEvaluatorResult must preserve pathway comparison findings"
            )
        if not _same_references(
            result.downstream_propagation_findings,
            downstream,
        ):
            raise PathwayEvaluationInvariantError(
                "FabricEvaluatorResult must preserve downstream findings"
            )
        if result.transition_pathway is not transition_pathway:
            raise PathwayEvaluationInvariantError(
                "FabricEvaluatorResult must preserve TransitionPathway context"
            )
        if result.system_context is not system_context:
            raise PathwayEvaluationInvariantError(
                "FabricEvaluatorResult must preserve system context"
            )
        if result.evaluation_run_id != evaluation_run_id:
            raise PathwayEvaluationInvariantError(
                "FabricEvaluatorResult must preserve the evaluation run identity"
            )
        if result.user_id != token.user_id or result.pathway_id != token.pathway_id:
            raise PathwayEvaluationInvariantError(
                "Fabric result attribution must match the ProductPathway"
            )

    @staticmethod
    def _collect_assumptions(
        pathway: ProductPathway,
        queue_results: tuple[QueueEvaluatorResult, ...],
        fabric_results: tuple[FabricEvaluatorResult, ...],
    ) -> tuple[str, ...]:
        return pathway.assumptions + tuple(
            value
            for result in queue_results
            for value in result.assumptions
        ) + tuple(
            value
            for result in fabric_results
            for value in result.assumptions
        )

    @staticmethod
    def _collect_uncertainties(
        pathway: ProductPathway,
        queue_results: tuple[QueueEvaluatorResult, ...],
        fabric_results: tuple[FabricEvaluatorResult, ...],
    ) -> tuple[str, ...]:
        return pathway.uncertainties + tuple(
            value
            for result in queue_results
            for value in result.uncertainties
        ) + tuple(
            value
            for result in fabric_results
            for value in result.uncertainties
        )

    @staticmethod
    def _collect_evidence(
        pathway: ProductPathway,
        direct: tuple[ComparisonFinding, ...],
        substitution: tuple[ComparisonFinding, ...],
        downstream: tuple[ComparisonFinding, ...],
        queue_results: tuple[QueueEvaluatorResult, ...],
        fabric_results: tuple[FabricEvaluatorResult, ...],
        documentation_findings: tuple[DocumentationFinding, ...],
    ) -> tuple[SourceReference, ...]:
        sources = [pathway.evidence_references]
        sources.extend(result.evidence_references for result in direct)
        sources.extend(result.evidence_references for result in substitution)
        sources.extend(result.evidence_references for result in downstream)
        sources.extend(result.evidence_references for result in queue_results)
        sources.extend(result.evidence_references for result in fabric_results)
        sources.extend(
            result.evidence_references for result in documentation_findings
        )
        return tuple(reference for source in sources for reference in source)
