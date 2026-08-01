# Climate State transition model OS
# Github Project Code: https://github.com/hsbay/ClimateSOS, CC-BY 4.0 2026 @safiume

"""
Immutable domain models for the ClimateSOS runtime and Product Pathway Adapter.

This module contains the existing ClimateSOS v0.7 toy-runtime models and the
shared data contracts passed between the Product Pathway Adapter,
synchronization services, runtime, binding logic, and result evaluation.

Behavior belongs in service modules such as ``evaluator.py`` and
``product_adapter.py``.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum

from .states import (
    FabricStatus,
    GuardrailResolution,
    QueueStatus,
    RemedyBusStatus,
    RemedyEligibility,
    ResultingState,
)


@dataclass(frozen=True)
class Queue:
    """A throughput, latency, or capacity constraint."""

    name: str
    status: QueueStatus = QueueStatus.CLEAR
    capacity: float | None = None
    demand: float | None = None
    latency_years: float | None = None
    ttl_years: float | None = None

    @property
    def is_nonblocking(self) -> bool:
        """Return true when the queue does not block token evaluation.

        A constrained queue is not fully clear, but it is nonblocking in the
        bounded v0.7 data-center tests. Later runtimes may attach warnings,
        pressure, or BoundaryStress to constrained queues.
        """

        return self.status in {QueueStatus.CLEAR, QueueStatus.CONSTRAINED}

    @property
    def is_blocking(self) -> bool:
        return self.status in {
            QueueStatus.BLOCKED,
            QueueStatus.SEVERELY_BLOCKED,
            QueueStatus.EXPIRED,
            QueueStatus.CLOSED,
        }

    @property
    def clearance_ratio(self) -> float | None:
        if self.capacity is None or self.demand is None:
            return None
        if self.demand <= 0:
            return 1.0
        return min(1.0, self.capacity / self.demand)


@dataclass(frozen=True)
class Fabric:
    """A coordination surface grouping queues."""

    name: str
    status: FabricStatus = FabricStatus.READY
    queues: tuple[str, ...] = ()
    notes: str = ""

    @property
    def is_ready(self) -> bool:
        return self.status == FabricStatus.READY

    @property
    def is_blocking(self) -> bool:
        return self.status in {FabricStatus.UNREADY, FabricStatus.CLOSED}


@dataclass(frozen=True)
class RemedyBus:
    """Special-purpose corrective pathway for evidence, repair, and re-evaluation."""

    status: RemedyBusStatus = RemedyBusStatus.NOT_APPLICABLE
    conditions_verified: bool = False
    notes: str = ""

    @property
    def accepted(self) -> bool:
        return self.status in {
            RemedyBusStatus.REMEDY_ACCEPTED,
            RemedyBusStatus.REMEDY_CONDITIONED,
            RemedyBusStatus.RE_EVALUATION_EVENT,
        }


@dataclass(frozen=True)
class IdentityToken:
    """State-bearing object evaluated by the runtime."""

    name: str
    created_year: int
    ttl_years: int
    required_queues: tuple[str, ...]
    required_fabrics: tuple[str, ...] = ()
    guardrail_resolution: GuardrailResolution = GuardrailResolution.PASS
    remedy_eligibility: RemedyEligibility = RemedyEligibility.NOT_NEEDED
    resulting_state: ResultingState | None = None
    history: tuple[str, ...] = ()
    notes: str = ""


@dataclass(frozen=True)
class ScenarioState:
    """Minimal scenario container for v0.7 data-center tests."""

    current_year: int
    queues: dict[str, Queue]
    fabrics: dict[str, Fabric] = field(default_factory=dict)
    fossil_fallback_available: bool = False
    remedy_bus: RemedyBus = field(default_factory=RemedyBus)


@dataclass(frozen=True)
class RuntimeEvaluationResult:
    """Structured result emitted by the v0.7 evaluator."""

    resulting_state: ResultingState
    guardrail_resolution: GuardrailResolution
    validity: bool
    bottlenecks: tuple[str, ...]
    closed_queues: tuple[str, ...]
    remedy_bus_status: RemedyBusStatus
    explanation_trace: tuple[str, ...]

    def as_dict(self) -> dict[str, object]:
        return {
            "resulting_state": self.resulting_state.value,
            "guardrail_resolution": self.guardrail_resolution.value,
            "validity": self.validity,
            "bottlenecks": list(self.bottlenecks),
            "closed_queues": list(self.closed_queues),
            "remedy_bus_status": self.remedy_bus_status.value,
            "explanation_trace": list(self.explanation_trace),
        }

# =====================================================================
# Product Pathway Adapter models
# =====================================================================

@dataclass(frozen=True, slots=True)
class Context:
    """
    Evaluation context associated with a product pathway.

    Context records the circumstances in which a pathway is being inspected,
    including its invocation mode and declared system boundary.

    More detailed objects such as SystemBoundary, StressTest, and
    PathwayComparison may replace or extend the provisional fields below as
    those contracts are implemented.
    """

    # ------------------------------------------------------------------
    # Identity
    # ------------------------------------------------------------------

    user_id: str
    pathway_id: str

    # ------------------------------------------------------------------
    # Domain data
    # ------------------------------------------------------------------

    invocation_mode: str = "evaluation"
    system_boundary: str | None = None
    synchronization_window: str | None = None

    # ------------------------------------------------------------------
    # Provenance
    # ------------------------------------------------------------------

    source_ids: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class Deployment:
    """
    Declared deployment setting for a product pathway.

    Deployment describes where, when, and under what operating circumstances
    a pathway is proposed to exist. It is intentionally open-ended and is not
    represented by a closed deployment enum.
    """

    # ------------------------------------------------------------------
    # Identity
    # ------------------------------------------------------------------

    user_id: str
    pathway_id: str
    deployment_id: str

    # ------------------------------------------------------------------
    # Domain data
    # ------------------------------------------------------------------

    name: str
    geography: str | None = None
    jurisdiction: str | None = None
    operating_scope: str | None = None
    evaluation_start: str | None = None
    evaluation_end: str | None = None

    # ------------------------------------------------------------------
    # Provenance
    # ------------------------------------------------------------------

    source_ids: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class ProductPathway:
    """
    Canonical immutable representation of a proposed intervention.

    ProductPathway is the runtime-compatible representation emitted by the
    ProductAdapter after translating an externally described product,
    portfolio, pathway, comparison, or stress-test proposal.

    It describes participants, protocols, proposed operators, dependencies,
    evidence, and claimed state changes. It does not determine whether those
    claims are valid.
    """

    # ------------------------------------------------------------------
    # Identity
    # ------------------------------------------------------------------

    user_id: str
    pathway_id: str

    # ------------------------------------------------------------------
    # Domain data
    # ------------------------------------------------------------------

    name: str
    description: str

    context: Context
    deployments: tuple[Deployment, ...] = ()

    nodes: tuple[PathwayNode, ...] = ()
    edges: tuple[PathwayEdge, ...] = ()

    participants: tuple[str, ...] = ()
    protocols: tuple[str, ...] = ()
    proposed_operators: tuple[str, ...] = ()
    dependencies: tuple[str, ...] = ()

    claimed_product_outputs: tuple[str, ...] = ()
    claimed_system_contributions: tuple[str, ...] = ()

    unresolved_requirements: tuple[str, ...] = ()

    # ------------------------------------------------------------------
    # Provenance
    # ------------------------------------------------------------------

    source_text: str | None = None
    source_ids: tuple[str, ...] = ()
    evidence_ids: tuple[str, ...] = ()


class ProductQueueDirection(StrEnum):
    """Direction of a queue relative to its product pathway."""

    INPUT = "input"
    OUTPUT = "output"


@dataclass(frozen=True, slots=True)
class PathwayNode:
    """One component in a normalized product-pathway graph."""

    id: str
    name: str
    kind: str
    description: str = ""
    queue_direction: ProductQueueDirection | None = None
    source_ids: tuple[str, ...] = ()
    evidence_ids: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class PathwayEdge:
    """A directed relationship between two product-pathway nodes."""

    source_node_id: str
    target_node_id: str
    relationship: str
    description: str = ""
    source_ids: tuple[str, ...] = ()
    evidence_ids: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class ProductQueue:
    """A queue derived from a ProductPathway that originated from a customer's
    product question.

    QueueBundler creates ProductQueue instances by projecting queue-labelled
    nodes from a ProductPathway into its queue representation.

    Direction describes whether the queue supplies an input required by the
    product pathway or carries an output produced by it.
    """

    id: str
    name: str
    direction: ProductQueueDirection

    source_ids: tuple[str, ...] = ()
    evidence_ids: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class ProductQueueBundle:
    """Collection of queues derived from one product pathway.

    The bundle keeps all queues created for a ProductPathway together so they
    can be synchronized, bound, compared, and evaluated as one product
    interface.

    Queue direction is defined by each ProductQueue. The bundle does not assign
    or alter queue direction.
    """

    product_pathway_id: str
    queues: tuple[ProductQueue, ...] = ()

    source_ids: tuple[str, ...] = ()
    evidence_ids: tuple[str, ...] = ()

    @property
    def input_queues(self) -> tuple[ProductQueue, ...]:
        """Return queues interpreted as product inputs."""
        return tuple(
            queue
            for queue in self.queues
            if queue.direction is ProductQueueDirection.INPUT
        )

    @property
    def output_queues(self) -> tuple[ProductQueue, ...]:
        """Return queues interpreted as product outputs."""
        return tuple(
            queue
            for queue in self.queues
            if queue.direction is ProductQueueDirection.OUTPUT
        )


@dataclass(frozen=True, slots=True)
class SynchronizationComparison:
    """Immutable findings produced by product-pathway synchronization.

    The comparison preserves the exact product queue bundle evaluated by the
    synchronization process together with its findings and unresolved
    requirements. It does not resolve a bound state or construct the final
    evaluation result.
    """

    product_pathway_id: str
    queue_bundle: ProductQueueBundle

    findings: tuple[str, ...] = ()
    unresolved_requirements: tuple[str, ...] = ()

    source_ids: tuple[str, ...] = ()
    evidence_ids: tuple[str, ...] = ()
