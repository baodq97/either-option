"""Tests for either_option.unsafe — Task 11.

Covers:
- value_or_failure on Some/Success → returns inner value.
- value_or_failure on Nothing/Failure → raises OptionValueMissingError.
- Custom message and message_factory variants.
- Exception chaining when Failure payload is an Exception.
- value_or_default on all four variants → inner or None.
- to_optional on Some/Nothing → inner or None.
- Mutual-exclusion guard: message + message_factory → TypeError.
"""

import pytest

from either_option import Failure, Nothing, Option, Some, Success
from either_option.unsafe import (
    OptionValueMissingError,
    to_optional,
    value_or_default,
    value_or_failure,
)

# ---------------------------------------------------------------------------
# value_or_failure — Option branch
# ---------------------------------------------------------------------------


def test_value_or_failure_some_returns_value() -> None:
    assert value_or_failure(Some(42)) == 42


def test_value_or_failure_some_string_returns_value() -> None:
    assert value_or_failure(Some("hello")) == "hello"


def test_value_or_failure_some_with_message_returns_value() -> None:
    assert value_or_failure(Some(7), message="unused") == 7


def test_value_or_failure_nothing_raises_default_message() -> None:
    with pytest.raises(OptionValueMissingError, match=r"Option has no value\."):
        value_or_failure(Nothing())


def test_value_or_failure_nothing_raises_custom_message() -> None:
    with pytest.raises(OptionValueMissingError, match="custom error"):
        value_or_failure(Nothing(), message="custom error")


def test_value_or_failure_nothing_no_message_none_default() -> None:
    """Passing message=None explicitly still uses the default."""
    with pytest.raises(OptionValueMissingError, match=r"Option has no value\."):
        value_or_failure(Nothing(), message=None)


# ---------------------------------------------------------------------------
# value_or_failure — Either branch, message only
# ---------------------------------------------------------------------------


def test_value_or_failure_success_returns_value() -> None:
    assert value_or_failure(Success(99)) == 99


def test_value_or_failure_success_with_message_returns_value() -> None:
    assert value_or_failure(Success("ok"), message="ignored") == "ok"


def test_value_or_failure_failure_raises_default_message() -> None:
    with pytest.raises(OptionValueMissingError, match=r"Either has no value\."):
        value_or_failure(Failure("err"))


def test_value_or_failure_failure_raises_custom_message() -> None:
    with pytest.raises(OptionValueMissingError, match="specific error"):
        value_or_failure(Failure("err"), message="specific error")


# ---------------------------------------------------------------------------
# value_or_failure — Either branch, exception chaining
# ---------------------------------------------------------------------------


def test_value_or_failure_failure_exception_payload_chains_cause() -> None:
    """If the Failure payload is an Exception, __cause__ must be set."""
    inner = ValueError("root cause")
    with pytest.raises(OptionValueMissingError) as exc_info:
        value_or_failure(Failure(inner))
    assert exc_info.value.__cause__ is inner


def test_value_or_failure_failure_non_exception_payload_no_chain() -> None:
    """Non-Exception payload (e.g. str) should not be set as __cause__."""
    with pytest.raises(OptionValueMissingError) as exc_info:
        value_or_failure(Failure("not-an-exception"))
    assert exc_info.value.__cause__ is None


def test_value_or_failure_failure_custom_message_exception_chains() -> None:
    inner = RuntimeError("boom")
    with pytest.raises(OptionValueMissingError, match="oops") as exc_info:
        value_or_failure(Failure(inner), message="oops")
    assert exc_info.value.__cause__ is inner


# ---------------------------------------------------------------------------
# value_or_failure — Either branch, message_factory
# ---------------------------------------------------------------------------


def test_value_or_failure_success_message_factory_returns_value() -> None:
    assert value_or_failure(Success(1), message_factory=lambda e: f"err: {e}") == 1


def test_value_or_failure_failure_message_factory_called_with_exception() -> None:
    inner = KeyError("missing")
    received: list[object] = []

    def factory(e: object) -> str:
        received.append(e)
        return f"got: {e!r}"

    with pytest.raises(OptionValueMissingError, match="got:") as exc_info:
        value_or_failure(Failure(inner), message_factory=factory)

    assert received == [inner]
    # factory-produced message
    assert "got:" in str(exc_info.value)
    # Exception payload → chained
    assert exc_info.value.__cause__ is inner


def test_value_or_failure_failure_message_factory_non_exception_no_chain() -> None:
    with pytest.raises(OptionValueMissingError) as exc_info:
        value_or_failure(Failure(42), message_factory=lambda e: f"val={e}")
    assert exc_info.value.__cause__ is None


# ---------------------------------------------------------------------------
# Mutual exclusion guard
# ---------------------------------------------------------------------------


def test_value_or_failure_message_and_factory_raises_type_error() -> None:
    with pytest.raises(TypeError, match="mutually exclusive"):
        value_or_failure(  # type: ignore[call-overload]
            Failure("x"),
            message="oops",
            message_factory=lambda _e: "also oops",  # type: ignore[reportUnknownLambdaType]
        )


# ---------------------------------------------------------------------------
# value_or_default
# ---------------------------------------------------------------------------


def test_value_or_default_some_returns_value() -> None:
    assert value_or_default(Some(5)) == 5


def test_value_or_default_nothing_returns_none() -> None:
    assert value_or_default(Nothing()) is None


def test_value_or_default_success_returns_value() -> None:
    assert value_or_default(Success("x")) == "x"


def test_value_or_default_failure_returns_none() -> None:
    assert value_or_default(Failure(RuntimeError("bad"))) is None


def test_value_or_default_none_value_returns_none() -> None:
    """Some(None) → returns None (the inner value)."""
    opt: Option[None] = Some(None)
    assert value_or_default(opt) is None


# ---------------------------------------------------------------------------
# to_optional
# ---------------------------------------------------------------------------


def test_to_optional_some_returns_value() -> None:
    assert to_optional(Some(10)) == 10


def test_to_optional_nothing_returns_none() -> None:
    assert to_optional(Nothing()) is None


def test_to_optional_some_none_value_returns_none() -> None:
    """to_optional(Some(None)) → None (inner value, not absence)."""
    opt: Option[None] = Some(None)
    assert to_optional(opt) is None


# ---------------------------------------------------------------------------
# OptionValueMissingError re-exported from top-level package
# ---------------------------------------------------------------------------


def test_option_value_missing_error_importable_from_package() -> None:
    from either_option import OptionValueMissingError as E  # noqa: PLC0415

    assert E is OptionValueMissingError


def test_option_value_missing_error_in_all() -> None:
    import either_option  # noqa: PLC0415

    assert "OptionValueMissingError" in either_option.__all__
