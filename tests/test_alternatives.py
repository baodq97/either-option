"""Tests for or_value, or_else, or_option, or_option_else and Either variants — Task 5.

Covers:
- Option: Some + Nothing paths for or_value, or_else, or_option, or_option_else
- Either: Success + Failure paths for or_value, or_else, or_with,
          or_option, or_option_else, or_option_with
- On Some/Success: self is returned (no allocation), factory NOT called
- On Nothing/Failure: alternative is applied
- Laziness: factory/mapping NOT called when value present
- or_with / or_option_with: mapping receives the actual exception
"""

from optional_python import Either, Nothing, Option, Some, Success, nothing, some

# ---------------------------------------------------------------------------
# Option.or_value
# ---------------------------------------------------------------------------


def test_option_or_value_some_returns_self() -> None:
    s = some(1)
    result = s.or_value(99)
    assert result is s


def test_option_or_value_nothing_returns_some_of_alternative() -> None:
    result = nothing().or_value(42)
    assert result == some(42)
    assert isinstance(result, Some)


def test_option_or_value_some_ignores_alternative() -> None:
    assert some("x").or_value("y") == some("x")


def test_option_or_value_nothing_wraps_alternative() -> None:
    result = nothing().or_value("hello")
    assert isinstance(result, Some)
    assert result == some("hello")


def test_option_or_value_with_falsy_alternative() -> None:
    result = nothing().or_value(0)
    assert result == some(0)


# ---------------------------------------------------------------------------
# Option.or_else  (lazy)
# ---------------------------------------------------------------------------


def test_option_or_else_some_returns_self() -> None:
    s = some(1)
    result = s.or_else(lambda: 99)
    assert result is s


def test_option_or_else_nothing_calls_factory() -> None:
    result = nothing().or_else(lambda: 42)
    assert result == some(42)


def test_option_or_else_factory_not_called_when_some() -> None:
    factory_calls = 0

    def factory() -> int:
        nonlocal factory_calls
        factory_calls += 1
        return 99

    _ = some(1).or_else(factory)
    assert factory_calls == 0


def test_option_or_else_factory_called_once_when_nothing() -> None:
    factory_calls = 0

    def factory() -> int:
        nonlocal factory_calls
        factory_calls += 1
        return 0

    _ = nothing().or_else(factory)
    assert factory_calls == 1


def test_option_or_else_wraps_factory_result() -> None:
    result = nothing().or_else(lambda: "generated")
    assert isinstance(result, Some)
    assert result == some("generated")


# ---------------------------------------------------------------------------
# Option.or_option
# ---------------------------------------------------------------------------


def test_option_or_option_some_returns_self() -> None:
    s = some(1)
    result = s.or_option(some(99))
    assert result is s


def test_option_or_option_nothing_returns_alternative_option() -> None:
    alt: Option[int] = some(77)
    result = nothing().or_option(alt)
    assert result is alt


def test_option_or_option_nothing_with_nothing_alternative() -> None:
    result = nothing().or_option(nothing())
    assert isinstance(result, Nothing)


def test_option_or_option_some_ignores_alternative() -> None:
    assert some(5).or_option(some(99)) == some(5)


# ---------------------------------------------------------------------------
# Option.or_option_else  (lazy)
# ---------------------------------------------------------------------------


def test_option_or_option_else_some_returns_self() -> None:
    s = some(1)
    result = s.or_option_else(lambda: some(99))
    assert result is s


def test_option_or_option_else_nothing_calls_factory() -> None:
    alt = some(55)
    result = nothing().or_option_else(lambda: alt)
    assert result is alt


def test_option_or_option_else_factory_not_called_when_some() -> None:
    factory_calls = 0

    def factory() -> Option[int]:
        nonlocal factory_calls
        factory_calls += 1
        return some(99)

    _ = some(1).or_option_else(factory)
    assert factory_calls == 0


def test_option_or_option_else_factory_called_once_when_nothing() -> None:
    factory_calls = 0

    def factory() -> Option[int]:
        nonlocal factory_calls
        factory_calls += 1
        return some(0)

    _ = nothing().or_option_else(factory)
    assert factory_calls == 1


def test_option_or_option_else_can_return_nothing() -> None:
    result = nothing().or_option_else(lambda: nothing())
    assert isinstance(result, Nothing)


# ---------------------------------------------------------------------------
# Either.or_value
# ---------------------------------------------------------------------------


def test_either_or_value_success_returns_self() -> None:
    s: Either[int, str] = Either.some(1)
    result = s.or_value(99)
    assert result is s


def test_either_or_value_failure_returns_success_of_alternative() -> None:
    result = Either.none("err").or_value(42)
    assert result == Either.some(42)
    assert isinstance(result, Success)


def test_either_or_value_success_ignores_alternative() -> None:
    assert Either.some("x").or_value("y") == Either.some("x")


# ---------------------------------------------------------------------------
# Either.or_else  (lazy)
# ---------------------------------------------------------------------------


def test_either_or_else_success_returns_self() -> None:
    s: Either[int, str] = Either.some(1)
    result = s.or_else(lambda: 99)
    assert result is s


def test_either_or_else_failure_calls_factory() -> None:
    result = Either.none("err").or_else(lambda: 42)
    assert result == Either.some(42)


def test_either_or_else_factory_not_called_on_success() -> None:
    factory_calls = 0

    def factory() -> int:
        nonlocal factory_calls
        factory_calls += 1
        return 99

    _ = Either.some(1).or_else(factory)
    assert factory_calls == 0


def test_either_or_else_factory_called_once_on_failure() -> None:
    factory_calls = 0

    def factory() -> int:
        nonlocal factory_calls
        factory_calls += 1
        return 0

    _ = Either.none("err").or_else(factory)
    assert factory_calls == 1


# ---------------------------------------------------------------------------
# Either.or_with  (failure-receiving mapping, Either-only)
# ---------------------------------------------------------------------------


def test_either_or_with_success_returns_self() -> None:
    s: Either[int, str] = Either.some(1)
    result = s.or_with(lambda _exc: 0)
    assert result is s


def test_either_or_with_failure_calls_mapping() -> None:
    result = Either.none("boom").or_with(len)
    assert result == Either.some(4)


def test_either_or_with_mapping_receives_exception() -> None:
    received: list[str] = []

    def mapping(exc: str) -> int:
        received.append(exc)
        return -1

    _ = Either.none("the-error").or_with(mapping)
    assert received == ["the-error"]


def test_either_or_with_mapping_not_called_on_success() -> None:
    mapping_calls = 0

    def mapping(_exc: str) -> int:
        nonlocal mapping_calls
        mapping_calls += 1
        return 0

    _ = Either.some(5).or_with(mapping)
    assert mapping_calls == 0


def test_either_or_with_result_wraps_in_success() -> None:
    result = Either.none("err").or_with(lambda exc: exc.upper())
    assert result == Either.some("ERR")
    assert isinstance(result, Success)


# ---------------------------------------------------------------------------
# Either.or_option
# ---------------------------------------------------------------------------


def test_either_or_option_success_returns_self() -> None:
    s: Either[int, str] = Either.some(1)
    alt: Either[int, str] = Either.some(99)
    result = s.or_option(alt)
    assert result is s


def test_either_or_option_failure_returns_alternative() -> None:
    alt: Either[int, str] = Either.some(77)
    result: Either[int, str] = Either.none("err").or_option(alt)
    assert result is alt


def test_either_or_option_failure_with_failure_alternative() -> None:
    alt: Either[int, str] = Either.none("alt-err")
    result: Either[int, str] = Either.none("orig-err").or_option(alt)
    assert result is alt


# ---------------------------------------------------------------------------
# Either.or_option_else  (lazy)
# ---------------------------------------------------------------------------


def test_either_or_option_else_success_returns_self() -> None:
    s: Either[int, str] = Either.some(1)
    result = s.or_option_else(lambda: Either.some(99))
    assert result is s


def test_either_or_option_else_failure_calls_factory() -> None:
    alt: Either[int, str] = Either.some(55)
    result: Either[int, str] = Either.none("err").or_option_else(lambda: alt)
    assert result is alt


def test_either_or_option_else_factory_not_called_on_success() -> None:
    factory_calls = 0

    def factory() -> Either[int, str]:
        nonlocal factory_calls
        factory_calls += 1
        return Either.some(99)

    e: Either[int, str] = Either.some(1)
    _ = e.or_option_else(factory)
    assert factory_calls == 0


def test_either_or_option_else_factory_called_once_on_failure() -> None:
    factory_calls = 0

    def factory() -> Either[int, str]:
        nonlocal factory_calls
        factory_calls += 1
        return Either.some(0)

    e: Either[int, str] = Either.none("err")
    _ = e.or_option_else(factory)
    assert factory_calls == 1


# ---------------------------------------------------------------------------
# Either.or_option_with  (failure-receiving, Either-only)
# ---------------------------------------------------------------------------


def test_either_or_option_with_success_returns_self() -> None:
    s: Either[int, str] = Either.some(1)
    result = s.or_option_with(lambda _exc: Either.some(0))
    assert result is s


def test_either_or_option_with_failure_calls_mapping() -> None:
    alt: Either[int, str] = Either.some(42)
    result: Either[int, str] = Either.none("err").or_option_with(lambda _exc: alt)
    assert result is alt


def test_either_or_option_with_mapping_receives_exception() -> None:
    received: list[str] = []

    def mapping(exc: str) -> Either[int, str]:
        received.append(exc)
        return Either.some(-1)

    e: Either[int, str] = Either.none("the-error")
    _ = e.or_option_with(mapping)
    assert received == ["the-error"]


def test_either_or_option_with_mapping_not_called_on_success() -> None:
    mapping_calls = 0

    def mapping(_exc: str) -> Either[int, str]:
        nonlocal mapping_calls
        mapping_calls += 1
        return Either.some(0)

    e: Either[int, str] = Either.some(5)
    _ = e.or_option_with(mapping)
    assert mapping_calls == 0


def test_either_or_option_with_can_return_failure() -> None:
    """Mapping may return a Failure — the new Failure is returned."""
    result: Either[int, str] = Either.none("orig").or_option_with(
        lambda exc: Either.none(f"remapped-{exc}")
    )
    assert result == Either.none("remapped-orig")
