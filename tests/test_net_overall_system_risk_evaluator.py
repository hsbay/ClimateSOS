from collections import Counter
from dataclasses import FrozenInstanceError, fields, replace
from typing import TypeVar, cast

import pytest

from climatesos.pathway_evaluation import (
    ContributionFinding,
    IdentityToken,
    IntegratedCharterResult,
    NetOverallSystemContribution,
    NetOverallSystemRiskEvaluationInvariantError,
    NetOverallSystemRiskEvaluator,
    NetOverallSystemRiskResult,
    OpaqueReference,
    PathwayEngineResult,
    PathwayRelationship,
    ProductPathway,
    ScaleDiagnosticResult,
    ScaleFinding,
    SourceReference,
    SystemRiskFinding,
    SystemRiskFindingFunction,
    TransitionPathway,
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
        self.authoritative = TransitionPathway(
            reference_id="authoritative",
            identity_token=_record(IdentityToken, token_id="older-lineage"),
            evaluation_run_id="older-run",
            user_id="global-user",
            pathway_id="global-pathway",
        )
        self.contribution_finding = ContributionFinding(
            finding_id="contribution-1",
            effect_description="Supported contribution",
        )
        engine_result = _record(
            PathwayEngineResult,
            identity_token=self.identity_token,
        )
        self.contribution = NetOverallSystemContribution(
            product_pathway=self.product_pathway,
            pathway_engine_result=engine_result,
            integrated_charter_result=_record(IntegratedCharterResult),
            transition_pathway=self.authoritative,
            contribution_findings=(self.contribution_finding,),
            evaluation_run_id="run-1",
            user_id="user-1",
            pathway_id="pathway-1",
            evaluator_version="contribution-v1",
            rule_set_version="contribution-rules-v1",
        )
        self.scale_finding = ScaleFinding(
            finding_id="scale-1",
            description="Supported scale condition",
        )
        self.scale_result = ScaleDiagnosticResult(
            product_pathway=self.product_pathway,
            net_overall_system_contribution=self.contribution,
            transition_pathway=self.authoritative,
            scale_findings=(self.scale_finding,),
            evaluation_run_id="run-1",
            user_id="user-1",
            pathway_id="pathway-1",
            evaluator_version="scale-v1",
            rule_set_version="scale-rules-v1",
        )
        self.relationship = _record(PathwayRelationship)
        self.system_reference = _record(OpaqueReference)
        self.evidence = _record(SourceReference)
        self.provenance = _record(SourceReference)
        self.candidate = TransitionPathway(
            reference_id="candidate",
            provenance=(self.provenance,),
            identity_token=self.identity_token,
            evaluation_run_id="run-1",
            user_id="user-1",
            pathway_id="pathway-1",
            authoritative_transition_pathway=self.authoritative,
            product_pathway=self.product_pathway,
            net_overall_system_contribution=self.contribution,
            scale_diagnostic_result=self.scale_result,
            affected_relationships=(self.relationship,),
            dependencies=(self.system_reference,),
            conditions=("candidate condition",),
            unresolved_conditions=("candidate unresolved condition",),
            evidence_references=(self.evidence,),
            compiler_version="compiler-v1",
            model_version="transition-v1",
            rule_set_version="compiler-rules-v1",
        )

    def finding(self, **overrides: object) -> SystemRiskFinding:
        values: dict[str, object] = {
            "finding_id": "risk-1",
            "description": "Completed adverse and unresolved risk",
            "risk_states": ("increased", "unresolved"),
            "transition_relationships": (self.relationship,),
            "propagation_relationships": (self.relationship,),
            "supporting_contribution_findings": (self.contribution_finding,),
            "supporting_scale_findings": (self.scale_finding,),
            "supporting_system_references": (self.system_reference,),
            "evidence_references": (self.evidence,),
            "provenance": (self.provenance,),
        }
        values.update(overrides)
        return SystemRiskFinding(**values)  # type: ignore[arg-type]


class _Rule:
    def __init__(
        self,
        name: str,
        output: object = (),
        calls: list[str] | None = None,
    ) -> None:
        self.name = name
        self.output = output
        self.calls = calls

    def __call__(self, *args: object) -> object:
        if self.calls is not None:
            self.calls.append(self.name)
        return self.output


def _evaluator(
    *,
    candidate_reference: object = (),
    system_interaction: object = (),
    transition_delivery: object = (),
    timing_sequencing: object = (),
    bottleneck_failure: object = (),
    fossil_persistence_fallback: object = (),
    dependency_propagation: object = (),
    biosphere_climate: object = (),
    charter_unresolved: object = (),
    calls: list[str] | None = None,
) -> tuple[NetOverallSystemRiskEvaluator, tuple[_Rule, ...]]:
    rules = (
        _Rule("candidate-reference", candidate_reference, calls),
        _Rule("system-interaction", system_interaction, calls),
        _Rule("transition-delivery", transition_delivery, calls),
        _Rule("timing-sequencing", timing_sequencing, calls),
        _Rule("bottleneck-failure", bottleneck_failure, calls),
        _Rule(
            "fossil-persistence-fallback",
            fossil_persistence_fallback,
            calls,
        ),
        _Rule("dependency-propagation", dependency_propagation, calls),
        _Rule("biosphere-climate", biosphere_climate, calls),
        _Rule("charter-unresolved", charter_unresolved, calls),
    )

    evaluator = NetOverallSystemRiskEvaluator(
        candidate_reference_risk_function=cast(
            SystemRiskFindingFunction,
            rules[0],
        ),
        system_interaction_risk_function=cast(
            SystemRiskFindingFunction,
            rules[1],
        ),
        transition_delivery_risk_function=cast(
            SystemRiskFindingFunction,
            rules[2],
        ),
        timing_sequencing_risk_function=cast(
            SystemRiskFindingFunction,
            rules[3],
        ),
        bottleneck_failure_risk_function=cast(
            SystemRiskFindingFunction,
            rules[4],
        ),
        fossil_persistence_fallback_risk_function=cast(
            SystemRiskFindingFunction,
            rules[5],
        ),
        dependency_propagation_risk_function=cast(
            SystemRiskFindingFunction,
            rules[6],
        ),
        biosphere_climate_risk_function=cast(
            SystemRiskFindingFunction,
            rules[7],
        ),
        charter_unresolved_risk_function=cast(
            SystemRiskFindingFunction,
            rules[8],
        ),
        evaluator_version="risk-v1",
        rule_set_version="risk-rules-v1",
    )
    return evaluator, rules


def _evaluate(
    context: _Context,
    evaluator: NetOverallSystemRiskEvaluator,
    *,
    candidate: TransitionPathway | None = None,
    authoritative: TransitionPathway | None = None,
    evaluation_run_id: str = "run-1",
    user_id: str = "user-1",
    pathway_id: str = "pathway-1",
) -> NetOverallSystemRiskResult:
    return evaluator.evaluate(
        candidate or context.candidate,
        authoritative or context.authoritative,
        None,
        context.system_reference,
        ("risk assumption",),
        ("risk uncertainty",),
        (context.evidence,),
        (context.provenance,),
        user_id,
        pathway_id,
        evaluation_run_id,
    )


def test_evaluator_constructs_result_and_preserves_exact_upstream_context() -> None:
    context = _Context()
    finding = context.finding()
    evaluator, rules = _evaluator(candidate_reference=(finding,))

    result = _evaluate(context, evaluator)

    assert type(result) is NetOverallSystemRiskResult
    assert result.candidate_transition_pathway is context.candidate
    assert result.authoritative_transition_pathway is context.authoritative
    assert result.risk_findings == (finding,)
    assert result.risk_findings[0] is finding
    assert context.candidate.product_pathway is context.product_pathway
    assert context.candidate.net_overall_system_contribution is context.contribution
    assert context.candidate.scale_diagnostic_result is context.scale_result
    assert result.evaluation_run_id == "run-1"
    assert result.user_id == "user-1"
    assert result.pathway_id == "pathway-1"
    assert result.evaluator_version == "risk-v1"
    assert result.rule_set_version == "risk-rules-v1"
    assert result.assumptions == ("risk assumption",)
    assert result.uncertainties == ("risk uncertainty",)
    assert result.evidence_references == (context.evidence,)
    assert result.provenance == (context.provenance,)
    assert all(len(rule.calls or []) == 0 for rule in rules)


def test_authoritative_pathway_may_retain_older_lineage_and_run() -> None:
    context = _Context()
    evaluator, _ = _evaluator(candidate_reference=(context.finding(),))

    assert context.authoritative.identity_token is not context.identity_token
    assert context.authoritative.identity_token.token_id == "older-lineage"
    assert context.authoritative.evaluation_run_id == "older-run"

    result = _evaluate(context, evaluator)

    assert result.authoritative_transition_pathway is context.authoritative


@pytest.mark.parametrize(
    ("candidate_field", "replacement_factory"),
    [
        ("product_pathway", lambda: _record(ProductPathway)),
        (
            "net_overall_system_contribution",
            lambda: _record(NetOverallSystemContribution),
        ),
        ("scale_diagnostic_result", lambda: _record(ScaleDiagnosticResult)),
        (
            "authoritative_transition_pathway",
            lambda: TransitionPathway("authoritative"),
        ),
    ],
)
def test_reconstructed_candidate_upstream_references_reject_before_rules(
    candidate_field: str,
    replacement_factory: object,
) -> None:
    context = _Context()
    candidate = replace(context.candidate)

    if candidate_field == "net_overall_system_contribution":
        replacement_value: object = replace(context.contribution)
    elif candidate_field == "scale_diagnostic_result":
        replacement_value = replace(
            context.scale_result,
            net_overall_system_contribution=replace(context.contribution),
        )
    else:
        replacement_value = cast(
            "object",
            replacement_factory(),
        )  # type: ignore[operator]

    object.__setattr__(candidate, candidate_field, replacement_value)

    calls: list[str] = []
    evaluator, _ = _evaluator(calls=calls)

    with pytest.raises(NetOverallSystemRiskEvaluationInvariantError):
        _evaluate(context, evaluator, candidate=candidate)

    assert calls == []


@pytest.mark.parametrize(
    ("attribute", "value"),
    [
        ("evaluation_run_id", "other-run"),
        ("user_id", "other-user"),
        ("pathway_id", "other-pathway"),
    ],
)
def test_input_attribution_mismatches_reject_before_rules(
    attribute: str,
    value: str,
) -> None:
    context = _Context()
    calls: list[str] = []
    evaluator, _ = _evaluator(calls=calls)

    kwargs = {attribute: value}
    with pytest.raises(NetOverallSystemRiskEvaluationInvariantError):
        _evaluate(context, evaluator, **kwargs)

    assert calls == []


def test_incorrect_current_lineage_rejects_before_rules() -> None:
    context = _Context()
    candidate = replace(
        context.candidate,
        identity_token=_record(IdentityToken, token_id="other-lineage"),
    )
    calls: list[str] = []
    evaluator, _ = _evaluator(calls=calls)

    with pytest.raises(NetOverallSystemRiskEvaluationInvariantError):
        _evaluate(context, evaluator, candidate=candidate)

    assert calls == []


@pytest.mark.parametrize(
    "domain",
    [
        "candidate_reference",
        "system_interaction",
        "transition_delivery",
        "timing_sequencing",
        "bottleneck_failure",
        "fossil_persistence_fallback",
        "dependency_propagation",
        "biosphere_climate",
        "charter_unresolved",
    ],
)
def test_each_risk_domain_requires_tuple_of_system_risk_findings(
    domain: str,
) -> None:
    context = _Context()
    evaluator, _ = _evaluator(**{domain: ("not-a-risk-finding",)})

    with pytest.raises(NetOverallSystemRiskEvaluationInvariantError):
        _evaluate(context, evaluator)


def test_all_section_14_surfaces_aggregate_deterministically() -> None:
    context = _Context()

    comparison = SystemRiskFinding(
        "comparison",
        "Candidate changes reference-state risks",
        risk_states=("new", "increased", "reduced", "resolved", "transferred"),
        supporting_contribution_findings=(context.contribution_finding,),
    )
    interaction = SystemRiskFinding(
        "interaction",
        "Pathway interaction creates system risk",
        risk_scope="combined transition",
        risk_type="system interaction",
        causes=("shared transition function",),
        transition_function_references=(context.system_reference,),
        supporting_scale_findings=(context.scale_finding,),
    )
    delivery = SystemRiskFinding(
        "delivery",
        "Transition delivery constraints",
        infrastructure_constraints=("interconnection",),
        finance_constraints=("capital availability",),
        workforce_constraints=("specialist capacity",),
        adequacy_constraints=("replacement adequacy",),
        delivery_constraints=("transport capacity",),
        supply_chain_constraints=("component availability",),
        other_transition_constraints=("institutional execution",),
    )
    timing = SystemRiskFinding(
        "timing",
        "Transition timing and sequence risk",
        timeline_effects=("reduced schedule margin",),
        sequencing_effects=("dependency must complete first",),
    )
    failure = SystemRiskFinding(
        "failure",
        "Bottleneck, pitfall, and failure-mode risk",
        bottlenecks=("shared infrastructure",),
        pitfalls=("single point of failure",),
        failure_modes=("delivery failure",),
    )
    fossil = SystemRiskFinding(
        "fossil",
        "Fossil persistence and fallback risk",
        fossil_fallback_risks=("fallback operation",),
        fossil_persistence_risks=("delayed retirement",),
    )
    propagation = SystemRiskFinding(
        "propagation",
        "Dependency risk propagates across the transition",
        transition_relationships=(context.relationship,),
        propagation_relationships=(context.relationship,),
        supporting_system_references=(context.system_reference,),
    )
    biosphere = SystemRiskFinding(
        "biosphere",
        "Compound biosphere and climate-system risk",
        risk_type="biosphere and climate-system risk",
        causes=("reinforcing feedback", "threshold behavior"),
    )
    unresolved = SystemRiskFinding(
        "unresolved",
        "Charter-style and unresolved risk",
        risk_states=("unresolved",),
        charter_style_findings=("biosphere integrity risk",),
        conditions=("conditional on future evidence",),
        unresolved_conditions=("system interaction unresolved",),
        evidence_references=(context.evidence,),
        provenance=(context.provenance,),
    )

    calls: list[str] = []
    evaluator, _ = _evaluator(
        candidate_reference=(comparison, comparison),
        system_interaction=(interaction,),
        transition_delivery=(delivery,),
        timing_sequencing=(timing,),
        bottleneck_failure=(failure,),
        fossil_persistence_fallback=(fossil,),
        dependency_propagation=(propagation,),
        biosphere_climate=(biosphere,),
        charter_unresolved=(unresolved,),
        calls=calls,
    )

    result = _evaluate(context, evaluator)

    assert result.risk_findings == (
        comparison,
        comparison,
        interaction,
        delivery,
        timing,
        failure,
        fossil,
        propagation,
        biosphere,
        unresolved,
    )
    assert result.risk_findings[0] is result.risk_findings[1]

    # Every sibling domain executes exactly once. Runtime scheduling order is
    # deliberately not part of the architectural contract.
    expected_domains = {
        "candidate-reference",
        "system-interaction",
        "transition-delivery",
        "timing-sequencing",
        "bottleneck-failure",
        "fossil-persistence-fallback",
        "dependency-propagation",
        "biosphere-climate",
        "charter-unresolved",
    }
    assert Counter(calls) == Counter({name: 1 for name in expected_domains})


@pytest.mark.parametrize("support_kind", ["type", "contribution", "scale"])
def test_invalid_finding_material_support_rejects(
    support_kind: str,
) -> None:
    context = _Context()

    if support_kind == "type":
        finding = context.finding(
            supporting_contribution_findings=(object(),),
        )
    elif support_kind == "contribution":
        finding = context.finding(
            supporting_contribution_findings=(replace(context.contribution_finding),),
        )
    else:
        finding = context.finding(
            supporting_scale_findings=(replace(context.scale_finding),),
        )

    evaluator, _ = _evaluator(candidate_reference=(finding,))

    with pytest.raises(NetOverallSystemRiskEvaluationInvariantError):
        _evaluate(context, evaluator)


def test_findings_may_use_different_valid_support_subsets() -> None:
    context = _Context()

    contribution_only = context.finding(
        finding_id="contribution-only",
        supporting_scale_findings=(),
        supporting_system_references=(),
    )
    scale_only = context.finding(
        finding_id="scale-only",
        supporting_contribution_findings=(),
        supporting_system_references=(),
    )

    evaluator, _ = _evaluator(
        candidate_reference=(contribution_only,),
        system_interaction=(scale_only,),
    )

    result = _evaluate(context, evaluator)

    assert result.risk_findings == (contribution_only, scale_only)


def test_adverse_and_unresolved_findings_are_valid_results() -> None:
    context = _Context()
    finding = context.finding(
        risk_states=("increased", "unresolved"),
        unresolved_conditions=("material uncertainty remains",),
    )
    evaluator, _ = _evaluator(charter_unresolved=(finding,))

    result = _evaluate(context, evaluator)

    assert result.risk_findings == (finding,)


def test_risk_evaluation_does_not_mutate_transition_states() -> None:
    context = _Context()
    evaluator, _ = _evaluator()

    result = _evaluate(context, evaluator)

    assert result.risk_findings == ()
    assert context.candidate.authoritative_transition_pathway is context.authoritative
    assert context.candidate.identity_token is context.identity_token
    assert context.authoritative.evaluation_run_id == "older-run"
    assert context.authoritative.authoritative_transition_pathway is None


def test_rule_exception_propagates_unchanged() -> None:
    context = _Context()
    failure = RuntimeError("risk rule failed")

    def fail(*_args: object) -> tuple[SystemRiskFinding, ...]:
        raise failure

    evaluator, _ = _evaluator()
    evaluator = NetOverallSystemRiskEvaluator(
        candidate_reference_risk_function=fail,
        system_interaction_risk_function=evaluator.system_interaction_risk_function,
        transition_delivery_risk_function=evaluator.transition_delivery_risk_function,
        timing_sequencing_risk_function=evaluator.timing_sequencing_risk_function,
        bottleneck_failure_risk_function=evaluator.bottleneck_failure_risk_function,
        fossil_persistence_fallback_risk_function=(
            evaluator.fossil_persistence_fallback_risk_function
        ),
        dependency_propagation_risk_function=(
            evaluator.dependency_propagation_risk_function
        ),
        biosphere_climate_risk_function=evaluator.biosphere_climate_risk_function,
        charter_unresolved_risk_function=evaluator.charter_unresolved_risk_function,
        evaluator_version=evaluator.evaluator_version,
        rule_set_version=evaluator.rule_set_version,
    )

    with pytest.raises(RuntimeError) as caught:
        _evaluate(context, evaluator)

    assert caught.value is failure


def test_evaluator_is_immutable() -> None:
    evaluator, _ = _evaluator()

    with pytest.raises(FrozenInstanceError):
        evaluator.evaluator_version = "changed"  # type: ignore[misc]


def test_evaluator_adds_no_downstream_or_scalar_operations() -> None:
    field_names = {field.name for field in fields(NetOverallSystemRiskEvaluator)}
    forbidden = {
        "final_pathway_assembly",
        "final_charter",
        "promotion",
        "validator",
        "binding",
        "pathway_assessment",
        "score",
        "rank",
        "weight",
        "vote",
        "optimization",
        "scalar_aggregation",
    }

    assert field_names.isdisjoint(forbidden)
