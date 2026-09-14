from dataclasses import dataclass
from typing import TypeVar

from climatesos.pathway_evaluation import (
    ComparisonFinding,
    CompleteScaleDiagnosticFunction,
    ContributionFinding,
    DocumentationFinding,
    FabricEvaluatorResult,
    NetOverallSystemContribution,
    OpaqueReference,
    PathwayEngineResult,
    PathwayObject,
    ProductPathway,
    QueueEvaluatorResult,
    ScaleDiagnosticFindingFunction,
    ScaleDiagnosticResult,
    ScaleFinding,
    SourceReference,
    TransitionPathway,
    ValidatedScaleDiagnosticEvaluator,
)

T = TypeVar("T")


def _record(record_type: type[T], **values: object) -> T:
    record = object.__new__(record_type)
    for name, value in values.items():
        object.__setattr__(record, name, value)
    return record


@dataclass(frozen=True)
class _Context:
    contribution: NetOverallSystemContribution
    product_pathway: ProductPathway
    transition_pathway: TransitionPathway
    contribution_finding: ContributionFinding
    pathway_output: PathwayObject
    comparison_finding: ComparisonFinding
    queue_result: QueueEvaluatorResult
    fabric_result: FabricEvaluatorResult
    documentation_finding: DocumentationFinding
    transition_function: OpaqueReference
    system_reference: OpaqueReference
    evidence: SourceReference
    provenance: SourceReference


def _context() -> _Context:
    pathway_output = _record(PathwayObject)
    comparison_finding = _record(ComparisonFinding)
    queue_result = _record(QueueEvaluatorResult)
    fabric_result = _record(FabricEvaluatorResult)
    documentation_finding = _record(DocumentationFinding)
    contribution_finding = ContributionFinding(
        finding_id="contribution-1",
        effect_description="Established contribution",
    )
    product_pathway = _record(
        ProductPathway,
        evaluation_run_id="run-1",
        user_id="user-1",
        pathway_id="pathway-1",
        objects=(pathway_output,),
    )
    transition_pathway = _record(TransitionPathway)
    pathway_engine_result = _record(
        PathwayEngineResult,
        direct_comparison_findings=(comparison_finding,),
        substitution_combination_findings=(),
        downstream_propagation_findings=(),
        queue_results=(queue_result,),
        fabric_results=(fabric_result,),
        documentation_findings=(documentation_finding,),
    )
    contribution = _record(
        NetOverallSystemContribution,
        product_pathway=product_pathway,
        transition_pathway=transition_pathway,
        pathway_engine_result=pathway_engine_result,
        contribution_findings=(contribution_finding,),
        evaluation_run_id="run-1",
        user_id="user-1",
        pathway_id="pathway-1",
    )
    return _Context(
        contribution=contribution,
        product_pathway=product_pathway,
        transition_pathway=transition_pathway,
        contribution_finding=contribution_finding,
        pathway_output=pathway_output,
        comparison_finding=comparison_finding,
        queue_result=queue_result,
        fabric_result=fabric_result,
        documentation_finding=documentation_finding,
        transition_function=_record(OpaqueReference),
        system_reference=_record(OpaqueReference),
        evidence=_record(SourceReference),
        provenance=_record(SourceReference),
    )


def _rule(
    name: str,
    findings: tuple[ScaleFinding, ...],
    calls: list[str],
) -> ScaleDiagnosticFindingFunction:
    def rule(*args: object) -> tuple[ScaleFinding, ...]:
        calls.append(name)
        return findings

    return rule


def _composer(
    rules: tuple[ScaleDiagnosticFindingFunction, ...],
) -> CompleteScaleDiagnosticFunction:
    return CompleteScaleDiagnosticFunction(
        material_scale_function=rules[0],
        scale_dimensions_function=rules[1],
        scale_progression_function=rules[2],
        timing_sequencing_function=rules[3],
        constraint_bottleneck_function=rules[4],
        response_condition_function=rules[5],
        scale_dependent_effect_function=rules[6],
        limited_local_function=rules[7],
        stale_success_function=rules[8],
        unresolved_scale_function=rules[9],
        evaluator_version="scale-v1",
        rule_set_version="scale-rules-v1",
    )


def _evaluate(
    context: _Context,
    composer: CompleteScaleDiagnosticFunction,
) -> ScaleDiagnosticResult:
    return ValidatedScaleDiagnosticEvaluator(composer).evaluate(
        context.contribution,
        context.product_pathway,
        context.transition_pathway,
        context.system_reference,
        ("material assumption",),
        ("material uncertainty",),
        (context.evidence,),
        (context.provenance,),
        "user-1",
        "pathway-1",
        "run-1",
    )


def test_all_section_12_surfaces_compose_with_exact_material_support() -> None:
    context = _context()
    findings = (
        ScaleFinding(
            "material",
            "Contribution reaches material scale",
            scale_scope="regional",
            statuses=("demonstrated-scale",),
            contribution_findings=(context.contribution_finding,),
            transition_function_references=(context.transition_function,),
            geographic_scope="region-a",
            system_scope="system-a",
            supporting_pathway_outputs=(context.pathway_output,),
        ),
        ScaleFinding(
            "dimensions",
            "Scale dimensions established",
            quantity_findings=("quantity",),
            capacity_findings=("capacity",),
            throughput_findings=("throughput",),
            coverage_findings=("coverage",),
            replication_findings=("replication",),
            deployment_findings=("deployment",),
            supporting_comparison_findings=(context.comparison_finding,),
        ),
        ScaleFinding(
            "progression",
            "Progression conditions established",
            scale_progression_findings=("learning curve",),
        ),
        ScaleFinding(
            "timing",
            "Timing and sequencing established",
            timing_conditions=("transition window",),
            sequencing_conditions=("infrastructure first",),
        ),
        ScaleFinding(
            "constraint",
            "Scale is constrained",
            statuses=("constrained-scale",),
            constraints=("scarce input",),
            bottlenecks=("delivery bottleneck",),
            supporting_queue_results=(context.queue_result,),
        ),
        ScaleFinding(
            "response",
            "Scale response conditions established",
            scale_increases=("capacity expansion",),
            unblocks=("interconnection",),
            constraint_mitigations=("resource efficiency",),
            workarounds=("alternate delivery",),
            resolution_conditions=("permit issued",),
        ),
        ScaleFinding(
            "effect",
            "Scaling changes system burdens",
            scale_dependent_effects=("higher shared-resource demand",),
            supporting_fabric_results=(context.fabric_result,),
            supporting_documentation_findings=(context.documentation_finding,),
            supporting_system_references=(context.system_reference,),
            evidence_references=(context.evidence,),
            provenance=(context.provenance,),
        ),
        ScaleFinding(
            "limited",
            "Contribution remains local",
            finding_type="limited-local-contribution",
            statuses=("limited-scale",),
        ),
        ScaleFinding(
            "stale",
            "Historical success is stale",
            finding_type="stale-success",
            statuses=("stale-success",),
        ),
        ScaleFinding(
            "unresolved",
            "Broader scale remains unresolved",
            statuses=("conditional-scale", "unresolved-scale"),
            unresolved_conditions=("future supply is unknown",),
        ),
    )
    calls: list[str] = []
    names = (
        "material",
        "dimensions",
        "progression",
        "timing",
        "constraint",
        "response",
        "effect",
        "limited",
        "stale",
        "unresolved",
    )
    rules = tuple(
        _rule(name, (finding,), calls)
        for name, finding in zip(names, findings, strict=True)
    )

    result = _evaluate(context, _composer(rules))

    assert result.scale_findings == findings
    assert calls == list(names)
    assert result.product_pathway is context.product_pathway
    assert result.net_overall_system_contribution is context.contribution
    assert result.transition_pathway is context.transition_pathway
    assert result.scale_findings[0].contribution_findings[0] is (
        context.contribution_finding
    )
    assert result.scale_findings[1].supporting_comparison_findings[0] is (
        context.comparison_finding
    )
    assert result.scale_findings[4].supporting_queue_results[0] is (
        context.queue_result
    )
    assert result.scale_findings[6].supporting_fabric_results[0] is (
        context.fabric_result
    )


def test_composition_preserves_order_duplicates_and_support_subsets() -> None:
    context = _context()
    duplicate = ScaleFinding(
        "duplicate",
        "Preserved duplicate",
        contribution_findings=(context.contribution_finding,),
    )
    queue_only = ScaleFinding(
        "queue-only",
        "Different material support",
        supporting_queue_results=(context.queue_result,),
    )
    calls: list[str] = []
    empty_rules = tuple(_rule(f"empty-{index}", (), calls) for index in range(8))
    rules = (
        _rule("first", (duplicate,), calls),
        _rule("second", (queue_only, duplicate), calls),
        *empty_rules,
    )

    result = _evaluate(context, _composer(rules))

    assert result.scale_findings[0] is duplicate
    assert result.scale_findings[1] is queue_only
    assert result.scale_findings[2] is duplicate
    assert result.scale_findings[0].supporting_queue_results == ()
    assert result.scale_findings[1].contribution_findings == ()


def test_scale_effects_do_not_rewrite_contribution_semantics() -> None:
    context = _context()
    scale_effect = ScaleFinding(
        "scale-effect",
        "Effect that emerges only at scale",
        scale_dependent_effects=("new delivery requirement",),
        contribution_findings=(context.contribution_finding,),
    )
    calls: list[str] = []
    rules = tuple(
        _rule(str(index), (scale_effect,) if index == 6 else (), calls)
        for index in range(10)
    )

    result = _evaluate(context, _composer(rules))

    assert result.scale_findings == (scale_effect,)
    assert context.contribution_finding.effect_description == "Established contribution"
    assert not hasattr(result, "score")
    assert not hasattr(result, "candidate_transition_pathway")
    assert not hasattr(result, "net_overall_system_risk")


def test_composer_preserves_supplied_result_context() -> None:
    context = _context()
    calls: list[str] = []
    rules = tuple(_rule(str(index), (), calls) for index in range(10))

    result = _evaluate(context, _composer(rules))

    assert result.evaluation_run_id == "run-1"
    assert result.user_id == "user-1"
    assert result.pathway_id == "pathway-1"
    assert result.evaluator_version == "scale-v1"
    assert result.rule_set_version == "scale-rules-v1"
    assert result.assumptions == ("material assumption",)
    assert result.uncertainties == ("material uncertainty",)
    assert result.evidence_references == (context.evidence,)
    assert result.provenance == (context.provenance,)
