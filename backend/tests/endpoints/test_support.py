from unittest.mock import patch

import pytest


@pytest.mark.parametrize(
    "url",
    [
        None,
        "",
        "javascript:alert(1)",
        "http://example.org",
        "https://user:secret@example.org",
        "https://localhost/pay",
        "https://[invalid",
    ],
)
def test_unconfigured_or_unsafe_support_link_is_hidden(client, url):
    with patch("config.GAMEIO_SUPPORT_URL", url):
        response = client.get("/api/heartbeat")
    assert response.status_code == 200
    assert response.json()["FRONTEND"]["SUPPORT_URL"] is None


def test_support_link_is_public_and_does_not_require_an_account(client):
    url = "https://checkout.example.org/gameio?currency=USD"
    with patch("config.GAMEIO_SUPPORT_URL", url):
        response = client.get("/api/heartbeat")
    assert response.status_code == 200
    assert response.json()["FRONTEND"]["SUPPORT_URL"] == url
