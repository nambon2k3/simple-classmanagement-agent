"""Tuition billing business logic."""

from __future__ import annotations

from datetime import date

from app.core.logging import get_logger
from app.models.classroom import Classroom
from app.repositories.attendance_repository import AttendanceRepository
from app.repositories.class_repository import ClassRepository
from app.schemas.tuition import (
    ClassTeachingDaysRow,
    ClassTuitionSummary,
    SetClassTuitionFeeInput,
    SetClassTuitionFeeOutput,
    StudentTuitionRow,
    TeachingDaysReportInput,
    TeachingDaysReportOutput,
    TuitionReportInput,
    TuitionReportOutput,
)
from app.services.class_service import ClassService
from app.services.report_service import resolve_period
from app.utils.money import format_vnd

logger = get_logger(__name__)


class TuitionService:
    """Calculate tuition from attendance and class fee settings."""

    def __init__(
        self,
        attendance_repository: AttendanceRepository,
        class_repository: ClassRepository,
        class_service: ClassService,
    ) -> None:
        """Wire the service to its data sources."""
        self._attendance = attendance_repository
        self._classes = class_repository
        self._class_service = class_service

    async def set_class_tuition_fee(
        self, teacher_id: int, payload: SetClassTuitionFeeInput
    ) -> SetClassTuitionFeeOutput:
        """Delegate fee updates to the class service."""
        return await self._class_service.set_class_tuition_fee(teacher_id, payload)

    async def tuition_report(
        self, teacher_id: int, payload: TuitionReportInput
    ) -> TuitionReportOutput:
        """Bill students from completed attendance in a date range."""
        date_range = resolve_period(payload.period, payload.start_date, payload.end_date)
        classrooms = await self._resolve_classrooms(teacher_id, payload.class_name)

        summaries: list[ClassTuitionSummary] = []
        grand_total = 0
        teaching_days = 0

        for classroom in classrooms:
            summary = await self._class_tuition_summary(
                classroom,
                date_range.start_date,
                date_range.end_date,
            )
            summaries.append(summary)
            grand_total += summary.total_tuition_vnd
            teaching_days += summary.teaching_days

        logger.info(
            "Tuition report generated",
            extra={"teacher_id": teacher_id, "classes": len(summaries), "total": grand_total},
        )
        return TuitionReportOutput(
            range=date_range,
            teaching_days=teaching_days,
            classes=summaries,
            total_tuition_vnd=grand_total,
            formatted_total=format_vnd(grand_total),
        )

    async def teaching_days_report(
        self, teacher_id: int, payload: TeachingDaysReportInput
    ) -> TeachingDaysReportOutput:
        """Count how many days the teacher held completed sessions."""
        date_range = resolve_period(payload.period, payload.start_date, payload.end_date)
        rows = await self._attendance.teaching_days_per_class(
            teacher_id, date_range.start_date, date_range.end_date
        )
        total = await self._attendance.count_teaching_days_for_teacher(
            teacher_id, date_range.start_date, date_range.end_date
        )
        return TeachingDaysReportOutput(
            range=date_range,
            total_teaching_days=total,
            classes=[
                ClassTeachingDaysRow(class_name=name, teaching_days=count) for name, count in rows
            ],
        )

    async def _resolve_classrooms(
        self, teacher_id: int, class_name: str | None
    ) -> list[Classroom]:
        if class_name:
            return [await self._class_service.resolve(teacher_id, class_name)]
        return await self._classes.list_for_teacher(teacher_id)

    async def _class_tuition_summary(
        self, classroom: Classroom, start: date, end: date
    ) -> ClassTuitionSummary:
        daily_fee = classroom.daily_tuition_fee
        teaching_days = await self._attendance.count_teaching_days_for_class(
            classroom.id, start, end
        )
        billable = await self._attendance.billable_days_per_student(classroom.id, start, end)
        billed_ids = {student.id for student, _ in billable}

        students: list[StudentTuitionRow] = []
        for student, attended_days in billable:
            amount = attended_days * daily_fee
            students.append(
                StudentTuitionRow(
                    student_code=student.student_code,
                    full_name=student.full_name,
                    attended_days=attended_days,
                    amount_vnd=amount,
                    formatted_amount=format_vnd(amount),
                )
            )

        # Students with zero attended days still appear with 0 tuition.
        full_class = await self._classes.get_with_students(classroom.id, classroom.teacher_id)
        if full_class is not None:
            for student in full_class.students:
                if student.id in billed_ids:
                    continue
                students.append(
                    StudentTuitionRow(
                        student_code=student.student_code,
                        full_name=student.full_name,
                        attended_days=0,
                        amount_vnd=0,
                        formatted_amount=format_vnd(0),
                    )
                )
            students.sort(key=lambda row: row.full_name)

        total = sum(row.amount_vnd for row in students)
        return ClassTuitionSummary(
            class_name=classroom.name,
            daily_tuition_fee=daily_fee,
            formatted_daily_fee=format_vnd(daily_fee),
            teaching_days=teaching_days,
            students=students,
            total_tuition_vnd=total,
            formatted_total=format_vnd(total),
        )
