"""Equality semantics — spec §5.1."""

from either_option import Either, Failure, Nothing, Some, nothing, some


def test_some_equal_when_inner_equal() -> None:
    assert some(10) == some(10)


def test_some_unequal_when_inner_unequal() -> None:
    assert some(10) != some(11)


def test_nothing_always_equal_to_nothing() -> None:
    assert nothing() == nothing()
    assert Nothing() == Nothing()


def test_some_unequal_to_nothing() -> None:
    assert some(10) != nothing()
    assert nothing() != some(10)


def test_some_with_none_inner_equal() -> None:
    assert some(None) == some(None)


def test_some_none_inner_unequal_to_nothing() -> None:
    assert some(None) != nothing()


def test_success_equal_when_inner_equal() -> None:
    assert Either.some(10) == Either.some(10)


def test_failure_equal_when_exception_equal() -> None:
    assert Either.none("err") == Either.none("err")


def test_success_unequal_to_failure() -> None:
    assert Either.some(10) != Either.none("err")


def test_cross_flavour_unequal() -> None:
    """Option.some(1) != Either.some(1) — different types."""
    assert some(1) != Either.some(1)
    assert nothing() != Either.none("err")


def test_cross_type_unequal() -> None:
    assert some(1) != 1
    assert some(1) != "some(1)"
    assert nothing() != None  # noqa: E711


def test_subclass_eq_consistent() -> None:
    """Some.__eq__ uses isinstance check, so equality is reflexive within the family."""
    s: Some[int] = Some(5)
    assert s == Some(5)
    assert s != Failure("x")
