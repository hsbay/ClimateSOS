"""Structural assembly boundaries for pathway-owned queues and fabrics."""

from collections.abc import Callable
from dataclasses import dataclass

from .enums import CharterCheckStatus
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


_INITIAL_CHARTER_INTEGRITY_FAILURES = frozenset(
    {
        CharterCheckStatus.ERROR,
        CharterCheckStatus.MISSING,
        CharterCheckStatus.NULL,
        CharterCheckStatus.NOACK,
    }
)


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

        self._validate_initial_result(initial_result)
        pathway = initial_result.adapter_result.product_pathway
        queue_bundles = self.queue_bundler.bundle(pathway)
        if self.fabric_assembler is None:
            return queue_bundles, ()
        fabrics = self.fabric_assembler.assemble(pathway, queue_bundles)
        return queue_bundles, fabrics

    @staticmethod
    def _validate_initial_result(initial_result: InitialCharterResult) -> None:
        if not isinstance(initial_result, InitialCharterResult):
            raise AssemblyInvariantError(
                "ProductAssembly requires a completed InitialCharterResult"
            )
        if (
            initial_result.status == "ERROR"
            or initial_result.execution_error is not None
        ):
            raise AssemblyInvariantError(
                "ProductAssembly requires an InitialCharterResult without "
                "execution-integrity failure"
            )
        if any(
            result.status in _INITIAL_CHARTER_INTEGRITY_FAILURES
            for result in initial_result.check_results
        ):
            raise AssemblyInvariantError(
                "ProductAssembly cannot consume an InitialCharterResult with "
                "check-result integrity failure"
            )

        adapter_result = initial_result.adapter_result
        pathway = adapter_result.product_pathway
        intake_bundle = adapter_result.intake_bundle
        evaluation_run = adapter_result.evaluation_run
        if evaluation_run is not intake_bundle.evaluation_run:
            raise AssemblyInvariantError(
                "ProductAdapterResult must preserve the ProductIntakeBundle "
                "EvaluationRun reference"
            )

        token_id = pathway.identity_token.token_id
        if (
            initial_result.identity_token.token_id != token_id
            or intake_bundle.identity_token.token_id != token_id
            or evaluation_run.identity_token_id != token_id
        ):
            raise AssemblyInvariantError(
                "ProductAssembly inputs must share the ProductPathway IdentityToken"
            )

        evaluation_run_id = pathway.evaluation_run_id
        if (
            initial_result.evaluation_run_id != evaluation_run_id
            or evaluation_run.evaluation_run_id != evaluation_run_id
            or intake_bundle.evaluation_run.evaluation_run_id != evaluation_run_id
        ):
            raise AssemblyInvariantError(
                "ProductAssembly inputs must share the ProductPathway EvaluationRun"
            )
