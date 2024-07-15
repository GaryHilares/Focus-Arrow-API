from datetime import datetime
from liberty_arrow.adapters.token import AbstractTokenGenerator
from liberty_arrow.adapters.email import AbstractEmailClient
from liberty_arrow.adapters.templates import AbstractTemplateRenderer
from liberty_arrow.domain.model import (
    ConfirmationEmailRateExceeded,
    ConfirmationLinkNotValid,
    EmailNotVerified,
    VerificationEmailHistoryEntry,
    VerifiedEmailEntry,
)
from liberty_arrow.services.uow import AbstractUnitOfWork
from liberty_arrow.domain.commands import (
    SendConfirmationEmail,
    ConfirmEmail,
    SendCodeToEmail,
)


def send_confirmation_email(
    email_client: AbstractEmailClient,
    token_generator: AbstractTokenGenerator,
    template_renderer: AbstractTemplateRenderer,
    uow: AbstractUnitOfWork,
    command: SendConfirmationEmail,
):
    email_history_record = uow.email_history.get_record_by_address(command.address)
    if uow.verified_emails.contains(VerifiedEmailEntry(command.address)) or (
        email_history_record is not None
        and email_history_record.sent.date() == datetime.today().date()
    ):
        raise ConfirmationEmailRateExceeded
    token = token_generator.generate()
    content = template_renderer.render("emails/confirmation.html", token=token)
    email_client.send(command.address, "Confirm your Liberty Arrow token", content)
    uow.email_history.add_record(
        VerificationEmailHistoryEntry(command.address, datetime.now(), token)
    )


def confirm_email(uow: AbstractUnitOfWork, command: ConfirmEmail):
    record = uow.email_history.get_record_by_token(command.code)
    if record is None or record.sent.date() != datetime.today().date():
        raise ConfirmationLinkNotValid
    uow.verified_emails.add(VerifiedEmailEntry(record.address))


def send_code_email(
    email_client: AbstractEmailClient,
    token_generator: AbstractTokenGenerator,
    template_renderer: AbstractTemplateRenderer,
    uow: AbstractUnitOfWork,
    command: SendCodeToEmail,
):
    if not uow.verified_emails.contains(VerifiedEmailEntry(command.address)):
        raise EmailNotVerified
    token = token_generator.generate()
    content = template_renderer.render("emails/token.html", token=token)
    email_client.send(command.address, "Liberty Arrow token", content)
    return token
