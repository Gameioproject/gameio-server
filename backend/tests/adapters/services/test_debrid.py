from typing import Any

import pytest

from adapters.services import debrid


class _FakeCache:
    def __init__(self) -> None:
        self.store: dict[str, Any] = {}

    async def get(self, key: str):
        return self.store.get(key)

    async def set(self, key: str, value: Any, ex: int | None = None) -> None:
        self.store[key] = value

    async def delete(self, key: str) -> None:
        self.store.pop(key, None)


class _FakeRealDebrid:
    """The calls a resolution makes, scripted per test."""

    instances: list["_FakeRealDebrid"] = []

    def __init__(self, client: Any) -> None:
        self.calls: list[tuple[str, Any]] = []
        self.statuses = iter(["waiting_files_selection", "downloaded"])
        _FakeRealDebrid.instances.append(self)

    async def add_magnet(self, magnet: str) -> str:
        self.calls.append(("add_magnet", magnet))
        return "RD1"

    async def info(self, torrent_id: str) -> dict[str, Any] | None:
        self.calls.append(("info", torrent_id))
        return {
            "status": next(self.statuses, "downloaded"),
            "files": [
                {"id": 1, "path": "/Redump/Sony - PlayStation 2/A (USA).zip"},
                {"id": 2, "path": "/Redump/Sony - PlayStation 2/B (USA).zip"},
            ],
            "links": ["https://real-debrid.com/d/abc"],
        }

    async def select_files(self, torrent_id: str, file_id: int) -> None:
        self.calls.append(("select_files", (torrent_id, file_id)))

    async def unrestrict(self, link: str) -> str:
        self.calls.append(("unrestrict", link))
        return "https://download.real-debrid.com/d/abc/B%20(USA).zip"


@pytest.fixture
def fake_debrid(monkeypatch):
    _FakeRealDebrid.instances.clear()
    cache = _FakeCache()
    monkeypatch.setattr(debrid, "DEBRID_API_KEY", "key")
    monkeypatch.setattr(debrid, "DEBRID_PROVIDER", "realdebrid")
    monkeypatch.setattr(debrid, "async_cache", cache)
    monkeypatch.setattr(debrid, "_RealDebrid", _FakeRealDebrid)
    monkeypatch.setattr(debrid, "READY_POLL_SECONDS", 0)
    class _Ctx:
        @staticmethod
        def get():
            return object()

    monkeypatch.setattr(debrid, "ctx_httpx_client", _Ctx)
    return cache


async def test_resolve_selects_the_one_file_and_caches_the_link(fake_debrid):
    link = await debrid.resolve_torrent_file(
        "a" * 40, "magnet:?xt=urn:btih:" + "a" * 40, "Redump/Sony - PlayStation 2/B (USA).zip"
    )
    assert link == "https://download.real-debrid.com/d/abc/B%20(USA).zip"
    calls = _FakeRealDebrid.instances[0].calls
    assert calls[0] == ("add_magnet", "magnet:?xt=urn:btih:" + "a" * 40)
    assert ("select_files", ("RD1", 2)) in calls
    assert calls[-1] == ("unrestrict", "https://real-debrid.com/d/abc")

    again = await debrid.resolve_torrent_file(
        "a" * 40, "magnet:?xt=urn:btih:" + "a" * 40, "Redump/Sony - PlayStation 2/B (USA).zip"
    )
    assert again == link
    assert len(_FakeRealDebrid.instances) == 1


async def test_resolve_without_key_is_an_error(monkeypatch):
    monkeypatch.setattr(debrid, "DEBRID_API_KEY", None)
    with pytest.raises(debrid.DebridError) as excinfo:
        await debrid.resolve_torrent_file("a" * 40, "magnet:?", "x.zip")
    assert "DEBRID_API_KEY" in str(excinfo.value)
    assert not excinfo.value.retry_later


async def test_resolve_reports_a_torrent_still_fetching(fake_debrid, monkeypatch):
    class _Slow(_FakeRealDebrid):
        def __init__(self, client: Any) -> None:
            super().__init__(client)
            self.statuses = iter([])

        async def info(self, torrent_id: str):
            payload = await super().info(torrent_id)
            assert payload is not None
            payload["status"] = "downloading"
            return payload

    monkeypatch.setattr(debrid, "_RealDebrid", _Slow)
    monkeypatch.setattr(debrid, "READY_POLL_ATTEMPTS", 2)
    with pytest.raises(debrid.DebridError) as excinfo:
        await debrid.resolve_torrent_file("b" * 40, "magnet:?", "Redump/Sony - PlayStation 2/A (USA).zip")
    assert excinfo.value.retry_later


def test_real_debrid_error_codes_are_named():
    import httpx

    too_big = httpx.Response(503, json={"error": "torrent_too_big", "error_code": 29})
    with pytest.raises(debrid.DebridError) as excinfo:
        debrid._RealDebrid._raise_for(too_big)
    assert excinfo.value.too_big and not excinfo.value.retry_later

    busy = httpx.Response(503, json={"error": "too_many_active_downloads", "error_code": 21})
    with pytest.raises(debrid.DebridError) as excinfo:
        debrid._RealDebrid._raise_for(busy)
    assert excinfo.value.retry_later and not excinfo.value.too_big
