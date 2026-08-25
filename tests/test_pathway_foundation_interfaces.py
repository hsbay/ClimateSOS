"""Checks for data/component separation in the new foundation."""

from dataclasses import is_dataclass
from inspect import signature
from typing import get_type_hints

from climatesos.pathway_evaluation import (
    CharterEvaluator,
    FabricEvaluator,
    PathwayEngineResult,
    PathwayEvaluationEngine,
    ProductAdapter,
    ProductPathway,
)


def test_models_are_data_records_without_work_performing_methods() -> None:
    assert is_dataclass(ProductPathway)
    assert is_dataclass(PathwayEngineResult)
    assert not hasattr(ProductPathway, "evaluate")
    assert not hasattr(PathwayEngineResult, "evaluate")


def test_work_performing_protocols_expose_only_specified_boundaries() -> None:
    assert callable(ProductAdapter.adapt)
    assert callable(CharterEvaluator.evaluate_initial)
    assert callable(CharterEvaluator.evaluate_integrated)
    assert callable(PathwayEvaluationEngine.evaluate)

    adapter_hints = get_type_hints(ProductAdapter.adapt)
    assert adapter_hints["return"].__name__ == "ProductAdapterResult"


def test_fabric_evaluator_receives_required_pathway_findings() -> None:
    parameter_names = signature(FabricEvaluator.evaluate).parameters

    assert "pathway_comparison_findings" in parameter_names
    assert "downstream_propagation_findings" in parameter_names
