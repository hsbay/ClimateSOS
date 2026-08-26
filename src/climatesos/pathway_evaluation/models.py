"""Immutable records for the specified product-pathway foundation.

Records carry references and neutral findings. Evaluation logic belongs to the
work-performing interfaces, not to these data objects.
"""

from dataclasses import dataclass
from typing import Literal, TypeAlias

from .enums import (
    EvaluationExecutionStatus,
    QueueCategory,
    QueueEvaluationState,
    QueueLifecycleState,
    QueueOperationalStatus,
    QueueOrderingStatus,
    QueueSynchronizationStatus,
)

Scalar: TypeAlias = str | int | float | bool | None


@dataclass(frozen=True, slots=True)
class Attribute:
    """An immutable named value for fields whose schema is not specified."""

    name: str
    value: Scalar


@dataclass(frozen=True, slots=True)
class SourceReference:
    """Stable reference to preserved intake source material."""

    reference_id: str
    locator: str | None = None


@dataclass(frozen=True, slots=True)
class OpaqueReference:
    """Identity-only reference to a resource whose schema is not specified."""

    reference_id: str



@dataclass(frozen=True, slots=True)
class IdentityToken:
    """Canonical identity issued upstream by the Identity Layer."""

    user_id: str
    pathway_id: str


@dataclass(frozen=True, slots=True)
class IntakeArtifact:
    """One immutable submitted artifact preserved by the Intake Layer."""

    artifact_id: str
    media_type: str
    content: str | bytes
    provenance: tuple[SourceReference, ...] = ()


@dataclass(frozen=True, slots=True)
class ProductIntakeBundle:
    """Immutable association of an identity with submitted pathway material."""

    identity_token: IdentityToken
    materials: tuple[IntakeArtifact, ...]
    metadata: tuple[Attribute, ...] = ()
    documentation: tuple[SourceReference, ...] = ()
    evidence: tuple[SourceReference, ...] = ()
    provenance: tuple[SourceReference, ...] = ()


@dataclass(frozen=True, slots=True)
class PathwayObject:
    """An attributable atomic object in a normalized pathway graph."""

    object_id: str
    object_type: str
    user_id: str
    pathway_id: str
    attributes: tuple[Attribute, ...] = ()
    source_references: tuple[SourceReference, ...] = ()
    evidence_references: tuple[SourceReference, ...] = ()


@dataclass(frozen=True, slots=True)
class PathwayRelationship:
    """An attributable directed relationship between pathway objects."""

    relationship_id: str
    relationship_type: str
    source_object_id: str
    target_object_id: str
    user_id: str
    pathway_id: str
    attributes: tuple[Attribute, ...] = ()
    source_references: tuple[SourceReference, ...] = ()


@dataclass(frozen=True, slots=True)
class QueueElement:
    """A queue function identified in, and owned by, a ProductPathway."""

    pathway_object: PathwayObject
    category: QueueCategory


@dataclass(frozen=True, slots=True)
class ProductPathway:
    """Normalized immutable map or graph created by ProductAdapter."""

    identity_token: IdentityToken
    pathway_type: str
    time_window: str | None
    geographic_scope: str | None
    system_scope: str | None
    objects: tuple[PathwayObject, ...]
    relationships: tuple[PathwayRelationship, ...]
    queue_elements: tuple[QueueElement, ...] = ()
    assumptions: tuple[str, ...] = ()
    uncertainties: tuple[str, ...] = ()
    documentation_references: tuple[SourceReference, ...] = ()
    evidence_references: tuple[SourceReference, ...] = ()


@dataclass(frozen=True, slots=True)
class ProductAdapterResult:
    """Adapter output retaining the pathway-to-intake association."""

    product_pathway: ProductPathway
    intake_bundle: ProductIntakeBundle


@dataclass(frozen=True, slots=True)
class CharterCheckResult:
    """One executed Charter check.

    The separate Charter flow owns the complete status vocabulary, so status is
    intentionally not narrowed to an invented enum here.
    """

    check_id: str
    status: str
    findings: tuple[str, ...] = ()
    supporting_evaluation_findings: tuple[OpaqueReference, ...] = ()
    supporting_system_findings: tuple[OpaqueReference, ...] = ()
    evidence_references: tuple[SourceReference, ...] = ()
    provenance: tuple[SourceReference, ...] = ()
    execution_error: str | None = None


@dataclass(frozen=True, slots=True)
class CharterEvaluationContext:
    """Versioned resources required to run a Charter pass."""

    foundational_charter: OpaqueReference
    applicable_check_definitions: tuple[OpaqueReference, ...]
    evaluator_version: str
    rule_set_version: str
    required_check_ids: tuple[str, ...]
    runtime_configuration: tuple[Attribute, ...] = ()


@dataclass(frozen=True, slots=True)
class InitialCharterResult:
    """Complete immutable result of the initial Charter pass."""

    adapter_result: ProductAdapterResult
    check_results: tuple[CharterCheckResult, ...]
    evaluator_version: str
    rule_set_version: str
    status: str
    execution_error: str | None = None


@dataclass(frozen=True, slots=True)
class ProductQueueBundle:
    """Related pathway-owned queue elements grouped without evaluation state."""

    bundle_id: str
    product_pathway: ProductPathway
    queue_elements: tuple[QueueElement, ...]
    relationships: tuple[PathwayRelationship, ...] = ()
    assembly_metadata: tuple[Attribute, ...] = ()


@dataclass(frozen=True, slots=True)
class ProductFabric:
    """Immutable coordination surface referencing queue bundles."""

    fabric_id: str
    coordination_function: str
    product_pathway: ProductPathway
    queue_bundles: tuple[ProductQueueBundle, ...]
    relationships: tuple[PathwayRelationship, ...] = ()
    assembly_metadata: tuple[Attribute, ...] = ()


@dataclass(frozen=True, slots=True)
class TransitionPathway:
    """Immutable authoritative reference snapshot used during evaluation."""

    reference_id: str
    provenance: tuple[SourceReference, ...] = ()


QueueSubject: TypeAlias = QueueElement | ProductQueueBundle


@dataclass(frozen=True, slots=True)
class QueueProgressRecord:
    """One material queue condition in an evaluation run."""

    evaluated_queue: QueueSubject
    evaluation_run_id: str
    operational_status: QueueOperationalStatus
    lifecycle_state: QueueLifecycleState
    ordering_status: QueueOrderingStatus | None
    synchronization_status: QueueSynchronizationStatus | None
    evaluation_position: int
    user_id: str
    pathway_id: str
    conditions: tuple[Attribute, ...] = ()
    change_basis: tuple[SourceReference, ...] = ()


@dataclass(frozen=True, slots=True)
class QueueExecutionResult:
    """Exactly one immutable execution completion record per queue and run."""

    evaluated_queue: QueueSubject
    evaluation_run_id: str
    execution_state: str
    progress_records: tuple[QueueProgressRecord, ...]
    user_id: str
    pathway_id: str
    material_work: tuple[str, ...] = ()
    execution_information: tuple[Attribute, ...] = ()
    evidence_references: tuple[SourceReference, ...] = ()
    transition_pathway: TransitionPathway | None = None
    system_context: OpaqueReference | None = None


@dataclass(frozen=True, slots=True)
class QueueEvaluatorResult:
    """The evaluator's final immutable conclusion for one queue and run."""

    evaluated_queue: QueueSubject
    evaluation_run_id: str
    final_operational_status: QueueOperationalStatus
    final_lifecycle_state: QueueLifecycleState
    ordering_status: QueueOrderingStatus | None
    synchronization_status: QueueSynchronizationStatus | None
    evaluation_state: QueueEvaluationState | None
    execution_result: QueueExecutionResult
    progress_records: tuple[QueueProgressRecord, ...]
    transition_pathway: TransitionPathway
    evaluator_version: str
    rule_set_version: str
    user_id: str
    pathway_id: str
    findings: tuple[str, ...] = ()
    assumptions: tuple[str, ...] = ()
    uncertainties: tuple[str, ...] = ()
    evidence_references: tuple[SourceReference, ...] = ()
    temporal_context: tuple[Attribute, ...] = ()


@dataclass(frozen=True, slots=True)
class QueueEvaluationFailure:
    """Record that a required queue-evaluation attempt did not complete."""

    evaluated_queue: QueueSubject
    evaluation_run_id: str
    user_id: str
    pathway_id: str
    execution_status: Literal[EvaluationExecutionStatus.EVALUATION_FAILED] = (
        EvaluationExecutionStatus.EVALUATION_FAILED
    )


@dataclass(frozen=True, slots=True)
class ComparisonFinding:
    """Traceable direct, substitution/combination, or propagation finding."""

    finding_id: str
    finding_type: str
    description: str
    pathway_object_references: tuple[OpaqueReference, ...] = ()
    pathway_relationship_references: tuple[OpaqueReference, ...] = ()
    transition_object_references: tuple[OpaqueReference, ...] = ()
    transition_relationship_references: tuple[OpaqueReference, ...] = ()
    system_model_basis: tuple[OpaqueReference, ...] = ()
    evidence_references: tuple[SourceReference, ...] = ()


@dataclass(frozen=True, slots=True)
class DocumentationFinding:
    """Neutral evidence finding produced by DocumentationEvaluator."""

    finding_id: str
    subject_id: str
    status: str
    description: str
    evidence_references: tuple[SourceReference, ...] = ()


@dataclass(frozen=True, slots=True)
class FabricEvaluatorResult:
    """Immutable coordination result for one ProductFabric."""

    product_fabric: ProductFabric
    queue_results: tuple[QueueEvaluatorResult, ...]
    pathway_comparison_findings: tuple[ComparisonFinding, ...]
    downstream_propagation_findings: tuple[ComparisonFinding, ...]
    transition_pathway: TransitionPathway
    coordination_condition: str
    evaluator_version: str
    rule_set_version: str
    evaluation_run_id: str
    user_id: str
    pathway_id: str
    findings: tuple[str, ...] = ()
    assumptions: tuple[str, ...] = ()
    uncertainties: tuple[str, ...] = ()
    evidence_references: tuple[SourceReference, ...] = ()


@dataclass(frozen=True, slots=True)
class PathwayEngineResult:
    """Consolidated result through the specified pathway-engine boundary."""

    product_pathway: ProductPathway
    transition_pathway: TransitionPathway
    initial_charter_result: InitialCharterResult
    direct_comparison_findings: tuple[ComparisonFinding, ...]
    substitution_combination_findings: tuple[ComparisonFinding, ...]
    downstream_propagation_findings: tuple[ComparisonFinding, ...]
    queue_results: tuple[QueueEvaluatorResult, ...]
    fabric_results: tuple[FabricEvaluatorResult, ...]
    documentation_findings: tuple[DocumentationFinding, ...]
    evaluator_versions: tuple[Attribute, ...]
    rule_set_versions: tuple[Attribute, ...]
    user_id: str
    pathway_id: str
    assumptions: tuple[str, ...] = ()
    uncertainties: tuple[str, ...] = ()
    unresolved_conditions: tuple[str, ...] = ()
    evidence_references: tuple[SourceReference, ...] = ()
    provenance: tuple[SourceReference, ...] = ()


@dataclass(frozen=True, slots=True)
class IntegratedCharterResult:
    """Complete immutable Charter pass over a PathwayEngineResult."""

    pathway_engine_result: PathwayEngineResult
    initial_charter_result: InitialCharterResult
    check_results: tuple[CharterCheckResult, ...]
    evaluator_version: str
    rule_set_version: str
    status: str
    execution_error: str | None = None
