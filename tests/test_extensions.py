"""Tests for optional_python.extensions — Task 9."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from collections.abc import Callable

from optional_python import Either, Failure, Nothing, Option, Some, Success
from optional_python.extensions import (
    from_optional,
    none_when,
    some_not_none,
    some_when,
)

# ---------------------------------------------------------------------------
# some_not_none — Option form
# ---------------------------------------------------------------------------


def test_some_not_none_with_none_returns_nothing() -> None:
    result: Option[str] = some_not_none(None)
    assert isinstance(result, Nothing)


def test_some_not_none_with_zero_returns_some() -> None:
    result = some_not_none(0)
    assert isinstance(result, Some)
    assert result.value == 0


def test_some_not_none_with_string_returns_some() -> None:
    result = some_not_none("x")
    assert isinstance(result, Some)
    assert result.value == "x"


def test_some_not_none_with_false_returns_some() -> None:
    # False is not None — should be wrapped.
    # Assign to typed variable first to avoid FBT003 (boolean positional arg lint).
    falsy_val: bool = False
    result = some_not_none(falsy_val)
    assert isinstance(result, Some)
    assert result.value is False


def test_some_not_none_with_empty_string_returns_some() -> None:
    result = some_not_none("")
    assert isinstance(result, Some)
    assert result.value == ""


# ---------------------------------------------------------------------------
# some_not_none — Either form (exception=)
# ---------------------------------------------------------------------------


def test_some_not_none_exception_present_returns_success() -> None:
    err = ValueError("missing")
    result = some_not_none("hello", exception=err)
    assert isinstance(result, Success)
    assert result.value == "hello"


def test_some_not_none_exception_absent_returns_failure() -> None:
    err = ValueError("missing")
    result: Either[str, ValueError] = some_not_none(None, exception=err)
    assert isinstance(result, Failure)
    assert result.exception is err


def test_some_not_none_exception_zero_returns_success() -> None:
    result = some_not_none(0, exception=RuntimeError("bad"))
    assert isinstance(result, Success)
    assert result.value == 0


# ---------------------------------------------------------------------------
# some_not_none — Either form (exception_else=)
# ---------------------------------------------------------------------------


def test_some_not_none_exception_else_present_returns_success() -> None:
    calls: list[int] = []

    def factory() -> ValueError:
        calls.append(1)
        return ValueError("missing")

    result = some_not_none("hello", exception_else=factory)
    assert isinstance(result, Success)
    assert result.value == "hello"
    # Factory must NOT be called on the present-value path.
    assert len(calls) == 0


def test_some_not_none_exception_else_absent_returns_failure() -> None:
    calls: list[int] = []

    def factory() -> ValueError:
        calls.append(1)
        return ValueError("missing")

    result: Either[str, ValueError] = some_not_none(None, exception_else=factory)
    assert isinstance(result, Failure)
    assert isinstance(result.exception, ValueError)
    assert len(calls) == 1


def test_some_not_none_exception_else_lazy() -> None:
    """Factory is called exactly once only on the absent path."""
    calls: list[str] = []

    def factory() -> str:
        calls.append("called")
        return "error"

    _present = some_not_none("present", exception_else=factory)
    assert calls == []

    _absent: Either[str, str] = some_not_none(None, exception_else=factory)
    assert calls == ["called"]


# ---------------------------------------------------------------------------
# some_not_none — mutual exclusion of kwargs
# ---------------------------------------------------------------------------


def test_some_not_none_both_kwargs_raises() -> None:
    with pytest.raises(TypeError):
        _ = some_not_none(  # pyright: ignore[reportCallIssue,reportUnknownVariableType]
            "x",
            exception=ValueError("a"),
            exception_else=lambda: ValueError("b"),
        )


# ---------------------------------------------------------------------------
# some_when — Option form
# ---------------------------------------------------------------------------


def test_some_when_true_predicate_returns_some() -> None:
    result = some_when(10, lambda v: v > 5)
    assert isinstance(result, Some)
    assert result.value == 10


def test_some_when_false_predicate_returns_nothing() -> None:
    result = some_when(3, lambda v: v > 5)
    assert isinstance(result, Nothing)


def test_some_when_truthy_non_bool_predicate() -> None:
    # Predicate returns a truthy int, not a bool — should still produce Some.
    # len("abc") = 3 (truthy).
    pred: Callable[[str], bool] = len  # type: ignore[assignment]  # intentional: len returns int
    result = some_when("abc", pred)
    assert isinstance(result, Some)


def test_some_when_falsy_non_bool_predicate() -> None:
    # Predicate returns 0 (falsy int), not False — should produce Nothing.
    # len("") = 0 (falsy).
    pred: Callable[[str], bool] = len  # type: ignore[assignment]  # intentional: len returns int
    result = some_when("", pred)
    assert isinstance(result, Nothing)


def test_some_when_predicate_raises_propagates() -> None:
    def bad_predicate(_: int) -> bool:
        msg = "oops"
        raise RuntimeError(msg)

    with pytest.raises(RuntimeError, match="oops"):
        _ = some_when(42, bad_predicate)


# ---------------------------------------------------------------------------
# some_when — Either form (exception=)
# ---------------------------------------------------------------------------


def test_some_when_exception_true_returns_success() -> None:
    result = some_when(10, lambda v: v > 5, exception=ValueError("low"))
    assert isinstance(result, Success)
    assert result.value == 10


def test_some_when_exception_false_returns_failure() -> None:
    err = ValueError("low")
    result = some_when(3, lambda v: v > 5, exception=err)
    assert isinstance(result, Failure)
    assert result.exception is err


# ---------------------------------------------------------------------------
# some_when — Either form (exception_else=)
# ---------------------------------------------------------------------------


def test_some_when_exception_else_true_factory_not_called() -> None:
    calls: list[int] = []

    def factory() -> str:
        calls.append(1)
        return "err"

    result = some_when(10, lambda v: v > 5, exception_else=factory)
    assert isinstance(result, Success)
    assert len(calls) == 0


def test_some_when_exception_else_false_factory_called() -> None:
    result = some_when(3, lambda v: v > 5, exception_else=lambda: "too low")
    assert isinstance(result, Failure)
    assert result.exception == "too low"


def test_some_when_both_kwargs_raises() -> None:
    with pytest.raises(TypeError):
        _ = some_when(  # pyright: ignore[reportCallIssue,reportUnknownVariableType]
            10,
            lambda v: v > 5,  # pyright: ignore[reportUnknownLambdaType]
            exception=ValueError("a"),
            exception_else=lambda: ValueError("b"),
        )


# ---------------------------------------------------------------------------
# none_when — Option form
# ---------------------------------------------------------------------------


def test_none_when_true_predicate_returns_nothing() -> None:
    result = none_when(10, lambda v: v > 5)
    assert isinstance(result, Nothing)


def test_none_when_false_predicate_returns_some() -> None:
    result = none_when(3, lambda v: v > 5)
    assert isinstance(result, Some)
    assert result.value == 3


def test_none_when_truthy_non_bool_predicate_returns_nothing() -> None:
    # len("abc") = 3 (truthy) → none_when returns Nothing.
    pred: Callable[[str], bool] = len  # type: ignore[assignment]  # intentional: len returns int
    result = none_when("abc", pred)
    assert isinstance(result, Nothing)


def test_none_when_falsy_non_bool_predicate_returns_some() -> None:
    # len("") = 0 (falsy) → none_when returns Some.
    pred: Callable[[str], bool] = len  # type: ignore[assignment]  # intentional: len returns int
    result = none_when("", pred)
    assert isinstance(result, Some)


def test_none_when_predicate_raises_propagates() -> None:
    def bad_predicate(_: int) -> bool:
        msg = "oops"
        raise RuntimeError(msg)

    with pytest.raises(RuntimeError, match="oops"):
        _ = none_when(42, bad_predicate)


# ---------------------------------------------------------------------------
# none_when — Either form (exception=)
# ---------------------------------------------------------------------------


def test_none_when_exception_false_predicate_returns_success() -> None:
    # predicate false → some(value) → Success(value)
    result = none_when(3, lambda v: v > 5, exception=ValueError("not allowed"))
    assert isinstance(result, Success)
    assert result.value == 3


def test_none_when_exception_true_predicate_returns_failure() -> None:
    err = ValueError("not allowed")
    result = none_when(10, lambda v: v > 5, exception=err)
    assert isinstance(result, Failure)
    assert result.exception is err


# ---------------------------------------------------------------------------
# none_when — Either form (exception_else=)
# ---------------------------------------------------------------------------


def test_none_when_exception_else_false_predicate_factory_not_called() -> None:
    calls: list[int] = []

    def factory() -> str:
        calls.append(1)
        return "err"

    result = none_when(3, lambda v: v > 5, exception_else=factory)
    assert isinstance(result, Success)
    assert len(calls) == 0


def test_none_when_exception_else_true_predicate_factory_called() -> None:
    result = none_when(10, lambda v: v > 5, exception_else=lambda: "too high")
    assert isinstance(result, Failure)
    assert result.exception == "too high"


def test_none_when_both_kwargs_raises() -> None:
    with pytest.raises(TypeError):
        _ = none_when(  # pyright: ignore[reportCallIssue,reportUnknownVariableType]
            10,
            lambda v: v > 5,  # pyright: ignore[reportUnknownLambdaType]
            exception=ValueError("a"),
            exception_else=lambda: ValueError("b"),
        )


# ---------------------------------------------------------------------------
# from_optional
# ---------------------------------------------------------------------------


def test_from_optional_none_returns_nothing() -> None:
    result: Option[str] = from_optional(None)
    assert isinstance(result, Nothing)


def test_from_optional_value_returns_some() -> None:
    result = from_optional("hello")
    assert isinstance(result, Some)
    assert result.value == "hello"


def test_from_optional_zero_returns_some() -> None:
    result = from_optional(0)
    assert isinstance(result, Some)
    assert result.value == 0


def test_from_optional_false_returns_some() -> None:
    # Assign to typed variable first to avoid FBT003 (boolean positional arg lint).
    falsy_val: bool = False
    result = from_optional(falsy_val)
    assert isinstance(result, Some)
    assert result.value is False


def test_from_optional_returns_option_type() -> None:
    """from_optional always returns Option, never Either."""
    result: Option[str] = from_optional("abc")
    assert isinstance(result, Option)


# ---------------------------------------------------------------------------
# Type-level sanity: verify return types are from the right branch
# ---------------------------------------------------------------------------


def test_some_not_none_option_form_returns_option_instance() -> None:
    result: Option[int] = some_not_none(42)
    assert isinstance(result, Option)


def test_some_when_option_form_returns_option_instance() -> None:
    result: Option[int] = some_when(42, lambda v: v > 0)
    assert isinstance(result, Option)


def test_none_when_option_form_returns_option_instance() -> None:
    result: Option[int] = none_when(42, lambda v: v < 0)
    assert isinstance(result, Option)


def test_some_not_none_either_form_returns_either_instance() -> None:
    result: Either[int, str] = some_not_none(42, exception="err")
    assert isinstance(result, Either)


def test_some_when_either_form_returns_either_instance() -> None:
    result: Either[int, str] = some_when(42, lambda v: v > 0, exception="err")
    assert isinstance(result, Either)


def test_none_when_either_form_returns_either_instance() -> None:
    result: Either[int, str] = none_when(42, lambda v: v < 0, exception="err")
    assert isinstance(result, Either)


# ---------------------------------------------------------------------------
# Import completeness smoke test
# ---------------------------------------------------------------------------


def test_public_names_importable() -> None:
    """All four helpers are importable from optional_python.extensions."""
    # Verify module-level imports at the top of this file resolve the right names.
    assert callable(some_not_none)
    assert callable(some_when)
    assert callable(none_when)
    assert callable(from_optional)


# ---------------------------------------------------------------------------
# Additional edge cases
# ---------------------------------------------------------------------------


def test_some_not_none_with_list_returns_some() -> None:
    result = some_not_none([1, 2, 3])
    assert isinstance(result, Some)
    assert result.value == [1, 2, 3]


def test_some_when_with_identity_predicate() -> None:
    # identity predicate: truthy non-None values → Some, falsy → Nothing
    assert isinstance(some_when("non-empty", bool), Some)
    assert isinstance(some_when("", bool), Nothing)


def test_none_when_symmetric_with_some_when() -> None:
    """none_when(v, p) is Nothing when some_when(v, p) is Some."""

    def gt10(x: int) -> bool:
        return x > 10

    v = 42
    sw = some_when(v, gt10)
    nw = none_when(v, gt10)
    # gt10(42) is True → some_when returns Some, none_when returns Nothing
    assert isinstance(sw, Some)
    assert isinstance(nw, Nothing)


def test_none_when_symmetric_false_pred() -> None:
    def gt10(x: int) -> bool:
        return x > 10

    v = 2
    sw = some_when(v, gt10)
    nw = none_when(v, gt10)
    assert isinstance(sw, Nothing)
    assert isinstance(nw, Some)


def test_some_not_none_exception_else_none_value_factory_called_once() -> None:
    """Factory called exactly once per invocation — not repeatedly."""
    calls: list[int] = []

    def factory() -> str:
        calls.append(1)
        return "err"

    _a: Either[str, str] = some_not_none(None, exception_else=factory)
    _b: Either[str, str] = some_not_none(None, exception_else=factory)
    assert calls == [1, 1]
