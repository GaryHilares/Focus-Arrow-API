from dataclasses import dataclass


@dataclass(frozen=True)
class Command:
    pass


@dataclass(frozen=True)
class SendVerificationEmail(Command):
    address: str


@dataclass(frozen=True)
class VerifyEmail(Command):
    token: str


@dataclass(frozen=True)
class SendTokenToEmail(Command):
    address: str


@dataclass(frozen=True)
class CheckEmailConfirmed(Command):
    address: str
