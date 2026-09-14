from dataclasses import fields
from typing import TypeVar

from climatesos.pathway_evaluation import (
    CandidateTransitionRuleFunction,
    CompleteTransitionPathwayCompilationFunction,
    IdentityToken,
    NetOverallSystemContribution,
    OpaqueReference,
    PathwayEngineResult,
    PathwayRelationship,
    ProductPathway,
    ScaleDiagnosticResult,
    SourceReference,
    TransitionPathway,
    ValidatedTransitionPathwayCompiler,
)

T = TypeVar("T")


def _record(record_type: type[T], **values: object) -> T:
    record = object.__new__(record_type)
    for name, value in values.items():
        object.__setattr__(record, name, value)
    return record


def _rule(
    name: str,
    values: tuple[T, ...],
    calls: list[str],
) -> CandidateTransitionRuleFunction[T]:
    def rule(*args: object) -> tuple[T, ...]:
        calls.append(name)
        return values

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
        engine_result = _record(
            PathwayEngineResult,
            identity_token=self.identity_token,
        )
        self.authoritative_provenance = _record(SourceReference)
        self.authoritative = TransitionPathway(
            reference_id="authoritative",
            provenance=(self.authoritative_provenance,),
            identity_token=_record(IdentityToken, token_id="older-lineage"),
            evaluation_run_id="older-run",
        )
        self.contribution = _record(
            NetOverallSystemContribution,
            product_pathway=self.product_pathway,
            pathway_engine_result=engine_result,
            transition_pathway=self.authoritative,
            evaluation_run_id="run-1",
            user_id="user-1",
            pathway_id="pathway-1",
        )
        self.scale_result = ScaleDiagnosticResult(
            product_pathway=self.product_pathway,
            net_overall_system_contribution=self.contribution,
            transition_pathway=self.authoritative,
            scale_findings=(),
            evaluation_run_id="run-1",
            user_id="user-1",
            pathway_id="pathway-1",
            evaluator_version="scale-v1",
            rule_set_version="scale-rules-v1",
        )
        self.transition_context = _record(OpaqueReference)
        self.system_context = _record(OpaqueReference)
        self.input_dependency = _record(OpaqueReference)
        self.evidence = _record(SourceReference)
        self.provenance = _record(SourceReference)


def test_all_section_13_surfaces_compose_through_validated_boundary() -> None:
    context = _Context()
    calls: list[str] = []
    incorporated = _record(OpaqueReference)
    relationship_two = _record(PathwayRelationship)
    relationship_one = _record(PathwayRelationship)
    compiled_dependency = _record(OpaqueReference)
    unchanged = _record(OpaqueReference)
    composer = CompleteTransitionPathwayCompilationFunction(
        incorporated_transition_function=_rule(
            "incorporated",
            (incorporated, incorporated),
            calls,
        ),
        affected_relationship_function=_rule(
            "relationships",
            (relationship_two, relationship_one),
            calls,
        ),
        dependency_function=_rule(
            "dependencies",
            (compiled_dependency, compiled_dependency),
            calls,
        ),
        condition_function=_rule(
            "conditions",
            ("compiled condition", "compiled condition"),
            calls,
        ),
        timing_condition_function=_rule(
            "timing",
            ("required transition window",),
            calls,
        ),
        sequencing_condition_function=_rule(
            "sequencing",
            ("infrastructure first",),
            calls,
        ),
        contribution_condition_function=_rule(
            "contribution",
            ("supported contribution condition",),
            calls,
        ),
        scale_condition_function=_rule(
            "scale",
            ("constrained scale condition",),
            calls,
        ),
        unchanged_transition_function=_rule(
            "unchanged",
            (unchanged, unchanged),
            calls,
        ),
        unresolved_condition_function=_rule(
            "unresolved",
            ("unresolved capacity",),
            calls,
        ),
        reference_id="candidate-1",
        compiler_version="compiler-v1",
        model_version="transition-model-v1",
        rule_set_version="compiler-rules-v1",
    )
    compiler = ValidatedTransitionPathwayCompiler(composer)

    candidate = compiler.compile(
        context.product_pathway,
        context.contribution,
        context.scale_result,
        context.authoritative,
        context.transition_context,
        context.system_context,
        ("supplied condition",),
        (context.input_dependency,),
        ("supplied assumption",),
        ("supplied uncertainty",),
        (context.evidence,),
        (context.provenance,),
        context.identity_token,
        "run-1",
        "user-1",
        "pathway-1",
    )

    assert type(candidate) is TransitionPathway
    assert candidate is not context.authoritative
    assert candidate.authoritative_transition_pathway is context.authoritative
    assert candidate.product_pathway is context.product_pathway
    assert candidate.net_overall_system_contribution is context.contribution
    assert candidate.scale_diagnostic_result is context.scale_result
    assert candidate.identity_token is context.identity_token
    assert candidate.evaluation_run_id == "run-1"
    assert candidate.user_id == "user-1"
    assert candidate.pathway_id == "pathway-1"
    assert candidate.incorporated_transition_references == (
        incorporated,
        incorporated,
    )
    assert candidate.affected_relationships == (relationship_two, relationship_one)
    assert candidate.dependencies == (
        context.input_dependency,
        compiled_dependency,
        compiled_dependency,
    )
    assert candidate.conditions == (
        "supplied condition",
        "compiled condition",
        "compiled condition",
    )
    assert candidate.timing_conditions == ("required transition window",)
    assert candidate.sequencing_conditions == ("infrastructure first",)
    assert candidate.contribution_conditions == (
        "supported contribution condition",
    )
    assert candidate.scale_conditions == ("constrained scale condition",)
    assert candidate.unchanged_transition_references == (unchanged, unchanged)
    assert candidate.unresolved_conditions == ("unresolved capacity",)
    assert candidate.assumptions == ("supplied assumption",)
    assert candidate.uncertainties == ("supplied uncertainty",)
    assert candidate.evidence_references == (context.evidence,)
    assert candidate.provenance == (context.provenance,)
    assert candidate.compiler_version == "compiler-v1"
    assert candidate.model_version == "transition-model-v1"
    assert candidate.rule_set_version == "compiler-rules-v1"
    assert calls == [
        "incorporated",
        "relationships",
        "dependencies",
        "conditions",
        "timing",
        "sequencing",
        "contribution",
        "scale",
        "unchanged",
        "unresolved",
    ]


def test_composition_leaves_authoritative_transition_unchanged() -> None:
    context = _Context()
    calls: list[str] = []
    empty_opaque: CandidateTransitionRuleFunction[OpaqueReference] = _rule(
        "opaque", (), calls
    )
    empty_relationship: CandidateTransitionRuleFunction[PathwayRelationship] = (
        _rule("relationship", (), calls)
    )
    empty_text: CandidateTransitionRuleFunction[str] = _rule("text", (), calls)
    composer = CompleteTransitionPathwayCompilationFunction(
        incorporated_transition_function=empty_opaque,
        affected_relationship_function=empty_relationship,
        dependency_function=empty_opaque,
        condition_function=empty_text,
        timing_condition_function=empty_text,
        sequencing_condition_function=empty_text,
        contribution_condition_function=empty_text,
        scale_condition_function=empty_text,
        unchanged_transition_function=empty_opaque,
        unresolved_condition_function=empty_text,
        reference_id="candidate-2",
        compiler_version="compiler-v1",
        model_version="transition-model-v1",
        rule_set_version="compiler-rules-v1",
    )

    candidate = ValidatedTransitionPathwayCompiler(composer).compile(
        context.product_pathway,
        context.contribution,
        context.scale_result,
        context.authoritative,
        None,
        None,
        (),
        (),
        (),
        (),
        (),
        (),
        context.identity_token,
        "run-1",
        "user-1",
        "pathway-1",
    )

    assert candidate is not context.authoritative
    assert context.authoritative.reference_id == "authoritative"
    assert context.authoritative.provenance == (context.authoritative_provenance,)
    assert context.authoritative.authoritative_transition_pathway is None
    assert context.authoritative.incorporated_transition_references == ()


def test_composer_introduces_no_authority_downstream_or_scalar_operations() -> None:
    field_names = {
        field.name for field in fields(CompleteTransitionPathwayCompilationFunction)
    }
    forbidden = {
        "authoritative_promotion",
        "risk_evaluation",
        "final_assembly",
        "final_charter",
        "validator",
        "binding",
        "score",
        "rank",
        "weight",
        "vote",
        "optimization",
    }

    assert field_names.isdisjoint(forbidden)
