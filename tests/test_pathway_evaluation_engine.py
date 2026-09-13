"""Focused structural tests for pathway-engine orchestration."""

from dataclasses import replace
from typing import TypeAlias

import pytest

from climatesos.pathway_evaluation import (
    Attribute,
    ComparisonFinding,
    DocumentationFinding,
    EvaluationRun,
    FabricEvaluatorResult,
    IdentityToken,
    InitialCharterResult,
    OpaqueReference,
    PathwayEvaluationIncompleteError,
    PathwayEvaluationInvariantError,
    PathwayObject,
    ProductAdapterResult,
    ProductFabric,
    ProductIntakeBundle,
    ProductPathway,
    ProductQueueBundle,
    QueueCategory,
    QueueElement,
    QueueEvaluationFailure,
    QueueEvaluatorResult,
    QueueExecutionResult,
    QueueLifecycleState,
    QueueOperationalStatus,
    StructuralPathwayEvaluationEngine,
    TransitionPathway,
)

QueueSubjectType: TypeAlias = QueueElement | ProductQueueBundle
ComparisonFindings: TypeAlias = tuple[ComparisonFinding, ...]
ComparisonCall: TypeAlias = tuple[
    ProductPathway,
    TransitionPathway,
    OpaqueReference | None,
]
PropagationCall: TypeAlias = tuple[
    ProductPathway,
    TransitionPathway,
    ComparisonFindings,
    OpaqueReference | None,
]
QueueCall: TypeAlias = tuple[
    QueueSubjectType,
    ProductPathway,
    ComparisonFindings,
    ComparisonFindings,
    TransitionPathway,
    OpaqueReference | None,
    str,
]
FabricCall: TypeAlias = tuple[
    ProductFabric,
    tuple[QueueEvaluatorResult, ...],
    ComparisonFindings,
    ComparisonFindings,
    TransitionPathway,
    OpaqueReference | None,
    str,
]
DocumentationCall: TypeAlias = tuple[
    ProductAdapterResult,
    tuple[QueueEvaluatorResult, ...],
    tuple[FabricEvaluatorResult, ...],
    ComparisonFindings,
]


def _foundation() -> tuple[
    ProductAdapterResult,
    InitialCharterResult,
    tuple[ProductQueueBundle, ProductQueueBundle],
    tuple[ProductFabric],
]:
    token = IdentityToken("token-1")
    evaluation_run = EvaluationRun("run-1", token.token_id)
    objects = tuple(
        PathwayObject(
            object_id=f"object-{index}",
            object_type="queue",
            user_id="user-1",
            pathway_id="pathway-1",
        )
        for index in range(3)
    )
    queues = tuple(
        QueueElement(item, QueueCategory.UNCLASSIFIED) for item in objects
    )
    pathway = ProductPathway(
        identity_token=token,
        evaluation_run_id=evaluation_run.evaluation_run_id,
        user_id="user-1",
        pathway_id="pathway-1",
        pathway_type="test",
        time_window=None,
        geographic_scope=None,
        system_scope=None,
        objects=objects,
        relationships=(),
        queue_elements=queues,
        assumptions=("pathway assumption",),
        uncertainties=("pathway uncertainty",),
    )
    adapter = ProductAdapterResult(
        product_pathway=pathway,
        intake_bundle=ProductIntakeBundle(token, evaluation_run, ()),
        evaluation_run=evaluation_run,
    )
    initial = InitialCharterResult(
        identity_token=token,
        evaluation_run_id=evaluation_run.evaluation_run_id,
        adapter_result=adapter,
        check_results=(),
        evaluator_version="charter-v1",
        rule_set_version="charter-rules-v1",
        status="completed",
    )
    bundles = (
        ProductQueueBundle("bundle-1", pathway, (queues[0],)),
        ProductQueueBundle("bundle-2", pathway, (queues[1],)),
    )
    fabric = ProductFabric(
        fabric_id="fabric-1",
        coordination_function="caller-defined",
        product_pathway=pathway,
        queue_bundles=bundles,
    )
    return adapter, initial, bundles, (fabric,)


class RecordingComparator:
    def __init__(self) -> None:
        self.direct: ComparisonFindings = (
            ComparisonFinding("direct", "direct", "direct"),
        )
        self.substitution: ComparisonFindings = (
            ComparisonFinding("substitution", "substitution", "substitution"),
        )
        self.downstream: ComparisonFindings = (
            ComparisonFinding("downstream", "propagation", "downstream"),
        )
        self.direct_input: ComparisonCall | None = None
        self.substitution_input: ComparisonCall | None = None
        self.propagation_input: PropagationCall | None = None

    def compare_direct(
        self,
        pathway: ProductPathway,
        transition: TransitionPathway,
        system_context: OpaqueReference | None,
    ) -> ComparisonFindings:
        self.direct_input = (pathway, transition, system_context)
        return self.direct

    def evaluate_substitution_and_combination(
        self,
        pathway: ProductPathway,
        transition: TransitionPathway,
        system_context: OpaqueReference | None,
    ) -> ComparisonFindings:
        self.substitution_input = (pathway, transition, system_context)
        return self.substitution

    def propagate_downstream(
        self,
        pathway: ProductPathway,
        transition: TransitionPathway,
        findings: ComparisonFindings,
        system_context: OpaqueReference | None,
    ) -> ComparisonFindings:
        self.propagation_input = (pathway, transition, findings, system_context)
        return self.downstream


class RecordingQueueEvaluator:
    def __init__(self) -> None:
        self.calls: list[QueueCall] = []

    def evaluate(
        self,
        queue: QueueSubjectType,
        pathway: ProductPathway,
        pathway_findings: ComparisonFindings,
        downstream: ComparisonFindings,
        transition: TransitionPathway,
        system_context: OpaqueReference | None,
        run_id: str,
    ) -> QueueEvaluatorResult:
        self.calls.append(
            (
                queue,
                pathway,
                pathway_findings,
                downstream,
                transition,
                system_context,
                run_id,
            )
        )
        execution = QueueExecutionResult(
            evaluated_queue=queue,
            evaluation_run_id=run_id,
            execution_state="completed",
            progress_records=(),
            user_id=pathway.user_id,
            pathway_id=pathway.pathway_id,
            transition_pathway=transition,
            system_context=system_context,
        )
        return QueueEvaluatorResult(
            evaluated_queue=queue,
            evaluation_run_id=run_id,
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
            user_id=pathway.user_id,
            pathway_id=pathway.pathway_id,
            assumptions=("queue assumption",),
            uncertainties=("queue uncertainty",),
        )


class RecordingFabricEvaluator:
    def __init__(self) -> None:
        self.calls: list[FabricCall] = []

    def evaluate(
        self,
        fabric: ProductFabric,
        queue_results: tuple[QueueEvaluatorResult, ...],
        pathway_findings: ComparisonFindings,
        downstream: ComparisonFindings,
        transition: TransitionPathway,
        system_context: OpaqueReference | None,
        run_id: str,
    ) -> FabricEvaluatorResult:
        self.calls.append(
            (
                fabric,
                queue_results,
                pathway_findings,
                downstream,
                transition,
                system_context,
                run_id,
            )
        )
        pathway = fabric.product_pathway
        return FabricEvaluatorResult(
            product_fabric=fabric,
            queue_results=queue_results,
            pathway_comparison_findings=pathway_findings,
            downstream_propagation_findings=downstream,
            transition_pathway=transition,
            coordination_condition="caller-defined",
            evaluator_version="fabric-v1",
            rule_set_version="fabric-rules-v1",
            evaluation_run_id=run_id,
            user_id=pathway.user_id,
            pathway_id=pathway.pathway_id,
            system_context=system_context,
            assumptions=("fabric assumption",),
            uncertainties=("fabric uncertainty",),
        )


class RecordingDocumentationEvaluator:
    def __init__(self) -> None:
        self.calls: list[DocumentationCall] = []
        self.findings: tuple[DocumentationFinding, ...] = (
            DocumentationFinding("documentation-1", "pathway-1", "known", "finding"),
        )

    def evaluate(
        self,
        adapter: ProductAdapterResult,
        queue_results: tuple[QueueEvaluatorResult, ...],
        fabric_results: tuple[FabricEvaluatorResult, ...],
        comparison_findings: ComparisonFindings,
    ) -> tuple[DocumentationFinding, ...]:
        self.calls.append(
            (adapter, queue_results, fabric_results, comparison_findings)
        )
        return self.findings


def _engine() -> tuple[
    StructuralPathwayEvaluationEngine,
    RecordingComparator,
    RecordingQueueEvaluator,
    RecordingFabricEvaluator,
    RecordingDocumentationEvaluator,
]:
    comparator = RecordingComparator()
    queues = RecordingQueueEvaluator()
    fabrics = RecordingFabricEvaluator()
    documentation = RecordingDocumentationEvaluator()
    evaluator_versions = (Attribute("engine", "v1"),)
    rule_versions = (Attribute("engine", "rules-v1"),)
    engine = StructuralPathwayEvaluationEngine(
        comparator,
        queues,
        fabrics,
        documentation,
        evaluator_versions,
        rule_versions,
    )
    return engine, comparator, queues, fabrics, documentation


def test_engine_routes_context_and_preserves_results_by_reference() -> None:
    adapter, initial, bundles, fabrics = _foundation()
    engine, comparator, queue_evaluator, fabric_evaluator, documentation = _engine()
    transition = TransitionPathway("transition-1")
    system_context = OpaqueReference("system-1")

    result = engine.evaluate(
        adapter,
        initial,
        bundles,
        fabrics,
        transition,
        system_context,
        "run-1",
    )

    assert result.product_pathway is adapter.product_pathway
    assert result.identity_token is adapter.product_pathway.identity_token
    assert result.initial_charter_result is initial
    assert result.transition_pathway is transition
    assert result.system_context is system_context
    assert result.evaluation_run_id == "run-1"
    assert result.direct_comparison_findings is comparator.direct
    assert result.substitution_combination_findings is comparator.substitution
    assert result.downstream_propagation_findings is comparator.downstream
    assert result.documentation_findings is documentation.findings
    assert result.evaluator_versions is engine.evaluator_versions
    assert result.rule_set_versions is engine.rule_set_versions
    assert (result.user_id, result.pathway_id) == ("user-1", "pathway-1")

    assert [call[0] for call in queue_evaluator.calls] == list(bundles)
    assert comparator.direct_input == (
        adapter.product_pathway,
        transition,
        system_context,
    )
    assert comparator.substitution_input == (
        adapter.product_pathway,
        transition,
        system_context,
    )
    pathway_findings = comparator.direct + comparator.substitution
    assert comparator.propagation_input == (
        adapter.product_pathway,
        transition,
        pathway_findings,
        system_context,
    )
    assert all(call[2] == pathway_findings for call in queue_evaluator.calls)
    assert all(call[3] is comparator.downstream for call in queue_evaluator.calls)
    assert all(call[5] is system_context for call in queue_evaluator.calls)

    fabric_call = fabric_evaluator.calls[0]
    assert fabric_call[0] is fabrics[0]
    assert fabric_call[1] == result.queue_results[:2]
    assert all(
        fabric_result is result.fabric_results[index]
        for index, fabric_result in enumerate(documentation.calls[0][2])
    )
    assert documentation.calls[0][0] is adapter
    assert documentation.calls[0][1] is result.queue_results
    assert documentation.calls[0][2] is result.fabric_results
    assert documentation.calls[0][3] == (
        comparator.direct + comparator.substitution + comparator.downstream
    )


def test_engine_accepts_reconstructed_identity_token_with_same_id() -> None:
    adapter, initial, bundles, fabrics = _foundation()
    engine, comparator, _, _, _ = _engine()
    reconstructed_token = IdentityToken(adapter.product_pathway.identity_token.token_id)
    reconstructed_adapter = replace(
        adapter,
        intake_bundle=replace(
            adapter.intake_bundle,
            identity_token=reconstructed_token,
        ),
    )
    reconstructed_initial = replace(
        initial,
        adapter_result=reconstructed_adapter,
    )

    result = engine.evaluate(
        reconstructed_adapter,
        reconstructed_initial,
        bundles,
        fabrics,
        TransitionPathway("transition-1"),
        None,
        "run-1",
    )

    assert reconstructed_token is not adapter.product_pathway.identity_token
    assert result.identity_token is adapter.product_pathway.identity_token
    assert comparator.direct_input is not None


def test_engine_rejects_mismatched_lineage_and_caller_run_before_evaluation() -> None:
    adapter, initial, bundles, fabrics = _foundation()
    engine, comparator, _, _, _ = _engine()
    transition = TransitionPathway("transition-1")
    mismatched_adapter = replace(
        adapter,
        evaluation_run=replace(
            adapter.evaluation_run,
            identity_token_id="token-2",
        ),
    )
    mismatched_initial = replace(initial, adapter_result=mismatched_adapter)

    with pytest.raises(PathwayEvaluationInvariantError, match="IdentityToken"):
        engine.evaluate(
            mismatched_adapter,
            mismatched_initial,
            bundles,
            fabrics,
            transition,
            None,
            "run-1",
        )
    with pytest.raises(PathwayEvaluationInvariantError, match="EvaluationRun"):
        engine.evaluate(
            adapter,
            initial,
            bundles,
            fabrics,
            transition,
            None,
            "run-2",
        )
    assert comparator.direct_input is None


def test_queue_failure_prevents_result_and_is_not_sent_downstream(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    adapter, initial, bundles, fabrics = _foundation()
    engine, _, queue_evaluator, fabric_evaluator, documentation = _engine()
    transition = TransitionPathway("transition-1")
    def fail_first(
        queue: QueueSubjectType,
        pathway: ProductPathway,
        pathway_findings: ComparisonFindings,
        downstream: ComparisonFindings,
        received_transition: TransitionPathway,
        system_context: OpaqueReference | None,
        run_id: str,
    ) -> QueueEvaluationFailure:
        return QueueEvaluationFailure(
            evaluated_queue=queue,
            evaluation_run_id=run_id,
            user_id=pathway.user_id,
            pathway_id=pathway.pathway_id,
        )

    monkeypatch.setattr(queue_evaluator, "evaluate", fail_first)
    with pytest.raises(PathwayEvaluationIncompleteError) as raised:
        engine.evaluate(
            adapter,
            initial,
            bundles,
            fabrics,
            transition,
            None,
            "run-1",
        )

    assert raised.value.failure.evaluated_queue is bundles[0]
    assert fabric_evaluator.calls == []
    assert documentation.calls == []
def test_engine_rejects_foreign_ownership_and_result_attribution(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    adapter, initial, bundles, fabrics = _foundation()
    engine, _, queue_evaluator, _, _ = _engine()
    transition = TransitionPathway("transition-1")
    foreign_pathway = replace(
        adapter.product_pathway,
        identity_token=IdentityToken("token-2"),
    )
    foreign_bundle = replace(bundles[0], product_pathway=foreign_pathway)

    with pytest.raises(
        PathwayEvaluationInvariantError,
        match="ProductPathway ownership",
    ):
        engine.evaluate(
            adapter,
            initial,
            (foreign_bundle, bundles[1]),
            (),
            transition,
            None,
            "run-1",
        )

    original_evaluate = queue_evaluator.evaluate

    def misattribute(
        queue: QueueSubjectType,
        pathway: ProductPathway,
        pathway_findings: ComparisonFindings,
        downstream: ComparisonFindings,
        received_transition: TransitionPathway,
        system_context: OpaqueReference | None,
        run_id: str,
    ) -> QueueEvaluatorResult:
        result = original_evaluate(
            queue,
            pathway,
            pathway_findings,
            downstream,
            received_transition,
            system_context,
            run_id,
        )
        return replace(result, user_id="user-2")

    monkeypatch.setattr(queue_evaluator, "evaluate", misattribute)
    with pytest.raises(
        PathwayEvaluationInvariantError,
        match="attribution",
    ):
        engine.evaluate(
            adapter,
            initial,
            bundles,
            fabrics,
            transition,
            None,
            "run-1",
        )
