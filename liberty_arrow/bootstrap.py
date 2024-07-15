from jinja2 import PackageLoader
from liberty_arrow.adapters.email import GmailClient
from liberty_arrow.adapters.templates import JinjaTemplateRenderer
from liberty_arrow.adapters.token import RandomTokenGenerator
from liberty_arrow.services.message_bus import MessageBus
from liberty_arrow.domain.commands import (
    ConfirmEmail,
    SendCodeToEmail,
    SendConfirmationEmail,
)
from liberty_arrow.services.handlers import (
    send_confirmation_email,
    confirm_email,
    send_code_email,
)
from functools import partial
from liberty_arrow.services.uow import MongoUnitOfWork
from dotenv import dotenv_values
from pymongo import MongoClient


def bootstrap() -> MessageBus:
    config = dotenv_values(".env")
    URL = f"mongodb+srv://{config['MONGODB_USER']}:{config['MONGODB_PASSWORD']}@{config['MONGODB_HOST']}/?retryWrites=true&w=majority"
    conn_pool = MongoClient(URL)
    uow = MongoUnitOfWork(conn_pool)
    email_client = GmailClient(config["GMAIL_USERNAME"], config["GMAIL_APP_PASSWORD"])
    pin_generator = RandomTokenGenerator()
    template_renderer = JinjaTemplateRenderer(PackageLoader("liberty_arrow"))

    command_handlers = {
        ConfirmEmail: confirm_email,
        SendCodeToEmail: partial(
            send_code_email, email_client, pin_generator, template_renderer
        ),
        SendConfirmationEmail: partial(
            send_confirmation_email, email_client, pin_generator, template_renderer
        ),
    }

    return MessageBus(uow, command_handlers)
