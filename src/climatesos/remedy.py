# Climate State transition model OS
# Github Project Code: https://github.com/hsbay/ClimateSOS, CC-BY 4.0 2026 @safiume

"""Minimal RemedyBus helpers for the ClimateSOS v0.7 toy runtime."""

from .models import RemedyBus
from .states import RemedyBusStatus


def accepted_remedy(conditions_verified: bool = True, notes: str = "") -> RemedyBus:
    """Create a RemedyBus state for accepted corrective evidence.

    The RemedyBus does not authorize continuation. It only marks that corrective
    evidence exists and that the token should be re-evaluated by the evaluator.
    """

    return RemedyBus(
        status=RemedyBusStatus.REMEDY_ACCEPTED,
        conditions_verified=conditions_verified,
        notes=notes,
    )


def incomplete_remedy(notes: str = "") -> RemedyBus:
    """Create a RemedyBus state for incomplete corrective action."""

    return RemedyBus(status=RemedyBusStatus.REMEDY_INCOMPLETE, notes=notes)
