from collections.abc import Callable
from dataclasses import FrozenInstanceError, fields
from typing import TypeVar

import pytest

from climatesos.pathway_evaluation import (
    IdentityToken,
    NetOverallSystemContribution,
    OpaqueReference,
    PathwayEngineResult,
    ProductPathway,
    ScaleDiagnosticResult,
    SourceReference,
    TransitionPathway,
    TransitionPathwayCompilationInvariantError,
    ValidatedTransitionPathwayCompiler,
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
        pathway_engine_result = _record(
            PathwayEngineResult,
            identity_token=self.identity_token,
        )
        self.authoritative = TransitionPathway(
            reference_id="authoritative",
            identity_token=_record(IdentityToken, token_id="older-lineage"),
            evaluation_run_id="older-run",
            user_id="global-user",
            pathway_id="global-pathway",
        )
        self.contribution = _record(
            NetOverallSystemContribution,
            product_pathway=self.product_pathway,
            pathway_engine_result=pathway_engine_result,
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
        self.evidence = _record(SourceReference)
        self.provenance = _record(SourceReference)

    def candidate(self, **overrides: object) -> TransitionPathway:
        values: dict[str, object] = {
            "reference_id": "candidate",
            "provenance": (self.provenance,),
            "identity_token": self.identity_token,
            "evaluation_run_id": "run-1",
            "user_id": "user-1",
            "pathway_id": "pathway-1",
            "authoritative_transition_pathway": self.authoritative,
            "product_pathway": self.product_pathway,
            "net_overall_system_contribution": self.contribution,
            "scale_diagnostic_result": self.scale_result,
            "conditions": ("conditional change",),
            "dependencies": (_record(OpaqueReference),),
            "assumptions": ("assumption",),
            "uncertainties": ("uncertainty",),
            "evidence_references": (self.evidence,),
            "compiler_version": "compiler-v1",
            "model_version": "transition-v1",
            "rule_set_version": "compiler-rules-v1",
        }
        values.update(overrides)
        return TransitionPathway(**values)  # type: ignore[arg-type]


def _compile(
    context: _Context,
    function: Callable[..., object],
    *,
    evaluation_run_id: str = "run-1",
    user_id: str = "user-1",
    pathway_id: str = "pathway-1",
) -> TransitionPathway:
    return ValidatedTransitionPathwayCompiler(function).compile(
        context.product_pathway,
        context.contribution,
        context.scale_result,
        context.authoritative,
        None,
        None,
        ("conditional change",),
        (_record(OpaqueReference),),
        ("assumption",),
        ("uncertainty",),
        (context.evidence,),
        (context.provenance,),
        context.identity_token,
        evaluation_run_id,
        user_id,
        pathway_id,
    )


def test_valid_inputs_invoke_once_and_preserve_exact_candidate_context() -> None:
    context = _Context()
    candidate = context.candidate()
    calls = 0

    def compilation_function(*args: object) -> object:
        nonlocal calls
        calls += 1
        assert args[:4] == (
            context.product_pathway,
            context.contribution,
            context.scale_result,
            context.authoritative,
        )
        return candidate

    result = _compile(context, compilation_function)

    assert calls == 1
    assert result is candidate
    assert result is not context.authoritative
    assert result.authoritative_transition_pathway is context.authoritative
    assert result.product_pathway is context.product_pathway
    assert result.net_overall_system_contribution is context.contribution
    assert result.scale_diagnostic_result is context.scale_result
    assert result.identity_token is context.identity_token
    assert result.evaluation_run_id == "run-1"
    assert result.user_id == "user-1"
    assert result.pathway_id == "pathway-1"


def test_authoritative_pathway_may_have_an_older_lineage_and_run() -> None:
    context = _Context()

    assert context.authoritative.identity_token is not context.identity_token
    assert context.authoritative.evaluation_run_id == "older-run"
    assert _compile(context, lambda *args: context.candidate()).reference_id == (
        "candidate"
    )


def test_returning_authoritative_pathway_itself_rejects() -> None:
    context = _Context()

    with pytest.raises(TransitionPathwayCompilationInvariantError):
        _compile(context, lambda *args: context.authoritative)


@pytest.mark.parametrize(
    ("field", "replacement_factory"),
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
def test_reconstructed_candidate_upstream_references_reject(
    field: str,
    replacement_factory: Callable[[], object],
) -> None:
    context = _Context()
    candidate = context.candidate(**{field: replacement_factory()})

    with pytest.raises(TransitionPathwayCompilationInvariantError):
        _compile(context, lambda *args: candidate)


@pytest.mark.parametrize(
    ("attribute", "value"),
    [
        ("evaluation_run_id", "other-run"),
        ("user_id", "other-user"),
        ("pathway_id", "other-pathway"),
    ],
)
def test_input_attribution_mismatches_reject_before_execution(
    attribute: str,
    value: str,
) -> None:
    context = _Context()
    calls = 0

    def compilation_function(*args: object) -> object:
        nonlocal calls
        calls += 1
        return context.candidate()

    with pytest.raises(TransitionPathwayCompilationInvariantError):
        _compile(context, compilation_function, **{attribute: value})

    assert calls == 0


def test_incorrect_input_lineage_rejects_before_execution() -> None:
    context = _Context()
    context.product_pathway = _record(
        ProductPathway,
        identity_token=_record(IdentityToken, token_id="other-lineage"),
        evaluation_run_id="run-1",
        user_id="user-1",
        pathway_id="pathway-1",
    )
    calls = 0

    def compilation_function(*args: object) -> object:
        nonlocal calls
        calls += 1
        return context.candidate()

    with pytest.raises(TransitionPathwayCompilationInvariantError):
        _compile(context, compilation_function)

    assert calls == 0


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("identity_token", None),
        ("identity_token", _record(IdentityToken, token_id="other-lineage")),
        ("evaluation_run_id", None),
        ("evaluation_run_id", "other-run"),
        ("user_id", None),
        ("user_id", "other-user"),
        ("pathway_id", None),
        ("pathway_id", "other-pathway"),
        ("compiler_version", None),
        ("model_version", None),
        ("rule_set_version", None),
    ],
)
def test_missing_or_incorrect_candidate_lineage_attribution_and_versions_reject(
    field: str,
    value: object,
) -> None:
    context = _Context()
    candidate = context.candidate(**{field: value})

    with pytest.raises(TransitionPathwayCompilationInvariantError):
        _compile(context, lambda *args: candidate)


def test_non_transition_pathway_return_rejects() -> None:
    context = _Context()

    with pytest.raises(TransitionPathwayCompilationInvariantError):
        _compile(context, lambda *args: object())


def test_compiler_exception_propagates_unchanged() -> None:
    context = _Context()
    failure = RuntimeError("compiler failed")

    def compilation_function(*args: object) -> object:
        raise failure

    with pytest.raises(RuntimeError) as caught:
        _compile(context, compilation_function)

    assert caught.value is failure


def test_validated_compiler_is_immutable() -> None:
    context = _Context()
    compiler = ValidatedTransitionPathwayCompiler(
        lambda *args: context.candidate()
    )

    with pytest.raises(FrozenInstanceError):
        compiler.compilation_function = lambda *args: object()  # type: ignore[misc]


def test_validated_boundary_adds_no_downstream_or_scalar_surfaces() -> None:
    field_names = {field.name for field in fields(ValidatedTransitionPathwayCompiler)}

    assert field_names == {"compilation_function"}
    forbidden = (
        "authoritative_promotion",
        "risk_evaluation",
        "final_assembly",
        "validation",
        "binding",
        "score",
        "rank",
        "weight",
        "vote",
        "optimization",
    )
    assert all(
        not hasattr(ValidatedTransitionPathwayCompiler, name) for name in forbidden
    )
