import inspect
from dataclasses import FrozenInstanceError, fields
from typing import TypeVar

import pytest

from climatesos.pathway_evaluation import (
    EvaluationTrace,
    FinalPathwayAssembly,
    FinalPathwayResult,
    IdentityToken,
    InitialCharterResult,
    IntegratedCharterResult,
    NetOverallSystemContribution,
    NetOverallSystemRiskResult,
    PathwayEngineResult,
    ProductPathway,
    ScaleDiagnosticResult,
    TransitionPathway,
)

T = TypeVar("T")


def _record(record_type: type[T], **values: object) -> T:
    record = object.__new__(record_type)
    for name, value in values.items():
        object.__setattr__(record, name, value)
    return record


def _final_result() -> tuple[
    FinalPathwayResult,
    ProductPathway,
    TransitionPathway,
    TransitionPathway,
    NetOverallSystemRiskResult,
    EvaluationTrace,
    IdentityToken,
]:
    identity_token = _record(IdentityToken, token_id="lineage-1")
    product_pathway = _record(ProductPathway)
    authoritative = TransitionPathway(
        reference_id="authoritative",
        identity_token=_record(IdentityToken, token_id="older-lineage"),
        evaluation_run_id="older-run",
    )
    candidate = TransitionPathway(
        reference_id="candidate",
        identity_token=identity_token,
        evaluation_run_id="run-1",
        user_id="user-1",
        pathway_id="pathway-1",
        authoritative_transition_pathway=authoritative,
        product_pathway=product_pathway,
        compiler_version="compiler-v1",
        model_version="transition-v1",
        rule_set_version="compiler-rules-v1",
    )
    risk_result = NetOverallSystemRiskResult(
        candidate_transition_pathway=candidate,
        authoritative_transition_pathway=authoritative,
        risk_findings=(),
        evaluation_run_id="run-1",
        user_id="user-1",
        pathway_id="pathway-1",
        evaluator_version="risk-v1",
        rule_set_version="risk-rules-v1",
    )
    trace = EvaluationTrace(
        initial_charter_result=_record(InitialCharterResult),
        pathway_engine_result=_record(PathwayEngineResult),
        integrated_charter_result=_record(IntegratedCharterResult),
        net_overall_system_contribution=_record(NetOverallSystemContribution),
        scale_diagnostic_result=_record(ScaleDiagnosticResult),
    )
    result = FinalPathwayResult(
        product_pathway=product_pathway,
        authoritative_transition_pathway=authoritative,
        candidate_transition_pathway=candidate,
        net_overall_system_risk_result=risk_result,
        evaluation_trace=trace,
        identity_token=identity_token,
        evaluation_run_id="run-1",
        user_id="user-1",
        pathway_id="pathway-1",
        assembly_version="assembly-v1",
        assembly_rule_version="assembly-rules-v1",
    )
    return (
        result,
        product_pathway,
        authoritative,
        candidate,
        risk_result,
        trace,
        identity_token,
    )


def test_final_pathway_result_and_evaluation_trace_are_immutable() -> None:
    result, *_, trace, _ = _final_result()

    with pytest.raises(FrozenInstanceError):
        result.evaluation_run_id = "changed"  # type: ignore[misc]
    with pytest.raises(FrozenInstanceError):
        trace.scale_diagnostic_result = _record(  # type: ignore[misc]
            ScaleDiagnosticResult
        )


def test_final_result_preserves_exact_primary_and_trace_references() -> None:
    (
        result,
        product_pathway,
        authoritative,
        candidate,
        risk_result,
        trace,
        identity_token,
    ) = _final_result()

    assert result.product_pathway is product_pathway
    assert result.authoritative_transition_pathway is authoritative
    assert result.candidate_transition_pathway is candidate
    assert result.net_overall_system_risk_result is risk_result
    assert result.evaluation_trace is trace
    assert result.identity_token is identity_token
    assert result.evaluation_run_id == "run-1"
    assert result.user_id == "user-1"
    assert result.pathway_id == "pathway-1"
    assert result.assembly_version == "assembly-v1"
    assert result.assembly_rule_version == "assembly-rules-v1"

    assert trace.initial_charter_result is (
        result.evaluation_trace.initial_charter_result
    )
    assert trace.pathway_engine_result is result.evaluation_trace.pathway_engine_result
    assert trace.integrated_charter_result is (
        result.evaluation_trace.integrated_charter_result
    )
    assert trace.net_overall_system_contribution is (
        result.evaluation_trace.net_overall_system_contribution
    )
    assert trace.scale_diagnostic_result is (
        result.evaluation_trace.scale_diagnostic_result
    )


def test_candidate_remains_non_authoritative_and_reference_may_be_older() -> None:
    result, _, authoritative, candidate, *_ = _final_result()

    assert candidate is not authoritative
    assert candidate.authoritative_transition_pathway is authoritative
    assert result.candidate_transition_pathway is candidate
    assert result.authoritative_transition_pathway is authoritative
    assert authoritative.evaluation_run_id == "older-run"
    assert authoritative.identity_token is not result.identity_token


def test_final_pathway_assembly_matches_section_15() -> None:
    signature = inspect.signature(FinalPathwayAssembly.assemble)

    assert tuple(signature.parameters) == (
        "self",
        "product_pathway",
        "authoritative_transition_pathway",
        "candidate_transition_pathway",
        "net_overall_system_risk_result",
        "initial_charter_result",
        "pathway_engine_result",
        "integrated_charter_result",
        "net_overall_system_contribution",
        "scale_diagnostic_result",
        "identity_token",
        "evaluation_run_id",
        "user_id",
        "pathway_id",
    )
    assert signature.return_annotation is FinalPathwayResult


def test_final_pathway_foundation_has_only_section_15_surfaces() -> None:
    result_fields = {field.name for field in fields(FinalPathwayResult)}
    trace_fields = {field.name for field in fields(EvaluationTrace)}
    forbidden = {
        "final_charter_result",
        "validator_result",
        "authoritative_promotion",
        "bound_pathway",
        "pathway_assessment",
        "score",
        "rank",
        "weight",
        "vote",
        "optimization_result",
    }

    assert result_fields.isdisjoint(forbidden)
    assert trace_fields.isdisjoint(forbidden)
    assert trace_fields == {
        "initial_charter_result",
        "pathway_engine_result",
        "integrated_charter_result",
        "net_overall_system_contribution",
        "scale_diagnostic_result",
    }
    assert result_fields.isdisjoint(trace_fields)
