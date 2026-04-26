"""Targeted tests to close coverage gaps in ABC and Failure paths."""

from __future__ import annotations

import asyncio

import pytest

from either_option import Either, Failure, Some, Success, nothing, some

# ---- Option.__bool__ -------------------------------------------------------


def test_some_bool_true() -> None:
    s = some(1)
    assert bool(s) is True


def test_nothing_bool_false() -> None:
    n = nothing()
    assert bool(n) is False


def test_option_truthy_in_if() -> None:
    if some(1):
        assert True
    else:
        msg = "Some(1) should be truthy"
        raise AssertionError(msg)


def test_option_falsy_nothing_in_if() -> None:
    if nothing():
        msg = "Nothing should be falsy"
        raise AssertionError(msg)
    assert True


# ---- Either: is_failure, is_some, is_none, __bool__, to_iterable, __contains__


def test_either_is_failure_on_failure() -> None:
    e: Either[int, str] = Either.none("err")
    assert e.is_failure is True
    assert e.is_some is False
    assert e.is_none is True
    assert bool(e) is False


def test_either_is_failure_on_success() -> None:
    e: Either[int, str] = Either.some(1)
    assert e.is_failure is False
    assert e.is_some is True
    assert e.is_none is False
    assert bool(e) is True


def test_either_to_iterable_success() -> None:
    e: Either[int, str] = Either.some(7)
    assert list(e.to_iterable()) == [7]


def test_either_to_iterable_failure() -> None:
    e: Either[int, str] = Either.none("err")
    assert list(e.to_iterable()) == []


def test_either_contains_via_in_operator() -> None:
    e: Either[int, str] = Either.some(7)
    assert 7 in e
    assert 8 not in e
    f: Either[int, str] = Either.none("err")
    assert 7 not in f


# ---- Failure: is_success, contains, exists --------------------------------


def test_failure_is_success_false() -> None:
    f: Either[int, str] = Either.none("err")
    assert f.is_success is False


def test_failure_contains_returns_false() -> None:
    f: Either[int, str] = Either.none("err")
    assert f.contains(0) is False
    assert f.contains("err") is False  # exception payload is not "the value"


def test_failure_exists_returns_false() -> None:
    f: Either[int, str] = Either.none("err")
    assert f.exists(lambda _x: True) is False


# ---- Success: contains, exists --------------------------------------------


def test_success_contains_via_value() -> None:
    s: Either[int, str] = Either.some(42)
    assert s.contains(42) is True
    assert s.contains(43) is False


def test_success_exists_with_predicate() -> None:
    s: Either[int, str] = Either.some(42)
    assert s.exists(lambda x: x > 0) is True
    assert s.exists(lambda x: x < 0) is False


# ---- __lt__ NotImplemented branches (cross-class) ------------------------


def test_some_lt_unrelated_returns_not_implemented() -> None:
    s: Some[int] = Some(1)
    other: object = "string"
    with pytest.raises(TypeError):
        _ = s < other


def test_nothing_lt_unrelated_returns_not_implemented() -> None:
    n = nothing()
    other: object = 0
    with pytest.raises(TypeError):
        _ = n < other


def test_success_lt_unrelated_returns_not_implemented() -> None:
    s = Success(1)
    other: object = "x"
    with pytest.raises(TypeError):
        _ = s < other


def test_failure_lt_unrelated_returns_not_implemented() -> None:
    f = Failure("x")
    other: object = 0
    with pytest.raises(TypeError):
        _ = f < other


# ---- filter_async error paths --------------------------------------------


def test_filter_async_both_exception_args_raises() -> None:
    async def predicate(_x: int) -> bool:
        return False

    async def main() -> None:
        e: Either[int, str] = Either.some(1)
        with pytest.raises(TypeError, match=r"not both"):
            _ = await e.filter_async(predicate, exception="x", exception_else=lambda: "y")

    asyncio.run(main())


def test_filter_async_no_exception_arg_when_failed_raises() -> None:
    async def predicate(_x: int) -> bool:
        return False

    async def call_filter() -> Either[int, str]:
        e: Either[int, str] = Either.some(1)
        return await e.filter_async(predicate)

    async def main() -> None:
        with pytest.raises(TypeError, match=r"requires exception"):
            _ = await call_filter()

    asyncio.run(main())


def test_filter_async_with_exception_else() -> None:
    async def predicate(_x: int) -> bool:
        return False

    async def main() -> Either[int, str]:
        e: Either[int, str] = Either.some(1)
        return await e.filter_async(predicate, exception_else=lambda: "lazy")

    assert asyncio.run(main()) == Either.none("lazy")


# ---- Failure async no-op paths -------------------------------------------


def test_failure_value_or_else_async_calls_factory() -> None:
    async def factory() -> int:
        return 99

    async def main() -> int:
        e: Either[int, str] = Either.none("err")
        return await e.value_or_else_async(factory)

    assert asyncio.run(main()) == 99


def test_failure_or_option_else_async_calls_factory() -> None:
    async def factory() -> Either[int, str]:
        return Either.some(99)

    async def main() -> Either[int, str]:
        e: Either[int, str] = Either.none("err")
        return await e.or_option_else_async(factory)

    assert asyncio.run(main()) == Either.some(99)


# ---- Failure async pass-through (not_none-style) -------------------------


def test_failure_filter_async_pass_through() -> None:
    """Failure paths through filter_async return self regardless of predicate."""

    async def predicate(_x: int) -> bool:
        return False

    async def main() -> Either[int, str]:
        e: Either[int, str] = Either.none("orig")
        return await e.filter_async(predicate, exception="ignored")

    assert asyncio.run(main()) == Either.none("orig")


# ---- Some.contains / exists (sanity) -------------------------------------


def test_some_contains_via_value() -> None:
    s = some(42)
    assert s.contains(42) is True
    assert s.contains(43) is False


def test_some_exists_truthy_predicate() -> None:
    s = some(42)
    assert s.exists(lambda x: x > 0) is True


def test_some_exists_falsy_predicate() -> None:
    s = some(42)
    assert s.exists(lambda x: x < 0) is False


# ---- Success async no-op paths (return self / value) ---------------------


def test_success_value_or_with_async_skips_mapping() -> None:
    calls = 0

    async def mapping(_e: str) -> int:
        nonlocal calls
        calls += 1
        return -1

    async def main() -> int:
        e: Either[int, str] = Either.some(5)
        return await e.value_or_with_async(mapping)

    assert asyncio.run(main()) == 5
    assert calls == 0


def test_success_or_else_async_skips_factory() -> None:
    calls = 0

    async def factory() -> int:
        nonlocal calls
        calls += 1
        return 99

    async def main() -> Either[int, str]:
        e: Either[int, str] = Either.some(5)
        return await e.or_else_async(factory)

    assert asyncio.run(main()) == Either.some(5)
    assert calls == 0


def test_success_or_with_async_skips_mapping() -> None:
    calls = 0

    async def mapping(_e: str) -> int:
        nonlocal calls
        calls += 1
        return 99

    async def main() -> Either[int, str]:
        e: Either[int, str] = Either.some(5)
        return await e.or_with_async(mapping)

    assert asyncio.run(main()) == Either.some(5)
    assert calls == 0


def test_success_or_option_else_async_skips_factory() -> None:
    calls = 0

    async def factory() -> Either[int, str]:
        nonlocal calls
        calls += 1
        return Either.some(99)

    async def main() -> Either[int, str]:
        e: Either[int, str] = Either.some(5)
        return await e.or_option_else_async(factory)

    assert asyncio.run(main()) == Either.some(5)
    assert calls == 0


def test_success_or_option_with_async_skips_mapping() -> None:
    calls = 0

    async def mapping(_e: str) -> Either[int, str]:
        nonlocal calls
        calls += 1
        return Either.some(99)

    async def main() -> Either[int, str]:
        e: Either[int, str] = Either.some(5)
        return await e.or_option_with_async(mapping)

    assert asyncio.run(main()) == Either.some(5)
    assert calls == 0


# ---- Failure async no-op paths (return self) ------------------------------


def test_failure_flat_map_async_skips_mapping() -> None:
    calls = 0

    async def mapping(_x: int) -> Either[str, str]:
        nonlocal calls
        calls += 1
        return Either.some("ok")

    async def main() -> Either[str, str]:
        e: Either[int, str] = Either.none("err")
        return await e.flat_map_async(mapping)

    assert asyncio.run(main()) == Either.none("err")
    assert calls == 0


# ---- Failure.__eq__ Success cross-branch returns False -------------------


def test_failure_eq_success_returns_false() -> None:
    f: Either[int, str] = Either.none("err")
    s: Either[int, str] = Either.some(0)
    assert f != s
    assert s != f
    # Confirm explicit False, not NotImplemented (which would also produce False).
    assert (f == s) is False
    assert (s == f) is False
