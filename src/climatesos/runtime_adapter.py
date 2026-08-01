# Climate State transition model OS
# Github Project Code: https://github.com/hsbay/ClimateSOS, CC-BY 4.0 2026 @safiume

"""Provisional services connecting pathway analysis to the ClimateSOS runtime.

These contracts remain intentionally minimal while the synchronization,
binding, and evaluation boundaries are refined.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from .models import (
    Context,
    Deployment,
    ProductPathway,
    ProductQueueBundle,
    RuntimeEvaluationResult,
    ScenarioState,
    SynchronizationComparison,
)


@runtime_checkable
class RuntimePort(Protocol):
    """Port through which downstream services invoke a ClimateSOS runtime.

    Implementations may wrap the current in-process runtime or a future remote,
    distributed, or versioned runtime. Runtime-facing services should depend
    on this protocol rather than on a particular runtime implementation.
    """

    def evaluate(self, scenario: ScenarioState) -> RuntimeEvaluationResult:
        """Evaluate a runtime-ready scenario."""
        ...


class SynchronizationEngine:
    """Synchronize a product queue bundle with its operating context.

    Synchronization analyzes how a product queue bundle relates to contextual,
    deployment, sequencing, and timing constraints.

    This initial service contains no synchronization policy. Its contract will
    be refined through the first implemented vertical slice.
    """

    def synchronize(
        self,
        bundle: ProductQueueBundle,
        context: Context,
        deployment: Deployment,
    ) -> SynchronizationComparison:
        """Return synchronization findings for a product queue bundle."""
        raise NotImplementedError


class BindingHandler:
    """Bind a synchronized product queue bundle to runtime state.

    Binding converts adapter-level queue relationships into a representation
    accepted by the ClimateSOS runtime. It must preserve unresolved bindings
    rather than silently inventing runtime assumptions.
    """

    def bind(
        self,
        bundle: ProductQueueBundle,
        base_state: ScenarioState,
    ) -> ScenarioState:
        """Bind an adapter queue bundle into a runtime scenario."""
        raise NotImplementedError


class ResultEvaluator:
    """Interpret runtime output in relation to the submitted pathway.

    The runtime remains authoritative for runtime evaluation. This service
    associates runtime output with the pathway and its provenance and will
    later construct the adapter-level evaluation result models.
    """

    def evaluate(
        self,
        pathway: ProductPathway,
        bundle: ProductQueueBundle,
        runtime_result: RuntimeEvaluationResult,
    ) -> RuntimeEvaluationResult:
        """Return the interpreted result for the current foundation stage."""
        raise NotImplementedError
