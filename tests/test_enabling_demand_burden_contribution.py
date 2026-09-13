"""Focused enabling, dependency, demand, and transition-burden rule tests."""

from dataclasses import dataclass, fields, replace
from inspect import signature
from typing import cast, get_args, get_type_hints

import pytest

import climatesos.pathway_evaluation as pathway_evaluation
from climatesos.pathway_evaluation import (
    ComparisonFinding,
    ContributionFinding,
    DependencyBottleneckRuleFunction,
    DocumentationFinding,
    EnablingDemandBurdenEvaluationInvariantError,
    EnablingDemandBurdenFindingFunction,
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
    TransitionBurdenRuleFunction,
    TransitionDemandEffectRuleFunction,
    TransitionEnablingCapacityRuleFunction,
    TransitionPathway,
)


@dataclass(frozen=True, slots=True)
class _Artifacts:
    output: PathwayObject
    comparison: ComparisonFinding
    constrained_queue: QueueEvaluatorResult
    clear_queue: QueueEvaluatorResult
    fabric: FabricEvaluatorResult
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
        object_id="output-1",
        object_type="infrastructure demand resource claim",
        user_id="user-1",
        pathway_id="pathway-1",
    )
    workforce_object = PathwayObject(
        object_id="queue-1",
        object_type="enabling bottleneck workforce",
        user_id="user-1",
        pathway_id="pathway-1",
    )
    delivery_object = replace(workforce_object, object_id="queue-2")
    workforce_queue = QueueElement(
        workforce_object,
        QueueCategory.WORKFORCE_AND_EXECUTION,
    )
    delivery_queue = QueueElement(
        delivery_object,
        QueueCategory.PRODUCT_OUTPUT_AND_DELIVERY_ACCESS,
    )
    pathway = ProductPathway(
        identity_token=token,
        evaluation_run_id=run.evaluation_run_id,
        user_id="user-1",
        pathway_id="pathway-1",
        pathway_type="infrastructure demand and bottleneck pathway",
        time_window="2030",
        geographic_scope="local",
        system_scope="power",
        objects=(output, workforce_object, delivery_object),
        relationships=(),
        queue_elements=(workforce_queue, delivery_queue),
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
    system_context = OpaqueReference("system-1")
    constrained_bundle = ProductQueueBundle(
        "constrained-bundle",
        pathway,
        (workforce_queue,),
    )
    clear_bundle = ProductQueueBundle("clear-bundle", pathway, (delivery_queue,))

    def queue_result(
        bundle: ProductQueueBundle,
        status: QueueOperationalStatus,
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
            final_operational_status=status,
            final_lifecycle_state=QueueLifecycleState.OPEN,
            ordering_status=None,
            synchronization_status=None,
            evaluation_state=None,
            execution_result=execution,
            progress_records=(),
            transition_pathway=transition,
            evaluator_version="queue-1",
            rule_set_version="queue-rules-1",
            user_id=pathway.user_id,
            pathway_id=pathway.pathway_id,
            findings=("bottleneck demand infrastructure burden",),
        )

    constrained_queue = queue_result(
        constrained_bundle,
        QueueOperationalStatus.CONSTRAINED,
    )
    clear_queue = queue_result(clear_bundle, QueueOperationalStatus.CLEAR)
    comparison = ComparisonFinding(
        finding_id="comparison-1",
        finding_type="enabling demand burden claim",
        description="claims bottleneck relief and reduced infrastructure demand",
    )
    product_fabric = ProductFabric(
        fabric_id="fabric-1",
        coordination_function="enabling coordination",
        product_pathway=pathway,
        queue_bundles=(constrained_bundle, clear_bundle),
    )
    fabric = FabricEvaluatorResult(
        product_fabric=product_fabric,
        queue_results=(constrained_queue, clear_queue),
        pathway_comparison_findings=(comparison,),
        downstream_propagation_findings=(),
        transition_pathway=transition,
        coordination_condition="bottleneck resolved and capacity enabled",
        evaluator_version="fabric-1",
        rule_set_version="fabric-rules-1",
        evaluation_run_id=run.evaluation_run_id,
        user_id=pathway.user_id,
        pathway_id=pathway.pathway_id,
        system_context=system_context,
        findings=("resource burden shifted",),
    )
    documentation = DocumentationFinding(
        finding_id="documentation-1",
        subject_id=output.object_id,
        status="supported demand claim",
        description="claims enabling capacity and burden reduction",
    )
    engine = PathwayEngineResult(
        identity_token=token,
        product_pathway=pathway,
        transition_pathway=transition,
        initial_charter_result=initial,
        direct_comparison_findings=(comparison,),
        substitution_combination_findings=(),
        downstream_propagation_findings=(),
        queue_results=(constrained_queue, clear_queue),
        fabric_results=(fabric,),
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
        constrained_queue,
        clear_queue,
        fabric,
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
    enabling: _Rule,
    dependency: _Rule,
    demand: _Rule,
    burden: _Rule,
) -> EnablingDemandBurdenFindingFunction:
    return EnablingDemandBurdenFindingFunction(
        enabling,
        dependency,
        demand,
        burden,
    )


def test_rule_aliases_and_composer_have_exact_contracts() -> None:
    for rule_type in (
        TransitionEnablingCapacityRuleFunction,
        DependencyBottleneckRuleFunction,
        TransitionDemandEffectRuleFunction,
        TransitionBurdenRuleFunction,
    ):
        parameter_types, return_type = get_args(rule_type)
        assert parameter_types == [PathwayEngineResult, IntegratedCharterResult]
        assert return_type == tuple[ContributionFinding, ...]

    callable_hints = get_type_hints(EnablingDemandBurdenFindingFunction.__call__)
    assert callable_hints["return"] == tuple[ContributionFinding, ...]
    assert tuple(
        signature(EnablingDemandBurdenFindingFunction.__call__).parameters
    ) == ("self", "pathway_engine_result", "integrated_charter_result")
    assert {field.name for field in fields(EnablingDemandBurdenFindingFunction)} == {
        "enabling_capacity_rule",
        "dependency_bottleneck_rule",
        "demand_effect_rule",
        "transition_burden_rule",
    }


def test_rules_execute_once_with_exact_inputs_and_preserve_order() -> None:
    artifacts = _artifacts()
    later_id = _finding("z-enabling")
    earlier_id = _finding("a-enabling")
    dependency = _finding("dependency")
    demand = _finding("demand")
    burden = _finding("burden")
    enabling_rule = _Rule((later_id, earlier_id, later_id))
    dependency_rule = _Rule((dependency,))
    demand_rule = _Rule((demand,))
    burden_rule = _Rule((burden,))
    composer = _composer(
        enabling_rule,
        dependency_rule,
        demand_rule,
        burden_rule,
    )

    result = composer(artifacts.engine, artifacts.integrated)

    for rule in (enabling_rule, dependency_rule, demand_rule, burden_rule):
        assert rule.calls == [(artifacts.engine, artifacts.integrated)]
    assert result == (later_id, earlier_id, later_id, dependency, demand, burden)
    assert result[0] is result[2]
    assert not isinstance(result, NetOverallSystemContribution)


@pytest.mark.parametrize(
    "empty_rule",
    ("enabling", "dependency", "demand", "burden"),
)
def test_empty_tuple_from_each_rule_is_valid(empty_rule: str) -> None:
    artifacts = _artifacts()
    finding = _finding("preserved")
    enabling = _Rule(()) if empty_rule == "enabling" else _Rule((finding,))
    dependency = _Rule(()) if empty_rule == "dependency" else _Rule((finding,))
    demand = _Rule(()) if empty_rule == "demand" else _Rule((finding,))
    burden = _Rule(()) if empty_rule == "burden" else _Rule((finding,))

    result = _composer(enabling, dependency, demand, burden)(
        artifacts.engine,
        artifacts.integrated,
    )

    assert isinstance(result, tuple)


def test_all_empty_rules_return_an_empty_finding_tuple() -> None:
    artifacts = _artifacts()

    result = _composer(_Rule(()), _Rule(()), _Rule(()), _Rule(()))(
        artifacts.engine,
        artifacts.integrated,
    )

    assert result == ()


@pytest.mark.parametrize(
    "rule_name",
    ("enabling", "dependency", "demand", "burden"),
)
@pytest.mark.parametrize(
    "malformed",
    (None, [], _finding("single"), (_finding("valid"), object())),
)
def test_malformed_result_from_every_rule_position_rejects(
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
    enabling: TransitionEnablingCapacityRuleFunction = empty
    dependency: DependencyBottleneckRuleFunction = empty
    demand: TransitionDemandEffectRuleFunction = empty
    burden: TransitionBurdenRuleFunction = empty
    if rule_name == "enabling":
        enabling = cast(TransitionEnablingCapacityRuleFunction, malformed_rule)
    elif rule_name == "dependency":
        dependency = cast(DependencyBottleneckRuleFunction, malformed_rule)
    elif rule_name == "demand":
        demand = cast(TransitionDemandEffectRuleFunction, malformed_rule)
    else:
        burden = cast(TransitionBurdenRuleFunction, malformed_rule)
    composer = EnablingDemandBurdenFindingFunction(
        enabling,
        dependency,
        demand,
        burden,
    )

    with pytest.raises(EnablingDemandBurdenEvaluationInvariantError):
        composer(artifacts.engine, artifacts.integrated)


@pytest.mark.parametrize(
    "failed_rule",
    ("enabling", "dependency", "demand", "burden"),
)
def test_rule_exception_propagates_and_stops_later_rules(failed_rule: str) -> None:
    artifacts = _artifacts()
    calls: list[str] = []

    def rule(name: str) -> TransitionEnablingCapacityRuleFunction:
        def execute(
            _engine: PathwayEngineResult,
            _integrated: IntegratedCharterResult,
        ) -> tuple[ContributionFinding, ...]:
            calls.append(name)
            if name == failed_rule:
                raise RuntimeError(f"{name} failed")
            return ()

        return execute

    composer = EnablingDemandBurdenFindingFunction(
        rule("enabling"),
        rule("dependency"),
        rule("demand"),
        rule("burden"),
    )

    with pytest.raises(RuntimeError, match=f"{failed_rule} failed"):
        composer(artifacts.engine, artifacts.integrated)

    expected_calls = {
        "enabling": ["enabling"],
        "dependency": ["enabling", "dependency"],
        "demand": ["enabling", "dependency", "demand"],
        "burden": ["enabling", "dependency", "demand", "burden"],
    }
    assert calls == expected_calls[failed_rule]


def test_suggestive_upstream_states_categories_and_text_do_not_infer_findings() -> None:
    artifacts = _artifacts()

    assert artifacts.constrained_queue.final_operational_status is (
        QueueOperationalStatus.CONSTRAINED
    )
    assert artifacts.clear_queue.final_operational_status is (
        QueueOperationalStatus.CLEAR
    )
    constrained_subject = artifacts.constrained_queue.evaluated_queue
    assert isinstance(constrained_subject, ProductQueueBundle)
    assert (
        constrained_subject.queue_elements[0].category
        is QueueCategory.WORKFORCE_AND_EXECUTION
    )

    result = _composer(_Rule(()), _Rule(()), _Rule(()), _Rule(()))(
        artifacts.engine,
        artifacts.integrated,
    )

    assert result == ()


def test_only_explicit_rule_findings_appear() -> None:
    artifacts = _artifacts()
    explicit = _finding("explicit")

    result = _composer(_Rule(()), _Rule(()), _Rule((explicit,)), _Rule(()))(
        artifacts.engine,
        artifacts.integrated,
    )

    assert result == (explicit,)
    assert result[0] is explicit


def test_open_ended_substantive_findings_are_preserved_unchanged() -> None:
    artifacts = _artifacts()
    limited = _finding("limited", ("limited enabling",))
    conditional = _finding("conditional", ("conditional enabling",))
    unresolved_enabling = _finding("unresolved-enabling", ("caller unresolved",))
    relief = _finding("relief", ("caller bottleneck relief",))
    worsening = _finding("worsening", ("caller bottleneck worsening",))
    shifted = _finding("shifted", ("shifted unresolved constraint",))
    added_demand = _finding("added-demand", ("caller additional demand",))
    avoided_demand = _finding("avoided-demand", ("caller avoided demand",))
    unresolved_demand = _finding("unresolved-demand", ("conditional demand",))
    burden = _finding("burden", ("caller additional burden",))
    reduced_burden = _finding("reduced-burden", ("caller shifted burden",))
    adverse = _finding("adverse", ("unresolved adverse burden",))
    expected = (
        limited,
        conditional,
        unresolved_enabling,
        relief,
        worsening,
        shifted,
        added_demand,
        avoided_demand,
        unresolved_demand,
        burden,
        reduced_burden,
        adverse,
    )
    composer = _composer(
        _Rule(expected[:3]),
        _Rule(expected[3:6]),
        _Rule(expected[6:9]),
        _Rule(expected[9:]),
    )

    result = composer(artifacts.engine, artifacts.integrated)

    assert result == expected
    assert all(
        actual is supplied
        for actual, supplied in zip(result, expected, strict=True)
    )


def test_findings_preserve_distinct_material_upstream_subsets() -> None:
    artifacts = _artifacts()
    enabling = replace(
        _finding("enabling"),
        supporting_queue_results=(artifacts.constrained_queue,),
    )
    bottleneck = replace(
        _finding("bottleneck"),
        supporting_queue_results=(artifacts.clear_queue,),
        supporting_fabric_results=(artifacts.fabric,),
    )
    demand = replace(
        _finding("demand"),
        pathway_output_references=(artifacts.output,),
        supporting_comparison_findings=(artifacts.comparison,),
    )
    burden = replace(
        _finding("burden"),
        supporting_documentation_findings=(artifacts.documentation,),
        supporting_system_references=(OpaqueReference("system-burden-1"),),
    )

    result = _composer(
        _Rule((enabling,)),
        _Rule((bottleneck,)),
        _Rule((demand,)),
        _Rule((burden,)),
    )(artifacts.engine, artifacts.integrated)

    assert result == (enabling, bottleneck, demand, burden)
    assert enabling.supporting_queue_results[0] is artifacts.constrained_queue
    assert bottleneck.supporting_queue_results[0] is artifacts.clear_queue
    assert bottleneck.supporting_fabric_results[0] is artifacts.fabric
    assert demand.pathway_output_references[0] is artifacts.output
    assert demand.supporting_comparison_findings[0] is artifacts.comparison
    assert burden.supporting_documentation_findings[0] is artifacts.documentation
    assert burden.supporting_system_references


def test_no_subrecords_deferred_domains_scale_or_scalar_fields_are_added() -> None:
    finding_fields = {field.name for field in fields(ContributionFinding)}
    composer_fields = {
        field.name for field in fields(EnablingDemandBurdenFindingFunction)
    }
    forbidden_exports = (
        "EmissionsAccountingRuleFunction",
        "CDRRuleFunction",
        "BiosphereContributionEvaluator",
        "ScaleFinding",
        "ScaleDiagnosticResult",
    )

    assert all(not hasattr(pathway_evaluation, name) for name in forbidden_exports)
    assert {
        "queue_execution_results",
        "queue_progress_records",
        "supporting_queue_execution_results",
        "supporting_queue_progress_records",
    }.isdisjoint(finding_fields)
    assert {
        "replication",
        "scale_threshold",
        "score",
        "rank",
        "weight",
        "votes",
    }.isdisjoint(composer_fields | finding_fields)
