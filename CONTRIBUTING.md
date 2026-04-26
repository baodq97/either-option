# Contributing to either-option

Thanks for your interest! This is a small, focused library and the bar for
quality is intentionally high — the verify loop is enforced in CI on every PR.

## Quick links

- **Bug?** → [open an issue](https://github.com/baodq97/either-option/issues/new?template=bug_report.yml)
- **Feature idea?** → [open a feature request](https://github.com/baodq97/either-option/issues/new?template=feature_request.yml)
- **Security issue?** → see [SECURITY.md](SECURITY.md) — please **do not** file a public issue.

## Dev setup

You need [`uv`](https://docs.astral.sh/uv/) (>= 0.11) and `git`. Everything else,
including the Python interpreter, is installed by `uv`.

```bash
git clone https://github.com/baodq97/either-option
cd either-option
uv sync                  # installs Python 3.10, dev tools, package in editable mode
uv run pytest -q         # smoke test
```

## The verify loop

Every PR must pass these five commands. CI runs them automatically.

```bash
uv run ruff format --check .   # formatter
uv run ruff check .            # linter (rules: ALL minus formatter conflicts)
uv run pyright                 # type checker (strict, every report* = error)
uv run pytest -q               # tests (filterwarnings = error)
uv run pytest --cov            # tests + coverage (requires 100%)
```

Apply auto-fixes:

```bash
uv run ruff check --fix .
uv run ruff format .
```

## Coding rules

- **Python 3.10 floor.** Develop on 3.10 (`.python-version`); CI also tests
  3.11–3.14. Use `typing_extensions` for anything `>= 3.11` you need.
- **Pyright `--strict`** — no `Any`, no `cast()`, no untyped `# type: ignore`.
  Every escape hatch needs a code (`# type: ignore[arg-type]`) and a comment.
- **No new runtime deps** without a concrete in-tree caller. Keep the install
  surface tiny.
- **No upper version caps** on runtime deps unless you have evidence of a real
  incompatibility.
- **100% line + branch coverage**, enforced by `fail_under = 100`. Add tests
  with the change.
- **Tests are pytest functions** (no `unittest.TestCase`). Each test is
  independently runnable.
- **Public API only via `__init__.py`** — `__all__` is the contract.
- See [`CLAUDE.md`](CLAUDE.md) for the full DO-NOT list.

## Pull request flow

1. Fork + branch from `main`.
2. Make focused commits — small PRs are merged faster than large ones.
3. Run the verify loop locally.
4. Push and open a PR; CI must be green for review.
5. Update [`CHANGELOG.md`](CHANGELOG.md) under `## [Unreleased]` with your
   change in the appropriate section (Added / Changed / Fixed / Removed).
6. Maintainer squash-merges. Title becomes the squashed commit message.

## Release process (maintainers)

1. Move `## [Unreleased]` items into a new `## [X.Y.Z] - YYYY-MM-DD` section
   in `CHANGELOG.md`.
2. Bump `version` in `pyproject.toml` (own commit).
3. `git tag -a vX.Y.Z -m "vX.Y.Z" && git push origin vX.Y.Z`.
4. The `release.yml` workflow builds + publishes to PyPI via OIDC trusted
   publisher and creates a GitHub Release.

## Code of Conduct

This project follows the [Contributor Covenant v2.1](CODE_OF_CONDUCT.md).
By participating, you agree to abide by it.
