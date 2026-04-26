"""Collections helpers + the unsafe boundary.

Run:
    uv run python examples/04_collections_and_unsafe.py
"""

from __future__ import annotations

from either_option import Either, nothing, some
from either_option.collections import (
    element_at_or_none,
    failures,
    first_or_none,
    get_or_none,
    single_or_none,
    successes,
    values,
)
from either_option.unsafe import OptionValueMissingError, value_or_default, value_or_failure


def main() -> None:
    items = [1, 2, 3, 4, 5]

    # first_or_none, last_or_none, single_or_none, element_at_or_none.
    print("first_or_none(>3):", first_or_none(items, lambda x: x > 3))
    print("element_at_or_none(2):", element_at_or_none(items, 2))
    print("element_at_or_none(99):", element_at_or_none(items, 99))
    print("single_or_none(==3):", single_or_none(items, lambda x: x == 3))
    print("single_or_none(>0):", single_or_none(items, lambda x: x > 0))  # multi -> Nothing

    # get_or_none from dict and from list-of-tuples.
    d = {"a": 1, "b": 2}
    print("get_or_none(d, 'a'):", get_or_none(d, "a"))
    print("get_or_none(d, 'z'):", get_or_none(d, "z"))
    pairs = [("x", 10), ("y", 20)]
    print("get_or_none(pairs, 'x'):", get_or_none(pairs, "x"))

    # values / successes / failures: stream-flatten collections of Options/Eithers.
    options = [some(1), some(2), some(3)]
    print("values:", list(values(options)))

    eithers: list[Either[int, str]] = [
        Either.some(1),
        Either.none("err-a"),
        Either.some(2),
        Either.none("err-b"),
    ]
    print("successes:", list(successes(eithers)))
    print("failures:", list(failures(eithers)))

    # The opt-in unsafe boundary.
    print("value_or_default(some(7)):", value_or_default(some(7)))
    print("value_or_failure(some(7)):", value_or_failure(some(7)))

    # value_or_failure raises on absent — this is the explicit "unsafe" extraction.
    try:
        value_or_failure(nothing(), message="no value here")
    except OptionValueMissingError as exc:
        print("caught:", exc)


if __name__ == "__main__":
    main()
