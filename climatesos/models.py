# Climate State transition model OS
# Github Project Code: https://github.com/hsbay/ClimateSOS, CC-BY 4.0 2026 @safiume

"""Data models for the ClimateSOS v0.7 toy evaluator."""

from dataclasses import dataclass, field

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
    def is_clear(self) -> bool:
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
class EvaluationResult:
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
