from __future__ import annotations

from datetime import date

from regulatory_reporting_engine.domain import ScheduleFrequency, SourceRecord
from regulatory_reporting_engine.reporting import ReportService
from regulatory_reporting_engine.repository import ReportingRepository
from regulatory_reporting_engine.scheduling import SchedulingService


def test_schedule_runs_report_and_records_execution_history() -> None:
    repository = ReportingRepository()
    reports = ReportService(repository)
    scheduling = SchedulingService(repository, reports)
    reports.add_source_record(SourceRecord("ledger", date(2026, 1, 5), 100, "GBP", "fees"))
    schedule = scheduling.create_schedule(
        "capital-liquidity",
        ScheduleFrequency.MONTHLY,
        {"jurisdiction": "UK"},
    )

    execution = scheduling.run_schedule(schedule.id, date(2026, 1, 1), date(2026, 1, 31))
    report = repository.get_report(execution.report_id)

    assert execution.status == "completed"
    assert execution.attempts == 1
    assert report.parameters["jurisdiction"] == "UK"
    assert repository.list_executions()[0].id == execution.id
