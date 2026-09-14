"""Concrete boundary for adapting intake into a normalized pathway graph."""

from collections.abc import Callable
from dataclasses import dataclass

from .models import ProductAdapterResult, ProductIntakeBundle, ProductPathway

PathwayNormalizer = Callable[[ProductIntakeBundle], ProductPathway]


class AdapterInvariantError(ValueError):
    """Raised when normalized output violates the adapter's structural contract."""


@dataclass(frozen=True, slots=True)
class ProductAdapter:
    """Adapt intake using caller-supplied translation semantics.

    The specification does not define a source-artifact schema or parsing
    rules. A normalizer therefore owns that translation, while this boundary
    enforces the identity, attribution, and graph invariants that every
    normalized pathway must satisfy.
    """

    normalizer: PathwayNormalizer

    def adapt(self, intake_bundle: ProductIntakeBundle) -> ProductAdapterResult:
        """Normalize one bundle and retain the original bundle by reference."""

        pathway = self.normalizer(intake_bundle)
        self._validate(pathway, intake_bundle)
        return ProductAdapterResult(
            product_pathway=pathway,
            intake_bundle=intake_bundle,
            evaluation_run=intake_bundle.evaluation_run,
        )

    @staticmethod
    def _validate(
        pathway: ProductPathway,
        intake_bundle: ProductIntakeBundle,
    ) -> None:
        token = intake_bundle.identity_token
        evaluation_run = intake_bundle.evaluation_run
        if pathway.identity_token.token_id != token.token_id:
            raise AdapterInvariantError(
                "ProductPathway must preserve the intake bundle's IdentityToken"
            )
        if evaluation_run.identity_token_id != token.token_id:
            raise AdapterInvariantError(
                "EvaluationRun must reference the intake lineage IdentityToken"
            )
        if pathway.evaluation_run_id != evaluation_run.evaluation_run_id:
            raise AdapterInvariantError(
                "ProductPathway evaluation_run_id must match the EvaluationRun"
            )

        object_ids: set[str] = set()
        for pathway_object in pathway.objects:
            if (
                pathway_object.user_id != pathway.user_id
                or pathway_object.pathway_id != pathway.pathway_id
            ):
                raise AdapterInvariantError(
                    "Every PathwayObject must carry the ProductPathway attribution"
                )
            if pathway_object.object_id in object_ids:
                raise AdapterInvariantError(
                    f"Duplicate pathway object identifier: {pathway_object.object_id}"
                )
            object_ids.add(pathway_object.object_id)

        relationship_ids: set[str] = set()
        for relationship in pathway.relationships:
            if (
                relationship.user_id != pathway.user_id
                or relationship.pathway_id != pathway.pathway_id
            ):
                raise AdapterInvariantError(
                    "Every PathwayRelationship must carry ProductPathway attribution"
                )
            if relationship.relationship_id in relationship_ids:
                raise AdapterInvariantError(
                    "Duplicate pathway relationship identifier: "
                    f"{relationship.relationship_id}"
                )
            relationship_ids.add(relationship.relationship_id)
            if (
                relationship.source_object_id not in object_ids
                or relationship.target_object_id not in object_ids
            ):
                raise AdapterInvariantError(
                    "Every PathwayRelationship endpoint must reference a pathway object"
                )
