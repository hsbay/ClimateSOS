"""Foundation invariants for Section 11 contribution records and boundary."""

from dataclasses import FrozenInstanceError, fields
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
    NetOverallSystemContributionEvaluator,
    OpaqueReference,
    PathwayEngineResult,
    PathwayObject,
    ProductAdapterResult,
    ProductFabric,
    ProductIntakeBundle,
    ProductPathway,
    ProductQueueBundle,
    QueueCategory,
    QueueElement,
    QueueEvaluatorResult,
    QueueExecutionResult,
    QueueLifecycleState,
    QueueOperationalStatus,
    QueueProgressRecord,
    SourceReference,
    TransitionPathway,
)


def _upstream_results() -> tuple[
    ProductPathway,
    PathwayEngineResult,
    IntegratedCharterResult,
    TransitionPathway,
]:
    token = IdentityToken("token-1")
    evaluation_run = EvaluationRun("run-1", token.token_id)
    intake = ProductIntakeBundle(token, evaluation_run, ())
    output = PathwayObject(
        object_id="output-1",
        object_type="pathway-output",
        user_id="user-1",
        pathway_id="pathway-1",
    )
    queue_object = PathwayObject(
        object_id="queue-1",
        object_type="deployment",
        user_id="user-1",
        pathway_id="pathway-1",
    )
    queue_element = QueueElement(
        queue_object,
        QueueCategory.PRODUCT_OUTPUT_AND_DELIVERY_ACCESS,
    )
    pathway = ProductPathway(
        identity_token=token,
        evaluation_run_id=evaluation_run.evaluation_run_id,
        user_id="user-1",
        pathway_id="pathway-1",
        pathway_type="test",
        time_window="2030",
        geographic_scope="local",
        system_scope="power",
        objects=(output, queue_object),
        relationships=(),
        queue_elements=(queue_element,),
    )
    adapter_result = ProductAdapterResult(pathway, intake, evaluation_run)
    initial_result = InitialCharterResult(
        identity_token=token,
        evaluation_run_id=evaluation_run.evaluation_run_id,
        adapter_result=adapter_result,
        check_results=(),
        evaluator_version="initial-1",
        rule_set_version="charter-1",
        status="PASS",
    )
    transition = TransitionPathway("transition-1")
    system_context = OpaqueReference("system-context-1")
    queue_bundle = ProductQueueBundle(
        bundle_id="queue-bundle-1",
        product_pathway=pathway,
        queue_elements=(queue_element,),
    )
    progress = QueueProgressRecord(
        evaluated_queue=queue_bundle,
        evaluation_run_id=evaluation_run.evaluation_run_id,
        operational_status=QueueOperationalStatus.CLEAR,
        lifecycle_state=QueueLifecycleState.OPEN,
        ordering_status=None,
        synchronization_status=None,
        evaluation_position=0,
        user_id=pathway.user_id,
        pathway_id=pathway.pathway_id,
    )
    execution = QueueExecutionResult(
        evaluated_queue=queue_bundle,
        evaluation_run_id=evaluation_run.evaluation_run_id,
        execution_state="completed",
        progress_records=(progress,),
        user_id=pathway.user_id,
        pathway_id=pathway.pathway_id,
        transition_pathway=transition,
        system_context=system_context,
    )
    queue_result = QueueEvaluatorResult(
        evaluated_queue=queue_bundle,
        evaluation_run_id=evaluation_run.evaluation_run_id,
        final_operational_status=QueueOperationalStatus.CLEAR,
        final_lifecycle_state=QueueLifecycleState.OPEN,
        ordering_status=None,
        synchronization_status=None,
        evaluation_state=None,
        execution_result=execution,
        progress_records=(progress,),
        transition_pathway=transition,
        evaluator_version="queue-1",
        rule_set_version="queue-rules-1",
        user_id=pathway.user_id,
        pathway_id=pathway.pathway_id,
    )
    comparison = ComparisonFinding(
        finding_id="comparison-1",
        finding_type="direct",
        description="Material comparison finding.",
    )
    fabric = ProductFabric(
        fabric_id="fabric-1",
        coordination_function="delivery coordination",
        product_pathway=pathway,
        queue_bundles=(queue_bundle,),
    )
    fabric_result = FabricEvaluatorResult(
        product_fabric=fabric,
        queue_results=(queue_result,),
        pathway_comparison_findings=(comparison,),
        downstream_propagation_findings=(),
        transition_pathway=transition,
        coordination_condition="coordinated",
        evaluator_version="fabric-1",
        rule_set_version="fabric-rules-1",
        evaluation_run_id=evaluation_run.evaluation_run_id,
        user_id=pathway.user_id,
        pathway_id=pathway.pathway_id,
        system_context=system_context,
    )
    documentation = DocumentationFinding(
        finding_id="documentation-1",
        subject_id=output.object_id,
        status="supported",
        description="Material documentation finding.",
    )
    engine_result = PathwayEngineResult(
        identity_token=token,
        product_pathway=pathway,
        transition_pathway=transition,
        initial_charter_result=initial_result,
        direct_comparison_findings=(comparison,),
        substitution_combination_findings=(),
        downstream_propagation_findings=(),
        queue_results=(queue_result,),
        fabric_results=(fabric_result,),
        documentation_findings=(documentation,),
        evaluation_run_id=evaluation_run.evaluation_run_id,
        system_context=system_context,
        evaluator_versions=(),
        rule_set_versions=(),
        user_id=pathway.user_id,
        pathway_id=pathway.pathway_id,
    )
    integrated_result = IntegratedCharterResult(
        identity_token=token,
        evaluation_run_id=evaluation_run.evaluation_run_id,
        pathway_engine_result=engine_result,
        initial_charter_result=initial_result,
        check_results=(),
        evaluator_version="integrated-1",
        rule_set_version="charter-1",
        status="PASS",
    )
    return pathway, engine_result, integrated_result, transition


def _contribution() -> NetOverallSystemContribution:
    pathway, engine_result, integrated_result, transition = _upstream_results()
    evidence = SourceReference("evidence-1", "page 2")
    provenance = SourceReference("provenance-1")
    comparison = engine_result.direct_comparison_findings[0]
    queue_result = engine_result.queue_results[0]
    fabric_result = engine_result.fabric_results[0]
    documentation = engine_result.documentation_findings[0]
    first = ContributionFinding(
        finding_id="contribution-1",
        effect_description="Supports a local transition function.",
        contribution_scope="local",
        contribution_type="enabling",
        contribution_mechanism="constraint reduction",
        contribution_statuses=("supported", "limited", "conditional"),
        pathway_output_references=(pathway.objects[0],),
        net_zero_transition_effects=("reduces a material bottleneck",),
        transition_function_references=(OpaqueReference("function-1"),),
        system_effects=("strengthens local delivery",),
        timing_effects=("available only after infrastructure delivery",),
        dependencies=("grid connection",),
        conditions=("permit granted",),
        supporting_comparison_findings=(comparison,),
        supporting_queue_results=(queue_result,),
        supporting_fabric_results=(fabric_result,),
        supporting_documentation_findings=(documentation,),
        supporting_system_references=(OpaqueReference("relationship-1"),),
        evidence_references=(evidence,),
        provenance=(provenance,),
    )
    second = ContributionFinding(
        finding_id="contribution-2",
        effect_description="A broader effect remains unresolved.",
        contribution_statuses=("indirect", "time-limited", "unresolved"),
    )
    return NetOverallSystemContribution(
        product_pathway=pathway,
        pathway_engine_result=engine_result,
        integrated_charter_result=integrated_result,
        transition_pathway=transition,
        contribution_findings=(first, second),
        evaluation_run_id=engine_result.evaluation_run_id,
        user_id=engine_result.user_id,
        pathway_id=engine_result.pathway_id,
        evaluator_version="contribution-1",
        rule_set_version="contribution-rules-1",
        assumptions=("upstream system context remains applicable",),
        uncertainties=("regional propagation is uncertain",),
        evidence_references=(evidence,),
        provenance=(provenance,),
    )


def test_contribution_records_are_frozen_and_use_immutable_collections() -> None:
    contribution = _contribution()
    finding = contribution.contribution_findings[0]

    with pytest.raises(FrozenInstanceError):
        contribution.pathway_id = "changed"  # type: ignore[misc]
    with pytest.raises(FrozenInstanceError):
        finding.effect_description = "changed"  # type: ignore[misc]
    with pytest.raises(TypeError):
        contribution.contribution_findings[0] = finding  # type: ignore[index]
    with pytest.raises(TypeError):
        finding.conditions[0] = "changed"  # type: ignore[index]


def test_contribution_preserves_upstream_relationships_and_attribution() -> None:
    contribution = _contribution()
    engine_result = contribution.pathway_engine_result

    assert contribution.integrated_charter_result.pathway_engine_result is engine_result
    assert contribution.product_pathway is engine_result.product_pathway
    assert contribution.transition_pathway is engine_result.transition_pathway
    assert contribution.evaluation_run_id == engine_result.evaluation_run_id
    assert contribution.user_id == engine_result.user_id
    assert contribution.pathway_id == engine_result.pathway_id
    assert contribution.evaluator_version == "contribution-1"
    assert contribution.rule_set_version == "contribution-rules-1"


def test_multiple_rich_findings_preserve_open_statuses_and_traceability() -> None:
    contribution = _contribution()
    engine_result = contribution.pathway_engine_result
    first, second = contribution.contribution_findings

    assert len(contribution.contribution_findings) == 2
    assert first.contribution_statuses == ("supported", "limited", "conditional")
    assert second.contribution_statuses == ("indirect", "time-limited", "unresolved")
    assert first.contribution_mechanism == "constraint reduction"
    assert first.timing_effects == (
        "available only after infrastructure delivery",
    )
    assert first.dependencies == ("grid connection",)
    assert first.conditions == ("permit granted",)
    assert (
        first.pathway_output_references[0]
        is engine_result.product_pathway.objects[0]
    )
    assert (
        first.supporting_comparison_findings[0]
        is engine_result.direct_comparison_findings[0]
    )
    assert first.supporting_queue_results[0] is engine_result.queue_results[0]
    assert first.supporting_fabric_results[0] is engine_result.fabric_results[0]
    assert (
        first.supporting_documentation_findings[0]
        is engine_result.documentation_findings[0]
    )
    assert first.supporting_system_references == (
        OpaqueReference("relationship-1"),
    )
    assert first.evidence_references == (SourceReference("evidence-1", "page 2"),)
    assert first.provenance == (SourceReference("provenance-1"),)
    finding_fields = {field.name for field in fields(ContributionFinding)}
    assert "execution_error" not in finding_fields

    assert second.supporting_comparison_findings == ()
    assert second.supporting_queue_results == ()
    assert second.supporting_fabric_results == ()
    assert second.supporting_documentation_findings == ()


def test_material_queue_summary_keeps_subordinate_records_reachable_only() -> None:
    finding = _contribution().contribution_findings[0]
    queue_result = finding.supporting_queue_results[0]
    finding_fields = {field.name for field in fields(ContributionFinding)}

    assert isinstance(queue_result.execution_result, QueueExecutionResult)
    assert isinstance(queue_result.progress_records[0], QueueProgressRecord)
    assert {
        "supporting_queue_execution_results",
        "supporting_queue_progress_records",
    }.isdisjoint(finding_fields)


def test_contribution_uses_concrete_flow_summary_and_output_types() -> None:
    hints = get_type_hints(ContributionFinding)

    assert hints["pathway_output_references"] == tuple[PathwayObject, ...]
    assert hints["supporting_comparison_findings"] == tuple[ComparisonFinding, ...]
    assert hints["supporting_queue_results"] == tuple[QueueEvaluatorResult, ...]
    assert hints["supporting_fabric_results"] == tuple[FabricEvaluatorResult, ...]
    assert hints["supporting_documentation_findings"] == tuple[
        DocumentationFinding, ...
    ]
    assert hints["transition_function_references"] == tuple[OpaqueReference, ...]
    assert hints["supporting_system_references"] == tuple[OpaqueReference, ...]


def test_contribution_result_has_no_identity_or_scalar_ranking_field() -> None:
    field_names = {field.name for field in fields(NetOverallSystemContribution)}

    assert "identity_token" not in field_names
    assert {"score", "goodness_score", "rank", "ranking"}.isdisjoint(field_names)


def test_contribution_evaluator_protocol_has_exact_two_input_contract() -> None:
    parameters = signature(NetOverallSystemContributionEvaluator.evaluate).parameters
    hints = get_type_hints(NetOverallSystemContributionEvaluator.evaluate)

    assert tuple(parameters) == (
        "self",
        "pathway_engine_result",
        "integrated_charter_result",
    )
    assert hints["pathway_engine_result"] is PathwayEngineResult
    assert hints["integrated_charter_result"] is IntegratedCharterResult
    assert hints["return"] is NetOverallSystemContribution
