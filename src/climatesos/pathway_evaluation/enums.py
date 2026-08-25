"""Specified status vocabularies for product-pathway evaluation."""

from enum import StrEnum


class _StringEnum(StrEnum):
    """A JSON-friendly string-valued enum."""


class QueueCategory(_StringEnum):
    """Canonical queue functions defined by the pathway specification."""

    FEEDSTOCK_AND_INPUT_ACCESS = "feedstock_and_input_access"
    PRODUCTION_CONVERSION_AND_EXECUTION_CAPACITY = (
        "production_conversion_and_execution_capacity"
    )
    PRODUCT_OUTPUT_AND_DELIVERY_ACCESS = "product_output_and_delivery_access"
    BANKABILITY_AND_REVENUE_CERTAINTY = "bankability_and_revenue_certainty"
    PROJECT_FINANCE = "project_finance"
    NON_DILUTIVE_CAPITAL_AND_PUBLIC_SUPPORT = (
        "non_dilutive_capital_and_public_support"
    )
    PERMITTING_AND_AUTHORIZATION = "permitting_and_authorization"
    WORKFORCE_AND_EXECUTION = "workforce_and_execution"
    MRV = "mrv"
    DOCUMENTATION_AND_EVIDENCE = "documentation_and_evidence"
    FOSSIL_EXIT_FINANCE_AND_PERSISTENCE_CLOSURE = (
        "fossil_exit_finance_and_persistence_closure"
    )
    UNCLASSIFIED = "unclassified"


class QueueOperationalStatus(_StringEnum):
    """A queue's ability to perform its represented function."""

    CLEAR = "clear"
    CONSTRAINED = "constrained"
    BLOCKED = "blocked"
    DELAYED = "delayed"


class QueueLifecycleState(_StringEnum):
    """A queue's evaluated lifecycle state."""

    OPEN = "open"
    CLOSED = "closed"
    EXPIRED = "expired"
    STALE = "stale"


class QueueOrderingStatus(_StringEnum):
    """A queue's sequencing result, evaluated independently of lifecycle."""

    ORDERED = "ordered"
    MISORDERED = "misordered"
    NOT_APPLICABLE = "not_applicable"


class QueueSynchronizationStatus(_StringEnum):
    """A queue's timing-coordination result."""

    SYNCHRONIZED = "synchronized"
    UNSYNCHRONIZED = "unsynchronized"
    NOT_REQUIRED = "not_required"


class QueueEvaluationState(_StringEnum):
    """Special queue-evaluation state explicitly defined by the specification."""

    NODETERMINATION = "NODETERMINATION"


class EvaluationExecutionStatus(_StringEnum):
    """Execution integrity, separate from evaluated pathway conditions."""

    COMPLETED = "completed"
    EVALUATION_FAILED = "evaluation_failed"
