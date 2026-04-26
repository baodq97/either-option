"""__iter__, to_iterable, __contains__, contains(), exists() — spec §3.5."""

from either_option import Either, nothing, some


def test_some_iterates_one_element() -> None:
    assert list(some(10)) == [10]


def test_nothing_iterates_zero_elements() -> None:
    assert list(nothing()) == []


def test_success_iterates_one_element() -> None:
    assert list(Either.some(10)) == [10]


def test_failure_iterates_zero_elements() -> None:
    assert list(Either.none("err")) == []


def test_some_to_iterable_one_element() -> None:
    assert list(some(10).to_iterable()) == [10]


def test_nothing_to_iterable_zero() -> None:
    assert list(nothing().to_iterable()) == []


def test_for_loop_executes_once_for_some() -> None:
    seen = list(some(7))
    assert seen == [7]


def test_for_loop_skips_nothing() -> None:
    seen = list(nothing())
    assert seen == []


def test_comprehension_over_some() -> None:
    assert [x * 2 for x in some(5)] == [10]


def test_in_operator_some_match() -> None:
    assert 10 in some(10)


def test_in_operator_some_no_match() -> None:
    assert 11 not in some(10)


def test_in_operator_nothing() -> None:
    assert 0 not in nothing()


def test_contains_method_some_match() -> None:
    assert some(10).contains(10) is True


def test_contains_method_some_no_match() -> None:
    assert some(10).contains(11) is False


def test_contains_method_nothing() -> None:
    assert nothing().contains(10) is False


def test_exists_some_predicate_true() -> None:
    assert some(10).exists(lambda x: x > 5) is True


def test_exists_some_predicate_false() -> None:
    assert some(10).exists(lambda x: x > 100) is False


def test_exists_nothing_always_false() -> None:
    assert nothing().exists(lambda _: True) is False
