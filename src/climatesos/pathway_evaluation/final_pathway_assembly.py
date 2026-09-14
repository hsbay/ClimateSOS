"""Validated boundary for caller-supplied final pathway assembly."""

from collections.abc import Callable
from dataclasses import dataclass
from typing import TypeVar

from .models import (
    Attribute,
    CharterCheckResult,
    ComparisonFinding,
    ContributionFinding,
    DocumentationFinding,
    EvaluationTrace,
    FabricEvaluatorResult,
    FinalPathwayResult,
    IdentityToken,
    InitialCharterResult,
    IntegratedCharterResult,
    NetOverallSystemContribution,
    NetOverallSystemRiskResult,
    OpaqueReference,
    PathwayEngineResult,
    PathwayObject,
    PathwayRelationship,
    ProductAdapterResult,
    ProductPathway,
    QueueElement,
    QueueEvaluatorResult,
    ScaleDiagnosticResult,
    ScaleFinding,
    SourceReference,
    SystemRiskFinding,
    TransitionPathway,
)

FinalPathwayAssemblyFunction = Callable[
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
    object,
]

T = TypeVar("T")


class FinalPathwayAssemblyInvariantError(ValueError):
    """Raised when final-pathway inputs or output are structurally incoherent."""


def _require_tuple_of(
    value: object,
    expected_type: type[T],
    description: str,
) -> tuple[T, ...]:
    if not isinstance(value, tuple) or not all(
        isinstance(item, expected_type) for item in value
    ):
        raise FinalPathwayAssemblyInvariantError(
            f"{description} must be a tuple of {expected_type.__name__} objects"
        )
    return value


def _require_versions(*versions: object) -> None:
    if not all(isinstance(version, str) for version in versions):
        raise FinalPathwayAssemblyInvariantError("Artifact versions must be strings")


@dataclass(frozen=True, slots=True)
class ValidatedFinalPathwayAssembly:
    """Validate structural integrity around final pathway assembly."""

    assembly_function: FinalPathwayAssemblyFunction

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
    ) -> FinalPathwayResult:
        """Invoke assembly once after validating the completed evaluation state."""

        self._validate_inputs(
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
        raw_result = self.assembly_function(
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
        if type(raw_result) is not FinalPathwayResult:
            raise FinalPathwayAssemblyInvariantError(
                "Assembly must return exactly FinalPathwayResult"
            )
        self._validate_result(
            raw_result,
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
        return raw_result

    @classmethod
    def _validate_inputs(
        cls,
        product: ProductPathway,
        authoritative: TransitionPathway,
        candidate: TransitionPathway,
        risk: NetOverallSystemRiskResult,
        initial: InitialCharterResult,
        engine: PathwayEngineResult,
        integrated: IntegratedCharterResult,
        contribution: NetOverallSystemContribution,
        scale: ScaleDiagnosticResult,
        identity_token: IdentityToken,
        evaluation_run_id: str,
        user_id: str,
        pathway_id: str,
    ) -> None:
        expected_types = (
            (product, ProductPathway),
            (authoritative, TransitionPathway),
            (candidate, TransitionPathway),
            (risk, NetOverallSystemRiskResult),
            (initial, InitialCharterResult),
            (engine, PathwayEngineResult),
            (integrated, IntegratedCharterResult),
            (contribution, NetOverallSystemContribution),
            (scale, ScaleDiagnosticResult),
            (identity_token, IdentityToken),
        )
        if any(type(value) is not expected for value, expected in expected_types):
            raise FinalPathwayAssemblyInvariantError(
                "Assembly inputs must use their exact Packet 11A artifact types"
            )
        if not all(
            isinstance(value, str)
            for value in (evaluation_run_id, user_id, pathway_id)
        ):
            raise FinalPathwayAssemblyInvariantError(
                "Assembly attribution values must be strings"
            )
        cls._validate_relationships(
            product,
            authoritative,
            candidate,
            risk,
            initial,
            engine,
            integrated,
            contribution,
            scale,
        )
        cls._validate_attribution(
            product,
            candidate,
            risk,
            initial,
            engine,
            integrated,
            contribution,
            scale,
            identity_token,
            evaluation_run_id,
            user_id,
            pathway_id,
        )
        cls._validate_structures(
            product,
            authoritative,
            candidate,
            risk,
            initial,
            engine,
            integrated,
            contribution,
            scale,
        )

    @staticmethod
    def _validate_relationships(
        product: ProductPathway,
        authoritative: TransitionPathway,
        candidate: TransitionPathway,
        risk: NetOverallSystemRiskResult,
        initial: InitialCharterResult,
        engine: PathwayEngineResult,
        integrated: IntegratedCharterResult,
        contribution: NetOverallSystemContribution,
        scale: ScaleDiagnosticResult,
    ) -> None:
        relationships = (
            (candidate is not authoritative, "Candidate must be non-authoritative"),
            (
                candidate.authoritative_transition_pathway is authoritative,
                "Candidate must preserve authoritative TransitionPathway",
            ),
            (
                candidate.product_pathway is product,
                "Candidate must preserve ProductPathway",
            ),
            (
                candidate.net_overall_system_contribution is contribution,
                "Candidate must preserve NetOverallSystemContribution",
            ),
            (
                candidate.scale_diagnostic_result is scale,
                "Candidate must preserve ScaleDiagnosticResult",
            ),
            (
                risk.candidate_transition_pathway is candidate,
                "Risk result must preserve candidate TransitionPathway",
            ),
            (
                risk.authoritative_transition_pathway is authoritative,
                "Risk result must preserve authoritative TransitionPathway",
            ),
            (engine.product_pathway is product, "Engine must preserve ProductPathway"),
            (
                engine.transition_pathway is authoritative,
                "Engine must preserve authoritative TransitionPathway",
            ),
            (
                engine.initial_charter_result is initial,
                "Engine must preserve InitialCharterResult",
            ),
            (
                integrated.pathway_engine_result is engine,
                "Integrated Charter must preserve PathwayEngineResult",
            ),
            (
                integrated.initial_charter_result is initial,
                "Integrated Charter must preserve InitialCharterResult",
            ),
            (
                contribution.product_pathway is product,
                "Contribution must preserve ProductPathway",
            ),
            (
                contribution.pathway_engine_result is engine,
                "Contribution must preserve PathwayEngineResult",
            ),
            (
                contribution.integrated_charter_result is integrated,
                "Contribution must preserve IntegratedCharterResult",
            ),
            (
                contribution.transition_pathway is authoritative,
                "Contribution must preserve authoritative TransitionPathway",
            ),
            (scale.product_pathway is product, "Scale must preserve ProductPathway"),
            (
                scale.net_overall_system_contribution is contribution,
                "Scale must preserve NetOverallSystemContribution",
            ),
            (
                scale.transition_pathway is authoritative,
                "Scale must preserve authoritative TransitionPathway",
            ),
        )
        for valid, message in relationships:
            if not valid:
                raise FinalPathwayAssemblyInvariantError(message)

    @staticmethod
    def _validate_attribution(
        product: ProductPathway,
        candidate: TransitionPathway,
        risk: NetOverallSystemRiskResult,
        initial: InitialCharterResult,
        engine: PathwayEngineResult,
        integrated: IntegratedCharterResult,
        contribution: NetOverallSystemContribution,
        scale: ScaleDiagnosticResult,
        identity_token: IdentityToken,
        evaluation_run_id: str,
        user_id: str,
        pathway_id: str,
    ) -> None:
        run_artifacts = (
            product,
            candidate,
            risk,
            initial,
            engine,
            integrated,
            contribution,
            scale,
        )
        if any(
            artifact.evaluation_run_id != evaluation_run_id
            for artifact in run_artifacts
        ):
            raise FinalPathwayAssemblyInvariantError(
                "Current assembly artifacts must share evaluation_run_id"
            )
        attributed_artifacts = (product, candidate, risk, engine, contribution, scale)
        if any(artifact.user_id != user_id for artifact in attributed_artifacts):
            raise FinalPathwayAssemblyInvariantError(
                "Current assembly artifacts must share user_id"
            )
        if any(artifact.pathway_id != pathway_id for artifact in attributed_artifacts):
            raise FinalPathwayAssemblyInvariantError(
                "Current assembly artifacts must share pathway_id"
            )
        token_id = identity_token.token_id
        lineage_tokens = (
            product.identity_token,
            candidate.identity_token,
            initial.identity_token,
            engine.identity_token,
            integrated.identity_token,
        )
        if not isinstance(token_id, str) or any(
            type(token) is not IdentityToken or token.token_id != token_id
            for token in lineage_tokens
        ):
            raise FinalPathwayAssemblyInvariantError(
                "Current assembly artifacts must share IdentityToken lineage"
            )

    @staticmethod
    def _validate_structures(
        product: ProductPathway,
        authoritative: TransitionPathway,
        candidate: TransitionPathway,
        risk: NetOverallSystemRiskResult,
        initial: InitialCharterResult,
        engine: PathwayEngineResult,
        integrated: IntegratedCharterResult,
        contribution: NetOverallSystemContribution,
        scale: ScaleDiagnosticResult,
    ) -> None:
        _require_tuple_of(product.objects, PathwayObject, "Product objects")
        _require_tuple_of(
            product.relationships, PathwayRelationship, "Product relationships"
        )
        _require_tuple_of(
            product.queue_elements, QueueElement, "Product queue elements"
        )
        _require_tuple_of(product.assumptions, str, "Product assumptions")
        _require_tuple_of(product.uncertainties, str, "Product uncertainties")
        _require_tuple_of(
            product.documentation_references,
            SourceReference,
            "Product documentation references",
        )
        _require_tuple_of(
            product.evidence_references, SourceReference, "Product evidence references"
        )
        if not isinstance(product.pathway_type, str) or any(
            value is not None and not isinstance(value, str)
            for value in (
                product.time_window,
                product.geographic_scope,
                product.system_scope,
            )
        ):
            raise FinalPathwayAssemblyInvariantError(
                "Product pathway type and scopes must be structurally valid"
            )
        if not isinstance(authoritative.reference_id, str):
            raise FinalPathwayAssemblyInvariantError(
                "Authoritative TransitionPathway must preserve reference identity"
            )
        _require_tuple_of(
            authoritative.provenance,
            SourceReference,
            "Authoritative TransitionPathway provenance",
        )
        if not isinstance(candidate.reference_id, str):
            raise FinalPathwayAssemblyInvariantError(
                "Candidate TransitionPathway reference identity must be a string"
            )
        _require_tuple_of(
            candidate.incorporated_transition_references,
            OpaqueReference,
            "Candidate incorporated transition references",
        )
        _require_tuple_of(
            candidate.affected_relationships,
            PathwayRelationship,
            "Candidate affected relationships",
        )
        _require_tuple_of(
            candidate.dependencies, OpaqueReference, "Candidate dependencies"
        )
        for values, description in (
            (candidate.assumptions, "Candidate assumptions"),
            (candidate.uncertainties, "Candidate uncertainties"),
            (candidate.conditions, "Candidate conditions"),
            (candidate.timing_conditions, "Candidate timing conditions"),
            (candidate.sequencing_conditions, "Candidate sequencing conditions"),
            (candidate.contribution_conditions, "Candidate contribution conditions"),
            (candidate.scale_conditions, "Candidate scale conditions"),
            (candidate.unresolved_conditions, "Candidate unresolved conditions"),
        ):
            _require_tuple_of(values, str, description)
        _require_tuple_of(
            candidate.unchanged_transition_references,
            OpaqueReference,
            "Candidate unchanged transition references",
        )
        _require_tuple_of(
            candidate.evidence_references,
            SourceReference,
            "Candidate evidence references",
        )
        _require_tuple_of(candidate.provenance, SourceReference, "Candidate provenance")
        _require_versions(
            candidate.compiler_version,
            candidate.model_version,
            candidate.rule_set_version,
        )

        if type(initial.adapter_result) is not ProductAdapterResult:
            raise FinalPathwayAssemblyInvariantError(
                "Initial Charter must preserve exactly ProductAdapterResult"
            )
        if initial.adapter_result.product_pathway is not product:
            raise FinalPathwayAssemblyInvariantError(
                "Initial Charter adapter result must preserve ProductPathway"
            )
        _require_tuple_of(initial.check_results, CharterCheckResult, "Initial checks")
        _require_versions(initial.evaluator_version, initial.rule_set_version)
        if not isinstance(initial.status, str) or (
            initial.execution_error is not None
            and not isinstance(initial.execution_error, str)
        ):
            raise FinalPathwayAssemblyInvariantError(
                "Initial Charter status fields must be structurally valid"
            )
        _require_tuple_of(
            engine.direct_comparison_findings,
            ComparisonFinding,
            "Engine direct comparison findings",
        )
        _require_tuple_of(
            engine.substitution_combination_findings,
            ComparisonFinding,
            "Engine substitution-combination findings",
        )
        _require_tuple_of(
            engine.downstream_propagation_findings,
            ComparisonFinding,
            "Engine downstream propagation findings",
        )
        _require_tuple_of(
            engine.queue_results, QueueEvaluatorResult, "Engine queue results"
        )
        _require_tuple_of(
            engine.fabric_results, FabricEvaluatorResult, "Engine fabric results"
        )
        _require_tuple_of(
            engine.documentation_findings,
            DocumentationFinding,
            "Engine documentation findings",
        )
        _require_tuple_of(
            engine.evaluator_versions, Attribute, "Engine evaluator versions"
        )
        _require_tuple_of(
            engine.rule_set_versions, Attribute, "Engine rule-set versions"
        )
        _require_tuple_of(engine.assumptions, str, "Engine assumptions")
        _require_tuple_of(engine.uncertainties, str, "Engine uncertainties")
        _require_tuple_of(
            engine.unresolved_conditions, str, "Engine unresolved conditions"
        )
        _require_tuple_of(
            engine.evidence_references,
            SourceReference,
            "Engine evidence references",
        )
        _require_tuple_of(engine.provenance, SourceReference, "Engine provenance")
        _require_tuple_of(
            integrated.check_results, CharterCheckResult, "Integrated checks"
        )
        _require_versions(integrated.evaluator_version, integrated.rule_set_version)
        if not isinstance(integrated.status, str) or (
            integrated.execution_error is not None
            and not isinstance(integrated.execution_error, str)
        ):
            raise FinalPathwayAssemblyInvariantError(
                "Integrated Charter status fields must be structurally valid"
            )

        for artifact, findings, finding_type, label in (
            (
                contribution,
                contribution.contribution_findings,
                ContributionFinding,
                "Contribution",
            ),
            (scale, scale.scale_findings, ScaleFinding, "Scale"),
            (risk, risk.risk_findings, SystemRiskFinding, "Risk"),
        ):
            _require_tuple_of(findings, finding_type, f"{label} findings")
            _require_tuple_of(artifact.assumptions, str, f"{label} assumptions")
            _require_tuple_of(artifact.uncertainties, str, f"{label} uncertainties")
            _require_tuple_of(
                artifact.evidence_references,
                SourceReference,
                f"{label} evidence references",
            )
            _require_tuple_of(
                artifact.provenance, SourceReference, f"{label} provenance"
            )
            _require_versions(artifact.evaluator_version, artifact.rule_set_version)

    @staticmethod
    def _validate_result(
        result: FinalPathwayResult,
        product: ProductPathway,
        authoritative: TransitionPathway,
        candidate: TransitionPathway,
        risk: NetOverallSystemRiskResult,
        initial: InitialCharterResult,
        engine: PathwayEngineResult,
        integrated: IntegratedCharterResult,
        contribution: NetOverallSystemContribution,
        scale: ScaleDiagnosticResult,
        identity_token: IdentityToken,
        evaluation_run_id: str,
        user_id: str,
        pathway_id: str,
    ) -> None:
        primary_references = (
            (result.product_pathway, product),
            (result.authoritative_transition_pathway, authoritative),
            (result.candidate_transition_pathway, candidate),
            (result.net_overall_system_risk_result, risk),
        )
        if any(actual is not expected for actual, expected in primary_references):
            raise FinalPathwayAssemblyInvariantError(
                "Final result must preserve exact primary artifact references"
            )
        if type(result.evaluation_trace) is not EvaluationTrace:
            raise FinalPathwayAssemblyInvariantError(
                "Final result must contain exactly EvaluationTrace"
            )
        trace_references = (
            (result.evaluation_trace.initial_charter_result, initial),
            (result.evaluation_trace.pathway_engine_result, engine),
            (result.evaluation_trace.integrated_charter_result, integrated),
            (result.evaluation_trace.net_overall_system_contribution, contribution),
            (result.evaluation_trace.scale_diagnostic_result, scale),
        )
        if any(actual is not expected for actual, expected in trace_references):
            raise FinalPathwayAssemblyInvariantError(
                "EvaluationTrace must preserve exact upstream artifact references"
            )
        if (
            type(result.identity_token) is not IdentityToken
            or result.identity_token.token_id != identity_token.token_id
        ):
            raise FinalPathwayAssemblyInvariantError(
                "Final result must preserve IdentityToken lineage"
            )
        if (
            result.evaluation_run_id != evaluation_run_id
            or result.user_id != user_id
            or result.pathway_id != pathway_id
        ):
            raise FinalPathwayAssemblyInvariantError(
                "Final result must preserve current-run attribution"
            )
        _require_versions(result.assembly_version, result.assembly_rule_version)
