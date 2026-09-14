"""Structural execution boundary for all three Charter evaluation passes."""

from collections.abc import Callable
from dataclasses import dataclass
from typing import cast

from .enums import CharterCheckStatus
from .models import (
    Attribute,
    CharterCheckResult,
    CharterEvaluationContext,
    CharterStatus,
    EvaluationTrace,
    FinalCharterResult,
    FinalPathwayResult,
    IdentityToken,
    InitialCharterResult,
    IntegratedCharterResult,
    NetOverallSystemContribution,
    NetOverallSystemRiskResult,
    OpaqueReference,
    PathwayEngineResult,
    ProductAdapterResult,
    ProductPathway,
    ScaleDiagnosticResult,
    SourceReference,
    TransitionPathway,
)

InitialCharterCheckFunction = Callable[
    [ProductAdapterResult, OpaqueReference, CharterEvaluationContext],
    CharterCheckResult,
]
IntegratedCharterCheckFunction = Callable[
    [PathwayEngineResult, OpaqueReference, CharterEvaluationContext],
    CharterCheckResult,
]
InitialCharterStatusFunction = Callable[
    [
        ProductAdapterResult,
        tuple[CharterCheckResult, ...],
        CharterEvaluationContext,
    ],
    str,
]
IntegratedCharterStatusFunction = Callable[
    [
        PathwayEngineResult,
        tuple[CharterCheckResult, ...],
        CharterEvaluationContext,
    ],
    str,
]
FinalCharterCheckFunction = Callable[
    [FinalPathwayResult, OpaqueReference, CharterEvaluationContext],
    CharterCheckResult,
]
FinalCharterStatusFunction = Callable[
    [
        FinalPathwayResult,
        tuple[CharterCheckResult, ...],
        CharterEvaluationContext,
    ],
    str,
]

_SUBSTANTIVE_CHECK_STATUSES = frozenset(
    {
        CharterCheckStatus.PASS,
        CharterCheckStatus.FAIL,
        CharterCheckStatus.UNRESOLVED,
        CharterCheckStatus.NOT_APPLICABLE,
    }
)
_INTEGRITY_FAILURE_STATUSES = frozenset(
    {
        CharterCheckStatus.ERROR,
        CharterCheckStatus.MISSING,
        CharterCheckStatus.NULL,
        CharterCheckStatus.NOACK,
    }
)


class CharterEvaluationInvariantError(ValueError):
    """Raised when a Charter pass is structurally incomplete or incoherent."""


def _is_string(value: object) -> bool:
    return isinstance(value, str)


def _is_charter_check_status(value: object) -> bool:
    return isinstance(value, CharterCheckStatus)


def _is_optional_string(value: object) -> bool:
    return value is None or isinstance(value, str)


def _string_tuple_or_empty(value: object) -> tuple[str, ...]:
    if isinstance(value, tuple) and all(isinstance(item, str) for item in value):
        return cast(tuple[str, ...], value)
    return ()


def _opaque_reference_tuple_or_empty(value: object) -> tuple[OpaqueReference, ...]:
    if isinstance(value, tuple) and all(
        isinstance(item, OpaqueReference) for item in value
    ):
        return cast(tuple[OpaqueReference, ...], value)
    return ()


def _source_reference_tuple_or_empty(value: object) -> tuple[SourceReference, ...]:
    if isinstance(value, tuple) and all(
        isinstance(item, SourceReference) for item in value
    ):
        return cast(tuple[SourceReference, ...], value)
    return ()


def _is_valid_charter_status(value: object) -> bool:
    return (
        isinstance(value, CharterStatus)
        and isinstance(value.status, str)
        and isinstance(value.findings, tuple)
        and all(isinstance(finding, str) for finding in value.findings)
        and isinstance(value.evidence_references, tuple)
        and all(
            isinstance(reference, SourceReference)
            for reference in value.evidence_references
        )
        and isinstance(value.documentation_references, tuple)
        and all(
            isinstance(reference, SourceReference)
            for reference in value.documentation_references
        )
        and isinstance(value.pathway_references, tuple)
        and all(
            isinstance(reference, OpaqueReference)
            for reference in value.pathway_references
        )
    )


def _charter_status_tuple_or_empty(value: object) -> tuple[CharterStatus, ...]:
    if isinstance(value, tuple) and all(
        _is_valid_charter_status(item) for item in value
    ):
        return cast(tuple[CharterStatus, ...], value)
    return ()


def _validate_context(
    context: CharterEvaluationContext,
) -> dict[str, OpaqueReference]:
    if not isinstance(context, CharterEvaluationContext):
        raise CharterEvaluationInvariantError(
            "Charter evaluation requires CharterEvaluationContext"
        )
    if not isinstance(context.foundational_charter, OpaqueReference):
        raise CharterEvaluationInvariantError(
            "Foundational Charter must be an OpaqueReference"
        )
    if not isinstance(context.applicable_check_definitions, tuple) or not all(
        isinstance(definition, OpaqueReference)
        for definition in context.applicable_check_definitions
    ):
        raise CharterEvaluationInvariantError(
            "Applicable check definitions must be OpaqueReference objects"
        )
    if not isinstance(context.required_check_ids, tuple) or not all(
        isinstance(check_id, str) for check_id in context.required_check_ids
    ):
        raise CharterEvaluationInvariantError(
            "Required check identities must be an immutable tuple of strings"
        )
    if not isinstance(context.runtime_configuration, tuple) or not all(
        isinstance(item, Attribute) for item in context.runtime_configuration
    ):
        raise CharterEvaluationInvariantError(
            "Runtime configuration must be an immutable tuple of Attribute objects"
        )
    if not isinstance(context.evaluator_version, str) or not isinstance(
        context.rule_set_version,
        str,
    ):
        raise CharterEvaluationInvariantError(
            "Evaluator and rule-set versions must be strings"
        )

    required_ids = context.required_check_ids
    if not required_ids:
        raise CharterEvaluationInvariantError(
            "Charter evaluation requires at least one required check"
        )
    if len(set(required_ids)) != len(required_ids):
        raise CharterEvaluationInvariantError(
            "Required Charter check identities must be unique"
        )
    definitions: dict[str, OpaqueReference] = {}
    for definition in context.applicable_check_definitions:
        if definition.reference_id in definitions:
            raise CharterEvaluationInvariantError(
                "Applicable Charter check definition identities must be unique"
            )
        definitions[definition.reference_id] = definition

    required_set = set(required_ids)
    definition_set = set(definitions)
    if required_set != definition_set:
        missing = required_set - definition_set
        unexpected = definition_set - required_set
        if missing:
            raise CharterEvaluationInvariantError(
                "Evaluation context is missing required Charter check definitions: "
                + ", ".join(sorted(missing))
            )
        raise CharterEvaluationInvariantError(
            "Evaluation context contains unexpected Charter check definitions: "
            + ", ".join(sorted(unexpected))
        )
    return definitions


def _malformed_result_error(result: object, expected_check_id: str) -> str | None:
    if not isinstance(result, CharterCheckResult):
        return f"Required Charter check {expected_check_id} returned no valid result"
    if result.check_id != expected_check_id:
        return (
            f"Required Charter check {expected_check_id} returned result identity "
            f"{result.check_id}"
        )
    if not _is_charter_check_status(result.status):
        return f"Required Charter check {expected_check_id} returned malformed status"
    if not isinstance(result.charter_statuses, tuple) or not all(
        _is_valid_charter_status(charter_status)
        for charter_status in result.charter_statuses
    ):
        return (
            f"Required Charter check {expected_check_id} returned malformed "
            "Charter statuses"
        )
    if not isinstance(result.findings, tuple) or not all(
        isinstance(finding, str) for finding in result.findings
    ):
        return f"Required Charter check {expected_check_id} returned malformed findings"
    reference_fields = (
        result.supporting_evaluation_findings,
        result.supporting_system_findings,
    )
    if any(
        not isinstance(references, tuple)
        or not all(isinstance(reference, OpaqueReference) for reference in references)
        for references in reference_fields
    ):
        return (
            f"Required Charter check {expected_check_id} returned malformed "
            "supporting references"
        )
    source_fields = (result.evidence_references, result.provenance)
    if any(
        not isinstance(references, tuple)
        or not all(isinstance(reference, SourceReference) for reference in references)
        for references in source_fields
    ):
        return (
            f"Required Charter check {expected_check_id} returned malformed "
            "source references"
        )
    if not _is_optional_string(result.execution_error):
        return (
            f"Required Charter check {expected_check_id} returned malformed "
            "execution error"
        )
    if (
        result.status in _SUBSTANTIVE_CHECK_STATUSES
        and result.execution_error is not None
    ):
        return (
            f"Required Charter check {expected_check_id} returned execution error "
            f"with substantive status {result.status.value}: {result.execution_error}"
        )
    return None


def _integrity_failure_result(
    check_id: str,
    status: CharterCheckStatus,
    execution_error: str,
    malformed_result: object = None,
) -> CharterCheckResult:
    if (
        not isinstance(malformed_result, CharterCheckResult)
        or malformed_result.check_id != check_id
    ):
        return CharterCheckResult(
            check_id=check_id,
            status=status,
            execution_error=execution_error,
        )

    reported_error = malformed_result.execution_error
    if _is_string(reported_error):
        reported_error = cast(str, reported_error)
    if isinstance(reported_error, str) and reported_error not in execution_error:
        execution_error = (
            f"{execution_error}; reported execution error: {reported_error}"
        )
    return CharterCheckResult(
        check_id=check_id,
        status=status,
        charter_statuses=_charter_status_tuple_or_empty(
            malformed_result.charter_statuses
        ),
        findings=_string_tuple_or_empty(malformed_result.findings),
        supporting_evaluation_findings=_opaque_reference_tuple_or_empty(
            malformed_result.supporting_evaluation_findings
        ),
        supporting_system_findings=_opaque_reference_tuple_or_empty(
            malformed_result.supporting_system_findings
        ),
        evidence_references=_source_reference_tuple_or_empty(
            malformed_result.evidence_references
        ),
        provenance=_source_reference_tuple_or_empty(malformed_result.provenance),
        execution_error=execution_error,
    )


def _execute_required_checks(
    required_ids: tuple[str, ...],
    definitions: dict[str, OpaqueReference],
    execute: Callable[[OpaqueReference], object],
) -> tuple[CharterCheckResult, ...]:
    results: list[CharterCheckResult] = []
    for check_id in required_ids:
        try:
            raw_result = execute(definitions[check_id])
        except Exception as error:
            execution_error = (
                f"Required Charter check {check_id} raised "
                f"{type(error).__name__}: {error}"
            )
            results.append(
                _integrity_failure_result(
                    check_id,
                    CharterCheckStatus.ERROR,
                    execution_error,
                )
            )
            continue
        if raw_result is None:
            results.append(
                _integrity_failure_result(
                    check_id,
                    CharterCheckStatus.NULL,
                    f"Required Charter check {check_id} returned null",
                )
            )
            continue
        malformed_error = _malformed_result_error(raw_result, check_id)
        if malformed_error is not None:
            results.append(
                _integrity_failure_result(
                    check_id,
                    CharterCheckStatus.ERROR,
                    malformed_error,
                    raw_result,
                )
            )
            continue
        results.append(cast(CharterCheckResult, raw_result))
    return tuple(results)


def _integrity_error(check_results: tuple[CharterCheckResult, ...]) -> str | None:
    errors = tuple(
        result.execution_error
        or f"Required Charter check {result.check_id} is {result.status.value}"
        for result in check_results
        if result.status in _INTEGRITY_FAILURE_STATUSES
    )
    return "; ".join(errors) if errors else None


def _stage_status(
    stage_name: str,
    status_function: Callable[[], object],
) -> tuple[str, str | None]:
    try:
        status = status_function()
    except Exception as error:
        return (
            "ERROR",
            f"{stage_name} Charter status calculation raised "
            f"{type(error).__name__}: {error}",
        )
    if not isinstance(status, str):
        return (
            "ERROR",
            f"{stage_name} Charter status calculation returned malformed status",
        )
    return status, None


def _validate_initial_artifact(adapter_result: ProductAdapterResult) -> None:
    if not isinstance(adapter_result, ProductAdapterResult):
        raise CharterEvaluationInvariantError(
            "Initial Charter evaluation requires ProductAdapterResult"
        )
    pathway = adapter_result.product_pathway
    intake_bundle = adapter_result.intake_bundle
    evaluation_run = adapter_result.evaluation_run
    token_id = pathway.identity_token.token_id
    if (
        intake_bundle.identity_token.token_id != token_id
        or evaluation_run.identity_token_id != token_id
    ):
        raise CharterEvaluationInvariantError(
            "Initial Charter artifacts must share the canonical IdentityToken"
        )
    if pathway.evaluation_run_id != evaluation_run.evaluation_run_id:
        raise CharterEvaluationInvariantError(
            "Initial Charter artifacts must share the EvaluationRun"
        )


def _validate_integrated_artifact(engine_result: PathwayEngineResult) -> None:
    if not isinstance(engine_result, PathwayEngineResult):
        raise CharterEvaluationInvariantError(
            "Integrated Charter evaluation requires PathwayEngineResult"
        )
    pathway = engine_result.product_pathway
    token = pathway.identity_token
    initial_result = engine_result.initial_charter_result
    if (
        initial_result.status == "ERROR"
        or initial_result.execution_error is not None
        or any(
            result.status in _INTEGRITY_FAILURE_STATUSES
            for result in initial_result.check_results
        )
    ):
        raise CharterEvaluationInvariantError(
            "Integrated Charter evaluation cannot consume an Initial Charter "
            "evaluator-integrity failure"
        )
    if initial_result.adapter_result.product_pathway is not pathway:
        raise CharterEvaluationInvariantError(
            "PathwayEngineResult must preserve the Initial Charter pathway reference"
        )
    if (
        initial_result.adapter_result.evaluation_run
        is not initial_result.adapter_result.intake_bundle.evaluation_run
    ):
        raise CharterEvaluationInvariantError(
            "ProductAdapterResult must preserve the ProductIntakeBundle "
            "EvaluationRun reference"
        )
    if (
        engine_result.identity_token.token_id != token.token_id
        or initial_result.identity_token.token_id != token.token_id
        or initial_result.adapter_result.intake_bundle.identity_token.token_id
        != token.token_id
        or initial_result.adapter_result.evaluation_run.identity_token_id
        != token.token_id
        or engine_result.user_id != pathway.user_id
        or engine_result.pathway_id != pathway.pathway_id
    ):
        raise CharterEvaluationInvariantError(
            "Integrated Charter artifact attribution must match the ProductPathway"
        )
    if (
        engine_result.evaluation_run_id != pathway.evaluation_run_id
        or initial_result.evaluation_run_id != pathway.evaluation_run_id
        or initial_result.adapter_result.evaluation_run.evaluation_run_id
        != pathway.evaluation_run_id
        or initial_result.adapter_result.intake_bundle.evaluation_run.evaluation_run_id
        != pathway.evaluation_run_id
    ):
        raise CharterEvaluationInvariantError(
            "Integrated Charter artifact EvaluationRun must match the ProductPathway"
        )


def _validate_provenance(value: object, artifact_name: str) -> None:
    if not isinstance(value, tuple) or not all(
        isinstance(reference, SourceReference) for reference in value
    ):
        raise CharterEvaluationInvariantError(
            f"{artifact_name} provenance must contain SourceReference objects"
        )


def _validate_historical_charter_result(
    result: InitialCharterResult | IntegratedCharterResult,
    stage_name: str,
) -> None:
    if not isinstance(result.check_results, tuple) or not all(
        isinstance(check, CharterCheckResult) for check in result.check_results
    ):
        raise CharterEvaluationInvariantError(
            f"{stage_name} Charter checks must preserve CharterCheckResult objects"
        )
    for check in result.check_results:
        if not isinstance(check.check_id, str) or _malformed_result_error(
            check, check.check_id
        ) is not None:
            raise CharterEvaluationInvariantError(
                f"{stage_name} Charter check structure is malformed"
            )
    if not all(
        isinstance(value, str)
        for value in (result.evaluator_version, result.rule_set_version, result.status)
    ) or not _is_optional_string(result.execution_error):
        raise CharterEvaluationInvariantError(
            f"{stage_name} Charter result fields are malformed"
        )


def _validate_final_artifact(final_result: FinalPathwayResult) -> None:
    if type(final_result) is not FinalPathwayResult:
        raise CharterEvaluationInvariantError(
            "Final Charter evaluation requires exactly FinalPathwayResult"
        )
    trace = final_result.evaluation_trace
    if type(trace) is not EvaluationTrace:
        raise CharterEvaluationInvariantError(
            "FinalPathwayResult must preserve exactly EvaluationTrace"
        )
    product = final_result.product_pathway
    authoritative = final_result.authoritative_transition_pathway
    candidate = final_result.candidate_transition_pathway
    risk = final_result.net_overall_system_risk_result
    initial = trace.initial_charter_result
    engine = trace.pathway_engine_result
    integrated = trace.integrated_charter_result
    contribution = trace.net_overall_system_contribution
    scale = trace.scale_diagnostic_result
    required_types = (
        (product, ProductPathway),
        (authoritative, TransitionPathway),
        (candidate, TransitionPathway),
        (risk, NetOverallSystemRiskResult),
        (initial, InitialCharterResult),
        (engine, PathwayEngineResult),
        (integrated, IntegratedCharterResult),
        (contribution, NetOverallSystemContribution),
        (scale, ScaleDiagnosticResult),
        (final_result.identity_token, IdentityToken),
    )
    if any(type(value) is not expected for value, expected in required_types):
        raise CharterEvaluationInvariantError(
            "Final Charter inputs must preserve exact upstream artifact types"
        )

    relationships = (
        candidate is not authoritative,
        candidate.product_pathway is product,
        candidate.authoritative_transition_pathway is authoritative,
        candidate.net_overall_system_contribution is contribution,
        candidate.scale_diagnostic_result is scale,
        risk.candidate_transition_pathway is candidate,
        risk.authoritative_transition_pathway is authoritative,
        engine.product_pathway is product,
        engine.transition_pathway is authoritative,
        engine.initial_charter_result is initial,
        integrated.pathway_engine_result is engine,
        integrated.initial_charter_result is initial,
        contribution.product_pathway is product,
        contribution.pathway_engine_result is engine,
        contribution.integrated_charter_result is integrated,
        contribution.transition_pathway is authoritative,
        scale.product_pathway is product,
        scale.net_overall_system_contribution is contribution,
        scale.transition_pathway is authoritative,
    )
    if not all(relationships):
        raise CharterEvaluationInvariantError(
            "Final Charter inputs must preserve exact upstream relationships"
        )
    if (
        type(initial.adapter_result) is not ProductAdapterResult
        or initial.adapter_result.product_pathway is not product
    ):
        raise CharterEvaluationInvariantError(
            "Initial Charter result must preserve the current ProductPathway"
        )

    token_id = final_result.identity_token.token_id
    current_tokens = (
        product.identity_token,
        candidate.identity_token,
        initial.identity_token,
        engine.identity_token,
        integrated.identity_token,
    )
    if not isinstance(token_id, str) or any(
        type(token) is not IdentityToken or token.token_id != token_id
        for token in current_tokens
    ):
        raise CharterEvaluationInvariantError(
            "Final Charter inputs must share current IdentityToken lineage"
        )
    current_run_id = final_result.evaluation_run_id
    current_artifacts = (
        product,
        candidate,
        risk,
        initial,
        engine,
        integrated,
        contribution,
        scale,
    )
    if not isinstance(current_run_id, str) or any(
        artifact.evaluation_run_id != current_run_id
        for artifact in current_artifacts
    ):
        raise CharterEvaluationInvariantError(
            "Final Charter inputs must share current evaluation_run_id"
        )
    attributed_artifacts = (product, candidate, risk, engine, contribution, scale)
    if any(
        artifact.user_id != final_result.user_id
        or artifact.pathway_id != final_result.pathway_id
        for artifact in attributed_artifacts
    ):
        raise CharterEvaluationInvariantError(
            "Final Charter inputs must share current user and pathway attribution"
        )
    if not all(
        isinstance(value, str)
        for value in (
            final_result.user_id,
            final_result.pathway_id,
            final_result.assembly_version,
            final_result.assembly_rule_version,
        )
    ):
        raise CharterEvaluationInvariantError(
            "FinalPathwayResult attribution and versions must be strings"
        )

    _validate_historical_charter_result(initial, "Initial")
    _validate_historical_charter_result(integrated, "Integrated")
    for artifact, name in (
        (authoritative, "Authoritative transition"),
        (candidate, "Candidate transition"),
        (risk, "System-risk result"),
        (engine, "Pathway-engine result"),
        (contribution, "Contribution result"),
        (scale, "Scale result"),
    ):
        _validate_provenance(artifact.provenance, name)


def _replace_reused_final_checks(
    check_results: tuple[CharterCheckResult, ...],
    initial: InitialCharterResult,
    integrated: IntegratedCharterResult,
) -> tuple[CharterCheckResult, ...]:
    historical_checks = initial.check_results + integrated.check_results
    return tuple(
        _integrity_failure_result(
            result.check_id,
            CharterCheckStatus.ERROR,
            f"Required Final Charter check {result.check_id} reused prior-stage result",
            result,
        )
        if any(result is historical for historical in historical_checks)
        else result
        for result in check_results
    )


@dataclass(frozen=True, slots=True)
class CharterEvaluator:
    """Run complete independent Charter passes at each evaluation stage."""

    initial_check_function: InitialCharterCheckFunction
    integrated_check_function: IntegratedCharterCheckFunction
    initial_status_function: InitialCharterStatusFunction
    integrated_status_function: IntegratedCharterStatusFunction
    final_check_function: FinalCharterCheckFunction | None = None
    final_status_function: FinalCharterStatusFunction | None = None

    def evaluate_initial(
        self,
        adapter_result: ProductAdapterResult,
        context: CharterEvaluationContext,
    ) -> InitialCharterResult:
        """Execute all Initial checks and construct one immutable result."""

        _validate_initial_artifact(adapter_result)
        definitions = _validate_context(context)
        check_results = _execute_required_checks(
            context.required_check_ids,
            definitions,
            lambda definition: self.initial_check_function(
                adapter_result,
                definition,
                context,
            ),
        )
        execution_error = _integrity_error(check_results)
        if execution_error is None:
            status, execution_error = _stage_status(
                "Initial",
                lambda: self.initial_status_function(
                    adapter_result,
                    check_results,
                    context,
                ),
            )
        else:
            status = "ERROR"
        return InitialCharterResult(
            identity_token=adapter_result.product_pathway.identity_token,
            evaluation_run_id=adapter_result.product_pathway.evaluation_run_id,
            adapter_result=adapter_result,
            check_results=check_results,
            evaluator_version=context.evaluator_version,
            rule_set_version=context.rule_set_version,
            status=status,
            execution_error=execution_error,
        )

    def evaluate_integrated(
        self,
        engine_result: PathwayEngineResult,
        context: CharterEvaluationContext,
    ) -> IntegratedCharterResult:
        """Rerun all checks with Integrated-stage information."""

        _validate_integrated_artifact(engine_result)
        definitions = _validate_context(context)
        check_results = _execute_required_checks(
            context.required_check_ids,
            definitions,
            lambda definition: self.integrated_check_function(
                engine_result,
                definition,
                context,
            ),
        )
        execution_error = _integrity_error(check_results)
        if execution_error is None:
            status, execution_error = _stage_status(
                "Integrated",
                lambda: self.integrated_status_function(
                    engine_result,
                    check_results,
                    context,
                ),
            )
        else:
            status = "ERROR"
        return IntegratedCharterResult(
            identity_token=engine_result.identity_token,
            evaluation_run_id=engine_result.evaluation_run_id,
            pathway_engine_result=engine_result,
            initial_charter_result=engine_result.initial_charter_result,
            check_results=check_results,
            evaluator_version=context.evaluator_version,
            rule_set_version=context.rule_set_version,
            status=status,
            execution_error=execution_error,
        )

    def evaluate_final(
        self,
        final_pathway_result: FinalPathwayResult,
        context: CharterEvaluationContext,
    ) -> FinalCharterResult:
        """Rerun all checks independently with Final-stage information."""

        final_check_function = self.final_check_function
        final_status_function = self.final_status_function
        if final_check_function is None or final_status_function is None:
            raise CharterEvaluationInvariantError(
                "Final Charter evaluation requires Final-stage check and "
                "status functions"
            )
        _validate_final_artifact(final_pathway_result)
        definitions = _validate_context(context)
        check_results = _execute_required_checks(
            context.required_check_ids,
            definitions,
            lambda definition: final_check_function(
                final_pathway_result,
                definition,
                context,
            ),
        )
        trace = final_pathway_result.evaluation_trace
        check_results = _replace_reused_final_checks(
            check_results,
            trace.initial_charter_result,
            trace.integrated_charter_result,
        )
        execution_error = _integrity_error(check_results)
        if execution_error is None:
            status, execution_error = _stage_status(
                "Final",
                lambda: final_status_function(
                    final_pathway_result,
                    check_results,
                    context,
                ),
            )
        else:
            status = "ERROR"
        return FinalCharterResult(
            identity_token=final_pathway_result.identity_token,
            evaluation_run_id=final_pathway_result.evaluation_run_id,
            final_pathway_result=final_pathway_result,
            initial_charter_result=trace.initial_charter_result,
            integrated_charter_result=trace.integrated_charter_result,
            check_results=check_results,
            evaluator_version=context.evaluator_version,
            rule_set_version=context.rule_set_version,
            status=status,
            execution_error=execution_error,
        )
