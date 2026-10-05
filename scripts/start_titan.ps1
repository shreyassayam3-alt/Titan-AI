Set-Location $PSScriptRoot\..
$env:PYTHONPATH = "$PWD"
python -m uvicorn apps.mission_runner.web_app:app --host 127.0.0.1 --port 8000
