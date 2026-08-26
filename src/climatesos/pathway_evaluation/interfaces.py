"""Work-performing component contracts for the specified foundation.

These protocols define ownership boundaries only. Concrete evaluation rules are
absent until their semantics are specified.
"""

from typing import Protocol

from .models import (
    CharterEvaluationContext,
    ComparisonFinding,
    DocumentationFinding,
    FabricEvaluatorResult,
    InitialCharterResult,
    IntegratedCharterResult,
    OpaqueReference,
    PathwayEngineResult,
    ProductAdapterResult,
    ProductFabric,
    ProductIntakeBundle,
    ProductPathway,
    ProductQueueBundle,
    QueueEvaluationFailure,
    QueueEvaluatorResult,
    QueueSubject,
    TransitionPathway,
)


class ProductAdapter(Protocol):
    """Translate one immutable intake bundle into one normalized pathway."""

    def adapt(self, intake_bundle: ProductIntakeBundle) -> ProductAdapterResult: ...


class CharterEvaluator(Protocol):
    """Run complete, independent Initial and Integrated Charter passes."""

    def evaluate_initial(
        self,
        adapter_result: ProductAdapterResult,
        context: CharterEvaluationContext,
    ) -> InitialCharterResult: ...

    def evaluate_integrated(
        self,
        engine_result: PathwayEngineResult,
        context: CharterEvaluationContext,
    ) -> IntegratedCharterResult: ...


class QueueBundler(Protocol):
    """Group only queue elements already represented by a ProductPathway."""

    def bundle(self, pathway: ProductPathway) -> tuple[ProductQueueBundle, ...]: ...


class FabricAssembler(Protocol):
    """Group applicable queue bundles without evaluating fabric readiness."""

    def assemble(
        self,
        pathway: ProductPathway,
        queue_bundles: tuple[ProductQueueBundle, ...],
    ) -> tuple[ProductFabric, ...]: ...


class ProductAssembly(Protocol):
    """Coordinate bundling and optional fabric assembly."""

    def assemble(
        self,
        initial_result: InitialCharterResult,
    ) -> tuple[tuple[ProductQueueBundle, ...], tuple[ProductFabric, ...]]: ...


class PathwayComparator(Protocol):
    """Produce comparison findings without modifying either pathway."""

    def compare_direct(
        self,
        pathway: ProductPathway,
        transition_pathway: TransitionPathway,
    ) -> tuple[ComparisonFinding, ...]: ...

    def evaluate_substitution_and_combination(
        self,
        pathway: ProductPathway,
        transition_pathway: TransitionPathway,
    ) -> tuple[ComparisonFinding, ...]: ...

    def propagate_downstream(
        self,
        pathway: ProductPathway,
        transition_pathway: TransitionPathway,
        comparison_findings: tuple[ComparisonFinding, ...],
    ) -> tuple[ComparisonFinding, ...]: ...


class QueueEvaluator(Protocol):
    """Evaluate one member of a pathway's queue family for one run."""

    def evaluate(
        self,
        queue: QueueSubject,
        pathway: ProductPathway,
        pathway_comparison_findings: tuple[ComparisonFinding, ...],
        downstream_propagation_findings: tuple[ComparisonFinding, ...],
        transition_pathway: TransitionPathway,
        system_context: OpaqueReference | None,
        evaluation_run_id: str,
    ) -> QueueEvaluatorResult | QueueEvaluationFailure: ...


class FabricEvaluator(Protocol):
    """Evaluate coordination without mutating a ProductFabric or queue result."""

    def evaluate(
        self,
        fabric: ProductFabric,
        queue_results: tuple[QueueEvaluatorResult, ...],
        pathway_comparison_findings: tuple[ComparisonFinding, ...],
        downstream_propagation_findings: tuple[ComparisonFinding, ...],
        transition_pathway: TransitionPathway,
        evaluation_run_id: str,
    ) -> FabricEvaluatorResult: ...


class DocumentationEvaluator(Protocol):
    """Evaluate evidence and provenance reached through preserved references."""

    def evaluate(
        self,
        adapter_result: ProductAdapterResult,
        queue_results: tuple[QueueEvaluatorResult, ...],
        fabric_results: tuple[FabricEvaluatorResult, ...],
        comparison_findings: tuple[ComparisonFinding, ...],
    ) -> tuple[DocumentationFinding, ...]: ...


class PathwayEvaluationEngine(Protocol):
    """Orchestrate specified evaluators and produce PathwayEngineResult."""

    def evaluate(
        self,
        adapter_result: ProductAdapterResult,
        initial_charter_result: InitialCharterResult,
        queue_bundles: tuple[ProductQueueBundle, ...],
        fabrics: tuple[ProductFabric, ...],
        transition_pathway: TransitionPathway,
        system_context: OpaqueReference | None,
        evaluation_run_id: str,
    ) -> PathwayEngineResult: ...
