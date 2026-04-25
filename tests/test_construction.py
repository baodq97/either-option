"""Construction, factories, @final, singleton identity, repr."""

import pytest

from optional_python import Either, Failure, Nothing, Option, Some, Success, nothing, some


def test_some_factory_wraps_value() -> None:
    opt = some(10)
    assert isinstance(opt, Some)
    assert opt.value == 10


def test_nothing_factory_returns_singleton() -> None:
    a = nothing()
    b = nothing()
    assert a is b
    assert isinstance(a, Nothing)


def test_nothing_direct_construction_returns_singleton() -> None:
    assert Nothing() is Nothing()
    assert Nothing() is nothing()


def test_option_some_classmethod() -> None:
    assert Option.some(5) == some(5)


def test_option_none_classmethod() -> None:
    assert Option.none() is nothing()


def test_either_some_classmethod_returns_success() -> None:
    e = Either.some(10)
    assert isinstance(e, Success)
    assert e.value == 10


def test_either_none_classmethod_returns_failure() -> None:
    e = Either.none("err")
    assert isinstance(e, Failure)
    assert e.exception == "err"


def test_some_is_final() -> None:
    """@final is a type-checker-only guard; pyright rejects this (see pyright: ignore)."""

    class _Sub(Some[int]):  # pyright: ignore[reportGeneralTypeIssues]
        pass

    # Runtime subclassing is not blocked by @final in CPython; pyright catches it instead.
    assert issubclass(_Sub, Some)


def test_nothing_is_final() -> None:
    """@final is a type-checker-only guard; pyright rejects this (see pyright: ignore)."""

    class _Sub(Nothing):  # pyright: ignore[reportGeneralTypeIssues]
        pass

    assert issubclass(_Sub, Nothing)


def test_success_is_final() -> None:
    """@final is a type-checker-only guard; pyright rejects this (see pyright: ignore)."""

    class _Sub(Success[int]):  # pyright: ignore[reportGeneralTypeIssues]
        pass

    assert issubclass(_Sub, Success)


def test_failure_is_final() -> None:
    """@final is a type-checker-only guard; pyright rejects this (see pyright: ignore)."""

    class _Sub(Failure[str]):  # pyright: ignore[reportGeneralTypeIssues]
        pass

    assert issubclass(_Sub, Failure)


def test_option_is_abstract() -> None:
    with pytest.raises(TypeError):
        _ = Option()  # pyright: ignore[reportAbstractUsage,reportUnknownVariableType]


def test_either_is_abstract() -> None:
    with pytest.raises(TypeError):
        _ = Either()  # pyright: ignore[reportAbstractUsage,reportUnknownVariableType]


def test_some_uses_slots() -> None:
    s = some(1)
    with pytest.raises(AttributeError):
        s.foo = "bar"  # pyright: ignore[reportAttributeAccessIssue]


def test_nothing_uses_slots() -> None:
    n = nothing()
    with pytest.raises(AttributeError):
        n.foo = "bar"  # pyright: ignore[reportAttributeAccessIssue]
