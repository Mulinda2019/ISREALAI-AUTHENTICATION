import os
from app import create_app, db
from flask_migrate import upgrade
import logging

app = create_app()

def ensure_database():
    """Create database and run migrations if needed."""
    database_uri = app.config.get("SQLALCHEMY_DATABASE_URI", "")
    if database_uri.startswith("sqlite:///"):
        db_path = database_uri.replace("sqlite:///", "")
        if not os.path.exists(db_path):
            logging.info(f"Database not found at {db_path}, creating new database...")
            # Create tables directly (only if not using migrations)
            with app.app_context():
                db.create_all()
                logging.info("Database tables created.")
            # If you use Alembic migrations, run them instead:
            # with app.app_context():
            #     upgrade()
        else:
            logging.info(f"Database found at {db_path}.")
    else:
        # For other DBs, just run migrations
        logging.info("Running migrations for non-sqlite database...")
        with app.app_context():
            upgrade()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    ensure_database()
    app.run(host="0.0.0.0", port=5000, debug=True)
