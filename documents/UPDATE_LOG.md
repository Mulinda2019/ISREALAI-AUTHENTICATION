# Update Log

## Overview
- Added missing Python dependencies and ensured the SQLite database directory is created automatically.
- Simplified form classes (login, registration, reset password) and exposed them via `app.forms`.
- Fixed circular model relationships and aligned `User` fields with test expectations.
- Added minimal HTML templates for core routes and improved safe template rendering.
- Introduced test configuration and helper decorators to stabilize route handling.

## Testing
- `PYTHONPATH=. pytest` *(fails: UndefinedError for LoginForm.csrf_token, ResourceClosedError in services, and keyword errors in models)*
- `python run.py` starts the development server at `http://127.0.0.1:5000`.

