"""
Database session management.

Uses SQLAlchemy's declarative ORM. Defaults to a local SQLite file for
development (see app/config.py); the same engine setup also works against
PostgreSQL by setting DB_ENGINE=postgres. `get_db` is the FastAPI dependency
every repository/service uses to obtain a scoped session.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import settings

_is_sqlite = settings.DATABASE_URL.startswith("sqlite")

_engine_kwargs = {"pool_pre_ping": True, "future": True}
if _is_sqlite:
    # SQLite: one file-backed connection shared across FastAPI's threaded
    # request handling; pool_size/max_overflow don't apply to its pool.
    _engine_kwargs["connect_args"] = {"check_same_thread": False}
else:
    _engine_kwargs["pool_size"] = 10
    _engine_kwargs["max_overflow"] = 20

engine = create_engine(settings.DATABASE_URL, **_engine_kwargs)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)

Base = declarative_base()


def get_db():
    """FastAPI dependency yielding a request-scoped DB session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Create all tables. Called once on application startup.

    In a real production rollout this would be replaced by Alembic
    migrations, but `create_all` is safe and idempotent for bootstrapping.
    """
    from app.models import (  # noqa: F401  (import needed to register models on Base)
        user,
        dataset,
        etl_log,
        customer,
        order,
        product,
        vendor_product,
        segmentation,
        prediction,
        ml_model,
        report,
    )

    Base.metadata.create_all(bind=engine)
