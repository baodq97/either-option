"""Either: Railway-Oriented Programming with explicit failure types.

Run:
    uv run python examples/02_either_rop.py
"""

from __future__ import annotations

from dataclasses import dataclass

from optional_python import Either, Failure, Success
from optional_python.safe import call_safe, safe


@dataclass
class User:
    """A toy user record."""

    name: str
    age: int


# ---- Synchronous railway pipeline ----------------------------------------


@safe(catch=ValueError)
def parse_age(raw: str) -> int:
    """Lift int() into an Either; ValueError -> Failure."""
    return int(raw)


def validate_age(age: int) -> Either[int, str]:
    """Plain Either-returning validator."""
    if age < 0:
        return Either.none("age must be non-negative")
    if age > 130:
        return Either.none("age must be realistic")
    return Either.some(age)


def to_user(name: str, age: int) -> Either[User, str]:
    return Either.some(User(name=name, age=age))


def make_user(name: str, raw_age: str) -> Either[User, str]:
    """The full pipeline: parse → validate → construct."""
    return (
        parse_age(raw_age)
        .map_failure(lambda e: f"invalid age: {e}")
        .flat_map(validate_age)
        .flat_map(lambda age: to_user(name, age))
    )


def main() -> None:
    # Happy path:
    print(make_user("alice", "30"))

    # Parse failure short-circuits the rest of the chain:
    print(make_user("bob", "thirty"))

    # Validation failure short-circuits subsequent steps:
    print(make_user("eve", "-3"))

    # tap / tap_failure for instrumentation without breaking the chain:
    audit_log: list[str] = []
    final = (
        make_user("alice", "30")
        .tap(lambda u: audit_log.append(f"created {u.name}"))
        .tap_failure(lambda e: audit_log.append(f"failed: {e}"))
    )
    print("final =", final)
    print("audit_log =", audit_log)

    # Pattern matching to extract a value or default:
    match make_user("zara", "25"):
        case Success(user):
            print(f"hello {user.name}, age {user.age}")
        case Failure(err):
            print(f"could not create user: {err}")
        case _:
            print("unreachable: Either is sealed")

    # call_safe: one-shot lift without a decorator.
    result = call_safe(int, "not-a-number", catch=ValueError)
    print("call_safe result:", result)


if __name__ == "__main__":
    main()
