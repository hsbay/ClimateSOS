"""Invariants that do not require unspecified evaluation behavior."""

from dataclasses import FrozenInstanceError, fields

import pytest

from climatesos.pathway_evaluation import (
    CharterCheckResult,
    CharterEvaluationContext,
    ComparisonFinding,
    EvaluationExecutionStatus,
    FabricEvaluatorResult,
    IdentityToken,
    IntakeArtifact,
    OpaqueReference,
    PathwayObject,
    ProductAdapterResult,
    ProductIntakeBundle,
    ProductPathway,
    QueueEvaluationFailure,
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


def test_queue_execution_can_preserve_required_evaluation_context() -> None:
    field_names = {field.name for field in fields(QueueExecutionResult)}

    assert "transition_pathway" in field_names
    assert "system_context" in field_names


def test_fabric_result_preserves_consumed_evaluation_context() -> None:
    field_names = {field.name for field in fields(FabricEvaluatorResult)}

    assert {
        "pathway_comparison_findings",
        "downstream_propagation_findings",
        "transition_pathway",
    } <= field_names

def test_charter_context_preserves_opaque_resources_and_required_ids() -> None:
    field_names = {field.name for field in fields(CharterEvaluationContext)}

    assert {
        "foundational_charter",
        "applicable_check_definitions",
        "required_check_ids",
        "evaluator_version",
        "rule_set_version",
        "runtime_configuration",
    } <= field_names
    assert fields(CharterEvaluationContext)[0].type is OpaqueReference


def test_charter_check_preserves_structural_finding_references() -> None:
    field_names = {field.name for field in fields(CharterCheckResult)}

    assert "supporting_evaluation_findings" in field_names
    assert "supporting_system_findings" in field_names


def test_comparison_finding_preserves_required_traceability() -> None:
    field_names = {field.name for field in fields(ComparisonFinding)}

    assert {
        "pathway_object_references",
        "pathway_relationship_references",
        "transition_object_references",
        "transition_relationship_references",
        "system_model_basis",
    } <= field_names


def test_queue_evaluation_failure_is_not_a_completed_result() -> None:
    completed_fields = {field.name for field in fields(QueueEvaluatorResult)}
    failure_fields = {field.name for field in fields(QueueEvaluationFailure)}
    failure_status = next(
        field for field in fields(QueueEvaluationFailure)
        if field.name == "execution_status"
    )

    assert "execution_status" not in completed_fields
    assert "execution_result" in completed_fields
    assert "execution_status" in failure_fields
    assert "execution_result" not in failure_fields
    assert "final_operational_status" not in failure_fields
    assert failure_status.default is EvaluationExecutionStatus.EVALUATION_FAILED
