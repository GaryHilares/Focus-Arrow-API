from typing import Any, Callable, Dict
from liberty_arrow.domain.commands import Command
from liberty_arrow.services.uow import AbstractUnitOfWork

Message = Command


class MessageBus:
    def __init__(
        self,
        uow: AbstractUnitOfWork,
        command_handlers: Dict[type, Callable[[Command], None]],
    ):
        self.uow = uow
        self.command_handlers = command_handlers

    def handle_command(self, command: Command):
        return self.command_handlers[type(command)](self.uow, command)

    def handle_message(self, message: Message) -> Any:
        messages = [message]
        results = []
        while len(messages) > 0:
            to_handle = messages.pop(0)
            if isinstance(to_handle, Command):
                results.append(self.handle_command(to_handle))
            messages.extend(self.uow.flush_messages())
        return results[0]
