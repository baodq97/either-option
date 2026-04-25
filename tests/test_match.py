"""Tests for match(), match_some(), match_none() — Task 3.

Covers:
- Option: Some + Nothing paths for all three methods
- Either: Success + Failure paths for all three methods
- Value-returning forms (match)
- Side-effect forms (match_some, match_none)
- Keyword-only enforcement for match()
"""

import pytest

from optional_python import Either, Failure, Nothing, Option, Some, Success, nothing, some

# ---------------------------------------------------------------------------
# Option.match — value-returning
# ---------------------------------------------------------------------------


def test_option_match_some_calls_some_branch() -> None:
    opt: Option[int] = some(42)
    result = opt.match(some=lambda v: v * 2, none=lambda: -1)
    assert result == 84


def test_option_match_nothing_calls_none_branch() -> None:
    opt: Option[int] = nothing()
    result = opt.match(some=lambda v: v * 2, none=lambda: -1)
    assert result == -1


def test_option_match_some_does_not_call_none_branch() -> None:
    called = [False]

    def none_branch() -> int:
        called[0] = True
        return -1

    _ = some(10).match(some=lambda v: v, none=none_branch)
    assert not called[0]


def test_option_match_nothing_does_not_call_some_branch() -> None:
    called = [False]

    def some_branch(v: int) -> int:
        called[0] = True
        return v

    _ = nothing().match(some=some_branch, none=lambda: 0)
    assert not called[0]


def test_option_match_returns_value_from_some() -> None:
    result: str = some(5).match(some=lambda v: f"got {v}", none=lambda: "empty")
    assert result == "got 5"


def test_option_match_returns_value_from_none() -> None:
    result: str = nothing().match(some=lambda _v: "present", none=lambda: "empty")
    assert result == "empty"


def test_option_match_keyword_only_enforcement() -> None:
    opt: Option[int] = some(1)
    with pytest.raises(TypeError):
        opt.match(lambda v: v, lambda: 0)  # type: ignore[misc]


def test_option_match_some_receives_value() -> None:
    received: list[int] = []

    def collect(v: int) -> None:
        received.append(v)

    some(99).match(some=collect, none=lambda: None)
    assert received == [99]


# ---------------------------------------------------------------------------
# Option.match_some — side-effect form
# ---------------------------------------------------------------------------


def test_option_match_some_calls_action_when_some() -> None:
    called_with: list[int] = []

    def collect(v: int) -> None:
        called_with.append(v)

    some(7).match_some(action=collect)
    assert called_with == [7]


def test_option_match_some_skips_action_when_nothing() -> None:
    called = [False]

    def action(_v: object) -> None:
        called[0] = True

    nothing().match_some(action=action)
    assert not called[0]


def test_option_match_some_nothing_instance_direct() -> None:
    """Nothing.match_some must be a no-op."""
    Nothing().match_some(action=lambda _v: pytest.fail("should not be called"))


# ---------------------------------------------------------------------------
# Option.match_none — side-effect form
# ---------------------------------------------------------------------------


def test_option_match_none_calls_action_when_nothing() -> None:
    called = [False]

    def action() -> None:
        called[0] = True

    nothing().match_none(action=action)
    assert called[0]


def test_option_match_none_skips_action_when_some() -> None:
    some(3).match_none(action=lambda: pytest.fail("should not be called"))


def test_option_match_none_some_instance_direct() -> None:
    """Some.match_none must be a no-op."""
    Some(42).match_none(action=lambda: pytest.fail("should not be called"))


# ---------------------------------------------------------------------------
# Either.match — value-returning
# ---------------------------------------------------------------------------


def test_either_match_success_calls_some_branch() -> None:
    e: Either[int, str] = Either.some(10)
    result = e.match(some=lambda v: v + 1, none=lambda _exc: -1)
    assert result == 11


def test_either_match_failure_calls_none_branch() -> None:
    e: Either[int, str] = Either.none("error")
    result = e.match(some=lambda v: v + 1, none=len)
    assert result == 5


def test_either_match_success_does_not_call_none_branch() -> None:
    called = [False]

    def none_branch(_exc: str) -> int:
        called[0] = True
        return -1

    _ = Either.some(5).match(some=lambda v: v, none=none_branch)
    assert not called[0]


def test_either_match_failure_does_not_call_some_branch() -> None:
    called = [False]

    def some_branch(v: int) -> int:
        called[0] = True
        return v

    _ = Either.none("err").match(some=some_branch, none=lambda _exc: 0)
    assert not called[0]


def test_either_match_none_branch_receives_exception() -> None:
    received: list[str] = []

    def collect(exc: str) -> None:
        received.append(exc)

    Either.none("boom").match(
        some=lambda _v: None,
        none=collect,
    )
    assert received == ["boom"]


def test_either_match_keyword_only_enforcement() -> None:
    e: Either[int, str] = Either.some(1)
    with pytest.raises(TypeError):
        e.match(lambda v: v, lambda _exc: 0)  # type: ignore[misc]


def test_either_match_returns_value_from_some() -> None:
    result: str = Either.some(3).match(some=lambda v: f"ok {v}", none=lambda exc: f"err {exc}")
    assert result == "ok 3"


def test_either_match_returns_value_from_none() -> None:
    result: str = Either.none("bad").match(some=lambda v: f"ok {v}", none=lambda exc: f"err {exc}")
    assert result == "err bad"


# ---------------------------------------------------------------------------
# Either.match_some — side-effect form
# ---------------------------------------------------------------------------


def test_either_match_some_calls_action_on_success() -> None:
    called_with: list[int] = []

    def collect(v: int) -> None:
        called_with.append(v)

    Either.some(55).match_some(action=collect)
    assert called_with == [55]


def test_either_match_some_skips_action_on_failure() -> None:
    Either.none("err").match_some(action=lambda _v: pytest.fail("should not be called"))


def test_either_match_some_failure_instance_direct() -> None:
    """Failure.match_some must be a no-op."""
    Failure("x").match_some(action=lambda _v: pytest.fail("should not be called"))


# ---------------------------------------------------------------------------
# Either.match_none — side-effect form
# ---------------------------------------------------------------------------


def test_either_match_none_calls_action_on_failure() -> None:
    received: list[str] = []

    def collect(exc: str) -> None:
        received.append(exc)

    Either.none("whoops").match_none(action=collect)
    assert received == ["whoops"]


def test_either_match_none_skips_action_on_success() -> None:
    Either.some(1).match_none(action=lambda _exc: pytest.fail("should not be called"))


def test_either_match_none_success_instance_direct() -> None:
    """Success.match_none must be a no-op."""
    Success(42).match_none(action=lambda _exc: pytest.fail("should not be called"))


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------


def test_option_match_some_with_none_inner_value() -> None:
    """Some(None) is distinct from Nothing; some branch is called."""
    received: list[object] = []

    def on_some(v: object) -> None:
        received.append(v)

    def on_none() -> None:
        received.append("NOTHING")

    some(None).match(some=on_some, none=on_none)
    assert received == [None]


def test_either_match_some_with_falsy_value() -> None:
    received: list[int] = []

    def collect(v: int) -> None:
        received.append(v)

    Either.some(0).match_some(action=collect)
    assert received == [0]
