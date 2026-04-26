"""Tests for map, flat_map, map_failure, tap, tap_failure, flatten — Task 6."""

from __future__ import annotations

import either_option
from either_option import Either, Failure, Nothing, Option, Success, flatten, nothing, some

# ---------------------------------------------------------------------------
# Option.map
# ---------------------------------------------------------------------------


def test_some_map_applies_function() -> None:
    result = some(3).map(lambda x: x * 2)
    assert result == some(6)


def test_some_map_returns_option() -> None:
    result: Option[str] = some(42).map(str)
    assert result == some("42")


def test_some_map_identity() -> None:
    result = some(10).map(lambda x: x)
    assert result == some(10)


def test_some_map_chain() -> None:
    result = some(1).map(lambda x: x + 1).map(lambda x: x * 3)
    assert result == some(6)


def test_nothing_map_returns_nothing() -> None:
    result = nothing().map(lambda x: x * 2)
    assert result == nothing()
    assert isinstance(result, Nothing)


def test_nothing_map_fn_not_called() -> None:
    called = False

    def fn(x: object) -> object:
        nonlocal called
        called = True
        return x

    _ = nothing().map(fn)
    assert not called


# ---------------------------------------------------------------------------
# Option.flat_map
# ---------------------------------------------------------------------------


def test_some_flat_map_applies_function() -> None:
    result = some(3).flat_map(lambda x: some(x * 2))
    assert result == some(6)


def test_some_flat_map_can_return_nothing() -> None:
    result = some(3).flat_map(lambda _: nothing())
    assert result == nothing()


def test_some_flat_map_chain() -> None:
    result = some(1).flat_map(lambda x: some(x + 1)).flat_map(lambda x: some(x * 3))
    assert result == some(6)


def test_nothing_flat_map_returns_nothing() -> None:
    result = nothing().flat_map(lambda x: some(x))
    assert result == nothing()


def test_nothing_flat_map_fn_not_called() -> None:
    called = False

    def fn(x: object) -> Option[object]:
        nonlocal called
        called = True
        return some(x)

    _ = nothing().flat_map(fn)
    assert not called


# ---------------------------------------------------------------------------
# Option.tap
# ---------------------------------------------------------------------------


def test_some_tap_calls_fn_with_value() -> None:
    captured: list[int] = []
    result = some(42).tap(captured.append)
    assert captured == [42]
    assert result == some(42)


def test_some_tap_returns_same_object() -> None:
    opt = some(1)
    returned = opt.tap(lambda _: None)
    assert returned is opt


def test_nothing_tap_fn_not_called() -> None:
    called = False

    def fn(_: object) -> None:
        nonlocal called
        called = True

    _ = nothing().tap(fn)
    assert not called


def test_nothing_tap_returns_nothing_singleton() -> None:
    n = nothing()
    returned = n.tap(lambda _: None)
    assert returned is n


# ---------------------------------------------------------------------------
# Either.map
# ---------------------------------------------------------------------------


def test_success_map_applies_function() -> None:
    result = Success(3).map(lambda x: x * 2)
    assert result == Success(6)


def test_success_map_chain() -> None:
    result = Success(1).map(lambda x: x + 1).map(lambda x: x * 3)
    assert result == Success(6)


def test_failure_map_passes_through() -> None:
    f: Either[int, str] = Failure("err")
    result = f.map(lambda x: x * 2)
    assert result == Failure("err")


def test_failure_map_fn_not_called() -> None:
    called = False

    def fn(x: object) -> object:
        nonlocal called
        called = True
        return x

    _ = Failure("err").map(fn)
    assert not called


# ---------------------------------------------------------------------------
# Either.flat_map
# ---------------------------------------------------------------------------


def test_success_flat_map_applies_function() -> None:
    result = Success(3).flat_map(lambda x: Success(x * 2))
    assert result == Success(6)


def test_success_flat_map_can_return_failure() -> None:
    result = Success(3).flat_map(lambda _: Failure("bad"))
    assert result == Failure("bad")


def test_failure_flat_map_passes_through() -> None:
    f: Either[int, str] = Failure("err")
    result = f.flat_map(lambda x: Success(x * 2))
    assert result == Failure("err")


def test_failure_flat_map_fn_not_called() -> None:
    called = False

    def fn(x: object) -> Either[object, str]:
        nonlocal called
        called = True
        return Success(x)

    _ = Failure("err").flat_map(fn)
    assert not called


# ---------------------------------------------------------------------------
# Either.map_failure
# ---------------------------------------------------------------------------


def test_failure_map_failure_applies_function() -> None:
    result = Failure("err").map_failure(str.upper)
    assert result == Failure("ERR")


def test_success_map_failure_passes_through() -> None:
    result: Either[int, str] = Success(42)
    mapped = result.map_failure(str.upper)
    assert mapped == Success(42)


def test_success_map_failure_fn_not_called() -> None:
    called = False

    def fn(x: object) -> object:
        nonlocal called
        called = True
        return x

    _ = Success(42).map_failure(fn)
    assert not called


# ---------------------------------------------------------------------------
# Either.tap
# ---------------------------------------------------------------------------


def test_success_tap_calls_fn_with_value() -> None:
    captured: list[int] = []
    result = Success(42).tap(captured.append)
    assert captured == [42]
    assert result == Success(42)


def test_success_tap_returns_same_object() -> None:
    s = Success(1)
    returned = s.tap(lambda _: None)
    assert returned is s


def test_failure_tap_fn_not_called() -> None:
    called = False

    def fn(_: object) -> None:
        nonlocal called
        called = True

    _ = Failure("err").tap(fn)
    assert not called


# ---------------------------------------------------------------------------
# Either.tap_failure
# ---------------------------------------------------------------------------


def test_failure_tap_failure_calls_fn_with_exception() -> None:
    captured: list[str] = []
    result = Failure("err").tap_failure(captured.append)
    assert captured == ["err"]
    assert result == Failure("err")


def test_failure_tap_failure_returns_same_object() -> None:
    f = Failure("err")
    returned = f.tap_failure(lambda _: None)
    assert returned is f


def test_success_tap_failure_fn_not_called() -> None:
    called = False

    def fn(_: object) -> None:
        nonlocal called
        called = True

    _ = Success(42).tap_failure(fn)
    assert not called


# ---------------------------------------------------------------------------
# flatten (Option)
# ---------------------------------------------------------------------------


def test_flatten_some_some() -> None:
    result = flatten(some(some(42)))
    assert result == some(42)


def test_flatten_some_nothing() -> None:
    result = flatten(some(nothing()))
    assert result == nothing()


def test_flatten_nothing() -> None:
    opt: Option[Option[int]] = nothing()
    result: Option[int] = flatten(opt)
    assert result == nothing()


def test_flatten_option_identity_preserved() -> None:
    inner = some(99)
    outer = some(inner)
    result = flatten(outer)
    assert result is inner


# ---------------------------------------------------------------------------
# flatten (Either)
# ---------------------------------------------------------------------------


def test_flatten_success_success() -> None:
    result = flatten(Success(Success(42)))
    assert result == Success(42)


def test_flatten_success_failure() -> None:
    result = flatten(Success(Failure("err")))
    assert result == Failure("err")


def test_flatten_failure_passes_through() -> None:
    f: Either[Either[int, str], str] = Failure("outer")
    result: Either[int, str] = flatten(f)
    assert result == Failure("outer")


def test_flatten_either_identity_preserved() -> None:
    inner: Either[int, str] = Success(7)
    outer: Either[Either[int, str], str] = Success(inner)
    result = flatten(outer)
    assert result is inner


# ---------------------------------------------------------------------------
# flatten is exported from either_option
# ---------------------------------------------------------------------------


def test_flatten_in_public_api() -> None:

    assert hasattr(either_option, "flatten")
    assert "flatten" in either_option.__all__


# ---------------------------------------------------------------------------
# tap side-effect + chain composition
# ---------------------------------------------------------------------------


def test_tap_in_map_chain() -> None:
    log: list[int] = []
    result = some(1).map(lambda x: x + 1).tap(log.append).map(lambda x: x * 10)
    assert result == some(20)
    assert log == [2]


def test_tap_failure_in_map_chain() -> None:
    log: list[str] = []
    result: Either[int, str] = Failure("oops").tap_failure(log.append).map(lambda x: x + 1)
    assert result == Failure("oops")
    assert log == ["oops"]


def test_flat_map_short_circuits_on_failure() -> None:
    calls: list[str] = []

    def step(x: int) -> Either[int, str]:
        calls.append(f"step({x})")
        return Success(x + 1)

    result: Either[int, str] = Failure("err").flat_map(step).flat_map(step).flat_map(step)
    assert result == Failure("err")
    assert calls == []


def test_flat_map_short_circuits_after_first_failure() -> None:
    calls: list[str] = []

    def ok(x: int) -> Either[int, str]:
        calls.append(f"ok({x})")
        return Success(x + 1)

    def bad(x: int) -> Either[int, str]:
        calls.append(f"bad({x})")
        return Failure("stop")

    result = Success(0).flat_map(ok).flat_map(bad).flat_map(ok)
    assert result == Failure("stop")
    assert calls == ["ok(0)", "bad(1)"]


# ---------------------------------------------------------------------------
# map preservation through chain
# ---------------------------------------------------------------------------


def test_map_preserves_nothing_through_chain() -> None:
    result = nothing().map(lambda x: x + 1).map(lambda x: x * 2).map(str)
    assert result == nothing()
    assert isinstance(result, Nothing)


def test_map_preserves_failure_through_chain() -> None:
    base: Either[int, str] = Failure("err")
    result: Either[str, str] = base.map(lambda x: x + 1).map(str)
    assert result == Failure("err")


def test_nothing_map_fn_never_called_confirming_short_circuit() -> None:
    """nothing().map never invokes the fn — confirms short-circuit even with raising fn."""
    calls: list[int] = []

    def raising_fn(x: int) -> int:
        calls.append(x)
        msg = "should not run"
        raise AssertionError(msg)

    result = nothing().map(raising_fn)
    assert result == nothing()
    assert calls == []
