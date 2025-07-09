from datetime import datetime
from focus_arrow.adapters.token import AbstractTokenGenerator
from focus_arrow.adapters.email import AbstractEmailClient
from focus_arrow.adapters.templates import AbstractTemplateRenderer
from focus_arrow.domain.model import (
    ConfirmationEmailRateExceeded,
    ConfirmationLinkNotValid,
    EmailNotVerified,
    VerificationEmailHistoryEntry,
    VerifiedEmailEntry,
)
from focus_arrow.services.uow import AbstractUnitOfWork
from focus_arrow.domain.commands import (
    SendVerificationEmail,
    VerifyEmail,
    SendTokenToEmail,
    CheckEmailConfirmed,
    SendUninstallationEmail,
)


def send_confirmation_email(
    email_client: AbstractEmailClient,
    token_generator: AbstractTokenGenerator,
    template_renderer: AbstractTemplateRenderer,
    uow: AbstractUnitOfWork,
    command: SendVerificationEmail,
) -> None:
    email_history_record = uow.email_history.get_record_by_address(command.address)
    if uow.verified_emails.contains(VerifiedEmailEntry(command.address)) or (
        email_history_record is not None
        and email_history_record.sent.date() == datetime.today().date()
    ):
        raise ConfirmationEmailRateExceeded
    token = token_generator.generate()
    content = template_renderer.render("emails/confirmation.html", token=token)
    email_client.send(command.address, "Confirm your Focus Arrow token", content)
    uow.email_history.add_record(
        VerificationEmailHistoryEntry(command.address, datetime.now(), token)
    )


def verify_email(uow: AbstractUnitOfWork, command: VerifyEmail) -> None:
    record = uow.email_history.get_record_by_token(command.token)
    if record is None or record.sent.date() != datetime.today().date():
        raise ConfirmationLinkNotValid
    uow.verified_emails.add(VerifiedEmailEntry(record.address))


def check_email_confirmed(
    uow: AbstractUnitOfWork, command: CheckEmailConfirmed
) -> bool:
    return uow.verified_emails.contains(VerifiedEmailEntry(command.address))


def send_token_to_email(
    email_client: AbstractEmailClient,
    token_generator: AbstractTokenGenerator,
    template_renderer: AbstractTemplateRenderer,
    uow: AbstractUnitOfWork,
    command: SendTokenToEmail,
) -> str:
    if not uow.verified_emails.contains(VerifiedEmailEntry(command.address)):
        raise EmailNotVerified
    token = token_generator.generate()
    content = template_renderer.render("emails/token.html", token=token)
    email_client.send(command.address, "Focus Arrow token", content)
    return token


def send_uninstallation_email(
    email_client: AbstractEmailClient,
    template_renderer: AbstractTemplateRenderer,
    uow: AbstractUnitOfWork,
    command: SendUninstallationEmail,
):
    if not uow.verified_emails.contains(VerifiedEmailEntry(command.address)):
        raise EmailNotVerified
    content = template_renderer.render("emails/uninstallation.html")
    email_client.send(command.address, "Focus Arrow was uninstalled", content)
