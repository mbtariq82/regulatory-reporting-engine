# Regulatory Reporting Engine

Training implementation of a regulatory reporting API. It gathers source
records, generates period reports, validates data, supports schedules and
execution history, and records audit events for generation, approval, and
submission.

## Features

- Source record ingestion for reporting inputs.
- Report generation with totals, category breakdowns, source record lineage, and
  validation issues.
- Validation rules for period order, non-negative amounts, and currency format.
- Approval and submission flow with user attribution.
- Report schedules with execution history and retry tracking.
- Audit trail for report reconstruction.

## Run locally

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install -e ".[dev]"
uvicorn regulatory_reporting_engine.main:app --reload
```

Open `http://127.0.0.1:8000/docs` for interactive API docs.

## Test

```bash
pytest
```

## Key endpoints

- `POST /source-records`
- `POST /reports`
- `GET /reports/{report_id}`
- `POST /reports/{report_id}/approve`
- `POST /reports/{report_id}/submit`
- `GET /reports/{report_id}/audit`
- `POST /schedules`
- `POST /schedules/{schedule_id}/run`
