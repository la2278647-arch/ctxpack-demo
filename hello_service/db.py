"""Database session handling.

The engine is created lazily so importing the package never touches the
filesystem - tests can swap in an in-memory engine before the first request.
"""

from collections.abc import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from hello_service.config import get_settings


class Base(DeclarativeBase):
    pass


_engine = None
_Session = None


def get_engine():
    """Build the engine on first use. Module-level so tests can reset it."""
    global _engine, _Session
    if _engine is None:
        _engine = create_engine(get_settings().database_url, echo=False)
        _Session = sessionmaker(bind=_engine, expire_on_commit=False)
    return _engine


def reset_engine() -> None:
    """Drop the cached engine. Used by tests between cases."""
    global _engine, _Session
    if _engine is not None:
        _engine.dispose()
    _engine = None
    _Session = None


def get_session() -> Iterator[Session]:
    """Yield a session and close it, even if the request raised."""
    factory = _Session or sessionmaker(bind=get_engine())
    session = factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
