# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

This is a Python library (`optional-python`) supporting **Python 3.10+**, using the `uv_build` backend, src-layout, and `py.typed` marker. The minimum is 3.10 deliberately — the bulk of production Python is on 3.10/3.11, and a library exists to be installed, not to chase the newest interpreter.

Below are rules to NOT violate when working in this repo. They are tuned to ship a top-quality, broadly-installable Python library.

## Tooling — DO NOT

- Do NOT invoke `python`, `python3`, `pip`, `pytest`, `ruff`, `mypy`, `pyright`, or any tool from the project venv directly. Always go through `uv run …` (or `uvx` for one-shots). The interpreter on PATH is not guaranteed to match `.python-version`.
- Do NOT run `pip install` to add a dependency. Use `uv add <pkg>` (and `uv add --dev <pkg>` for dev tools); never hand-edit `[project.dependencies]` to introduce a new package.
- Do NOT introduce `setup.py`, `setup.cfg`, `requirements.txt`, `Pipfile`, `poetry.lock`, or `tox.ini`. The single source of truth is `pyproject.toml` + `uv.lock`.
- Do NOT swap the build backend away from `uv_build`.
- Do NOT raise `requires-python` above `>=3.10` casually. Bumping the floor is a breaking change for downstream users — only do it for a concrete, justified reason (a dep dropped support, a needed stdlib feature, etc.) and call it out in CHANGELOG.
- Do NOT lower `.python-version` to match `requires-python`'s floor either. **Develop and test on the minimum supported version (3.10)** so 3.11+/3.12+/3.13+/3.14+ syntax can't slip in by accident. CI should additionally test the newest stable.
- Do NOT delete `src/optional_python/py.typed`. It is the PEP 561 marker that tells downstream type checkers this package ships types.
- Do NOT ship `uv.lock` as a runtime artifact or read it from library code; libraries pin via `pyproject.toml`, applications pin via the lockfile.

## Dependencies — DO NOT

- Do NOT add a runtime dependency without a concrete in-tree caller. A library's blast radius is its dependency closure; every added dep is a downstream conflict risk.
- Do NOT add upper version caps (`<2`, `<3`, `~=`) on runtime deps unless you have evidence of a specific incompatibility. Caps cause solver deadlocks for downstream users — prefer `>=` floors.
- Do NOT pull in heavyweight frameworks (FastAPI, Django, pandas, numpy, pydantic, requests) just for a small piece of functionality — prefer stdlib or a tiny focused dep.
- Do NOT mix runtime and dev deps. Test/lint/type-check tooling goes in a `[dependency-groups]` group (`dev`), never in `[project.dependencies]`.
- Do NOT depend on a package that itself has no `py.typed` marker for public API surface — it'll force `Any` to leak through your types.
- Do NOT depend on a package whose own `requires-python` is stricter than ours (e.g. a dep that needs `>=3.12`) — it silently breaks our 3.10/3.11 support.

## Public API — DO NOT

- Do NOT export a name from `optional_python/__init__.py` without adding it to `__all__`. If `__all__` is missing, every non-underscore name becomes part of the public API by accident.
- Do NOT put non-trivial logic, side effects, network calls, or heavy imports in `__init__.py`. Import time matters; users pay for it on every `import optional_python`.
- Do NOT expose a third-party type (e.g. `httpx.Response`, `pydantic.BaseModel`) in a public signature without re-exporting it. Hidden transitive types break IDE/typechecker UX for callers.
- Do NOT hardcode `__version__` as a string literal. Read it from installed metadata (`importlib.metadata.version("optional-python")`) so wheel and source agree.
- Do NOT make a backwards-incompatible change (rename, remove, type-narrow a parameter, change return type, raise a new exception, change default) without a major version bump. Additive only on minor.
- Do NOT add a CLI entry point, `__main__.py`, or `[project.scripts]` — this is a library, not an application.

## Python version compatibility — DO NOT (3.10 floor)

These features exist but are NOT in 3.10. Do not use them in `src/` unconditionally:

- Do NOT use `tomllib` (stdlib in 3.11+). For 3.10 fall back to the `tomli` package, or avoid TOML parsing in library code entirely.
- Do NOT use `typing.Self` directly imported from `typing` (3.11+). Import from `typing_extensions` if you actually need it.
- Do NOT use `typing.Never`, `typing.assert_type`, `typing.assert_never`, `typing.LiteralString`, `typing.NotRequired`, `typing.Required` from `typing` (3.11+). Use `typing_extensions`.
- Do NOT use `except*` / `ExceptionGroup` / `BaseExceptionGroup` (3.11+).
- Do NOT use the new generic syntax `def f[T](x: T)`, `class Foo[T]:`, or `type Alias = ...` (PEP 695, 3.12+). Use the classic `TypeVar` + `Generic[T]` form.
- Do NOT use `typing.override`, `typing.TypeIs`, `typing.ReadOnly`, `warnings.deprecated` from stdlib (3.12+/3.13+). Use `typing_extensions`.
- Do NOT use PEP 696 TypeVar defaults (`TypeVar("T", default=int)`) from stdlib `typing` (3.13+). Use `typing_extensions`.
- Do NOT use f-string features that require 3.12+ (multi-line expressions, reusing quote characters, comments inside braces). Keep f-strings 3.10-compatible.
- Do NOT rely on PEP 703 free-threaded builds (3.13+ experimental, 3.14 broader). The library must work correctly under the standard GIL build on 3.10.
- Do NOT rely on PEP 649 deferred evaluation of annotations (default in 3.14). Treat annotations as evaluated at definition time on 3.10–3.13.
- Do NOT use `datetime.UTC` (3.11+). Use `datetime.timezone.utc`.
- Do NOT use `asyncio.TaskGroup` (3.11+) or `asyncio.timeout()` (3.11+) without an `if sys.version_info` guard or a backport.
- Do NOT add `from __future__ import annotations` blanket-style across the codebase. It works on 3.10 but it changes runtime annotation visibility (`get_type_hints`, dataclasses-with-strings, pydantic v1 patterns) — only add it to a file when there's a concrete forward-reference need.

## Typing — DO NOT

- Do NOT use `typing.List`, `typing.Dict`, `typing.Tuple`, `typing.Set`, `typing.Type`, `typing.FrozenSet`. Use the builtin generics (`list[X]`, `dict[K, V]`, `tuple[X, ...]`, `set[X]`, `type[X]`, `frozenset[X]`) — these run natively on 3.10+ (PEP 585).
- Do NOT use `typing.Optional[X]` or `typing.Union[A, B]`. Use `X | None` and `A | B` — runtime-supported on 3.10+ (PEP 604).
- Do NOT type a public parameter or return as `Any`, `object`, or untyped `dict`/`list`. If the shape is dynamic, model it (`TypedDict`, `Protocol`, generics).
- Do NOT use `cast()` to silence a type error. Fix the type, narrow with `isinstance`/`assert`, or use a `TypeGuard` (available from `typing` on 3.10+).
- Do NOT add `# type: ignore` without a specific error code (`# type: ignore[arg-type]`) and a one-line comment explaining why.

## Code style — DO NOT

- Do NOT use `assert` for runtime validation in library code. Asserts are stripped under `python -O`; raise `ValueError`/`TypeError` instead. Asserts are fine inside tests.
- Do NOT use mutable defaults (`def f(x=[])`, `def f(x={})`). Use `None` and assign inside the body.
- Do NOT catch bare `Exception` or `BaseException` to swallow errors. Catch the narrowest type, and never catch `KeyboardInterrupt` / `SystemExit` accidentally.
- Do NOT raise a bare `Exception(...)`. Use a domain-specific subclass or a precise stdlib exception.
- Do NOT use `os.path` for path manipulation in new code. Use `pathlib.Path`.
- Do NOT use `print()` for diagnostics in library code. Use `logging.getLogger(__name__)` and never call `logging.basicConfig()` from library code — that's the application's job.
- Do NOT call blocking I/O (`time.sleep`, `requests.get`, `open()` for large files, subprocess) from inside an `async def`. Use the async-native equivalent or `asyncio.to_thread` (3.9+, fine on 3.10).
- Do NOT use relative imports that cross sibling subpackages (`from ..other_pkg import x`). Use absolute imports rooted at `optional_python.…`.
- Do NOT silence a linter finding with `# noqa` without a code (`# noqa: E501`) — and prefer fixing the issue.
- Do NOT shadow stdlib or builtin names (`id`, `type`, `list`, `dict`, `input`, `format`, `filter`, `map`).

## Tests — DO NOT

- Do NOT put tests inside `src/optional_python/`. Tests live in a top-level `tests/` directory; only shipped code goes under `src/`.
- Do NOT rely on import order, filesystem CWD, network access, real time (`time.sleep`, `datetime.now()`), or environment variables in tests. Inject a clock, fake the network, use `tmp_path`/`monkeypatch`.
- Do NOT share mutable state between tests via module globals or class attributes. Each test must be independently runnable in any order.
- Do NOT use `unittest.TestCase` style for new tests in this repo. Use plain `pytest` functions + fixtures.
- Do NOT skip a version of Python in the test matrix that is in `requires-python`. Every supported minor (3.10, 3.11, 3.12, 3.13, 3.14) must be exercised in CI.

## Concurrency — DO NOT

- Do NOT call `asyncio.get_event_loop()` (deprecated). Use `asyncio.get_running_loop()` inside coroutines and `asyncio.run()` at the entry point.
- Do NOT introduce module-level locks or rely on the GIL for atomicity of compound operations on shared mutable state — even on 3.10, multi-statement read-modify-write across threads is unsafe, and the library should remain correct on free-threaded builds users may try later.

## Git / release — DO NOT

- Do NOT commit `.venv/`, `__pycache__/`, `*.pyc`, `dist/`, `build/`, `*.egg-info/`, or anything already covered by `.gitignore`.
- Do NOT bump `version` in `pyproject.toml` and edit code in the same commit. Version bumps are their own commit so release tags are clean.
