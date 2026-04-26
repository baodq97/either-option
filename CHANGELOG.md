# Changelog

All notable changes to **either-option** are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.1] - 2026-04-26

### Changed

- CI: bumped `actions/checkout` v4 → v6, `astral-sh/setup-uv` v4 → v8.1.0,
  `actions/upload-artifact` v4 → v7.

### Added

- Release workflow (`release.yml`) auto-publishes on `v*.*.*` tags via PyPI
  trusted publisher (OIDC), runs full 5-version test matrix, and creates a
  GitHub Release.
- `dependabot.yml` for weekly updates of GitHub Actions and uv-managed
  Python deps.
- OSS docs: `CHANGELOG.md`, `CONTRIBUTING.md`, `SECURITY.md`,
  `CODE_OF_CONDUCT.md`, issue + PR templates.

## [0.1.0] - 2026-04-26

### Added

- `Option[T]` sum type with `Some(value)` and `Nothing` (singleton) subclasses.
- `Either[T, E]` sum type with `Success(value)` and `Failure(exception)` subclasses.
- Sealed pattern matching support (PEP 634) for both sum types.
- Sync combinator surface: `map`, `flat_map`, `filter`, `tap`, `match`,
  `value_or`, `value_or_else`, `value_or_with`, `or_else`, `or_with`,
  `or_option_else`, `or_option_with`, `map_failure`, `flat_map_failure`,
  `to_iterable`, `contains`, `exists`.
- Async variants of every combinator with `_async` suffix.
- `Either.from_awaitable(awaitable, catch=...)` to lift coroutines.
- `flatten()` free function.
- `@safe` and `@safe_async` decorators (ParamSpec-typed) and `call_safe`
  one-shot helper.
- `extensions` module: `some_not_none`, `some_when`, `none_when`,
  `from_optional` (with `@overload` for Either-returning form).
- `collections` module: `first_or_none`, `last_or_none`, `single_or_none`,
  `element_at_or_none`, `get_or_none`, `values`, `successes`, `failures`.
- `unsafe` module: opt-in `value_or_failure`, `value_or_default`, `to_optional`,
  and `OptionValueMissingError`.
- `__reduce__` (pickle) round-trip via public factories.
- `total_ordering` for both sum types.
- `py.typed` marker (PEP 561).

### Quality

- 545 tests passing on Python 3.10, 3.11, 3.12, 3.13, 3.14.
- 100% line + branch coverage (enforced via `fail_under = 100`).
- Pyright `--strict` clean (every `report*` diagnostic = `error`).
- Ruff with `select = ["ALL"]` clean.

[Unreleased]: https://github.com/baodq97/either-option/compare/v0.1.1...HEAD
[0.1.1]: https://github.com/baodq97/either-option/releases/tag/v0.1.1
[0.1.0]: https://github.com/baodq97/either-option/releases/tag/v0.1.0
