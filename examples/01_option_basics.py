"""Option basics: presence/absence, factories, fluent combinators.

Run:
    uv run python examples/01_option_basics.py
"""

from __future__ import annotations

from either_option import Nothing, Option, Some, nothing, some
from either_option.extensions import some_not_none, some_when


def find_user(uid: int) -> Option[str]:
    """Tiny in-memory 'lookup' returning Some(name) or Nothing()."""
    db = {1: "alice", 2: "bob"}
    return some_not_none(db.get(uid))


def main() -> None:
    # 1. Construct an Option two ways.
    a: Option[int] = some(10)
    b: Option[int] = nothing()

    # 2. Truthiness: Some is truthy, Nothing is falsy.
    print("bool(a) =", bool(a), "  bool(b) =", bool(b))

    # 3. Defaults: value_or never raises.
    print("a.value_or(0) =", a.value_or(0))
    print("b.value_or(0) =", b.value_or(0))

    # 4. Fluent map/filter chain — only runs on Some.
    pipeline = some(7).map(lambda x: x * 2).filter(lambda x: x > 10).map(lambda x: f"v={x}")
    print("pipeline =", pipeline)

    # 5. Pattern matching with __match_args__.
    for opt in (find_user(1), find_user(2), find_user(99)):
        match opt:
            case Some(name):
                print(f"found: {name}")
            case Nothing():
                print("missing")
            case _:
                print("unreachable: Option is sealed")

    # 6. Iteration: Option is a 0-or-1-element sequence.
    print("list(some(5)) =", list(some(5)))
    print("list(nothing()) =", list(nothing()))

    # 7. some_when: keep value only if predicate holds.
    even_only = some_when(8, lambda x: x % 2 == 0)
    odd_only = some_when(7, lambda x: x % 2 == 0)
    print("some_when(8, even) =", even_only)
    print("some_when(7, even) =", odd_only)


if __name__ == "__main__":
    main()
