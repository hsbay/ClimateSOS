from dataclasses import FrozenInstanceError, dataclass, fields
from typing import TypeVar, cast

import pytest

from climatesos.pathway_evaluation import (
    CandidateTransitionRuleFunction,
    IdentityToken,
    NetOverallSystemContribution,
    OpaqueReference,
    PathwayEngineResult,
    PathwayRelationship,
    ProductPathway,
    ScaleDiagnosticResult,
    SourceReference,
    TransitionPathway,
    TransitionPathwayCompilationInvariantError,
    TransitionPathwayCompiler,
)

T = TypeVar("T")


def _record(record_type: type[T], **values: object) -> T:
    record = object.__new__(record_type)
    for name, value in values.items():
        object.__setattr__(record, name, value)
    return record


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
        self.pathway_engine_result = _record(
            PathwayEngineResult,
            identity_token=self.identity_token,
        )
        self.authoritative_provenance = _record(SourceReference)
        self.authoritative = TransitionPathway(
            reference_id="authoritative",
            provenance=(self.authoritative_provenance,),
            identity_token=_record(IdentityToken, token_id="older-lineage"),
            evaluation_run_id="older-run",
            user_id="global-user",
            pathway_id="global-pathway",
        )
        self.contribution = _record(
            NetOverallSystemContribution,
            product_pathway=self.product_pathway,
            pathway_engine_result=self.pathway_engine_result,
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


class _Rule:
    def __init__(self, output: object = ()) -> None:
        self.output = output
        self.calls: list[tuple[object, ...]] = []

    def __call__(self, *args: object) -> object:
        self.calls.append(args)
        return self.output


@dataclass(frozen=True)
class _Rules:
    incorporated: _Rule
    relationships: _Rule
    dependencies: _Rule
    conditions: _Rule
    timing: _Rule
    sequencing: _Rule
    contribution: _Rule
    scale: _Rule
    unchanged: _Rule
    unresolved: _Rule

    @property
    def all(self) -> tuple[_Rule, ...]:
        return (
            self.incorporated,
            self.relationships,
            self.dependencies,
            self.conditions,
            self.timing,
            self.sequencing,
            self.contribution,
            self.scale,
            self.unchanged,
            self.unresolved,
        )


def _compiler(
    *,
    incorporated: object = (),
    relationships: object = (),
    dependencies: object = (),
    conditions: object = (),
    timing: object = (),
    sequencing: object = (),
    contribution: object = (),
    scale: object = (),
    unchanged: object = (),
    unresolved: object = (),
) -> tuple[TransitionPathwayCompiler, _Rules]:
    rules = _Rules(
        incorporated=_Rule(incorporated),
        relationships=_Rule(relationships),
        dependencies=_Rule(dependencies),
        conditions=_Rule(conditions),
        timing=_Rule(timing),
        sequencing=_Rule(sequencing),
        contribution=_Rule(contribution),
        scale=_Rule(scale),
        unchanged=_Rule(unchanged),
        unresolved=_Rule(unresolved),
    )

    compiler = TransitionPathwayCompiler(
        incorporated_transition_function=cast(
            CandidateTransitionRuleFunction[OpaqueReference],
            rules.incorporated,
        ),
        affected_relationship_function=cast(
            CandidateTransitionRuleFunction[PathwayRelationship],
            rules.relationships,
        ),
        dependency_function=cast(
            CandidateTransitionRuleFunction[OpaqueReference],
            rules.dependencies,
        ),
        condition_function=cast(
            CandidateTransitionRuleFunction[str],
            rules.conditions,
        ),
        timing_condition_function=cast(
            CandidateTransitionRuleFunction[str],
            rules.timing,
        ),
        sequencing_condition_function=cast(
            CandidateTransitionRuleFunction[str],
            rules.sequencing,
        ),
        contribution_condition_function=cast(
            CandidateTransitionRuleFunction[str],
            rules.contribution,
        ),
        scale_condition_function=cast(
            CandidateTransitionRuleFunction[str],
            rules.scale,
        ),
        unchanged_transition_function=cast(
            CandidateTransitionRuleFunction[OpaqueReference],
            rules.unchanged,
        ),
        unresolved_condition_function=cast(
            CandidateTransitionRuleFunction[str],
            rules.unresolved,
        ),
        reference_id="candidate-1",
        compiler_version="compiler-v1",
        model_version="transition-model-v1",
        rule_set_version="compiler-rules-v1",
    )
    return compiler, rules


def _compile(
    context: _Context,
    compiler: TransitionPathwayCompiler,
    *,
    evaluation_run_id: str = "run-1",
    user_id: str = "user-1",
    pathway_id: str = "pathway-1",
) -> TransitionPathway:
    return compiler.compile(
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
        evaluation_run_id,
        user_id,
        pathway_id,
    )


def test_compiler_constructs_candidate_and_preserves_exact_upstream_context() -> None:
    context = _Context()
    compiler, rules = _compiler()

    candidate = _compile(context, compiler)

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
    assert candidate.reference_id == "candidate-1"
    assert candidate.compiler_version == "compiler-v1"
    assert candidate.model_version == "transition-model-v1"
    assert candidate.rule_set_version == "compiler-rules-v1"
    assert all(len(rule.calls) == 1 for rule in rules.all)


def test_authoritative_pathway_may_have_older_lineage_and_run() -> None:
    context = _Context()
    compiler, _ = _compiler()

    assert context.authoritative.identity_token is not context.identity_token
    assert context.authoritative.identity_token.token_id == "older-lineage"
    assert context.authoritative.evaluation_run_id == "older-run"

    candidate = _compile(context, compiler)

    assert candidate.authoritative_transition_pathway is context.authoritative


@pytest.mark.parametrize(
    ("attribute", "value"),
    [
        ("evaluation_run_id", "other-run"),
        ("user_id", "other-user"),
        ("pathway_id", "other-pathway"),
    ],
)
def test_input_attribution_mismatches_reject_before_rule_execution(
    attribute: str,
    value: str,
) -> None:
    context = _Context()
    compiler, rules = _compiler()

    with pytest.raises(TransitionPathwayCompilationInvariantError):
        _compile(context, compiler, **{attribute: value})

    assert all(rule.calls == [] for rule in rules.all)


def test_incorrect_current_lineage_rejects_before_rule_execution() -> None:
    context = _Context()
    context.product_pathway = _record(
        ProductPathway,
        identity_token=_record(IdentityToken, token_id="other-lineage"),
        evaluation_run_id="run-1",
        user_id="user-1",
        pathway_id="pathway-1",
    )
    compiler, rules = _compiler()

    with pytest.raises(TransitionPathwayCompilationInvariantError):
        _compile(context, compiler)

    assert all(rule.calls == [] for rule in rules.all)


@pytest.mark.parametrize(
    ("domain", "invalid"),
    [
        ("incorporated", ("not-an-opaque-reference",)),
        ("relationships", ("not-a-relationship",)),
        ("dependencies", ("not-an-opaque-reference",)),
        ("conditions", (_record(OpaqueReference),)),
        ("timing", (_record(OpaqueReference),)),
        ("sequencing", (_record(OpaqueReference),)),
        ("contribution", (_record(OpaqueReference),)),
        ("scale", (_record(OpaqueReference),)),
        ("unchanged", ("not-an-opaque-reference",)),
        ("unresolved", (_record(OpaqueReference),)),
    ],
)
def test_each_rule_output_must_match_its_declared_type(
    domain: str,
    invalid: object,
) -> None:
    context = _Context()
    compiler, _ = _compiler(**{domain: invalid})

    with pytest.raises(TransitionPathwayCompilationInvariantError):
        _compile(context, compiler)


def test_all_section_13_surfaces_are_composed_deterministically() -> None:
    context = _Context()
    incorporated = _record(OpaqueReference)
    relationship_two = _record(PathwayRelationship)
    relationship_one = _record(PathwayRelationship)
    compiled_dependency = _record(OpaqueReference)
    unchanged = _record(OpaqueReference)

    compiler, rules = _compiler(
        incorporated=(incorporated, incorporated),
        relationships=(relationship_two, relationship_one),
        dependencies=(compiled_dependency, compiled_dependency),
        conditions=("compiled condition", "compiled condition"),
        timing=("required transition window",),
        sequencing=("infrastructure first",),
        contribution=("supported contribution condition",),
        scale=("constrained scale condition",),
        unchanged=(unchanged, unchanged),
        unresolved=("unresolved capacity",),
    )

    candidate = _compile(context, compiler)

    assert candidate.incorporated_transition_references == (
        incorporated,
        incorporated,
    )
    assert candidate.affected_relationships == (
        relationship_two,
        relationship_one,
    )
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
    assert candidate.contribution_conditions == ("supported contribution condition",)
    assert candidate.scale_conditions == ("constrained scale condition",)
    assert candidate.unchanged_transition_references == (
        unchanged,
        unchanged,
    )
    assert candidate.unresolved_conditions == ("unresolved capacity",)
    assert candidate.assumptions == ("supplied assumption",)
    assert candidate.uncertainties == ("supplied uncertainty",)
    assert candidate.evidence_references == (context.evidence,)
    assert candidate.provenance == (context.provenance,)

    # All sibling compiler rules must execute exactly once, but runtime
    # scheduling order is intentionally not part of the contract.
    assert all(len(rule.calls) == 1 for rule in rules.all)


def test_duplicate_and_supplied_values_are_preserved() -> None:
    context = _Context()
    dependency = _record(OpaqueReference)
    compiler, _ = _compiler(
        dependencies=(dependency, dependency),
        conditions=("repeat", "repeat"),
    )

    candidate = _compile(context, compiler)

    assert candidate.dependencies == (
        context.input_dependency,
        dependency,
        dependency,
    )
    assert candidate.conditions == (
        "supplied condition",
        "repeat",
        "repeat",
    )


def test_compilation_leaves_authoritative_transition_unchanged() -> None:
    context = _Context()
    compiler, _ = _compiler()

    candidate = _compile(context, compiler)

    assert candidate is not context.authoritative
    assert context.authoritative.reference_id == "authoritative"
    assert context.authoritative.provenance == (context.authoritative_provenance,)
    assert context.authoritative.authoritative_transition_pathway is None
    assert context.authoritative.incorporated_transition_references == ()


def test_rule_exception_propagates_unchanged() -> None:
    context = _Context()
    failure = RuntimeError("compiler rule failed")

    def fail(*_args: object) -> tuple[OpaqueReference, ...]:
        raise failure

    compiler, _ = _compiler()
    compiler = TransitionPathwayCompiler(
        incorporated_transition_function=fail,
        affected_relationship_function=compiler.affected_relationship_function,
        dependency_function=compiler.dependency_function,
        condition_function=compiler.condition_function,
        timing_condition_function=compiler.timing_condition_function,
        sequencing_condition_function=compiler.sequencing_condition_function,
        contribution_condition_function=compiler.contribution_condition_function,
        scale_condition_function=compiler.scale_condition_function,
        unchanged_transition_function=compiler.unchanged_transition_function,
        unresolved_condition_function=compiler.unresolved_condition_function,
        reference_id=compiler.reference_id,
        compiler_version=compiler.compiler_version,
        model_version=compiler.model_version,
        rule_set_version=compiler.rule_set_version,
    )

    with pytest.raises(RuntimeError) as caught:
        _compile(context, compiler)

    assert caught.value is failure


def test_compiler_is_immutable() -> None:
    compiler, _ = _compiler()

    with pytest.raises(FrozenInstanceError):
        compiler.reference_id = "changed"  # type: ignore[misc]


def test_compiler_adds_no_authority_downstream_or_scalar_surfaces() -> None:
    field_names = {field.name for field in fields(TransitionPathwayCompiler)}
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
