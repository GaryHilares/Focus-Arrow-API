import datetime
import pytest
from liberty_arrow.domain.model import VerificationEmailHistoryEntry, VerifiedEmailEntry
from liberty_arrow.services import repositories
from dotenv import dotenv_values
from pymongo import MongoClient


@pytest.fixture
def verified_email_repo() -> repositories.MongoVerifiedEmailRepository:
    config = dotenv_values(".env")
    URL = f"mongodb+srv://{config['MONGODB_USER']}:{config['MONGODB_PASSWORD']}@{config['MONGODB_HOST']}/?retryWrites=true&w=majority"
    conn_pool = MongoClient(URL)
    return repositories.MongoVerifiedEmailRepository(conn_pool)


@pytest.fixture
def email_history_repo() -> repositories.MongoEmailHistoryRepository:
    config = dotenv_values(".env")
    URL = f"mongodb+srv://{config['MONGODB_USER']}:{config['MONGODB_PASSWORD']}@{config['MONGODB_HOST']}/?retryWrites=true&w=majority"
    conn_pool = MongoClient(URL)
    return repositories.MongoEmailHistoryRepository(conn_pool)


def test_verified_email_repository_with_single_user(verified_email_repo):
    repo = verified_email_repo
    repo.add(VerifiedEmailEntry("someuser@example.com"))
    assert repo.contains(VerifiedEmailEntry("someuser@example.com"))
    assert not repo.contains(VerifiedEmailEntry("otheruser@example.com"))
    assert not repo.contains(VerifiedEmailEntry("bob@example.org"))
    assert not repo.contains(VerifiedEmailEntry("thirduser@example.io"))
    repo._collection.delete_one({"address": "someuser@example.com"})


def test_verified_email_repository_with_multiple_users(verified_email_repo):
    repo = verified_email_repo
    repo.add(VerifiedEmailEntry("bob2@example.org"))
    repo.add(VerifiedEmailEntry("alice2@example.com"))
    assert repo.contains(VerifiedEmailEntry("bob2@example.org"))
    assert repo.contains(VerifiedEmailEntry("alice2@example.com"))
    assert not repo.contains(VerifiedEmailEntry("someuser2@example.com"))
    assert not repo.contains(VerifiedEmailEntry("otheruser2@example.com"))
    assert not repo.contains(VerifiedEmailEntry("thirduser2@example.io"))
    repo._collection.delete_one({"address": "bob2@example.org"})
    repo._collection.delete_one({"address": "alice2@example.com"})


def test_email_history_repo_records_and_retrieves_records(email_history_repo):
    expected_bob_record = VerificationEmailHistoryEntry(
        "bob@example.com", datetime.datetime(2024, 1, 1), "BOB_TOKEN"
    )
    expected_alice_record = VerificationEmailHistoryEntry(
        "alice@example.org", datetime.datetime(2023, 5, 7), "ALICE_TOKEN"
    )
    email_history_repo.add_record(expected_bob_record)
    email_history_repo.add_record(expected_alice_record)
    actual__bob_record = email_history_repo.get_record_by_address("bob@example.com")
    actual_alice_record = email_history_repo.get_record_by_token("ALICE_TOKEN")
    assert actual__bob_record == expected_bob_record
    assert actual_alice_record == expected_alice_record
    email_history_repo._collection.delete_one({"address": "bob@example.com"})
    email_history_repo._collection.delete_one({"address": "alice@example.org"})
