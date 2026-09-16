"""Identity-layer construction for product-pathway evaluation."""

from collections.abc import Callable
from dataclasses import dataclass

from .models import EvaluationRun, IdentityToken

EvaluationRunIssuer = Callable[
    [IdentityToken, str | None, str | None],
    EvaluationRun,
]


@dataclass(frozen=True, slots=True)
class IdentityLayer:
    """Establish lineage identity and create a run before pathway intake.

    The supplied issuers own identifier generation and identity-resolution
    semantics. This boundary deliberately performs no authorization.
    """

    identity_token_issuer: Callable[[], IdentityToken]
    evaluation_run_issuer: EvaluationRunIssuer

    def resolve(
        self,
        *,
        identity_token: IdentityToken | None = None,
        predecessor_run_id: str | None = None,
        resolution_record_id: str | None = None,
    ) -> tuple[IdentityToken, EvaluationRun]:
        """Establish or reuse a token and create its immutable evaluation run."""

        token = identity_token or self.identity_token_issuer()
        evaluation_run = self.evaluation_run_issuer(
            token,
            predecessor_run_id,
            resolution_record_id,
        )
        if evaluation_run.identity_token_id != token.token_id:
            raise ValueError("EvaluationRun must reference the resolved IdentityToken")
        if evaluation_run.predecessor_run_id != predecessor_run_id:
            raise ValueError(
                "EvaluationRun must preserve the predecessor run reference"
            )
        if evaluation_run.resolution_record_id != resolution_record_id:
            raise ValueError(
                "EvaluationRun must preserve the resolution record reference"
            )
        return token, evaluation_run
