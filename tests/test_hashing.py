"""Hashing invariants — spec §5.2."""

import pytest

from optional_python import Either, nothing, some


def test_some_is_hashable() -> None:
    _ = hash(some(10))  # must not raise


def test_nothing_is_hashable() -> None:
    _ = hash(nothing())


def test_success_is_hashable() -> None:
    _ = hash(Either.some(10))


def test_failure_is_hashable() -> None:
    _ = hash(Either.none("err"))


def test_equal_implies_same_hash() -> None:
    assert hash(some(10)) == hash(some(10))
    assert hash(nothing()) == hash(nothing())
    assert hash(Either.some(10)) == hash(Either.some(10))
    assert hash(Either.none("err")) == hash(Either.none("err"))


def test_some_hash_distinct_from_nothing() -> None:
    """Tagged-tuple scheme avoids the C# Some(0) == Nothing collision."""
    assert hash(some(0)) != hash(nothing())


def test_some_hash_distinct_from_success() -> None:
    """Cross-flavour same-payload values have different tags -> different hashes."""
    assert hash(some(10)) != hash(Either.some(10))


def test_dict_key_works() -> None:
    d: dict[object, str] = {some(1): "a", nothing(): "b", Either.some(1): "c"}
    assert d[some(1)] == "a"
    assert d[nothing()] == "b"
    assert d[Either.some(1)] == "c"


def test_some_with_unhashable_inner_propagates_typeerror() -> None:
    """Spec §5.2: inner unhashable means outer unhashable, like tuple."""
    with pytest.raises(TypeError):
        _ = hash(some([1, 2, 3]))


def test_failure_with_unhashable_propagates_typeerror() -> None:
    with pytest.raises(TypeError):
        _ = hash(Either.none([1, 2, 3]))


def test_set_membership() -> None:
    s = {some(1), some(2), nothing()}
    assert some(1) in s
    assert some(3) not in s
    assert nothing() in s
