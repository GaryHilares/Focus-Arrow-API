from liberty_arrow.domain.model import VerifiedEmailEntry
from liberty_arrow.services import repositories
from dotenv import dotenv_values
from pymongo import MongoClient


def test_verified_email_repository_with_single_user():
    config = dotenv_values(".env")
    URL = f"mongodb+srv://{config['MONGODB_USER']}:{config['MONGODB_PASSWORD']}@{config['MONGODB_HOST']}/?retryWrites=true&w=majority"
    conn_pool = MongoClient(URL)
    repo = repositories.MongoVerifiedEmailRepository(conn_pool)
    repo.add(VerifiedEmailEntry("someuser@example.com"))
    assert repo.contains(VerifiedEmailEntry("someuser@example.com"))
    assert not repo.contains(VerifiedEmailEntry("otheruser@example.com"))
    assert not repo.contains(VerifiedEmailEntry("bob@example.org"))
    assert not repo.contains(VerifiedEmailEntry("thirduser@example.io"))


def test_verified_email_repository_with_multiple_users():
    config = dotenv_values(".env")
    URL = f"mongodb+srv://{config['MONGODB_USER']}:{config['MONGODB_PASSWORD']}@{config['MONGODB_HOST']}/?retryWrites=true&w=majority"
    conn_pool = MongoClient(URL)
    repo = repositories.MongoVerifiedEmailRepository(conn_pool)
    repo.add(VerifiedEmailEntry("bob2@example.org"))
    repo.add(VerifiedEmailEntry("alice2@example.com"))
    assert repo.contains(VerifiedEmailEntry("bob2@example.org"))
    assert repo.contains(VerifiedEmailEntry("alice2@example.com"))
    assert not repo.contains(VerifiedEmailEntry("someuser2@example.com"))
    assert not repo.contains(VerifiedEmailEntry("otheruser2@example.com"))
    assert not repo.contains(VerifiedEmailEntry("thirduser2@example.io"))
