from abc import ABC, abstractmethod
from typing import Optional
import pymongo
import psycopg
from psycopg.rows import dict_row
from focus_arrow.domain.model import VerifiedEmailEntry, VerificationEmailHistoryEntry


class AbstractVerifiedEmailRepository(ABC):
    @abstractmethod
    def contains(self, entry: VerifiedEmailEntry) -> bool:
        raise NotImplementedError

    @abstractmethod
    def add(self, entry: VerifiedEmailEntry) -> None:
        raise NotImplementedError


class MongoVerifiedEmailRepository(AbstractVerifiedEmailRepository):
    def __init__(self, conn_pool: pymongo.MongoClient):
        db_conn = conn_pool["Focus-Arrow"]
        self._collection = db_conn["verified-emails"]

    def contains(self, entry: VerifiedEmailEntry) -> bool:
        return self._collection.find_one({"address": entry.address}) is not None

    def add(self, entry: VerifiedEmailEntry) -> None:
        if not self.contains(entry):
            self._collection.insert_one({"address": entry.address})


class PostgreVerifiedEmailRepository(AbstractVerifiedEmailRepository):
    def __init__(self, conn_str: str):
        self.conn_str = conn_str

    def contains(self, entry: VerifiedEmailEntry) -> bool:
        with psycopg.connect(self.conn_str) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT * FROM verified_emails WHERE email_address = %s;",
                    (entry.address,),
                )
                result = cur.fetchone()
        return result is not None

    def add(self, entry: VerifiedEmailEntry) -> None:
        with psycopg.connect(self.conn_str) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO verified_emails (email_address) VALUES (%s);",
                    (entry.address,),
                )


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
        db_conn = conn_pool["Focus-Arrow"]
        self._collection = db_conn["verification-email-history"]

    def add_record(self, entry: VerificationEmailHistoryEntry) -> None:
        self._collection.update_one(
            {"address": entry.address},
            {"$set": {"sent": entry.sent, "token": entry.token}},
            True,
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


class PostgreEmailHistoryRepository(AbstractEmailHistoryRepository):
    def __init__(self, conn_str: str):
        self.conn_str = conn_str

    def add_record(self, entry: VerificationEmailHistoryEntry) -> None:
        with psycopg.connect(self.conn_str) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO verification_email_history (address, sent, token)
                            VALUES (%s, %s, %s);
                """,
                    (entry.address, entry.sent, entry.token),
                )

    def get_record_by_address(
        self, address: str
    ) -> Optional[VerificationEmailHistoryEntry]:
        with psycopg.connect(self.conn_str) as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(
                    """
                    SELECT * FROM verification_email_history WHERE address = %s ORDER BY sent DESC;
                """,
                    (address,),
                )
                result = cur.fetchone()
        if result is None:
            return None
        return VerificationEmailHistoryEntry(
            address=result["address"], sent=result["sent"], token=result["token"]
        )

    def get_record_by_token(
        self, token: str
    ) -> Optional[VerificationEmailHistoryEntry]:
        with psycopg.connect(self.conn_str) as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(
                    """
                    SELECT * FROM verification_email_history WHERE token = %s ORDER BY sent DESC;
                """,
                    (token,),
                )
                result = cur.fetchone()
        if result is None:
            return None
        return VerificationEmailHistoryEntry(
            address=result["address"], sent=result["sent"], token=result["token"]
        )
