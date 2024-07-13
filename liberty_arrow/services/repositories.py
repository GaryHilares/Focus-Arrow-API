from abc import ABC, abstractmethod
from typing import Optional
import pymongo
from liberty_arrow.domain.model import VerifiedEmailEntry, VerificationEmailHistoryEntry


class AbstractVerifiedEmailRepository(ABC):
    @abstractmethod
    def contains(self, entry: VerifiedEmailEntry) -> bool:
        raise NotImplementedError

    @abstractmethod
    def add(self, entry: VerifiedEmailEntry) -> None:
        raise NotImplementedError


class MongoVerifiedEmailRepository(AbstractVerifiedEmailRepository):
    def __init__(self, conn_pool: pymongo.MongoClient):
        db_conn = conn_pool["Liberty-Arrow"]
        self._collection = db_conn["verification-email-history"]

    def contains(self, entry: VerifiedEmailEntry) -> bool:
        return self._collection.find_one({"address": entry.address}) is not None

    def add(self, entry: VerifiedEmailEntry) -> None:
        if not self.contains(entry):
            self._collection.insert_one({"address": entry.address})


class AbstractEmailHistoryRepository(ABC):
    @abstractmethod
    def add_record(self, entry: VerificationEmailHistoryEntry) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_record_by_address(
        self, address: str
    ) -> Optional[VerificationEmailHistoryEntry]:
        raise NotImplementedError

    @abstractmethod
    def get_record_by_token(
        self, token: str
    ) -> Optional[VerificationEmailHistoryEntry]:
        raise NotImplementedError


class MongoEmailHistoryRepository(AbstractEmailHistoryRepository):
    def __init__(self, conn_pool: pymongo.MongoClient):
        db_conn = conn_pool["Liberty-Arrow"]
        self._collection = db_conn["verified-emails"]

    def add_record(self, entry: VerificationEmailHistoryEntry) -> None:
        self._collection.update_one(
            {"address": entry.address}, {"sent": entry.sent, "token": entry.token}, True
        )

    def get_record_by_address(
        self, address: str
    ) -> Optional[VerificationEmailHistoryEntry]:
        record = self._collection.find_one({"address": address})
        if record is None:
            return None
        return VerificationEmailHistoryEntry(
            address=record["address"], sent=record["sent"], token=record["token"]
        )

    def get_record_by_token(
        self, token: str
    ) -> Optional[VerificationEmailHistoryEntry]:
        record = self._collection.find_one({"token": token})
        if record is None:
            return None
        return VerificationEmailHistoryEntry(
            address=record["address"], sent=record["sent"], token=record["token"]
        )
