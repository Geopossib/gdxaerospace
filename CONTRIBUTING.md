# Contributing to GDX Aerospace

Thanks for your interest in contributing.

## Development setup

```bash
git clone https://github.com/Geopossib/gdxaerospace.git
cd gdxaerospace
uv sync
```

## Ground rules for engineering code

1. **Cite your source.** Every equation must reference the textbook,
   standard, or paper it comes from in the docstring (e.g. "Anderson,
   *Fundamentals of Aerodynamics*, Eq. 4.12" or "ICAO Doc 7488").
2. **State assumptions explicitly** in the docstring (e.g. "assumes calorically
   perfect gas", "valid for 0 ≤ altitude ≤ 11 km").
3. **SI units internally.** Public APIs may accept `aerounits` quantities for
   convenience, but internal computation is always SI.
4. **Validate inputs.** Raise a specific exception from
   `aerocalc.exceptions` (or the relevant package's `exceptions` module) with
   a message that tells the user how to fix the input.
5. **Multiple models stay explicit.** If a phenomenon has more than one
   standard model or approximation, expose it as a named `model=` parameter
   rather than picking one silently.
6. **Every function needs a numerical test**, not just a smoke test. Compare
   against a published reference value with an explicit tolerance.

## Style

- Python 3.11+, full type hints, `ruff` for lint/format, `mypy` for type
  checking.
- Run `uv run ruff check .` and `uv run pytest` before opening a PR.

## Commit style

Use [Conventional Commits](https://www.conventionalcommits.org/):
`feat:`, `fix:`, `docs:`, `test:`, `refactor:`, `chore:`.

## Adding a new package

Each package under `packages/<name>/` is its own installable unit with its
own `pyproject.toml`, `src/<name>/`, and `tests/`. Copy the structure of
`packages/aerocalc` as a starting template.
