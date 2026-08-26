"""Intake-layer construction for product-pathway evaluation."""

from .models import (
    Attribute,
    IdentityToken,
    IntakeArtifact,
    ProductIntakeBundle,
    SourceReference,
)


class IntakeLayer:
    """Associate submitted material with its canonical identity."""

    def bundle(
        self,
        *,
        identity_token: IdentityToken,
        materials: tuple[IntakeArtifact, ...],
        metadata: tuple[Attribute, ...] = (),
        documentation: tuple[SourceReference, ...] = (),
        evidence: tuple[SourceReference, ...] = (),
        provenance: tuple[SourceReference, ...] = (),
    ) -> ProductIntakeBundle:
        """Return an immutable bundle containing the supplied objects unchanged."""

        return ProductIntakeBundle(
            identity_token=identity_token,
            materials=materials,
            metadata=metadata,
            documentation=documentation,
            evidence=evidence,
            provenance=provenance,
        )
