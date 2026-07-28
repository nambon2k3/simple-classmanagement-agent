"""Repository layer: the only place that builds SQL."""

from app.repositories.attendance_repository import AttendanceRepository
from app.repositories.base import BaseRepository
from app.repositories.class_repository import ClassRepository
from app.repositories.student_repository import StudentRepository
from app.repositories.teacher_repository import TeacherRepository

__all__ = [
    "AttendanceRepository",
    "BaseRepository",
    "ClassRepository",
    "StudentRepository",
    "TeacherRepository",
]
