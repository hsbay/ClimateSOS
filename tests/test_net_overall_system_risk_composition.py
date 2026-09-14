from dataclasses import fields
from typing import TypeVar

from climatesos.pathway_evaluation import (
    CompleteNetOverallSystemRiskFunction,
    ContributionFinding,
    IdentityToken,
    IntegratedCharterResult,
    NetOverallSystemContribution,
    OpaqueReference,
    PathwayEngineResult,
    PathwayRelationship,
    ProductPathway,
    ScaleDiagnosticResult,
    ScaleFinding,
    SourceReference,
    SystemRiskFinding,
    SystemRiskFindingFunction,
    TransitionPathway,
    ValidatedNetOverallSystemRiskEvaluator,
)

T = TypeVar("T")


def _record(record_type: type[T], **values: object) -> T:
    record = object.__new__(record_type)
    for name, value in values.items():
        object.__setattr__(record, name, value)
    return record


def _rule(
    name: str,
    findings: tuple[SystemRiskFinding, ...],
    calls: list[str],
) -> SystemRiskFindingFunction:
    def rule(*args: object) -> tuple[SystemRiskFinding, ...]:
        calls.append(name)
        return findings

    return rule


class _Context:
    def __init__(self) -> None:
        self.identity_token = _record(IdentityToken, token_id="lineage-1")
        self.product_pathway = _record(
            ProductPathway,
            identity_token=self.identity_token,
            evaluation_run_id="run-1",
            user_id="user-1",
            pathway_id="pathway-1",
        )
        self.authoritative = TransitionPathway(
            reference_id="authoritative",
            identity_token=_record(IdentityToken, token_id="older-lineage"),
            evaluation_run_id="older-run",
        )
        self.contribution_finding = ContributionFinding(
            finding_id="contribution-1",
            effect_description="Supported contribution",
        )
        engine_result = _record(
            PathwayEngineResult,
            identity_token=self.identity_token,
        )
        self.contribution = NetOverallSystemContribution(
            product_pathway=self.product_pathway,
            pathway_engine_result=engine_result,
            integrated_charter_result=_record(IntegratedCharterResult),
            transition_pathway=self.authoritative,
            contribution_findings=(self.contribution_finding,),
            evaluation_run_id="run-1",
            user_id="user-1",
            pathway_id="pathway-1",
            evaluator_version="contribution-v1",
            rule_set_version="contribution-rules-v1",
        )
        self.scale_finding = ScaleFinding(
            finding_id="scale-1",
            description="Supported scale condition",
        )
        self.scale_result = ScaleDiagnosticResult(
            product_pathway=self.product_pathway,
            net_overall_system_contribution=self.contribution,
            transition_pathway=self.authoritative,
            scale_findings=(self.scale_finding,),
            evaluation_run_id="run-1",
            user_id="user-1",
            pathway_id="pathway-1",
            evaluator_version="scale-v1",
            rule_set_version="scale-rules-v1",
        )
        self.relationship = _record(PathwayRelationship)
        self.system_reference = _record(OpaqueReference)
        self.evidence = _record(SourceReference)
        self.provenance = _record(SourceReference)
        self.candidate = TransitionPathway(
            reference_id="candidate",
            provenance=(self.provenance,),
            identity_token=self.identity_token,
            evaluation_run_id="run-1",
            user_id="user-1",
            pathway_id="pathway-1",
            authoritative_transition_pathway=self.authoritative,
            product_pathway=self.product_pathway,
            net_overall_system_contribution=self.contribution,
            scale_diagnostic_result=self.scale_result,
            affected_relationships=(self.relationship,),
            dependencies=(self.system_reference,),
            conditions=("candidate condition",),
            unresolved_conditions=("candidate unresolved condition",),
            evidence_references=(self.evidence,),
            compiler_version="compiler-v1",
            model_version="transition-v1",
            rule_set_version="compiler-rules-v1",
        )


def test_all_section_14_surfaces_compose_once_in_order_and_validate() -> None:
    context = _Context()
    comparison = SystemRiskFinding(
        "comparison",
        "Candidate changes reference-state risks",
        risk_states=("new", "increased", "reduced", "resolved", "transferred"),
        supporting_contribution_findings=(context.contribution_finding,),
    )
    interaction = SystemRiskFinding(
        "interaction",
        "Pathway interaction creates system risk",
        risk_scope="combined transition",
        risk_type="system interaction",
        causes=("shared transition function",),
        transition_function_references=(context.system_reference,),
        supporting_scale_findings=(context.scale_finding,),
    )
    delivery = SystemRiskFinding(
        "delivery",
        "Transition delivery constraints",
        infrastructure_constraints=("interconnection",),
        finance_constraints=("capital availability",),
        workforce_constraints=("specialist capacity",),
        adequacy_constraints=("replacement adequacy",),
        delivery_constraints=("transport capacity",),
        supply_chain_constraints=("component availability",),
        other_transition_constraints=("institutional execution",),
    )
    timing = SystemRiskFinding(
        "timing",
        "Transition timing and sequence risk",
        timeline_effects=("reduced schedule margin",),
        sequencing_effects=("dependency must complete first",),
    )
    failure = SystemRiskFinding(
        "failure",
        "Bottleneck, pitfall, and failure-mode risk",
        bottlenecks=("shared infrastructure",),
        pitfalls=("single point of failure",),
        failure_modes=("delivery failure",),
    )
    fossil = SystemRiskFinding(
        "fossil",
        "Fossil persistence and fallback risk",
        fossil_fallback_risks=("fallback operation",),
        fossil_persistence_risks=("delayed retirement",),
    )
    propagation = SystemRiskFinding(
        "propagation",
        "Dependency risk propagates across the transition",
        transition_relationships=(context.relationship,),
        propagation_relationships=(context.relationship,),
        supporting_system_references=(context.system_reference,),
    )
    biosphere = SystemRiskFinding(
        "biosphere",
        "Compound biosphere and climate-system risk",
        risk_type="biosphere and climate-system risk",
        causes=("reinforcing feedback", "threshold behavior"),
    )
    unresolved = SystemRiskFinding(
        "unresolved",
        "Charter-style and unresolved risk",
        risk_states=("unresolved",),
        charter_style_findings=("biosphere integrity risk",),
        conditions=("conditional on future evidence",),
        unresolved_conditions=("system interaction unresolved",),
        evidence_references=(context.evidence,),
        provenance=(context.provenance,),
    )
    calls: list[str] = []
    composer = CompleteNetOverallSystemRiskFunction(
        candidate_reference_risk_function=_rule(
            "comparison",
            (comparison, comparison),
            calls,
        ),
        system_interaction_risk_function=_rule(
            "interaction", (interaction,), calls
        ),
        transition_delivery_risk_function=_rule("delivery", (delivery,), calls),
        timing_sequencing_risk_function=_rule("timing", (timing,), calls),
        bottleneck_failure_risk_function=_rule("failure", (failure,), calls),
        fossil_persistence_fallback_risk_function=_rule(
            "fossil", (fossil,), calls
        ),
        dependency_propagation_risk_function=_rule(
            "propagation", (propagation,), calls
        ),
        biosphere_climate_risk_function=_rule(
            "biosphere", (biosphere,), calls
        ),
        charter_unresolved_risk_function=_rule(
            "unresolved", (unresolved,), calls
        ),
        evaluator_version="risk-v1",
        rule_set_version="risk-rules-v1",
    )

    result = ValidatedNetOverallSystemRiskEvaluator(composer).evaluate(
        context.candidate,
        context.authoritative,
        None,
        context.system_reference,
        ("material assumption",),
        ("material uncertainty",),
        (context.evidence,),
        (context.provenance,),
        "user-1",
        "pathway-1",
        "run-1",
    )

    assert result.candidate_transition_pathway is context.candidate
    assert result.authoritative_transition_pathway is context.authoritative
    assert result.risk_findings == (
        comparison,
        comparison,
        interaction,
        delivery,
        timing,
        failure,
        fossil,
        propagation,
        biosphere,
        unresolved,
    )
    assert result.risk_findings[0] is result.risk_findings[1]
    assert calls == [
        "comparison",
        "interaction",
        "delivery",
        "timing",
        "failure",
        "fossil",
        "propagation",
        "biosphere",
        "unresolved",
    ]
    assert result.evaluation_run_id == "run-1"
    assert result.user_id == "user-1"
    assert result.pathway_id == "pathway-1"
    assert result.evaluator_version == "risk-v1"
    assert result.rule_set_version == "risk-rules-v1"
    assert result.assumptions == ("material assumption",)
    assert result.uncertainties == ("material uncertainty",)
    assert result.evidence_references == (context.evidence,)
    assert result.provenance == (context.provenance,)
    assert comparison.supporting_scale_findings == ()
    assert comparison.evidence_references == ()
    assert interaction.supporting_contribution_findings == ()
    assert interaction.evidence_references == ()


def test_risk_composition_does_not_mutate_transition_states() -> None:
    context = _Context()
    calls: list[str] = []
    empty = _rule("empty", (), calls)
    composer = CompleteNetOverallSystemRiskFunction(
        candidate_reference_risk_function=empty,
        system_interaction_risk_function=empty,
        transition_delivery_risk_function=empty,
        timing_sequencing_risk_function=empty,
        bottleneck_failure_risk_function=empty,
        fossil_persistence_fallback_risk_function=empty,
        dependency_propagation_risk_function=empty,
        biosphere_climate_risk_function=empty,
        charter_unresolved_risk_function=empty,
        evaluator_version="risk-v1",
        rule_set_version="risk-rules-v1",
    )

    result = composer(
        context.candidate,
        context.authoritative,
        None,
        None,
        (),
        (),
        (),
        (),
        "user-1",
        "pathway-1",
        "run-1",
    )

    assert result.risk_findings == ()
    assert context.candidate.authoritative_transition_pathway is context.authoritative
    assert context.candidate.identity_token is context.identity_token
    assert context.authoritative.evaluation_run_id == "older-run"
    assert context.authoritative.authoritative_transition_pathway is None


def test_composer_adds_no_downstream_or_scalar_operations() -> None:
    field_names = {field.name for field in fields(CompleteNetOverallSystemRiskFunction)}
    forbidden = {
        "final_pathway_assembly",
        "final_charter",
        "promotion",
        "validator",
        "binding",
        "pathway_assessment",
        "score",
        "rank",
        "weight",
        "vote",
        "optimization",
        "scalar_aggregation",
    }

    assert field_names.isdisjoint(forbidden)
