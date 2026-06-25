from __future__ import annotations

from datetime import date

from regulatory_reporting_engine.domain import (
    AuditEntry,
    Report,
    ReportStatus,
    SourceRecord,
    ValidationIssue,
    utcnow,
)
from regulatory_reporting_engine.repository import ReportingRepository


class ReportService:
    def __init__(self, repository: ReportingRepository) -> None:
        self.repository = repository

    def add_source_record(self, record: SourceRecord) -> SourceRecord:
        return self.repository.save_source_record(record)

    def generate(
        self,
        report_type: str,
        period_start: date,
        period_end: date,
        parameters: dict[str, str] | None = None,
        user: str = "system",
    ) -> Report:
        records = [
            record
            for record in self.repository.list_source_records()
            if period_start <= record.record_date <= period_end
        ]
        issues = self._validate(records, period_start, period_end)
        output = {
            "report_type": report_type,
            "period_start": period_start.isoformat(),
            "period_end": period_end.isoformat(),
            "record_count": len(records),
            "total_amount": round(sum(record.amount for record in records), 2),
            "by_category": self._totals_by_category(records),
        }
        report = Report(
            report_type=report_type,
            period_start=period_start,
            period_end=period_end,
            parameters=parameters or {},
            source_record_ids=[record.id for record in records],
            output=output,
            validation_issues=issues,
            status=ReportStatus.FAILED_VALIDATION if issues else ReportStatus.VALIDATED,
        )
        self.repository.save_report(report)
        self.repository.add_audit(
            AuditEntry(
                action="report_generated",
                user=user,
                report_id=report.id,
                details={"source_records": str(len(records))},
            )
        )
        return report

    def approve(self, report_id: str, user: str) -> Report:
        report = self.repository.get_report(report_id)
        if report.status is not ReportStatus.VALIDATED:
            raise ValueError("Only validated reports can be approved.")
        report.status = ReportStatus.APPROVED
        report.approved_by = user
        report.updated_at = utcnow()
        self.repository.add_audit(AuditEntry("report_approved", user, report.id, {}))
        return self.repository.save_report(report)

    def submit(self, report_id: str, user: str) -> Report:
        report = self.repository.get_report(report_id)
        if report.status is not ReportStatus.APPROVED:
            raise ValueError("Only approved reports can be submitted.")
        report.status = ReportStatus.SUBMITTED
        report.submitted_at = utcnow()
        report.updated_at = report.submitted_at
        self.repository.add_audit(AuditEntry("report_submitted", user, report.id, {}))
        return self.repository.save_report(report)

    @staticmethod
    def _validate(
        records: list[SourceRecord],
        period_start: date,
        period_end: date,
    ) -> list[ValidationIssue]:
        issues: list[ValidationIssue] = []
        if period_start > period_end:
            issues.append(ValidationIssue("period_order", "period_start must be before period_end."))
        for record in records:
            if record.amount < 0:
                issues.append(
                    ValidationIssue(
                        "non_negative_amount",
                        "Source record amount must not be negative.",
                        record.id,
                    )
                )
            if len(record.currency) != 3:
                issues.append(
                    ValidationIssue(
                        "currency_format",
                        "Currency must be a three-letter code.",
                        record.id,
                    )
                )
        return issues

    @staticmethod
    def _totals_by_category(records: list[SourceRecord]) -> dict[str, float]:
        totals: dict[str, float] = {}
        for record in records:
            totals[record.category] = round(totals.get(record.category, 0) + record.amount, 2)
        return totals
