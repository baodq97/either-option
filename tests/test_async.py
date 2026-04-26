"""Async surface — spec §4."""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, TypeVar

import pytest

from either_option import Either, Failure, Nothing, Option, Some, Success, nothing, some

if TYPE_CHECKING:
    from collections.abc import Coroutine

R = TypeVar("R")


def run(awaitable: Coroutine[object, object, R]) -> R:
    """Run a coroutine to completion in a fresh event loop."""
    return asyncio.run(awaitable)


# ===========================================================================
# Option.map_async
# ===========================================================================


def test_option_map_async_some() -> None:
    async def main() -> Option[int]:
        async def double(x: int) -> int:
            return x * 2

        return await some(5).map_async(double)

    assert run(main()) == some(10)


def test_option_map_async_nothing_does_not_call_mapping() -> None:
    calls = 0

    async def mapping(x: int) -> int:
        nonlocal calls
        calls += 1
        return x

    async def main() -> Option[int]:
        opt: Option[int] = nothing()
        return await opt.map_async(mapping)

    assert run(main()) == nothing()
    assert calls == 0


# ===========================================================================
# Option.flat_map_async
# ===========================================================================


def test_option_flat_map_async_some_returning_some() -> None:
    async def to_opt(x: int) -> Option[str]:
        return some(str(x))

    async def main() -> Option[str]:
        return await some(7).flat_map_async(to_opt)

    assert run(main()) == some("7")


def test_option_flat_map_async_some_returning_nothing() -> None:
    async def to_opt(_x: int) -> Option[str]:
        return nothing()

    async def main() -> Option[str]:
        return await some(7).flat_map_async(to_opt)

    assert run(main()) == nothing()


def test_option_flat_map_async_nothing_skips() -> None:
    calls = 0

    async def to_opt(x: int) -> Option[str]:
        nonlocal calls
        calls += 1
        return some(str(x))

    async def main() -> Option[str]:
        opt: Option[int] = nothing()
        return await opt.flat_map_async(to_opt)

    assert run(main()) == nothing()
    assert calls == 0


# ===========================================================================
# Option.filter_async
# ===========================================================================


def test_option_filter_async_some_truthy_keeps() -> None:
    async def is_positive(x: int) -> bool:
        return x > 0

    async def main() -> Option[int]:
        return await some(5).filter_async(is_positive)

    assert run(main()) == some(5)


def test_option_filter_async_some_falsy_drops() -> None:
    async def is_positive(x: int) -> bool:
        return x > 0

    async def main() -> Option[int]:
        return await some(-1).filter_async(is_positive)

    assert run(main()) == nothing()


def test_option_filter_async_nothing_skips() -> None:
    calls = 0

    async def predicate(_x: int) -> bool:
        nonlocal calls
        calls += 1
        return True

    async def main() -> Option[int]:
        opt: Option[int] = nothing()
        return await opt.filter_async(predicate)

    assert run(main()) == nothing()
    assert calls == 0


# ===========================================================================
# Option.tap_async
# ===========================================================================


def test_option_tap_async_some_calls_fn_and_returns_self() -> None:
    seen: list[int] = []

    async def log(x: int) -> None:
        seen.append(x)

    async def main() -> Some[int]:
        s = some(5)
        # tap returns Self so the static type is the receiver's class
        result = await s.tap_async(log)
        assert result is s
        return result

    _ = run(main())
    assert seen == [5]


def test_option_tap_async_nothing_skips_fn() -> None:
    calls = 0

    async def log(_x: int) -> None:
        nonlocal calls
        calls += 1

    async def main() -> None:
        opt: Option[int] = nothing()
        _ = await opt.tap_async(log)

    _ = run(main())
    assert calls == 0


# ===========================================================================
# Option.match_async / match_some_async / match_none_async
# ===========================================================================


def test_option_match_async_some() -> None:
    async def some_branch(x: int) -> str:
        return f"have {x}"

    async def none_branch() -> str:
        return "empty"

    async def main() -> str:
        return await some(7).match_async(some=some_branch, none=none_branch)

    assert run(main()) == "have 7"


def test_option_match_async_nothing() -> None:
    async def some_branch(x: int) -> str:
        return f"have {x}"

    async def none_branch() -> str:
        return "empty"

    async def main() -> str:
        opt: Option[int] = nothing()
        return await opt.match_async(some=some_branch, none=none_branch)

    assert run(main()) == "empty"


def test_option_match_some_async_calls_only_on_some() -> None:
    seen: list[int] = []

    async def action(x: int) -> None:
        seen.append(x)

    async def main() -> None:
        await some(3).match_some_async(action)
        opt: Option[int] = nothing()
        await opt.match_some_async(action)

    _ = run(main())
    assert seen == [3]


def test_option_match_none_async_calls_only_on_nothing() -> None:
    calls = 0

    async def action() -> None:
        nonlocal calls
        calls += 1

    async def main() -> None:
        await some(3).match_none_async(action)
        opt: Option[int] = nothing()
        await opt.match_none_async(action)

    _ = run(main())
    assert calls == 1


# ===========================================================================
# Option.value_or_else_async / or_else_async / or_option_else_async
# ===========================================================================


def test_option_value_or_else_async_some_skips_factory() -> None:
    calls = 0

    async def factory() -> int:
        nonlocal calls
        calls += 1
        return 0

    async def main() -> int:
        return await some(5).value_or_else_async(factory)

    assert run(main()) == 5
    assert calls == 0


def test_option_value_or_else_async_nothing_calls_factory() -> None:
    async def factory() -> int:
        return 99

    async def main() -> int:
        opt: Option[int] = nothing()
        return await opt.value_or_else_async(factory)

    assert run(main()) == 99


def test_option_or_else_async_some() -> None:
    async def factory() -> int:
        return 99

    async def main() -> Option[int]:
        return await some(5).or_else_async(factory)

    assert run(main()) == some(5)


def test_option_or_else_async_nothing() -> None:
    async def factory() -> int:
        return 99

    async def main() -> Option[int]:
        opt: Option[int] = nothing()
        return await opt.or_else_async(factory)

    assert run(main()) == some(99)


def test_option_or_option_else_async_some() -> None:
    async def factory() -> Option[int]:
        return some(99)

    async def main() -> Option[int]:
        return await some(5).or_option_else_async(factory)

    assert run(main()) == some(5)


def test_option_or_option_else_async_nothing() -> None:
    async def factory() -> Option[int]:
        return some(99)

    async def main() -> Option[int]:
        opt: Option[int] = nothing()
        return await opt.or_option_else_async(factory)

    assert run(main()) == some(99)


# ===========================================================================
# Either.map_async / flat_map_async / map_failure_async
# ===========================================================================


def test_either_map_async_success() -> None:
    async def double(x: int) -> int:
        return x * 2

    async def main() -> Either[int, str]:
        e: Either[int, str] = Either.some(5)
        return await e.map_async(double)

    assert run(main()) == Either.some(10)


def test_either_map_async_failure_skips() -> None:
    calls = 0

    async def mapping(x: int) -> int:
        nonlocal calls
        calls += 1
        return x

    async def main() -> Either[int, str]:
        e: Either[int, str] = Either.none("err")
        return await e.map_async(mapping)

    assert run(main()) == Either.none("err")
    assert calls == 0


def test_either_flat_map_async_success_to_success() -> None:
    async def step(x: int) -> Either[str, str]:
        return Either.some(f"v={x}")

    async def main() -> Either[str, str]:
        e: Either[int, str] = Either.some(5)
        return await e.flat_map_async(step)

    assert run(main()) == Either.some("v=5")


def test_either_flat_map_async_success_to_failure_widens_error() -> None:
    async def step(_x: int) -> Either[str, str]:
        return Either.none("downstream")

    async def main() -> Either[str, str]:
        e: Either[int, str] = Either.some(5)
        return await e.flat_map_async(step)

    assert run(main()) == Either.none("downstream")


def test_either_map_failure_async_failure() -> None:
    async def to_int(s: str) -> int:
        return len(s)

    async def main() -> Either[int, int]:
        e: Either[int, str] = Either.none("oops")
        return await e.map_failure_async(to_int)

    assert run(main()) == Either.none(4)


def test_either_map_failure_async_success_skips() -> None:
    calls = 0

    async def to_int(s: str) -> int:
        nonlocal calls
        calls += 1
        return len(s)

    async def main() -> Either[int, int]:
        e: Either[int, str] = Either.some(5)
        return await e.map_failure_async(to_int)

    assert run(main()) == Either.some(5)
    assert calls == 0


# ===========================================================================
# Either.filter_async
# ===========================================================================


def test_either_filter_async_success_truthy_keeps() -> None:
    async def is_positive(x: int) -> bool:
        return x > 0

    async def main() -> Either[int, str]:
        e: Either[int, str] = Either.some(5)
        return await e.filter_async(is_positive, exception="non-positive")

    assert run(main()) == Either.some(5)


def test_either_filter_async_success_falsy_returns_failure() -> None:
    async def is_positive(x: int) -> bool:
        return x > 0

    async def main() -> Either[int, str]:
        e: Either[int, str] = Either.some(-1)
        return await e.filter_async(is_positive, exception="non-positive")

    assert run(main()) == Either.none("non-positive")


def test_either_filter_async_failure_skips() -> None:
    calls = 0

    async def predicate(_x: int) -> bool:
        nonlocal calls
        calls += 1
        return True

    async def main() -> Either[int, str]:
        e: Either[int, str] = Either.none("orig")
        return await e.filter_async(predicate, exception="filter-out")

    assert run(main()) == Either.none("orig")
    assert calls == 0


# ===========================================================================
# Either.tap_async / tap_failure_async
# ===========================================================================


def test_either_tap_async_success_calls_fn() -> None:
    seen: list[int] = []

    async def log(x: int) -> None:
        seen.append(x)

    async def main() -> None:
        e: Either[int, str] = Either.some(5)
        _ = await e.tap_async(log)

    _ = run(main())
    assert seen == [5]


def test_either_tap_async_failure_skips_fn() -> None:
    calls = 0

    async def log(_x: int) -> None:
        nonlocal calls
        calls += 1

    async def main() -> None:
        e: Either[int, str] = Either.none("err")
        _ = await e.tap_async(log)

    _ = run(main())
    assert calls == 0


def test_either_tap_failure_async_failure_calls_fn() -> None:
    seen: list[str] = []

    async def log(s: str) -> None:
        seen.append(s)

    async def main() -> None:
        e: Either[int, str] = Either.none("boom")
        _ = await e.tap_failure_async(log)

    _ = run(main())
    assert seen == ["boom"]


def test_either_tap_failure_async_success_skips_fn() -> None:
    calls = 0

    async def log(_s: str) -> None:
        nonlocal calls
        calls += 1

    async def main() -> None:
        e: Either[int, str] = Either.some(5)
        _ = await e.tap_failure_async(log)

    _ = run(main())
    assert calls == 0


# ===========================================================================
# Either.match_async / match_some_async / match_none_async
# ===========================================================================


def test_either_match_async_success() -> None:
    async def s_branch(x: int) -> str:
        return f"ok:{x}"

    async def f_branch(s: str) -> str:
        return f"err:{s}"

    async def main() -> str:
        e: Either[int, str] = Either.some(5)
        return await e.match_async(some=s_branch, none=f_branch)

    assert run(main()) == "ok:5"


def test_either_match_async_failure() -> None:
    async def s_branch(x: int) -> str:
        return f"ok:{x}"

    async def f_branch(s: str) -> str:
        return f"err:{s}"

    async def main() -> str:
        e: Either[int, str] = Either.none("boom")
        return await e.match_async(some=s_branch, none=f_branch)

    assert run(main()) == "err:boom"


def test_either_match_some_async_only_on_success() -> None:
    seen: list[int] = []

    async def action(x: int) -> None:
        seen.append(x)

    async def main() -> None:
        e1: Either[int, str] = Either.some(7)
        await e1.match_some_async(action)
        e2: Either[int, str] = Either.none("err")
        await e2.match_some_async(action)

    _ = run(main())
    assert seen == [7]


def test_either_match_none_async_only_on_failure() -> None:
    seen: list[str] = []

    async def action(s: str) -> None:
        seen.append(s)

    async def main() -> None:
        e1: Either[int, str] = Either.some(7)
        await e1.match_none_async(action)
        e2: Either[int, str] = Either.none("err")
        await e2.match_none_async(action)

    _ = run(main())
    assert seen == ["err"]


# ===========================================================================
# Either.value_or_else_async / value_or_with_async / or_else_async / or_with_async
# ===========================================================================


def test_either_value_or_else_async_success_skips() -> None:
    calls = 0

    async def factory() -> int:
        nonlocal calls
        calls += 1
        return 0

    async def main() -> int:
        e: Either[int, str] = Either.some(5)
        return await e.value_or_else_async(factory)

    assert run(main()) == 5
    assert calls == 0


def test_either_value_or_with_async_failure_calls_mapping() -> None:
    async def mapping(s: str) -> int:
        return len(s)

    async def main() -> int:
        e: Either[int, str] = Either.none("boom")
        return await e.value_or_with_async(mapping)

    assert run(main()) == 4


def test_either_or_else_async_failure_returns_factory() -> None:
    async def factory() -> int:
        return 99

    async def main() -> Either[int, str]:
        e: Either[int, str] = Either.none("err")
        return await e.or_else_async(factory)

    assert run(main()) == Either.some(99)


def test_either_or_with_async_failure_passes_exception() -> None:
    received: list[str] = []

    async def mapping(s: str) -> int:
        received.append(s)
        return len(s)

    async def main() -> Either[int, str]:
        e: Either[int, str] = Either.none("oops")
        return await e.or_with_async(mapping)

    assert run(main()) == Either.some(4)
    assert received == ["oops"]


def test_either_or_option_else_async_failure_returns_factory() -> None:
    async def factory() -> Either[int, str]:
        return Either.some(7)

    async def main() -> Either[int, str]:
        e: Either[int, str] = Either.none("err")
        return await e.or_option_else_async(factory)

    assert run(main()) == Either.some(7)


def test_either_or_option_with_async_failure_calls_mapping() -> None:
    received: list[str] = []

    async def mapping(s: str) -> Either[int, str]:
        received.append(s)
        return Either.some(len(s))

    async def main() -> Either[int, str]:
        e: Either[int, str] = Either.none("xy")
        return await e.or_option_with_async(mapping)

    assert run(main()) == Either.some(2)
    assert received == ["xy"]


# ===========================================================================
# Either.from_awaitable
# ===========================================================================


def test_from_awaitable_success() -> None:
    async def good() -> int:
        return 42

    async def main() -> Either[int, Exception]:
        return await Either.from_awaitable(good())

    result = run(main())
    assert result == Either.some(42)


def test_from_awaitable_catches_exception() -> None:
    async def bad() -> int:
        msg = "boom"
        raise ValueError(msg)

    async def main() -> Either[int, Exception]:
        return await Either.from_awaitable(bad())

    result = run(main())
    assert isinstance(result, Failure)
    exc: object = result.exception
    assert isinstance(exc, ValueError)
    assert str(exc) == "boom"


def test_from_awaitable_specific_catch_filter() -> None:
    async def bad() -> int:
        msg = "value error"
        raise ValueError(msg)

    async def main() -> Either[int, ValueError]:
        return await Either.from_awaitable(bad(), catch=ValueError)

    result = run(main())
    assert isinstance(result, Failure)
    exc: object = result.exception
    assert isinstance(exc, ValueError)


def test_from_awaitable_uncaught_exception_propagates() -> None:
    async def bad() -> int:
        raise RuntimeError

    async def main() -> Either[int, ValueError]:
        return await Either.from_awaitable(bad(), catch=ValueError)

    with pytest.raises(RuntimeError):
        _ = run(main())


def test_from_awaitable_tuple_catch() -> None:
    async def bad() -> int:
        raise KeyError

    async def main() -> Either[int, Exception]:
        return await Either.from_awaitable(bad(), catch=(KeyError, ValueError))

    result = run(main())
    assert isinstance(result, Failure)
    exc: object = result.exception
    assert isinstance(exc, KeyError)


# ===========================================================================
# Async chain end-to-end (spec §4.3 example)
# ===========================================================================


def test_async_chain_success() -> None:
    """Demonstrate a real ROP chain with multiple async hops."""

    async def fetch_id(name: str) -> Either[int, str]:
        return Either.some(len(name)) if name else Either.none("empty")

    async def fetch_value(uid: int) -> int:
        return uid * 10

    async def main() -> Either[int, str]:
        step1 = await fetch_id("hello")
        return await step1.map_async(fetch_value)

    assert run(main()) == Either.some(50)


def test_async_chain_short_circuits_on_failure() -> None:
    """Failure at step 1 means step 2 is never invoked."""
    step2_calls = 0

    async def fetch_id(name: str) -> Either[int, str]:
        return Either.some(len(name)) if name else Either.none("empty")

    async def fetch_value(uid: int) -> int:
        nonlocal step2_calls
        step2_calls += 1
        return uid * 10

    async def main() -> Either[int, str]:
        step1 = await fetch_id("")
        return await step1.map_async(fetch_value)

    assert run(main()) == Either.none("empty")
    assert step2_calls == 0


# ===========================================================================
# Pattern matching in async tests still works at runtime
# ===========================================================================


def test_async_result_pattern_match() -> None:
    async def make_either(value: int, error: str | None) -> Either[int, str]:
        if error is not None:
            return Either.none(error)
        return Either.some(value)

    async def main() -> str:
        e = await make_either(42, None)
        result = await e.map_async(_double_async)
        match result:
            case Success(v):
                return f"ok:{v}"
            case Failure(_):
                return "err"
            case _:
                return "?"

    assert run(main()) == "ok:84"


async def _double_async(x: int) -> int:
    return x * 2


# ===========================================================================
# Sanity: Some/Nothing types still match at runtime in async contexts
# ===========================================================================


def test_some_nothing_runtime_types_in_async() -> None:
    async def make(present: bool) -> Option[int]:  # noqa: FBT001
        return some(1) if present else nothing()

    async def main() -> tuple[bool, bool]:
        s = await make(present=True)
        n = await make(present=False)
        return isinstance(s, Some), isinstance(n, Nothing)

    assert run(main()) == (True, True)
