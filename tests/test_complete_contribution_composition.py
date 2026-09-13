"""Focused complete contribution-domain composition tests."""

from dataclasses import dataclass, fields
from inspect import signature
from typing import cast, get_type_hints

import pytest

from climatesos.pathway_evaluation import (
    CompleteNetOverallSystemContributionFunction,
    ContributionFinding,
    EmissionsCdrBiosphereFindingFunction,
    EnablingDemandBurdenFindingFunction,
    EvaluationRun,
    FossilDisplacementContributionFunction,
    IdentityToken,
    InitialCharterResult,
    IntegratedCharterResult,
    NetOverallSystemContribution,
    PathwayEngineResult,
    PathwayObject,
    ProductAdapterResult,
    ProductIntakeBundle,
    ProductPathway,
    ReliabilityDeliveryTimingFindingFunction,
    SourceReference,
    TransitionPathway,
    ValidatedNetOverallSystemContributionEvaluator,
)


@dataclass(frozen=True, slots=True)
class _Artifacts:
    pathway: ProductPathway
    engine: PathwayEngineResult
    integrated: IntegratedCharterResult


class _FossilDomain:
    def __init__(
        self,
        findings: tuple[ContributionFinding, ...],
        calls: list[str],
        failure: str | None = None,
    ) -> None:
        self.findings = findings
        self.calls = calls
        self.failure = failure
        self.result: NetOverallSystemContribution | None = None
        self.received: list[
            tuple[PathwayEngineResult, IntegratedCharterResult]
        ] = []

    def __call__(
        self,
        engine: PathwayEngineResult,
        integrated: IntegratedCharterResult,
    ) -> NetOverallSystemContribution:
        self.calls.append("fossil")
        self.received.append((engine, integrated))
        if self.failure is not None:
            raise RuntimeError(self.failure)
        self.result = NetOverallSystemContribution(
            product_pathway=engine.product_pathway,
            pathway_engine_result=engine,
            integrated_charter_result=integrated,
            transition_pathway=engine.transition_pathway,
            contribution_findings=self.findings,
            evaluation_run_id=engine.evaluation_run_id,
            user_id=engine.user_id,
            pathway_id=engine.pathway_id,
            evaluator_version="ignored-fossil-version",
            rule_set_version="ignored-fossil-rules",
            assumptions=("ignored fossil assumption",),
        )
        return self.result


class _FindingDomain:
    def __init__(
        self,
        name: str,
        findings: tuple[ContributionFinding, ...],
        calls: list[str],
        failure: str | None = None,
    ) -> None:
        self.name = name
        self.findings = findings
        self.calls = calls
        self.failure = failure
        self.received: list[
            tuple[PathwayEngineResult, IntegratedCharterResult]
        ] = []

    def __call__(
        self,
        engine: PathwayEngineResult,
        integrated: IntegratedCharterResult,
    ) -> tuple[ContributionFinding, ...]:
        self.calls.append(self.name)
        self.received.append((engine, integrated))
        if self.failure is not None:
            raise RuntimeError(self.failure)
        return self.findings


def _artifacts() -> _Artifacts:
    token = IdentityToken("token-1")
    run = EvaluationRun("run-1", token.token_id)
    intake = ProductIntakeBundle(token, run, ())
    output = PathwayObject(
        object_id="output-1",
        object_type="caller-defined",
        user_id="user-1",
        pathway_id="pathway-1",
    )
    pathway = ProductPathway(
        identity_token=token,
        evaluation_run_id=run.evaluation_run_id,
        user_id="user-1",
        pathway_id="pathway-1",
        pathway_type="caller-defined",
        time_window="2030",
        geographic_scope="local",
        system_scope="power",
        objects=(output,),
        relationships=(),
    )
    adapter = ProductAdapterResult(pathway, intake, run)
    initial = InitialCharterResult(
        identity_token=token,
        evaluation_run_id=run.evaluation_run_id,
        adapter_result=adapter,
        check_results=(),
        evaluator_version="initial-1",
        rule_set_version="charter-1",
        status="PASS",
    )
    transition = TransitionPathway("transition-1")
    engine = PathwayEngineResult(
        identity_token=token,
        product_pathway=pathway,
        transition_pathway=transition,
        initial_charter_result=initial,
        direct_comparison_findings=(),
        substitution_combination_findings=(),
        downstream_propagation_findings=(),
        queue_results=(),
        fabric_results=(),
        documentation_findings=(),
        evaluation_run_id=run.evaluation_run_id,
        system_context=None,
        evaluator_versions=(),
        rule_set_versions=(),
        user_id=pathway.user_id,
        pathway_id=pathway.pathway_id,
    )
    integrated = IntegratedCharterResult(
        identity_token=token,
        evaluation_run_id=run.evaluation_run_id,
        pathway_engine_result=engine,
        initial_charter_result=initial,
        check_results=(),
        evaluator_version="integrated-1",
        rule_set_version="charter-1",
        status="PASS",
    )
    return _Artifacts(pathway, engine, integrated)


def _finding(finding_id: str) -> ContributionFinding:
    return ContributionFinding(finding_id, f"effect-{finding_id}")


def _composer(
    fossil: _FossilDomain,
    reliability: _FindingDomain,
    enabling: _FindingDomain,
    emissions: _FindingDomain,
) -> CompleteNetOverallSystemContributionFunction:
    return CompleteNetOverallSystemContributionFunction(
        fossil_contribution_function=cast(
            FossilDisplacementContributionFunction,
            fossil,
        ),
        reliability_delivery_timing_function=cast(
            ReliabilityDeliveryTimingFindingFunction,
            reliability,
        ),
        enabling_demand_burden_function=cast(
            EnablingDemandBurdenFindingFunction,
            enabling,
        ),
        emissions_cdr_biosphere_function=cast(
            EmissionsCdrBiosphereFindingFunction,
            emissions,
        ),
        evaluator_version="complete-1",
        rule_set_version="complete-rules-1",
        assumptions=("complete assumption",),
        uncertainties=("complete uncertainty",),
        evidence_references=(SourceReference("complete-evidence-1"),),
        provenance=(SourceReference("complete-provenance-1"),),
    )


def test_complete_composer_has_required_fields_and_signature() -> None:
    composer_fields = {
        field.name for field in fields(CompleteNetOverallSystemContributionFunction)
    }
    assert composer_fields == {
        "fossil_contribution_function",
        "reliability_delivery_timing_function",
        "enabling_demand_burden_function",
        "emissions_cdr_biosphere_function",
        "evaluator_version",
        "rule_set_version",
        "assumptions",
        "uncertainties",
        "evidence_references",
        "provenance",
    }
    assert tuple(
        signature(CompleteNetOverallSystemContributionFunction.__call__).parameters
    ) == ("self", "pathway_engine_result", "integrated_charter_result")
    hints = get_type_hints(CompleteNetOverallSystemContributionFunction.__call__)
    assert hints["return"] is NetOverallSystemContribution


def test_domains_execute_once_in_order_and_preserve_exact_findings() -> None:
    artifacts = _artifacts()
    calls: list[str] = []
    duplicate = _finding("duplicate")
    fossil_first = _finding("z-fossil")
    fossil_second = _finding("a-fossil")
    reliability = _finding("reliability")
    enabling = _finding("enabling")
    emissions = _finding("emissions")
    fossil_domain = _FossilDomain((fossil_first, fossil_second, duplicate), calls)
    reliability_domain = _FindingDomain(
        "reliability",
        (reliability, duplicate),
        calls,
    )
    enabling_domain = _FindingDomain("enabling", (enabling,), calls)
    emissions_domain = _FindingDomain("emissions", (emissions,), calls)
    composer = _composer(
        fossil_domain,
        reliability_domain,
        enabling_domain,
        emissions_domain,
    )

    result = composer(artifacts.engine, artifacts.integrated)

    assert calls == ["fossil", "reliability", "enabling", "emissions"]
    for domain in (
        fossil_domain,
        reliability_domain,
        enabling_domain,
        emissions_domain,
    ):
        assert domain.received == [(artifacts.engine, artifacts.integrated)]
    assert result.contribution_findings == (
        fossil_first,
        fossil_second,
        duplicate,
        reliability,
        duplicate,
        enabling,
        emissions,
    )
    assert result.contribution_findings[2] is result.contribution_findings[4]


def test_final_result_preserves_upstream_references_attribution_and_metadata() -> None:
    artifacts = _artifacts()
    calls: list[str] = []
    fossil = _FossilDomain((), calls)
    composer = _composer(
        fossil,
        _FindingDomain("reliability", (), calls),
        _FindingDomain("enabling", (), calls),
        _FindingDomain("emissions", (), calls),
    )

    result = composer(artifacts.engine, artifacts.integrated)

    assert result.product_pathway is artifacts.pathway
    assert result.pathway_engine_result is artifacts.engine
    assert result.integrated_charter_result is artifacts.integrated
    assert result.transition_pathway is artifacts.engine.transition_pathway
    assert result.evaluation_run_id == artifacts.engine.evaluation_run_id
    assert result.user_id == artifacts.engine.user_id
    assert result.pathway_id == artifacts.engine.pathway_id
    assert result.evaluator_version == "complete-1"
    assert result.rule_set_version == "complete-rules-1"
    assert result.assumptions == ("complete assumption",)
    assert result.uncertainties == ("complete uncertainty",)
    assert result.evidence_references == (SourceReference("complete-evidence-1"),)
    assert result.provenance == (SourceReference("complete-provenance-1"),)
    assert fossil.result is not None
    assert result is not fossil.result
    assert result.assumptions != fossil.result.assumptions


@pytest.mark.parametrize(
    "failed_domain",
    ("fossil", "reliability", "enabling", "emissions"),
)
def test_domain_exception_propagates_and_stops_later_domains(
    failed_domain: str,
) -> None:
    artifacts = _artifacts()
    calls: list[str] = []
    error = "domain failed" if failed_domain == "fossil" else None
    fossil = _FossilDomain((), calls, error)
    reliability = _FindingDomain(
        "reliability",
        (),
        calls,
        "domain failed" if failed_domain == "reliability" else None,
    )
    enabling = _FindingDomain(
        "enabling",
        (),
        calls,
        "domain failed" if failed_domain == "enabling" else None,
    )
    emissions = _FindingDomain(
        "emissions",
        (),
        calls,
        "domain failed" if failed_domain == "emissions" else None,
    )
    composer = _composer(fossil, reliability, enabling, emissions)

    with pytest.raises(RuntimeError, match="domain failed"):
        composer(artifacts.engine, artifacts.integrated)

    expected_calls = {
        "fossil": ["fossil"],
        "reliability": ["fossil", "reliability"],
        "enabling": ["fossil", "reliability", "enabling"],
        "emissions": ["fossil", "reliability", "enabling", "emissions"],
    }
    assert calls == expected_calls[failed_domain]


def test_complete_composer_integrates_through_packet_7b_validator() -> None:
    artifacts = _artifacts()
    calls: list[str] = []
    finding = _finding("validated")
    composer = _composer(
        _FossilDomain((finding,), calls),
        _FindingDomain("reliability", (), calls),
        _FindingDomain("enabling", (), calls),
        _FindingDomain("emissions", (), calls),
    )
    evaluator = ValidatedNetOverallSystemContributionEvaluator(composer)

    result = evaluator.evaluate(artifacts.engine, artifacts.integrated)

    assert result.contribution_findings == (finding,)
    assert result.pathway_engine_result is artifacts.engine


def test_no_scalar_score_rank_weight_or_voting_fields_are_introduced() -> None:
    composer_fields = {
        field.name for field in fields(CompleteNetOverallSystemContributionFunction)
    }
    result_fields = {field.name for field in fields(NetOverallSystemContribution)}

    assert {"score", "rank", "ranking", "weight", "vote", "voting"}.isdisjoint(
        composer_fields | result_fields
    )
