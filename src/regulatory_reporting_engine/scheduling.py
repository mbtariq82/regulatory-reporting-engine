from __future__ import annotations

from datetime import date

from regulatory_reporting_engine.domain import (
    ExecutionRecord,
    ReportSchedule,
    ScheduleFrequency,
)
from regulatory_reporting_engine.reporting import ReportService
from regulatory_reporting_engine.repository import ReportingRepository


class SchedulingService:
    def __init__(
        self,
        repository: ReportingRepository,
        report_service: ReportService,
    ) -> None:
        self.repository = repository
        self.report_service = report_service

    def create_schedule(
        self,
        report_type: str,
        frequency: ScheduleFrequency,
        parameters: dict[str, str] | None = None,
    ) -> ReportSchedule:
        return self.repository.save_schedule(
            ReportSchedule(
                report_type=report_type,
                frequency=frequency,
                parameters=parameters or {},
            )
        )

    def run_schedule(
        self,
        schedule_id: str,
        period_start: date,
        period_end: date,
        user: str = "scheduler",
        max_attempts: int = 3,
    ) -> ExecutionRecord:
        schedule = self.repository.get_schedule(schedule_id)
        attempts = 0
        last_error: str | None = None
        while attempts < max_attempts:
            attempts += 1
            try:
                report = self.report_service.generate(
                    schedule.report_type,
                    period_start,
                    period_end,
                    schedule.parameters,
                    user=user,
                )
                return self.repository.save_execution(
                    ExecutionRecord(
                        schedule_id=schedule.id,
                        report_id=report.id,
                        status="completed",
                        attempts=attempts,
                    )
                )
            except Exception as exc:
                last_error = str(exc)
        return self.repository.save_execution(
            ExecutionRecord(
                schedule_id=schedule.id,
                report_id=None,
                status="failed",
                attempts=attempts,
                error=last_error,
            )
        )
