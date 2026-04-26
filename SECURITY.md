# Security Policy

## Supported versions

`either-option` follows [Semantic Versioning](https://semver.org/). Only the
**latest minor** of the **latest major** receives security fixes.

| Version | Supported |
|---|:-:|
| `0.1.x` | yes |
| `< 0.1` | no |

## Reporting a vulnerability

**Please do not file a public issue.**

Use GitHub's private vulnerability reporting:

> https://github.com/baodq97/either-option/security/advisories/new

If that is unavailable, email **baodq97@gmail.com** with the subject prefix
`[security] either-option` and as much detail as you can share (reproducer,
affected version, impact).

You will receive an acknowledgement within **5 business days**. After triage,
we will keep you posted on remediation timing. Once a fix is released, we will
credit you in the changelog and the GitHub Security Advisory unless you prefer
to remain anonymous.

## Scope

In scope:

- Logic bugs in `either-option` itself that could be abused (e.g. unsafe
  pickle round-trip, memory exhaustion, crash on pathological input).
- Type-system holes that allow `Any` to leak through public signatures.

Out of scope:

- Bugs in user code that misuse the library.
- Issues in transitive dependencies (`typing_extensions`, etc.) — please
  report those upstream first.
- Vulnerabilities that require an attacker to already control the Python
  process.
