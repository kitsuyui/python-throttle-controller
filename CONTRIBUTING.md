# Contributing

Thanks for your interest in improving `throttle-controller`.

This package is currently in alpha. Keep changes small, focused, and easy to
review. The controller is intended for single-threaded, single-process use
today; multi-threaded or multi-process behavior should be discussed before
implementation.

## Getting Started

Install [uv](https://docs.astral.sh/uv/) first, then install the project
dependencies:

```sh
uv sync
```

This repository uses [lefthook](https://lefthook.dev/) for local Git hooks. If
you have `lefthook` on your `PATH`, install the hooks once:

```sh
lefthook install
```

The hooks run the same core commands that CI uses, but you can also run them
manually.

## Local Checks

Run these commands before opening a pull request:

```sh
uv run poe check
uv run poe test
uv run poe coverage-xml
uv build
```

`uv run poe check` runs Ruff and mypy. Keep formatting and type errors fixed in
the same change that introduces them.

## Tests

Add or update tests in `tests/` for behavior changes. For time-sensitive
behavior, prefer the `now` parameter on `SimpleThrottleController.create()` so
tests do not depend on wall-clock time.

## Pull Requests

- Keep each pull request focused on one topic.
- Include a short summary of user-visible behavior changes.
- Mention any compatibility impact, especially while the package is in alpha.
- Include the local checks you ran in the pull request description.

## Reporting Issues

When reporting a problem, include:

- the installed `throttle-controller` version,
- the Python version and operating system,
- a minimal reproduction,
- the expected behavior,
- the actual behavior.

Please avoid sharing private credentials, tokens, or service data in issues or
pull requests.
