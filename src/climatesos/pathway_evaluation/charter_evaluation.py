"""Structural execution boundary for Initial and Integrated Charter passes."""

from collections.abc import Callable
from dataclasses import dataclass
from typing import cast

from .models import (
    Attribute,
    CharterCheckResult,
    CharterEvaluationContext,
    InitialCharterResult,
    IntegratedCharterResult,
    OpaqueReference,
    PathwayEngineResult,
    ProductAdapterResult,
    SourceReference,
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


class CharterEvaluationInvariantError(ValueError):
    """Raised when a Charter pass is structurally incomplete or incoherent."""


def _is_string(value: object) -> bool:
    return isinstance(value, str)


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
    if not _is_string(result.status):
        return f"Required Charter check {expected_check_id} returned malformed status"
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
    if result.status != "MISSING" and result.execution_error is not None:
        return (
            f"Required Charter check {expected_check_id} returned execution error "
            f"with non-MISSING status: {result.execution_error}"
        )
    return None


def _missing_check_result(
    check_id: str,
    execution_error: str,
    malformed_result: object = None,
) -> CharterCheckResult:
    if (
        not isinstance(malformed_result, CharterCheckResult)
        or malformed_result.check_id != check_id
    ):
        return CharterCheckResult(
            check_id=check_id,
            status="MISSING",
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
        status="MISSING",
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
            results.append(_missing_check_result(check_id, execution_error))
            continue
        malformed_error = _malformed_result_error(raw_result, check_id)
        if malformed_error is not None:
            results.append(_missing_check_result(check_id, malformed_error, raw_result))
            continue
        results.append(cast(CharterCheckResult, raw_result))
    return tuple(results)


def _integrity_error(check_results: tuple[CharterCheckResult, ...]) -> str | None:
    errors = tuple(
        result.execution_error or f"Required Charter check {result.check_id} is MISSING"
        for result in check_results
        if result.status == "MISSING"
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
    if initial_result.status == "ERROR" and initial_result.execution_error is not None:
        raise CharterEvaluationInvariantError(
            "Integrated Charter evaluation cannot consume an Initial Charter "
            "evaluator-integrity ERROR"
        )
    if initial_result.adapter_result.product_pathway is not pathway:
        raise CharterEvaluationInvariantError(
            "PathwayEngineResult must preserve the Initial Charter pathway reference"
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
    ):
        raise CharterEvaluationInvariantError(
            "Integrated Charter artifact EvaluationRun must match the ProductPathway"
        )


@dataclass(frozen=True, slots=True)
class ValidatedCharterEvaluator:
    """Run complete independent Initial and Integrated Charter passes."""

    initial_check_function: InitialCharterCheckFunction
    integrated_check_function: IntegratedCharterCheckFunction
    initial_status_function: InitialCharterStatusFunction
    integrated_status_function: IntegratedCharterStatusFunction

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
