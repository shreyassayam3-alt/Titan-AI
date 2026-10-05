FROM python:3.12-slim

WORKDIR /app

COPY . /app

RUN python -m pip install --upgrade pip && \
    pip install -e ".[dev]"

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "apps.mission_runner.web_app:app", "--host", "0.0.0.0", "--port", "8000"]
