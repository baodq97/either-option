"""optional-python unsafe module — value extraction without None-safety.

Mirrors the C# `Optional.Unsafe` namespace: callers must opt in by importing
from this submodule explicitly.  The only name promoted to the top-level
``optional_python`` package is ``OptionValueMissingError`` (per spec §6).

Spec: docs/superpowers/specs/2026-04-26-optional-python-port-design.md §9
"""

from collections.abc import Callable
from typing import TypeVar, overload

from optional_python._core import Either, Failure, Nothing, Option, Some, Success

__all__ = [
    "OptionValueMissingError",
    "to_optional",
    "value_or_default",
    "value_or_failure",
]

T = TypeVar("T")
E = TypeVar("E")


class OptionValueMissingError(Exception):
    """Raised when value extraction is attempted on a Nothing or Failure."""


# ---------------------------------------------------------------------------
# value_or_failure
# ---------------------------------------------------------------------------

# Overload 1: Option[T] with optional message → T
# Overload 2: Either[T, E] with optional message → T
# Overload 3: Either[T, E] with message_factory (keyword-only) → T
#
# All three share a single implementation below.  The @overload decorators
# serve the type-checker only; the runtime body handles all cases.


@overload
def value_or_failure(
    opt: Option[T],
    message: str | None = ...,
) -> T: ...


@overload
def value_or_failure(
    opt: Either[T, E],
    message: str | None = ...,
) -> T: ...


@overload
def value_or_failure(
    opt: Either[T, E],
    *,
    message_factory: Callable[[E], str],
) -> T: ...


def value_or_failure(
    opt: Option[T] | Either[T, E],
    message: str | None = None,
    *,
    message_factory: Callable[[E], str] | None = None,
) -> T:
    """Return the inner value, or raise ``OptionValueMissingError``.

    Parameters
    ----------
    opt:
        A ``Some``, ``Nothing``, ``Success``, or ``Failure``.
    message:
        Optional custom error message.  If omitted, a default is used.
        Mutually exclusive with *message_factory*.
    message_factory:
        Keyword-only.  A callable that receives the ``Failure`` payload and
        returns an error message string.  Only valid for ``Either`` inputs.
        Mutually exclusive with *message*.

    Raises:
    ------
    TypeError
        If both *message* and *message_factory* are supplied.
    OptionValueMissingError
        If ``opt`` is ``Nothing`` or ``Failure``.
    """
    if message is not None and message_factory is not None:
        msg = "message and message_factory are mutually exclusive"
        raise TypeError(msg)

    if isinstance(opt, Some):
        return opt.value

    if isinstance(opt, Success):
        return opt.value

    if isinstance(opt, Nothing):
        raise OptionValueMissingError(message or "Option has no value.")

    if isinstance(opt, Failure):
        text = (
            message_factory(opt.exception)
            if message_factory is not None
            else (message or "Either has no value.")
        )
        exc = OptionValueMissingError(text)
        if isinstance(opt.exception, Exception):
            raise exc from opt.exception
        raise exc

    # Should never reach here for well-typed inputs, but guard defensively.
    type_name = type(opt).__name__  # pragma: no cover
    msg = f"value_or_failure expects Option or Either, got {type_name!r}"  # pragma: no cover
    raise TypeError(msg)  # pragma: no cover


# ---------------------------------------------------------------------------
# value_or_default
# ---------------------------------------------------------------------------


def value_or_default(opt: Option[T] | Either[T, E]) -> T | None:
    """Return the inner value on ``Some``/``Success``, or ``None`` otherwise.

    Spec §9.  Note: ``Some(None)`` returns ``None`` — callers that need to
    distinguish "present None" from "absent" should use pattern matching.
    """
    if isinstance(opt, (Some, Success)):
        return opt.value
    return None


# ---------------------------------------------------------------------------
# to_optional
# ---------------------------------------------------------------------------


def to_optional(opt: Option[T]) -> T | None:
    """Return the inner value on ``Some``, or ``None`` on ``Nothing``.

    Parallels C# ``ToNullable`` — spec §9.  Alias for
    ``value_or_default`` restricted to the ``Option`` flavour.
    """
    if isinstance(opt, Some):
        return opt.value
    return None
