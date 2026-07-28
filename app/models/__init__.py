"""ORM models.

Every model is re-exported here so that ``Base.metadata`` is fully populated by
a single ``import app.models`` — which is what Alembic's autogenerate and the
test fixtures rely on.
"""

from app.models.attendance import AttendanceRecord, AttendanceSession
from app.models.base import Base
from app.models.classroom import Classroom
from app.models.enums import AttendanceSessionStatus, AttendanceStatus
from app.models.student import Student
from app.models.teacher import Teacher

__all__ = [
    "AttendanceRecord",
    "AttendanceSession",
    "AttendanceSessionStatus",
    "AttendanceStatus",
    "Base",
    "Classroom",
    "Student",
    "Teacher",
]
