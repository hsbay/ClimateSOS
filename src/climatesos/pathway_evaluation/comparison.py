"""Structural execution boundary for caller-supplied pathway comparison."""

from collections.abc import Callable
from dataclasses import dataclass

from .models import (
    ComparisonFinding,
    OpaqueReference,
    ProductPathway,
    SourceReference,
    TransitionPathway,
)

DirectComparisonFunction = Callable[
    [ProductPathway, TransitionPathway, OpaqueReference | None],
    tuple[ComparisonFinding, ...],
]
SubstitutionCombinationFunction = DirectComparisonFunction
DownstreamPropagationFunction = Callable[
    [
        ProductPathway,
        TransitionPathway,
        tuple[ComparisonFinding, ...],
        OpaqueReference | None,
    ],
    tuple[ComparisonFinding, ...],
]


class ComparisonInvariantError(ValueError):
    """Raised when comparison inputs or findings are structurally incoherent."""


def _require_reference_tuple(
    value: object,
    expected_type: type[OpaqueReference] | type[SourceReference],
    description: str,
) -> None:
    if not isinstance(value, tuple) or not all(
        isinstance(item, expected_type) for item in value
    ):
        raise ComparisonInvariantError(
            f"{description} must be a tuple of {expected_type.__name__} objects"
        )


def validate_comparison_findings(
    findings: object,
    pathway: ProductPathway,
    description: str,
) -> tuple[ComparisonFinding, ...]:
    """Validate finding structure and pathway-owned reference attribution."""

    if not isinstance(findings, tuple) or not all(
        isinstance(finding, ComparisonFinding) for finding in findings
    ):
        raise ComparisonInvariantError(
            f"{description} must be a tuple of ComparisonFinding objects"
        )

    objects_by_id = {item.object_id: item for item in pathway.objects}
    relationships_by_id = {item.relationship_id: item for item in pathway.relationships}
    for finding in findings:
        reference_fields = (
            (
                finding.pathway_object_references,
                OpaqueReference,
                "Pathway object references",
            ),
            (
                finding.pathway_relationship_references,
                OpaqueReference,
                "Pathway relationship references",
            ),
            (
                finding.transition_object_references,
                OpaqueReference,
                "Transition object references",
            ),
            (
                finding.transition_relationship_references,
                OpaqueReference,
                "Transition relationship references",
            ),
            (finding.system_model_basis, OpaqueReference, "System-model basis"),
            (finding.evidence_references, SourceReference, "Evidence references"),
        )
        for values, expected_type, field_description in reference_fields:
            _require_reference_tuple(values, expected_type, field_description)

        for reference in finding.pathway_object_references:
            pathway_object = objects_by_id.get(reference.reference_id)
            if pathway_object is None:
                raise ComparisonInvariantError(
                    "ComparisonFinding references an object outside the ProductPathway"
                )
            if (
                pathway_object.user_id != pathway.user_id
                or pathway_object.pathway_id != pathway.pathway_id
            ):
                raise ComparisonInvariantError(
                    "Referenced pathway object attribution must match the "
                    "ProductPathway"
                )
        for reference in finding.pathway_relationship_references:
            relationship = relationships_by_id.get(reference.reference_id)
            if relationship is None:
                raise ComparisonInvariantError(
                    "ComparisonFinding references a relationship outside the "
                    "ProductPathway"
                )
            if (
                relationship.user_id != pathway.user_id
                or relationship.pathway_id != pathway.pathway_id
            ):
                raise ComparisonInvariantError(
                    "Referenced pathway relationship attribution must match the "
                    "ProductPathway"
                )
    return findings


@dataclass(frozen=True, slots=True)
class ValidatedPathwayComparator:
    """Coordinate comparison phases without supplying comparison semantics."""

    direct_comparison_function: DirectComparisonFunction
    substitution_combination_function: SubstitutionCombinationFunction
    downstream_propagation_function: DownstreamPropagationFunction

    def compare_direct(
        self,
        pathway: ProductPathway,
        transition_pathway: TransitionPathway,
        system_context: OpaqueReference | None,
    ) -> tuple[ComparisonFinding, ...]:
        """Run caller-supplied direct comparison and validate its findings."""

        return validate_comparison_findings(
            self.direct_comparison_function(
                pathway, transition_pathway, system_context
            ),
            pathway,
            "Direct comparison findings",
        )

    def evaluate_substitution_and_combination(
        self,
        pathway: ProductPathway,
        transition_pathway: TransitionPathway,
        system_context: OpaqueReference | None,
    ) -> tuple[ComparisonFinding, ...]:
        """Run caller-supplied substitution/combination evaluation."""

        return validate_comparison_findings(
            self.substitution_combination_function(
                pathway, transition_pathway, system_context
            ),
            pathway,
            "Substitution and combination findings",
        )

    def propagate_downstream(
        self,
        pathway: ProductPathway,
        transition_pathway: TransitionPathway,
        comparison_findings: tuple[ComparisonFinding, ...],
        system_context: OpaqueReference | None,
    ) -> tuple[ComparisonFinding, ...]:
        """Run bounded caller-supplied propagation from comparison findings."""

        validated_inputs = validate_comparison_findings(
            comparison_findings,
            pathway,
            "Pathway comparison findings",
        )
        return validate_comparison_findings(
            self.downstream_propagation_function(
                pathway,
                transition_pathway,
                validated_inputs,
                system_context,
            ),
            pathway,
            "Downstream propagation findings",
        )
