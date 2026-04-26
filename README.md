# either-option

[![CI](https://github.com/baodq97/either-option/actions/workflows/ci.yml/badge.svg)](https://github.com/baodq97/either-option/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/either-option.svg)](https://pypi.org/project/either-option/)
[![Python](https://img.shields.io/pypi/pyversions/either-option.svg)](https://pypi.org/project/either-option/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**Railway-Oriented Programming for Python.** A typed, sealed `Option[T]` and
`Either[T, E]` with sync **and async** combinators. Pyright `--strict` clean,
100% line + branch coverage, 545 tests.

A Python port of the C# [`Optional`](https://github.com/nlkl/Optional) library
by Nils Lück, reframed for **ROP** in idiomatic Python 3.10+.

## Why this library

There are several `Optional`-flavoured packages on PyPI. `either-option` is the
only one that ships **all** of:

| Feature | `either-option` | `py-optional` | `optional-python` (ponytailer) | `optional` (alex, 2015) |
|---|:-:|:-:|:-:|:-:|
| `Option[T]` (Some / Nothing) | ✓ | ✓ | ✓ | ✓ |
| `Either[T, E]` (Success / Failure) | ✓ | — | partial (`Try`) | — |
| `async` combinators (`map_async`, `flat_map_async`, …) | ✓ | — | — | — |
| Sealed `match` / pattern matching | ✓ | — | — | — |
| `@safe` / `@safe_async` decorators | ✓ | — | — | — |
| Collection helpers (`first_or_none`, `successes`, …) | ✓ | — | — | — |
| Pyright `--strict` clean | ✓ | mypy | — | — |
| 100% line + branch coverage | ✓ | partial | — | — |
| Active | ✓ | ✓ | abandoned | abandoned |

## Install

```bash
pip install either-option
# or
uv add either-option
```

Requires Python **3.10+** (tested on 3.10–3.14).

## Quick start

```python
from either_option import Either, Failure, Success
from either_option.safe import safe

@safe(catch=ValueError)
def parse_age(raw: str) -> int:
    return int(raw)

def validate(age: int) -> Either[int, str]:
    return Either.some(age) if 0 <= age <= 130 else Either.none("out of range")

result = (
    parse_age("42")
    .map_failure(lambda e: f"parse: {e}")
    .flat_map(validate)
)

match result:
    case Success(age): print(f"got {age}")
    case Failure(err): print(f"oops: {err}")
    case _: pass  # Either is sealed
```

## What's in the box

```python
from either_option import (
    Option, Some, Nothing, some, nothing,    # presence/absence
    Either, Success, Failure, flatten,       # success/failure + flatten()
    OptionValueMissingError,                 # raised by opt-in unsafe getters
)
from either_option.safe import safe, safe_async, call_safe
from either_option.extensions import some_not_none, some_when, none_when, from_optional
from either_option.collections import (
    first_or_none, last_or_none, single_or_none, element_at_or_none, get_or_none,
    values, successes, failures,
)
from either_option.unsafe import value_or_failure, value_or_default, to_optional
```

**Sync combinators:** `map`, `flat_map`, `filter`, `tap`, `match`, `value_or`,
`value_or_else`, `value_or_with`, `or_else`, `or_with`, `or_option_else`,
`or_option_with`, `map_failure`, `flat_map_failure`, `to_iterable`, `contains`,
`exists`.

**Async variants:** every method above has an `_async` counterpart accepting
async callables (`map_async`, `flat_map_async`, `filter_async`,
`value_or_else_async`, `or_with_async`, …), plus
`Either.from_awaitable(awaitable, catch=...)` to lift coroutines.

## Examples

Runnable end-to-end demos in `examples/`:

- `examples/01_option_basics.py` — `Option`, factories, fluent combinators, pattern matching.
- `examples/02_either_rop.py` — `Either` ROP pipeline with `@safe`, `map_failure`, `tap`.
- `examples/03_async_pipeline.py` — async ROP with `map_async`, `flat_map_async`, `Either.from_awaitable`.
- `examples/04_collections_and_unsafe.py` — collection helpers + opt-in unsafe extraction.

```bash
uv run python examples/01_option_basics.py
uv run python examples/02_either_rop.py
uv run python examples/03_async_pipeline.py
uv run python examples/04_collections_and_unsafe.py
```

---

## Development

### Prerequisites

| Tool | Min version | Why | Install |
|---|---|---|---|
| **Python** | 3.10 | Library targets `>=3.10`. `uv` installs the right interpreter for you on first sync. | See `uv` below — it installs Python 3.10 automatically. |
| **uv** | 0.11 | Package manager, build backend (`uv_build`), test runner, and Python installer. The repo pins `required-version = ">=0.11"` so older versions are rejected. | **Win:** `powershell -ExecutionPolicy Bypass -c "irm https://astral.sh/uv/install.ps1 \| iex"`<br>**macOS / Linux:** `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| **Git** | any recent | Clone repo + (optionally) reference upstream C# source. | Platform package manager. |

### First-time setup

```bash
git clone https://github.com/baodq97/either-option
cd either-option
uv sync                  # installs Python 3.10, dev deps (ruff, pyright, pytest)
uv run pytest            # verify smoke test passes
```

### The verify loop

These commands are the contract the codebase must always satisfy:

```bash
uv run ruff format --check .   # formatter
uv run ruff check .            # linter (rules: ALL minus formatter conflicts)
uv run pyright                 # type checker (strict, every report* = error)
uv run pytest -q               # tests (filterwarnings = error)
uv run pytest --cov            # tests + coverage (requires 100%)
```

To **apply** instead of just checking:

```bash
uv run ruff check --fix .      # apply auto-fixable lint
uv run ruff format .           # apply formatter
```

### Multi-version testing

```bash
uv python install 3.10 3.11 3.12 3.13 3.14   # ~150 MB per version, one-time
uv run --python 3.11 pytest                  # run tests on Python 3.11
uv run --python 3.12 pyright                 # type-check on Python 3.12
```

### Repo layout

```
either-option/
├── src/either_option/        # shipped Python code
│   ├── __init__.py           # public re-exports
│   ├── _core.py              # Option/Either + concrete subclasses, sync + async
│   ├── extensions.py         # some_not_none / some_when / none_when / from_optional
│   ├── collections.py        # first_or_none / values / successes / failures …
│   ├── unsafe.py             # value_or_failure / value_or_default / to_optional
│   ├── safe.py               # @safe / @safe_async / call_safe
│   └── py.typed              # PEP 561 marker
├── tests/                    # pytest suite (545 tests; 100% line+branch coverage)
├── examples/                 # runnable demo scripts
├── reference/                # gitignored: clone of nlkl/Optional (C# source) for porting reference
├── pyproject.toml            # single source of truth: deps, ruff, pyright, pytest, uv config
├── CLAUDE.md                 # rules for AI agents working in this repo
└── .python-version           # 3.10 — pins dev interpreter to the support floor
```

The `reference/` folder is gitignored — clone the upstream C# source there with:

```bash
git clone --depth 1 https://github.com/nlkl/Optional reference/optional
```

It is purely for reading; nothing under `reference/` is built, tested, or shipped.

---

## Credits

This project is a Python port of the C# [`Optional`](https://github.com/nlkl/Optional)
library by Nils Lück, distributed under the MIT License. The original copyright
notice is preserved in [`LICENSE`](LICENSE).

## License

[MIT](LICENSE) © 2026 Bao Do.
