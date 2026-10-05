"""Entry point for running TITAN via 'python -m apps.titan_cli'."""

import asyncio
import sys

from apps.titan_cli.cli import main

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
