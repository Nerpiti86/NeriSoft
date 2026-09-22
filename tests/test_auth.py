from starlette.requests import Request

from app.core.auth import setup_request_is_allowed


def _request_from(host: str) -> Request:
    return Request(
        {
            "type": "http",
            "asgi": {"version": "3.0"},
            "http_version": "1.1",
            "method": "GET",
            "scheme": "http",
            "path": "/setup",
            "raw_path": b"/setup",
            "query_string": b"",
            "root_path": "",
            "headers": [],
            "client": (host, 12345),
            "server": ("127.0.0.1", 8000),
        }
    )


def test_setup_is_allowed_from_ipv4_loopback() -> None:
    assert setup_request_is_allowed(_request_from("127.0.0.1"), allow_remote=False)


def test_setup_is_allowed_from_ipv6_loopback() -> None:
    assert setup_request_is_allowed(_request_from("::1"), allow_remote=False)


def test_setup_is_blocked_from_lan_by_default() -> None:
    assert not setup_request_is_allowed(_request_from("192.168.1.30"), allow_remote=False)


def test_setup_can_be_explicitly_enabled_for_lan() -> None:
    assert setup_request_is_allowed(_request_from("192.168.1.30"), allow_remote=True)
