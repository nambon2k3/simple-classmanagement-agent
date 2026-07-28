"""Service layer: all business rules, validation and authorisation."""

from app.services.attendance_service import AttendanceService
from app.services.class_service import ClassService
from app.services.container import ServiceContainer
from app.services.report_service import ReportService, resolve_period
from app.services.student_service import StudentService
from app.services.teacher_service import TeacherService

__all__ = [
    "AttendanceService",
    "ClassService",
    "ReportService",
    "ServiceContainer",
    "StudentService",
    "TeacherService",
    "resolve_period",
]
