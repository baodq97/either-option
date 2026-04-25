"""Collections helpers for optional_python — Task 10.

Port of C# ``OptionCollectionExtensions``.  All functions are pure, lazy where
the return type is ``Iterator``, and import-safe on Python 3.10+.

Spec: docs/superpowers/specs/2026-04-26-optional-python-port-design.md §8
"""

from __future__ import annotations

import itertools
from collections.abc import Callable, Iterable, Iterator, Mapping
from typing import TypeVar

from optional_python._core import Either, Failure, Option, Some, Success, nothing, some

T = TypeVar("T")
K = TypeVar("K")
V = TypeVar("V")
E = TypeVar("E")


def first_or_none(
    it: Iterable[T],
    predicate: Callable[[T], bool] | None = None,
) -> Option[T]:
    """Return the first element of an iterable (optionally matching a predicate).

    Args:
        it: Any iterable to search.
        predicate: Optional filter; when given, only matching elements are
            considered.

    Returns:
        ``some(element)`` for the first qualifying element, or ``nothing()``
        when the iterable is empty or no element matches the predicate.
    """
    if predicate is None:
        for element in it:
            return some(element)
        return nothing()

    for element in it:
        if predicate(element):
            return some(element)
    return nothing()


def last_or_none(
    it: Iterable[T],
    predicate: Callable[[T], bool] | None = None,
) -> Option[T]:
    """Return the last element of an iterable (optionally matching a predicate).

    Iterates the entire sequence in a single pass, keeping the most recently
    seen qualifying element.

    Args:
        it: Any iterable to search.
        predicate: Optional filter; when given, only matching elements are
            considered.

    Returns:
        ``some(element)`` for the last qualifying element, or ``nothing()``
        when the iterable is empty or no element matches the predicate.
    """
    result: Option[T] = nothing()
    if predicate is None:
        for element in it:
            result = some(element)
    else:
        for element in it:
            if predicate(element):
                result = some(element)
    return result


def single_or_none(
    it: Iterable[T],
    predicate: Callable[[T], bool] | None = None,
) -> Option[T]:
    """Return the sole element of an iterable (optionally matching a predicate).

    Returns ``nothing()`` when zero *or more than one* element qualifies —
    this is a deliberate deviation from C#'s ``SingleOrDefault`` which raises
    on multiple matches (spec §8).

    The implementation is single-pass and does not load the full iterable into
    memory; it stops scanning as soon as a second match is found.

    Args:
        it: Any iterable to search.
        predicate: Optional filter; when given, only matching elements are
            considered.

    Returns:
        ``some(element)`` if exactly one qualifying element exists, otherwise
        ``nothing()``.
    """
    found: Option[T] = nothing()
    if predicate is None:
        iterator = iter(it)
        try:
            first = next(iterator)
        except StopIteration:
            return nothing()
        try:
            _ = next(iterator)
            return nothing()  # more than one element
        except StopIteration:
            return some(first)

    for element in it:
        if predicate(element):
            if isinstance(found, Some):
                return nothing()  # second match — return nothing immediately
            found = some(element)
    return found


def element_at_or_none(it: Iterable[T], index: int) -> Option[T]:
    """Return the element at a 0-based index in an iterable.

    Works safely with generators and any other non-indexable iterable by using
    ``itertools.islice`` for efficient advancement.

    Args:
        it: Any iterable to index into.
        index: 0-based position to retrieve.

    Returns:
        ``some(element)`` when ``index`` is in range, ``nothing()`` when
        ``index`` is negative or beyond the end of the iterable.
    """
    if index < 0:
        return nothing()
    # islice skips `index` elements cheaply, then we take exactly one.
    sliced = itertools.islice(it, index, index + 1)
    for element in sliced:
        return some(element)
    return nothing()


def get_or_none(
    source: Mapping[K, V] | Iterable[tuple[K, V]],
    key: K,
) -> Option[V]:
    """Look up a key in a mapping or an iterable of (key, value) pairs.

    When ``source`` is a ``Mapping`` (e.g. ``dict``), a direct O(1) lookup is
    used.  Otherwise the iterable is scanned linearly for the first pair whose
    first element compares equal to ``key``.

    Args:
        source: A ``Mapping[K, V]`` or an ``Iterable[tuple[K, V]]`` to search.
        key: The key to locate.

    Returns:
        ``some(value)`` when the key is found, ``nothing()`` otherwise.
    """
    if isinstance(source, Mapping):
        # Use a sentinel to distinguish a stored None from a missing key.
        _sentinel: object = object()
        found = source.get(key, _sentinel)  # type: ignore[reportUnknownMemberType]  # Mapping.get exists at runtime
        if found is not _sentinel:
            return some(found)  # type: ignore[reportArgumentType]  # narrowed: found is V (not sentinel)
        return nothing()

    # Linear scan over (k, v) pairs.
    for k, v in source:
        if k == key:
            return some(v)
    return nothing()


def values(options: Iterable[Option[T]]) -> Iterator[T]:
    """Yield the inner value of every ``Some`` in an iterable of options.

    ``Nothing`` elements are silently skipped.  The result is a lazy
    ``Iterator``; no element is evaluated before it is requested.

    Args:
        options: An iterable of ``Option[T]`` instances (mix of ``Some`` and
            ``Nothing`` is fine).

    Yields:
        The unwrapped value of each ``Some`` element, in order.
    """
    for opt in options:
        if isinstance(opt, Some):
            yield opt.value


def successes(eithers: Iterable[Either[T, E]]) -> Iterator[T]:
    """Yield the inner value of every ``Success`` in an iterable of eithers.

    ``Failure`` elements are silently skipped.  The result is a lazy
    ``Iterator``; no element is evaluated before it is requested.

    Args:
        eithers: An iterable of ``Either[T, E]`` instances.

    Yields:
        The unwrapped value of each ``Success`` element, in order.
    """
    for either in eithers:
        if isinstance(either, Success):
            yield either.value


def failures(eithers: Iterable[Either[T, E]]) -> Iterator[E]:
    """Yield the exception of every ``Failure`` in an iterable of eithers.

    ``Success`` elements are silently skipped.  The result is a lazy
    ``Iterator``; no element is evaluated before it is requested.

    Args:
        eithers: An iterable of ``Either[T, E]`` instances.

    Yields:
        The unwrapped exception of each ``Failure`` element, in order.
    """
    for either in eithers:
        if isinstance(either, Failure):
            yield either.exception
