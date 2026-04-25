# optional-python

A Python port of the C# [`Optional`](https://github.com/nlkl/optional) library by `nlkl` —
explicit, type-safe handling of optional values without relying on `None`.

> Status: pre-implementation. Harness and tooling are set up; the port itself has not started.

---

## Prerequisites

You need these tools on your machine **before** running anything in this repo. Versions
listed are the minimum tested floors.

### Required

| Tool | Min version | Why | Install |
|---|---|---|---|
| **Python** | 3.10 | Library targets `>=3.10`. `uv` installs the right interpreter for you on first sync, but you still need a system Python or `uv` itself to bootstrap. | See `uv` below — it installs Python 3.10 automatically. |
| **uv** | 0.11 | Package manager, build backend (`uv_build`), test runner, and Python installer. The repo pins `required-version = ">=0.11"` so older versions are rejected. | **Win:** `powershell -ExecutionPolicy Bypass -c "irm https://astral.sh/uv/install.ps1 \| iex"`<br>**macOS / Linux:** `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| **Git** | any recent | Clone repo + (optionally) reference upstream C# source. | Platform package manager. |

That's it for running tests, linting, and type-checking the project itself.

### Optional — only if you use the AI dev loop in `.claude/`

| Tool | Why |
|---|---|
| **jq** | Required by `.claude/hooks/format-py.sh` to parse tool-call JSON from stdin. Without `jq`, the auto-format-on-save hook silently no-ops. The Stop verify hook does **not** need `jq`. |
| **Bash** | Hooks are bash scripts. On Windows, Git Bash (bundled with Git for Windows) is sufficient. |

**Install jq:**
- **Win:** `winget install jqlang.jq` — *or* download `jq-windows-amd64.exe` from
  [jqlang/jq releases](https://github.com/jqlang/jq/releases) and drop it into a
  directory on `PATH` (e.g. `~/.local/bin/jq.exe`). The winget package has had
  a stale-registry bug; if `which jq` fails after winget install, fall back to
  the direct download.
- **macOS:** `brew install jq`
- **Linux:** `apt install jq` / `dnf install jq` / `pacman -S jq`

### Optional — for full multi-version test matrix

The library supports Python 3.10 through 3.14. Local development pins **3.10**
(the floor — see `.python-version`) so you cannot accidentally use 3.11+ syntax.
To test on additional versions:

```bash
uv python install 3.10 3.11 3.12 3.13 3.14   # ~150 MB per version, one-time
uv run --python 3.11 pytest                  # run tests on Python 3.11
uv run --python 3.12 pyright                 # type-check on Python 3.12
```

---

## First-time setup

```bash
git clone <this-repo>
cd optional-python
uv sync                  # installs Python 3.10, dev deps (ruff, pyright, pytest)
uv run pytest            # verify smoke test passes
```

`uv sync` reads `pyproject.toml` + `uv.lock`, downloads the pinned Python
interpreter if missing, creates `.venv/`, and installs the package in editable
mode plus the `dev` dependency group.

---

## The verify loop

These four commands are the contract the codebase must always satisfy. Run them
before declaring any change done.

```bash
uv run ruff format --check .   # formatter
uv run ruff check .            # linter (rules: ALL minus formatter conflicts)
uv run pyright                 # type checker (strict, every report* = error)
uv run pytest -q               # tests (filterwarnings = error)
```

To **apply** instead of just checking:

```bash
uv run ruff check --fix .      # apply auto-fixable lint
uv run ruff format .           # apply formatter
```

If you also have the AI dev hooks active (see `.claude/settings.json`), the
`Stop` hook runs the verify loop in the background after each Claude turn and
wakes the model only on failure — you do not need to run it manually unless
working solo.

---

## Repo layout

```
optional-python/
├── src/optional_python/   # shipped Python code (currently a stub)
├── tests/                 # pytest tests
├── reference/             # gitignored: clone of nlkl/optional (C# source) for porting reference
├── .claude/               # Claude Code hooks + settings (project-scoped)
├── pyproject.toml         # single source of truth: deps, ruff, pyright, pytest, uv config
├── CLAUDE.md              # rules for AI agents working in this repo (DO-NOT list)
└── .python-version        # 3.10 — pins dev interpreter to the support floor
```

The `reference/` folder is gitignored — clone the upstream C# source there with:

```bash
git clone --depth 1 https://github.com/nlkl/optional reference/optional
```

It is purely for reading; nothing under `reference/` is built, tested, or shipped.

---

## License

TBD.
