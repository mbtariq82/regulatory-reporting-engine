from __future__ import annotations

from fastapi.testclient import TestClient

from regulatory_reporting_engine.main import create_app


def test_api_generates_approves_submits_and_audits_report() -> None:
    client = TestClient(create_app())
    client.post(
        "/source-records",
        json={
            "source": "ledger",
            "record_date": "2026-01-05",
            "amount": 100,
            "currency": "GBP",
            "category": "fees",
        },
    )

    report = client.post(
        "/reports",
        json={
            "report_type": "capital-liquidity",
            "period_start": "2026-01-01",
            "period_end": "2026-01-31",
            "parameters": {"jurisdiction": "UK"},
            "user": "analyst",
        },
    )
    report_id = report.json()["id"]
    approved = client.post(f"/reports/{report_id}/approve", json={"user": "manager"})
    submitted = client.post(f"/reports/{report_id}/submit", json={"user": "submitter"})
    audit = client.get(f"/reports/{report_id}/audit")

    assert report.status_code == 201
    assert report.json()["status"] == "validated"
    assert approved.json()["status"] == "approved"
    assert submitted.json()["status"] == "submitted"
    assert [entry["action"] for entry in audit.json()] == [
        "report_generated",
        "report_approved",
        "report_submitted",
    ]


def test_api_creates_and_runs_schedule() -> None:
    client = TestClient(create_app())
    client.post(
        "/source-records",
        json={
            "source": "ledger",
            "record_date": "2026-01-05",
            "amount": 100,
            "currency": "GBP",
            "category": "fees",
        },
    )
    schedule = client.post(
        "/schedules",
        json={
            "report_type": "capital-liquidity",
            "frequency": "monthly",
            "parameters": {"jurisdiction": "UK"},
        },
    )
    execution = client.post(
        f"/schedules/{schedule.json()['id']}/run",
        json={
            "period_start": "2026-01-01",
            "period_end": "2026-01-31",
            "user": "scheduler",
        },
    )

    assert schedule.status_code == 201
    assert execution.status_code == 200
    assert execution.json()["status"] == "completed"
    assert execution.json()["report_id"] is not None
