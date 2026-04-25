"""optional-python core: Option[T] and Either[T, E] as ABC + @final subclasses.

Spec: docs/superpowers/specs/2026-04-26-optional-python-port-design.md
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, ClassVar, Generic, TypeVar

from typing_extensions import Never, Self, final, override

if TYPE_CHECKING:
    from collections.abc import Callable, Iterator

T = TypeVar("T")  # invariant — used only in classmethod factories
T_co = TypeVar("T_co", covariant=True)
U = TypeVar("U")
E = TypeVar("E")  # invariant — used only in classmethod factories
E_co = TypeVar("E_co", covariant=True)
F = TypeVar("F")
R = TypeVar("R")


# ---------------------------------------------------------------------------
# Option type
# ---------------------------------------------------------------------------


class Option(ABC, Generic[T_co]):
    """Sum type: Some(value) | Nothing.

    Spec §2.1. Concrete subclasses (`Some`, `Nothing`) carry the data;
    methods dispatch via abstract methods + isinstance where needed.
    """

    __slots__ = ()

    @property
    @abstractmethod
    def is_some(self) -> bool: ...

    @property
    def is_none(self) -> bool:
        return not self.is_some

    def __bool__(self) -> bool:
        return self.is_some

    @classmethod
    def some(cls, value: T) -> Option[T]:
        """Create a Some option wrapping the given value."""
        return Some(value)

    @classmethod
    def none(cls) -> Option[Never]:
        """Return the Nothing singleton."""
        return Nothing()

    # Equality + hash must be defined per concrete subclass — see §13.2.
    @abstractmethod
    @override
    def __eq__(self, other: object) -> bool: ...

    @abstractmethod
    @override
    def __hash__(self) -> int: ...

    # ---- Iteration --------------------------------------------------------

    @abstractmethod
    def __iter__(self) -> Iterator[T_co]: ...

    def to_iterable(self) -> Iterator[T_co]:
        """Return an iterator over 0 or 1 elements."""
        return iter(self)

    def __contains__(self, value: object) -> bool:
        return self.contains(value)

    @abstractmethod
    def contains(self, value: object) -> bool: ...

    @abstractmethod
    def exists(self, predicate: Callable[[T_co], bool]) -> bool: ...

    # ---- Method signatures for the typing spike -----------------------
    # Bodies are stubs; landed in later Tasks. The signatures below are
    # the gate: pyright must accept them and the call sites in test_typing.py.

    @abstractmethod
    def value_or(self, alternative: U) -> T_co | U: ...

    @abstractmethod
    def or_value(self, alternative: U) -> Option[T_co | U]: ...

    @abstractmethod
    def or_option(self, alternative: Option[U]) -> Option[T_co | U]: ...

    @abstractmethod
    def with_exception(self, exception: E_co) -> Either[T_co, E_co]: ...

    @abstractmethod
    def map(self, mapping: Callable[[T_co], U]) -> Option[U]: ...

    @abstractmethod
    def flat_map(self, mapping: Callable[[T_co], Option[U]]) -> Option[U]: ...

    @abstractmethod
    def filter(self, predicate: Callable[[T_co], bool]) -> Option[T_co]: ...

    @abstractmethod
    def tap(self, fn: Callable[[T_co], object]) -> Self: ...

    # ---- Match family (Task 3) --------------------------------------------

    @abstractmethod
    def match(self, *, some: Callable[[T_co], R], none: Callable[[], R]) -> R: ...

    @abstractmethod
    def match_some(self, action: Callable[[T_co], None]) -> None: ...

    @abstractmethod
    def match_none(self, action: Callable[[], None]) -> None: ...

    # ---- Value extraction (Task 4) ----------------------------------------

    @abstractmethod
    def value_or_else(self, factory: Callable[[], U]) -> T_co | U: ...


@final
class Some(Option[T_co]):
    """A present value. Spec §2.1."""

    __slots__ = ("value",)
    __match_args__ = ("value",)

    value: T_co

    def __init__(self, value: T_co) -> None:
        self.value = value

    @property
    @override
    def is_some(self) -> bool:
        return True

    @override
    def __eq__(self, other: object) -> bool:
        if isinstance(other, Some):
            # other.value is Unknown (generic T of 'other' unbound in __eq__).
            # Equality comparison is intentionally value-level; bool() is safe.
            return bool(self.value == other.value)  # type: ignore[reportUnknownMemberType,reportUnknownArgumentType]
        return NotImplemented

    @override
    def __hash__(self) -> int:
        return hash(("optional_python.Some", self.value))

    @override
    def __repr__(self) -> str:
        return f"Some({self.value!r})"

    # ---- Iteration --------------------------------------------------------

    @override
    def __iter__(self) -> Iterator[T_co]:
        yield self.value

    @override
    def contains(self, value: object) -> bool:
        return bool(self.value == value)

    @override
    def exists(self, predicate: Callable[[T_co], bool]) -> bool:
        return bool(predicate(self.value))

    # Stub bodies — TODO Tasks 6-7 implement.
    @override
    def value_or(self, alternative: U) -> T_co | U:
        raise NotImplementedError

    @override
    def or_value(self, alternative: U) -> Option[T_co | U]:
        raise NotImplementedError

    @override
    def or_option(self, alternative: Option[U]) -> Option[T_co | U]:
        raise NotImplementedError

    @override
    def with_exception(self, exception: E_co) -> Either[T_co, E_co]:
        raise NotImplementedError

    @override
    def map(self, mapping: Callable[[T_co], U]) -> Option[U]:
        raise NotImplementedError

    @override
    def flat_map(self, mapping: Callable[[T_co], Option[U]]) -> Option[U]:
        raise NotImplementedError

    @override
    def filter(self, predicate: Callable[[T_co], bool]) -> Option[T_co]:
        raise NotImplementedError

    @override
    def tap(self, fn: Callable[[T_co], object]) -> Self:
        raise NotImplementedError

    # ---- Match family (Task 3) --------------------------------------------

    @override
    def match(self, *, some: Callable[[T_co], R], none: Callable[[], R]) -> R:
        return some(self.value)

    @override
    def match_some(self, action: Callable[[T_co], None]) -> None:
        action(self.value)

    @override
    def match_none(self, action: Callable[[], None]) -> None:
        pass

    # ---- Value extraction (Task 4) ----------------------------------------

    @override
    def value_or_else(self, factory: Callable[[], U]) -> T_co | U:
        return self.value


@final
class Nothing(Option[Never]):
    """Singleton. @final + cached __new__ + Option[Never] superclass — spec §2.1, §13.6."""

    __slots__ = ()

    _instance: ClassVar[Nothing | None] = None

    def __new__(cls) -> Nothing:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @property
    @override
    def is_some(self) -> bool:
        return False

    @override
    def __eq__(self, other: object) -> bool:
        if isinstance(other, Nothing):
            return True
        return NotImplemented

    @override
    def __hash__(self) -> int:
        return hash(("optional_python.Nothing",))

    @override
    def __repr__(self) -> str:
        return "Nothing"

    # ---- Iteration --------------------------------------------------------

    @override
    def __iter__(self) -> Iterator[Never]:
        return iter(())

    @override
    def contains(self, value: object) -> bool:
        return False

    @override
    def exists(self, predicate: Callable[[Any], bool]) -> bool:
        return False

    @override
    def value_or(self, alternative: U) -> U:
        raise NotImplementedError

    @override
    def or_value(self, alternative: U) -> Option[U]:
        raise NotImplementedError

    @override
    def or_option(self, alternative: Option[U]) -> Option[U]:
        raise NotImplementedError

    @override
    def with_exception(self, exception: E_co) -> Either[Never, E_co]:
        raise NotImplementedError

    @override
    def map(self, mapping: Callable[[Any], U]) -> Option[U]:
        raise NotImplementedError

    @override
    def flat_map(self, mapping: Callable[[Any], Option[U]]) -> Option[U]:
        raise NotImplementedError

    @override
    def filter(self, predicate: Callable[[Any], bool]) -> Option[Never]:
        raise NotImplementedError

    @override
    def tap(self, fn: Callable[[Any], object]) -> Self:
        raise NotImplementedError

    # ---- Match family (Task 3) --------------------------------------------

    @override
    def match(self, *, some: Callable[[Any], R], none: Callable[[], R]) -> R:
        return none()

    @override
    def match_some(self, action: Callable[[Any], None]) -> None:
        pass

    @override
    def match_none(self, action: Callable[[], None]) -> None:
        action()

    # ---- Value extraction (Task 4) ----------------------------------------

    @override
    def value_or_else(self, factory: Callable[[], U]) -> U:
        return factory()


def some(value: T) -> Some[T]:
    """Wrap a value in Some. Returns Option[T]."""
    return Some(value)


def nothing() -> Nothing:
    """Return the Nothing singleton. Typed as Option[Never] for widening."""
    return Nothing()


# ---------------------------------------------------------------------------
# Either type
# ---------------------------------------------------------------------------


class Either(ABC, Generic[T_co, E_co]):
    """Sum type: Success(value) | Failure(exception). Spec §2.2."""

    __slots__ = ()

    @property
    @abstractmethod
    def is_success(self) -> bool: ...

    @property
    def is_failure(self) -> bool:
        return not self.is_success

    @property
    def is_some(self) -> bool:
        return self.is_success

    @property
    def is_none(self) -> bool:
        return self.is_failure

    def __bool__(self) -> bool:
        return self.is_success

    @classmethod
    def some(cls, value: T) -> Either[T, Never]:
        """Create a Success wrapping the given value."""
        return Success(value)

    @classmethod
    def none(cls, exception: E) -> Either[Never, E]:
        """Create a Failure wrapping the given exception."""
        return Failure(exception)

    @abstractmethod
    @override
    def __eq__(self, other: object) -> bool: ...

    @abstractmethod
    @override
    def __hash__(self) -> int: ...

    # ---- Iteration --------------------------------------------------------

    @abstractmethod
    def __iter__(self) -> Iterator[T_co]: ...

    def to_iterable(self) -> Iterator[T_co]:
        """Return an iterator over 0 or 1 elements."""
        return iter(self)

    def __contains__(self, value: object) -> bool:
        return self.contains(value)

    @abstractmethod
    def contains(self, value: object) -> bool: ...

    @abstractmethod
    def exists(self, predicate: Callable[[T_co], bool]) -> bool: ...

    # Method-signature stubs for the typing spike.
    @abstractmethod
    def value_or(self, alternative: U) -> T_co | U: ...

    @abstractmethod
    def or_value(self, alternative: U) -> Either[T_co | U, E_co]: ...

    @abstractmethod
    def or_option(self, alternative: Either[U, E_co]) -> Either[T_co | U, E_co]: ...

    @abstractmethod
    def map(self, mapping: Callable[[T_co], U]) -> Either[U, E_co]: ...

    @abstractmethod
    def map_failure(self, mapping: Callable[[E_co], F]) -> Either[T_co, F]: ...

    @abstractmethod
    def flat_map(self, mapping: Callable[[T_co], Either[U, E_co]]) -> Either[U, E_co]: ...

    @abstractmethod
    def filter(
        self,
        predicate: Callable[[T_co], bool],
        *,
        exception: E_co | None = None,
        exception_else: Callable[[], E_co] | None = None,
    ) -> Either[T_co, E_co]: ...

    @abstractmethod
    def without_exception(self) -> Option[T_co]: ...

    @abstractmethod
    def tap(self, fn: Callable[[T_co], object]) -> Self: ...

    @abstractmethod
    def tap_failure(self, fn: Callable[[E_co], object]) -> Self: ...

    # ---- Match family (Task 3) --------------------------------------------

    @abstractmethod
    def match(self, *, some: Callable[[T_co], R], none: Callable[[E_co], R]) -> R: ...

    @abstractmethod
    def match_some(self, action: Callable[[T_co], None]) -> None: ...

    @abstractmethod
    def match_none(self, action: Callable[[E_co], None]) -> None: ...

    # ---- Value extraction (Task 4) ----------------------------------------

    @abstractmethod
    def value_or_else(self, factory: Callable[[], U]) -> T_co | U: ...

    @abstractmethod
    def value_or_with(self, mapping: Callable[[E_co], U]) -> T_co | U: ...


@final
class Success(Either[T_co, Never]):
    """A green-track value. Spec §2.2."""

    __slots__ = ("value",)
    __match_args__ = ("value",)

    value: T_co

    def __init__(self, value: T_co) -> None:
        self.value = value

    @property
    @override
    def is_success(self) -> bool:
        return True

    @override
    def __eq__(self, other: object) -> bool:
        if isinstance(other, Success):
            # other.value is Unknown (generic T of 'other' unbound in __eq__).
            # Equality comparison is intentionally value-level; bool() is safe.
            return bool(self.value == other.value)  # type: ignore[reportUnknownMemberType,reportUnknownArgumentType]
        if isinstance(other, Failure):
            return False
        return NotImplemented

    @override
    def __hash__(self) -> int:
        return hash(("optional_python.Success", self.value))

    @override
    def __repr__(self) -> str:
        return f"Success({self.value!r})"

    # ---- Iteration --------------------------------------------------------

    @override
    def __iter__(self) -> Iterator[T_co]:
        yield self.value

    @override
    def contains(self, value: object) -> bool:
        return bool(self.value == value)

    @override
    def exists(self, predicate: Callable[[T_co], bool]) -> bool:
        return bool(predicate(self.value))

    @override
    def value_or(self, alternative: U) -> T_co | U:
        raise NotImplementedError

    @override
    def or_value(self, alternative: U) -> Either[T_co | U, Never]:
        raise NotImplementedError

    @override
    def or_option(self, alternative: Either[U, Never]) -> Either[T_co | U, Never]:
        raise NotImplementedError

    @override
    def map(self, mapping: Callable[[T_co], U]) -> Either[U, Never]:
        raise NotImplementedError

    @override
    def map_failure(self, mapping: Callable[[Never], F]) -> Either[T_co, F]:
        raise NotImplementedError

    @override
    def flat_map(self, mapping: Callable[[T_co], Either[U, F]]) -> Either[U, F]:
        raise NotImplementedError

    @override
    def filter(
        self,
        predicate: Callable[[T_co], bool],
        *,
        exception: F | None = None,
        exception_else: Callable[[], F] | None = None,
    ) -> Either[T_co, F]:
        raise NotImplementedError

    @override
    def without_exception(self) -> Option[T_co]:
        raise NotImplementedError

    @override
    def tap(self, fn: Callable[[T_co], object]) -> Self:
        raise NotImplementedError

    @override
    def tap_failure(self, fn: Callable[[Never], object]) -> Self:
        raise NotImplementedError

    # ---- Match family (Task 3) --------------------------------------------

    @override
    def match(self, *, some: Callable[[T_co], R], none: Callable[[Any], R]) -> R:
        return some(self.value)

    @override
    def match_some(self, action: Callable[[T_co], None]) -> None:
        action(self.value)

    @override
    def match_none(self, action: Callable[[Any], None]) -> None:
        pass

    # ---- Value extraction (Task 4) ----------------------------------------

    @override
    def value_or_else(self, factory: Callable[[], U]) -> T_co | U:
        return self.value

    @override
    def value_or_with(self, mapping: Callable[[Any], U]) -> T_co | U:
        return self.value


@final
class Failure(Either[Never, E_co]):
    """A red-track exception. Spec §2.2."""

    __slots__ = ("exception",)
    __match_args__ = ("exception",)

    exception: E_co

    def __init__(self, exception: E_co) -> None:
        self.exception = exception

    @property
    @override
    def is_success(self) -> bool:
        return False

    @override
    def __eq__(self, other: object) -> bool:
        if isinstance(other, Failure):
            # other.exception is Unknown (generic E of 'other' unbound in __eq__).
            # Equality comparison is intentionally value-level; bool() is safe.
            return bool(self.exception == other.exception)  # type: ignore[reportUnknownMemberType,reportUnknownArgumentType]
        if isinstance(other, Success):
            return False
        return NotImplemented

    @override
    def __hash__(self) -> int:
        return hash(("optional_python.Failure", self.exception))

    @override
    def __repr__(self) -> str:
        return f"Failure({self.exception!r})"

    # ---- Iteration --------------------------------------------------------

    @override
    def __iter__(self) -> Iterator[Never]:
        return iter(())

    @override
    def contains(self, value: object) -> bool:
        return False

    @override
    def exists(self, predicate: Callable[[Any], bool]) -> bool:
        return False

    @override
    def value_or(self, alternative: U) -> U:
        raise NotImplementedError

    @override
    def or_value(self, alternative: U) -> Either[U, E_co]:
        raise NotImplementedError

    @override
    def or_option(self, alternative: Either[U, E_co]) -> Either[U, E_co]:
        raise NotImplementedError

    @override
    def map(self, mapping: Callable[[Any], U]) -> Either[U, E_co]:
        raise NotImplementedError

    @override
    def map_failure(self, mapping: Callable[[E_co], F]) -> Either[Never, F]:
        raise NotImplementedError

    @override
    def flat_map(self, mapping: Callable[[Any], Either[U, E_co]]) -> Either[U, E_co]:
        raise NotImplementedError

    @override
    def filter(
        self,
        predicate: Callable[[Any], bool],
        *,
        exception: E_co | None = None,
        exception_else: Callable[[], E_co] | None = None,
    ) -> Either[Never, E_co]:
        raise NotImplementedError

    @override
    def without_exception(self) -> Option[Never]:
        raise NotImplementedError

    @override
    def tap(self, fn: Callable[[Any], object]) -> Self:
        raise NotImplementedError

    @override
    def tap_failure(self, fn: Callable[[E_co], object]) -> Self:
        raise NotImplementedError

    # ---- Match family (Task 3) --------------------------------------------

    @override
    def match(self, *, some: Callable[[Any], R], none: Callable[[E_co], R]) -> R:
        return none(self.exception)

    @override
    def match_some(self, action: Callable[[Any], None]) -> None:
        pass

    @override
    def match_none(self, action: Callable[[E_co], None]) -> None:
        action(self.exception)

    # ---- Value extraction (Task 4) ----------------------------------------

    @override
    def value_or_else(self, factory: Callable[[], U]) -> U:
        return factory()

    @override
    def value_or_with(self, mapping: Callable[[E_co], U]) -> U:
        return mapping(self.exception)
