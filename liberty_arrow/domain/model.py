from datetime import datetime
from dataclasses import dataclass


@dataclass
class VerifiedEmailEntry:
    """
    Records an email that is verified to receive emails from Liberty Arrow.
    """

    address: str


@dataclass
class VerificationEmailHistoryEntry:
    """
    Records the last time that an email was sent by Liberty Arrow to the given address.
    """

    address: str
    sent: datetime
    token: str
