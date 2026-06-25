from __future__ import annotations

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from regulatory_reporting_engine.domain import (
    NotFoundError,
    ReportingError,
    SourceRecord,
    ValidationError,
)
from regulatory_reporting_engine.reporting import ReportService
from regulatory_reporting_engine.repository import ReportingRepository
from regulatory_reporting_engine.scheduling import SchedulingService
from regulatory_reporting_engine.schemas import (
    AuditResponse,
    ExecutionResponse,
    GenerateReportRequest,
    HealthResponse,
    ReportResponse,
    RunScheduleRequest,
    ScheduleRequest,
    ScheduleResponse,
    SourceRecordRequest,
    SourceRecordResponse,
    UserActionRequest,
)


def create_app(repository: ReportingRepository | None = None) -> FastAPI:
    repository = repository or ReportingRepository()
    report_service = ReportService(repository)
    scheduling_service = SchedulingService(repository, report_service)

    app = FastAPI(
        title="Regulatory Reporting Engine",
        version="0.1.0",
        summary="Report generation, validation, scheduling, and audit API.",
    )
    app.state.repository = repository
    app.state.report_service = report_service
    app.state.scheduling_service = scheduling_service

    @app.exception_handler(ReportingError)
    async def handle_reporting_error(_request: Request, exc: ReportingError) -> JSONResponse:
        status_code = status.HTTP_400_BAD_REQUEST
        if isinstance(exc, NotFoundError):
            status_code = status.HTTP_404_NOT_FOUND
        elif isinstance(exc, ValidationError):
            status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
        return JSONResponse(status_code=status_code, content={"detail": str(exc)})

    @app.get("/health", response_model=HealthResponse)
    def health() -> HealthResponse:
        return HealthResponse(status="ok")

    @app.post("/source-records", status_code=status.HTTP_201_CREATED, response_model=SourceRecordResponse)
    def add_source_record(payload: SourceRecordRequest) -> SourceRecordResponse:
        return SourceRecordResponse.model_validate(
            report_service.add_source_record(
                SourceRecord(
                    source=payload.source,
                    record_date=payload.record_date,
                    amount=payload.amount,
                    currency=payload.currency,
                    category=payload.category,
                )
            )
        )

    @app.post("/reports", status_code=status.HTTP_201_CREATED, response_model=ReportResponse)
    def generate_report(payload: GenerateReportRequest) -> ReportResponse:
        return ReportResponse.model_validate(
            report_service.generate(
                payload.report_type,
                payload.period_start,
                payload.period_end,
                payload.parameters,
                user=payload.user,
            )
        )

    @app.get("/reports/{report_id}", response_model=ReportResponse)
    def get_report(report_id: str) -> ReportResponse:
        return ReportResponse.model_validate(repository.get_report(report_id))

    @app.post("/reports/{report_id}/approve", response_model=ReportResponse)
    def approve_report(report_id: str, payload: UserActionRequest) -> ReportResponse:
        return ReportResponse.model_validate(report_service.approve(report_id, payload.user))

    @app.post("/reports/{report_id}/submit", response_model=ReportResponse)
    def submit_report(report_id: str, payload: UserActionRequest) -> ReportResponse:
        return ReportResponse.model_validate(report_service.submit(report_id, payload.user))

    @app.get("/reports/{report_id}/audit", response_model=list[AuditResponse])
    def report_audit(report_id: str) -> list[AuditResponse]:
        repository.get_report(report_id)
        return [AuditResponse.model_validate(entry) for entry in repository.audit_for_report(report_id)]

    @app.post("/schedules", status_code=status.HTTP_201_CREATED, response_model=ScheduleResponse)
    def create_schedule(payload: ScheduleRequest) -> ScheduleResponse:
        return ScheduleResponse.model_validate(
            scheduling_service.create_schedule(
                payload.report_type,
                payload.frequency,
                payload.parameters,
            )
        )

    @app.post("/schedules/{schedule_id}/run", response_model=ExecutionResponse)
    def run_schedule(schedule_id: str, payload: RunScheduleRequest) -> ExecutionResponse:
        return ExecutionResponse.model_validate(
            scheduling_service.run_schedule(
                schedule_id,
                payload.period_start,
                payload.period_end,
                user=payload.user,
            )
        )

    return app


app = create_app()
