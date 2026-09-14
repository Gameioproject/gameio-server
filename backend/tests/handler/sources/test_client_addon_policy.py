from unittest.mock import Mock

import pytest

import config
from handler.database import db_game_source_handler
from handler.sources.policy import SourceHandlingDisabled, server_sources_enabled
from models.game_source import GameHostKind


@pytest.mark.parametrize(
    "method,args,kwargs",
    [
        (
            "add_host",
            (),
            {"name": "test", "kind": GameHostKind.HTTP, "base": "https://example.org"},
        ),
        ("update_host", (1,), {"name": "test"}),
        ("delete_host", (1,), {}),
        ("mark_index_started", (1,), {}),
        ("mark_index_finished", (1, None), {}),
        ("upsert_sources", (1, []), {}),
        ("delete_source", (1,), {}),
        ("delete_sources_of_host", (1,), {}),
    ],
)
def test_cutover_rejects_source_database_mutations_before_access(
    monkeypatch, method, args, kwargs
):
    monkeypatch.setattr(config, "GAMEIO_CLIENT_ADDONS_ONLY", True)
    session = Mock()
    with pytest.raises(SourceHandlingDisabled):
        getattr(db_game_source_handler, method)(*args, **kwargs, session=session)
    assert session.mock_calls == []


def test_private_migration_reads_remain_available(monkeypatch):
    monkeypatch.setattr(config, "GAMEIO_CLIENT_ADDONS_ONLY", True)
    session = Mock()
    marker = object()
    session.get.return_value = marker
    assert db_game_source_handler.get_host(1, session=session) is marker
    assert session.get.call_count == 1


@pytest.mark.parametrize("flag", [False, True])
def test_rollout_policy_uses_explicit_configuration(monkeypatch, flag):
    monkeypatch.setattr(config, "GAMEIO_CLIENT_ADDONS_ONLY", flag)
    assert server_sources_enabled() is not flag
