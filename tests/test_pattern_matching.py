"""__match_args__ + match/case — spec §10."""

from optional_python import Either, Failure, Nothing, Option, Some, Success


def _opt(value: int | None) -> Option[int]:
    """Return Option[int] — used to avoid Some/Nothing type narrowing in tests."""
    return Some(value) if value is not None else Nothing()


def _either(value: str | None, error: str | None) -> Either[str, str]:
    """Return Either[str, str] — avoids Success/Failure narrowing in tests."""
    if value is not None:
        return Success(value)
    if error is not None:
        return Failure(error)
    msg = "must supply either value or error"
    raise ValueError(msg)


def test_match_some_binds_value() -> None:
    opt = _opt(42)
    match opt:
        case Some(value):
            assert value == 42
        case Nothing():
            msg = "expected Some branch"
            raise AssertionError(msg)
        case _:
            msg = "unreachable: Option is sealed"
            raise AssertionError(msg)


def test_match_nothing() -> None:
    opt = _opt(None)
    match opt:
        case Some(_):
            msg = "expected Nothing branch"
            raise AssertionError(msg)
        case Nothing():
            pass
        case _:
            msg = "unreachable: Option is sealed"
            raise AssertionError(msg)


def test_match_success_binds_value() -> None:
    e = _either("ok", None)
    match e:
        case Success(value):
            assert value == "ok"
        case Failure(_):
            msg = "expected Success branch"
            raise AssertionError(msg)
        case _:
            msg = "unreachable: Either is sealed"
            raise AssertionError(msg)


def test_match_failure_binds_exception() -> None:
    e = _either(None, "boom")
    match e:
        case Success(_):
            msg = "expected Failure branch"
            raise AssertionError(msg)
        case Failure(error):
            assert error == "boom"
        case _:
            msg = "unreachable: Either is sealed"
            raise AssertionError(msg)


def test_match_with_guard() -> None:
    opt = _opt(15)
    match opt:
        case Some(x) if x > 10:
            assert True
        case _:
            msg = "guard should have matched"
            raise AssertionError(msg)
