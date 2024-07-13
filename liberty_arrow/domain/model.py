from datetime import datetime
from dataclasses import dataclass


@dataclass(frozen=True)
class VerifiedEmailEntry:
    """
    Records an email that is verified to receive emails from Liberty Arrow.
    """

    address: str


@dataclass(frozen=True)
class VerificationEmailHistoryEntry:
    """
    Records the last time that an email was sent by Liberty Arrow to the given address.
    """

    address: str
    sent: datetime
    token: str
