"""Extension helpers for constructing Option and Either from plain values.

Spec §7: ``some_not_none``, ``some_when``, ``none_when``, ``from_optional``.

These helpers cover the three "guarded" construction patterns from the C#
``OptionExtensions`` class (``SomeNotNull``, ``SomeWhen``, ``NoneWhen``) and
the ``ToOption`` / ``from_optional`` bridge from nullable Python types.

Usage::

    from optional_python.extensions import (
        some_not_none,
        some_when,
        none_when,
        from_optional,
    )

    # Plain Option forms:
    some_not_none("hello")  # Some("hello")
    some_not_none(None)  # Nothing
    some_when(10, lambda v: v > 5)  # Some(10)
    none_when(10, lambda v: v > 5)  # Nothing

    # Either forms — pass ``exception=`` or ``exception_else=``:
    some_not_none("hello", exception=ApiError("missing"))  # Success("hello")
    some_when(10, lambda v: v > 5, exception_else=lambda: "too low")  # Success(10)

``from_optional`` is Option-shaped only.  Callers that want an Either chain
``from_optional(x).with_exception(err)`` instead.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, TypeVar, overload

if TYPE_CHECKING:
    from collections.abc import Callable

from optional_python._core import Either, Failure, Nothing, Option, Some, Success

__all__ = [
    "from_optional",
    "none_when",
    "some_not_none",
    "some_when",
]

T = TypeVar("T")
E = TypeVar("E")

# ---------------------------------------------------------------------------
# Internal sentinel — distinguishes "caller passed nothing" from None / False.
# ---------------------------------------------------------------------------

_MISSING: object = object()

_MUTUAL_EXCLUSION_MSG = "provide either 'exception' or 'exception_else', not both"


# ---------------------------------------------------------------------------
# some_not_none
# ---------------------------------------------------------------------------


@overload
def some_not_none(value: T | None) -> Option[T]: ...


@overload
def some_not_none(value: T | None, *, exception: E) -> Either[T, E]: ...


@overload
def some_not_none(value: T | None, *, exception_else: Callable[[], E]) -> Either[T, E]: ...


def some_not_none(
    value: T | None,
    *,
    exception: E | object = _MISSING,
    exception_else: Callable[[], E] | None = None,
) -> Option[T] | Either[T, E]:
    """Return ``Some(value)`` or ``Nothing`` depending on whether *value* is ``None``.

    When neither *exception* nor *exception_else* is supplied, returns an
    ``Option[T]``.  When one of them is supplied, returns an ``Either[T, E]``
    instead — ``Success(value)`` if present, ``Failure(err)`` if absent.

    Args:
        value: The candidate value.  If ``None``, the absent branch is taken.
        exception: An eager exception to attach on the absent path.  Mutually
            exclusive with *exception_else*.
        exception_else: A zero-argument factory called *lazily* — only on the
            absent path.  Mutually exclusive with *exception*.

    Returns:
        ``Option[T]`` when neither *exception* nor *exception_else* is given;
        ``Either[T, E]`` otherwise.

    Raises:
        TypeError: If both *exception* and *exception_else* are supplied.

    Note:
        Passing ``exception=None`` is not supported — ``None`` is a valid
        exception object in some designs, but it is indistinguishable from
        "not provided" here.  Use ``exception_else=lambda: None`` if you
        genuinely need ``Failure(None)``.
    """
    has_exception = exception is not _MISSING
    has_exception_else = exception_else is not None

    if has_exception and has_exception_else:
        raise TypeError(_MUTUAL_EXCLUSION_MSG)

    present = value is not None

    if not has_exception and not has_exception_else:
        # Plain Option form.
        if present:
            return Some(value)
        return Nothing()

    # Either form.
    if present:
        return Success(value)

    if has_exception:
        return Failure(exception)  # type: ignore[arg-type]  # exception: E (sentinel excluded above)

    # has_exception_else is True here; exception_else is not None (established above).
    if exception_else is not None:
        return Failure(exception_else())

    # Unreachable: one of has_exception / has_exception_else is always True here.
    raise RuntimeError("unreachable")  # noqa: EM101


# ---------------------------------------------------------------------------
# some_when
# ---------------------------------------------------------------------------


@overload
def some_when(value: T, predicate: Callable[[T], bool]) -> Option[T]: ...


@overload
def some_when(value: T, predicate: Callable[[T], bool], *, exception: E) -> Either[T, E]: ...


@overload
def some_when(
    value: T, predicate: Callable[[T], bool], *, exception_else: Callable[[], E]
) -> Either[T, E]: ...


def some_when(
    value: T,
    predicate: Callable[[T], bool],
    *,
    exception: E | object = _MISSING,
    exception_else: Callable[[], E] | None = None,
) -> Option[T] | Either[T, E]:
    """Return ``Some(value)`` when *predicate(value)* is truthy, else ``Nothing``.

    When neither *exception* nor *exception_else* is supplied, returns an
    ``Option[T]``.  When one is supplied, returns ``Either[T, E]``.

    Args:
        value: The candidate value passed to *predicate*.
        predicate: A callable receiving *value* and returning a bool-like
            result.  The predicate is always called; if it raises, the
            exception propagates to the caller.
        exception: An eager exception to attach on the absent path (predicate
            returned falsy).  Mutually exclusive with *exception_else*.
        exception_else: A zero-argument factory called *lazily* only on the
            absent path.  Mutually exclusive with *exception*.

    Returns:
        ``Option[T]`` when neither *exception* nor *exception_else* is given;
        ``Either[T, E]`` otherwise.

    Raises:
        TypeError: If both *exception* and *exception_else* are supplied.
    """
    has_exception = exception is not _MISSING
    has_exception_else = exception_else is not None

    if has_exception and has_exception_else:
        raise TypeError(_MUTUAL_EXCLUSION_MSG)

    present = bool(predicate(value))

    if not has_exception and not has_exception_else:
        if present:
            return Some(value)
        return Nothing()

    if present:
        return Success(value)

    if has_exception:
        return Failure(exception)  # type: ignore[arg-type]  # exception: E (sentinel excluded above)

    # has_exception_else is True here; exception_else is not None (established above).
    if exception_else is not None:
        return Failure(exception_else())

    raise RuntimeError("unreachable")  # noqa: EM101


# ---------------------------------------------------------------------------
# none_when
# ---------------------------------------------------------------------------


@overload
def none_when(value: T, predicate: Callable[[T], bool]) -> Option[T]: ...


@overload
def none_when(value: T, predicate: Callable[[T], bool], *, exception: E) -> Either[T, E]: ...


@overload
def none_when(
    value: T, predicate: Callable[[T], bool], *, exception_else: Callable[[], E]
) -> Either[T, E]: ...


def none_when(
    value: T,
    predicate: Callable[[T], bool],
    *,
    exception: E | object = _MISSING,
    exception_else: Callable[[], E] | None = None,
) -> Option[T] | Either[T, E]:
    """Return ``Nothing`` when *predicate(value)* is truthy, else ``Some(value)``.

    The inverse of :func:`some_when`.  When neither *exception* nor
    *exception_else* is supplied, returns an ``Option[T]``.  When one is
    supplied, returns ``Either[T, E]``.

    Args:
        value: The candidate value passed to *predicate*.
        predicate: A callable receiving *value* and returning a bool-like
            result.  The predicate is always called; if it raises, the
            exception propagates to the caller.
        exception: An eager exception to attach on the absent path (predicate
            returned truthy).  Mutually exclusive with *exception_else*.
        exception_else: A zero-argument factory called *lazily* only on the
            absent path.  Mutually exclusive with *exception*.

    Returns:
        ``Option[T]`` when neither *exception* nor *exception_else* is given;
        ``Either[T, E]`` otherwise.

    Raises:
        TypeError: If both *exception* and *exception_else* are supplied.
    """
    has_exception = exception is not _MISSING
    has_exception_else = exception_else is not None

    if has_exception and has_exception_else:
        raise TypeError(_MUTUAL_EXCLUSION_MSG)

    # none_when is some_when with the predicate inverted.
    present = not bool(predicate(value))

    if not has_exception and not has_exception_else:
        if present:
            return Some(value)
        return Nothing()

    if present:
        return Success(value)

    if has_exception:
        return Failure(exception)  # type: ignore[arg-type]  # exception: E (sentinel excluded above)

    # has_exception_else is True here; exception_else is not None (established above).
    if exception_else is not None:
        return Failure(exception_else())

    raise RuntimeError("unreachable")  # noqa: EM101


# ---------------------------------------------------------------------------
# from_optional
# ---------------------------------------------------------------------------


def from_optional(value: T | None) -> Option[T]:
    """Convert a nullable Python value to an ``Option[T]``.

    Equivalent to :func:`some_not_none` but explicitly Option-shaped only.
    Callers that need an ``Either`` should chain
    ``from_optional(x).with_exception(err)`` instead.

    Args:
        value: A value that may be ``None``.

    Returns:
        ``Some(value)`` if *value* is not ``None``; ``Nothing`` otherwise.
    """
    if value is not None:
        return Some(value)
    return Nothing()
