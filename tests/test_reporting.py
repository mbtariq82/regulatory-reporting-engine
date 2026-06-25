from __future__ import annotations

from datetime import date

from regulatory_reporting_engine.domain import ReportStatus, SourceRecord
from regulatory_reporting_engine.reporting import ReportService
from regulatory_reporting_engine.repository import ReportingRepository


def test_generates_valid_report_with_audit_trail() -> None:
    repository = ReportingRepository()
    service = ReportService(repository)
    service.add_source_record(SourceRecord("ledger", date(2026, 1, 5), 100, "GBP", "fees"))
    service.add_source_record(SourceRecord("ledger", date(2026, 1, 6), 50, "GBP", "interest"))

    report = service.generate("capital-liquidity", date(2026, 1, 1), date(2026, 1, 31), user="analyst")

    assert report.status is ReportStatus.VALIDATED
    assert report.output["record_count"] == 2
    assert report.output["total_amount"] == 150
    assert report.output["by_category"] == {"fees": 100, "interest": 50}
    assert repository.audit_for_report(report.id)[0].action == "report_generated"


def test_validation_issues_keep_report_from_approval() -> None:
    repository = ReportingRepository()
    service = ReportService(repository)
    service.add_source_record(SourceRecord("ledger", date(2026, 1, 5), -10, "GBP", "fees"))

    report = service.generate("capital-liquidity", date(2026, 1, 1), date(2026, 1, 31))

    assert report.status is ReportStatus.FAILED_VALIDATION
    assert report.validation_issues[0].rule == "non_negative_amount"
