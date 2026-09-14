"""Work-performing component contracts for the specified foundation.

These protocols define ownership boundaries only. Concrete evaluation rules are
absent until their semantics are specified.
"""

from typing import Protocol

from .models import (
    FinalPathwayResult,
    IdentityToken,
    InitialCharterResult,
    IntegratedCharterResult,
    NetOverallSystemContribution,
    NetOverallSystemRiskResult,
    OpaqueReference,
    PathwayEngineResult,
    ProductPathway,
    ScaleDiagnosticResult,
    SourceReference,
    TransitionPathway,
)


class NetOverallSystemContributionEvaluator(Protocol):
    """Evaluate contribution using completed engine and Integrated Charter results."""

    def evaluate(
        self,
        pathway_engine_result: PathwayEngineResult,
        integrated_charter_result: IntegratedCharterResult,
    ) -> NetOverallSystemContribution: ...


class ScaleDiagnosticEvaluator(Protocol):
    """Evaluate the scale of an established net overall system contribution."""

    def evaluate(
        self,
        net_overall_system_contribution: NetOverallSystemContribution,
        product_pathway: ProductPathway,
        transition_pathway: TransitionPathway,
        system_context: OpaqueReference | None,
        assumptions: tuple[str, ...],
        uncertainties: tuple[str, ...],
        evidence_references: tuple[SourceReference, ...],
        provenance: tuple[SourceReference, ...],
        user_id: str,
        pathway_id: str,
        evaluation_run_id: str,
    ) -> ScaleDiagnosticResult: ...


class TransitionPathwayCompiler(Protocol):
    """Compile completed evaluation into a non-authoritative transition mapping."""

    def compile(
        self,
        product_pathway: ProductPathway,
        net_overall_system_contribution: NetOverallSystemContribution,
        scale_diagnostic_result: ScaleDiagnosticResult,
        authoritative_transition_pathway: TransitionPathway,
        transition_context: OpaqueReference | None,
        system_context: OpaqueReference | None,
        conditions: tuple[str, ...],
        dependencies: tuple[OpaqueReference, ...],
        assumptions: tuple[str, ...],
        uncertainties: tuple[str, ...],
        evidence_references: tuple[SourceReference, ...],
        provenance: tuple[SourceReference, ...],
        identity_token: IdentityToken,
        evaluation_run_id: str,
        user_id: str,
        pathway_id: str,
    ) -> TransitionPathway: ...


class NetOverallSystemRiskEvaluator(Protocol):
    """Evaluate systemic risk in a completed candidate transition mapping."""

    def evaluate(
        self,
        candidate_transition_pathway: TransitionPathway,
        authoritative_transition_pathway: TransitionPathway,
        transition_context: OpaqueReference | None,
        system_context: OpaqueReference | None,
        assumptions: tuple[str, ...],
        uncertainties: tuple[str, ...],
        evidence_references: tuple[SourceReference, ...],
        provenance: tuple[SourceReference, ...],
        user_id: str,
        pathway_id: str,
        evaluation_run_id: str,
    ) -> NetOverallSystemRiskResult: ...


class FinalPathwayAssembly(Protocol):
    """Assemble completed evaluation state without re-evaluating findings."""

    def assemble(
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
    ) -> FinalPathwayResult: ...
