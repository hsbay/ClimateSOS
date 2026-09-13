"""Foundation invariants for the Section 12 Scale Diagnostic boundary."""

from dataclasses import FrozenInstanceError, fields, is_dataclass
from inspect import signature
from typing import get_type_hints

import pytest

from climatesos.pathway_evaluation import (
    ComparisonFinding,
    ContributionFinding,
    DocumentationFinding,
    EvaluationRun,
    FabricEvaluatorResult,
    IdentityToken,
    InitialCharterResult,
    IntegratedCharterResult,
    NetOverallSystemContribution,
    OpaqueReference,
    PathwayEngineResult,
    PathwayObject,
    ProductAdapterResult,
    ProductIntakeBundle,
    ProductPathway,
    QueueEvaluatorResult,
    ScaleDiagnosticEvaluator,
    ScaleDiagnosticResult,
    ScaleFinding,
    SourceReference,
    TransitionPathway,
)


def _scale_records() -> tuple[
    ProductPathway,
    TransitionPathway,
    ContributionFinding,
    ScaleFinding,
    ScaleDiagnosticResult,
]:
    token = IdentityToken("token-1")
    run = EvaluationRun("run-1", token.token_id)
    intake = ProductIntakeBundle(token, run, ())
    output = PathwayObject(
        object_id="output-1",
        object_type="caller-defined",
        user_id="user-1",
        pathway_id="pathway-1",
    )
    pathway = ProductPathway(
        identity_token=token,
        evaluation_run_id=run.evaluation_run_id,
        user_id="user-1",
        pathway_id="pathway-1",
        pathway_type="caller-defined",
        time_window="2030",
        geographic_scope="local",
        system_scope="power",
        objects=(output,),
        relationships=(),
    )
    adapter = ProductAdapterResult(pathway, intake, run)
    initial = InitialCharterResult(
        identity_token=token,
        evaluation_run_id=run.evaluation_run_id,
        adapter_result=adapter,
        check_results=(),
        evaluator_version="initial-1",
        rule_set_version="charter-1",
        status="PASS",
    )
    transition = TransitionPathway("transition-1")
    engine = PathwayEngineResult(
        identity_token=token,
        product_pathway=pathway,
        transition_pathway=transition,
        initial_charter_result=initial,
        direct_comparison_findings=(),
        substitution_combination_findings=(),
        downstream_propagation_findings=(),
        queue_results=(),
        fabric_results=(),
        documentation_findings=(),
        evaluation_run_id=run.evaluation_run_id,
        system_context=None,
        evaluator_versions=(),
        rule_set_versions=(),
        user_id=pathway.user_id,
        pathway_id=pathway.pathway_id,
    )
    integrated = IntegratedCharterResult(
        identity_token=token,
        evaluation_run_id=run.evaluation_run_id,
        pathway_engine_result=engine,
        initial_charter_result=initial,
        check_results=(),
        evaluator_version="integrated-1",
        rule_set_version="charter-1",
        status="PASS",
    )
    contribution_finding = ContributionFinding(
        finding_id="contribution-1",
        effect_description="Caller-established contribution.",
        pathway_output_references=(output,),
    )
    contribution = NetOverallSystemContribution(
        product_pathway=pathway,
        pathway_engine_result=engine,
        integrated_charter_result=integrated,
        transition_pathway=transition,
        contribution_findings=(contribution_finding,),
        evaluation_run_id=run.evaluation_run_id,
        user_id=pathway.user_id,
        pathway_id=pathway.pathway_id,
        evaluator_version="contribution-1",
        rule_set_version="contribution-rules-1",
    )
    scale_finding = ScaleFinding(
        finding_id="scale-1",
        description="Caller-established scale condition.",
        scale_scope="regional",
        finding_type="future-caller-defined-type",
        statuses=("conditional", "future-caller-defined-status"),
        contribution_findings=(contribution_finding,),
        transition_function_references=(OpaqueReference("function-1"),),
        geographic_scope="region-1",
        system_scope="power",
        capacity_findings=("caller-established capacity",),
        replication_findings=("caller-established replication",),
        scale_progression_findings=("caller-established progression",),
        timing_conditions=("caller-established timing",),
        constraints=("caller-established constraint",),
        bottlenecks=("caller-established bottleneck",),
        scale_dependent_effects=("caller-established effect",),
        unresolved_conditions=("caller-established uncertainty",),
        supporting_pathway_outputs=(output,),
        supporting_system_references=(OpaqueReference("system-1"),),
        evidence_references=(SourceReference("evidence-1"),),
        provenance=(SourceReference("provenance-1"),),
    )
    result = ScaleDiagnosticResult(
        product_pathway=pathway,
        net_overall_system_contribution=contribution,
        transition_pathway=transition,
        scale_findings=(scale_finding,),
        evaluation_run_id=run.evaluation_run_id,
        user_id=pathway.user_id,
        pathway_id=pathway.pathway_id,
        evaluator_version="scale-1",
        rule_set_version="scale-rules-1",
        assumptions=("caller-established assumption",),
        uncertainties=("caller-established uncertainty",),
        evidence_references=(SourceReference("evidence-1"),),
        provenance=(SourceReference("provenance-1"),),
    )
    return pathway, transition, contribution_finding, scale_finding, result


def test_scale_models_are_frozen_slotted_and_collections_are_immutable() -> None:
    _, _, _, finding, result = _scale_records()

    assert is_dataclass(ScaleFinding)
    assert is_dataclass(ScaleDiagnosticResult)
    assert hasattr(ScaleFinding, "__slots__")
    assert hasattr(ScaleDiagnosticResult, "__slots__")
    with pytest.raises(FrozenInstanceError):
        finding.description = "changed"  # type: ignore[misc]
    with pytest.raises(FrozenInstanceError):
        result.pathway_id = "changed"  # type: ignore[misc]
    with pytest.raises(TypeError):
        finding.statuses[0] = "changed"  # type: ignore[index]
    with pytest.raises(TypeError):
        result.scale_findings[0] = finding  # type: ignore[index]


def test_scale_result_preserves_required_references_and_attribution() -> None:
    pathway, transition, _, finding, result = _scale_records()

    assert result.product_pathway is pathway
    assert result.transition_pathway is transition
    assert result.scale_findings[0] is finding
    assert result.net_overall_system_contribution.product_pathway is pathway
    assert result.evaluation_run_id == "run-1"
    assert result.user_id == pathway.user_id
    assert result.pathway_id == pathway.pathway_id


def test_scale_finding_has_its_own_typed_material_evidence_surface() -> None:
    _, _, contribution_finding, finding, _ = _scale_records()
    hints = get_type_hints(ScaleFinding)

    assert finding.contribution_findings[0] is contribution_finding
    assert hints["contribution_findings"] == tuple[ContributionFinding, ...]
    assert hints["supporting_pathway_outputs"] == tuple[PathwayObject, ...]
    assert hints["supporting_comparison_findings"] == tuple[ComparisonFinding, ...]
    assert hints["supporting_queue_results"] == tuple[QueueEvaluatorResult, ...]
    assert hints["supporting_fabric_results"] == tuple[FabricEvaluatorResult, ...]
    assert hints["supporting_documentation_findings"] == tuple[
        DocumentationFinding, ...
    ]
    assert hints["supporting_system_references"] == tuple[OpaqueReference, ...]


def test_scale_models_exclude_identity_subrecords_taxonomies_and_scores() -> None:
    finding_fields = {field.name for field in fields(ScaleFinding)}
    result_fields = {field.name for field in fields(ScaleDiagnosticResult)}

    assert "identity_token" not in finding_fields | result_fields
    assert {
        "queue_execution_results",
        "queue_progress_records",
        "supporting_queue_execution_results",
        "supporting_queue_progress_records",
    }.isdisjoint(finding_fields)
    assert {"score", "rank", "ranking", "weight", "vote", "voting"}.isdisjoint(
        finding_fields | result_fields
    )
    assert get_type_hints(ScaleFinding)["statuses"] == tuple[str, ...]


def test_scale_diagnostic_evaluator_has_specified_artifact_contract() -> None:
    parameters = signature(ScaleDiagnosticEvaluator.evaluate).parameters
    hints = get_type_hints(ScaleDiagnosticEvaluator.evaluate)

    assert tuple(parameters) == (
        "self",
        "net_overall_system_contribution",
        "product_pathway",
        "transition_pathway",
        "system_context",
        "assumptions",
        "uncertainties",
        "evidence_references",
        "provenance",
        "user_id",
        "pathway_id",
        "evaluation_run_id",
    )
    assert hints["net_overall_system_contribution"] is NetOverallSystemContribution
    assert hints["product_pathway"] is ProductPathway
    assert hints["transition_pathway"] is TransitionPathway
    assert hints["system_context"] == OpaqueReference | None
    assert hints["assumptions"] == tuple[str, ...]
    assert hints["uncertainties"] == tuple[str, ...]
    assert hints["evidence_references"] == tuple[SourceReference, ...]
    assert hints["provenance"] == tuple[SourceReference, ...]
    assert hints["user_id"] is str
    assert hints["pathway_id"] is str
    assert hints["evaluation_run_id"] is str
    assert hints["return"] is ScaleDiagnosticResult
