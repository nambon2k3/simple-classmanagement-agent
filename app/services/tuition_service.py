"""Tuition billing business logic."""

from __future__ import annotations

from datetime import date

from app.core.exceptions import ClassNotFoundError, StudentNotFoundError
from app.core.logging import get_logger
from app.models.classroom import Classroom
from app.models.enums import TuitionChargeStatus
from app.repositories.attendance_repository import AttendanceRepository
from app.repositories.class_repository import ClassRepository
from app.repositories.student_repository import StudentRepository
from app.repositories.tuition_charge_repository import TuitionChargeRepository
from app.schemas.tuition import (
    AttendanceMark,
    ClassAttendanceSinceOutput,
    ClassTeachingDaysRow,
    ClassTuitionSummary,
    SetClassTuitionFeeInput,
    SetClassTuitionFeeOutput,
    StudentAttendanceSinceRow,
    StudentTuitionRow,
    StudentTuitionStatusRow,
    TeachingDaysReportInput,
    TeachingDaysReportOutput,
    TuitionReportInput,
    TuitionReportOutput,
    TuitionStatusSummary,
)
from app.services.class_service import ClassService
from app.services.report_service import resolve_period
from app.utils.datetime_utils import utc_now
from app.utils.money import format_vnd

logger = get_logger(__name__)


class TuitionService:
    """Calculate tuition from attendance and class fee settings."""

    def __init__(
        self,
        attendance_repository: AttendanceRepository,
        class_repository: ClassRepository,
        class_service: ClassService,
        tuition_charge_repository: TuitionChargeRepository,
        student_repository: StudentRepository,
    ) -> None:
        """Wire the service to its data sources."""
        self._attendance = attendance_repository
        self._classes = class_repository
        self._class_service = class_service
        self._charges = tuition_charge_repository
        self._students = student_repository

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

    async def status_summary(self, teacher_id: int) -> TuitionStatusSummary:
        """Completed versus unpaid tuition across every class."""
        not_yet, completed = await self._charges.totals_for_teacher(teacher_id)
        return TuitionStatusSummary(
            not_yet_vnd=not_yet,
            completed_vnd=completed,
            formatted_not_yet=format_vnd(not_yet),
            formatted_completed=format_vnd(completed),
        )

    async def student_status_rows(
        self, teacher_id: int, class_id: int
    ) -> list[StudentTuitionStatusRow]:
        """Per-student payment status for one owned class."""
        classroom = await self._classes.get_owned(class_id, teacher_id)
        if classroom is None:
            raise ClassNotFoundError("I couldn't find that class.")
        roster = await self._students.list_for_class(class_id)
        charges = await self._charges.list_for_class(class_id)
        unpaid_days: dict[int, int] = {}
        unpaid_vnd: dict[int, int] = {}
        completed_vnd: dict[int, int] = {}
        for charge in charges:
            if charge.status is TuitionChargeStatus.NOT_YET:
                unpaid_days[charge.student_id] = unpaid_days.get(charge.student_id, 0) + 1
                unpaid_vnd[charge.student_id] = (
                    unpaid_vnd.get(charge.student_id, 0) + charge.amount_vnd
                )
            else:
                completed_vnd[charge.student_id] = (
                    completed_vnd.get(charge.student_id, 0) + charge.amount_vnd
                )
        rows: list[StudentTuitionStatusRow] = []
        for student in roster:
            days = unpaid_days.get(student.id, 0)
            unpaid = unpaid_vnd.get(student.id, 0)
            paid = completed_vnd.get(student.id, 0)
            status = (
                TuitionChargeStatus.NOT_YET.label if days else TuitionChargeStatus.COMPLETED.label
            )
            rows.append(
                StudentTuitionStatusRow(
                    student_id=student.id,
                    student_code=student.student_code,
                    full_name=student.full_name,
                    unpaid_days=days,
                    unpaid_vnd=unpaid,
                    completed_vnd=paid,
                    formatted_unpaid=format_vnd(unpaid),
                    status=status,
                )
            )
        rows.sort(key=lambda row: row.full_name)
        return rows

    async def attendance_since_payment(
        self, teacher_id: int, class_id: int
    ) -> ClassAttendanceSinceOutput:
        """Day-by-day attendance for each student since their last payment.

        The window starts the day after the latest session a student has
        already paid for, so a teacher can see exactly which days the next
        tuition submission will cover.
        """
        classroom = await self._classes.get_owned(class_id, teacher_id)
        if classroom is None:
            raise ClassNotFoundError("I couldn't find that class.")

        roster = await self._students.list_for_class(class_id)
        paid_through = await self._charges.paid_through_per_student(class_id)
        outstanding = await self._charges.unpaid_totals_per_student(class_id)
        session_dates = await self._attendance.list_session_dates_for_class(class_id)
        marks = {
            (student_id, day): status
            for student_id, day, status in await self._attendance.list_marks_for_class(class_id)
        }

        rows: list[StudentAttendanceSinceRow] = []
        covered: set[date] = set()
        total_present = 0
        total_absent = 0

        for student in roster:
            since = paid_through.get(student.id)
            window = [day for day in session_dates if since is None or day > since]
            covered.update(window)
            entries: list[AttendanceMark] = []
            present_days = 0
            for day in window:
                status = marks.get((student.id, day))
                attended = status is not None and status.counts_as_attended
                present_days += int(attended)
                entries.append(
                    AttendanceMark(
                        session_date=day,
                        attended=attended,
                        recorded=status is not None,
                    )
                )
            absent_days = len(window) - present_days
            total_present += present_days
            total_absent += absent_days
            unpaid = outstanding.get(student.id, 0)
            rows.append(
                StudentAttendanceSinceRow(
                    student_id=student.id,
                    student_code=student.student_code,
                    full_name=student.full_name,
                    paid_through=since,
                    marks=entries,
                    present_days=present_days,
                    absent_days=absent_days,
                    unpaid_vnd=unpaid,
                    formatted_unpaid=format_vnd(unpaid),
                )
            )

        rows.sort(key=lambda row: row.full_name)
        return ClassAttendanceSinceOutput(
            class_name=classroom.name,
            students=rows,
            total_present=total_present,
            total_absent=total_absent,
            session_days=len(covered),
        )

    async def mark_student_completed(self, teacher_id: int, class_id: int, student_id: int) -> int:
        """Pay every outstanding present day for one student in a class.

        Returns:
            The number of charges marked completed.
        """
        classroom = await self._classes.get_owned(class_id, teacher_id)
        if classroom is None:
            raise ClassNotFoundError("I couldn't find that class.")
        student = await self._students.get(student_id)
        if student is None or student.class_id != class_id:
            raise StudentNotFoundError("I couldn't find that student in this class.")
        updated = await self._charges.complete_for_student(
            student_id, class_id, completed_at=utc_now()
        )
        logger.info(
            "Tuition marked completed",
            extra={"class_id": class_id, "student_id": student_id, "charges": updated},
        )
        return updated

    async def _resolve_classrooms(self, teacher_id: int, class_name: str | None) -> list[Classroom]:
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
