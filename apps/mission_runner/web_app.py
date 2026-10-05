"""Web interface for running Titan missions."""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

from apps.mission_runner.run_mission import build_runner

app = FastAPI(title="Titan AI", version="0.1.0")


class MissionRequest(BaseModel):
    goal: str = Field(..., min_length=1, description="Mission goal to execute")
    description: str | None = Field(default=None, description="Optional goal description")
    priority: int = Field(default=0, ge=0, description="Priority for the mission")


@app.get("/", response_class=HTMLResponse)
async def index() -> str:
    return """
    <!doctype html>
    <html lang="en">
      <head>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <title>TITAN AI</title>
        <style>
          :root { color-scheme: light dark; }
          * { box-sizing: border-box; }
          body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 2rem;
            background: linear-gradient(180deg, #020817, #0f172a);
            color: #e2e8f0;
          }
          .card {
            max-width: 980px;
            margin: 0 auto;
            padding: 2rem;
            border-radius: 18px;
            background: rgba(15, 23, 42, 0.9);
            box-shadow: 0 20px 40px rgba(15, 23, 42, 0.45);
            border: 1px solid rgba(148, 163, 184, 0.2);
          }
          h1 { margin-top: 0; }
          .grid {
            display: grid;
            grid-template-columns: 1.1fr 0.9fr;
            gap: 1.5rem;
          }
          form { display: flex; flex-direction: column; gap: 0.75rem; }
          textarea, input, button {
            width: 100%;
            box-sizing: border-box;
            padding: 0.9rem 1rem;
            border-radius: 10px;
            border: 1px solid #334155;
            font-size: 1rem;
          }
          textarea, input {
            background: rgba(15, 23, 42, 0.7);
            color: #f8fafc;
          }
          button {
            background: linear-gradient(135deg, #22c55e, #16a34a);
            color: #052e16;
            font-weight: 700;
            cursor: pointer;
            border: none;
          }
          .result-panel {
            margin-top: 1.5rem;
            padding: 1.2rem;
            background: rgba(15, 23, 42, 0.75);
            border-radius: 12px;
            border: 1px solid rgba(148, 163, 184, 0.2);
          }
          .status-pill {
            display: inline-block;
            padding: 0.35rem 0.7rem;
            border-radius: 999px;
            background: rgba(34, 197, 94, 0.15);
            color: #4ade80;
            font-size: 0.8rem;
            font-weight: 700;
            margin-bottom: 0.75rem;
          }
          .muted { color: #cbd5e1; }
          ul { padding-left: 1.2rem; }
          code {
            background: rgba(148, 163, 184, 0.08);
            padding: 0.1rem 0.35rem;
            border-radius: 5px;
          }
          @media (max-width: 720px) {
            .grid { grid-template-columns: 1fr; }
            body { padding: 1rem; }
          }
        </style>
      </head>
      <body>
        <div class="card">
          <h1>TITAN AI</h1>
          <p class="muted">Run a mission against the local Titan runtime.</p>
          <div class="grid">
            <form id="mission-form">
              <label for="goal">Goal</label>
              <textarea id="goal" name="goal" rows="3" placeholder="Research today's AI news" required></textarea>
              <label for="description">Description</label>
              <input id="description" name="description" placeholder="Optional summary" />
              <label for="priority">Priority</label>
              <input id="priority" name="priority" type="number" min="0" value="0" />
              <button type="submit">Launch mission</button>
            </form>

            <div class="result-panel" id="result">
              <div class="status-pill">Idle</div>
              <div class="muted">Waiting for a mission...</div>
            </div>
          </div>
        </div>

        <script>
          const form = document.getElementById('mission-form');
          const result = document.getElementById('result');

          function renderMission(data) {
            const report = data.report || {};
            const summary = report.executive_summary || 'Mission completed without a custom executive summary.';
            const findings = Array.isArray(report.key_findings) ? report.key_findings : [];
            const plan = Array.isArray(data.plan) ? data.plan : [];
            const llmSummary = data.llm_summary || 'No LLM summary available.';

            result.innerHTML = `
              <div class="status-pill">Live</div>
              <h2>${data.goal || 'Mission result'}</h2>
              <p class="muted">${summary}</p>
              <div>
                <strong>Plan</strong>
                <ul>${plan.map(item => `<li>${item}</li>`).join('')}</ul>
              </div>
              <div>
                <strong>Key findings</strong>
                <ul>${findings.length ? findings.map(item => `<li>${item}</li>`).join('') : '<li>No findings available.</li>'}</ul>
              </div>
              <div>
                <strong>LLM summary</strong>
                <p>${llmSummary}</p>
              </div>
              <div>
                <strong>Provider</strong>
                <p>${report.llm_provider || 'unknown'}</p>
              </div>
            `;
          }

          form.addEventListener('submit', async (event) => {
            event.preventDefault();
            const payload = {
              goal: document.getElementById('goal').value,
              description: document.getElementById('description').value || null,
              priority: Number(document.getElementById('priority').value || 0),
            };

            result.innerHTML = '<div class="status-pill">Running</div><div class="muted">Executing mission...</div>';
            try {
              const response = await fetch('/api/mission', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload),
              });
              const data = await response.json();
              if (!response.ok) {
                throw new Error(data.detail || 'Mission failed');
              }
              renderMission(data);
            } catch (error) {
              result.innerHTML = `<div class="status-pill">Error</div><div class="muted">${(error.message || 'Unknown error')}</div>`;
            }
          });
        </script>
      </body>
    </html>
    """


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "titan-ai"}


@app.post("/api/mission")
async def launch_mission(payload: MissionRequest) -> dict[str, Any]:
    runner = build_runner()
    execution = await runner.run(payload.goal, description=payload.description, priority=payload.priority)

    raw_report = execution.report.results[0] if execution.report.results else None
    report = getattr(raw_report, "output", raw_report) if raw_report is not None else None
    metadata = getattr(report, "metadata", {}) if report is not None else {}
    report_payload: dict[str, Any] = {}
    if report is not None:
        report_payload = {
            "type": type(report).__name__,
            "topic": getattr(report, "topic", None),
            "news_items": len(getattr(report, "news_items", []) or []),
            "sources": len(getattr(report, "sources", []) or []),
            "executive_summary": metadata.get("executive_summary"),
            "change_summary": metadata.get("change_summary"),
            "key_findings": metadata.get("key_findings", []),
            "llm_provider": metadata.get("llm_provider", "unknown"),
            "provider_summary": metadata.get("provider_summary"),
        }

    return {
        "goal": execution.goal.title,
        "description": execution.goal.description,
        "plan": [task.title for task in execution.plan],
        "report": report_payload,
        "llm_summary": metadata.get("llm_summary"),
        "log_lines": list(execution.log_lines),
    }
