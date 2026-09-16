"""Focused checks for the Identity -> Intake -> ProductAdapter boundary."""

from dataclasses import FrozenInstanceError, fields, replace

import pytest

from climatesos.pathway_evaluation import (
    AdapterInvariantError,
    Attribute,
    EvaluationRun,
    IdentityLayer,
    IdentityToken,
    IntakeArtifact,
    IntakeLayer,
    PathwayObject,
    PathwayRelationship,
    ProductAdapter,
    ProductIntakeBundle,
    ProductPathway,
    SourceReference,
)


def _bundle() -> ProductIntakeBundle:
    issued_token = IdentityToken("token-1")
    token, evaluation_run = IdentityLayer(
        lambda: issued_token,
        lambda resolved, predecessor, resolution: EvaluationRun(
            "run-1", resolved.token_id, predecessor, resolution
        ),
    ).resolve()
    source = SourceReference(reference_id="source-1", locator="submission.txt")
    artifact = IntakeArtifact(
        artifact_id="artifact-1",
        media_type="text/plain",
        content="customer-supplied material",
        provenance=(source,),
    )
    return IntakeLayer().bundle(
        identity_token=token,
        evaluation_run=evaluation_run,
        materials=(artifact,),
        metadata=(Attribute(name="submitted_by", value="customer"),),
        documentation=(source,),
        evidence=(source,),
        provenance=(source,),
    )


def _pathway(bundle: ProductIntakeBundle) -> ProductPathway:
    first = PathwayObject("object-1", "declared_input", "user-1", "pathway-1")
    second = PathwayObject("object-2", "declared_output", "user-1", "pathway-1")
    relationship = PathwayRelationship(
        "relationship-1",
        "produces",
        first.object_id,
        second.object_id,
        "user-1",
        "pathway-1",
    )
    return ProductPathway(
        identity_token=bundle.identity_token,
        evaluation_run_id=bundle.evaluation_run.evaluation_run_id,
        user_id="user-1",
        pathway_id="pathway-1",
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

    result = ProductAdapter(normalize).adapt(bundle)

    assert seen_bundles[0] is bundle
    assert result.intake_bundle is bundle
    assert result.evaluation_run is bundle.evaluation_run
    assert result.product_pathway.identity_token is bundle.identity_token
    assert result.product_pathway.evaluation_run_id == "run-1"
    assert result.intake_bundle.materials[0] is bundle.materials[0]


def test_intake_preserves_supplied_immutable_contents_and_references() -> None:
    bundle = _bundle()
    rebuilt = IntakeLayer().bundle(
        identity_token=bundle.identity_token,
        evaluation_run=bundle.evaluation_run,
        materials=bundle.materials,
        metadata=bundle.metadata,
        documentation=bundle.documentation,
        evidence=bundle.evidence,
        provenance=bundle.provenance,
    )

    assert rebuilt.identity_token is bundle.identity_token
    assert rebuilt.evaluation_run is bundle.evaluation_run
    assert rebuilt.materials == bundle.materials
    assert rebuilt.materials[0] is bundle.materials[0]
    assert rebuilt.metadata == bundle.metadata
    assert rebuilt.documentation == bundle.documentation
    assert rebuilt.evidence == bundle.evidence
    assert rebuilt.provenance == bundle.provenance


def test_identity_token_contains_token_id_only() -> None:
    assert [field.name for field in fields(IdentityToken)] == ["token_id"]


def test_identity_layer_reuses_lineage_for_a_new_run() -> None:
    token = IdentityToken("token-1")
    layer = IdentityLayer(
        lambda: IdentityToken("unused"),
        lambda resolved, predecessor, resolution: EvaluationRun(
            "run-2", resolved.token_id, predecessor, resolution
        ),
    )

    resolved_token, evaluation_run = layer.resolve(
        identity_token=token,
        predecessor_run_id="run-1",
        resolution_record_id="resolution-1",
    )

    assert resolved_token is token
    assert evaluation_run == EvaluationRun(
        "run-2", "token-1", "run-1", "resolution-1"
    )


def test_adapter_rejects_different_identity_token_id() -> None:
    bundle = _bundle()

    def replace_token(received: ProductIntakeBundle) -> ProductPathway:
        return replace(_pathway(received), identity_token=IdentityToken("token-2"))

    with pytest.raises(AdapterInvariantError, match="preserve"):
        ProductAdapter(replace_token).adapt(bundle)


def test_adapter_accepts_reconstructed_token_with_same_token_id() -> None:
    bundle = _bundle()
    reconstructed_token = IdentityToken(bundle.identity_token.token_id)

    result = ProductAdapter(
        lambda received: replace(
            _pathway(received), identity_token=reconstructed_token
        )
    ).adapt(bundle)

    assert reconstructed_token is not bundle.identity_token
    assert result.product_pathway.identity_token is reconstructed_token


def test_adapter_rejects_mismatched_evaluation_run_id() -> None:
    bundle = _bundle()

    with pytest.raises(AdapterInvariantError, match="evaluation_run_id"):
        ProductAdapter(
            lambda received: replace(
                _pathway(received), evaluation_run_id="different-run"
            )
        ).adapt(bundle)


@pytest.mark.parametrize("atomic_kind", ["object", "relationship"])
def test_adapter_rejects_cross_pathway_attribution(atomic_kind: str) -> None:
    bundle = _bundle()
    pathway = _pathway(bundle)
    if atomic_kind == "object":
        changed = replace(
            pathway,
            objects=(*pathway.objects, replace(pathway.objects[0], pathway_id="other")),
        )
    else:
        changed = replace(
            pathway,
            relationships=(replace(pathway.relationships[0], user_id="other"),),
        )

    with pytest.raises(AdapterInvariantError, match=f"Pathway{atomic_kind.title()}"):
        ProductAdapter(lambda _: changed).adapt(bundle)


@pytest.mark.parametrize(
    "failure", ["duplicate-object", "duplicate-relationship", "dangling-relationship"]
)
def test_adapter_rejects_invalid_graph_structure(failure: str) -> None:
    bundle = _bundle()
    pathway = _pathway(bundle)
    if failure == "duplicate-object":
        changed = replace(
            pathway,
            objects=(pathway.objects[0], pathway.objects[0]),
            relationships=(),
        )
    elif failure == "duplicate-relationship":
        changed = replace(
            pathway,
            relationships=(pathway.relationships[0], pathway.relationships[0]),
        )
    else:
        changed = replace(
            pathway,
            relationships=(
                replace(pathway.relationships[0], target_object_id="missing-object"),
            ),
        )

    with pytest.raises(AdapterInvariantError):
        ProductAdapter(lambda _: changed).adapt(bundle)


def test_evaluation_run_is_immutable() -> None:
    evaluation_run = _bundle().evaluation_run

    with pytest.raises(FrozenInstanceError):
        evaluation_run.evaluation_run_id = "different-run"  # type: ignore[misc]


def test_adapter_exposes_no_downstream_execution_behavior() -> None:
    adapter = ProductAdapter(_pathway)

    assert not hasattr(adapter, "assemble")
    assert not hasattr(adapter, "bundle")
    assert not hasattr(adapter, "evaluate")
