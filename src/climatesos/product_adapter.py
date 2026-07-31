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
    """Coordinate translation between product pathways and the runtime.

    ProductAdapter is an orchestration boundary, not a second runtime. It
    delegates synchronization, binding, runtime execution, and result
    interpretation to their respective services.
    """

    def __init__(
        self,
        *,
        synchronization_engine: SynchronizationEngine,
        binding_handler: BindingHandler,
        runtime: RuntimePort,
        result_evaluator: ResultEvaluator,
    ) -> None:
        """Create a product adapter from explicit service dependencies."""
        self._synchronization_engine = synchronization_engine
        self._binding_handler = binding_handler
        self._runtime = runtime
        self._result_evaluator = result_evaluator

    def compile(
        self,
        pathway: ProductPathway,
        context: Context,
        deployment: Deployment,
    ) -> ProductQueueBundle:
        """Compile an external pathway into a synchronized queue bundle."""
        return self._synchronization_engine.synchronize(
            pathway=pathway,
            context=context,
            deployment=deployment,
        )

    def evaluate(
        self,
        pathway: ProductPathway,
        context: Context,
        deployment: Deployment,
        base_state: ScenarioState,
    ) -> RuntimeEvaluationResult:
        """Compile, bind, and submit a product pathway for evaluation.

        The return type intentionally remains RuntimeEvaluationResult until the
        adapter-level EvaluationResult model is introduced.
        """
        bundle = self.compile(
            pathway=pathway,
            context=context,
            deployment=deployment,
        )

        scenario = self._binding_handler.bind(
            bundle=bundle,
            base_state=base_state,
        )

        runtime_result = self._runtime.evaluate(scenario)

        return self._result_evaluator.evaluate(
            pathway=pathway,
            bundle=bundle,
            runtime_result=runtime_result,
        )
