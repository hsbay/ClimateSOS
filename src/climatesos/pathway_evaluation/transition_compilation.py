"""Validated boundary for caller-supplied candidate transition compilation."""

from collections.abc import Callable
from dataclasses import dataclass
from typing import TypeVar

from .models import (
    IdentityToken,
    NetOverallSystemContribution,
    OpaqueReference,
    PathwayRelationship,
    ProductPathway,
    ScaleDiagnosticResult,
    SourceReference,
    TransitionPathway,
)

TransitionPathwayCompilationFunction = Callable[
    [
        ProductPathway,
        NetOverallSystemContribution,
        ScaleDiagnosticResult,
        TransitionPathway,
        OpaqueReference | None,
        OpaqueReference | None,
        tuple[str, ...],
        tuple[OpaqueReference, ...],
        tuple[str, ...],
        tuple[str, ...],
        tuple[SourceReference, ...],
        tuple[SourceReference, ...],
        IdentityToken,
        str,
        str,
        str,
    ],
    object,
]

T = TypeVar("T")


class TransitionPathwayCompilationInvariantError(ValueError):
    """Raised when compilation inputs or candidate output are incoherent."""


def _require_tuple_of(
    value: object,
    expected_type: type[T],
    description: str,
) -> tuple[T, ...]:
    if not isinstance(value, tuple) or not all(
        isinstance(item, expected_type) for item in value
    ):
        raise TransitionPathwayCompilationInvariantError(
            f"{description} must be a tuple of {expected_type.__name__} objects"
        )
    return value


@dataclass(frozen=True, slots=True)
class ValidatedTransitionPathwayCompiler:
    """Validate inputs and a caller-supplied candidate transition mapping."""

    compilation_function: TransitionPathwayCompilationFunction

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
    ) -> TransitionPathway:
        """Invoke compilation without supplying transition-change semantics."""

        self._validate_inputs(
            product_pathway,
            net_overall_system_contribution,
            scale_diagnostic_result,
            authoritative_transition_pathway,
            transition_context,
            system_context,
            conditions,
            dependencies,
            assumptions,
            uncertainties,
            evidence_references,
            provenance,
            identity_token,
            evaluation_run_id,
            user_id,
            pathway_id,
        )
        raw_candidate = self.compilation_function(
            product_pathway,
            net_overall_system_contribution,
            scale_diagnostic_result,
            authoritative_transition_pathway,
            transition_context,
            system_context,
            conditions,
            dependencies,
            assumptions,
            uncertainties,
            evidence_references,
            provenance,
            identity_token,
            evaluation_run_id,
            user_id,
            pathway_id,
        )
        if type(raw_candidate) is not TransitionPathway:
            raise TransitionPathwayCompilationInvariantError(
                "Transition compilation must return exactly TransitionPathway"
            )
        self._validate_candidate(
            raw_candidate,
            product_pathway,
            net_overall_system_contribution,
            scale_diagnostic_result,
            authoritative_transition_pathway,
            identity_token,
            evaluation_run_id,
            user_id,
            pathway_id,
        )
        return raw_candidate

    @staticmethod
    def _validate_inputs(
        product_pathway: ProductPathway,
        contribution: NetOverallSystemContribution,
        scale_result: ScaleDiagnosticResult,
        authoritative_pathway: TransitionPathway,
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
    ) -> None:
        exact_inputs = (
            (product_pathway, ProductPathway, "ProductPathway"),
            (
                contribution,
                NetOverallSystemContribution,
                "NetOverallSystemContribution",
            ),
            (scale_result, ScaleDiagnosticResult, "ScaleDiagnosticResult"),
            (
                authoritative_pathway,
                TransitionPathway,
                "authoritative TransitionPathway",
            ),
            (identity_token, IdentityToken, "IdentityToken"),
        )
        for value, expected_type, description in exact_inputs:
            if type(value) is not expected_type:
                raise TransitionPathwayCompilationInvariantError(
                    f"Compilation requires exactly {description}"
                )
        if any(
            context is not None and not isinstance(context, OpaqueReference)
            for context in (transition_context, system_context)
        ):
            raise TransitionPathwayCompilationInvariantError(
                "Transition and system context must be OpaqueReference or None"
            )
        _require_tuple_of(conditions, str, "Compilation conditions")
        _require_tuple_of(dependencies, OpaqueReference, "Compilation dependencies")
        _require_tuple_of(assumptions, str, "Compilation assumptions")
        _require_tuple_of(uncertainties, str, "Compilation uncertainties")
        _require_tuple_of(
            evidence_references,
            SourceReference,
            "Compilation evidence references",
        )
        _require_tuple_of(provenance, SourceReference, "Compilation provenance")
        if not all(
            isinstance(value, str)
            for value in (evaluation_run_id, user_id, pathway_id)
        ):
            raise TransitionPathwayCompilationInvariantError(
                "Compilation attribution values must be strings"
            )

        if scale_result.product_pathway is not product_pathway:
            raise TransitionPathwayCompilationInvariantError(
                "Scale result must preserve the supplied ProductPathway"
            )
        if scale_result.net_overall_system_contribution is not contribution:
            raise TransitionPathwayCompilationInvariantError(
                "Scale result must preserve the supplied contribution"
            )
        if scale_result.transition_pathway is not authoritative_pathway:
            raise TransitionPathwayCompilationInvariantError(
                "Scale result must preserve the authoritative TransitionPathway"
            )
        if contribution.product_pathway is not product_pathway:
            raise TransitionPathwayCompilationInvariantError(
                "Contribution must preserve the supplied ProductPathway"
            )
        if contribution.transition_pathway is not authoritative_pathway:
            raise TransitionPathwayCompilationInvariantError(
                "Contribution must preserve the authoritative TransitionPathway"
            )

        if any(
            artifact.evaluation_run_id != evaluation_run_id
            for artifact in (product_pathway, contribution, scale_result)
        ):
            raise TransitionPathwayCompilationInvariantError(
                "Current evaluation artifacts must share evaluation_run_id"
            )
        if any(
            artifact.user_id != user_id
            for artifact in (product_pathway, contribution, scale_result)
        ):
            raise TransitionPathwayCompilationInvariantError(
                "Current evaluation artifacts must share user_id"
            )
        if any(
            artifact.pathway_id != pathway_id
            for artifact in (product_pathway, contribution, scale_result)
        ):
            raise TransitionPathwayCompilationInvariantError(
                "Current evaluation artifacts must share pathway_id"
            )
        token_id = identity_token.token_id
        if (
            product_pathway.identity_token.token_id != token_id
            or contribution.pathway_engine_result.identity_token.token_id != token_id
        ):
            raise TransitionPathwayCompilationInvariantError(
                "Compilation inputs must share the current evaluation lineage"
            )

    @staticmethod
    def _validate_candidate(
        candidate: TransitionPathway,
        product_pathway: ProductPathway,
        contribution: NetOverallSystemContribution,
        scale_result: ScaleDiagnosticResult,
        authoritative_pathway: TransitionPathway,
        identity_token: IdentityToken,
        evaluation_run_id: str,
        user_id: str,
        pathway_id: str,
    ) -> None:
        if candidate is authoritative_pathway:
            raise TransitionPathwayCompilationInvariantError(
                "Compiled candidate must be distinct from authoritative state"
            )
        exact_references = (
            (
                candidate.authoritative_transition_pathway,
                authoritative_pathway,
                "authoritative TransitionPathway",
            ),
            (candidate.product_pathway, product_pathway, "ProductPathway"),
            (
                candidate.net_overall_system_contribution,
                contribution,
                "NetOverallSystemContribution",
            ),
            (
                candidate.scale_diagnostic_result,
                scale_result,
                "ScaleDiagnosticResult",
            ),
        )
        for actual, expected, description in exact_references:
            if actual is not expected:
                raise TransitionPathwayCompilationInvariantError(
                    f"Candidate must preserve exact {description}"
                )
        if (
            candidate.identity_token is None
            or candidate.identity_token.token_id != identity_token.token_id
        ):
            raise TransitionPathwayCompilationInvariantError(
                "Candidate must preserve current evaluation lineage"
            )
        if candidate.evaluation_run_id != evaluation_run_id:
            raise TransitionPathwayCompilationInvariantError(
                "Candidate must preserve evaluation_run_id"
            )
        if candidate.user_id != user_id:
            raise TransitionPathwayCompilationInvariantError(
                "Candidate must preserve user_id"
            )
        if candidate.pathway_id != pathway_id:
            raise TransitionPathwayCompilationInvariantError(
                "Candidate must preserve pathway_id"
            )
        if not isinstance(candidate.reference_id, str):
            raise TransitionPathwayCompilationInvariantError(
                "Candidate reference_id must be a string"
            )

        opaque_collections = (
            candidate.incorporated_transition_references,
            candidate.dependencies,
            candidate.unchanged_transition_references,
        )
        if any(
            not isinstance(values, tuple)
            or not all(isinstance(value, OpaqueReference) for value in values)
            for values in opaque_collections
        ):
            raise TransitionPathwayCompilationInvariantError(
                "Candidate transition reference collections must contain "
                "OpaqueReference objects"
            )
        _require_tuple_of(
            candidate.affected_relationships,
            PathwayRelationship,
            "Candidate affected relationships",
        )
        text_collections = (
            candidate.conditions,
            candidate.timing_conditions,
            candidate.sequencing_conditions,
            candidate.contribution_conditions,
            candidate.scale_conditions,
            candidate.unresolved_conditions,
            candidate.assumptions,
            candidate.uncertainties,
        )
        if any(
            not isinstance(values, tuple)
            or not all(isinstance(value, str) for value in values)
            for values in text_collections
        ):
            raise TransitionPathwayCompilationInvariantError(
                "Candidate condition collections must be tuples of strings"
            )
        _require_tuple_of(
            candidate.evidence_references,
            SourceReference,
            "Candidate evidence references",
        )
        _require_tuple_of(
            candidate.provenance,
            SourceReference,
            "Candidate provenance",
        )
        if not all(
            isinstance(version, str)
            for version in (
                candidate.compiler_version,
                candidate.model_version,
                candidate.rule_set_version,
            )
        ):
            raise TransitionPathwayCompilationInvariantError(
                "Candidate compiler, model, and rule-set versions must be strings"
            )
