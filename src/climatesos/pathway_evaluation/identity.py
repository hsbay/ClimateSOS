"""Identity-layer construction for product-pathway evaluation."""

from collections.abc import Callable
from dataclasses import dataclass

from .models import IdentityToken


@dataclass(frozen=True, slots=True)
class IdentityLayer:
    """Expose caller-supplied canonical identity issuance to pathway intake.

    The specification does not yet define how identity is generated,
    authorized, or issued. The supplied issuer owns those semantics.
    """

    issuer: Callable[[], IdentityToken]

    def issue(self) -> IdentityToken:
        """Return the canonical token produced by the configured issuer."""

        return self.issuer()
