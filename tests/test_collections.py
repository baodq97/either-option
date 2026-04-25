"""Tests for optional_python.collections — Task 10.

Each function is exercised with: empty input, single match, multiple elements,
no-match, and predicate variants where applicable.
"""

import itertools

from optional_python._core import Either, Failure, Option, Success, nothing, some
from optional_python.collections import (
    element_at_or_none,
    failures,
    first_or_none,
    get_or_none,
    last_or_none,
    single_or_none,
    successes,
    values,
)

# ---------------------------------------------------------------------------
# first_or_none
# ---------------------------------------------------------------------------


def test_first_or_none_empty_list() -> None:
    result: Option[int] = first_or_none([])
    assert result == nothing()
    assert result.is_none


def test_first_or_none_single_element() -> None:
    result = first_or_none([42])
    assert result == some(42)


def test_first_or_none_multiple_elements() -> None:
    result = first_or_none([1, 2, 3])
    assert result == some(1)


def test_first_or_none_generator() -> None:
    result = first_or_none(x for x in [10, 20, 30])
    assert result == some(10)


def test_first_or_none_predicate_match() -> None:
    result = first_or_none(range(100), predicate=lambda x: x == 50)
    assert result == some(50)


def test_first_or_none_predicate_first_match() -> None:
    result = first_or_none(range(100), predicate=lambda x: x > 50)
    assert result == some(51)


def test_first_or_none_predicate_no_match() -> None:
    result = first_or_none(range(100), predicate=lambda x: x == -1)
    assert result == nothing()


def test_first_or_none_predicate_empty() -> None:
    result: Option[int] = first_or_none([], predicate=lambda x: x == 1)
    assert result == nothing()


def test_first_or_none_predicate_single_match() -> None:
    result = first_or_none([0], predicate=lambda x: x == 0)
    assert result == some(0)


def test_first_or_none_predicate_single_no_match() -> None:
    result = first_or_none([0], predicate=lambda x: x == -1)
    assert result == nothing()


# ---------------------------------------------------------------------------
# last_or_none
# ---------------------------------------------------------------------------


def test_last_or_none_empty_list() -> None:
    result: Option[int] = last_or_none([])
    assert result == nothing()


def test_last_or_none_single_element() -> None:
    result = last_or_none([99])
    assert result == some(99)


def test_last_or_none_multiple_elements() -> None:
    result = last_or_none([1, 2, 3])
    assert result == some(3)


def test_last_or_none_generator() -> None:
    result = last_or_none(x for x in [10, 20, 30])
    assert result == some(30)


def test_last_or_none_predicate_match() -> None:
    result = last_or_none(range(100), predicate=lambda x: x == 50)
    assert result == some(50)


def test_last_or_none_predicate_last_match() -> None:
    # Last element > 50 in range(100) is 99
    result = last_or_none(range(100), predicate=lambda x: x > 50)
    assert result == some(99)


def test_last_or_none_predicate_last_below_50() -> None:
    # Last element < 50 in range(100) is 49
    result = last_or_none(range(100), predicate=lambda x: x < 50)
    assert result == some(49)


def test_last_or_none_predicate_no_match() -> None:
    result = last_or_none(range(100), predicate=lambda x: x == -1)
    assert result == nothing()


def test_last_or_none_predicate_empty() -> None:
    result: Option[int] = last_or_none([], predicate=lambda x: x == 1)
    assert result == nothing()


def test_last_or_none_predicate_single_match() -> None:
    result = last_or_none([0], predicate=lambda x: x == 0)
    assert result == some(0)


def test_last_or_none_predicate_single_no_match() -> None:
    result = last_or_none([0], predicate=lambda x: x == -1)
    assert result == nothing()


# ---------------------------------------------------------------------------
# single_or_none
# ---------------------------------------------------------------------------


def test_single_or_none_empty() -> None:
    result: Option[int] = single_or_none([])
    assert result == nothing()


def test_single_or_none_single_element() -> None:
    result = single_or_none([42])
    assert result == some(42)


def test_single_or_none_multiple_elements_returns_nothing() -> None:
    result = single_or_none([1, 2, 3])
    assert result == nothing()


def test_single_or_none_generator_single() -> None:
    result = single_or_none(x for x in [99])
    assert result == some(99)


def test_single_or_none_generator_multiple_returns_nothing() -> None:
    result = single_or_none(x for x in [1, 2])
    assert result == nothing()


def test_single_or_none_predicate_exactly_one_match() -> None:
    result = single_or_none(range(100), predicate=lambda x: x == 50)
    assert result == some(50)


def test_single_or_none_predicate_no_match() -> None:
    result = single_or_none(range(100), predicate=lambda x: x == -1)
    assert result == nothing()


def test_single_or_none_predicate_multiple_matches_returns_nothing() -> None:
    result = single_or_none(range(100), predicate=lambda x: x > 50)
    assert result == nothing()


def test_single_or_none_predicate_multiple_matches_below_50() -> None:
    result = single_or_none(range(100), predicate=lambda x: x < 50)
    assert result == nothing()


def test_single_or_none_predicate_empty() -> None:
    result: Option[int] = single_or_none([], predicate=lambda x: x == 1)
    assert result == nothing()


def test_single_or_none_predicate_single_match_value() -> None:
    result = single_or_none([0], predicate=lambda x: x == 0)
    assert result == some(0)


def test_single_or_none_predicate_single_no_match() -> None:
    result = single_or_none([0], predicate=lambda x: x == -1)
    assert result == nothing()


# ---------------------------------------------------------------------------
# element_at_or_none
# ---------------------------------------------------------------------------


def test_element_at_or_none_negative_index() -> None:
    result = element_at_or_none([1, 2, 3], -1)
    assert result == nothing()


def test_element_at_or_none_in_range() -> None:
    data = list(range(10))
    for i in range(10):
        assert element_at_or_none(data, i) == some(i)


def test_element_at_or_none_out_of_range() -> None:
    result = element_at_or_none([1, 2, 3], 10)
    assert result == nothing()


def test_element_at_or_none_out_of_range_exact_length() -> None:
    data = list(range(100))
    result = element_at_or_none(data, 100)
    assert result == nothing()


def test_element_at_or_none_empty_list() -> None:
    result: Option[int] = element_at_or_none([], 0)
    assert result == nothing()


def test_element_at_or_none_generator_in_range() -> None:
    # Generator does not support __len__ or __getitem__
    gen = (x for x in range(10))
    result = element_at_or_none(gen, 5)
    assert result == some(5)


def test_element_at_or_none_generator_out_of_range() -> None:
    gen = (x for x in range(5))
    result = element_at_or_none(gen, 10)
    assert result == nothing()


def test_element_at_or_none_generator_negative() -> None:
    gen = (x for x in range(5))
    result = element_at_or_none(gen, -1)
    assert result == nothing()


def test_element_at_or_none_single_element_at_zero() -> None:
    result = element_at_or_none([0], 0)
    assert result == some(0)


def test_element_at_or_none_single_element_at_two() -> None:
    result = element_at_or_none([0], 2)
    assert result == nothing()


# ---------------------------------------------------------------------------
# get_or_none
# ---------------------------------------------------------------------------


def test_get_or_none_dict_present_key() -> None:
    data = {"a": 1, "b": 2}
    result = get_or_none(data, "a")
    assert result == some(1)


def test_get_or_none_dict_missing_key() -> None:
    data = {"a": 1}
    result = get_or_none(data, "z")
    assert result == nothing()


def test_get_or_none_list_of_tuples_present() -> None:
    data = [("a", 1), ("b", 2), ("c", 3)]
    result = get_or_none(data, "b")
    assert result == some(2)


def test_get_or_none_list_of_tuples_missing() -> None:
    data = [("a", 1), ("b", 2)]
    result = get_or_none(data, "z")
    assert result == nothing()


def test_get_or_none_empty_dict() -> None:
    result: Option[int] = get_or_none({}, "key")
    assert result == nothing()


def test_get_or_none_empty_list_of_tuples() -> None:
    result: Option[int] = get_or_none([], "key")
    assert result == nothing()


def test_get_or_none_integer_keys_dict() -> None:
    data = {i: str(i) for i in range(50, 100)}
    for i in range(50, 100):
        assert get_or_none(data, i) == some(str(i))
    for i in range(-50, 50):
        assert get_or_none(data, i) == nothing()


# ---------------------------------------------------------------------------
# values
# ---------------------------------------------------------------------------


def test_values_mixed_options() -> None:
    opts: list[Option[str]] = [some("a"), nothing(), nothing(), some("b"), nothing(), some("c")]
    result = list(values(opts))
    assert result == ["a", "b", "c"]


def test_values_empty_list() -> None:
    empty: list[Option[int]] = []
    result = list(values(empty))
    assert result == []


def test_values_all_some() -> None:
    opts: list[Option[int]] = [some(1), some(2), some(3)]
    result = list(values(opts))
    assert result == [1, 2, 3]


def test_values_all_nothing() -> None:
    opts: list[Option[int]] = [nothing(), nothing(), nothing()]
    result = list(values(opts))
    assert result == []


def test_values_single_some() -> None:
    result = list(values([some("x")]))
    assert result == ["x"]


def test_values_single_nothing() -> None:
    result = list(values([nothing()]))
    assert result == []


def test_values_is_lazy() -> None:
    """values() must be a lazy generator — we can islice an infinite source."""

    def infinite_options() -> "itertools.chain[Option[int]]":
        # Alternates some(0), nothing(), some(1), nothing(), …
        return itertools.chain.from_iterable((some(i), nothing()) for i in itertools.count())

    result: list[int] = list(itertools.islice(values(infinite_options()), 5))
    assert result == [0, 1, 2, 3, 4]


# ---------------------------------------------------------------------------
# successes
# ---------------------------------------------------------------------------


def test_successes_mixed() -> None:
    eithers: list[Either[str, str]] = [
        Success("a"),
        Failure("err1"),
        Failure("err2"),
        Success("b"),
        Success("c"),
    ]
    result = list(successes(eithers))
    assert result == ["a", "b", "c"]


def test_successes_empty() -> None:
    empty: list[Either[int, str]] = []
    result = list(successes(empty))
    assert result == []


def test_successes_all_success() -> None:
    eithers: list[Either[int, str]] = [Success(1), Success(2), Success(3)]
    result = list(successes(eithers))
    assert result == [1, 2, 3]


def test_successes_all_failure() -> None:
    eithers: list[Either[int, str]] = [Failure("x"), Failure("y")]
    result = list(successes(eithers))
    assert result == []


def test_successes_single_success() -> None:
    result = list(successes([Success(42)]))
    assert result == [42]


def test_successes_single_failure() -> None:
    result = list(successes([Failure("e")]))
    assert result == []


def test_successes_is_lazy() -> None:
    """successes() must be a lazy generator."""

    def infinite_eithers() -> "itertools.chain[Either[int, str]]":
        return itertools.chain.from_iterable((Success(i), Failure("e")) for i in itertools.count())

    result: list[int] = list(itertools.islice(successes(infinite_eithers()), 5))
    assert result == [0, 1, 2, 3, 4]


# ---------------------------------------------------------------------------
# failures
# ---------------------------------------------------------------------------


def test_failures_mixed() -> None:
    eithers: list[Either[str, str]] = [
        Failure("a"),
        Success("val"),
        Success("val"),
        Failure("b"),
        Failure("c"),
    ]
    result = list(failures(eithers))
    assert result == ["a", "b", "c"]


def test_failures_empty() -> None:
    empty: list[Either[int, str]] = []
    result = list(failures(empty))
    assert result == []


def test_failures_all_failure() -> None:
    eithers: list[Either[int, str]] = [Failure("x"), Failure("y"), Failure("z")]
    result = list(failures(eithers))
    assert result == ["x", "y", "z"]


def test_failures_all_success() -> None:
    eithers: list[Either[int, str]] = [Success(1), Success(2)]
    result = list(failures(eithers))
    assert result == []


def test_failures_single_failure() -> None:
    result = list(failures([Failure("err")]))
    assert result == ["err"]


def test_failures_single_success() -> None:
    result = list(failures([Success(1)]))
    assert result == []


def test_failures_is_lazy() -> None:
    """failures() must be a lazy generator."""

    def infinite_eithers() -> "itertools.chain[Either[int, str]]":
        return itertools.chain.from_iterable(
            (Failure(f"e{i}"), Success(i)) for i in itertools.count()
        )

    result: list[str] = list(itertools.islice(failures(infinite_eithers()), 5))
    assert result == ["e0", "e1", "e2", "e3", "e4"]


# ---------------------------------------------------------------------------
# successes and failures from the same source list (both can run)
# ---------------------------------------------------------------------------


def test_successes_and_failures_from_same_list() -> None:
    """Both successes() and failures() can consume a shared list source."""
    source: list[Either[int, str]] = [
        Success(1),
        Failure("a"),
        Success(2),
        Failure("b"),
        Success(3),
    ]
    assert list(successes(source)) == [1, 2, 3]
    assert list(failures(source)) == ["a", "b"]
