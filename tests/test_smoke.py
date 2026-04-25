"""Smoke test: package imports cleanly and the greeting is stable."""

from optional_python import hello


def test_hello_returns_greeting() -> None:
    """`hello()` returns the canonical greeting string."""
    assert hello() == "Hello from optional-python!"
