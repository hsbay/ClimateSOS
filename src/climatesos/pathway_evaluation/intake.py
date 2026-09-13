"""Intake-layer construction for product-pathway evaluation."""

from .models import (
    Attribute,
    EvaluationRun,
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
        evaluation_run: EvaluationRun,
        materials: tuple[IntakeArtifact, ...],
        metadata: tuple[Attribute, ...] = (),
        documentation: tuple[SourceReference, ...] = (),
        evidence: tuple[SourceReference, ...] = (),
        provenance: tuple[SourceReference, ...] = (),
    ) -> ProductIntakeBundle:
        """Return an immutable bundle containing the supplied objects unchanged."""

        if evaluation_run.identity_token_id != identity_token.token_id:
            raise ValueError("EvaluationRun must reference the supplied IdentityToken")
        return ProductIntakeBundle(
            identity_token=identity_token,
            evaluation_run=evaluation_run,
            materials=materials,
            metadata=metadata,
            documentation=documentation,
            evidence=evidence,
            provenance=provenance,
        )
