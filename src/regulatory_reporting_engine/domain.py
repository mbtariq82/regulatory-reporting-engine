from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, date, datetime
from enum import StrEnum
from uuid import uuid4


def utcnow() -> datetime:
    return datetime.now(UTC)


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex[:12]}"


class ReportingError(Exception):
    pass


class NotFoundError(ReportingError):
    pass


class ValidationError(ReportingError):
    pass


class ReportStatus(StrEnum):
    DRAFT = "draft"
    VALIDATED = "validated"
    FAILED_VALIDATION = "failed-validation"
    APPROVED = "approved"
    SUBMITTED = "submitted"


class ScheduleFrequency(StrEnum):
    DAILY = "daily"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"


@dataclass
class SourceRecord:
    source: str
    record_date: date
    amount: float
    currency: str
    category: str
    id: str = field(default_factory=lambda: new_id("src"))


@dataclass
class ValidationIssue:
    rule: str
    message: str
    source_record_id: str | None = None


@dataclass
class Report:
    report_type: str
    period_start: date
    period_end: date
    parameters: dict[str, str]
    source_record_ids: list[str]
    output: dict[str, object]
    validation_issues: list[ValidationIssue]
    status: ReportStatus
    approved_by: str | None = None
    submitted_at: datetime | None = None
    id: str = field(default_factory=lambda: new_id("report"))
    created_at: datetime = field(default_factory=utcnow)
    updated_at: datetime = field(default_factory=utcnow)


@dataclass
class ReportSchedule:
    report_type: str
    frequency: ScheduleFrequency
    parameters: dict[str, str]
    active: bool = True
    id: str = field(default_factory=lambda: new_id("schedule"))
    created_at: datetime = field(default_factory=utcnow)


@dataclass
class ExecutionRecord:
    schedule_id: str
    report_id: str | None
    status: str
    attempts: int
    error: str | None = None
    id: str = field(default_factory=lambda: new_id("exec"))
    created_at: datetime = field(default_factory=utcnow)


@dataclass
class AuditEntry:
    action: str
    user: str
    report_id: str | None
    details: dict[str, str]
    id: str = field(default_factory=lambda: new_id("audit"))
    created_at: datetime = field(default_factory=utcnow)
