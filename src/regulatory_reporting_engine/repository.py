from __future__ import annotations

from threading import RLock

from regulatory_reporting_engine.domain import (
    AuditEntry,
    ExecutionRecord,
    NotFoundError,
    Report,
    ReportSchedule,
    SourceRecord,
)


class ReportingRepository:
    def __init__(self) -> None:
        self._source_records: dict[str, SourceRecord] = {}
        self._reports: dict[str, Report] = {}
        self._schedules: dict[str, ReportSchedule] = {}
        self._executions: dict[str, ExecutionRecord] = {}
        self._audit: list[AuditEntry] = []
        self._lock = RLock()

    def save_source_record(self, record: SourceRecord) -> SourceRecord:
        with self._lock:
            self._source_records[record.id] = record
            return record

    def list_source_records(self) -> list[SourceRecord]:
        with self._lock:
            return list(self._source_records.values())

    def save_report(self, report: Report) -> Report:
        with self._lock:
            self._reports[report.id] = report
            return report

    def get_report(self, report_id: str) -> Report:
        with self._lock:
            try:
                return self._reports[report_id]
            except KeyError as exc:
                raise NotFoundError(f"Report {report_id!r} was not found.") from exc

    def list_reports(self) -> list[Report]:
        with self._lock:
            return list(self._reports.values())

    def save_schedule(self, schedule: ReportSchedule) -> ReportSchedule:
        with self._lock:
            self._schedules[schedule.id] = schedule
            return schedule

    def get_schedule(self, schedule_id: str) -> ReportSchedule:
        with self._lock:
            try:
                return self._schedules[schedule_id]
            except KeyError as exc:
                raise NotFoundError(f"Schedule {schedule_id!r} was not found.") from exc

    def list_schedules(self) -> list[ReportSchedule]:
        with self._lock:
            return list(self._schedules.values())

    def save_execution(self, execution: ExecutionRecord) -> ExecutionRecord:
        with self._lock:
            self._executions[execution.id] = execution
            return execution

    def list_executions(self) -> list[ExecutionRecord]:
        with self._lock:
            return list(self._executions.values())

    def add_audit(self, entry: AuditEntry) -> AuditEntry:
        with self._lock:
            self._audit.append(entry)
            return entry

    def audit_for_report(self, report_id: str) -> list[AuditEntry]:
        with self._lock:
            return [entry for entry in self._audit if entry.report_id == report_id]
