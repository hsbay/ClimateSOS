"""Runtime state enums for the ClimateSOS v0.7 toy evaluator."""

from enum import Enum


class _StrEnum(str, Enum):
    """Small compatibility helper for string-valued enums."""

    def __str__(self) -> str:
        return self.value


class ResultingState(_StrEnum):
    """v0.1/v0.7 resulting states for the bounded data-center test case."""

    CLEAN_BOUND = "CleanBound"
    MIXED_BOUND = "MixedBound"
    FOSSIL_BOUND = "FossilBound"
    NO_ACK = "NoAck"
    HARM_BOUND = "HarmBound"
    BOUNDARY_STRESS = "BoundaryStress"


class GuardrailResolution(_StrEnum):
    """Guardrail status, intentionally separate from ResultingState."""

    PASS = "Pass"
    CONDITIONAL_PASS = "ConditionalPass"
    UNRESOLVED = "Unresolved"
    INVALID = "Invalid"


class RemedyEligibility(_StrEnum):
    """Whether a non-valid pathway may enter corrective handling."""

    NOT_NEEDED = "NotNeeded"
    EVIDENCE_REQUIRED = "EvidenceRequired"
    REMEDIABLE = "Remediable"
    NOT_REMEDIABLE = "NotRemediable"


class RemedyBusStatus(_StrEnum):
    """Minimal RemedyBus statuses for v0.7 tests."""

    NOT_APPLICABLE = "NotApplicable"
    REMEDY_REQUIRED = "RemedyRequired"
    REMEDY_SUBMITTED = "RemedySubmitted"
    REMEDY_ACCEPTED = "RemedyAccepted"
    REMEDY_REJECTED = "RemedyRejected"
    REMEDY_INCOMPLETE = "RemedyIncomplete"
    REMEDY_EXPIRED = "RemedyExpired"
    REMEDY_CONDITIONED = "RemedyConditioned"
    RE_EVALUATION_EVENT = "ReEvaluationEvent"


class QueueStatus(_StrEnum):
    """Queue status values used by the toy evaluator."""

    CLEAR = "Clear"
    CONSTRAINED = "Constrained"
    BLOCKED = "Blocked"
    SEVERELY_BLOCKED = "SeverelyBlocked"
    EXPIRED = "Expired"
    CLOSED = "Closed"


class FabricStatus(_StrEnum):
    """Fabric readiness values used by the toy evaluator."""

    READY = "ready"
    PARTIAL = "partial"
    UNREADY = "unready"
    CLOSED = "closed"
