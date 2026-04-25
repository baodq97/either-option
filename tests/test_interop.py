"""Tests for with_exception, with_exception_else, without_exception — Task 7."""

from __future__ import annotations

from optional_python import Either, Failure, Nothing, Option, Some, Success, nothing, some

# ---------------------------------------------------------------------------
# Option.with_exception
# ---------------------------------------------------------------------------


def test_some_with_exception_returns_success() -> None:
    result = some(42).with_exception("err")
    assert result == Success(42)
    assert isinstance(result, Success)


def test_some_with_exception_ignores_exception_arg() -> None:
    """The exception is never used when value is present."""
    result = some(99).with_exception("should not appear")
    assert result == Success(99)


def test_nothing_with_exception_returns_failure() -> None:
    result = nothing().with_exception("missing")
    assert result == Failure("missing")
    assert isinstance(result, Failure)


def test_nothing_with_exception_value_in_failure() -> None:
    result = nothing().with_exception(404)
    assert result == Failure(404)


def test_with_exception_return_type_is_either() -> None:
    result: Either[int, str] = some(1).with_exception("x")
    assert isinstance(result, Either)


# ---------------------------------------------------------------------------
# Option.with_exception_else
# ---------------------------------------------------------------------------


def test_some_with_exception_else_returns_success() -> None:
    called = False

    def factory() -> str:
        nonlocal called
        called = True
        return "err"

    result = some(42).with_exception_else(factory)
    assert result == Success(42)
    assert not called  # factory NOT called for Some


def test_nothing_with_exception_else_calls_factory_and_returns_failure() -> None:
    called = False

    def factory() -> str:
        nonlocal called
        called = True
        return "lazy err"

    result = nothing().with_exception_else(factory)
    assert result == Failure("lazy err")
    assert called


def test_with_exception_vs_with_exception_else_same_result() -> None:
    eager = nothing().with_exception("err")
    lazy = nothing().with_exception_else(lambda: "err")
    assert eager == lazy


# ---------------------------------------------------------------------------
# Either.without_exception
# ---------------------------------------------------------------------------


def test_success_without_exception_returns_some() -> None:
    result: Either[int, str] = Success(42)
    opt = result.without_exception()
    assert opt == some(42)
    assert isinstance(opt, Some)


def test_failure_without_exception_returns_nothing() -> None:
    result: Either[int, str] = Failure("err")
    opt = result.without_exception()
    assert opt == nothing()
    assert isinstance(opt, Nothing)


def test_without_exception_return_type_is_option() -> None:
    result: Either[int, str] = Success(7)
    opt: Option[int] = result.without_exception()
    assert isinstance(opt, Option)


# ---------------------------------------------------------------------------
# Round-trip: with_exception → without_exception
# ---------------------------------------------------------------------------


def test_some_round_trip_with_then_without() -> None:
    opt: Option[int] = some(5)
    either = opt.with_exception("err")
    back = either.without_exception()
    assert back == some(5)


def test_nothing_round_trip_with_then_without() -> None:
    either = nothing().with_exception("err")
    back = either.without_exception()
    assert back == nothing()


# ---------------------------------------------------------------------------
# Chain: with_exception + map + without_exception
# ---------------------------------------------------------------------------


def test_chain_with_exception_map_without() -> None:
    result = some(3).with_exception("err").map(lambda x: x * 2).without_exception()
    assert result == some(6)


def test_chain_nothing_with_exception_map_without() -> None:
    result = nothing().with_exception("no value").map(lambda x: x * 2).without_exception()
    assert result == nothing()
