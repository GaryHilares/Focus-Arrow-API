from dataclasses import dataclass


@dataclass
class Command:
    pass


@dataclass
class SendConfirmationEmail(Command):
    address: str


@dataclass
class ConfirmEmail(Command):
    code: str


@dataclass
class SendCodeToEmail(Command):
    address: str
