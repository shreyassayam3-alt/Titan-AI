"""Command-line entrypoint for running the TITAN API server."""

from __future__ import annotations

import argparse

import uvicorn


def build_parser() -> argparse.ArgumentParser:
    """Create the API server CLI parser."""
    parser = argparse.ArgumentParser(description="Run the TITAN API server")
    parser.add_argument("--host", default="0.0.0.0", help="Host interface")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind")
    return parser


def main(argv: list[str] | None = None) -> None:
    """Run the TITAN FastAPI app."""
    args = build_parser().parse_args(argv)
    uvicorn.run("apps.api.app:app", host=args.host, port=args.port, reload=False)


if __name__ == "__main__":
    main()
