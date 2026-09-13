"""Focused fossil-displacement contribution rule-composition tests."""

from dataclasses import dataclass, fields, replace
from inspect import signature
from typing import cast, get_args, get_type_hints

import pytest

from climatesos.pathway_evaluation import (
    ComparisonFinding,
    ContributionFinding,
    DocumentationFinding,
    EvaluationRun,
    FabricEvaluatorResult,
    FossilDisplacementContributionFunction,
    FossilDisplacementEvaluationInvariantError,
    FossilDisplacementRuleFunction,
    FossilFunctionClosureRuleFunction,
    FossilPersistenceClosureRuleFunction,
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
    QueueProgressRecord,
    SourceReference,
    TransitionPathway,
    ValidatedNetOverallSystemContributionEvaluator,
)


@dataclass(frozen=True, slots=True)
class _Artifacts:
    pathway: ProductPathway
    comparison: ComparisonFinding
    queue_result: QueueEvaluatorResult
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


def _artifacts(
    *,
    pathway_type: str = "caller-defined",
    object_type: str = "caller-defined",
    comparison_description: str = "caller-defined comparison",
    documentation_description: str = "caller-defined documentation",
) -> _Artifacts:
    token = IdentityToken("token-1")
    run = EvaluationRun("run-1", token.token_id)
    intake = ProductIntakeBundle(token, run, ())
    output = PathwayObject(
        object_id="output-1",
        object_type=object_type,
        user_id="user-1",
        pathway_id="pathway-1",
    )
    queue_object = PathwayObject(
        object_id="queue-1",
        object_type="delivery",
        user_id="user-1",
        pathway_id="pathway-1",
    )
    queue_element = QueueElement(
        queue_object,
        QueueCategory.PRODUCT_OUTPUT_AND_DELIVERY_ACCESS,
    )
    pathway = ProductPathway(
        identity_token=token,
        evaluation_run_id=run.evaluation_run_id,
        user_id="user-1",
        pathway_id="pathway-1",
        pathway_type=pathway_type,
        time_window="2030",
        geographic_scope="local",
        system_scope="power",
        objects=(output, queue_object),
        relationships=(),
        queue_elements=(queue_element,),
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
    bundle = ProductQueueBundle(
        bundle_id="bundle-1",
        product_pathway=pathway,
        queue_elements=(queue_element,),
    )
    progress = QueueProgressRecord(
        evaluated_queue=bundle,
        evaluation_run_id=run.evaluation_run_id,
        operational_status=QueueOperationalStatus.CLEAR,
        lifecycle_state=QueueLifecycleState.OPEN,
        ordering_status=None,
        synchronization_status=None,
        evaluation_position=0,
        user_id=pathway.user_id,
        pathway_id=pathway.pathway_id,
    )
    execution = QueueExecutionResult(
        evaluated_queue=bundle,
        evaluation_run_id=run.evaluation_run_id,
        execution_state="completed",
        progress_records=(progress,),
        user_id=pathway.user_id,
        pathway_id=pathway.pathway_id,
        transition_pathway=transition,
        system_context=system_context,
    )
    queue_result = QueueEvaluatorResult(
        evaluated_queue=bundle,
        evaluation_run_id=run.evaluation_run_id,
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
        finding_type="caller-defined",
        description=comparison_description,
    )
    fabric = ProductFabric(
        fabric_id="fabric-1",
        coordination_function="caller-defined",
        product_pathway=pathway,
        queue_bundles=(bundle,),
    )
    fabric_result = FabricEvaluatorResult(
        product_fabric=fabric,
        queue_results=(queue_result,),
        pathway_comparison_findings=(comparison,),
        downstream_propagation_findings=(),
        transition_pathway=transition,
        coordination_condition="caller-defined",
        evaluator_version="fabric-1",
        rule_set_version="fabric-rules-1",
        evaluation_run_id=run.evaluation_run_id,
        user_id=pathway.user_id,
        pathway_id=pathway.pathway_id,
        system_context=system_context,
    )
    documentation = DocumentationFinding(
        finding_id="documentation-1",
        subject_id=output.object_id,
        status="caller-defined",
        description=documentation_description,
    )
    engine = PathwayEngineResult(
        identity_token=token,
        product_pathway=pathway,
        transition_pathway=transition,
        initial_charter_result=initial,
        direct_comparison_findings=(comparison,),
        substitution_combination_findings=(),
        downstream_propagation_findings=(),
        queue_results=(queue_result,),
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
        pathway,
        comparison,
        queue_result,
        fabric_result,
        documentation,
        engine,
        integrated,
    )


def _finding(
    finding_id: str,
    statuses: tuple[str, ...] = ("caller-defined",),
    **changes: object,
) -> ContributionFinding:
    finding = ContributionFinding(
        finding_id=finding_id,
        effect_description=f"effect-{finding_id}",
        contribution_statuses=statuses,
    )
    if not changes:
        return finding
    return replace(finding, **changes)  # type: ignore[arg-type]


def _composer(
    displacement: _Rule,
    function_closure: _Rule,
    persistence_closure: _Rule,
) -> FossilDisplacementContributionFunction:
    return FossilDisplacementContributionFunction(
        displacement_rule=displacement,
        function_closure_rule=function_closure,
        persistence_closure_rule=persistence_closure,
        evaluator_version="fossil-1",
        rule_set_version="fossil-rules-1",
        assumptions=("configured assumption",),
        uncertainties=("configured uncertainty",),
        evidence_references=(SourceReference("result-evidence-1"),),
        provenance=(SourceReference("result-provenance-1"),),
    )


def test_rule_types_and_concrete_callable_have_exact_contracts() -> None:
    for rule_type in (
        FossilDisplacementRuleFunction,
        FossilFunctionClosureRuleFunction,
        FossilPersistenceClosureRuleFunction,
    ):
        parameter_types, return_type = get_args(rule_type)
        assert parameter_types == [PathwayEngineResult, IntegratedCharterResult]
        assert return_type == tuple[ContributionFinding, ...]

    parameter_names = signature(FossilDisplacementContributionFunction.__call__)
    callable_hints = get_type_hints(FossilDisplacementContributionFunction.__call__)
    assert tuple(parameter_names.parameters) == (
        "self",
        "pathway_engine_result",
        "integrated_charter_result",
    )
    assert callable_hints == {
        "pathway_engine_result": PathwayEngineResult,
        "integrated_charter_result": IntegratedCharterResult,
        "return": NetOverallSystemContribution,
    }
    assert {field.name for field in fields(FossilDisplacementContributionFunction)} == {
        "displacement_rule",
        "function_closure_rule",
        "persistence_closure_rule",
        "evaluator_version",
        "rule_set_version",
        "assumptions",
        "uncertainties",
        "evidence_references",
        "provenance",
    }


def test_rules_execute_once_with_exact_inputs_and_preserve_order() -> None:
    artifacts = _artifacts()
    later_id = _finding("z-displacement")
    earlier_id = _finding("a-displacement")
    function_finding = _finding("function")
    persistence_finding = _finding("persistence")
    displacement = _Rule((later_id, earlier_id, later_id))
    function_closure = _Rule((function_finding,))
    persistence_closure = _Rule((persistence_finding,))
    composer = _composer(displacement, function_closure, persistence_closure)

    result = composer(artifacts.engine, artifacts.integrated)

    for rule in (displacement, function_closure, persistence_closure):
        assert rule.calls == [(artifacts.engine, artifacts.integrated)]
    assert result.contribution_findings == (
        later_id,
        earlier_id,
        later_id,
        function_finding,
        persistence_finding,
    )
    assert result.contribution_findings[0] is result.contribution_findings[2]


def test_result_preserves_upstream_identity_attribution_and_metadata() -> None:
    artifacts = _artifacts()
    composer = _composer(_Rule(()), _Rule(()), _Rule(()))

    result = composer(artifacts.engine, artifacts.integrated)

    assert result.product_pathway is artifacts.pathway
    assert result.pathway_engine_result is artifacts.engine
    assert result.integrated_charter_result is artifacts.integrated
    assert result.transition_pathway is artifacts.engine.transition_pathway
    assert result.evaluation_run_id == artifacts.engine.evaluation_run_id
    assert result.user_id == artifacts.engine.user_id
    assert result.pathway_id == artifacts.engine.pathway_id
    assert result.evaluator_version == "fossil-1"
    assert result.rule_set_version == "fossil-rules-1"
    assert result.assumptions == ("configured assumption",)
    assert result.uncertainties == ("configured uncertainty",)
    assert result.evidence_references == (SourceReference("result-evidence-1"),)
    assert result.provenance == (SourceReference("result-provenance-1"),)


@pytest.mark.parametrize("empty_rule", ("displacement", "function", "persistence"))
def test_an_empty_tuple_from_any_rule_is_valid(empty_rule: str) -> None:
    artifacts = _artifacts()
    finding = _finding("preserved")
    displacement = _Rule(()) if empty_rule == "displacement" else _Rule((finding,))
    function = _Rule(()) if empty_rule == "function" else _Rule((finding,))
    persistence = _Rule(()) if empty_rule == "persistence" else _Rule((finding,))

    result = _composer(displacement, function, persistence)(
        artifacts.engine,
        artifacts.integrated,
    )

    assert isinstance(result, NetOverallSystemContribution)


def test_all_empty_rules_produce_empty_contribution_findings() -> None:
    artifacts = _artifacts()

    result = _composer(_Rule(()), _Rule(()), _Rule(()))(
        artifacts.engine,
        artifacts.integrated,
    )

    assert result.contribution_findings == ()


@pytest.mark.parametrize("rule_name", ("displacement", "function", "persistence"))
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
    displacement: FossilDisplacementRuleFunction = empty
    function: FossilFunctionClosureRuleFunction = empty
    persistence: FossilPersistenceClosureRuleFunction = empty
    if rule_name == "displacement":
        displacement = cast(FossilDisplacementRuleFunction, malformed_rule)
    elif rule_name == "function":
        function = cast(FossilFunctionClosureRuleFunction, malformed_rule)
    else:
        persistence = cast(FossilPersistenceClosureRuleFunction, malformed_rule)
    composer = FossilDisplacementContributionFunction(
        displacement,
        function,
        persistence,
        "fossil-1",
        "fossil-rules-1",
    )

    with pytest.raises(FossilDisplacementEvaluationInvariantError):
        composer(artifacts.engine, artifacts.integrated)


def test_rule_exception_propagates_without_an_unresolved_result() -> None:
    artifacts = _artifacts()

    def fail(
        _engine: PathwayEngineResult,
        _integrated: IntegratedCharterResult,
    ) -> tuple[ContributionFinding, ...]:
        raise RuntimeError("rule failed")

    composer = FossilDisplacementContributionFunction(
        _Rule(()),
        fail,
        _Rule((_finding("must-not-run"),)),
        "fossil-1",
        "fossil-rules-1",
    )

    with pytest.raises(RuntimeError, match="rule failed"):
        composer(artifacts.engine, artifacts.integrated)


@pytest.mark.parametrize(
    ("pathway_type", "object_type", "comparison_text", "documentation_text"),
    (
        (
            "clean replacement technology",
            "solar fossil substitute",
            "claims complete fossil displacement",
            "claims positive emissions and commercial performance",
        ),
        (
            "fossil persistence",
            "theoretical substitute",
            "says no displacement",
            "says activity is additional",
        ),
    ),
)
def test_suggestive_labels_and_descriptions_do_not_generate_findings(
    pathway_type: str,
    object_type: str,
    comparison_text: str,
    documentation_text: str,
) -> None:
    artifacts = _artifacts(
        pathway_type=pathway_type,
        object_type=object_type,
        comparison_description=comparison_text,
        documentation_description=documentation_text,
    )

    result = _composer(_Rule(()), _Rule(()), _Rule(()))(
        artifacts.engine,
        artifacts.integrated,
    )

    assert result.contribution_findings == ()


def test_only_explicit_rule_findings_appear() -> None:
    artifacts = _artifacts(
        comparison_description="fossil displacement is claimed",
        documentation_description="commercial emissions claim",
    )
    expected = _finding("explicit-rule-finding")

    result = _composer(_Rule((expected,)), _Rule(()), _Rule(()))(
        artifacts.engine,
        artifacts.integrated,
    )

    assert result.contribution_findings == (expected,)
    assert result.contribution_findings[0] is expected


def test_open_ended_substantive_findings_are_preserved_unchanged() -> None:
    artifacts = _artifacts()
    limited = _finding("limited", ("limited displacement",))
    conditional = _finding("conditional", ("conditional displacement",))
    function_unresolved = _finding("function", ("function remains unresolved",))
    persistence_unresolved = _finding(
        "persistence-unresolved",
        ("persistence remains unresolved",),
    )
    adverse = _finding("adverse", ("continued fallback", "adverse persistence"))
    composer = _composer(
        _Rule((limited, conditional)),
        _Rule((function_unresolved,)),
        _Rule((persistence_unresolved, adverse)),
    )

    result = composer(artifacts.engine, artifacts.integrated)

    assert result.contribution_findings == (
        limited,
        conditional,
        function_unresolved,
        persistence_unresolved,
        adverse,
    )
    assert all(
        actual is expected
        for actual, expected in zip(
            result.contribution_findings,
            (
                limited,
                conditional,
                function_unresolved,
                persistence_unresolved,
                adverse,
            ),
            strict=True,
        )
    )


def test_rules_preserve_different_material_evidence_subsets() -> None:
    artifacts = _artifacts()
    displacement = replace(
        _finding("displacement"),
        pathway_output_references=(artifacts.pathway.objects[0],),
        supporting_comparison_findings=(artifacts.comparison,),
    )
    function = replace(
        _finding("function"),
        supporting_queue_results=(artifacts.queue_result,),
    )
    persistence = replace(
        _finding("persistence"),
        supporting_fabric_results=(artifacts.fabric_result,),
        supporting_documentation_findings=(artifacts.documentation,),
    )
    composer = _composer(
        _Rule((displacement,)),
        _Rule((function,)),
        _Rule((persistence,)),
    )

    result = composer(artifacts.engine, artifacts.integrated)

    assert result.contribution_findings == (displacement, function, persistence)
    assert displacement.supporting_queue_results == ()
    assert function.supporting_comparison_findings == ()
    assert persistence.pathway_output_references == ()


def test_queue_subordinate_records_and_scalar_fields_are_not_added() -> None:
    finding_fields = {field.name for field in fields(ContributionFinding)}
    result_fields = {field.name for field in fields(NetOverallSystemContribution)}

    assert {
        "queue_execution_results",
        "queue_progress_records",
        "supporting_queue_execution_results",
        "supporting_queue_progress_records",
    }.isdisjoint(finding_fields)
    assert {"score", "rank", "ranking", "weight", "votes"}.isdisjoint(
        finding_fields | result_fields
    )


def test_composer_integrates_with_validated_contribution_boundary() -> None:
    artifacts = _artifacts()
    finding = replace(
        _finding("validated"),
        pathway_output_references=(artifacts.pathway.objects[0],),
        supporting_comparison_findings=(artifacts.comparison,),
        supporting_queue_results=(artifacts.queue_result,),
        supporting_fabric_results=(artifacts.fabric_result,),
        supporting_documentation_findings=(artifacts.documentation,),
    )
    composer = _composer(_Rule((finding,)), _Rule(()), _Rule(()))
    evaluator = ValidatedNetOverallSystemContributionEvaluator(composer)

    result = evaluator.evaluate(artifacts.engine, artifacts.integrated)

    assert result.contribution_findings == (finding,)
    assert result.pathway_engine_result is artifacts.engine
