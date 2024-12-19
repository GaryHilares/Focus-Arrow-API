from jinja2 import PackageLoader
from liberty_arrow.adapters.email import GmailClient
from liberty_arrow.adapters.templates import JinjaTemplateRenderer
from liberty_arrow.adapters.token import RandomTokenGenerator
from liberty_arrow.services.message_bus import MessageBus
from liberty_arrow.domain.commands import (
    VerifyEmail,
    SendTokenToEmail,
    SendVerificationEmail,
    CheckEmailConfirmed,
)
from liberty_arrow.services.handlers import (
    send_confirmation_email,
    verify_email,
    send_token_to_email,
    check_email_confirmed,
)
from functools import partial
from liberty_arrow.services.uow import MongoUnitOfWork
from os import getenv
from pymongo import MongoClient


def bootstrap() -> MessageBus:
    URL = f"mongodb+srv://{getenv('MONGODB_USER')}:{getenv('MONGODB_PASSWORD')}@{getenv('MONGODB_HOST')}/?retryWrites=true&w=majority"
    conn_pool = MongoClient(URL)
    uow = MongoUnitOfWork(conn_pool)
    email_client = GmailClient(getenv("GMAIL_USERNAME"), getenv("GMAIL_APP_PASSWORD"))
    pin_generator = RandomTokenGenerator()
    template_renderer = JinjaTemplateRenderer(PackageLoader("liberty_arrow"))

    command_handlers = {
        VerifyEmail: verify_email,
        SendTokenToEmail: partial(
            send_token_to_email, email_client, pin_generator, template_renderer
        ),
        SendVerificationEmail: partial(
            send_confirmation_email, email_client, pin_generator, template_renderer
        ),
        CheckEmailConfirmed: check_email_confirmed,
    }

    return MessageBus(uow, command_handlers)
