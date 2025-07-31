# tests/test_services.py

import pytest
from datetime import datetime, timedelta
from app.services.user.user_service import get_user_profile
from app.services.subscription.subscription_service import get_user_subscriptions, get_subscription_by_id
from app.models.user import User
from app.models.subscription import Subscription


@pytest.fixture
def sample_user(session):
    user = User(
        email="user@isreal.ai",
        name="Service Test User",
        password_hash="dummy",
        role="user",
        is_verified=True
    )
    session.add(user)
    session.commit()
    yield user
    session.delete(user)
    session.commit()


@pytest.fixture
def sample_subscriptions(session, sample_user):
    now = datetime.utcnow()
    sub1 = Subscription(
        user_id=sample_user.id,
        plan_name="Pro",
        status="active",
        renewal_date=now + timedelta(days=30),
        created_at=now
    )
    sub2 = Subscription(
        user_id=sample_user.id,
        plan_name="Basic",
        status="expired",
        renewal_date=now - timedelta(days=5),
        created_at=now - timedelta(days=60)
    )
    session.add_all([sub1, sub2])
    session.commit()
    yield [sub1, sub2]
    for sub in [sub1, sub2]:
        session.delete(sub)
    session.commit()


def test_get_user_profile_success(sample_user):
    user = get_user_profile(sample_user.id)
    assert user is not None
    assert user.email == "user@isreal.ai"
    assert user.is_verified is True


def test_get_user_profile_not_found():
    user = get_user_profile(99999)
    assert user is None


def test_get_user_subscriptions(sample_subscriptions, sample_user):
    subs = get_user_subscriptions(sample_user.id)
    assert isinstance(subs, list)
    assert len(subs) == 2
    assert any(sub.plan_name == "Pro" for sub in subs)

    # Check date deltas
    for sub in subs:
        assert abs((datetime.utcnow() - sub.created_at).days) < 70


def test_get_subscription_by_id_success(sample_subscriptions):
    target_id = sample_subscriptions[0].id
    sub = get_subscription_by_id(target_id)
    assert sub is not None
    assert sub.plan_name == "Pro"
    assert sub.status == "active"

    # Date assertions
    assert sub.renewal_date > datetime.utcnow()


def test_get_subscription_by_id_failure():
    sub = get_subscription_by_id(999999)
    assert sub is None