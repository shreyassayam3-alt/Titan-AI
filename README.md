# Titan AI

Titan AI is a Python 3.12+ monorepo prepared for applications, reusable services, agents, developer tools, and plugins.

## Repository layout

```text
apps/       Deployable application entry points
services/   Reusable domain and infrastructure services
agents/     AI agent packages and orchestration code
tools/      Internal developer and operational tooling
plugins/    Optional integration plugins
tests/      Cross-package and end-to-end tests
docs/       Architecture and operational documentation
scripts/    Local development and automation scripts
docker/     Container build and runtime assets
.github/    GitHub workflows and contribution templates
```

## Prerequisites

- Python 3.12 or later
- `uv` (preferred) or Python's built-in `venv` and `pip`

## Getting started

`uv` is not required to read or use this repository. If it is installed, use:

```bash
uv sync --all-groups
```

Otherwise, create a virtual environment and install the development dependencies:

```bash
python -m venv .venv
# PowerShell
.\\.venv\\Scripts\\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

Copy `.env.example` to `.env` before adding local configuration. Do not commit `.env` files.

## Common tasks

On systems with `make`:

```bash
make install
make format
make lint
make test
```

On Windows PowerShell:

```powershell
.\\scripts\\tasks.ps1 install
.\\scripts\\tasks.ps1 format
.\\scripts\\tasks.ps1 lint
.\\scripts\\tasks.ps1 test
```

See [the architecture notes](docs/architecture.md) for package boundaries and contribution conventions.

## Status

This is intentionally a project scaffold. It contains no business logic.

## License

Distributed under the [MIT License](LICENSE).
