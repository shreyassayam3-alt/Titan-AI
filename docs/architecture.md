# Architecture

Titan AI follows a modular-monolith-friendly monorepo layout. Each top-level runtime area owns its implementation details and exposes only deliberate interfaces to other areas.

## Boundaries

- `apps/` contains deployable entry points and composition roots.
- `services/` contains reusable business capabilities, domain models, and adapters.
- `agents/` contains agent definitions, prompts, tools, and orchestration.
- `tools/` contains internal utilities that are not product runtime dependencies.
- `plugins/` contains optional integrations with third-party systems.
- `tests/` contains cross-cutting tests; package-local tests can be added alongside a future package when useful.

Create independently versioned or deployable units as subdirectories within the appropriate area. Each future unit should own its `README.md`, package metadata as needed, tests, and configuration. Keep imports directed inward: entry points may depend on services and agents; services should not depend on apps.

## Configuration

Environment-specific configuration is supplied through environment variables. `.env.example` documents non-secret defaults; `.env` is local-only and ignored by Git. Use a secret manager for production credentials.

## Research providers

The research provider framework in `agents/research/providers/` normalizes search and news results from local Markdown documents, RSS feeds, and repository sources. The provider registry merges and ranks these results for a query.

## Quality baseline

Ruff handles formatting and linting, mypy provides static typing, and pytest runs tests. The root `pyproject.toml` centralizes their configuration.
