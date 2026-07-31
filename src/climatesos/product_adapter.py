# Climate State transition model OS
# Github Project Code: https://github.com/hsbay/ClimateSOS, CC-BY 4.0 2026 @safiume

"""Product pathway adapter services.

This module defines the architectural boundary between externally described
product pathways and the ClimateSOS runtime.

The adapter layer is responsible for translating, normalizing, synchronizing,
and binding pathway information into runtime-compatible objects. It does not
perform market simulation, engineering validation, protocol execution, or
other runtime evaluation itself.
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
)


@runtime_checkable
class RuntimePort(Protocol):
    """Port through which the adapter invokes a ClimateSOS runtime.

    Implementations may wrap the current in-process runtime or a future remote,
    distributed, or versioned runtime. Adapter services should depend on this
    protocol rather than on a particular runtime implementation.
    """

    def evaluate(self, scenario: ScenarioState) -> RuntimeEvaluationResult:
        """Evaluate a runtime-ready scenario."""
        ...


class SynchronizationEngine:
    """Synchronize a product pathway with its operating context.

    Synchronization identifies how pathway queues relate to contextual,
    deployment, sequencing, and timing constraints.

    This initial service contains no synchronization policy. Its contract will
    be refined through the first implemented vertical slice.
    """

    def synchronize(
        self,
        pathway: ProductPathway,
        context: Context,
        deployment: Deployment,
    ) -> ProductQueueBundle:
        """Produce a synchronized queue bundle for the pathway."""
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


class ProductAdapter:
    """Translate external product material into a ProductPathway.

    ProductAdapter is the intake translation boundary. It normalizes and
    structures externally supplied product material without creating product
    queues, synchronizing pathways, binding runtime state, or evaluating
    results.
    """

    def adapt(self, source: object) -> ProductPathway:
        """Translate one external product submission into a product pathway."""
        raise NotImplementedError
