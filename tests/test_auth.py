# tests/test_auth.py

import pytest
from flask import url_for
from werkzeug.security import generate_password_hash
from app.models.user import User
from app.extensions import db


@pytest.fixture
def test_user(session):
    """
    Create a verified user with hashed password for authentication tests.
    """
    user = User(
        email="testuser@isreal.ai",
        name="Test User",
        password_hash=generate_password_hash("TestPassword123"),
        role="user",
        is_verified=True
    )
    session.add(user)
    session.commit()
    return user


def test_login_success(client, test_user):
    """
    Login using correct credentials and verify successful redirect.
    """
    response = client.post(
        url_for("auth.login"),
        data={"email": "testuser@isreal.ai", "password": "TestPassword123"},
        follow_redirects=True
    )
    assert response.status_code == 200
    assert b"Welcome" in response.data or b"Dashboard" in response.data


def test_login_failure_wrong_password(client, test_user):
    """
    Attempt login with incorrect password.
    """
    response = client.post(
        url_for("auth.login"),
        data={"email": "testuser@isreal.ai", "password": "WrongPassword"},
        follow_redirects=True
    )
    assert response.status_code == 200
    assert b"Invalid email or password" in response.data


def test_login_failure_unregistered_email(client):
    """
    Attempt login with unregistered email.
    """
    response = client.post(
        url_for("auth.login"),
        data={"email": "ghost@isreal.ai", "password": "NoUserPass"},
        follow_redirects=True
    )
    assert response.status_code == 200
    assert b"Invalid email or password" in response.data


def test_login_failure_unverified_user(client, session):
    """
    Attempt login with a user who is not verified.
    """
    user = User(
        email="unverified@isreal.ai",
        name="Unverified User",
        password_hash=generate_password_hash("Unverified123"),
        role="user",
        is_verified=False
    )
    session.add(user)
    session.commit()

    response = client.post(
        url_for("auth.login"),
        data={"email": "unverified@isreal.ai", "password": "Unverified123"},
        follow_redirects=True
    )
    assert response.status_code == 200
    assert b"verify your email" in response.data.lower()


def test_reset_password_request_success(client, test_user):
    """
    Successfully request a password reset email.
    """
    response = client.post(
        url_for("auth.reset_password_request"),
        data={"email": "testuser@isreal.ai"},
        follow_redirects=True
    )
    assert response.status_code == 200
    assert b"password reset link" in response.data.lower()


def test_reset_password_request_unknown_email(client):
    """
    Request password reset for non-existent account.
    """
    response = client.post(
        url_for("auth.reset_password_request"),
        data={"email": "unknown@isreal.ai"},
        follow_redirects=True
    )
    assert response.status_code == 200
    assert b"email not found" in response.data.lower() or b"no account" in response.data.lower()


def test_register_new_user_success(client):
    """
    Successfully register a new user.
    """
    response = client.post(
        url_for("auth.register"),
        data={
            "email": "newuser@isreal.ai",
            "name": "New User",
            "password": "SecurePass456",
            "confirm_password": "SecurePass456"
        },
        follow_redirects=True
    )
    assert response.status_code == 200
    assert b"verify your email" in response.data.lower()


def test_register_password_mismatch(client):
    """
    Attempt registration with mismatching passwords.
    """
    response = client.post(
        url_for("auth.register"),
        data={
            "email": "mismatch@isreal.ai",
            "name": "Mismatch User",
            "password": "Password123",
            "confirm_password": "Password321"
        },
        follow_redirects=True
    )
    assert response.status_code == 200
    assert b"passwords must match" in response.data.lower() or b"error" in response.data.lower()


def test_register_duplicate_email(client, session):
    """
    Attempt registration using an already registered email.
    """
    user = User(
        email="duplicate@isreal.ai",
        name="Original",
        password_hash=generate_password_hash("DupedPass123"),
        role="user",
        is_verified=True
    )
    session.add(user)
    session.commit()

    response = client.post(
        url_for("auth.register"),
        data={
            "email": "duplicate@isreal.ai",
            "name": "New User",
            "password": "DupedPass123",
            "confirm_password": "DupedPass123"
        },
        follow_redirects=True
    )
    assert response.status_code == 200
    assert b"email already registered" in response.data.lower() or b"duplicate" in response.data.lower()