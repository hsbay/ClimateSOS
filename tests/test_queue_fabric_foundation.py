"""Structural and ownership checks for queue/fabric work boundaries."""

from dataclasses import FrozenInstanceError

import pytest

from climatesos.pathway_evaluation import (
    AssemblyInvariantError,
    ComparisonFinding,
    EvaluationRun,
    FabricEvaluationInvariantError,
    FabricEvaluatorResult,
    IdentityToken,
    InitialCharterResult,
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
    QueueEvaluationFailure,
    QueueEvaluationInvariantError,
    QueueEvaluatorResult,
    QueueExecutionResult,
    QueueLifecycleState,
    QueueOperationalStatus,
    QueueProgressRecord,
    SourceReference,
    StructuralProductAssembly,
    TransitionPathway,
    ValidatedFabricAssembler,
    ValidatedFabricEvaluator,
    ValidatedQueueBundler,
    ValidatedQueueEvaluator,
)


def _pathway() -> tuple[
    ProductPathway,
    QueueElement,
    QueueElement,
    PathwayRelationship,
]:
    token = IdentityToken("token-1")
    first_object = PathwayObject(
        object_id="queue-object-1",
        object_type="input_access",
        user_id="user-1",
        pathway_id="pathway-1",
    )
    second_object = PathwayObject(
        object_id="queue-object-2",
        object_type="delivery_access",
        user_id="user-1",
        pathway_id="pathway-1",
    )
    relationship = PathwayRelationship(
        relationship_id="relationship-1",
        relationship_type="depends_on",
        source_object_id=second_object.object_id,
        target_object_id=first_object.object_id,
        user_id="user-1",
        pathway_id="pathway-1",
    )
    first_queue = QueueElement(
        pathway_object=first_object,
        category=QueueCategory.FEEDSTOCK_AND_INPUT_ACCESS,
    )
    second_queue = QueueElement(
        pathway_object=second_object,
        category=QueueCategory.PRODUCT_OUTPUT_AND_DELIVERY_ACCESS,
    )
    pathway = ProductPathway(
        identity_token=token,
        evaluation_run_id="run-1",
        user_id="user-1",
        pathway_id="pathway-1",
        pathway_type="test",
        time_window=None,
        geographic_scope=None,
        system_scope=None,
        objects=(first_object, second_object),
        relationships=(relationship,),
        queue_elements=(first_queue, second_queue),
    )
    return pathway, first_queue, second_queue, relationship


def _bundles(
    pathway: ProductPathway,
    first_queue: QueueElement,
    second_queue: QueueElement,
    relationship: PathwayRelationship,
) -> tuple[ProductQueueBundle, ProductQueueBundle]:
    return (
        ProductQueueBundle(
            bundle_id="bundle-1",
            product_pathway=pathway,
            queue_elements=(first_queue,),
            relationships=(relationship,),
        ),
        ProductQueueBundle(
            bundle_id="bundle-2",
            product_pathway=pathway,
            queue_elements=(second_queue,),
            relationships=(relationship,),
        ),
    )


def _initial_result(pathway: ProductPathway) -> InitialCharterResult:
    source = SourceReference(reference_id="source-1")
    evaluation_run = EvaluationRun("run-1", pathway.identity_token.token_id)
    intake = ProductIntakeBundle(
        identity_token=pathway.identity_token,
        evaluation_run=evaluation_run,
        materials=(
            IntakeArtifact(
                artifact_id="artifact-1",
                media_type="text/plain",
                content="submitted material",
                provenance=(source,),
            ),
        ),
    )
    return InitialCharterResult(
        identity_token=pathway.identity_token,
        evaluation_run_id=evaluation_run.evaluation_run_id,
        adapter_result=ProductAdapterResult(pathway, intake, evaluation_run),
        check_results=(),
        evaluator_version="charter-v1",
        rule_set_version="charter-rules-v1",
        status="caller-established-valid-completion",
    )


def _queue_result(
    queue: ProductQueueBundle,
    transition: TransitionPathway,
    system_context: OpaqueReference | None,
    run_id: str = "run-1",
    include_progress: bool = True,
) -> QueueEvaluatorResult:
    pathway = queue.product_pathway
    progress = QueueProgressRecord(
        evaluated_queue=queue,
        evaluation_run_id=run_id,
        operational_status=QueueOperationalStatus.CLEAR,
        lifecycle_state=QueueLifecycleState.OPEN,
        ordering_status=None,
        synchronization_status=None,
        evaluation_position=0,
        user_id=pathway.user_id,
        pathway_id=pathway.pathway_id,
    )
    progress_records = (progress,) if include_progress else ()
    execution = QueueExecutionResult(
        evaluated_queue=queue,
        evaluation_run_id=run_id,
        execution_state="caller-defined-completion",
        progress_records=progress_records,
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
        progress_records=progress_records,
        transition_pathway=transition,
        evaluator_version="queue-v1",
        rule_set_version="queue-rules-v1",
        user_id=pathway.user_id,
        pathway_id=pathway.pathway_id,
    )


def test_assembly_preserves_pathway_owned_references_without_evaluation() -> None:
    pathway, first_queue, second_queue, relationship = _pathway()
    expected_bundles = _bundles(pathway, first_queue, second_queue, relationship)
    fabric = ProductFabric(
        fabric_id="fabric-1",
        coordination_function="caller-defined-coordination",
        product_pathway=pathway,
        queue_bundles=expected_bundles,
        relationships=(relationship,),
    )
    seen: list[object] = []

    def group(received_pathway: ProductPathway) -> tuple[ProductQueueBundle, ...]:
        seen.append(received_pathway)
        return expected_bundles

    def assemble_fabric(
        received_pathway: ProductPathway,
        received_bundles: tuple[ProductQueueBundle, ...],
    ) -> tuple[ProductFabric, ...]:
        seen.extend((received_pathway, received_bundles))
        return (fabric,)

    assembly = StructuralProductAssembly(
        queue_bundler=ValidatedQueueBundler(group),
        fabric_assembler=ValidatedFabricAssembler(assemble_fabric),
    )
    bundles, fabrics = assembly.assemble(_initial_result(pathway))

    assert bundles is expected_bundles
    assert fabrics == (fabric,)
    assert seen == [pathway, pathway, expected_bundles]
    assert not hasattr(assembly, "evaluate")
    with pytest.raises(FrozenInstanceError):
        bundles[0].bundle_id = "changed"  # type: ignore[misc]


def test_product_assembly_omits_fabrics_when_none_are_applicable() -> None:
    pathway, first_queue, second_queue, relationship = _pathway()
    expected_bundles = _bundles(pathway, first_queue, second_queue, relationship)
    assembly = StructuralProductAssembly(
        queue_bundler=ValidatedQueueBundler(lambda _: expected_bundles)
    )

    assert assembly.assemble(_initial_result(pathway)) == (expected_bundles, ())


def test_queue_bundler_rejects_elements_not_owned_by_pathway() -> None:
    pathway, _, _, _ = _pathway()
    foreign_object = PathwayObject(
        object_id="foreign",
        object_type="foreign",
        user_id=pathway.user_id,
        pathway_id="another-pathway",
    )
    foreign_queue = QueueElement(
        pathway_object=foreign_object,
        category=QueueCategory.UNCLASSIFIED,
    )
    invalid = ProductQueueBundle(
        bundle_id="invalid",
        product_pathway=pathway,
        queue_elements=(foreign_queue,),
    )

    with pytest.raises(AssemblyInvariantError, match="pathway queue elements"):
        ValidatedQueueBundler(lambda _: (invalid,)).bundle(pathway)


def test_fabric_assembler_rejects_unsupplied_or_single_bundle_membership() -> None:
    pathway, first_queue, second_queue, relationship = _pathway()
    bundles = _bundles(pathway, first_queue, second_queue, relationship)
    foreign_bundle = ProductQueueBundle(
        bundle_id="foreign",
        product_pathway=pathway,
        queue_elements=(first_queue,),
    )
    foreign_fabric = ProductFabric(
        fabric_id="foreign-fabric",
        coordination_function="caller-defined",
        product_pathway=pathway,
        queue_bundles=(bundles[0], foreign_bundle),
    )
    single_fabric = ProductFabric(
        fabric_id="single-fabric",
        coordination_function="caller-defined",
        product_pathway=pathway,
        queue_bundles=(bundles[0],),
    )

    with pytest.raises(AssemblyInvariantError, match="supplied queue bundles"):
        ValidatedFabricAssembler(lambda _pathway, _bundles: (foreign_fabric,)).assemble(
            pathway, bundles
        )
    with pytest.raises(AssemblyInvariantError, match="multiple queue bundles"):
        ValidatedFabricAssembler(lambda _pathway, _bundles: (single_fabric,)).assemble(
            pathway, bundles
        )


def test_queue_evaluator_routes_context_and_accepts_completed_result() -> None:
    pathway, first_queue, second_queue, relationship = _pathway()
    queue = _bundles(pathway, first_queue, second_queue, relationship)[0]
    transition = TransitionPathway(reference_id="transition-1")
    system_context = OpaqueReference(reference_id="system-1")
    direct = (ComparisonFinding("direct", "direct", "direct finding"),)
    downstream = (ComparisonFinding("downstream", "propagation", "downstream finding"),)
    expected = _queue_result(queue, transition, system_context)
    seen: list[object] = []

    def evaluate_queue(
        received_queue: QueueElement | ProductQueueBundle,
        received_pathway: ProductPathway,
        received_direct: tuple[ComparisonFinding, ...],
        received_downstream: tuple[ComparisonFinding, ...],
        received_transition: TransitionPathway,
        received_system: OpaqueReference | None,
        received_run: str,
    ) -> QueueEvaluatorResult | QueueEvaluationFailure:
        seen.extend(
            (
                received_queue,
                received_pathway,
                received_direct,
                received_downstream,
                received_transition,
                received_system,
                received_run,
            )
        )
        return expected

    result = ValidatedQueueEvaluator(evaluate_queue).evaluate(
        queue,
        pathway,
        direct,
        downstream,
        transition,
        system_context,
        "run-1",
    )

    assert result is expected
    assert seen == [
        queue,
        pathway,
        direct,
        downstream,
        transition,
        system_context,
        "run-1",
    ]


def test_queue_evaluator_accepts_completion_without_progress_records() -> None:
    pathway, first_queue, second_queue, relationship = _pathway()
    queue = _bundles(pathway, first_queue, second_queue, relationship)[0]
    transition = TransitionPathway(reference_id="transition-1")
    expected = _queue_result(queue, transition, None, include_progress=False)
    evaluator = ValidatedQueueEvaluator(
        lambda _queue, _pathway, _direct, _downstream, _transition, _system, _run: (
            expected
        )
    )

    result = evaluator.evaluate(queue, pathway, (), (), transition, None, "run-1")

    assert result is expected
    assert isinstance(result, QueueEvaluatorResult)
    assert result.progress_records == ()
    assert result.execution_result.progress_records == ()


def test_queue_evaluation_failure_remains_distinct_from_completion() -> None:
    pathway, first_queue, second_queue, relationship = _pathway()
    queue = _bundles(pathway, first_queue, second_queue, relationship)[0]
    transition = TransitionPathway(reference_id="transition-1")
    failure = QueueEvaluationFailure(
        evaluated_queue=queue,
        evaluation_run_id="run-1",
        user_id=pathway.user_id,
        pathway_id=pathway.pathway_id,
    )
    evaluator = ValidatedQueueEvaluator(
        lambda _queue, _pathway, _direct, _downstream, _transition, _system, _run: (
            failure
        )
    )

    result = evaluator.evaluate(queue, pathway, (), (), transition, None, "run-1")

    assert result is failure
    assert isinstance(result, QueueEvaluationFailure)
    assert not hasattr(result, "execution_result")


def test_queue_evaluator_rejects_malformed_completed_result() -> None:
    pathway, first_queue, second_queue, relationship = _pathway()
    queue = _bundles(pathway, first_queue, second_queue, relationship)[0]
    transition = TransitionPathway(reference_id="transition-1")
    valid = _queue_result(queue, transition, None)
    malformed_execution = QueueExecutionResult(
        evaluated_queue=queue,
        evaluation_run_id="different-run",
        execution_state=valid.execution_result.execution_state,
        progress_records=valid.execution_result.progress_records,
        user_id=valid.user_id,
        pathway_id=valid.pathway_id,
    )
    malformed = QueueEvaluatorResult(
        evaluated_queue=queue,
        evaluation_run_id=valid.evaluation_run_id,
        final_operational_status=valid.final_operational_status,
        final_lifecycle_state=valid.final_lifecycle_state,
        ordering_status=None,
        synchronization_status=None,
        evaluation_state=None,
        execution_result=malformed_execution,
        progress_records=valid.progress_records,
        transition_pathway=transition,
        evaluator_version=valid.evaluator_version,
        rule_set_version=valid.rule_set_version,
        user_id=valid.user_id,
        pathway_id=valid.pathway_id,
    )

    with pytest.raises(QueueEvaluationInvariantError, match="evaluation run"):
        ValidatedQueueEvaluator(
            lambda _queue, _pathway, _direct, _downstream, _transition, _system, _run: (
                malformed
            )
        ).evaluate(queue, pathway, (), (), transition, None, "run-1")


def test_fabric_evaluator_preserves_all_supplied_context() -> None:
    pathway, first_queue, second_queue, relationship = _pathway()
    bundles = _bundles(pathway, first_queue, second_queue, relationship)
    fabric = ProductFabric(
        fabric_id="fabric-1",
        coordination_function="caller-defined",
        product_pathway=pathway,
        queue_bundles=bundles,
        relationships=(relationship,),
    )
    transition = TransitionPathway(reference_id="transition-1")
    system_context = OpaqueReference(reference_id="fabric-system-1")
    queue_results = (
        _queue_result(bundles[0], transition, system_context),
        _queue_result(bundles[1], transition, system_context),
    )
    direct = (ComparisonFinding("direct", "direct", "direct finding"),)
    downstream = (ComparisonFinding("downstream", "propagation", "downstream finding"),)
    expected = FabricEvaluatorResult(
        product_fabric=fabric,
        queue_results=queue_results,
        pathway_comparison_findings=direct,
        downstream_propagation_findings=downstream,
        transition_pathway=transition,
        coordination_condition="caller-defined-condition",
        evaluator_version="fabric-v1",
        rule_set_version="fabric-rules-v1",
        evaluation_run_id="run-1",
        user_id=pathway.user_id,
        pathway_id=pathway.pathway_id,
        system_context=system_context,
    )
    seen: list[object] = []

    def evaluate_fabric(
        received_fabric: ProductFabric,
        received_results: tuple[QueueEvaluatorResult, ...],
        received_direct: tuple[ComparisonFinding, ...],
        received_downstream: tuple[ComparisonFinding, ...],
        received_transition: TransitionPathway,
        received_system: OpaqueReference | None,
        received_run: str,
    ) -> FabricEvaluatorResult:
        seen.extend(
            (
                received_fabric,
                received_results,
                received_direct,
                received_downstream,
                received_transition,
                received_system,
                received_run,
            )
        )
        return expected

    result = ValidatedFabricEvaluator(evaluate_fabric).evaluate(
        fabric,
        queue_results,
        direct,
        downstream,
        transition,
        system_context,
        "run-1",
    )

    assert result is expected
    assert seen == [
        fabric,
        queue_results,
        direct,
        downstream,
        transition,
        system_context,
        "run-1",
    ]
    assert result.system_context is system_context
    assert all(
        preserved is supplied
        for preserved, supplied in zip(result.queue_results, queue_results, strict=True)
    )


def test_fabric_evaluator_rejects_missing_participating_queue_result() -> None:
    pathway, first_queue, second_queue, relationship = _pathway()
    bundles = _bundles(pathway, first_queue, second_queue, relationship)
    fabric = ProductFabric(
        fabric_id="fabric-1",
        coordination_function="caller-defined",
        product_pathway=pathway,
        queue_bundles=bundles,
    )
    transition = TransitionPathway(reference_id="transition-1")
    one_result = (_queue_result(bundles[0], transition, None),)


    def fail_if_called(
        _fabric: ProductFabric,
        _results: tuple[QueueEvaluatorResult, ...],
        _direct: tuple[ComparisonFinding, ...],
        _downstream: tuple[ComparisonFinding, ...],
        _transition: TransitionPathway,
        _system: OpaqueReference | None,
        _run: str,
    ) -> FabricEvaluatorResult:
        pytest.fail("evaluation function must not run for invalid inputs")

    with pytest.raises(FabricEvaluationInvariantError, match="one result"):
        ValidatedFabricEvaluator(fail_if_called).evaluate(
            fabric,
            one_result,
            (),
            (),
            transition,
            None,
            "run-1",
        )
