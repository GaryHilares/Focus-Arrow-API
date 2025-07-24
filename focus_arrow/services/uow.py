from abc import ABC, abstractmethod
from typing import List
from pymongo import MongoClient
from focus_arrow.domain.commands import Command
from focus_arrow.services.repositories import (
    AbstractEmailHistoryRepository,
    AbstractVerifiedEmailRepository,
    MongoEmailHistoryRepository,
    MongoVerifiedEmailRepository,
    PostgreEmailHistoryRepository,
    PostgreVerifiedEmailRepository,
)


class AbstractUnitOfWork(ABC):
    @property
    @abstractmethod
    def verified_emails() -> AbstractVerifiedEmailRepository:
        raise NotImplementedError

    @property
    @abstractmethod
    def email_history() -> AbstractEmailHistoryRepository:
        raise NotImplementedError

    @abstractmethod
    def add_message(self, message: Command) -> None:
        raise NotImplementedError

    @abstractmethod
    def flush_messages(self) -> List[Command]:
        raise NotImplementedError


class MongoUnitOfWork(AbstractUnitOfWork):
    def __init__(self, conn_pool: MongoClient):
        self._emails = MongoVerifiedEmailRepository(conn_pool)
        self._email_history = MongoEmailHistoryRepository(conn_pool)
        self.messages = []

    @property
    def verified_emails(self):
        return self._emails

    @property
    def email_history(self):
        return self._email_history

    def add_message(self, message: Command) -> None:
        self.messages.append(message)

    def flush_messages(self) -> List[Command]:
        ret = self.messages
        self.messages = []
        return ret


class PostgreUnitOfWork(AbstractUnitOfWork):
    def __init__(self, conn_str: str):
        self._emails = PostgreVerifiedEmailRepository(conn_str)
        self._email_history = PostgreEmailHistoryRepository(conn_str)
        self.messages = []

    @property
    def verified_emails(self):
        return self._emails

    @property
    def email_history(self):
        return self._email_history

    def add_message(self, message: Command) -> None:
        self.messages.append(message)

    def flush_messages(self) -> List[Command]:
        ret = self.messages
        self.messages = []
        return ret
