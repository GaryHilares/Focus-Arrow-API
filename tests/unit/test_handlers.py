from typing import Literal, List, Optional
from focus_arrow.adapters.email import AbstractEmailClient
from focus_arrow.adapters.templates import AbstractTemplateRenderer
from focus_arrow.adapters.token import AbstractTokenGenerator
from focus_arrow.domain.commands import (
    Command,
    VerifyEmail,
    SendTokenToEmail,
    SendVerificationEmail,
)
from focus_arrow.domain.model import (
    ConfirmationEmailRateExceeded,
    ConfirmationLinkNotValid,
    EmailNotVerified,
    VerificationEmailHistoryEntry,
    VerifiedEmailEntry,
)
from focus_arrow.services import handlers
from focus_arrow.services.repositories import (
    AbstractEmailHistoryRepository,
    AbstractVerifiedEmailRepository,
)
from focus_arrow.services.uow import AbstractUnitOfWork
import pytest


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


class FakeTemplateRenderer(AbstractTemplateRenderer):
    def render(self, template_name: str, **kwargs):
        return f"{template_name}: {kwargs}"


def test_sends_confirmation_email():
    email_client = FakeEmailClient()
    token_generator = FakeTokenGenerator()
    template_renderer = FakeTemplateRenderer()
    uow = FakeUnitOfWork()
    command = SendVerificationEmail("user@example.com")
    handlers.send_confirmation_email(
        email_client, token_generator, template_renderer, uow, command
    )
    sent_one = len(email_client.sent) == 1
    email = email_client.sent[0] if sent_one else None
    assert sent_one
    assert email["to_address"] == "user@example.com"
    assert "FAKE_TOKEN" in email["content"]


def test_sends_confirmation_email_to_different_users():
    email_client = FakeEmailClient()
    token_generator = FakeTokenGenerator()
    uow = FakeUnitOfWork()
    template_renderer = FakeTemplateRenderer()
    commands = [
        SendVerificationEmail("bob@example.com"),
        SendVerificationEmail("alice@example.com"),
    ]
    for command in commands:
        handlers.send_confirmation_email(
            email_client, token_generator, template_renderer, uow, command
        )
    assert len(email_client.sent) == 2
    assert email_client.sent[0]["to_address"] == "bob@example.com"
    assert email_client.sent[1]["to_address"] == "alice@example.com"


def test_does_not_spam_confirmation_email_to_same_user():
    uow = FakeUnitOfWork()
    email_client = FakeEmailClient()
    token_generator = FakeTokenGenerator()
    template_renderer = FakeTemplateRenderer()
    command = SendVerificationEmail("bob@example.com")
    with pytest.raises(ConfirmationEmailRateExceeded):
        for _ in range(1000):
            handlers.send_confirmation_email(
                email_client, token_generator, template_renderer, uow, command
            )
    assert len(email_client.sent) <= 10


def test_does_not_confirms_email_with_non_existing_token():
    uow = FakeUnitOfWork()
    email_client = FakeEmailClient()
    token_generator = FakeTokenGenerator()
    template_renderer = FakeTemplateRenderer()
    handlers.send_confirmation_email(
        email_client,
        token_generator,
        template_renderer,
        uow,
        SendVerificationEmail("bob@example.com"),
    )
    with pytest.raises(ConfirmationLinkNotValid):
        handlers.verify_email(uow, VerifyEmail("NON_EXISTING_TOKEN"))
    assert not uow.verified_emails.contains("bob@example.com")


def test_confirms_email_with_right_token():
    uow = FakeUnitOfWork()
    email_client = FakeEmailClient()
    token_generator = FakeTokenGenerator()
    template_renderer = FakeTemplateRenderer()
    handlers.send_confirmation_email(
        email_client,
        token_generator,
        template_renderer,
        uow,
        SendVerificationEmail("bob@example.com"),
    )
    handlers.verify_email(uow, VerifyEmail("FAKE_TOKEN"))
    assert uow.verified_emails.contains(VerifiedEmailEntry("bob@example.com"))


def test_sends_code_to_verified_email():
    uow = FakeUnitOfWork()
    email_client = FakeEmailClient()
    token_generator = FakeTokenGenerator()
    template_renderer = FakeTemplateRenderer()
    handlers.send_confirmation_email(
        email_client,
        token_generator,
        template_renderer,
        uow,
        SendVerificationEmail("bob@example.com"),
    )
    handlers.verify_email(uow, VerifyEmail("FAKE_TOKEN"))
    code = handlers.send_token_to_email(
        email_client,
        token_generator,
        template_renderer,
        uow,
        SendTokenToEmail("bob@example.com"),
    )
    assert "bob@example.com" == email_client.sent[0]["to_address"]
    assert code in email_client.sent[0]["content"]


def test_does_not_send_code_to_unverified_email():
    uow = FakeUnitOfWork()
    email_client = FakeEmailClient()
    token_generator = FakeTokenGenerator()
    template_renderer = FakeTemplateRenderer()
    with pytest.raises(EmailNotVerified):
        handlers.send_token_to_email(
            email_client,
            token_generator,
            template_renderer,
            uow,
            SendTokenToEmail("bob@example.com"),
        )
    assert len(email_client.sent) == 0
