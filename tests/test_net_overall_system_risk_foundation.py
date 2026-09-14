import inspect
from dataclasses import FrozenInstanceError, fields
from typing import TypeVar

import pytest

from climatesos.pathway_evaluation import (
    ContributionFinding,
    IdentityToken,
    NetOverallSystemContribution,
    NetOverallSystemRiskEvaluator,
    NetOverallSystemRiskResult,
    OpaqueReference,
    PathwayRelationship,
    ProductPathway,
    ScaleDiagnosticResult,
    ScaleFinding,
    SourceReference,
    SystemRiskFinding,
    TransitionPathway,
)

T = TypeVar("T")


def _record(record_type: type[T], **values: object) -> T:
    record = object.__new__(record_type)
    for name, value in values.items():
        object.__setattr__(record, name, value)
    return record


def _risk_result() -> tuple[
    NetOverallSystemRiskResult,
    TransitionPathway,
    TransitionPathway,
    ContributionFinding,
    ScaleFinding,
    PathwayRelationship,
    OpaqueReference,
    SourceReference,
]:
    product_pathway = _record(ProductPathway)
    contribution = _record(NetOverallSystemContribution)
    authoritative = TransitionPathway("authoritative")
    scale_result = _record(ScaleDiagnosticResult)
    candidate = TransitionPathway(
        reference_id="candidate",
        identity_token=_record(IdentityToken),
        evaluation_run_id="run-1",
        user_id="user-1",
        pathway_id="pathway-1",
        authoritative_transition_pathway=authoritative,
        product_pathway=product_pathway,
        net_overall_system_contribution=contribution,
        scale_diagnostic_result=scale_result,
        compiler_version="compiler-v1",
        model_version="transition-v1",
        rule_set_version="compiler-rules-v1",
    )
    contribution_finding = ContributionFinding(
        finding_id="contribution-1",
        effect_description="Supported contribution",
    )
    scale_finding = ScaleFinding(
        finding_id="scale-1",
        description="Supported scale condition",
    )
    relationship = _record(PathwayRelationship)
    system_reference = _record(OpaqueReference)
    evidence = _record(SourceReference)
    provenance = _record(SourceReference)
    finding = SystemRiskFinding(
        finding_id="risk-1",
        description="One open-ended systemic risk finding",
        risk_scope="combined transition",
        risk_type="system interaction",
        risk_states=("new", "unresolved"),
        causes=("shared dependency",),
        transition_function_references=(system_reference,),
        transition_relationships=(relationship,),
        timeline_effects=("reduced schedule margin",),
        sequencing_effects=("dependency must precede deployment",),
        bottlenecks=("shared infrastructure",),
        pitfalls=("single point of failure",),
        failure_modes=("delivery failure",),
        fossil_fallback_risks=("fallback operation",),
        fossil_persistence_risks=("delayed retirement",),
        infrastructure_constraints=("interconnection",),
        finance_constraints=("capital availability",),
        workforce_constraints=("specialist capacity",),
        adequacy_constraints=("replacement adequacy",),
        delivery_constraints=("transport capacity",),
        supply_chain_constraints=("component availability",),
        other_transition_constraints=("institutional execution",),
        propagation_relationships=(relationship,),
        charter_style_findings=("biosphere integrity risk",),
        conditions=("conditional on dependency",),
        unresolved_conditions=("future capacity unknown",),
        supporting_contribution_findings=(contribution_finding,),
        supporting_scale_findings=(scale_finding,),
        supporting_system_references=(system_reference,),
        evidence_references=(evidence,),
        provenance=(provenance,),
    )
    result = NetOverallSystemRiskResult(
        candidate_transition_pathway=candidate,
        authoritative_transition_pathway=authoritative,
        risk_findings=(finding,),
        evaluation_run_id="run-1",
        user_id="user-1",
        pathway_id="pathway-1",
        evaluator_version="risk-v1",
        rule_set_version="risk-rules-v1",
        assumptions=("material assumption",),
        uncertainties=("material uncertainty",),
        evidence_references=(evidence,),
        provenance=(provenance,),
    )
    return (
        result,
        candidate,
        authoritative,
        contribution_finding,
        scale_finding,
        relationship,
        system_reference,
        evidence,
    )


def test_risk_finding_and_result_are_immutable_open_ended_records() -> None:
    result, *_ = _risk_result()
    finding = result.risk_findings[0]

    with pytest.raises(FrozenInstanceError):
        finding.description = "changed"  # type: ignore[misc]
    with pytest.raises(FrozenInstanceError):
        result.evaluation_run_id = "changed"  # type: ignore[misc]
    assert finding.risk_states == ("new", "unresolved")


def test_result_and_findings_preserve_exact_material_upstream_references() -> None:
    (
        result,
        candidate,
        authoritative,
        contribution_finding,
        scale_finding,
        relationship,
        system_reference,
        evidence,
    ) = _risk_result()
    finding = result.risk_findings[0]

    assert result.candidate_transition_pathway is candidate
    assert result.authoritative_transition_pathway is authoritative
    assert finding.supporting_contribution_findings[0] is contribution_finding
    assert finding.supporting_scale_findings[0] is scale_finding
    assert finding.transition_relationships[0] is relationship
    assert finding.supporting_system_references[0] is system_reference
    assert finding.evidence_references[0] is evidence
    assert result.evidence_references[0] is evidence


def test_risk_result_preserves_attribution_versions_evidence_and_provenance() -> None:
    result, *_ = _risk_result()

    assert result.evaluation_run_id == "run-1"
    assert result.user_id == "user-1"
    assert result.pathway_id == "pathway-1"
    assert result.evaluator_version == "risk-v1"
    assert result.rule_set_version == "risk-rules-v1"
    assert result.assumptions == ("material assumption",)
    assert result.uncertainties == ("material uncertainty",)
    assert result.provenance == result.risk_findings[0].provenance
    assert "identity_token" not in {
        field.name for field in fields(NetOverallSystemRiskResult)
    }


def test_risk_evaluator_protocol_matches_section_14() -> None:
    signature = inspect.signature(NetOverallSystemRiskEvaluator.evaluate)

    assert tuple(signature.parameters) == (
        "self",
        "candidate_transition_pathway",
        "authoritative_transition_pathway",
        "transition_context",
        "system_context",
        "assumptions",
        "uncertainties",
        "evidence_references",
        "provenance",
        "user_id",
        "pathway_id",
        "evaluation_run_id",
    )
    assert signature.return_annotation is NetOverallSystemRiskResult


def test_risk_foundation_adds_no_downstream_or_scalar_surfaces() -> None:
    result_fields = {field.name for field in fields(NetOverallSystemRiskResult)}
    finding_fields = {field.name for field in fields(SystemRiskFinding)}
    forbidden = {
        "final_pathway_result",
        "final_charter_result",
        "validator_result",
        "bound_pathway",
        "authoritative_promotion",
        "score",
        "rank",
        "weight",
        "vote",
        "optimization_result",
    }

    assert result_fields.isdisjoint(forbidden)
    assert finding_fields.isdisjoint(forbidden)
