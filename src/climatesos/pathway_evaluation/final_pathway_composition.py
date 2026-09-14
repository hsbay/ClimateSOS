"""Deterministic composition of the Section 15 final pathway result."""

from collections.abc import Callable
from dataclasses import dataclass

from .models import (
    EvaluationTrace,
    FinalPathwayResult,
    IdentityToken,
    InitialCharterResult,
    IntegratedCharterResult,
    NetOverallSystemContribution,
    NetOverallSystemRiskResult,
    PathwayEngineResult,
    ProductPathway,
    ScaleDiagnosticResult,
    TransitionPathway,
)

FinalPathwayVersionFunction = Callable[
    [
        ProductPathway,
        TransitionPathway,
        TransitionPathway,
        NetOverallSystemRiskResult,
        InitialCharterResult,
        PathwayEngineResult,
        IntegratedCharterResult,
        NetOverallSystemContribution,
        ScaleDiagnosticResult,
        IdentityToken,
        str,
        str,
        str,
    ],
    str,
]


@dataclass(frozen=True, slots=True)
class CompleteFinalPathwayAssemblyFunction:
    """Compose one result using explicit caller-supplied version rules."""

    assembly_version_function: FinalPathwayVersionFunction
    assembly_rule_version_function: FinalPathwayVersionFunction

    def __call__(
        self,
        product_pathway: ProductPathway,
        authoritative_transition_pathway: TransitionPathway,
        candidate_transition_pathway: TransitionPathway,
        net_overall_system_risk_result: NetOverallSystemRiskResult,
        initial_charter_result: InitialCharterResult,
        pathway_engine_result: PathwayEngineResult,
        integrated_charter_result: IntegratedCharterResult,
        net_overall_system_contribution: NetOverallSystemContribution,
        scale_diagnostic_result: ScaleDiagnosticResult,
        identity_token: IdentityToken,
        evaluation_run_id: str,
        user_id: str,
        pathway_id: str,
    ) -> FinalPathwayResult:
        """Execute each configured rule once and preserve exact upstream state."""

        arguments = (
            product_pathway,
            authoritative_transition_pathway,
            candidate_transition_pathway,
            net_overall_system_risk_result,
            initial_charter_result,
            pathway_engine_result,
            integrated_charter_result,
            net_overall_system_contribution,
            scale_diagnostic_result,
            identity_token,
            evaluation_run_id,
            user_id,
            pathway_id,
        )
        assembly_version = self.assembly_version_function(*arguments)
        assembly_rule_version = self.assembly_rule_version_function(*arguments)
        evaluation_trace = EvaluationTrace(
            initial_charter_result=initial_charter_result,
            pathway_engine_result=pathway_engine_result,
            integrated_charter_result=integrated_charter_result,
            net_overall_system_contribution=net_overall_system_contribution,
            scale_diagnostic_result=scale_diagnostic_result,
        )
        return FinalPathwayResult(
            product_pathway=product_pathway,
            authoritative_transition_pathway=authoritative_transition_pathway,
            candidate_transition_pathway=candidate_transition_pathway,
            net_overall_system_risk_result=net_overall_system_risk_result,
            evaluation_trace=evaluation_trace,
            identity_token=identity_token,
            evaluation_run_id=evaluation_run_id,
            user_id=user_id,
            pathway_id=pathway_id,
            assembly_version=assembly_version,
            assembly_rule_version=assembly_rule_version,
        )
