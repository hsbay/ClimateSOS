"""Invariants that do not require unspecified evaluation behavior."""

from dataclasses import FrozenInstanceError, fields

import pytest

from climatesos.pathway_evaluation import (
    FabricEvaluatorResult,
    IdentityToken,
    IntakeArtifact,
    PathwayObject,
    ProductAdapterResult,
    ProductIntakeBundle,
    ProductPathway,
    QueueEvaluationState,
    QueueEvaluatorResult,
    QueueExecutionResult,
    SourceReference,
    TransitionPathway,
)


def _foundation_objects() -> tuple[
    IdentityToken, ProductIntakeBundle, ProductPathway, ProductAdapterResult
]:
    token = IdentityToken(user_id="user-1", pathway_id="pathway-1")
    source = SourceReference(reference_id="source-1")
    bundle = ProductIntakeBundle(
        identity_token=token,
        materials=(
            IntakeArtifact(
                artifact_id="artifact-1",
                media_type="text/plain",
                content="submitted fact",
                provenance=(source,),
            ),
        ),
        provenance=(source,),
    )
    element = PathwayObject(
        object_id="object-1",
        object_type="declared_output",
        user_id=token.user_id,
        pathway_id=token.pathway_id,
        source_references=(source,),
    )
    pathway = ProductPathway(
        identity_token=token,
        pathway_type="test",
        time_window=None,
        geographic_scope=None,
        system_scope=None,
        objects=(element,),
        relationships=(),
    )
    return token, bundle, pathway, ProductAdapterResult(pathway, bundle)


def test_adapter_result_preserves_identity_and_intake_references() -> None:
    token, bundle, pathway, result = _foundation_objects()

    assert result.intake_bundle is bundle
    assert result.product_pathway is pathway
    assert pathway.identity_token is token
    assert pathway.objects[0].user_id == token.user_id
    assert pathway.objects[0].pathway_id == token.pathway_id


def test_foundation_records_are_frozen_and_collections_are_immutable() -> None:
    token, bundle, pathway, _ = _foundation_objects()

    with pytest.raises(FrozenInstanceError):
        token.user_id = "different-user"  # type: ignore[misc]

    with pytest.raises(TypeError):
        bundle.materials[0] = bundle.materials[0]  # type: ignore[index]

    with pytest.raises(FrozenInstanceError):
        pathway.pathway_type = "different-type"  # type: ignore[misc]


def test_no_determination_is_an_explicit_queue_evaluation_state() -> None:
    field_names = {field.name for field in fields(QueueEvaluatorResult)}

    assert "evaluation_state" in field_names
    assert "determination_resolved" not in field_names
    assert QueueEvaluationState.NODETERMINATION.value == "NODETERMINATION"


def test_transition_pathway_remains_an_opaque_reference() -> None:
    field_names = {field.name for field in fields(TransitionPathway)}

    assert "objects" not in field_names
    assert "relationships" not in field_names


def test_queue_execution_does_not_duplicate_transition_context() -> None:
    field_names = {field.name for field in fields(QueueExecutionResult)}

    assert "transition_pathway" not in field_names


def test_fabric_result_preserves_consumed_evaluation_context() -> None:
    field_names = {field.name for field in fields(FabricEvaluatorResult)}

    assert {
        "pathway_comparison_findings",
        "downstream_propagation_findings",
        "transition_pathway",
    } <= field_names
