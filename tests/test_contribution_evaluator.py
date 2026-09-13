"""Validated Net Overall System Contribution evaluator invariants."""

from dataclasses import dataclass, fields, replace
from typing import cast

import pytest

from climatesos.pathway_evaluation import (
    CharterCheckResult,
    CharterCheckStatus,
    ComparisonFinding,
    ContributionEvaluationInvariantError,
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
    ValidatedNetOverallSystemContributionEvaluator,
)


@dataclass(frozen=True, slots=True)
class _Artifacts:
    pathway: ProductPathway
    initial: InitialCharterResult
    transition: TransitionPathway
    comparison: ComparisonFinding
    queue_result: QueueEvaluatorResult
    fabric_result: FabricEvaluatorResult
    documentation: DocumentationFinding
    engine: PathwayEngineResult
    integrated: IntegratedCharterResult


class _RecordingContributionFunction:
    def __init__(self, output: object) -> None:
        self.output = output
        self.calls: list[
            tuple[PathwayEngineResult, IntegratedCharterResult]
        ] = []

    def __call__(
        self,
        engine: PathwayEngineResult,
        integrated: IntegratedCharterResult,
    ) -> object:
        self.calls.append((engine, integrated))
        return self.output


def _artifacts() -> _Artifacts:
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
    initial = InitialCharterResult(
        identity_token=token,
        evaluation_run_id=evaluation_run.evaluation_run_id,
        adapter_result=adapter_result,
        check_results=(),
        evaluator_version="initial-1",
        rule_set_version="charter-1",
        status="PASS",
    )
    transition = TransitionPathway("transition-1")
    system_context = OpaqueReference("system-1")
    queue_bundle = ProductQueueBundle(
        bundle_id="bundle-1",
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
        description="Material comparison.",
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
        description="Material documentation.",
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
        evaluation_run_id=evaluation_run.evaluation_run_id,
        system_context=system_context,
        evaluator_versions=(),
        rule_set_versions=(),
        user_id=pathway.user_id,
        pathway_id=pathway.pathway_id,
    )
    integrated = IntegratedCharterResult(
        identity_token=token,
        evaluation_run_id=evaluation_run.evaluation_run_id,
        pathway_engine_result=engine,
        initial_charter_result=initial,
        check_results=(),
        evaluator_version="integrated-1",
        rule_set_version="charter-1",
        status="PASS",
    )
    return _Artifacts(
        pathway,
        initial,
        transition,
        comparison,
        queue_result,
        fabric_result,
        documentation,
        engine,
        integrated,
    )


def _finding(
    artifacts: _Artifacts,
    statuses: tuple[str, ...] = ("supported",),
) -> ContributionFinding:
    return ContributionFinding(
        finding_id="contribution-1",
        effect_description="Supports a transition function.",
        contribution_scope="local",
        contribution_type="enabling",
        contribution_mechanism="constraint reduction",
        contribution_statuses=statuses,
        pathway_output_references=(artifacts.pathway.objects[0],),
        net_zero_transition_effects=("reduces a bottleneck",),
        transition_function_references=(OpaqueReference("function-1"),),
        system_effects=("supports delivery",),
        timing_effects=("available after infrastructure delivery",),
        dependencies=("grid connection",),
        conditions=("permit granted",),
        supporting_comparison_findings=(artifacts.comparison,),
        supporting_queue_results=(artifacts.queue_result,),
        supporting_fabric_results=(artifacts.fabric_result,),
        supporting_documentation_findings=(artifacts.documentation,),
        supporting_system_references=(OpaqueReference("system-relation-1"),),
        evidence_references=(SourceReference("evidence-1"),),
        provenance=(SourceReference("provenance-1"),),
    )


def _result(
    artifacts: _Artifacts,
    findings: tuple[ContributionFinding, ...] | None = None,
) -> NetOverallSystemContribution:
    return NetOverallSystemContribution(
        product_pathway=artifacts.pathway,
        pathway_engine_result=artifacts.engine,
        integrated_charter_result=artifacts.integrated,
        transition_pathway=artifacts.transition,
        contribution_findings=(
            findings if findings is not None else (_finding(artifacts),)
        ),
        evaluation_run_id=artifacts.engine.evaluation_run_id,
        user_id=artifacts.engine.user_id,
        pathway_id=artifacts.engine.pathway_id,
        evaluator_version="contribution-1",
        rule_set_version="contribution-rules-1",
        assumptions=("system context applies",),
        uncertainties=("propagation uncertain",),
        evidence_references=(SourceReference("evidence-1"),),
        provenance=(SourceReference("provenance-1"),),
    )


def _evaluate(
    artifacts: _Artifacts,
    output: object,
    engine: PathwayEngineResult | None = None,
    integrated: IntegratedCharterResult | None = None,
) -> tuple[object, _RecordingContributionFunction]:
    function = _RecordingContributionFunction(output)
    evaluator: NetOverallSystemContributionEvaluator = (
        ValidatedNetOverallSystemContributionEvaluator(function)
    )
    result = evaluator.evaluate(
        engine if engine is not None else artifacts.engine,
        integrated if integrated is not None else artifacts.integrated,
    )
    return result, function


@pytest.mark.parametrize(
    "status",
    ("PASS", "FAIL", "UNRESOLVED", "NOT_APPLICABLE"),
)
def test_substantive_integrated_charter_statuses_progress(status: str) -> None:
    artifacts = _artifacts()
    integrated = replace(artifacts.integrated, status=status)
    expected = replace(_result(artifacts), integrated_charter_result=integrated)

    actual, function = _evaluate(artifacts, expected, integrated=integrated)

    assert actual is expected
    assert function.calls == [(artifacts.engine, integrated)]


def test_valid_result_is_returned_unchanged_and_empty_findings_are_valid() -> None:
    artifacts = _artifacts()
    expected = _result(artifacts, ())

    actual, _ = _evaluate(artifacts, expected)

    assert actual is expected


@pytest.mark.parametrize(
    ("status", "execution_error"),
    (("ERROR", None), ("PASS", "integrated evaluator failed")),
)
def test_integrated_stage_integrity_failure_rejects_before_callback(
    status: str,
    execution_error: str | None,
) -> None:
    artifacts = _artifacts()
    integrated = replace(
        artifacts.integrated,
        status=status,
        execution_error=execution_error,
    )
    function = _RecordingContributionFunction(_result(artifacts))
    evaluator = ValidatedNetOverallSystemContributionEvaluator(function)

    with pytest.raises(ContributionEvaluationInvariantError):
        evaluator.evaluate(artifacts.engine, integrated)

    assert function.calls == []


@pytest.mark.parametrize(
    "status",
    (
        CharterCheckStatus.ERROR,
        CharterCheckStatus.MISSING,
        CharterCheckStatus.NULL,
        CharterCheckStatus.NOACK,
    ),
)
def test_integrity_check_status_rejects_before_callback(
    status: CharterCheckStatus,
) -> None:
    artifacts = _artifacts()
    check = CharterCheckResult("check-1", status)
    integrated = replace(artifacts.integrated, check_results=(check,))
    function = _RecordingContributionFunction(_result(artifacts))
    evaluator = ValidatedNetOverallSystemContributionEvaluator(function)

    with pytest.raises(ContributionEvaluationInvariantError):
        evaluator.evaluate(artifacts.engine, integrated)

    assert function.calls == []


def test_mismatched_engine_reference_rejects_before_callback() -> None:
    artifacts = _artifacts()
    integrated = replace(
        artifacts.integrated,
        pathway_engine_result=replace(artifacts.engine),
    )
    function = _RecordingContributionFunction(_result(artifacts))
    evaluator = ValidatedNetOverallSystemContributionEvaluator(function)

    with pytest.raises(ContributionEvaluationInvariantError):
        evaluator.evaluate(artifacts.engine, integrated)

    assert function.calls == []


def test_mismatched_initial_charter_reference_rejects_before_callback() -> None:
    artifacts = _artifacts()
    integrated = replace(
        artifacts.integrated,
        initial_charter_result=replace(artifacts.initial),
    )
    function = _RecordingContributionFunction(_result(artifacts))
    evaluator = ValidatedNetOverallSystemContributionEvaluator(function)

    with pytest.raises(ContributionEvaluationInvariantError):
        evaluator.evaluate(artifacts.engine, integrated)

    assert function.calls == []


def test_mismatched_token_id_rejects_before_callback() -> None:
    artifacts = _artifacts()
    engine = replace(artifacts.engine, identity_token=IdentityToken("token-2"))
    integrated = replace(artifacts.integrated, pathway_engine_result=engine)
    function = _RecordingContributionFunction(_result(artifacts))
    evaluator = ValidatedNetOverallSystemContributionEvaluator(function)

    with pytest.raises(ContributionEvaluationInvariantError):
        evaluator.evaluate(engine, integrated)

    assert function.calls == []


def test_distinct_identity_tokens_with_same_token_id_are_accepted() -> None:
    artifacts = _artifacts()
    engine = replace(
        artifacts.engine,
        identity_token=IdentityToken(artifacts.pathway.identity_token.token_id),
    )
    integrated = replace(
        artifacts.integrated,
        identity_token=IdentityToken(artifacts.pathway.identity_token.token_id),
        pathway_engine_result=engine,
    )
    expected = replace(
        _result(artifacts),
        pathway_engine_result=engine,
        integrated_charter_result=integrated,
    )

    actual, _ = _evaluate(
        artifacts,
        expected,
        engine=engine,
        integrated=integrated,
    )

    assert actual is expected
    assert engine.identity_token is not artifacts.pathway.identity_token
    assert integrated.identity_token is not engine.identity_token


@pytest.mark.parametrize("source", ("engine", "integrated"))
def test_mismatched_evaluation_run_rejects_before_callback(source: str) -> None:
    artifacts = _artifacts()
    engine = artifacts.engine
    integrated = artifacts.integrated
    if source == "engine":
        engine = replace(engine, evaluation_run_id="run-2")
        integrated = replace(integrated, pathway_engine_result=engine)
    else:
        integrated = replace(integrated, evaluation_run_id="run-2")
    function = _RecordingContributionFunction(_result(artifacts))
    evaluator = ValidatedNetOverallSystemContributionEvaluator(function)

    with pytest.raises(ContributionEvaluationInvariantError):
        evaluator.evaluate(engine, integrated)

    assert function.calls == []


@pytest.mark.parametrize(
    ("field_name", "value"),
    (("user_id", "user-2"), ("pathway_id", "pathway-2")),
)
def test_mismatched_engine_attribution_rejects_before_callback(
    field_name: str,
    value: str,
) -> None:
    artifacts = _artifacts()
    if field_name == "user_id":
        engine = replace(artifacts.engine, user_id=value)
    else:
        engine = replace(artifacts.engine, pathway_id=value)
    integrated = replace(artifacts.integrated, pathway_engine_result=engine)
    function = _RecordingContributionFunction(_result(artifacts))
    evaluator = ValidatedNetOverallSystemContributionEvaluator(function)

    with pytest.raises(ContributionEvaluationInvariantError):
        evaluator.evaluate(engine, integrated)

    assert function.calls == []


@pytest.mark.parametrize("output", (None, "not-a-contribution"))
def test_none_and_wrong_result_types_reject(output: object) -> None:
    artifacts = _artifacts()

    with pytest.raises(ContributionEvaluationInvariantError):
        _evaluate(artifacts, output)


@pytest.mark.parametrize(
    ("field_name", "foreign_value"),
    (
        ("product_pathway", "pathway"),
        ("pathway_engine_result", "engine"),
        ("integrated_charter_result", "integrated"),
        ("transition_pathway", "transition"),
    ),
)
def test_wrong_primary_result_reference_rejects(
    field_name: str,
    foreign_value: str,
) -> None:
    artifacts = _artifacts()
    result = _result(artifacts)
    if field_name == "product_pathway":
        malformed = replace(result, product_pathway=replace(artifacts.pathway))
    elif field_name == "pathway_engine_result":
        malformed = replace(
            result,
            pathway_engine_result=replace(artifacts.engine),
        )
    elif field_name == "integrated_charter_result":
        malformed = replace(
            result,
            integrated_charter_result=replace(artifacts.integrated),
        )
    else:
        assert foreign_value == "transition"
        malformed = replace(
            result,
            transition_pathway=replace(artifacts.transition),
        )

    with pytest.raises(ContributionEvaluationInvariantError):
        _evaluate(artifacts, malformed)


@pytest.mark.parametrize(
    ("field_name", "value"),
    (
        ("evaluation_run_id", "run-2"),
        ("user_id", "user-2"),
        ("pathway_id", "pathway-2"),
    ),
)
def test_wrong_result_attribution_rejects(field_name: str, value: str) -> None:
    artifacts = _artifacts()
    result = _result(artifacts)
    if field_name == "evaluation_run_id":
        malformed = replace(result, evaluation_run_id=value)
    elif field_name == "user_id":
        malformed = replace(result, user_id=value)
    else:
        malformed = replace(result, pathway_id=value)

    with pytest.raises(ContributionEvaluationInvariantError):
        _evaluate(artifacts, malformed)


def test_exact_material_summary_references_and_opaque_references_are_valid() -> None:
    artifacts = _artifacts()
    expected = _result(artifacts)

    actual, _ = _evaluate(artifacts, expected)
    finding = cast(NetOverallSystemContribution, actual).contribution_findings[0]

    assert finding.pathway_output_references[0] is artifacts.pathway.objects[0]
    assert finding.supporting_comparison_findings[0] is artifacts.comparison
    assert finding.supporting_queue_results[0] is artifacts.queue_result
    assert finding.supporting_fabric_results[0] is artifacts.fabric_result
    assert finding.supporting_documentation_findings[0] is artifacts.documentation
    assert isinstance(finding.transition_function_references[0], OpaqueReference)
    assert isinstance(finding.supporting_system_references[0], OpaqueReference)


@pytest.mark.parametrize(
    "field_name",
    (
        "pathway_output_references",
        "supporting_comparison_findings",
        "supporting_queue_results",
        "supporting_fabric_results",
        "supporting_documentation_findings",
    ),
)
def test_equal_but_nonidentical_material_support_rejects(field_name: str) -> None:
    artifacts = _artifacts()
    finding = _finding(artifacts)
    if field_name == "pathway_output_references":
        malformed_finding = replace(
            finding,
            pathway_output_references=(replace(artifacts.pathway.objects[0]),),
        )
    elif field_name == "supporting_comparison_findings":
        malformed_finding = replace(
            finding,
            supporting_comparison_findings=(replace(artifacts.comparison),),
        )
    elif field_name == "supporting_queue_results":
        malformed_finding = replace(
            finding,
            supporting_queue_results=(replace(artifacts.queue_result),),
        )
    elif field_name == "supporting_fabric_results":
        malformed_finding = replace(
            finding,
            supporting_fabric_results=(replace(artifacts.fabric_result),),
        )
    else:
        malformed_finding = replace(
            finding,
            supporting_documentation_findings=(replace(artifacts.documentation),),
        )
    malformed = _result(artifacts, (malformed_finding,))

    with pytest.raises(ContributionEvaluationInvariantError):
        _evaluate(artifacts, malformed)


def test_findings_may_preserve_distinct_material_subsets_and_empty_categories() -> None:
    artifacts = _artifacts()
    first = replace(
        _finding(artifacts),
        supporting_fabric_results=(),
        supporting_documentation_findings=(),
    )
    second = replace(
        _finding(artifacts),
        finding_id="contribution-2",
        supporting_comparison_findings=(),
        supporting_queue_results=(),
    )
    expected = _result(artifacts, (first, second))

    actual, _ = _evaluate(artifacts, expected)

    assert actual is expected
    assert first.supporting_comparison_findings == (artifacts.comparison,)
    assert first.supporting_fabric_results == ()
    assert second.supporting_comparison_findings == ()
    assert second.supporting_fabric_results == (artifacts.fabric_result,)


def test_queue_subordinate_records_are_not_contribution_finding_fields() -> None:
    artifacts = _artifacts()
    finding = _finding(artifacts)
    field_names = {field.name for field in fields(ContributionFinding)}

    assert finding.supporting_queue_results[0].execution_result is not None
    assert finding.supporting_queue_results[0].progress_records
    assert {
        "supporting_queue_execution_results",
        "supporting_queue_progress_records",
    }.isdisjoint(field_names)


@pytest.mark.parametrize(
    "statuses",
    (("limited",), ("conditional",), ("unresolved",)),
)
def test_limited_conditional_and_unresolved_findings_are_valid(
    statuses: tuple[str, ...],
) -> None:
    artifacts = _artifacts()
    expected = _result(artifacts, (_finding(artifacts, statuses),))

    actual, _ = _evaluate(artifacts, expected)

    assert actual is expected


def test_malformed_result_and_finding_collections_reject() -> None:
    artifacts = _artifacts()
    malformed_result = replace(
        _result(artifacts),
        assumptions=cast(tuple[str, ...], ["mutable"]),
    )
    malformed_finding = replace(
        _finding(artifacts),
        contribution_statuses=cast(tuple[str, ...], ["limited"]),
    )

    with pytest.raises(ContributionEvaluationInvariantError):
        _evaluate(artifacts, malformed_result)
    with pytest.raises(ContributionEvaluationInvariantError):
        _evaluate(artifacts, _result(artifacts, (malformed_finding,)))


def test_exact_input_types_are_required_before_callback() -> None:
    artifacts = _artifacts()
    function = _RecordingContributionFunction(_result(artifacts))
    evaluator = ValidatedNetOverallSystemContributionEvaluator(function)

    with pytest.raises(ContributionEvaluationInvariantError):
        evaluator.evaluate(cast(PathwayEngineResult, object()), artifacts.integrated)
    with pytest.raises(ContributionEvaluationInvariantError):
        evaluator.evaluate(
            artifacts.engine,
            cast(IntegratedCharterResult, object()),
        )

    assert function.calls == []


def test_callback_exception_is_not_converted_to_an_unresolved_finding() -> None:
    artifacts = _artifacts()

    def fail(
        _engine: PathwayEngineResult,
        _integrated: IntegratedCharterResult,
    ) -> object:
        raise RuntimeError("substantive evaluator failed")

    evaluator = ValidatedNetOverallSystemContributionEvaluator(fail)

    with pytest.raises(RuntimeError, match="substantive evaluator failed"):
        evaluator.evaluate(artifacts.engine, artifacts.integrated)
