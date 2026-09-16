import inspect
from dataclasses import FrozenInstanceError, fields
from typing import TypeVar, cast, get_type_hints

import pytest

import climatesos.pathway_evaluation as pathway_evaluation
from climatesos.pathway_evaluation import (
    BoundPathway,
    BoundState,
    ComparisonFinding,
    EvaluationTrace,
    FinalCharterResult,
    FinalPathwayResult,
    IdentityToken,
    InitialCharterResult,
    IntegratedCharterResult,
    OpaqueReference,
    PathwayAssessment,
    PathwayAssessmentEvaluator,
    ProductEvaluationContext,
    ProductEvaluationContextMode,
    ProductPathway,
    TransitionPathway,
)
from climatesos.pathway_evaluation.pathway_assessment import (
    PathwayAssessmentInvariantError,
    _PathwayAssessmentDetermination,
)

T = TypeVar("T")


def _record(record_type: type[T], **values: object) -> T:
    record = object.__new__(record_type)
    for name, value in values.items():
        object.__setattr__(record, name, value)
    return record


def _inputs(
    state: BoundState = BoundState.CLEAN_BOUND,
) -> tuple[BoundPathway, FinalCharterResult, IdentityToken]:
    token = IdentityToken("lineage-1")

    product = _record(
        ProductPathway,
        identity_token=token,
        evaluation_run_id="run-1",
        user_id="user-1",
        pathway_id="pathway-1",
    )

    initial = _record(InitialCharterResult)
    integrated = _record(IntegratedCharterResult)

    trace = _record(
        EvaluationTrace,
        initial_charter_result=initial,
        integrated_charter_result=integrated,
    )

    authoritative = TransitionPathway(
        reference_id="authoritative-transition",
        model_version="transition-model-v1",
    )

    final_pathway = _record(
        FinalPathwayResult,
        product_pathway=product,
        authoritative_transition_pathway=authoritative,
        evaluation_trace=trace,
        identity_token=token,
        evaluation_run_id="run-1",
        user_id="user-1",
        pathway_id="pathway-1",
    )

    final_charter = _record(
        FinalCharterResult,
        identity_token=token,
        evaluation_run_id="run-1",
        final_pathway_result=final_pathway,
        initial_charter_result=initial,
        integrated_charter_result=integrated,
    )

    bound = BoundPathway(
        final_pathway_result=final_pathway,
        bound_state=state,
        identity_token=token,
        evaluation_run_id="run-1",
        user_id="user-1",
        pathway_id="pathway-1",
        binding_mechanism_id="system-binding",
        binding_mechanism_version="system-binding-v1",
    )

    return bound, final_charter, token


def _determination(
    bound: BoundPathway,
    final_charter: FinalCharterResult,
) -> _PathwayAssessmentDetermination:
    del bound, final_charter

    return _PathwayAssessmentDetermination(
        assessment_outcome="successful",
        replacement_fitness=None,
        material_comparative_findings=(),
        material_improvements=(),
        material_regressions=(),
        progression_preventing_findings=(),
        upstream_result_references=(OpaqueReference("final-pathway"),),
        correctable=None,
        corrective_requirement=None,
        corrective_justification=None,
        successor_evaluation_conditions=(),
    )


def _evaluate(
    bound: BoundPathway,
    final_charter: FinalCharterResult,
    token: IdentityToken,
) -> PathwayAssessment:
    return PathwayAssessmentEvaluator(_determination).evaluate(
        bound,
        final_charter,
        ProductEvaluationContext(ProductEvaluationContextMode.USER_SUBMITTED),
        token,
        "run-1",
        "user-1",
        "pathway-1",
        "assessment-1",
    )


def test_pathway_assessment_has_exact_spec_derived_field_shape() -> None:
    assert {field.name for field in fields(PathwayAssessment)} == {
        "identity_token",
        "evaluation_run_id",
        "pathway_assessment_id",
        "user_id",
        "product_pathway",
        "initial_charter_result",
        "integrated_charter_result",
        "final_charter_result",
        "bound_pathway",
        "product_evaluation_context",
        "assessment_outcome",
        "replacement_fitness",
        "material_comparative_findings",
        "material_improvements",
        "material_regressions",
        "progression_preventing_findings",
        "upstream_result_references",
        "correctable",
        "corrective_requirement",
        "corrective_justification",
        "successor_evaluation_conditions",
        "reference_transition_pathway",
    }


def test_product_evaluation_context_is_exact_minimal_immutable_model() -> None:
    context = ProductEvaluationContext(
        ProductEvaluationContextMode.USER_SUBMITTED
    )
    hints = get_type_hints(ProductEvaluationContext)

    assert {mode.value for mode in ProductEvaluationContextMode} == {
        "global",
        "user_submitted",
    }
    assert {field.name for field in fields(ProductEvaluationContext)} == {
        "context_mode"
    }
    assert hints == {"context_mode": ProductEvaluationContextMode}

    with pytest.raises(FrozenInstanceError):
        context.context_mode = ProductEvaluationContextMode.GLOBAL  # type: ignore[misc]


def test_comparative_assessment_fields_use_concrete_comparison_findings() -> None:
    hints = get_type_hints(PathwayAssessment)

    assert hints["product_evaluation_context"] is ProductEvaluationContext
    assert hints["material_comparative_findings"] == tuple[ComparisonFinding, ...]
    assert hints["material_improvements"] == tuple[ComparisonFinding, ...]
    assert hints["material_regressions"] == tuple[ComparisonFinding, ...]

    # Potential typing questions intentionally remain open until Section 18
    # closes their concrete ownership/reference surface.
    assert hints["progression_preventing_findings"] == tuple[OpaqueReference, ...]
    assert hints["upstream_result_references"] == tuple[OpaqueReference, ...]


def test_evaluator_preserves_exact_required_references_and_immutability() -> None:
    bound, final_charter, token = _inputs()
    context = ProductEvaluationContext(
        ProductEvaluationContextMode.USER_SUBMITTED
    )

    result = PathwayAssessmentEvaluator(_determination).evaluate(
        bound,
        final_charter,
        context,
        token,
        "run-1",
        "user-1",
        "pathway-1",
        "assessment-1",
    )

    assert result.bound_pathway is bound
    assert result.final_charter_result is final_charter
    assert result.product_evaluation_context is context
    assert result.identity_token is token
    assert result.product_pathway is bound.final_pathway_result.product_pathway

    assert result.initial_charter_result is (
        bound.final_pathway_result.evaluation_trace.initial_charter_result
    )
    assert result.integrated_charter_result is (
        bound.final_pathway_result.evaluation_trace.integrated_charter_result
    )
    assert result.reference_transition_pathway is (
        bound.final_pathway_result.authoritative_transition_pathway
    )

    with pytest.raises(FrozenInstanceError):
        result.assessment_outcome = "changed"  # type: ignore[misc]


def test_evaluator_owns_pathway_assessment_construction() -> None:
    source = inspect.getsource(PathwayAssessmentEvaluator)

    assert "PathwayAssessment(" in source
    assert "assessment_function" not in source
    assert "determination_function" in source


def test_no_ack_cannot_enter_pathway_assessment() -> None:
    bound, final_charter, token = _inputs(BoundState.NO_ACK)

    with pytest.raises(PathwayAssessmentInvariantError, match="NoAck"):
        _evaluate(bound, final_charter, token)


@pytest.mark.parametrize(
    "malformed",
    [object(), object.__new__(BoundPathway)],
)
def test_wrong_type_or_malformed_bound_pathway_is_rejected(
    malformed: object,
) -> None:
    _, final_charter, token = _inputs()

    with pytest.raises(PathwayAssessmentInvariantError):
        _evaluate(
            cast(BoundPathway, malformed),
            final_charter,
            token,
        )


@pytest.mark.parametrize(
    "mismatch",
    ["lineage", "run", "user", "pathway"],
)
def test_input_identity_and_attribution_mismatch_is_rejected(
    mismatch: str,
) -> None:
    bound, final_charter, token = _inputs()

    run_id = "run-1"
    user_id = "user-1"
    pathway_id = "pathway-1"

    if mismatch == "lineage":
        token = IdentityToken("other-lineage")
    elif mismatch == "run":
        run_id = "other-run"
    elif mismatch == "user":
        user_id = "other-user"
    else:
        pathway_id = "other-pathway"

    with pytest.raises(PathwayAssessmentInvariantError):
        PathwayAssessmentEvaluator(_determination).evaluate(
            bound,
            final_charter,
            ProductEvaluationContext(
                ProductEvaluationContextMode.USER_SUBMITTED
            ),
            token,
            run_id,
            user_id,
            pathway_id,
            "assessment-1",
        )


def test_equivalent_identity_token_instance_preserves_canonical_lineage() -> None:
    bound, final_charter, token = _inputs()
    equivalent = IdentityToken(token.token_id)

    result = PathwayAssessmentEvaluator(_determination).evaluate(
        bound,
        final_charter,
        ProductEvaluationContext(ProductEvaluationContextMode.USER_SUBMITTED),
        equivalent,
        "run-1",
        "user-1",
        "pathway-1",
        "assessment-1",
    )

    assert result.identity_token is equivalent
    assert result.identity_token.token_id == token.token_id


def test_determination_function_cannot_own_pathway_assessment_result() -> None:
    bound, final_charter, token = _inputs()

    def whole_result(
        supplied_bound: BoundPathway,
        supplied_charter: FinalCharterResult,
    ) -> object:
        del supplied_bound, supplied_charter
        return object()

    with pytest.raises(
        PathwayAssessmentInvariantError,
        match="determination",
    ):
        PathwayAssessmentEvaluator(whole_result).evaluate(
            bound,
            final_charter,
            ProductEvaluationContext(
                ProductEvaluationContextMode.USER_SUBMITTED
            ),
            token,
            "run-1",
            "user-1",
            "pathway-1",
            "assessment-1",
        )


def test_comparative_determinations_reject_opaque_references() -> None:
    bound, final_charter, token = _inputs()

    def invalid_determination(
        supplied_bound: BoundPathway,
        supplied_charter: FinalCharterResult,
    ) -> _PathwayAssessmentDetermination:
        del supplied_bound, supplied_charter

        return _PathwayAssessmentDetermination(
            assessment_outcome="successful",
            replacement_fitness=None,
            material_comparative_findings=(
                cast(
                    ComparisonFinding,
                    OpaqueReference("comparison"),
                ),
            ),
            material_improvements=(),
            material_regressions=(),
            progression_preventing_findings=(),
            upstream_result_references=(),
            correctable=None,
            corrective_requirement=None,
            corrective_justification=None,
            successor_evaluation_conditions=(),
        )

    with pytest.raises(
        PathwayAssessmentInvariantError,
        match="ComparisonFinding",
    ):
        PathwayAssessmentEvaluator(invalid_determination).evaluate(
            bound,
            final_charter,
            ProductEvaluationContext(
                ProductEvaluationContextMode.USER_SUBMITTED
            ),
            token,
            "run-1",
            "user-1",
            "pathway-1",
            "assessment-1",
        )


def test_public_surface_contains_only_required_section_18_components() -> None:
    forbidden = {
        "ValidatedPathwayAssessmentEvaluator",
        "PathwayAssessmentPrecondition",
        "PathwayAssessmentValidator",
        "PathwayAssessmentResult",
        "PathwayAssessmentContext",
    }

    assert "PathwayAssessment" in pathway_evaluation.__all__
    assert "PathwayAssessmentEvaluator" in pathway_evaluation.__all__
    assert "ProductEvaluationContext" in pathway_evaluation.__all__
    assert "ProductEvaluationContextMode" in pathway_evaluation.__all__
    assert forbidden.isdisjoint(pathway_evaluation.__all__)
    assert all(
        not hasattr(pathway_evaluation, name)
        for name in forbidden
    )


def test_evaluator_is_concrete_and_contains_no_other_stage_logic() -> None:
    source = inspect.getsource(PathwayAssessmentEvaluator).lower()

    assert inspect.isclass(PathwayAssessmentEvaluator)
    assert "validatedpathwayassessmentevaluator" not in source
    assert all(
        name not in source
        for name in (
            "bindinghandler",
            "charterevaluator",
            "finalpathwayassembly",
            "boundstatedeterminer",
            "resolutionhandler",
            "transitionpathwayvalidator",
        )
    )
