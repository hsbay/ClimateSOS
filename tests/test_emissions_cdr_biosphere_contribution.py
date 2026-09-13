"""Focused source-emissions, CDR, and biosphere contribution-rule tests."""

from dataclasses import dataclass, fields, replace
from inspect import signature
from typing import cast, get_args, get_type_hints

import pytest

import climatesos.pathway_evaluation as pathway_evaluation
from climatesos.pathway_evaluation import (
    BiosphereContributionRuleFunction,
    CarbonRemovalRuleFunction,
    ComparisonFinding,
    ContributionFinding,
    DocumentationFinding,
    EmissionsCdrBiosphereEvaluationInvariantError,
    EmissionsCdrBiosphereFindingFunction,
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
    SourceEmissionsRuleFunction,
    TransitionPathway,
)


@dataclass(frozen=True, slots=True)
class _Artifacts:
    output: PathwayObject
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


def _artifacts() -> _Artifacts:
    token = IdentityToken("token-1")
    run = EvaluationRun("run-1", token.token_id)
    intake = ProductIntakeBundle(token, run, ())
    output = PathwayObject(
        object_id="output-1",
        object_type="verified carbon removal and ecosystem restoration",
        user_id="user-1",
        pathway_id="pathway-1",
    )
    queue_object = PathwayObject(
        object_id="queue-1",
        object_type="emissions measurement",
        user_id="user-1",
        pathway_id="pathway-1",
    )
    queue_element = QueueElement(queue_object, QueueCategory.MRV)
    pathway = ProductPathway(
        identity_token=token,
        evaluation_run_id=run.evaluation_run_id,
        user_id="user-1",
        pathway_id="pathway-1",
        pathway_type="net-negative ecological carbon project",
        time_window="2030",
        geographic_scope="local",
        system_scope="biosphere and industry",
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
    bundle = ProductQueueBundle("bundle-1", pathway, (queue_element,))
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
    queue_result = QueueEvaluatorResult(
        evaluated_queue=bundle,
        evaluation_run_id=run.evaluation_run_id,
        final_operational_status=QueueOperationalStatus.CLEAR,
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
        findings=("claims durable carbon removal and avoided emissions",),
    )
    comparison = ComparisonFinding(
        finding_id="comparison-1",
        finding_type="carbon removal and emissions claim",
        description="claims CDR substitutes for source-emissions elimination",
    )
    fabric = ProductFabric(
        fabric_id="fabric-1",
        coordination_function="biosphere coordination",
        product_pathway=pathway,
        queue_bundles=(bundle,),
    )
    fabric_result = FabricEvaluatorResult(
        product_fabric=fabric,
        queue_results=(queue_result,),
        pathway_comparison_findings=(comparison,),
        downstream_propagation_findings=(),
        transition_pathway=transition,
        coordination_condition="ecological benefit and removal durability claimed",
        evaluator_version="fabric-1",
        rule_set_version="fabric-rules-1",
        evaluation_run_id=run.evaluation_run_id,
        user_id=pathway.user_id,
        pathway_id=pathway.pathway_id,
        system_context=system_context,
        findings=("carbon benefit proves biosphere benefit",),
    )
    documentation = DocumentationFinding(
        finding_id="documentation-1",
        subject_id=output.object_id,
        status="verified removal claim",
        description="claims net-negative emissions and restored ecology",
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
        output,
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
) -> ContributionFinding:
    return ContributionFinding(
        finding_id=finding_id,
        effect_description=f"effect-{finding_id}",
        contribution_statuses=statuses,
    )


def _composer(
    emissions: _Rule,
    removal: _Rule,
    biosphere: _Rule,
) -> EmissionsCdrBiosphereFindingFunction:
    return EmissionsCdrBiosphereFindingFunction(emissions, removal, biosphere)


def test_rule_aliases_and_composer_have_exact_contracts() -> None:
    for rule_type in (
        SourceEmissionsRuleFunction,
        CarbonRemovalRuleFunction,
        BiosphereContributionRuleFunction,
    ):
        parameter_types, return_type = get_args(rule_type)
        assert parameter_types == [PathwayEngineResult, IntegratedCharterResult]
        assert return_type == tuple[ContributionFinding, ...]

    callable_hints = get_type_hints(EmissionsCdrBiosphereFindingFunction.__call__)
    assert callable_hints["return"] == tuple[ContributionFinding, ...]
    assert tuple(
        signature(EmissionsCdrBiosphereFindingFunction.__call__).parameters
    ) == ("self", "pathway_engine_result", "integrated_charter_result")
    assert {field.name for field in fields(EmissionsCdrBiosphereFindingFunction)} == {
        "source_emissions_rule",
        "carbon_removal_rule",
        "biosphere_contribution_rule",
    }


def test_rules_execute_once_on_shared_inputs_and_preserve_group_order() -> None:
    artifacts = _artifacts()
    later_id = _finding("z-source")
    earlier_id = _finding("a-source")
    removal = _finding("removal")
    biosphere = _finding("biosphere")
    emissions_rule = _Rule((later_id, earlier_id, later_id))
    removal_rule = _Rule((removal,))
    biosphere_rule = _Rule((biosphere,))
    composer = _composer(emissions_rule, removal_rule, biosphere_rule)

    result = composer(artifacts.engine, artifacts.integrated)

    for rule in (emissions_rule, removal_rule, biosphere_rule):
        assert rule.calls == [(artifacts.engine, artifacts.integrated)]
    assert result == (later_id, earlier_id, later_id, removal, biosphere)
    assert result[0] is result[2]
    assert not isinstance(result, NetOverallSystemContribution)


@pytest.mark.parametrize("rule_name", ("emissions", "removal", "biosphere"))
@pytest.mark.parametrize(
    "malformed",
    (None, [], _finding("single"), (_finding("valid"), object())),
)
def test_malformed_rule_results_reject(rule_name: str, malformed: object) -> None:
    artifacts = _artifacts()

    def malformed_rule(
        _engine: PathwayEngineResult,
        _integrated: IntegratedCharterResult,
    ) -> object:
        return malformed

    empty = _Rule(())
    emissions: SourceEmissionsRuleFunction = empty
    removal: CarbonRemovalRuleFunction = empty
    biosphere: BiosphereContributionRuleFunction = empty
    if rule_name == "emissions":
        emissions = cast(SourceEmissionsRuleFunction, malformed_rule)
    elif rule_name == "removal":
        removal = cast(CarbonRemovalRuleFunction, malformed_rule)
    else:
        biosphere = cast(BiosphereContributionRuleFunction, malformed_rule)
    composer = EmissionsCdrBiosphereFindingFunction(
        emissions,
        removal,
        biosphere,
    )

    with pytest.raises(EmissionsCdrBiosphereEvaluationInvariantError):
        composer(artifacts.engine, artifacts.integrated)


@pytest.mark.parametrize("failed_rule", ("emissions", "removal", "biosphere"))
def test_rule_exception_propagates_and_stops_later_rules(failed_rule: str) -> None:
    artifacts = _artifacts()
    calls: list[str] = []

    def rule(name: str) -> SourceEmissionsRuleFunction:
        def execute(
            _engine: PathwayEngineResult,
            _integrated: IntegratedCharterResult,
        ) -> tuple[ContributionFinding, ...]:
            calls.append(name)
            if name == failed_rule:
                raise RuntimeError(f"{name} failed")
            return ()

        return execute

    composer = EmissionsCdrBiosphereFindingFunction(
        rule("emissions"),
        rule("removal"),
        rule("biosphere"),
    )

    with pytest.raises(RuntimeError, match=f"{failed_rule} failed"):
        composer(artifacts.engine, artifacts.integrated)

    expected_calls = {
        "emissions": ["emissions"],
        "removal": ["emissions", "removal"],
        "biosphere": ["emissions", "removal", "biosphere"],
    }
    assert calls == expected_calls[failed_rule]


def test_suggestive_labels_and_text_do_not_generate_any_findings() -> None:
    artifacts = _artifacts()

    result = _composer(_Rule(()), _Rule(()), _Rule(()))(
        artifacts.engine,
        artifacts.integrated,
    )

    assert result == ()


def test_source_emissions_cdr_and_biosphere_findings_remain_distinct() -> None:
    artifacts = _artifacts()
    emissions = _finding("source-emissions")
    removal = _finding("carbon-removal")
    biosphere = _finding("biosphere")

    result = _composer(
        _Rule((emissions,)),
        _Rule((removal,)),
        _Rule((biosphere,)),
    )(artifacts.engine, artifacts.integrated)

    assert result == (emissions, removal, biosphere)
    assert result[0] is emissions
    assert result[1] is removal
    assert result[2] is biosphere


def test_cdr_is_not_composed_as_source_emissions_abatement() -> None:
    artifacts = _artifacts()
    removal = _finding("removal-only")

    result = _composer(_Rule(()), _Rule((removal,)), _Rule(()))(
        artifacts.engine,
        artifacts.integrated,
    )

    assert result == (removal,)
    assert result[0] is removal


def test_only_explicit_open_ended_rule_findings_are_preserved() -> None:
    artifacts = _artifacts()
    limited = _finding("limited-emissions", ("caller limited",))
    conditional = _finding("conditional-removal", ("caller conditional",))
    unresolved = _finding("unresolved-removal", ("caller unresolved",))
    adverse = _finding("adverse-biosphere", ("caller adverse",))
    positive = _finding("positive-biosphere", ("caller positive",))
    expected = (limited, conditional, unresolved, adverse, positive)

    result = _composer(
        _Rule((limited,)),
        _Rule((conditional, unresolved)),
        _Rule((adverse, positive)),
    )(artifacts.engine, artifacts.integrated)

    assert result == expected
    assert all(
        actual is supplied
        for actual, supplied in zip(result, expected, strict=True)
    )


def test_findings_preserve_distinct_material_evidence_subsets() -> None:
    artifacts = _artifacts()
    emissions = replace(
        _finding("emissions"),
        pathway_output_references=(artifacts.output,),
        supporting_comparison_findings=(artifacts.comparison,),
    )
    removal = replace(
        _finding("removal"),
        supporting_queue_results=(artifacts.queue_result,),
        supporting_documentation_findings=(artifacts.documentation,),
    )
    biosphere = replace(
        _finding("biosphere"),
        supporting_fabric_results=(artifacts.fabric_result,),
        supporting_system_references=(OpaqueReference("biosphere-system-1"),),
    )

    result = _composer(
        _Rule((emissions,)),
        _Rule((removal,)),
        _Rule((biosphere,)),
    )(artifacts.engine, artifacts.integrated)

    assert result == (emissions, removal, biosphere)
    assert emissions.supporting_comparison_findings[0] is artifacts.comparison
    assert removal.supporting_queue_results[0] is artifacts.queue_result
    assert removal.supporting_documentation_findings[0] is artifacts.documentation
    assert biosphere.supporting_fabric_results[0] is artifacts.fabric_result


def test_no_queue_subrecords_scale_or_scalar_fields_are_added() -> None:
    finding_fields = {field.name for field in fields(ContributionFinding)}
    composer_fields = {
        field.name for field in fields(EmissionsCdrBiosphereFindingFunction)
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
