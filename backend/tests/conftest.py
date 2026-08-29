import os
import re
from datetime import datetime, timedelta, timezone

import alembic.config
import pytest
from hypothesis import settings
from joserfc import jwt
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from config import ROMM_DB_DRIVER
from config.config_manager import ConfigManager
from handler.auth import auth_handler
from handler.auth.base_handler import ALGORITHM, oct_key
from handler.database import db_permission_handler, db_user_handler
from models.catalog import CatalogGame, CatalogGameGenre, CatalogGamePlatform
from models.client_token import ClientToken
from models.device import Device
from models.game_activity import GameAsset, GamePlaySession
from models.game_source import GameHost, GameSource
from models.user import Role, User

engine = create_engine(ConfigManager.get_db_engine(), pool_pre_ping=True)
session = sessionmaker(bind=engine, expire_on_commit=False)

settings.register_profile("ci", max_examples=200, deadline=None)
settings.register_profile("dev", max_examples=50, deadline=None)
settings.load_profile(os.getenv("HYPOTHESIS_PROFILE", "dev"))


def _ensure_database_exists() -> None:
    """Create the (possibly per-xdist-worker) test database if it's missing.

    The base `romm_test` database is provisioned by CI / local setup, but the
    per-worker databases used under pytest-xdist (`romm_test_gw0`, ...) are
    created on demand here, just before migrations run.
    """
    url = ConfigManager.get_db_engine()
    db_name = url.database
    if not db_name:
        return

    # The name is interpolated into a CREATE DATABASE statement below;
    # identifiers can't be passed as bind parameters, so validate it up-front
    # rather than rely on quoting. Test databases are always plain identifiers
    # (`romm_test`, `romm_test_gw0`, ...).
    if not re.fullmatch(r"[A-Za-z0-9_]+", db_name):
        raise ValueError(f"Refusing to create database with unsafe name: {db_name!r}")

    if ROMM_DB_DRIVER in ("mariadb", "mysql"):
        # Connect to a maintenance schema that always exists; CREATE DATABASE is
        # a server-level command regardless of the connected schema.
        admin_engine = create_engine(url.set(database="information_schema"))
        with admin_engine.begin() as conn:
            conn.execute(text(f"CREATE DATABASE IF NOT EXISTS `{db_name}`"))
        admin_engine.dispose()
    elif ROMM_DB_DRIVER == "postgresql":
        # CREATE DATABASE can't run inside a transaction.
        admin_engine = create_engine(
            url.set(database="postgres"), isolation_level="AUTOCOMMIT"
        )
        with admin_engine.connect() as conn:
            exists = conn.execute(
                text("SELECT 1 FROM pg_database WHERE datname = :name"),
                {"name": db_name},
            ).scalar()
            if not exists:
                conn.execute(text(f'CREATE DATABASE "{db_name}"'))
        admin_engine.dispose()


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    _ensure_database_exists()
    alembic.config.main(argv=["upgrade", "head"])


@pytest.fixture(autouse=True)
def clear_database():
    with session.begin() as s:
        s.query(ClientToken).delete(synchronize_session="evaluate")
        s.query(Device).delete(synchronize_session="evaluate")
        s.query(GameAsset).delete(synchronize_session="evaluate")
        s.query(GamePlaySession).delete(synchronize_session="evaluate")
        s.query(GameSource).delete(synchronize_session="evaluate")
        s.query(GameHost).delete(synchronize_session="evaluate")
        s.query(CatalogGameGenre).delete(synchronize_session="evaluate")
        s.query(CatalogGamePlatform).delete(synchronize_session="evaluate")
        s.query(CatalogGame).delete(synchronize_session="evaluate")
        s.query(User).delete(synchronize_session="evaluate")

    # Drop any cached gallery filter values to keep tests isolated.


@pytest.fixture(scope="module")
def vcr_config():
    """Fixture to configure VCR.py settings."""
    return {
        # Default `match_on`, plus raw_body.
        "match_on": ["method", "scheme", "host", "port", "path", "query", "raw_body"],
    }


@pytest.fixture
def admin_user():
    user = User(
        username="test_admin",
        hashed_password=auth_handler.get_password_hash("test_admin_password"),
        role=Role.ADMIN,
    )
    return db_user_handler.add_user(user)


@pytest.fixture
def editor_user():
    # role collapses to `user`; editor-level access now comes from the group.
    group = db_permission_handler.get_group_by_name("Editor (legacy)")
    user = User(
        username="test_editor",
        hashed_password=auth_handler.get_password_hash("test_editor_password"),
        role=Role.USER,
        permission_group_id=group.id if group else None,
    )
    return db_user_handler.add_user(user)


@pytest.fixture
def viewer_user():
    group = db_permission_handler.get_group_by_name("Viewer (legacy)")
    user = User(
        username="test_viewer",
        hashed_password=auth_handler.get_password_hash("test_viewer_password"),
        role=Role.USER,
        permission_group_id=group.id if group else None,
    )
    return db_user_handler.add_user(user)


@pytest.fixture
def expired_refresh_token(admin_user: User) -> str:
    expire = int((datetime.now(timezone.utc) + timedelta(seconds=-1)).timestamp())

    return jwt.encode(
        {"alg": ALGORITHM},
        {
            "sub": admin_user.username,
            "iss": "romm:oauth",
            "scopes": " ".join(admin_user.oauth_scopes),
            "type": "refresh",
            "jti": "expired-test-jti",
            "exp": expire,
        },
        oct_key,
    )
