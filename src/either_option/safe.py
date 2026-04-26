"""Lift exception-raising callables into Either."""

from __future__ import annotations

import functools
from typing import TYPE_CHECKING, TypeVar

from typing_extensions import ParamSpec

from either_option._core import Either, Failure, Success

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

__all__ = ["call_safe", "safe", "safe_async"]


P = ParamSpec("P")
T = TypeVar("T")
E = TypeVar("E", bound=BaseException)


def safe(
    *,
    catch: type[E] | tuple[type[E], ...] = Exception,
) -> Callable[[Callable[P, T]], Callable[P, Either[T, E]]]:
    """Decorate a sync callable so it returns an Either instead of raising.

    Args:
        catch: Exception type(s) to catch. Anything else propagates. Defaults
            to ``Exception`` so ``KeyboardInterrupt`` and ``SystemExit`` are
            never silently swallowed.

    Example:
        >>> from either_option.safe import safe
        >>> @safe(catch=ValueError)
        ... def parse_age(s: str) -> int:
        ...     return int(s)
        >>> parse_age("42").value_or(-1)
        42
        >>> parse_age("xx").is_failure
        True
    """
    catch_tuple: tuple[type[BaseException], ...] = catch if isinstance(catch, tuple) else (catch,)

    def decorator(fn: Callable[P, T]) -> Callable[P, Either[T, E]]:
        @functools.wraps(fn)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> Either[T, E]:
            try:
                value = fn(*args, **kwargs)
            except catch_tuple as exc:
                return Failure(exc)
            return Success(value)

        return wrapper

    return decorator


def safe_async(
    *,
    catch: type[E] | tuple[type[E], ...] = Exception,
) -> Callable[[Callable[P, Awaitable[T]]], Callable[P, Awaitable[Either[T, E]]]]:
    """Decorate an async callable so it returns an Either instead of raising.

    Same semantics as :func:`safe` but for ``async def`` functions.

    Example:
        >>> import asyncio
        >>> from either_option.safe import safe_async
        >>> @safe_async(catch=ValueError)
        ... async def parse_age(s: str) -> int:
        ...     return int(s)
        >>> asyncio.run(parse_age("42")).value_or(-1)
        42
    """
    catch_tuple: tuple[type[BaseException], ...] = catch if isinstance(catch, tuple) else (catch,)

    def decorator(fn: Callable[P, Awaitable[T]]) -> Callable[P, Awaitable[Either[T, E]]]:
        @functools.wraps(fn)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> Either[T, E]:
            try:
                value = await fn(*args, **kwargs)
            except catch_tuple as exc:
                return Failure(exc)
            return Success(value)

        return wrapper

    return decorator


def call_safe(
    fn: Callable[..., T],
    *args: object,
    catch: type[E] | tuple[type[E], ...] = Exception,
    **kwargs: object,
) -> Either[T, E]:
    """One-shot lift of a callable invocation into Either.

    Equivalent to ``safe(catch=...)(fn)(*args, **kwargs)`` but without leaving
    a decorated wrapper around.

    Example:
        >>> from either_option.safe import call_safe
        >>> call_safe(int, "42").value_or(-1)
        42
        >>> call_safe(int, "xx", catch=ValueError).is_failure
        True
    """
    catch_tuple: tuple[type[BaseException], ...] = catch if isinstance(catch, tuple) else (catch,)
    try:
        value = fn(*args, **kwargs)
    except catch_tuple as exc:
        return Failure(exc)
    return Success(value)
