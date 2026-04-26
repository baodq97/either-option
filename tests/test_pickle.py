"""Pickle round-trip — spec §5.4."""

import pickle

from either_option import Either, Failure, Nothing, Some, Success, nothing, some


def test_some_round_trips() -> None:
    s = some(42)
    restored = pickle.loads(pickle.dumps(s))  # noqa: S301
    assert restored == s
    assert isinstance(restored, Some)


def test_some_with_string_round_trips() -> None:
    s = some("hello")
    restored = pickle.loads(pickle.dumps(s))  # noqa: S301
    assert restored == s


def test_some_with_none_round_trips() -> None:
    s = some(None)
    restored = pickle.loads(pickle.dumps(s))  # noqa: S301
    assert restored == s


def test_nothing_round_trips_to_singleton() -> None:
    """The reconstructor returns the cached Nothing instance."""
    n = nothing()
    restored = pickle.loads(pickle.dumps(n))  # noqa: S301
    assert restored is nothing()
    assert restored is Nothing()


def test_success_round_trips() -> None:
    e = Either.some(42)
    restored = pickle.loads(pickle.dumps(e))  # noqa: S301
    assert restored == e
    assert isinstance(restored, Success)


def test_failure_round_trips() -> None:
    e = Either.none("boom")
    restored = pickle.loads(pickle.dumps(e))  # noqa: S301
    assert restored == e
    assert isinstance(restored, Failure)


def test_failure_with_exception_round_trips() -> None:
    err = ValueError("bad")
    e: Either[int, ValueError] = Either.none(err)
    restored: object = pickle.loads(pickle.dumps(e))  # noqa: S301
    assert isinstance(restored, Failure)
    exc = restored.exception  # type: ignore[reportUnknownMemberType]
    assert isinstance(exc, ValueError)
    assert str(exc) == "bad"


def test_nested_some_round_trips() -> None:
    s = some(some(1))
    restored = pickle.loads(pickle.dumps(s))  # noqa: S301
    assert restored == s


def test_pickle_in_dict() -> None:
    d = {"a": some(1), "b": nothing(), "c": Either.some(2), "d": Either.none("x")}
    restored = pickle.loads(pickle.dumps(d))  # noqa: S301
    assert restored == d
    assert restored["b"] is nothing()
