import inspect
from dataclasses import FrozenInstanceError, fields
from typing import TypeVar

import pytest

from climatesos.pathway_evaluation import (
    IdentityToken,
    NetOverallSystemContribution,
    OpaqueReference,
    PathwayRelationship,
    ProductPathway,
    ScaleDiagnosticResult,
    SourceReference,
    TransitionPathway,
    TransitionPathwayCompiler,
)

T = TypeVar("T")


def _record(record_type: type[T], **values: object) -> T:
    record = object.__new__(record_type)
    for name, value in values.items():
        object.__setattr__(record, name, value)
    return record


def _candidate() -> tuple[
    TransitionPathway,
    TransitionPathway,
    ProductPathway,
    NetOverallSystemContribution,
    ScaleDiagnosticResult,
    IdentityToken,
    SourceReference,
]:
    provenance = _record(SourceReference)
    identity_token = _record(IdentityToken)
    product_pathway = _record(ProductPathway)
    contribution = _record(NetOverallSystemContribution)
    authoritative = TransitionPathway(
        reference_id="authoritative-transition",
        provenance=(provenance,),
    )
    scale_result = ScaleDiagnosticResult(
        product_pathway=product_pathway,
        net_overall_system_contribution=contribution,
        transition_pathway=authoritative,
        scale_findings=(),
        evaluation_run_id="run-1",
        user_id="user-1",
        pathway_id="pathway-1",
        evaluator_version="scale-v1",
        rule_set_version="scale-rules-v1",
    )
    candidate = TransitionPathway(
        reference_id="candidate-transition",
        provenance=(provenance,),
        identity_token=identity_token,
        evaluation_run_id="run-1",
        user_id="user-1",
        pathway_id="pathway-1",
        authoritative_transition_pathway=authoritative,
        product_pathway=product_pathway,
        net_overall_system_contribution=contribution,
        scale_diagnostic_result=scale_result,
        incorporated_transition_references=(_record(OpaqueReference),),
        affected_relationships=(_record(PathwayRelationship),),
        dependencies=(_record(OpaqueReference),),
        conditions=("conditional change",),
        timing_conditions=("transition window",),
        sequencing_conditions=("dependency first",),
        contribution_conditions=("supported contribution",),
        scale_conditions=("constrained scale",),
        unchanged_transition_references=(_record(OpaqueReference),),
        unresolved_conditions=("unresolved capacity",),
        assumptions=("material assumption",),
        uncertainties=("material uncertainty",),
        evidence_references=(_record(SourceReference),),
        compiler_version="compiler-v1",
        model_version="transition-v1",
        rule_set_version="compiler-rules-v1",
    )
    return (
        candidate,
        authoritative,
        product_pathway,
        contribution,
        scale_result,
        identity_token,
        provenance,
    )


def test_candidate_reuses_immutable_transition_pathway_model() -> None:
    candidate, *_ = _candidate()

    assert type(candidate) is TransitionPathway
    with pytest.raises(FrozenInstanceError):
        candidate.reference_id = "changed"  # type: ignore[misc]


def test_candidate_preserves_required_identity_and_exact_upstream_references() -> None:
    (
        candidate,
        authoritative,
        product_pathway,
        contribution,
        scale_result,
        identity_token,
        provenance,
    ) = _candidate()

    assert candidate.identity_token is identity_token
    assert candidate.evaluation_run_id == "run-1"
    assert candidate.user_id == "user-1"
    assert candidate.pathway_id == "pathway-1"
    assert candidate.authoritative_transition_pathway is authoritative
    assert candidate.product_pathway is product_pathway
    assert candidate.net_overall_system_contribution is contribution
    assert candidate.scale_diagnostic_result is scale_result
    assert candidate.provenance[0] is provenance


def test_transition_pathway_compiler_protocol_matches_section_13() -> None:
    signature = inspect.signature(TransitionPathwayCompiler.compile)

    assert tuple(signature.parameters) == (
        "self",
        "product_pathway",
        "net_overall_system_contribution",
        "scale_diagnostic_result",
        "authoritative_transition_pathway",
        "transition_context",
        "system_context",
        "conditions",
        "dependencies",
        "assumptions",
        "uncertainties",
        "evidence_references",
        "provenance",
        "identity_token",
        "evaluation_run_id",
        "user_id",
        "pathway_id",
    )
    assert signature.return_annotation is TransitionPathway


def test_compiler_protocol_accepts_a_structurally_matching_foundation() -> None:
    candidate, *_ = _candidate()

    class CompilerFoundation:
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
            return candidate

    compiler: TransitionPathwayCompiler = CompilerFoundation()

    assert compiler.compile(
        _record(ProductPathway),
        _record(NetOverallSystemContribution),
        _record(ScaleDiagnosticResult),
        _record(TransitionPathway),
        None,
        None,
        (),
        (),
        (),
        (),
        (),
        (),
        _record(IdentityToken),
        "run-1",
        "user-1",
        "pathway-1",
    ) is candidate


def test_candidate_foundation_adds_no_downstream_or_scalar_surfaces() -> None:
    field_names = {field.name for field in fields(TransitionPathway)}

    assert field_names.isdisjoint(
        {
            "net_overall_system_risk",
            "final_pathway_result",
            "final_charter_result",
            "validator_result",
            "bound_pathway",
            "authoritative_status",
            "commitment_status",
            "score",
            "rank",
            "weight",
            "vote",
            "optimization_result",
        }
    )
