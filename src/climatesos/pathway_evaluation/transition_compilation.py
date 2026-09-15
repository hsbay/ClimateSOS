"""Candidate TransitionPathway compilation and invariant enforcement."""

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

T = TypeVar("T")

CandidateTransitionRuleFunction = Callable[
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
    tuple[T, ...],
]


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
class TransitionPathwayCompiler:
    """Compile evaluated pathway effects into one non-authoritative candidate."""

    # Transition-function, dependency, and unchanged-state references remain
    # opaque because the current Product Pathway Evaluation model defines no
    # concrete TransitionFunction, Dependency, or TransitionElement artifact.
    # Concrete PathwayRelationship objects are preserved wherever the modeled
    # artifact exists.
    incorporated_transition_function: CandidateTransitionRuleFunction[OpaqueReference]
    affected_relationship_function: CandidateTransitionRuleFunction[PathwayRelationship]
    dependency_function: CandidateTransitionRuleFunction[OpaqueReference]
    condition_function: CandidateTransitionRuleFunction[str]
    timing_condition_function: CandidateTransitionRuleFunction[str]
    sequencing_condition_function: CandidateTransitionRuleFunction[str]
    contribution_condition_function: CandidateTransitionRuleFunction[str]
    scale_condition_function: CandidateTransitionRuleFunction[str]
    unchanged_transition_function: CandidateTransitionRuleFunction[OpaqueReference]
    unresolved_condition_function: CandidateTransitionRuleFunction[str]
    reference_id: str
    compiler_version: str
    model_version: str
    rule_set_version: str

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
        """Compile, validate, and return one candidate transition state."""

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

        arguments = (
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

        # These rules derive sibling pieces of one candidate from the same
        # completed upstream evaluation state. Runtime scheduling is not part
        # of the compiler contract; each output must satisfy its own declared
        # artifact/reference type before candidate construction.
        incorporated_transition_references = _require_tuple_of(
            self.incorporated_transition_function(*arguments),
            OpaqueReference,
            "Incorporated transition references",
        )
        affected_relationships = _require_tuple_of(
            self.affected_relationship_function(*arguments),
            PathwayRelationship,
            "Affected relationships",
        )
        compiled_dependencies = _require_tuple_of(
            self.dependency_function(*arguments),
            OpaqueReference,
            "Compiled dependency references",
        )
        compiled_conditions = _require_tuple_of(
            self.condition_function(*arguments),
            str,
            "Compiled conditions",
        )
        timing_conditions = _require_tuple_of(
            self.timing_condition_function(*arguments),
            str,
            "Timing conditions",
        )
        sequencing_conditions = _require_tuple_of(
            self.sequencing_condition_function(*arguments),
            str,
            "Sequencing conditions",
        )
        contribution_conditions = _require_tuple_of(
            self.contribution_condition_function(*arguments),
            str,
            "Contribution conditions",
        )
        scale_conditions = _require_tuple_of(
            self.scale_condition_function(*arguments),
            str,
            "Scale conditions",
        )
        unchanged_transition_references = _require_tuple_of(
            self.unchanged_transition_function(*arguments),
            OpaqueReference,
            "Unchanged transition references",
        )
        unresolved_conditions = _require_tuple_of(
            self.unresolved_condition_function(*arguments),
            str,
            "Unresolved conditions",
        )

        candidate = TransitionPathway(
            reference_id=self.reference_id,
            provenance=provenance,
            identity_token=identity_token,
            evaluation_run_id=evaluation_run_id,
            user_id=user_id,
            pathway_id=pathway_id,
            authoritative_transition_pathway=authoritative_transition_pathway,
            product_pathway=product_pathway,
            net_overall_system_contribution=net_overall_system_contribution,
            scale_diagnostic_result=scale_diagnostic_result,
            incorporated_transition_references=incorporated_transition_references,
            affected_relationships=affected_relationships,
            dependencies=dependencies + compiled_dependencies,
            conditions=conditions + compiled_conditions,
            timing_conditions=timing_conditions,
            sequencing_conditions=sequencing_conditions,
            contribution_conditions=contribution_conditions,
            scale_conditions=scale_conditions,
            unchanged_transition_references=unchanged_transition_references,
            unresolved_conditions=unresolved_conditions,
            assumptions=assumptions,
            uncertainties=uncertainties,
            evidence_references=evidence_references,
            compiler_version=self.compiler_version,
            model_version=self.model_version,
            rule_set_version=self.rule_set_version,
        )

        self._validate_candidate(
            candidate,
            product_pathway,
            net_overall_system_contribution,
            scale_diagnostic_result,
            authoritative_transition_pathway,
            identity_token,
            evaluation_run_id,
            user_id,
            pathway_id,
        )
        return candidate

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
            isinstance(value, str) for value in (evaluation_run_id, user_id, pathway_id)
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
