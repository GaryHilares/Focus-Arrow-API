from dataclasses import dataclass


@dataclass(frozen=True)
class Command:
    pass


@dataclass(frozen=True)
class SendConfirmationEmail(Command):
    address: str


@dataclass(frozen=True)
class ConfirmEmail(Command):
    code: str


@dataclass(frozen=True)
class SendCodeToEmail(Command):
    address: str


@dataclass(frozen=True)
class CheckEmailConfirmed(Command):
    address: str
