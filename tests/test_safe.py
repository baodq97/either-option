"""@safe / @safe_async / call_safe — spec §4.2."""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

import pytest

from optional_python import Either, Failure, Success
from optional_python.safe import call_safe, safe, safe_async

if TYPE_CHECKING:
    from collections.abc import Awaitable


def _run(coroutine: Awaitable[object]) -> object:
    return asyncio.run(coroutine)  # type: ignore[arg-type]


# ---- @safe sync decorator -------------------------------------------------


def test_safe_returns_success_on_normal_return() -> None:
    @safe(catch=ValueError)
    def parse_age(s: str) -> int:
        return int(s)

    result = parse_age("42")
    assert isinstance(result, Success)
    assert result == Either.some(42)


def test_safe_returns_failure_on_caught_exception() -> None:
    @safe(catch=ValueError)
    def parse_age(s: str) -> int:
        return int(s)

    result = parse_age("xx")
    assert isinstance(result, Failure)
    exc = result.exception
    assert isinstance(exc, ValueError)


def test_safe_uncaught_exception_propagates() -> None:
    @safe(catch=ValueError)
    def boom() -> int:
        raise RuntimeError

    with pytest.raises(RuntimeError):
        _ = boom()


def test_safe_default_catch_is_exception() -> None:
    @safe()
    def boom() -> int:
        msg = "oops"
        raise ValueError(msg)

    result = boom()
    assert isinstance(result, Failure)


def test_safe_does_not_swallow_keyboard_interrupt() -> None:
    @safe()
    def boom() -> int:
        raise KeyboardInterrupt

    with pytest.raises(KeyboardInterrupt):
        _ = boom()


def test_safe_tuple_catch() -> None:
    @safe(catch=(KeyError, ValueError))
    def fail(kind: str) -> int:
        if kind == "key":
            raise KeyError
        if kind == "value":
            msg = "nope"
            raise ValueError(msg)
        return 0

    assert isinstance(fail("key"), Failure)
    assert isinstance(fail("value"), Failure)
    assert isinstance(fail("ok"), Success)


def test_safe_preserves_function_metadata() -> None:
    @safe(catch=ValueError)
    def named(x: int) -> int:
        """Doc."""
        return x

    assert named.__name__ == "named"
    assert named.__doc__ == "Doc."


def test_safe_preserves_args_and_kwargs() -> None:
    @safe(catch=ValueError)
    def add(a: int, b: int = 0) -> int:
        return a + b

    assert add(1, 2) == Either.some(3)
    assert add(1, b=10) == Either.some(11)


# ---- @safe_async ---------------------------------------------------------


def test_safe_async_returns_success_on_normal_return() -> None:
    @safe_async(catch=ValueError)
    async def parse_age(s: str) -> int:
        return int(s)

    result = _run(parse_age("42"))
    assert result == Either.some(42)


def test_safe_async_returns_failure_on_caught_exception() -> None:
    @safe_async(catch=ValueError)
    async def parse_age(s: str) -> int:
        return int(s)

    result = _run(parse_age("xx"))
    assert isinstance(result, Failure)


def test_safe_async_uncaught_exception_propagates() -> None:
    @safe_async(catch=ValueError)
    async def boom() -> int:
        raise RuntimeError

    with pytest.raises(RuntimeError):
        _ = _run(boom())


def test_safe_async_default_catch_is_exception() -> None:
    @safe_async()
    async def boom() -> int:
        msg = "oops"
        raise ValueError(msg)

    result = _run(boom())
    assert isinstance(result, Failure)


def test_safe_async_preserves_function_metadata() -> None:
    @safe_async(catch=ValueError)
    async def named(x: int) -> int:
        """Doc."""
        return x

    assert named.__name__ == "named"
    assert named.__doc__ == "Doc."


# ---- call_safe one-shot ---------------------------------------------------


def test_call_safe_success_path() -> None:
    result = call_safe(int, "42")
    assert result == Either.some(42)


def test_call_safe_failure_path() -> None:
    result = call_safe(int, "xx", catch=ValueError)
    assert isinstance(result, Failure)


def test_call_safe_kwargs() -> None:
    def add(a: int, b: int) -> int:
        return a + b

    result = call_safe(add, 1, b=2)
    assert result == Either.some(3)


def test_call_safe_tuple_catch() -> None:
    def fail() -> int:
        raise KeyError

    result = call_safe(fail, catch=(KeyError, ValueError))
    assert isinstance(result, Failure)


def test_call_safe_default_catch() -> None:
    def fail() -> int:
        msg = "oops"
        raise ValueError(msg)

    result = call_safe(fail)
    assert isinstance(result, Failure)
