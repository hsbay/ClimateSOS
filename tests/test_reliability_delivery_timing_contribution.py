"""Focused reliability, deliverability, and transition-timing rule tests."""

from dataclasses import dataclass, fields, replace
from inspect import signature
from typing import cast, get_args, get_type_hints

import pytest

import climatesos.pathway_evaluation as pathway_evaluation
from climatesos.pathway_evaluation import (
    ComparisonFinding,
    ContributionFinding,
    DeliverabilitySynchronizationRuleFunction,
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
    QueueOrderingStatus,
    QueueSynchronizationStatus,
    ReliabilityAdequacyRuleFunction,
    ReliabilityDeliveryTimingEvaluationInvariantError,
    ReliabilityDeliveryTimingFindingFunction,
    TransitionPathway,
    TransitionTimingRuleFunction,
)


@dataclass(frozen=True, slots=True)
class _Artifacts:
    output: PathwayObject
    comparison: ComparisonFinding
    clear_queue_result: QueueEvaluatorResult
    delayed_queue_result: QueueEvaluatorResult
    fabric_result: FabricEvaluatorResult
    documentation: DocumentationFinding
    engine: PathwayEngineResult
    integrated: IntegratedCharterResult


class _Rule:
    def __init__(self, findings: tuple[ContributionFinding, ...]) -> None:
        self.findings = findings
        self.calls: list[
            tuple[PathwayEngineResult, IntegratedCharterResult]
        ] = []

    def __call__(
        self,
        engine: PathwayEngineResult,
        integrated: IntegratedCharterResult,
    ) -> tuple[ContributionFinding, ...]:
        self.calls.append((engine, integrated))
        return self.findings


def _artifacts() -> _Artifacts:
    token = IdentityToken("token-1")
    run = EvaluationRun("run-1", token.token_id)
    intake = ProductIntakeBundle(token, run, ())
    output = PathwayObject(
        object_id="clean-output-1",
        object_type="reliable clean delivery claim",
        user_id="user-1",
        pathway_id="pathway-1",
    )
    first_queue_object = PathwayObject(
        object_id="queue-1",
        object_type="delivery queue",
        user_id="user-1",
        pathway_id="pathway-1",
    )
    second_queue_object = replace(first_queue_object, object_id="queue-2")
    first_queue = QueueElement(
        first_queue_object,
        QueueCategory.PRODUCT_OUTPUT_AND_DELIVERY_ACCESS,
    )
    second_queue = QueueElement(
        second_queue_object,
        QueueCategory.PERMITTING_AND_AUTHORIZATION,
    )
    pathway = ProductPathway(
        identity_token=token,
        evaluation_run_id=run.evaluation_run_id,
        user_id="user-1",
        pathway_id="pathway-1",
        pathway_type="clean reliable synchronized pathway",
        time_window="2036 after required 2032 window",
        geographic_scope="local",
        system_scope="power",
        objects=(output, first_queue_object, second_queue_object),
        relationships=(),
        queue_elements=(first_queue, second_queue),
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
    transition = TransitionPathway("transition-with-2032-window")
    system_context = OpaqueReference("system-1")
    first_bundle = ProductQueueBundle("bundle-1", pathway, (first_queue,))
    second_bundle = ProductQueueBundle("bundle-2", pathway, (second_queue,))

    def queue_result(
        bundle: ProductQueueBundle,
        operational_status: QueueOperationalStatus,
        synchronization_status: QueueSynchronizationStatus,
    ) -> QueueEvaluatorResult:
        execution = QueueExecutionResult(
            evaluated_queue=bundle,
            evaluation_run_id=run.evaluation_run_id,
            execution_state="completed",
            progress_records=(),
            user_id=pathway.user_id,
            pathway_id=pathway.pathway_id,
            transition_pathway=transition,
            system_context=system_context,
        )
        return QueueEvaluatorResult(
            evaluated_queue=bundle,
            evaluation_run_id=run.evaluation_run_id,
            final_operational_status=operational_status,
            final_lifecycle_state=QueueLifecycleState.OPEN,
            ordering_status=QueueOrderingStatus.ORDERED,
            synchronization_status=synchronization_status,
            evaluation_state=None,
            execution_result=execution,
            progress_records=(),
            transition_pathway=transition,
            evaluator_version="queue-1",
            rule_set_version="queue-rules-1",
            user_id=pathway.user_id,
            pathway_id=pathway.pathway_id,
            findings=("arbitrary queue timing text",),
        )

    clear_queue_result = queue_result(
        first_bundle,
        QueueOperationalStatus.CLEAR,
        QueueSynchronizationStatus.SYNCHRONIZED,
    )
    delayed_queue_result = queue_result(
        second_bundle,
        QueueOperationalStatus.DELAYED,
        QueueSynchronizationStatus.UNSYNCHRONIZED,
    )
    comparison = ComparisonFinding(
        finding_id="comparison-1",
        finding_type="caller-defined adequacy claim",
        description="claims reliable and timely delivery",
    )
    fabric = ProductFabric(
        fabric_id="fabric-1",
        coordination_function="delivery coordination",
        product_pathway=pathway,
        queue_bundles=(first_bundle, second_bundle),
    )
    fabric_result = FabricEvaluatorResult(
        product_fabric=fabric,
        queue_results=(clear_queue_result, delayed_queue_result),
        pathway_comparison_findings=(comparison,),
        downstream_propagation_findings=(),
        transition_pathway=transition,
        coordination_condition="perfectly coordinated claim",
        evaluator_version="fabric-1",
        rule_set_version="fabric-rules-1",
        evaluation_run_id=run.evaluation_run_id,
        user_id=pathway.user_id,
        pathway_id=pathway.pathway_id,
        system_context=system_context,
        findings=("arbitrary synchronized delivery text",),
    )
    documentation = DocumentationFinding(
        finding_id="documentation-1",
        subject_id=output.object_id,
        status="caller-defined",
        description="claims adequate reliability within the transition window",
    )
    engine = PathwayEngineResult(
        identity_token=token,
        product_pathway=pathway,
        transition_pathway=transition,
        initial_charter_result=initial,
        direct_comparison_findings=(comparison,),
        substitution_combination_findings=(),
        downstream_propagation_findings=(),
        queue_results=(clear_queue_result, delayed_queue_result),
        fabric_results=(fabric_result,),
        documentation_findings=(documentation,),
        evaluation_run_id=run.evaluation_run_id,
        system_context=system_context,
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
    return _Artifacts(
        output,
        comparison,
        clear_queue_result,
        delayed_queue_result,
        fabric_result,
        documentation,
        engine,
        integrated,
    )


def _finding(
    finding_id: str,
    statuses: tuple[str, ...] = ("caller-defined",),
) -> ContributionFinding:
    return ContributionFinding(
        finding_id=finding_id,
        effect_description=f"effect-{finding_id}",
        contribution_statuses=statuses,
    )


def _composer(
    reliability: _Rule,
    deliverability: _Rule,
    timing: _Rule,
) -> ReliabilityDeliveryTimingFindingFunction:
    return ReliabilityDeliveryTimingFindingFunction(
        reliability,
        deliverability,
        timing,
    )


def test_rule_aliases_and_finding_composer_have_exact_contracts() -> None:
    for rule_type in (
        ReliabilityAdequacyRuleFunction,
        DeliverabilitySynchronizationRuleFunction,
        TransitionTimingRuleFunction,
    ):
        parameter_types, return_type = get_args(rule_type)
        assert parameter_types == [PathwayEngineResult, IntegratedCharterResult]
        assert return_type == tuple[ContributionFinding, ...]

    callable_hints = get_type_hints(ReliabilityDeliveryTimingFindingFunction.__call__)
    assert callable_hints["return"] == tuple[ContributionFinding, ...]
    assert tuple(
        signature(ReliabilityDeliveryTimingFindingFunction.__call__).parameters
    ) == ("self", "pathway_engine_result", "integrated_charter_result")
    composer_fields = {
        field.name for field in fields(ReliabilityDeliveryTimingFindingFunction)
    }
    assert composer_fields == {
        "reliability_adequacy_rule",
        "deliverability_synchronization_rule",
        "transition_timing_rule",
    }


def test_rules_execute_once_with_exact_inputs_and_preserve_order() -> None:
    artifacts = _artifacts()
    later_id = _finding("z-reliability")
    earlier_id = _finding("a-reliability")
    delivery = _finding("delivery")
    timing = _finding("timing")
    reliability_rule = _Rule((later_id, earlier_id, later_id))
    delivery_rule = _Rule((delivery,))
    timing_rule = _Rule((timing,))
    composer = _composer(reliability_rule, delivery_rule, timing_rule)

    result = composer(artifacts.engine, artifacts.integrated)

    for rule in (reliability_rule, delivery_rule, timing_rule):
        assert rule.calls == [(artifacts.engine, artifacts.integrated)]
    assert result == (later_id, earlier_id, later_id, delivery, timing)
    assert result[0] is result[2]
    assert not isinstance(result, NetOverallSystemContribution)


@pytest.mark.parametrize("empty_rule", ("reliability", "delivery", "timing"))
def test_empty_tuple_from_each_rule_is_valid(empty_rule: str) -> None:
    artifacts = _artifacts()
    finding = _finding("preserved")
    reliability = _Rule(()) if empty_rule == "reliability" else _Rule((finding,))
    delivery = _Rule(()) if empty_rule == "delivery" else _Rule((finding,))
    timing = _Rule(()) if empty_rule == "timing" else _Rule((finding,))

    result = _composer(reliability, delivery, timing)(
        artifacts.engine,
        artifacts.integrated,
    )

    assert isinstance(result, tuple)


def test_all_empty_rules_return_an_empty_finding_tuple() -> None:
    artifacts = _artifacts()

    result = _composer(_Rule(()), _Rule(()), _Rule(()))(
        artifacts.engine,
        artifacts.integrated,
    )

    assert result == ()


@pytest.mark.parametrize("rule_name", ("reliability", "delivery", "timing"))
@pytest.mark.parametrize(
    "malformed",
    (None, [], _finding("single"), (_finding("valid"), object())),
)
def test_malformed_result_from_any_rule_rejects(
    rule_name: str,
    malformed: object,
) -> None:
    artifacts = _artifacts()

    def malformed_rule(
        _engine: PathwayEngineResult,
        _integrated: IntegratedCharterResult,
    ) -> object:
        return malformed

    empty = _Rule(())
    reliability: ReliabilityAdequacyRuleFunction = empty
    delivery: DeliverabilitySynchronizationRuleFunction = empty
    timing: TransitionTimingRuleFunction = empty
    if rule_name == "reliability":
        reliability = cast(ReliabilityAdequacyRuleFunction, malformed_rule)
    elif rule_name == "delivery":
        delivery = cast(DeliverabilitySynchronizationRuleFunction, malformed_rule)
    else:
        timing = cast(TransitionTimingRuleFunction, malformed_rule)
    composer = ReliabilityDeliveryTimingFindingFunction(
        reliability,
        delivery,
        timing,
    )

    with pytest.raises(ReliabilityDeliveryTimingEvaluationInvariantError):
        composer(artifacts.engine, artifacts.integrated)


@pytest.mark.parametrize("failed_rule", ("reliability", "delivery", "timing"))
def test_rule_exception_propagates_and_stops_later_rules(failed_rule: str) -> None:
    artifacts = _artifacts()
    calls: list[str] = []

    def rule(name: str) -> ReliabilityAdequacyRuleFunction:
        def execute(
            _engine: PathwayEngineResult,
            _integrated: IntegratedCharterResult,
        ) -> tuple[ContributionFinding, ...]:
            calls.append(name)
            if name == failed_rule:
                raise RuntimeError(f"{name} failed")
            return ()

        return execute

    composer = ReliabilityDeliveryTimingFindingFunction(
        rule("reliability"),
        rule("delivery"),
        rule("timing"),
    )

    with pytest.raises(RuntimeError, match=f"{failed_rule} failed"):
        composer(artifacts.engine, artifacts.integrated)

    expected_calls = {
        "reliability": ["reliability"],
        "delivery": ["reliability", "delivery"],
        "timing": ["reliability", "delivery", "timing"],
    }
    assert calls == expected_calls[failed_rule]


def test_suggestive_upstream_states_and_text_do_not_generate_findings() -> None:
    artifacts = _artifacts()
    assert artifacts.clear_queue_result.final_operational_status is (
        QueueOperationalStatus.CLEAR
    )
    assert artifacts.clear_queue_result.synchronization_status is (
        QueueSynchronizationStatus.SYNCHRONIZED
    )
    assert artifacts.delayed_queue_result.final_operational_status is (
        QueueOperationalStatus.DELAYED
    )
    assert artifacts.delayed_queue_result.synchronization_status is (
        QueueSynchronizationStatus.UNSYNCHRONIZED
    )

    result = _composer(_Rule(()), _Rule(()), _Rule(()))(
        artifacts.engine,
        artifacts.integrated,
    )

    assert result == ()


def test_only_explicit_rule_findings_appear() -> None:
    artifacts = _artifacts()
    explicit = _finding("explicit")

    result = _composer(_Rule(()), _Rule((explicit,)), _Rule(()))(
        artifacts.engine,
        artifacts.integrated,
    )

    assert result == (explicit,)
    assert result[0] is explicit


def test_open_ended_substantive_findings_are_preserved_unchanged() -> None:
    artifacts = _artifacts()
    limited = _finding("limited", ("limited reliability",))
    adequacy = _finding("adequacy", ("unresolved adequacy",))
    infrastructure = _finding("infrastructure", ("dependency remains",))
    synchronization = _finding("synchronization", ("unresolved coordination",))
    delayed = _finding("delayed", ("caller timing constraint",))
    outside_window = _finding("outside-window", ("caller window mismatch",))
    adverse = _finding("adverse", ("caller adverse timing effect",))
    composer = _composer(
        _Rule((limited, adequacy)),
        _Rule((infrastructure, synchronization)),
        _Rule((delayed, outside_window, adverse)),
    )

    result = composer(artifacts.engine, artifacts.integrated)

    expected = (
        limited,
        adequacy,
        infrastructure,
        synchronization,
        delayed,
        outside_window,
        adverse,
    )
    assert result == expected
    assert all(
        actual is supplied
        for actual, supplied in zip(result, expected, strict=True)
    )


def test_findings_preserve_distinct_material_upstream_subsets() -> None:
    artifacts = _artifacts()
    reliability = replace(
        _finding("reliability"),
        supporting_queue_results=(artifacts.clear_queue_result,),
    )
    deliverability = replace(
        _finding("deliverability"),
        supporting_queue_results=(artifacts.delayed_queue_result,),
    )
    synchronization = replace(
        _finding("synchronization"),
        supporting_fabric_results=(artifacts.fabric_result,),
    )
    timing = replace(
        _finding("timing"),
        supporting_comparison_findings=(artifacts.comparison,),
        transition_function_references=(OpaqueReference("transition-time-1"),),
        supporting_system_references=(OpaqueReference("system-time-1"),),
    )

    result = _composer(
        _Rule((reliability,)),
        _Rule((deliverability, synchronization)),
        _Rule((timing,)),
    )(artifacts.engine, artifacts.integrated)

    assert result == (reliability, deliverability, synchronization, timing)
    assert reliability.supporting_queue_results[0] is artifacts.clear_queue_result
    assert deliverability.supporting_queue_results[0] is (
        artifacts.delayed_queue_result
    )
    assert synchronization.supporting_fabric_results[0] is artifacts.fabric_result
    assert timing.supporting_comparison_findings[0] is artifacts.comparison
    assert timing.transition_function_references
    assert timing.supporting_system_references


def test_no_queue_subrecords_scale_models_or_scaling_fields_are_added() -> None:
    finding_fields = {field.name for field in fields(ContributionFinding)}
    composer_fields = {
        field.name for field in fields(ReliabilityDeliveryTimingFindingFunction)
    }

    assert {
        "queue_execution_results",
        "queue_progress_records",
        "supporting_queue_execution_results",
        "supporting_queue_progress_records",
    }.isdisjoint(finding_fields)
    assert not hasattr(pathway_evaluation, "ScaleFinding")
    assert not hasattr(pathway_evaluation, "ScaleDiagnosticResult")
    assert {
        "scale",
        "replication",
        "score",
        "rank",
        "weight",
        "votes",
    }.isdisjoint(composer_fields | finding_fields)
