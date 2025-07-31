# tests/test_routes.py

import pytest
from flask import url_for
from werkzeug.security import generate_password_hash
from app.models.user import User


@pytest.fixture
def test_user(session):
    """
    Verified user for route access testing.
    """
    user = User(
        email="routeuser@isreal.ai",
        name="Route User",
        password_hash=generate_password_hash("RoutePass789"),
        role="user",
        is_verified=True
    )
    session.add(user)
    session.commit()
    return user


def test_homepage_access(client):
    """
    Public homepage should render successfully.
    """
    response = client.get(url_for("main.home"))
    assert response.status_code == 200, "Homepage should return 200 OK"
    assert b"ISREAL.AI" in response.data or b"Welcome" in response.data


def test_signup_page_access(client):
    """
    Register page should be publicly accessible via GET.
    """
    response = client.get(url_for("auth.register"))
    assert response.status_code == 200, "Register page should return 200 OK"
    assert b"sign up" in response.data.lower() or b"register" in response.data.lower()


def test_login_page_access(client):
    """
    Login page should be accessible via GET.
    """
    response = client.get(url_for("auth.login"))
    assert response.status_code == 200, "Login page should return 200 OK"
    assert b"email" in response.data.lower() and b"password" in response.data.lower()


def test_dashboard_requires_login(client):
    """
    Unauthenticated users should be redirected to login page.
    """
    response = client.get(url_for("dashboard.home"), follow_redirects=True)
    assert response.status_code == 200, "Unauthenticated access should redirect"
    assert b"login" in response.data.lower() or b"sign in" in response.data.lower()


def test_dashboard_authenticated(client, test_user):
    """
    Authenticated user should access dashboard successfully.
    """
    with client:
        client.post(url_for("auth.login"), data={
            "email": "routeuser@isreal.ai",
            "password": "RoutePass789"
        }, follow_redirects=True)

        response = client.get(url_for("dashboard.home"))
        assert response.status_code == 200, "Authenticated dashboard access should succeed"
        assert b"dashboard" in response.data.lower()

        # Logout explicitly to isolate session
        client.get(url_for("auth.logout"), follow_redirects=True)


def test_admin_dashboard_requires_admin(client, test_user):
    """
    Non-admin user should be denied access to admin dashboard.
    """
    with client:
        client.post(url_for("auth.login"), data={
            "email": "routeuser@isreal.ai",
            "password": "RoutePass789"
        }, follow_redirects=True)

        response = client.get(url_for("admin_dashboard.admin_dashboard"), follow_redirects=True)
        assert response.status_code == 200, "Non-admin should be redirected or blocked"
        assert b"unauthorized" in response.data.lower() or b"not permitted" in response.data.lower()

        client.get(url_for("auth.logout"), follow_redirects=True)


def test_subscription_plans_requires_login(client):
    """
    Auth access required for subscription plans page.
    """
    response = client.get(url_for("subscription.view_plans"), follow_redirects=True)
    assert response.status_code == 200, "Unauthenticated access should redirect"
    assert b"login" in response.data.lower()


def test_invalid_method_on_dashboard(client):
    """
    POST request to dashboard (which should only allow GET) should be rejected.
    """
    response = client.post(url_for("dashboard.home"))
    assert response.status_code in [405, 400], "Invalid method should return 405 Method Not Allowed"


def test_404_error_page(client):
    """
    Request to unknown route should trigger 404 handler.
    """
    response = client.get("/nonexistent-page", follow_redirects=True)
    assert response.status_code == 404, "Unknown route should trigger 404"
    assert b"page not found" in response.data.lower() or b"404" in response.data