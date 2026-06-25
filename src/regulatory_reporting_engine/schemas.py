from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field

from regulatory_reporting_engine.domain import ReportStatus, ScheduleFrequency


class HealthResponse(BaseModel):
    status: str


class SourceRecordRequest(BaseModel):
    source: str
    record_date: date
    amount: float
    currency: str = Field(min_length=3, max_length=3)
    category: str


class GenerateReportRequest(BaseModel):
    report_type: str
    period_start: date
    period_end: date
    parameters: dict[str, str] = Field(default_factory=dict)
    user: str = "system"


class UserActionRequest(BaseModel):
    user: str


class ScheduleRequest(BaseModel):
    report_type: str
    frequency: ScheduleFrequency
    parameters: dict[str, str] = Field(default_factory=dict)


class RunScheduleRequest(BaseModel):
    period_start: date
    period_end: date
    user: str = "scheduler"


class SourceRecordResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    source: str
    record_date: date
    amount: float
    currency: str
    category: str


class ValidationIssueResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    rule: str
    message: str
    source_record_id: str | None


class ReportResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    report_type: str
    period_start: date
    period_end: date
    parameters: dict[str, str]
    source_record_ids: list[str]
    output: dict[str, object]
    validation_issues: list[ValidationIssueResponse]
    status: ReportStatus
    approved_by: str | None
    submitted_at: datetime | None
    created_at: datetime
    updated_at: datetime


class ScheduleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    report_type: str
    frequency: ScheduleFrequency
    parameters: dict[str, str]
    active: bool
    created_at: datetime


class ExecutionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    schedule_id: str
    report_id: str | None
    status: str
    attempts: int
    error: str | None
    created_at: datetime


class AuditResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    action: str
    user: str
    report_id: str | None
    details: dict[str, str]
    created_at: datetime
