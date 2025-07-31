# tests/conftest.py

import pytest
from app import create_app
from app.extensions import db as _db
from flask import template_rendered
from contextlib import contextmanager


@pytest.fixture(scope="session")
def app():
    """
    Create a Flask test application for the entire test session.
    Uses the 'testing' config mode defined in your configuration files.
    """
    test_app = create_app(config_name="testing")
    with test_app.app_context():
        yield test_app


@pytest.fixture(scope="session")
def db(app):
    """
    Provide a clean database instance for the test session.
    Drops and recreates all tables.
    """
    _db.app = app
    _db.drop_all()
    _db.create_all()
    yield _db
    _db.session.remove()
    _db.drop_all()


@pytest.fixture(scope="function")
def session(db):
    """
    Provide a fresh SQLAlchemy session for each test.
    Rolls back any changes to maintain test isolation.
    """
    connection = db.engine.connect()
    transaction = connection.begin()

    options = dict(bind=connection, binds={})
    session = db.create_scoped_session(options=options)

    db.session = session

    yield session

    transaction.rollback()
    connection.close()
    session.remove()


@pytest.fixture(scope="function")
def client(app):
    """
    Provide a Flask test client for making requests.
    """
    return app.test_client()


@pytest.fixture
def captured_templates(app):
    """
    Capture rendered templates and context during tests.
    Useful for testing view logic and data passed to templates.
    """
    recorded = []

    @contextmanager
    def capture():
        def record(sender, template, context, **extra):
            recorded.append((template, context))

        template_rendered.connect(record, app)
        try:
            yield recorded
        finally:
            template_rendered.disconnect(record, app)

    return capture()