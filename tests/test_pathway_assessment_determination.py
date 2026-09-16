import inspect
from dataclasses import dataclass, replace

import pytest

import climatesos.pathway_evaluation.pathway_assessment as assessment_module
from climatesos.pathway_evaluation import (
    BoundPathway,
    BoundState,
    CharterCheckResult,
    CharterCheckStatus,
    ComparisonFinding,
    ContributionFinding,
    DocumentationFinding,
    EvaluationRun,
    EvaluationTrace,
    FabricEvaluatorResult,
    FinalCharterResult,
    FinalPathwayResult,
    IdentityToken,
    InitialCharterResult,
    IntakeArtifact,
    IntegratedCharterResult,
    NetOverallSystemContribution,
    NetOverallSystemRiskResult,
    OpaqueReference,
    PathwayAssessment,
    PathwayAssessmentEvaluator,
    PathwayEngineResult,
    PathwayObject,
    ProductAdapterResult,
    ProductEvaluationContext,
    ProductEvaluationContextMode,
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
    QueueProgressRecord,
    QueueSynchronizationStatus,
    ScaleDiagnosticResult,
    ScaleFinding,
    SystemRiskFinding,
    TransitionPathway,
)


@dataclass(frozen=True)
class _CompletedLineage:
    product: ProductPathway
    initial: InitialCharterResult
    integrated: IntegratedCharterResult
    final_charter: FinalCharterResult
    bound: BoundPathway
    context: ProductEvaluationContext
    candidate: TransitionPathway
    authoritative: TransitionPathway
    token: IdentityToken
    direct: ComparisonFinding
    substitution: ComparisonFinding
    downstream: ComparisonFinding
    queue_result: QueueEvaluatorResult
    progress_record: QueueProgressRecord
    contribution_finding: ContributionFinding
    scale_finding: ScaleFinding
    risk_finding: SystemRiskFinding


def _completed_lineage(
    bound_state: BoundState = BoundState.CLEAN_BOUND,
) -> _CompletedLineage:
    token = IdentityToken("lineage-1")
    pathway_object = PathwayObject("object-1", "test", "user-1", "pathway-1")
    queue_element = QueueElement(
        pathway_object,
        QueueCategory.PRODUCTION_CONVERSION_AND_EXECUTION_CAPACITY,
    )
    product = ProductPathway(
        identity_token=token,
        evaluation_run_id="run-1",
        user_id="user-1",
        pathway_id="pathway-1",
        pathway_type="test",
        time_window=None,
        geographic_scope=None,
        system_scope=None,
        objects=(pathway_object,),
        relationships=(),
        queue_elements=(queue_element,),
    )
    intake = ProductIntakeBundle(
        identity_token=token,
        evaluation_run=EvaluationRun("run-1", token.token_id),
        materials=(IntakeArtifact("artifact-1", "text/plain", "input"),),
    )
    adapter = ProductAdapterResult(product, intake, intake.evaluation_run)
    initial_check = CharterCheckResult("initial-check", CharterCheckStatus.PASS)
    initial = InitialCharterResult(
        token,
        "run-1",
        adapter,
        (initial_check,),
        "charter-v1",
        "charter-rules-v1",
        "PASS",
    )
    authoritative = TransitionPathway(
        reference_id="authoritative-transition",
        model_version="model-v1",
    )
    bundle = ProductQueueBundle("bundle-1", product, (queue_element,))
    progress = QueueProgressRecord(
        bundle,
        "run-1",
        QueueOperationalStatus.CLEAR,
        QueueLifecycleState.CLOSED,
        QueueOrderingStatus.ORDERED,
        QueueSynchronizationStatus.SYNCHRONIZED,
        1,
        "user-1",
        "pathway-1",
    )
    execution = QueueExecutionResult(
        bundle,
        "run-1",
        "completed",
        (progress,),
        "user-1",
        "pathway-1",
        transition_pathway=authoritative,
    )
    queue_result = QueueEvaluatorResult(
        bundle,
        "run-1",
        QueueOperationalStatus.CLEAR,
        QueueLifecycleState.CLOSED,
        QueueOrderingStatus.ORDERED,
        QueueSynchronizationStatus.SYNCHRONIZED,
        None,
        execution,
        (progress,),
        authoritative,
        "queue-v1",
        "queue-rules-v1",
        "user-1",
        "pathway-1",
        findings=("failed restricted unresolved words are not classification",),
    )
    direct = ComparisonFinding(
        "direct",
        "caller-defined",
        "FAILED regression prose must not determine the assessment",
    )
    substitution = ComparisonFinding(
        "substitution",
        "caller-defined",
        "favorable improvement prose must not determine the assessment",
    )
    downstream = ComparisonFinding(
        "downstream",
        "caller-defined",
        "unresolved restrictive prose must not stop traversal",
    )
    fabric = ProductFabric("fabric-1", "coordinate", product, (bundle,))
    fabric_result = FabricEvaluatorResult(
        fabric,
        (queue_result,),
        (direct, substitution),
        (downstream,),
        authoritative,
        "coordinated",
        "fabric-v1",
        "fabric-rules-v1",
        "run-1",
        "user-1",
        "pathway-1",
    )
    documentation = DocumentationFinding(
        "documentation-1",
        "object-1",
        "complete",
        "documentation conclusion",
    )
    engine = PathwayEngineResult(
        token,
        product,
        authoritative,
        initial,
        (direct,),
        (substitution,),
        (downstream,),
        (queue_result,),
        (fabric_result,),
        (documentation,),
        "run-1",
        None,
        (),
        (),
        "user-1",
        "pathway-1",
    )
    integrated_check = CharterCheckResult(
        "integrated-check",
        CharterCheckStatus.PASS,
    )
    integrated = IntegratedCharterResult(
        token,
        "run-1",
        engine,
        initial,
        (integrated_check,),
        "charter-v1",
        "charter-rules-v1",
        "PASS",
    )
    contribution_finding = ContributionFinding(
        "contribution-1",
        "contribution conclusion",
        supporting_comparison_findings=(direct,),
        supporting_queue_results=(queue_result,),
        supporting_fabric_results=(fabric_result,),
        supporting_documentation_findings=(documentation,),
    )
    contribution = NetOverallSystemContribution(
        product,
        engine,
        integrated,
        authoritative,
        (contribution_finding,),
        "run-1",
        "user-1",
        "pathway-1",
        "contribution-v1",
        "contribution-rules-v1",
    )
    scale_finding = ScaleFinding(
        "scale-1",
        "scale conclusion",
        contribution_findings=(contribution_finding,),
        supporting_comparison_findings=(substitution,),
        supporting_queue_results=(queue_result,),
    )
    scale = ScaleDiagnosticResult(
        product,
        contribution,
        authoritative,
        (scale_finding,),
        "run-1",
        "user-1",
        "pathway-1",
        "scale-v1",
        "scale-rules-v1",
    )
    candidate = TransitionPathway(
        reference_id="candidate-transition",
        identity_token=token,
        evaluation_run_id="run-1",
        user_id="user-1",
        pathway_id="pathway-1",
        authoritative_transition_pathway=authoritative,
        product_pathway=product,
        net_overall_system_contribution=contribution,
        scale_diagnostic_result=scale,
        conditions=("condition remains attached",),
        unresolved_conditions=("structured unresolved condition",),
        compiler_version="compiler-v1",
        model_version="model-v1",
        rule_set_version="compiler-rules-v1",
    )
    risk_finding = SystemRiskFinding(
        "risk-1",
        "later risk conclusion",
        supporting_contribution_findings=(contribution_finding,),
        supporting_scale_findings=(scale_finding,),
    )
    risk = NetOverallSystemRiskResult(
        candidate,
        authoritative,
        (risk_finding,),
        "run-1",
        "user-1",
        "pathway-1",
        "risk-v1",
        "risk-rules-v1",
    )
    trace = EvaluationTrace(initial, engine, integrated, contribution, scale)
    final_pathway = FinalPathwayResult(
        product,
        authoritative,
        candidate,
        risk,
        trace,
        token,
        "run-1",
        "user-1",
        "pathway-1",
        "assembly-v1",
        "assembly-rules-v1",
    )
    final_check = CharterCheckResult(
        "final-check",
        CharterCheckStatus.PASS,
        supporting_evaluation_findings=(OpaqueReference("risk-finding-1"),),
    )
    final_charter = FinalCharterResult(
        token,
        "run-1",
        final_pathway,
        initial,
        integrated,
        (final_check,),
        "charter-v1",
        "charter-rules-v1",
        "PASS",
    )
    bound = BoundPathway(
        final_pathway,
        bound_state,
        token,
        "run-1",
        "user-1",
        "pathway-1",
        "binding",
        "binding-v1",
    )
    return _CompletedLineage(
        product,
        initial,
        integrated,
        final_charter,
        bound,
        ProductEvaluationContext(ProductEvaluationContextMode.GLOBAL),
        candidate,
        authoritative,
        token,
        direct,
        substitution,
        downstream,
        queue_result,
        progress,
        contribution_finding,
        scale_finding,
        risk_finding,
    )


def _evaluate(lineage: _CompletedLineage) -> PathwayAssessment:
    return PathwayAssessmentEvaluator().evaluate(
        lineage.product,
        lineage.initial,
        lineage.integrated,
        lineage.final_charter,
        lineage.bound,
        lineage.context,
        lineage.candidate,
        lineage.authoritative,
        IdentityToken(lineage.token.token_id),
        "run-1",
        "user-1",
        "pathway-1",
        "assessment-1",
    )


def test_only_explicitly_supported_comparisons_enter_internal_lineage() -> None:
    lineage = _completed_lineage()

    result = _evaluate(lineage)
    internal_lineage = assessment_module._collect_material_lineage(
        lineage.bound,
        lineage.initial,
        lineage.integrated,
        lineage.final_charter,
        lineage.candidate,
    )

    assert result.assessment_outcome == "successful"
    assert internal_lineage.supported_comparison_findings == (
        lineage.direct,
        lineage.substitution,
    )
    assert internal_lineage.supported_comparison_findings[0] is lineage.direct
    assert internal_lineage.supported_comparison_findings[1] is lineage.substitution


def test_unrelated_engine_comparison_is_not_material_without_fitness() -> None:
    lineage = _completed_lineage()

    result = _evaluate(lineage)

    assert lineage.downstream not in (
        lineage.contribution_finding.supporting_comparison_findings
        + lineage.scale_finding.supporting_comparison_findings
    )
    assert result.replacement_fitness is None
    assert result.material_comparative_findings == ()


def test_queue_summary_is_boundary_and_progress_is_not_surfaced() -> None:
    lineage = _completed_lineage()

    result = _evaluate(lineage)

    engine = lineage.bound.final_pathway_result.evaluation_trace.pathway_engine_result
    assert engine.queue_results == (lineage.queue_result,)
    assert lineage.queue_result.progress_records == (lineage.progress_record,)
    assert result.material_comparative_findings == ()
    assert result.progression_preventing_findings == ()
    assert "QueueProgressRecord" not in inspect.getsource(assessment_module)


def test_later_findings_preserve_upstream_objects_and_ownership() -> None:
    lineage = _completed_lineage()

    _evaluate(lineage)

    assert lineage.risk_finding.supporting_contribution_findings == (
        lineage.contribution_finding,
    )
    assert lineage.risk_finding.supporting_scale_findings == (lineage.scale_finding,)
    assert lineage.contribution_finding.supporting_comparison_findings[0] is (
        lineage.direct
    )


def test_charter_results_remain_separate_exact_authoritative_records() -> None:
    lineage = _completed_lineage()

    result = _evaluate(lineage)

    assert result.initial_charter_result is lineage.initial
    assert result.integrated_charter_result is lineage.integrated
    assert result.final_charter_result is lineage.final_charter
    charter_result_ids = {
        id(result.initial_charter_result),
        id(result.integrated_charter_result),
        id(result.final_charter_result),
    }
    assert len(charter_result_ids) == 3


def test_unknown_determinations_are_not_inferred_in_global_mode() -> None:
    result = _evaluate(_completed_lineage())

    assert result.correctable is None
    assert result.replacement_fitness is None
    assert result.material_improvements == ()
    assert result.material_regressions == ()
    assert result.upstream_result_references == ()


def test_user_context_does_not_make_global_comparative_determination() -> None:
    lineage = replace(
        _completed_lineage(),
        context=ProductEvaluationContext(ProductEvaluationContextMode.USER_SUBMITTED),
    )

    result = _evaluate(lineage)

    assert result.replacement_fitness is None
    assert result.material_comparative_findings == ()


@pytest.mark.parametrize(
    ("bound_state", "outcome"),
    (
        (BoundState.CLEAN_BOUND, "successful"),
        (BoundState.BIO_BOUND, "BioBound"),
        (BoundState.RESTORATION_BOUND, "RestorationBound"),
        (BoundState.MIXED_BOUND, "restricted"),
        (BoundState.BOUNDARY_STRESS, "BoundaryStress"),
        (BoundState.FOSSIL_BOUND, "failed"),
        (BoundState.HARM_BOUND, "failed"),
        (BoundState.UNBOUND, "unresolved"),
    ),
)
def test_outcome_uses_explicit_bound_state_semantics(
    bound_state: BoundState,
    outcome: str,
) -> None:
    assert _evaluate(_completed_lineage(bound_state)).assessment_outcome == outcome


def test_traversal_does_not_stop_before_later_material_branch() -> None:
    lineage = _completed_lineage()
    malformed_risk = replace(
        lineage.bound.final_pathway_result.net_overall_system_risk_result,
        risk_findings=(object(),),  # type: ignore[arg-type]
    )
    malformed_final = replace(
        lineage.bound.final_pathway_result,
        net_overall_system_risk_result=malformed_risk,
    )
    malformed_charter = replace(
        lineage.final_charter,
        final_pathway_result=malformed_final,
    )
    malformed_bound = replace(lineage.bound, final_pathway_result=malformed_final)
    malformed = replace(
        lineage,
        final_charter=malformed_charter,
        bound=malformed_bound,
    )

    with pytest.raises(ValueError, match="System risk findings"):
        _evaluate(malformed)


def test_no_keyword_classifier_or_generic_scoring_is_present() -> None:
    result = _evaluate(_completed_lineage(BoundState.CLEAN_BOUND))
    source = inspect.getsource(assessment_module).lower()

    assert result.assessment_outcome == "successful"
    assert "_failure_markers" not in source
    assert "_restricted_markers" not in source
    assert "severity" not in source
    assert "score" not in source
    assert "keyword" not in source


def test_exact_direct_references_and_canonical_token_lineage_are_preserved() -> None:
    lineage = _completed_lineage()

    result = _evaluate(lineage)

    assert result.product_pathway is lineage.product
    assert result.bound_pathway is lineage.bound
    assert result.product_evaluation_context is lineage.context
    assert result.reference_transition_pathway is lineage.authoritative
    final_pathway = lineage.bound.final_pathway_result
    assert final_pathway.candidate_transition_pathway is lineage.candidate
    assert result.identity_token is not lineage.token
    assert result.identity_token.token_id == lineage.token.token_id
