"""Ordering — spec §5.3."""

from __future__ import annotations

import pytest

from optional_python import Failure, Option, Success, nothing, some

# ---- Option ordering ------------------------------------------------------


def test_nothing_lt_some() -> None:
    assert nothing() < some(0)
    assert nothing() < some(-1)


def test_some_not_lt_nothing() -> None:
    assert not (some(0) < nothing())


def test_some_lt_some_via_inner() -> None:
    assert some(1) < some(2)
    assert not (some(2) < some(1))


def test_some_eq_via_inner() -> None:
    assert not (some(1) < some(1))
    assert some(1) == some(1)


def test_nothing_not_lt_nothing() -> None:
    assert not (nothing() < nothing())


def test_total_ordering_le_ge_gt_for_some() -> None:
    """total_ordering derives <=, >, >= from __lt__ + __eq__."""
    assert some(1) <= some(1)
    assert some(1) <= some(2)
    assert some(2) >= some(1)
    assert some(2) > some(1)


def test_total_ordering_for_nothing() -> None:
    assert nothing() <= nothing()
    assert nothing() <= some(0)
    assert some(0) >= nothing()
    assert some(0) > nothing()


def test_sort_options() -> None:
    items: list[Option[int]] = [some(3), nothing(), some(1), some(2)]
    items.sort(key=lambda o: (0,) if o.is_none else (1, o.value_or(0)))
    assert items == [nothing(), some(1), some(2), some(3)]


def test_sort_options_via_lt() -> None:
    """__lt__ direct compare also produces the documented ordering."""
    a: Option[int] = nothing()
    b: Option[int] = some(1)
    c: Option[int] = some(2)
    assert a < b < c
    assert not (c < a)


# ---- Either ordering ------------------------------------------------------


def test_failure_lt_success() -> None:
    assert Failure("x") < Success(0)


def test_success_not_lt_failure() -> None:
    assert not (Success(0) < Failure("x"))


def test_success_lt_success_via_inner() -> None:
    assert Success(1) < Success(2)
    assert not (Success(2) < Success(1))


def test_failure_lt_failure_via_inner() -> None:
    assert Failure("a") < Failure("b")
    assert not (Failure("b") < Failure("a"))


def test_total_ordering_for_either() -> None:
    assert Success(1) <= Success(1)
    assert Failure("a") <= Failure("a")
    assert Failure("a") <= Success(0)


# ---- Cross-flavour comparison raises -------------------------------------


def test_option_lt_either_raises() -> None:
    s = some(1)
    other: object = Success(1)
    with pytest.raises(TypeError):
        _ = s < other


def test_either_lt_option_raises() -> None:
    s = Success(1)
    other: object = some(1)
    with pytest.raises(TypeError):
        _ = s < other


def test_nothing_lt_failure_raises() -> None:
    n = nothing()
    other: object = Failure("x")
    with pytest.raises(TypeError):
        _ = n < other


# ---- Inner-not-orderable raises ------------------------------------------


def test_some_with_unorderable_inner_raises() -> None:
    with pytest.raises(TypeError):
        _ = some(object()) < some(object())


def test_failure_with_unorderable_inner_raises() -> None:
    with pytest.raises(TypeError):
        _ = Failure(object()) < Failure(object())
