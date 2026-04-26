"""Pyright snapshot tests — spec §13.5.

These tests exist to lock in typing behaviour. They run as ordinary pytest
tests (asserting True at runtime); the real value is that pyright --strict
must accept them. If pyright rejects, the build fails.
"""

from typing_extensions import assert_type

from either_option import Either, Failure, Nothing, Option, Some, Success, nothing, some


def test_some_factory_returns_some_int() -> None:
    s = some(10)
    _ = assert_type(s, Some[int])


def test_nothing_assigns_to_option_int() -> None:
    """The widening proof: nothing() is Option[Never], must flow into Option[int]."""
    opt: Option[int] = nothing()
    assert opt is nothing()


def test_failure_assigns_to_either_user_apierror() -> None:
    """Failure[Never, E] flows into Either[T, E]."""
    err: Either[int, str] = Either.none("boom")
    assert err == Either.none("boom")


def test_success_assigns_to_either_t_anyerror() -> None:
    ok: Either[int, str] = Either.some(10)
    assert ok == Either.some(10)


def test_some_value_attribute_typed() -> None:
    s = Some(10)
    _ = assert_type(s.value, int)


def test_failure_exception_attribute_typed() -> None:
    f = Failure("err")
    _ = assert_type(f.exception, str)


def _make_option_int() -> Option[int]:
    """Helper: returns an opaque Option[int] so pyright can't narrow the subject."""
    return some(10)


def _make_either_int_str() -> Either[int, str]:
    """Helper: returns an opaque Either[int, str] so pyright can't narrow the subject."""
    return Either.none("err")


def test_pattern_match_narrows_some() -> None:
    """Case Some(x) binds x as the inner type."""
    opt = _make_option_int()
    match opt:
        case Some(x):
            _ = assert_type(x, int)
        case Nothing():
            pass
        case _:
            pass


def test_pattern_match_narrows_failure() -> None:
    e = _make_either_int_str()
    match e:
        case Success(v):
            _ = assert_type(v, int)
        case Failure(err):
            _ = assert_type(err, str)
        case _:
            pass
