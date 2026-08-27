"""Focused tests for comparator and documentation structural boundaries."""

from dataclasses import FrozenInstanceError, replace

import pytest

from climatesos.pathway_evaluation import (
    ComparisonFinding,
    ComparisonInvariantError,
    DocumentationEvaluationInvariantError,
    DocumentationFinding,
    FabricEvaluatorResult,
    IdentityToken,
    IntakeArtifact,
    OpaqueReference,
    PathwayObject,
    PathwayRelationship,
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
    SourceReference,
    TransitionPathway,
    ValidatedDocumentationEvaluator,
    ValidatedPathwayComparator,
)


def _foundation() -> tuple[
    ProductAdapterResult,
    ProductQueueBundle,
    QueueEvaluatorResult,
    FabricEvaluatorResult,
    TransitionPathway,
    OpaqueReference,
]:
    token = IdentityToken("user-1", "pathway-1")
    source = SourceReference("source-1", "artifact-1")
    pathway_object = PathwayObject(
        object_id="object-1",
        object_type="represented-function",
        user_id=token.user_id,
        pathway_id=token.pathway_id,
        source_references=(source,),
        evidence_references=(source,),
    )
    relationship = PathwayRelationship(
        relationship_id="relationship-1",
        relationship_type="depends-on",
        source_object_id=pathway_object.object_id,
        target_object_id=pathway_object.object_id,
        user_id=token.user_id,
        pathway_id=token.pathway_id,
        source_references=(source,),
    )
    queue_element = QueueElement(pathway_object, QueueCategory.UNCLASSIFIED)
    pathway = ProductPathway(
        identity_token=token,
        pathway_type="test",
        time_window=None,
        geographic_scope=None,
        system_scope=None,
        objects=(pathway_object,),
        relationships=(relationship,),
        queue_elements=(queue_element,),
        documentation_references=(source,),
        evidence_references=(source,),
    )
    intake = ProductIntakeBundle(
        identity_token=token,
        materials=(
            IntakeArtifact(
                artifact_id="artifact-1",
                media_type="text/plain",
                content="preserved source",
                provenance=(source,),
            ),
        ),
        documentation=(source,),
        evidence=(source,),
        provenance=(source,),
    )
    adapter_result = ProductAdapterResult(pathway, intake)
    bundle = ProductQueueBundle(
        bundle_id="bundle-1",
        product_pathway=pathway,
        queue_elements=(queue_element,),
        relationships=(relationship,),
    )
    transition = TransitionPathway("transition-1", (source,))
    context = OpaqueReference("system-model-1")
    execution = QueueExecutionResult(
        evaluated_queue=bundle,
        evaluation_run_id="run-1",
        execution_state="caller-completed",
        progress_records=(),
        user_id=token.user_id,
        pathway_id=token.pathway_id,
        evidence_references=(source,),
        transition_pathway=transition,
        system_context=context,
    )
    queue_result = QueueEvaluatorResult(
        evaluated_queue=bundle,
        evaluation_run_id="run-1",
        final_operational_status=QueueOperationalStatus.CLEAR,
        final_lifecycle_state=QueueLifecycleState.OPEN,
        ordering_status=None,
        synchronization_status=None,
        evaluation_state=None,
        execution_result=execution,
        progress_records=(),
        transition_pathway=transition,
        evaluator_version="queue-v1",
        rule_set_version="queue-rules-v1",
        user_id=token.user_id,
        pathway_id=token.pathway_id,
        evidence_references=(source,),
    )
    fabric = ProductFabric(
        fabric_id="fabric-1",
        coordination_function="caller-defined",
        product_pathway=pathway,
        queue_bundles=(bundle,),
        relationships=(relationship,),
    )
    fabric_result = FabricEvaluatorResult(
        product_fabric=fabric,
        queue_results=(queue_result,),
        pathway_comparison_findings=(),
        downstream_propagation_findings=(),
        transition_pathway=transition,
        coordination_condition="caller-defined",
        evaluator_version="fabric-v1",
        rule_set_version="fabric-rules-v1",
        evaluation_run_id="run-1",
        user_id=token.user_id,
        pathway_id=token.pathway_id,
        system_context=context,
        evidence_references=(source,),
    )
    return (
        adapter_result,
        bundle,
        queue_result,
        fabric_result,
        transition,
        context,
    )


def _traceable_finding(adapter_result: ProductAdapterResult) -> ComparisonFinding:
    source = adapter_result.intake_bundle.evidence[0]
    return ComparisonFinding(
        finding_id="comparison-1",
        finding_type="caller-defined",
        description="caller-supplied conclusion",
        pathway_object_references=(OpaqueReference("object-1"),),
        pathway_relationship_references=(OpaqueReference("relationship-1"),),
        transition_object_references=(OpaqueReference("transition-object-1"),),
        transition_relationship_references=(
            OpaqueReference("transition-relationship-1"),
        ),
        system_model_basis=(OpaqueReference("system-model-1"),),
        evidence_references=(source,),
    )


def test_comparator_routes_each_caller_boundary_and_preserves_findings() -> None:
    adapter, _, _, _, transition, context = _foundation()
    pathway = adapter.product_pathway
    direct = (_traceable_finding(adapter),)
    substitution = (
        replace(
            direct[0],
            finding_id="comparison-2",
            finding_type="caller-defined-substitution",
        ),
    )
    downstream = (
        replace(
            direct[0],
            finding_id="comparison-3",
            finding_type="caller-defined-propagation",
        ),
    )
    calls: list[tuple[object, ...]] = []

    def compare_direct(
        received_pathway: ProductPathway,
        received_transition: TransitionPathway,
        received_context: OpaqueReference | None,
    ) -> tuple[ComparisonFinding, ...]:
        calls.append((received_pathway, received_transition, received_context))
        return direct

    def evaluate_substitution(
        received_pathway: ProductPathway,
        received_transition: TransitionPathway,
        received_context: OpaqueReference | None,
    ) -> tuple[ComparisonFinding, ...]:
        calls.append((received_pathway, received_transition, received_context))
        return substitution

    def propagate(
        received_pathway: ProductPathway,
        received_transition: TransitionPathway,
        received_findings: tuple[ComparisonFinding, ...],
        received_context: OpaqueReference | None,
    ) -> tuple[ComparisonFinding, ...]:
        calls.append(
            (
                received_pathway,
                received_transition,
                received_findings,
                received_context,
            )
        )
        return downstream

    comparator = ValidatedPathwayComparator(
        compare_direct,
        evaluate_substitution,
        propagate,
    )

    direct_result = comparator.compare_direct(pathway, transition, context)
    substitution_result = comparator.evaluate_substitution_and_combination(
        pathway,
        transition,
        context,
    )
    prior_findings = direct_result + substitution_result
    downstream_result = comparator.propagate_downstream(
        pathway,
        transition,
        prior_findings,
        context,
    )

    assert direct_result is direct
    assert substitution_result is substitution
    assert downstream_result is downstream
    assert calls == [
        (pathway, transition, context),
        (pathway, transition, context),
        (pathway, transition, prior_findings, context),
    ]
    assert direct_result[0].evidence_references[0] is adapter.intake_bundle.evidence[0]
    with pytest.raises(FrozenInstanceError):
        direct_result[0].description = "rewritten"  # type: ignore[misc]


def test_comparator_rejects_foreign_pathway_references_and_attribution() -> None:
    adapter, _, _, _, transition, context = _foundation()
    pathway = adapter.product_pathway
    foreign_reference = replace(
        _traceable_finding(adapter),
        pathway_object_references=(OpaqueReference("foreign-object"),),
    )
    comparator = ValidatedPathwayComparator(
        lambda _pathway, _transition, _context: (foreign_reference,),
        lambda _pathway, _transition, _context: (),
        lambda _pathway, _transition, _findings, _context: (),
    )

    with pytest.raises(ComparisonInvariantError, match="outside"):
        comparator.compare_direct(pathway, transition, context)

    misattributed_object = replace(pathway.objects[0], user_id="other-user")
    misattributed_pathway = replace(pathway, objects=(misattributed_object,))
    attributed_finding = _traceable_finding(adapter)
    comparator = replace(
        comparator,
        direct_comparison_function=(
            lambda _pathway, _transition, _context: (attributed_finding,)
        ),
    )

    with pytest.raises(ComparisonInvariantError, match="attribution"):
        comparator.compare_direct(misattributed_pathway, transition, context)


def test_comparator_rejects_non_tuple_results_without_inventing_an_outcome() -> None:
    adapter, _, _, _, transition, context = _foundation()
    comparator = ValidatedPathwayComparator(
        lambda _pathway, _transition, _context: [],  # type: ignore[arg-type,return-value]
        lambda _pathway, _transition, _context: (),
        lambda _pathway, _transition, _findings, _context: (),
    )

    with pytest.raises(ComparisonInvariantError, match="tuple"):
        comparator.compare_direct(adapter.product_pathway, transition, context)


def test_documentation_routes_existing_artifacts_and_preserves_caller_findings() -> (
    None
):
    adapter, _, queue_result, fabric_result, _, _ = _foundation()
    comparison_findings = (_traceable_finding(adapter),)
    evidence = adapter.intake_bundle.evidence[0]
    findings = (
        DocumentationFinding(
            finding_id="documentation-1",
            subject_id="object-1",
            status="caller-defined-status",
            description="caller-supplied documentation conclusion",
            evidence_references=(evidence,),
        ),
    )
    calls: list[tuple[object, ...]] = []

    def evaluate(
        received_adapter: ProductAdapterResult,
        received_queue_results: tuple[QueueEvaluatorResult, ...],
        received_fabric_results: tuple[FabricEvaluatorResult, ...],
        received_comparison_findings: tuple[ComparisonFinding, ...],
    ) -> tuple[DocumentationFinding, ...]:
        calls.append(
            (
                received_adapter,
                received_queue_results,
                received_fabric_results,
                received_comparison_findings,
            )
        )
        return findings

    evaluator = ValidatedDocumentationEvaluator(evaluate)
    queue_results = (queue_result,)
    fabric_results = (fabric_result,)

    result = evaluator.evaluate(
        adapter,
        queue_results,
        fabric_results,
        comparison_findings,
    )

    assert result is findings
    assert calls == [
        (adapter, queue_results, fabric_results, comparison_findings),
    ]
    assert result[0].status == "caller-defined-status"
    assert result[0].evidence_references[0] is evidence
    with pytest.raises(FrozenInstanceError):
        queue_result.user_id = "rewritten"  # type: ignore[misc]


def test_documentation_rejects_foreign_or_reconstructed_evaluation_artifacts() -> None:
    adapter, _, queue_result, fabric_result, _, _ = _foundation()
    evaluator = ValidatedDocumentationEvaluator(
        lambda _adapter, _queues, _fabrics, _comparisons: (),
    )
    wrong_attribution = replace(queue_result, user_id="other-user")

    with pytest.raises(
        DocumentationEvaluationInvariantError,
        match="attribution",
    ):
        evaluator.evaluate(adapter, (wrong_attribution,), (), ())

    reconstructed_queue_result = replace(queue_result)
    incoherent_fabric_result = replace(
        fabric_result,
        queue_results=(reconstructed_queue_result,),
    )
    with pytest.raises(
        DocumentationEvaluationInvariantError,
        match="preserve supplied queue result references",
    ):
        evaluator.evaluate(adapter, (queue_result,), (incoherent_fabric_result,), ())


def test_documentation_rejects_non_tuple_caller_findings() -> None:
    adapter, _, queue_result, fabric_result, _, _ = _foundation()
    evaluator = ValidatedDocumentationEvaluator(
        lambda _adapter, _queues, _fabrics, _comparisons: [],  # type: ignore[arg-type,return-value]
    )

    with pytest.raises(DocumentationEvaluationInvariantError, match="tuple"):
        evaluator.evaluate(adapter, (queue_result,), (fabric_result,), ())
