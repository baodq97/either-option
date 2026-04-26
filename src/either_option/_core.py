"""either-option core: Option[T] and Either[T, E] as ABC + @final subclasses."""

from __future__ import annotations

from abc import ABC, abstractmethod
from functools import total_ordering
from typing import TYPE_CHECKING, Any, ClassVar, Generic, TypeVar, overload

from typing_extensions import Never, Self, final, override

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable, Iterator

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
    def with_exception(self, exception: E) -> Either[T_co, E]: ...

    @abstractmethod
    def with_exception_else(self, factory: Callable[[], E]) -> Either[T_co, E]: ...

    @abstractmethod
    def not_none(self) -> Option[T_co]: ...

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

    # ---- Alternatives (Task 5) --------------------------------------------

    @abstractmethod
    def or_else(self, factory: Callable[[], U]) -> Option[T_co | U]: ...

    @abstractmethod
    def or_option_else(self, factory: Callable[[], Option[U]]) -> Option[T_co | U]: ...

    # ---- Async surface (Task 12) ------------------------------------------

    @abstractmethod
    async def map_async(self, mapping: Callable[[T_co], Awaitable[U]]) -> Option[U]: ...

    @abstractmethod
    async def flat_map_async(
        self, mapping: Callable[[T_co], Awaitable[Option[U]]]
    ) -> Option[U]: ...

    @abstractmethod
    async def filter_async(self, predicate: Callable[[T_co], Awaitable[bool]]) -> Option[T_co]: ...

    @abstractmethod
    async def tap_async(self, fn: Callable[[T_co], Awaitable[object]]) -> Self: ...

    @abstractmethod
    async def match_async(
        self, *, some: Callable[[T_co], Awaitable[R]], none: Callable[[], Awaitable[R]]
    ) -> R: ...

    @abstractmethod
    async def match_some_async(self, action: Callable[[T_co], Awaitable[None]]) -> None: ...

    @abstractmethod
    async def match_none_async(self, action: Callable[[], Awaitable[None]]) -> None: ...

    @abstractmethod
    async def value_or_else_async(self, factory: Callable[[], Awaitable[U]]) -> T_co | U: ...

    @abstractmethod
    async def or_else_async(self, factory: Callable[[], Awaitable[U]]) -> Option[T_co | U]: ...

    @abstractmethod
    async def or_option_else_async(
        self, factory: Callable[[], Awaitable[Option[U]]]
    ) -> Option[T_co | U]: ...


@final
@total_ordering
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
        return hash(("either_option.Some", self.value))

    @override
    def __repr__(self) -> str:
        return f"Some({self.value!r})"

    # ---- Ordering (Task 8) ------------------------------------------------

    def __lt__(self, other: object) -> bool:
        """Some(x) < Some(y) iff x < y; Nothing < Some(_) always."""
        if isinstance(other, Some):
            return bool(self.value < other.value)  # type: ignore[operator]
        if isinstance(other, Nothing):
            return False  # Some > Nothing
        return NotImplemented

    # ---- Pickle (Task 8) --------------------------------------------------

    @override
    def __reduce__(self) -> tuple[Any, tuple[Any]]:
        return (some, (self.value,))

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
        return self.value

    @override
    def or_value(self, alternative: U) -> Option[T_co | U]:
        return self

    @override
    def or_option(self, alternative: Option[U]) -> Option[T_co | U]:
        return self

    # ---- Interop (Task 7) ------------------------------------------------

    @override
    def with_exception(self, exception: E) -> Either[T_co, E]:
        return Success(self.value)

    @override
    def with_exception_else(self, factory: Callable[[], E]) -> Either[T_co, E]:
        return Success(self.value)

    @override
    def not_none(self) -> Option[T_co]:
        if self.value is None:
            return Nothing()
        return self

    # ---- Map / flat_map / tap (Task 6) ------------------------------------

    @override
    def map(self, mapping: Callable[[T_co], U]) -> Option[U]:
        return Some(mapping(self.value))

    @override
    def flat_map(self, mapping: Callable[[T_co], Option[U]]) -> Option[U]:
        return mapping(self.value)

    @override
    def filter(self, predicate: Callable[[T_co], bool]) -> Option[T_co]:
        return self if predicate(self.value) else Nothing()

    @override
    def tap(self, fn: Callable[[T_co], object]) -> Self:
        _ = fn(self.value)
        return self

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

    # ---- Alternatives (Task 5) --------------------------------------------

    @override
    def or_else(self, factory: Callable[[], U]) -> Option[T_co | U]:
        return self

    @override
    def or_option_else(self, factory: Callable[[], Option[U]]) -> Option[T_co | U]:
        return self

    # ---- Async surface (Task 12) ------------------------------------------

    @override
    async def map_async(self, mapping: Callable[[T_co], Awaitable[U]]) -> Option[U]:
        return Some(await mapping(self.value))

    @override
    async def flat_map_async(self, mapping: Callable[[T_co], Awaitable[Option[U]]]) -> Option[U]:
        return await mapping(self.value)

    @override
    async def filter_async(self, predicate: Callable[[T_co], Awaitable[bool]]) -> Option[T_co]:
        return self if await predicate(self.value) else Nothing()

    @override
    async def tap_async(self, fn: Callable[[T_co], Awaitable[object]]) -> Self:
        _ = await fn(self.value)
        return self

    @override
    async def match_async(
        self, *, some: Callable[[T_co], Awaitable[R]], none: Callable[[], Awaitable[R]]
    ) -> R:
        return await some(self.value)

    @override
    async def match_some_async(self, action: Callable[[T_co], Awaitable[None]]) -> None:
        await action(self.value)

    @override
    async def match_none_async(self, action: Callable[[], Awaitable[None]]) -> None:
        pass

    @override
    async def value_or_else_async(self, factory: Callable[[], Awaitable[U]]) -> T_co | U:
        return self.value

    @override
    async def or_else_async(self, factory: Callable[[], Awaitable[U]]) -> Option[T_co | U]:
        return self

    @override
    async def or_option_else_async(
        self, factory: Callable[[], Awaitable[Option[U]]]
    ) -> Option[T_co | U]:
        return self


@final
@total_ordering
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
        return hash(("either_option.Nothing",))

    @override
    def __repr__(self) -> str:
        return "Nothing"

    # ---- Ordering (Task 8) ------------------------------------------------

    def __lt__(self, other: object) -> bool:
        """Nothing < Some(_) always; Nothing == Nothing (handled by __eq__)."""
        if isinstance(other, Nothing):
            return False  # equal, not less than
        if isinstance(other, Some):
            return True  # Nothing < Some(_)
        return NotImplemented

    # ---- Pickle (Task 8) --------------------------------------------------

    @override
    def __reduce__(self) -> tuple[Any, tuple[()]]:
        return (nothing, ())

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
        return alternative

    @override
    def or_value(self, alternative: U) -> Option[U]:
        return Some(alternative)

    @override
    def or_option(self, alternative: Option[U]) -> Option[U]:
        return alternative

    # ---- Interop (Task 7) ------------------------------------------------

    @override
    def with_exception(self, exception: E) -> Either[Never, E]:
        return Failure(exception)

    @override
    def with_exception_else(self, factory: Callable[[], E]) -> Either[Never, E]:
        return Failure(factory())

    @override
    def not_none(self) -> Option[Never]:
        return self

    # ---- Map / flat_map / tap (Task 6) ------------------------------------

    @override
    def map(self, mapping: Callable[[Any], U]) -> Option[U]:
        return self

    @override
    def flat_map(self, mapping: Callable[[Any], Option[U]]) -> Option[U]:
        return self

    @override
    def filter(self, predicate: Callable[[Any], bool]) -> Option[Never]:
        return self

    @override
    def tap(self, fn: Callable[[Any], object]) -> Self:
        return self

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

    # ---- Alternatives (Task 5) --------------------------------------------

    @override
    def or_else(self, factory: Callable[[], U]) -> Option[U]:
        return Some(factory())

    @override
    def or_option_else(self, factory: Callable[[], Option[U]]) -> Option[U]:
        return factory()

    # ---- Async surface (Task 12) ------------------------------------------

    @override
    async def map_async(self, mapping: Callable[[Any], Awaitable[U]]) -> Option[U]:
        return self

    @override
    async def flat_map_async(self, mapping: Callable[[Any], Awaitable[Option[U]]]) -> Option[U]:
        return self

    @override
    async def filter_async(self, predicate: Callable[[Any], Awaitable[bool]]) -> Option[Never]:
        return self

    @override
    async def tap_async(self, fn: Callable[[Any], Awaitable[object]]) -> Self:
        return self

    @override
    async def match_async(
        self, *, some: Callable[[Any], Awaitable[R]], none: Callable[[], Awaitable[R]]
    ) -> R:
        return await none()

    @override
    async def match_some_async(self, action: Callable[[Any], Awaitable[None]]) -> None:
        pass

    @override
    async def match_none_async(self, action: Callable[[], Awaitable[None]]) -> None:
        await action()

    @override
    async def value_or_else_async(self, factory: Callable[[], Awaitable[U]]) -> U:
        return await factory()

    @override
    async def or_else_async(self, factory: Callable[[], Awaitable[U]]) -> Option[U]:
        return Some(await factory())

    @override
    async def or_option_else_async(self, factory: Callable[[], Awaitable[Option[U]]]) -> Option[U]:
        return await factory()


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
    def or_option(self, alternative: Either[U, F]) -> Either[T_co | U, E_co | F]: ...

    @abstractmethod
    def map(self, mapping: Callable[[T_co], U]) -> Either[U, E_co]: ...

    @abstractmethod
    def map_failure(self, mapping: Callable[[E_co], F]) -> Either[T_co, F]: ...

    @abstractmethod
    def flat_map(self, mapping: Callable[[T_co], Either[U, F]]) -> Either[U, E_co | F]: ...

    @abstractmethod
    def filter(
        self,
        predicate: Callable[[T_co], bool],
        *,
        exception: F | None = None,
        exception_else: Callable[[], F] | None = None,
    ) -> Either[T_co, E_co | F]: ...

    @abstractmethod
    def not_none(
        self,
        exception: F | None = None,
        *,
        exception_else: Callable[[], F] | None = None,
    ) -> Either[T_co, E_co | F]: ...

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

    # ---- Alternatives (Task 5) --------------------------------------------

    @abstractmethod
    def or_else(self, factory: Callable[[], U]) -> Either[T_co | U, E_co]: ...

    @abstractmethod
    def or_with(self, mapping: Callable[[E_co], U]) -> Either[T_co | U, E_co]: ...

    @abstractmethod
    def or_option_else(self, factory: Callable[[], Either[U, F]]) -> Either[T_co | U, E_co | F]: ...

    @abstractmethod
    def or_option_with(
        self, mapping: Callable[[E_co], Either[U, F]]
    ) -> Either[T_co | U, E_co | F]: ...

    # ---- Async surface (Task 12) ------------------------------------------

    @abstractmethod
    async def map_async(self, mapping: Callable[[T_co], Awaitable[U]]) -> Either[U, E_co]: ...

    @abstractmethod
    async def flat_map_async(
        self, mapping: Callable[[T_co], Awaitable[Either[U, F]]]
    ) -> Either[U, E_co | F]: ...

    @abstractmethod
    async def map_failure_async(
        self, mapping: Callable[[E_co], Awaitable[F]]
    ) -> Either[T_co, F]: ...

    @abstractmethod
    async def filter_async(
        self,
        predicate: Callable[[T_co], Awaitable[bool]],
        *,
        exception: F | None = None,
        exception_else: Callable[[], F] | None = None,
    ) -> Either[T_co, E_co | F]: ...

    @abstractmethod
    async def tap_async(self, fn: Callable[[T_co], Awaitable[object]]) -> Self: ...

    @abstractmethod
    async def tap_failure_async(self, fn: Callable[[E_co], Awaitable[object]]) -> Self: ...

    @abstractmethod
    async def match_async(
        self,
        *,
        some: Callable[[T_co], Awaitable[R]],
        none: Callable[[E_co], Awaitable[R]],
    ) -> R: ...

    @abstractmethod
    async def match_some_async(self, action: Callable[[T_co], Awaitable[None]]) -> None: ...

    @abstractmethod
    async def match_none_async(self, action: Callable[[E_co], Awaitable[None]]) -> None: ...

    @abstractmethod
    async def value_or_else_async(self, factory: Callable[[], Awaitable[U]]) -> T_co | U: ...

    @abstractmethod
    async def value_or_with_async(self, mapping: Callable[[E_co], Awaitable[U]]) -> T_co | U: ...

    @abstractmethod
    async def or_else_async(
        self, factory: Callable[[], Awaitable[U]]
    ) -> Either[T_co | U, E_co]: ...

    @abstractmethod
    async def or_with_async(
        self, mapping: Callable[[E_co], Awaitable[U]]
    ) -> Either[T_co | U, E_co]: ...

    @abstractmethod
    async def or_option_else_async(
        self, factory: Callable[[], Awaitable[Either[U, F]]]
    ) -> Either[T_co | U, E_co | F]: ...

    @abstractmethod
    async def or_option_with_async(
        self, mapping: Callable[[E_co], Awaitable[Either[U, F]]]
    ) -> Either[T_co | U, E_co | F]: ...

    # ---- from_awaitable (Task 12) -----------------------------------------

    @classmethod
    async def from_awaitable(
        cls,
        awaitable: Awaitable[T],
        catch: type[E] | tuple[type[E], ...] = Exception,
    ) -> Either[T, E]:
        """Lift an awaitable into Either, catching exceptions of type ``catch``.

        Args:
            awaitable: The coroutine or awaitable to run.
            catch: Exception type(s) to catch. Defaults to ``Exception``.

        Returns:
            ``Success(value)`` if the awaitable completes normally,
            ``Failure(exc)`` if an exception of type ``catch`` is raised.
        """
        try:
            value = await awaitable
        except BaseException as exc:  # narrowed below
            if isinstance(exc, catch if isinstance(catch, tuple) else (catch,)):
                return Failure(exc)  # type: ignore[arg-type]  # exc narrowed to catch type at runtime
            raise
        return Success(value)


@final
@total_ordering
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
        return hash(("either_option.Success", self.value))

    @override
    def __repr__(self) -> str:
        return f"Success({self.value!r})"

    # ---- Ordering (Task 8) ------------------------------------------------

    def __lt__(self, other: object) -> bool:
        """Success(x) < Success(y) iff x < y; Failure(_) < Success(_) always."""
        if isinstance(other, Success):
            return bool(self.value < other.value)  # type: ignore[operator]
        if isinstance(other, Failure):
            return False  # Success > Failure
        return NotImplemented

    # ---- Pickle (Task 8) --------------------------------------------------

    @override
    def __reduce__(self) -> tuple[Any, tuple[Any]]:
        return (Either.some, (self.value,))

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
        return self.value

    @override
    def or_value(self, alternative: U) -> Either[T_co | U, Never]:
        return self

    @override
    def or_option(self, alternative: Either[U, F]) -> Either[T_co | U, F]:
        return self

    # ---- Map / flat_map / tap (Task 6) ------------------------------------

    @override
    def map(self, mapping: Callable[[T_co], U]) -> Either[U, Never]:
        return Success(mapping(self.value))

    @override
    def map_failure(self, mapping: Callable[[Never], F]) -> Either[T_co, F]:
        return self

    @override
    def flat_map(self, mapping: Callable[[T_co], Either[U, F]]) -> Either[U, F]:
        return mapping(self.value)

    # ---- Filter / not_none (Task 7) ---------------------------------------

    @override
    def filter(
        self,
        predicate: Callable[[T_co], bool],
        *,
        exception: F | None = None,
        exception_else: Callable[[], F] | None = None,
    ) -> Either[T_co, F]:
        if exception is not None and exception_else is not None:
            msg = "filter() accepts exception or exception_else, not both"
            raise TypeError(msg)
        if predicate(self.value):
            return self
        if exception is not None:
            return Failure(exception)
        if exception_else is not None:
            return Failure(exception_else())
        msg = "filter() requires exception or exception_else when predicate fails"
        raise TypeError(msg)

    @override
    def not_none(
        self,
        exception: F | None = None,
        *,
        exception_else: Callable[[], F] | None = None,
    ) -> Either[T_co, F]:
        if self.value is not None:
            return self
        if exception is not None:
            return Failure(exception)
        if exception_else is not None:
            return Failure(exception_else())
        msg = "not_none() requires exception or exception_else when value is None"
        raise TypeError(msg)

    # ---- Interop (Task 7) ------------------------------------------------

    @override
    def without_exception(self) -> Option[T_co]:
        return Some(self.value)

    # ---- Tap (Task 6) ----------------------------------------------------

    @override
    def tap(self, fn: Callable[[T_co], object]) -> Self:
        _ = fn(self.value)
        return self

    @override
    def tap_failure(self, fn: Callable[[Never], object]) -> Self:
        return self

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

    # ---- Alternatives (Task 5) --------------------------------------------

    @override
    def or_else(self, factory: Callable[[], U]) -> Either[T_co | U, Never]:
        return self

    @override
    def or_with(self, mapping: Callable[[Any], U]) -> Either[T_co | U, Never]:
        return self

    @override
    def or_option_else(self, factory: Callable[[], Either[U, F]]) -> Either[T_co | U, F]:
        return self

    @override
    def or_option_with(self, mapping: Callable[[Any], Either[U, F]]) -> Either[T_co | U, F]:
        return self

    # ---- Async surface (Task 12) ------------------------------------------

    @override
    async def map_async(self, mapping: Callable[[T_co], Awaitable[U]]) -> Either[U, Never]:
        return Success(await mapping(self.value))

    @override
    async def flat_map_async(
        self, mapping: Callable[[T_co], Awaitable[Either[U, F]]]
    ) -> Either[U, F]:
        return await mapping(self.value)

    @override
    async def map_failure_async(self, mapping: Callable[[Never], Awaitable[F]]) -> Either[T_co, F]:
        return self

    @override
    async def filter_async(
        self,
        predicate: Callable[[T_co], Awaitable[bool]],
        *,
        exception: F | None = None,
        exception_else: Callable[[], F] | None = None,
    ) -> Either[T_co, F]:
        if exception is not None and exception_else is not None:
            msg = "filter_async() accepts exception or exception_else, not both"
            raise TypeError(msg)
        if await predicate(self.value):
            return self
        if exception is not None:
            return Failure(exception)
        if exception_else is not None:
            return Failure(exception_else())
        msg = "filter_async() requires exception or exception_else when predicate fails"
        raise TypeError(msg)

    @override
    async def tap_async(self, fn: Callable[[T_co], Awaitable[object]]) -> Self:
        _ = await fn(self.value)
        return self

    @override
    async def tap_failure_async(self, fn: Callable[[Never], Awaitable[object]]) -> Self:
        return self

    @override
    async def match_async(
        self,
        *,
        some: Callable[[T_co], Awaitable[R]],
        none: Callable[[Any], Awaitable[R]],
    ) -> R:
        return await some(self.value)

    @override
    async def match_some_async(self, action: Callable[[T_co], Awaitable[None]]) -> None:
        await action(self.value)

    @override
    async def match_none_async(self, action: Callable[[Any], Awaitable[None]]) -> None:
        pass

    @override
    async def value_or_else_async(self, factory: Callable[[], Awaitable[U]]) -> T_co | U:
        return self.value

    @override
    async def value_or_with_async(self, mapping: Callable[[Any], Awaitable[U]]) -> T_co | U:
        return self.value

    @override
    async def or_else_async(self, factory: Callable[[], Awaitable[U]]) -> Either[T_co | U, Never]:
        return self

    @override
    async def or_with_async(
        self, mapping: Callable[[Any], Awaitable[U]]
    ) -> Either[T_co | U, Never]:
        return self

    @override
    async def or_option_else_async(
        self, factory: Callable[[], Awaitable[Either[U, F]]]
    ) -> Either[T_co | U, F]:
        return self

    @override
    async def or_option_with_async(
        self, mapping: Callable[[Any], Awaitable[Either[U, F]]]
    ) -> Either[T_co | U, F]:
        return self


@final
@total_ordering
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
        return hash(("either_option.Failure", self.exception))

    @override
    def __repr__(self) -> str:
        return f"Failure({self.exception!r})"

    # ---- Ordering (Task 8) ------------------------------------------------

    def __lt__(self, other: object) -> bool:
        """Failure(e1) < Failure(e2) iff e1 < e2; Failure(_) < Success(_) always."""
        if isinstance(other, Failure):
            return bool(self.exception < other.exception)  # type: ignore[operator]
        if isinstance(other, Success):
            return True  # Failure < Success
        return NotImplemented

    # ---- Pickle (Task 8) --------------------------------------------------

    @override
    def __reduce__(self) -> tuple[Any, tuple[Any]]:
        return (Either.none, (self.exception,))

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
        return alternative

    @override
    def or_value(self, alternative: U) -> Either[U, E_co]:
        return Success(alternative)

    @override
    def or_option(self, alternative: Either[U, F]) -> Either[U, E_co | F]:
        return alternative

    # ---- Map / flat_map / tap (Task 6) ------------------------------------

    @override
    def map(self, mapping: Callable[[Any], U]) -> Either[U, E_co]:
        return self

    @override
    def map_failure(self, mapping: Callable[[E_co], F]) -> Either[Never, F]:
        return Failure(mapping(self.exception))

    @override
    def flat_map(self, mapping: Callable[[Any], Either[U, F]]) -> Either[U, E_co | F]:
        return self

    # ---- Filter / not_none (Task 7) ---------------------------------------

    @override
    def filter(
        self,
        predicate: Callable[[Any], bool],
        *,
        exception: F | None = None,
        exception_else: Callable[[], F] | None = None,
    ) -> Either[Never, E_co]:
        return self

    @override
    def not_none(
        self,
        exception: F | None = None,
        *,
        exception_else: Callable[[], F] | None = None,
    ) -> Either[Never, E_co]:
        return self

    # ---- Interop (Task 7) ------------------------------------------------

    @override
    def without_exception(self) -> Option[Never]:
        return Nothing()

    # ---- Tap (Task 6) ----------------------------------------------------

    @override
    def tap(self, fn: Callable[[Any], object]) -> Self:
        return self

    @override
    def tap_failure(self, fn: Callable[[E_co], object]) -> Self:
        _ = fn(self.exception)
        return self

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

    # ---- Alternatives (Task 5) --------------------------------------------

    @override
    def or_else(self, factory: Callable[[], U]) -> Either[U, E_co]:
        return Success(factory())

    @override
    def or_with(self, mapping: Callable[[E_co], U]) -> Either[U, E_co]:
        return Success(mapping(self.exception))

    @override
    def or_option_else(self, factory: Callable[[], Either[U, F]]) -> Either[U, E_co | F]:
        return factory()

    @override
    def or_option_with(self, mapping: Callable[[E_co], Either[U, F]]) -> Either[U, E_co | F]:
        return mapping(self.exception)

    # ---- Async surface (Task 12) ------------------------------------------

    @override
    async def map_async(self, mapping: Callable[[Any], Awaitable[U]]) -> Either[U, E_co]:
        return self

    @override
    async def flat_map_async(
        self, mapping: Callable[[Any], Awaitable[Either[U, F]]]
    ) -> Either[U, E_co | F]:
        return self

    @override
    async def map_failure_async(self, mapping: Callable[[E_co], Awaitable[F]]) -> Either[Never, F]:
        return Failure(await mapping(self.exception))

    @override
    async def filter_async(
        self,
        predicate: Callable[[Any], Awaitable[bool]],
        *,
        exception: F | None = None,
        exception_else: Callable[[], F] | None = None,
    ) -> Either[Never, E_co]:
        return self

    @override
    async def tap_async(self, fn: Callable[[Any], Awaitable[object]]) -> Self:
        return self

    @override
    async def tap_failure_async(self, fn: Callable[[E_co], Awaitable[object]]) -> Self:
        _ = await fn(self.exception)
        return self

    @override
    async def match_async(
        self,
        *,
        some: Callable[[Any], Awaitable[R]],
        none: Callable[[E_co], Awaitable[R]],
    ) -> R:
        return await none(self.exception)

    @override
    async def match_some_async(self, action: Callable[[Any], Awaitable[None]]) -> None:
        pass

    @override
    async def match_none_async(self, action: Callable[[E_co], Awaitable[None]]) -> None:
        await action(self.exception)

    @override
    async def value_or_else_async(self, factory: Callable[[], Awaitable[U]]) -> U:
        return await factory()

    @override
    async def value_or_with_async(self, mapping: Callable[[E_co], Awaitable[U]]) -> U:
        return await mapping(self.exception)

    @override
    async def or_else_async(self, factory: Callable[[], Awaitable[U]]) -> Either[U, E_co]:
        return Success(await factory())

    @override
    async def or_with_async(self, mapping: Callable[[E_co], Awaitable[U]]) -> Either[U, E_co]:
        return Success(await mapping(self.exception))

    @override
    async def or_option_else_async(
        self, factory: Callable[[], Awaitable[Either[U, F]]]
    ) -> Either[U, E_co | F]:
        return await factory()

    @override
    async def or_option_with_async(
        self, mapping: Callable[[E_co], Awaitable[Either[U, F]]]
    ) -> Either[U, E_co | F]:
        return await mapping(self.exception)


# ---------------------------------------------------------------------------
# Free functions (Task 6)
# ---------------------------------------------------------------------------


@overload
def flatten(opt: Option[Option[T]]) -> Option[T]: ...


@overload
def flatten(opt: Either[Either[T, E], E]) -> Either[T, E]: ...


def flatten(opt: Option[Option[T]] | Either[Either[T, E], E]) -> Option[T] | Either[T, E]:
    """Flatten a nested Option or Either one level.

    ``flatten(Some(Some(x)))`` → ``Some(x)``
    ``flatten(Some(Nothing()))`` → ``Nothing``
    ``flatten(Nothing())`` → ``Nothing``
    ``flatten(Success(Success(x)))`` → ``Success(x)``
    ``flatten(Success(Failure(e)))`` → ``Failure(e)``
    ``flatten(Failure(e))`` → ``Failure(e)``
    """
    if isinstance(opt, Some):
        return opt.value
    if isinstance(opt, Nothing):
        return opt
    if isinstance(opt, Success):
        return opt.value
    # Failure — pass through.
    # opt is Failure[Either[T,E], E]; the inner T-slot is unreachable (Never at
    # runtime), so returning it as Either[T, E] is sound.  Pyright can't express
    # "Failure[Either[T,E],E] <: Either[T,E]" because T_co is not yet narrowed.
    return opt  # type: ignore[return-value]  # Failure pass-through; see comment above
