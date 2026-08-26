"""Structural assembly boundaries for pathway-owned queues and fabrics."""

from collections.abc import Callable
from dataclasses import dataclass

from .interfaces import FabricAssembler, QueueBundler
from .models import (
    InitialCharterResult,
    ProductFabric,
    ProductPathway,
    ProductQueueBundle,
)

QueueGroupingFunction = Callable[
    [ProductPathway],
    tuple[ProductQueueBundle, ...],
]
FabricAssemblyFunction = Callable[
    [ProductPathway, tuple[ProductQueueBundle, ...]],
    tuple[ProductFabric, ...],
]


class AssemblyInvariantError(ValueError):
    """Raised when an assembly product violates pathway ownership."""


def _contains_reference(values: tuple[object, ...], candidate: object) -> bool:
    return any(value is candidate for value in values)


@dataclass(frozen=True, slots=True)
class ValidatedQueueBundler:
    """Delegate grouping decisions and enforce pathway-owned structure."""

    grouping_function: QueueGroupingFunction

    def bundle(self, pathway: ProductPathway) -> tuple[ProductQueueBundle, ...]:
        """Return validated immutable bundles for one pathway."""

        bundles = self.grouping_function(pathway)
        if not isinstance(bundles, tuple):
            raise AssemblyInvariantError("QueueBundler must return an immutable tuple")

        bundle_ids: set[str] = set()
        for bundle in bundles:
            if bundle.product_pathway is not pathway:
                raise AssemblyInvariantError(
                    "ProductQueueBundle must preserve its ProductPathway reference"
                )
            if bundle.bundle_id in bundle_ids:
                raise AssemblyInvariantError(
                    f"Duplicate queue bundle identifier: {bundle.bundle_id}"
                )
            bundle_ids.add(bundle.bundle_id)
            if not bundle.queue_elements:
                raise AssemblyInvariantError(
                    "ProductQueueBundle must reference at least one queue element"
                )
            for queue_element in bundle.queue_elements:
                if not _contains_reference(pathway.queue_elements, queue_element):
                    raise AssemblyInvariantError(
                        "ProductQueueBundle may contain only pathway queue elements"
                    )
            for relationship in bundle.relationships:
                if not _contains_reference(pathway.relationships, relationship):
                    raise AssemblyInvariantError(
                        "ProductQueueBundle may contain only pathway relationships"
                    )
        return bundles


@dataclass(frozen=True, slots=True)
class ValidatedFabricAssembler:
    """Delegate fabric membership and enforce bundle ownership."""

    assembly_function: FabricAssemblyFunction

    def assemble(
        self,
        pathway: ProductPathway,
        queue_bundles: tuple[ProductQueueBundle, ...],
    ) -> tuple[ProductFabric, ...]:
        """Return validated immutable fabrics for one pathway."""

        fabrics = self.assembly_function(pathway, queue_bundles)
        if not isinstance(fabrics, tuple):
            raise AssemblyInvariantError(
                "FabricAssembler must return an immutable tuple"
            )

        fabric_ids: set[str] = set()
        for fabric in fabrics:
            if fabric.product_pathway is not pathway:
                raise AssemblyInvariantError(
                    "ProductFabric must preserve its ProductPathway reference"
                )
            if fabric.fabric_id in fabric_ids:
                raise AssemblyInvariantError(
                    f"Duplicate fabric identifier: {fabric.fabric_id}"
                )
            fabric_ids.add(fabric.fabric_id)
            if len(fabric.queue_bundles) < 2:
                raise AssemblyInvariantError(
                    "ProductFabric must coordinate multiple queue bundles"
                )
            for bundle in fabric.queue_bundles:
                if not _contains_reference(queue_bundles, bundle):
                    raise AssemblyInvariantError(
                        "ProductFabric may reference only supplied queue bundles"
                    )
                if bundle.product_pathway is not pathway:
                    raise AssemblyInvariantError(
                        "ProductFabric queue bundles must share pathway ownership"
                    )
            for relationship in fabric.relationships:
                if not _contains_reference(pathway.relationships, relationship):
                    raise AssemblyInvariantError(
                        "ProductFabric may contain only pathway relationships"
                    )
        return fabrics


@dataclass(frozen=True, slots=True)
class StructuralProductAssembly:
    """Coordinate structural assembly after the Charter-stage precondition."""

    queue_bundler: QueueBundler
    fabric_assembler: FabricAssembler | None = None

    def assemble(
        self,
        initial_result: InitialCharterResult,
    ) -> tuple[tuple[ProductQueueBundle, ...], tuple[ProductFabric, ...]]:
        """Assemble queue bundles and optional fabrics without evaluation."""

        pathway = initial_result.adapter_result.product_pathway
        queue_bundles = self.queue_bundler.bundle(pathway)
        if self.fabric_assembler is None:
            return queue_bundles, ()
        fabrics = self.fabric_assembler.assemble(pathway, queue_bundles)
        return queue_bundles, fabrics
