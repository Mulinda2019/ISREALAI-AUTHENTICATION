# tests/test_forms.py

import pytest
from app.forms import RegistrationForm, LoginForm, ResetPasswordForm


def test_registration_empty_fields():
    form = RegistrationForm(data={
        "email": "",
        "name": "",
        "password": "",
        "confirm_password": ""
    })
    assert not form.validate(), "Form should reject empty fields"
    assert "This field is required." in form.email.errors
    assert "This field is required." in form.name.errors


def test_login_invalid_email_format():
    form = LoginForm(data={
        "email": "not-an-email",
        "password": "ValidPass123"
    })
    assert not form.validate(), "Login form should reject invalid email format"
    assert "Invalid email address." in form.email.errors


def test_reset_password_empty_email():
    form = ResetPasswordForm(data={
        "email": ""
    })
    assert not form.validate(), "Reset form should reject empty email"
    assert "This field is required." in form.email.errors


def test_registration_short_password():
    form = RegistrationForm(data={
        "email": "shortpass@isreal.ai",
        "name": "Shorty",
        "password": "123",
        "confirm_password": "123"
    })
    assert not form.validate(), "Password too short should be rejected"
    assert any("Too short" in msg or "Minimum" in msg for msg in form.password.errors)


def test_registration_name_field_empty():
    form = RegistrationForm(data={
        "email": "user@isreal.ai",
        "name": "",
        "password": "GoodPass123",
        "confirm_password": "GoodPass123"
    })
    assert not form.validate(), "Name field should be required"
    assert "This field is required." in form.name.errors