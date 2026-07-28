"""Service composition root.

Wiring lives here rather than inside the services themselves, so that a
handler, an API route or a test only has to say "give me the services for this
session" and every dependency is constructed consistently.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import cached_property

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings
from app.repositories.attendance_repository import AttendanceRepository
from app.repositories.class_repository import ClassRepository
from app.repositories.student_repository import StudentRepository
from app.repositories.teacher_repository import TeacherRepository
from app.services.attendance_service import AttendanceService
from app.services.class_service import ClassService
from app.services.report_service import ReportService
from app.services.student_service import StudentService
from app.services.teacher_service import TeacherService


@dataclass(eq=False)
class ServiceContainer:
    """Lazily builds the service graph for a single unit of work.

    All services share the same :class:`AsyncSession`, so a request either
    commits as a whole or rolls back as a whole.  Each service is built at most
    once per container thanks to :func:`functools.cached_property`.
    """

    session: AsyncSession
    settings: Settings | None = None

    def __post_init__(self) -> None:
        """Fall back to the process settings singleton when none was injected."""
        self.settings = self.settings or get_settings()

    # --------------------------------------------------------- repositories --

    @cached_property
    def teacher_repository(self) -> TeacherRepository:
        """Data access for teacher accounts."""
        return TeacherRepository(self.session)

    @cached_property
    def class_repository(self) -> ClassRepository:
        """Data access for classes."""
        return ClassRepository(self.session)

    @cached_property
    def student_repository(self) -> StudentRepository:
        """Data access for students."""
        return StudentRepository(self.session)

    @cached_property
    def attendance_repository(self) -> AttendanceRepository:
        """Data access for attendance sessions, records and aggregates."""
        return AttendanceRepository(self.session)

    # ------------------------------------------------------------- services --

    @cached_property
    def teachers(self) -> TeacherService:
        """Onboarding and authorisation of Telegram users."""
        return TeacherService(self.teacher_repository, self.settings)

    @cached_property
    def classes(self) -> ClassService:
        """Class creation, renaming, deletion and lookup."""
        return ClassService(self.class_repository, self.attendance_repository)

    @cached_property
    def students(self) -> StudentService:
        """Student enrolment, updates and reference resolution."""
        return StudentService(self.student_repository, self.classes)

    @cached_property
    def attendance(self) -> AttendanceService:
        """The attendance session workflow."""
        return AttendanceService(
            self.attendance_repository,
            self.student_repository,
            self.classes,
            self.students,
        )

    @cached_property
    def reports(self) -> ReportService:
        """Attendance reporting and aggregation."""
        return ReportService(
            self.attendance_repository,
            self.class_repository,
            self.classes,
            self.students,
        )
