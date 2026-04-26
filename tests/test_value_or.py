"""Tests for value_or, value_or_else, value_or_with — Task 4.

Covers:
- Option: Some + Nothing paths for value_or and value_or_else
- Either: Success + Failure paths for value_or, value_or_else, value_or_with
- Laziness: factory/mapping NOT called when value is present
- value_or_with: mapping receives the actual exception value
"""

from either_option import Either, Option, nothing, some

# ---------------------------------------------------------------------------
# Option.value_or
# ---------------------------------------------------------------------------


def test_option_value_or_some_returns_value() -> None:
    opt: Option[int] = some(42)
    assert opt.value_or(0) == 42


def test_option_value_or_nothing_returns_alternative() -> None:
    opt: Option[int] = nothing()
    assert opt.value_or(99) == 99


def test_option_value_or_some_ignores_alternative() -> None:
    assert some("hello").value_or("fallback") == "hello"


def test_option_value_or_different_types() -> None:
    """value_or widens the return type to T | U."""
    result = nothing().value_or("default")
    assert result == "default"


def test_option_value_or_with_falsy_value() -> None:
    """Some(0) is truthy in the option sense; value_or returns 0, not alternative."""
    assert some(0).value_or(99) == 0


def test_option_value_or_with_none_inner() -> None:
    """Some(None) is present; value_or returns None, not alternative."""
    assert some(None).value_or("fallback") is None


# ---------------------------------------------------------------------------
# Option.value_or_else
# ---------------------------------------------------------------------------


def test_option_value_or_else_some_returns_value() -> None:
    assert some(7).value_or_else(lambda: 99) == 7


def test_option_value_or_else_nothing_calls_factory() -> None:
    assert nothing().value_or_else(lambda: 42) == 42


def test_option_value_or_else_factory_not_called_when_some() -> None:
    factory_calls = 0

    def factory() -> int:
        nonlocal factory_calls
        factory_calls += 1
        return 99

    _ = some(1).value_or_else(factory)
    assert factory_calls == 0


def test_option_value_or_else_factory_called_exactly_once_when_nothing() -> None:
    factory_calls = 0

    def factory() -> int:
        nonlocal factory_calls
        factory_calls += 1
        return 0

    _ = nothing().value_or_else(factory)
    assert factory_calls == 1


def test_option_value_or_else_factory_result_returned() -> None:
    result = nothing().value_or_else(lambda: "from factory")
    assert result == "from factory"


# ---------------------------------------------------------------------------
# Either.value_or
# ---------------------------------------------------------------------------


def test_either_value_or_success_returns_value() -> None:
    e: Either[int, str] = Either.some(10)
    assert e.value_or(0) == 10


def test_either_value_or_failure_returns_alternative() -> None:
    e: Either[int, str] = Either.none("err")
    assert e.value_or(0) == 0


def test_either_value_or_success_ignores_alternative() -> None:
    assert Either.some("present").value_or("fallback") == "present"


def test_either_value_or_with_falsy_success_value() -> None:
    assert Either.some(0).value_or(99) == 0


# ---------------------------------------------------------------------------
# Either.value_or_else
# ---------------------------------------------------------------------------


def test_either_value_or_else_success_returns_value() -> None:
    assert Either.some(5).value_or_else(lambda: 99) == 5


def test_either_value_or_else_failure_calls_factory() -> None:
    assert Either.none("err").value_or_else(lambda: 42) == 42


def test_either_value_or_else_factory_not_called_on_success() -> None:
    factory_calls = 0

    def factory() -> int:
        nonlocal factory_calls
        factory_calls += 1
        return 99

    _ = Either.some(1).value_or_else(factory)
    assert factory_calls == 0


def test_either_value_or_else_factory_called_once_on_failure() -> None:
    factory_calls = 0

    def factory() -> int:
        nonlocal factory_calls
        factory_calls += 1
        return 0

    _ = Either.none("err").value_or_else(factory)
    assert factory_calls == 1


# ---------------------------------------------------------------------------
# Either.value_or_with — Either-only, mapping receives exception
# ---------------------------------------------------------------------------


def test_either_value_or_with_success_returns_value() -> None:
    e: Either[int, str] = Either.some(10)
    assert e.value_or_with(lambda _exc: 0) == 10


def test_either_value_or_with_failure_calls_mapping() -> None:
    e: Either[int, str] = Either.none("boom")
    assert e.value_or_with(len) == 4


def test_either_value_or_with_mapping_receives_exception() -> None:
    received: list[str] = []

    def mapping(exc: str) -> int:
        received.append(exc)
        return -1

    _ = Either.none("the-error").value_or_with(mapping)
    assert received == ["the-error"]


def test_either_value_or_with_mapping_not_called_on_success() -> None:
    mapping_calls = 0

    def mapping(_exc: str) -> int:
        nonlocal mapping_calls
        mapping_calls += 1
        return 0

    _ = Either.some(5).value_or_with(mapping)
    assert mapping_calls == 0


def test_either_value_or_with_exception_value_used_in_result() -> None:
    e: Either[int, str] = Either.none("fallback-value")
    result = e.value_or_with(lambda exc: exc.upper())
    assert result == "FALLBACK-VALUE"


# ---------------------------------------------------------------------------
# Type-widening: value_or with alternative of different type
# ---------------------------------------------------------------------------


def test_option_value_or_type_widening() -> None:
    """nothing().value_or(str) should return the str alternative."""
    result = nothing().value_or("wide")
    assert result == "wide"
    assert isinstance(result, str)


def test_either_value_or_with_returns_mapping_result() -> None:
    """value_or_with on Failure should return the mapping result."""
    result = Either.none(42).value_or_with(lambda exc: exc * 2)
    assert result == 84
