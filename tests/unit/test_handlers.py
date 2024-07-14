from audioop import add
import email
from typing import Literal, List, Optional
from liberty_arrow.adapters.email import AbstractEmailClient
from liberty_arrow.adapters.token import AbstractTokenGenerator
from liberty_arrow.domain.commands import (
    Command,
    ConfirmEmail,
    SendCodeToEmail,
    SendConfirmationEmail,
)
from liberty_arrow.domain.model import VerificationEmailHistoryEntry, VerifiedEmailEntry
from liberty_arrow.services import handlers
from liberty_arrow.services.repositories import (
    AbstractEmailHistoryRepository,
    AbstractVerifiedEmailRepository,
)
from liberty_arrow.services.uow import AbstractUnitOfWork


class FakeEmailClient(AbstractEmailClient):
    def __init__(self):
        self.sent = []

    def send(self, to_address: str, subject: str, content: str) -> None:
        self.sent.append(
            {"to_address": to_address, "subject": subject, "content": content}
        )


class FakeTokenGenerator(AbstractTokenGenerator):
    def generate(self) -> Literal["FAKE_TOKEN"]:
        return "FAKE_TOKEN"


class FakeVerifiedEmailRepository(AbstractVerifiedEmailRepository):
    def __init__(self):
        self.collection = set()

    def contains(self, entry: VerifiedEmailEntry) -> bool:
        return entry in self.collection

    def add(self, entry: VerifiedEmailEntry) -> None:
        self.collection.add(entry)


class FakeEmailHistoryRepository(AbstractEmailHistoryRepository):
    def __init__(self):
        self.collection = []

    def add_record(self, entry: VerificationEmailHistoryEntry) -> None:
        self.collection.append(entry)

    def get_record_by_address(
        self, address: str
    ) -> Optional[VerificationEmailHistoryEntry]:
        for record in self.collection:
            if record.address == address:
                return record
        return None

    def get_record_by_token(
        self, token: str
    ) -> Optional[VerificationEmailHistoryEntry]:
        for record in self.collection:
            if record.token == token:
                return record
        return None


class FakeUnitOfWork(AbstractUnitOfWork):
    def __init__(self):
        self._emails = FakeVerifiedEmailRepository()
        self._email_history = FakeEmailHistoryRepository()
        self.messages = []

    @property
    def verified_emails(self) -> FakeVerifiedEmailRepository:
        return self._emails

    @property
    def email_history(self) -> FakeEmailHistoryRepository:
        return self._email_history

    def add_message(self, message: Command) -> None:
        self.messages.append(message)

    def flush_messages(self) -> List[Command]:
        ret = self.messages
        self.messages = []
        return ret


def test_sends_confirmation_email_once_per_day():
    email_client = FakeEmailClient()
    token_generator = FakeTokenGenerator()
    uow = FakeUnitOfWork()
    commands = [
        SendConfirmationEmail("user@example.com"),
        SendConfirmationEmail("user@example.com"),
    ]
    for command in commands:
        handlers.send_confirmation_email(email_client, token_generator, uow, command)
    sent_one = len(email_client.sent) == 1
    email = email_client.sent[0] if sent_one else None
    assert sent_one
    assert email["to_address"] == "user@example.com"
    assert "FAKE_TOKEN" in email["content"]


def test_sends_confirmation_email_to_different_users():
    email_client = FakeEmailClient()
    token_generator = FakeTokenGenerator()
    uow = FakeUnitOfWork()
    commands = [
        SendConfirmationEmail("bob@example.com"),
        SendConfirmationEmail("alice@example.com"),
    ]
    for command in commands:
        handlers.send_confirmation_email(email_client, token_generator, uow, command)
    assert len(email_client.sent) == 2
    assert email_client.sent[0]["to_address"] == "bob@example.com"
    assert email_client.sent[1]["to_address"] == "alice@example.com"


def test_does_not_spam_confirmation_email_to_same_user():
    uow = FakeUnitOfWork()
    email_client = FakeEmailClient()
    token_generator = FakeTokenGenerator()
    command = SendConfirmationEmail("bob@example.com")
    for _ in range(1000):
        handlers.send_confirmation_email(email_client, token_generator, uow, command)
    assert len(email_client.sent) <= 10


def test_does_not_confirms_email_with_non_existing_token():
    uow = FakeUnitOfWork()
    email_client = FakeEmailClient()
    token_generator = FakeTokenGenerator()
    handlers.send_confirmation_email(
        email_client, token_generator, uow, SendConfirmationEmail("bob@example.com")
    )
    handlers.confirm_email(uow, ConfirmEmail("NON_EXISTING_TOKEN"))
    assert not uow.verified_emails.contains("bob@example.com")


def test_confirms_email_with_right_token():
    uow = FakeUnitOfWork()
    email_client = FakeEmailClient()
    token_generator = FakeTokenGenerator()
    handlers.send_confirmation_email(
        email_client, token_generator, uow, SendConfirmationEmail("bob@example.com")
    )
    handlers.confirm_email(uow, ConfirmEmail("FAKE_TOKEN"))
    assert uow.verified_emails.contains("bob@example.com")


def test_sends_code_to_verified_email():
    uow = FakeUnitOfWork()
    email_client = FakeEmailClient()
    token_generator = FakeTokenGenerator()
    handlers.send_confirmation_email(
        email_client, token_generator, uow, SendConfirmationEmail("bob@example.com")
    )
    handlers.confirm_email(uow, ConfirmEmail("FAKE_TOKEN"))
    code = handlers.send_code_email(
        email_client, token_generator, uow, SendCodeToEmail("bob@example.com")
    )
    assert "bob@example.com" == email_client.sent[0]["to_address"]
    assert code in email_client.sent[0]["content"]


def test_does_not_send_code_to_unverified_email():
    uow = FakeUnitOfWork()
    email_client = FakeEmailClient()
    token_generator = FakeTokenGenerator()
    handlers.send_code_email(
        email_client, token_generator, uow, SendCodeToEmail("bob@example.com")
    )
    assert len(email_client.sent) == 0
