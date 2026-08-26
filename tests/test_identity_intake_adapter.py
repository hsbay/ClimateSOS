"""Focused checks for the Identity -> Intake -> ProductAdapter boundary."""

import pytest

from climatesos.pathway_evaluation import (
    AdapterInvariantError,
    Attribute,
    IdentityLayer,
    IdentityToken,
    IntakeArtifact,
    IntakeLayer,
    PathwayObject,
    PathwayRelationship,
    ProductIntakeBundle,
    ProductPathway,
    SourceReference,
    ValidatedProductAdapter,
)


def _bundle() -> ProductIntakeBundle:
    issued_token = IdentityToken(user_id="user-1", pathway_id="pathway-1")
    token = IdentityLayer(lambda: issued_token).issue()
    source = SourceReference(reference_id="source-1", locator="submission.txt")
    artifact = IntakeArtifact(
        artifact_id="artifact-1",
        media_type="text/plain",
        content="customer-supplied material",
        provenance=(source,),
    )
    return IntakeLayer().bundle(
        identity_token=token,
        materials=(artifact,),
        metadata=(Attribute(name="submitted_by", value="customer"),),
        documentation=(source,),
        evidence=(source,),
        provenance=(source,),
    )


def _pathway(bundle: ProductIntakeBundle) -> ProductPathway:
    token = bundle.identity_token
    first = PathwayObject(
        object_id="object-1",
        object_type="declared_input",
        user_id=token.user_id,
        pathway_id=token.pathway_id,
    )
    second = PathwayObject(
        object_id="object-2",
        object_type="declared_output",
        user_id=token.user_id,
        pathway_id=token.pathway_id,
    )
    relationship = PathwayRelationship(
        relationship_id="relationship-1",
        relationship_type="produces",
        source_object_id=first.object_id,
        target_object_id=second.object_id,
        user_id=token.user_id,
        pathway_id=token.pathway_id,
    )
    return ProductPathway(
        identity_token=token,
        pathway_type="customer-declared",
        time_window=None,
        geographic_scope=None,
        system_scope=None,
        objects=(first, second),
        relationships=(relationship,),
    )


def test_flow_preserves_canonical_objects() -> None:
    bundle = _bundle()
    seen_bundles: list[ProductIntakeBundle] = []

    def normalize(received: ProductIntakeBundle) -> ProductPathway:
        seen_bundles.append(received)
        return _pathway(received)

    result = ValidatedProductAdapter(normalize).adapt(bundle)

    assert seen_bundles[0] is bundle
    assert result.intake_bundle is bundle
    assert result.product_pathway.identity_token is bundle.identity_token
    assert result.intake_bundle.materials[0] is bundle.materials[0]


def test_intake_preserves_supplied_immutable_contents_and_references() -> None:
    bundle = _bundle()
    rebuilt = IntakeLayer().bundle(
        identity_token=bundle.identity_token,
        materials=bundle.materials,
        metadata=bundle.metadata,
        documentation=bundle.documentation,
        evidence=bundle.evidence,
        provenance=bundle.provenance,
    )

    assert rebuilt.identity_token is bundle.identity_token
    assert rebuilt.materials == bundle.materials
    assert rebuilt.materials[0] is bundle.materials[0]
    assert rebuilt.metadata == bundle.metadata
    assert rebuilt.metadata[0] is bundle.metadata[0]
    assert rebuilt.documentation == bundle.documentation
    assert rebuilt.documentation[0] is bundle.documentation[0]
    assert rebuilt.evidence == bundle.evidence
    assert rebuilt.evidence[0] is bundle.evidence[0]
    assert rebuilt.provenance == bundle.provenance
    assert rebuilt.provenance[0] is bundle.provenance[0]


def test_adapter_rejects_replaced_identity_token() -> None:
    bundle = _bundle()

    def replace_token(received: ProductIntakeBundle) -> ProductPathway:
        pathway = _pathway(received)
        replacement = IdentityLayer(
            lambda: IdentityToken(
                user_id=received.identity_token.user_id,
                pathway_id=received.identity_token.pathway_id,
            )
        )
        replacement_token = replacement.issue()
        return ProductPathway(
            identity_token=replacement_token,
            pathway_type=pathway.pathway_type,
            time_window=None,
            geographic_scope=None,
            system_scope=None,
            objects=pathway.objects,
            relationships=pathway.relationships,
        )

    with pytest.raises(AdapterInvariantError, match="preserve"):
        ValidatedProductAdapter(replace_token).adapt(bundle)


def test_adapter_rejects_cross_pathway_attribution() -> None:
    bundle = _bundle()
    pathway = _pathway(bundle)
    wrong_object = PathwayObject(
        object_id="object-3",
        object_type="claim",
        user_id=bundle.identity_token.user_id,
        pathway_id="different-pathway",
    )

    def normalize(_: ProductIntakeBundle) -> ProductPathway:
        return ProductPathway(
            identity_token=pathway.identity_token,
            pathway_type=pathway.pathway_type,
            time_window=None,
            geographic_scope=None,
            system_scope=None,
            objects=(*pathway.objects, wrong_object),
            relationships=pathway.relationships,
        )

    with pytest.raises(AdapterInvariantError, match="PathwayObject"):
        ValidatedProductAdapter(normalize).adapt(bundle)


@pytest.mark.parametrize("failure", ["duplicate-object", "dangling-relationship"])
def test_adapter_rejects_invalid_graph_structure(failure: str) -> None:
    bundle = _bundle()
    pathway = _pathway(bundle)

    def normalize(_: ProductIntakeBundle) -> ProductPathway:
        objects: tuple[PathwayObject, ...]
        relationships: tuple[PathwayRelationship, ...]
        if failure == "duplicate-object":
            objects = (pathway.objects[0], pathway.objects[0])
            relationships = ()
        else:
            objects = pathway.objects
            relationships = (
                PathwayRelationship(
                    relationship_id="relationship-2",
                    relationship_type="depends_on",
                    source_object_id=objects[0].object_id,
                    target_object_id="missing-object",
                    user_id=bundle.identity_token.user_id,
                    pathway_id=bundle.identity_token.pathway_id,
                ),
            )
        return ProductPathway(
            identity_token=pathway.identity_token,
            pathway_type=pathway.pathway_type,
            time_window=None,
            geographic_scope=None,
            system_scope=None,
            objects=objects,
            relationships=relationships,
        )

    with pytest.raises(AdapterInvariantError):
        ValidatedProductAdapter(normalize).adapt(bundle)


def test_adapter_exposes_no_downstream_execution_behavior() -> None:
    adapter = ValidatedProductAdapter(_pathway)

    assert not hasattr(adapter, "assemble")
    assert not hasattr(adapter, "bundle")
    assert not hasattr(adapter, "evaluate")
