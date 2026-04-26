"""Tests for filter and not_none on Option and Either — Task 7."""

from __future__ import annotations

import pytest

from either_option import Either, Failure, Nothing, Option, Success, nothing, some

# ---------------------------------------------------------------------------
# Option.filter
# ---------------------------------------------------------------------------


def test_some_filter_passes_when_predicate_true() -> None:
    result = some(4).filter(lambda x: x % 2 == 0)
    assert result == some(4)


def test_some_filter_returns_same_object_when_true() -> None:
    opt = some(4)
    result = opt.filter(lambda x: x % 2 == 0)
    assert result is opt


def test_some_filter_returns_nothing_when_predicate_false() -> None:
    result = some(3).filter(lambda x: x % 2 == 0)
    assert result == nothing()
    assert isinstance(result, Nothing)


def test_nothing_filter_returns_nothing() -> None:
    result = nothing().filter(lambda _: True)
    assert result == nothing()


def test_nothing_filter_fn_not_called() -> None:
    called = False

    def pred(_: object) -> bool:
        nonlocal called
        called = True
        return True

    _ = nothing().filter(pred)
    assert not called


def test_some_filter_chain() -> None:
    result = some(6).filter(lambda x: x > 0).filter(lambda x: x % 2 == 0)
    assert result == some(6)


def test_some_filter_chain_second_fails() -> None:
    result = some(6).filter(lambda x: x > 0).filter(lambda x: x % 5 == 0)
    assert result == nothing()


# ---------------------------------------------------------------------------
# Option.not_none
# ---------------------------------------------------------------------------


def test_some_not_none_passes_through_non_none() -> None:
    result = some(42).not_none()
    assert result == some(42)


def test_some_not_none_returns_nothing_for_none() -> None:
    result: Option[int | None] = some(None)
    filtered = result.not_none()
    assert filtered == nothing()
    assert isinstance(filtered, Nothing)


def test_nothing_not_none_returns_nothing() -> None:
    result = nothing().not_none()
    assert result == nothing()


def test_some_not_none_same_object_for_non_none() -> None:
    opt: Option[int] = some(1)
    result = opt.not_none()
    assert result is opt


# ---------------------------------------------------------------------------
# Either.filter — Success path
# ---------------------------------------------------------------------------


def test_success_filter_passes_when_true() -> None:
    result: Either[int, str] = Success(4)
    filtered = result.filter(lambda x: x % 2 == 0, exception="odd")
    assert filtered == Success(4)


def test_success_filter_returns_failure_when_false_with_exception() -> None:
    result: Either[int, str] = Success(3)
    filtered = result.filter(lambda x: x % 2 == 0, exception="not even")
    assert filtered == Failure("not even")


def test_success_filter_returns_failure_when_false_with_exception_else() -> None:
    result: Either[int, str] = Success(3)
    filtered = result.filter(lambda x: x % 2 == 0, exception_else=lambda: "lazy err")
    assert filtered == Failure("lazy err")


def test_success_filter_exception_else_not_called_when_predicate_true() -> None:
    called = False

    def make_err() -> str:
        nonlocal called
        called = True
        return "err"

    result: Either[int, str] = Success(4)
    _ = result.filter(lambda x: x % 2 == 0, exception_else=make_err)
    assert not called


def test_success_filter_raises_when_both_provided() -> None:
    result: Either[int, str] = Success(3)
    with pytest.raises(TypeError, match=r"not both"):
        _ = result.filter(lambda x: x > 0, exception="a", exception_else=lambda: "b")


def test_success_filter_raises_when_neither_provided_and_predicate_false() -> None:
    result: Either[int, str] = Success(3)
    with pytest.raises(TypeError, match=r"requires exception"):
        _: Either[int, str] = result.filter(lambda x: x % 2 == 0)


def test_success_filter_no_error_when_neither_but_predicate_true() -> None:
    """Neither exception provided is OK if predicate passes."""
    result: Either[int, str] = Success(4)
    filtered: Either[int, str] = result.filter(lambda x: x % 2 == 0)
    assert filtered == Success(4)


# ---------------------------------------------------------------------------
# Either.filter — Failure path
# ---------------------------------------------------------------------------


def test_failure_filter_passes_through() -> None:
    f: Either[int, str] = Failure("err")
    result = f.filter(lambda x: x > 0, exception="other")
    assert result == Failure("err")


def test_failure_filter_no_exception_required() -> None:
    """Failure passes through even if neither exception/exception_else provided."""
    f: Either[int, str] = Failure("err")
    result = f.filter(lambda x: x > 0)
    assert result == Failure("err")


def test_failure_filter_predicate_not_called() -> None:
    called = False

    def pred(_: int) -> bool:
        nonlocal called
        called = True
        return True

    f: Either[int, str] = Failure("err")
    _ = f.filter(pred, exception="x")
    assert not called


# ---------------------------------------------------------------------------
# Either.not_none — Success path
# ---------------------------------------------------------------------------


def test_success_not_none_passes_through_non_none() -> None:
    result: Either[int, str] = Success(42)
    filtered = result.not_none(exception="missing")
    assert filtered == Success(42)


def test_success_not_none_returns_failure_for_none_with_exception() -> None:
    result: Either[int | None, str] = Success(None)
    filtered = result.not_none(exception="missing")
    assert filtered == Failure("missing")


def test_success_not_none_returns_failure_for_none_with_exception_else() -> None:
    result: Either[int | None, str] = Success(None)
    filtered = result.not_none(exception_else=lambda: "lazy missing")
    assert filtered == Failure("lazy missing")


def test_success_not_none_raises_when_none_and_no_exception() -> None:
    result: Either[int | None, str] = Success(None)
    with pytest.raises(TypeError, match=r"requires exception"):
        _: Either[int | None, str] = result.not_none()


def test_success_not_none_no_error_when_value_present_and_no_exception() -> None:
    result: Either[int, str] = Success(1)
    filtered: Either[int, str] = result.not_none()
    assert filtered == Success(1)


# ---------------------------------------------------------------------------
# Either.not_none — Failure path
# ---------------------------------------------------------------------------


def test_failure_not_none_passes_through() -> None:
    f: Either[int, str] = Failure("err")
    result = f.not_none(exception="missing")
    assert result == Failure("err")


def test_failure_not_none_no_exception_required() -> None:
    f: Either[int, str] = Failure("err")
    result = f.not_none()
    assert result == Failure("err")
