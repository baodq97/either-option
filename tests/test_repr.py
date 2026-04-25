"""__repr__ — spec §3.5."""

from optional_python import Either, nothing, some


def test_some_repr() -> None:
    assert repr(some(10)) == "Some(10)"


def test_some_repr_with_string() -> None:
    assert repr(some("hi")) == "Some('hi')"


def test_some_repr_with_none() -> None:
    assert repr(some(None)) == "Some(None)"


def test_nothing_repr() -> None:
    assert repr(nothing()) == "Nothing"


def test_success_repr() -> None:
    assert repr(Either.some(10)) == "Success(10)"


def test_failure_repr() -> None:
    assert repr(Either.none("err")) == "Failure('err')"
