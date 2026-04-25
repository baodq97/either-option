"""Async ROP: chain awaitable steps with Either.

Run:
    uv run python examples/03_async_pipeline.py
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass

from optional_python import Either, Failure, Success
from optional_python.safe import safe_async


@dataclass
class Profile:
    """Toy profile record."""

    user_id: int
    handle: str
    posts: int


# ---- Simulated async sources --------------------------------------------


@safe_async(catch=KeyError)
async def fetch_user_id(handle: str) -> int:
    """Look up a user by handle; raises KeyError when missing."""
    await asyncio.sleep(0)  # simulate I/O
    db = {"alice": 1, "bob": 2}
    return db[handle]


@safe_async(catch=ValueError)
async def fetch_post_count(uid: int) -> int:
    """Count posts; raises ValueError on uid <= 0."""
    await asyncio.sleep(0)
    if uid <= 0:
        msg = "uid must be positive"
        raise ValueError(msg)
    return uid * 7  # toy formula


async def build_profile(handle: str, uid: int, posts: int) -> Profile:
    return Profile(user_id=uid, handle=handle, posts=posts)


# ---- The pipeline --------------------------------------------------------


async def load_profile(handle: str) -> Either[Profile, Exception]:
    """Run an async ROP chain.

    Each step's failure short-circuits the rest. The chain reads top-to-bottom
    in plain ``await`` style — no monad transformer required.
    """
    user_id_e: Either[int, KeyError] = await fetch_user_id(handle)

    posts_e = await user_id_e.flat_map_async(fetch_post_count)

    audit: list[str] = []
    posts_e = await posts_e.tap_async(
        lambda p: _audit_async(audit, f"fetched posts: {p}"),
    )
    posts_e = await posts_e.tap_failure_async(
        lambda e: _audit_async(audit, f"pipeline error: {e}"),
    )

    profile_e = await user_id_e.flat_map_async(
        lambda uid: _zip_into_profile(handle, uid, posts_e),
    )

    print("audit:", audit)
    return profile_e


async def _audit_async(log: list[str], message: str) -> None:
    log.append(message)


async def _zip_into_profile(
    handle: str, uid: int, posts_e: Either[int, Exception]
) -> Either[Profile, Exception]:
    """Combine handle/uid with the post-count Either."""
    return await posts_e.map_async(lambda posts: build_profile(handle, uid, posts))


# ---- Demo ----------------------------------------------------------------


async def main() -> None:
    # Happy path:
    result = await load_profile("alice")
    match result:
        case Success(profile):
            print("ok:", profile)
        case Failure(err):
            print("oops:", err)
        case _:
            print("unreachable: Either is sealed")

    print()

    # Missing user — KeyError caught and short-circuits.
    result = await load_profile("nobody")
    match result:
        case Success(profile):
            print("ok:", profile)
        case Failure(err):
            print("oops:", repr(err))
        case _:
            print("unreachable: Either is sealed")

    print()

    # Either.from_awaitable: lift any awaitable into Either at the boundary.
    bare: Either[int, Exception] = await Either.from_awaitable(_raise_async())
    print("from_awaitable:", bare)


async def _raise_async() -> int:
    msg = "boom from awaitable"
    raise RuntimeError(msg)


if __name__ == "__main__":
    asyncio.run(main())
