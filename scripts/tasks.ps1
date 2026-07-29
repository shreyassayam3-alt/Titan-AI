param(
    [Parameter(Mandatory = $true, Position = 0)]
    [ValidateSet("install", "format", "lint", "typecheck", "test", "check")]
    [string]$Task
)

$ErrorActionPreference = "Stop"

switch ($Task) {
    "install" {
        if (Get-Command uv -ErrorAction SilentlyContinue) {
            uv sync --all-groups
        }
        else {
            python -m pip install -e ".[dev]"
        }
    }
    "format" { ruff format . }
    "lint" { ruff check . }
    "typecheck" { mypy apps services agents tools plugins }
    "test" { pytest }
    "check" {
        ruff check .
        mypy apps services agents tools plugins
        pytest
    }
}
