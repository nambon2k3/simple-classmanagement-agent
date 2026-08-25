"""JSON API backing the HTML/CSS/JS administrator dashboard.

Every route is a thin adapter: it takes the request body, calls the same
service methods the Streamlit dashboard used, and returns the service's own
Pydantic result.  Domain errors raised by the services are translated to HTTP
status codes by :func:`app.api.errors.register_exception_handlers`, so these
handlers contain no error mapping of their own.
"""

from __future__ import annotations

from datetime import date, time

from fastapi import APIRouter, Query, Request, Response, status
from pydantic import BaseModel

from app.api.deps import AdminContext
from app.core.exceptions import AppError, ValidationError
from app.models.enums import AttendanceStatus
from app.schemas.attendance import GetAttendanceStateInput, StartAttendanceInput
from app.schemas.classroom import (
    ClassInfoInput,
    ClassInfoOutput,
    CreateClassInput,
    CreateClassOutput,
    DeleteClassInput,
    RenameClassInput,
)
from app.schemas.reports import ReportPeriod
from app.schemas.schedule import ScheduleOccurrence
from app.schemas.student import (
    AddStudentInput,
    ImportStudentRow,
    ImportStudentsInput,
    ListStudentsInput,
    RemoveStudentInput,
    SearchStudentInput,
    StudentRead,
    UpdateStudentInput,
)
from app.schemas.tuition import (
    ClassAttendanceSinceOutput,
    SetClassTuitionFeeInput,
    StudentTuitionStatusRow,
    TuitionReportInput,
    TuitionReportOutput,
    TuitionStatusSummary,
)
from app.utils.class_icons import class_icon_data_uri, icon_dir, save_class_icon
from app.utils.datetime_utils import today
from app.utils.roster_file import RosterFileError, parse_roster_file
from app.web.runtime import WEB_CHAT_ID, get_web_runtime

router = APIRouter(prefix="/api", tags=["dashboard"])


# --------------------------------------------------------------- request bodies


class DescriptionRequest(BaseModel):
    """Body for updating a class description."""

    description: str | None = None


class MarkStatusRequest(BaseModel):
    """Body for marking one student in an attendance session."""

    session_id: int
    student_id: int
    status: AttendanceStatus


class MarkRemainingRequest(BaseModel):
    """Body for bulk-marking the unmarked students of a session."""

    session_id: int
    status: AttendanceStatus


class FinishRequest(BaseModel):
    """Body for finalising an attendance session."""

    session_id: int
    default_status: AttendanceStatus = AttendanceStatus.ABSENT


class SessionRequest(BaseModel):
    """Body carrying only a session identifier."""

    session_id: int


class StartAttendanceRequest(BaseModel):
    """Body for opening today's attendance session for a class."""

    class_name: str
    reopen: bool = False


class ScheduleRuleRequest(BaseModel):
    """Body for adding a weekly timetable slot."""

    class_id: int
    weekday: int
    start_time: time
    end_time: time


class RemoveRuleRequest(BaseModel):
    """Body for removing a weekly timetable slot."""

    class_id: int
    rule_id: int


class ExtraSessionRequest(BaseModel):
    """Body for adding a one-off extra class."""

    class_id: int
    session_date: date
    start_time: time
    end_time: time
    note: str | None = None


class MarkCompletedRequest(BaseModel):
    """Body for settling a student's outstanding tuition."""

    class_id: int
    student_id: int


class ChatRequest(BaseModel):
    """Body carrying one natural-language message for the assistant."""

    message: str


# --------------------------------------------------------------- session / meta


@router.get("/me")
async def get_me(ctx: AdminContext) -> dict[str, object]:
    """Identity of the administrator plus assistant availability."""
    _, teacher = ctx
    runtime = get_web_runtime()
    return {
        "display_name": teacher.display_name,
        "groq_enabled": bool(runtime.settings.groq_api_key.get_secret_value()),
        "groq_model": runtime.settings.groq_model,
    }


# --------------------------------------------------------------------- classes


@router.get("/classes")
async def list_classes(ctx: AdminContext) -> list[dict[str, object]]:
    """Every class the administrator owns, with icon availability."""
    services, teacher = ctx
    result = await services.classes.list_classes(teacher.id)
    return [
        {
            **item.model_dump(),
            "has_icon": class_icon_data_uri(item.id) is not None,
        }
        for item in result.classes
    ]


@router.post("/classes", status_code=status.HTTP_201_CREATED)
async def create_class(payload: CreateClassInput, ctx: AdminContext) -> CreateClassOutput:
    """Create a new class."""
    services, teacher = ctx
    return await services.classes.create_class(teacher.id, payload)


@router.get("/classes/{name}/info")
async def class_info(name: str, ctx: AdminContext) -> ClassInfoOutput:
    """Detailed settings for one class."""
    services, teacher = ctx
    return await services.classes.get_class_info(teacher.id, ClassInfoInput(name=name))


@router.post("/classes/rename")
async def rename_class(payload: RenameClassInput, ctx: AdminContext) -> dict[str, object]:
    """Rename a class."""
    services, teacher = ctx
    result = await services.classes.rename_class(teacher.id, payload)
    return {"message": result.message, "classroom": result.classroom.model_dump()}


@router.post("/classes/fee")
async def set_class_fee(payload: SetClassTuitionFeeInput, ctx: AdminContext) -> dict[str, object]:
    """Change a class's daily tuition fee."""
    services, teacher = ctx
    result = await services.classes.set_class_tuition_fee(teacher.id, payload)
    return {"message": result.message}


@router.post("/classes/{class_id}/description")
async def set_class_description(
    class_id: int, payload: DescriptionRequest, ctx: AdminContext
) -> dict[str, object]:
    """Update a class's free-text description."""
    services, teacher = ctx
    description = (payload.description or "").strip() or None
    await services.classes.set_class_description(teacher.id, class_id, description)
    return {"message": "Description updated."}


@router.post("/classes/delete")
async def delete_class(payload: DeleteClassInput, ctx: AdminContext) -> dict[str, object]:
    """Delete a class and everything belonging to it."""
    services, teacher = ctx
    result = await services.classes.delete_class(
        teacher.id, DeleteClassInput(name=payload.name, confirm=True)
    )
    return {
        "message": result.message,
        "deleted_class": result.deleted_class,
        "deleted_students": result.deleted_students,
    }


@router.get("/classes/{class_id}/icon")
async def get_class_icon(class_id: int) -> Response:
    """Serve the uploaded rail icon for a class, or 404 when there is none."""
    for suffix, mime in (
        (".png", "image/png"),
        (".jpg", "image/jpeg"),
        (".jpeg", "image/jpeg"),
        (".webp", "image/webp"),
        (".gif", "image/gif"),
    ):
        path = icon_dir() / f"{class_id}{suffix}"
        if path.is_file():
            return Response(content=path.read_bytes(), media_type=mime)
    return Response(status_code=status.HTTP_404_NOT_FOUND)


@router.post("/classes/{class_id}/icon")
async def upload_class_icon(
    class_id: int,
    request: Request,
    filename: str = Query(description="Original file name, used to pick the image type."),
) -> dict[str, object]:
    """Replace a class's rail icon with the uploaded image bytes."""
    data = await request.body()
    try:
        save_class_icon(class_id, filename, data)
    except ValueError as exc:
        raise ValidationError(str(exc)) from exc
    return {"message": "Icon updated."}


@router.post("/classes/{class_id}/roster")
async def import_roster(
    class_id: int,
    request: Request,
    ctx: AdminContext,
    filename: str = Query(description="Original file name, used to pick the reader."),
    class_name: str = Query(description="Name of the class to enrol everyone into."),
) -> dict[str, object]:
    """Parse an uploaded roster file and enrol its students."""
    services, teacher = ctx
    data = await request.body()
    try:
        parsed = parse_roster_file(filename, data)
    except RosterFileError as exc:
        raise ValidationError(str(exc)) from exc
    rows = [
        ImportStudentRow(
            student_code=row.student_code,
            full_name=row.full_name,
            email=row.email,
            phone=row.phone,
            note=row.note,
        )
        for row in parsed.rows
    ]
    if not rows:
        return {"message": "No students were imported.", "skipped": parsed.problems}
    imported = await services.students.import_students(
        teacher.id, ImportStudentsInput(class_name=class_name, students=rows)
    )
    return {
        "message": imported.message,
        "added": imported.added,
        "skipped": parsed.problems + imported.skipped,
    }


# -------------------------------------------------------------------- students


@router.get("/students")
async def list_students(
    ctx: AdminContext,
    class_name: str = Query(description="Class whose roster to return."),
) -> list[StudentRead]:
    """Roster of one class, ordered by name."""
    services, teacher = ctx
    result = await services.students.list_students(
        teacher.id, ListStudentsInput(class_name=class_name)
    )
    return result.students


@router.post("/students", status_code=status.HTTP_201_CREATED)
async def add_student(payload: AddStudentInput, ctx: AdminContext) -> dict[str, object]:
    """Enrol one student."""
    services, teacher = ctx
    result = await services.students.add_student(teacher.id, payload)
    return {"message": result.message, "student": result.student.model_dump()}


@router.post("/students/search")
async def search_students(payload: SearchStudentInput, ctx: AdminContext) -> list[StudentRead]:
    """Find students by a fragment of name or ID."""
    services, teacher = ctx
    result = await services.students.search_student(teacher.id, payload)
    return result.students


@router.post("/students/update")
async def update_student(payload: UpdateStudentInput, ctx: AdminContext) -> dict[str, object]:
    """Update one student's fields."""
    services, teacher = ctx
    result = await services.students.update_student(teacher.id, payload)
    return {"message": result.message, "student": result.student.model_dump()}


@router.post("/students/remove")
async def remove_student(payload: RemoveStudentInput, ctx: AdminContext) -> dict[str, object]:
    """Remove one student and their attendance history."""
    services, teacher = ctx
    result = await services.students.remove_student(
        teacher.id,
        RemoveStudentInput(
            student=payload.student, class_name=payload.class_name, confirm=True
        ),
    )
    return {"message": result.message}


# ------------------------------------------------------------------ attendance


@router.get("/attendance/today")
async def attendance_today(
    ctx: AdminContext,
    class_name: str = Query(description="Class to load today's roll-call for."),
) -> dict[str, object]:
    """Today's roster plus today's session, when one exists."""
    services, teacher = ctx
    roster = await services.students.list_students(
        teacher.id, ListStudentsInput(class_name=class_name)
    )
    session = await services.attendance.get_session_for_date(teacher.id, class_name, today())
    return {
        "students": [student.model_dump() for student in roster.students],
        "session": session.model_dump(mode="json") if session else None,
    }


@router.post("/attendance/start")
async def start_attendance(payload: StartAttendanceRequest, ctx: AdminContext) -> dict[str, object]:
    """Open (or resume) today's attendance session for a class."""
    services, teacher = ctx
    result = await services.attendance.start_attendance(
        teacher.id,
        StartAttendanceInput(
            class_name=payload.class_name,
            session_date=today().isoformat(),
            reopen=payload.reopen,
        ),
    )
    return {"message": result.message, "session": result.session.model_dump(mode="json")}


@router.post("/attendance/mark")
async def mark_attendance(payload: MarkStatusRequest, ctx: AdminContext) -> dict[str, object]:
    """Record one student's status in a session."""
    services, teacher = ctx
    await services.attendance.set_status_by_ids(
        teacher.id, payload.session_id, payload.student_id, payload.status
    )
    return {"message": "Saved."}


@router.post("/attendance/mark-remaining")
async def mark_remaining(payload: MarkRemainingRequest, ctx: AdminContext) -> dict[str, object]:
    """Bulk-mark the unmarked students of a session."""
    services, teacher = ctx
    result = await services.attendance.mark_remaining_in_session(
        teacher.id, payload.session_id, payload.status
    )
    return {"message": result.message}


@router.post("/attendance/finish")
async def finish_attendance(payload: FinishRequest, ctx: AdminContext) -> dict[str, object]:
    """Finalise a session, defaulting any unmarked student."""
    services, teacher = ctx
    result = await services.attendance.finish_session(
        teacher.id, payload.session_id, default_status=payload.default_status
    )
    rate = round(result.summary.attendance_rate * 100)
    return {
        "message": (
            f"Attendance saved — {result.class_name}. "
            f"{result.summary.present} present, {result.summary.absent} absent. "
            f"Attendance rate: {rate}%."
        )
    }


@router.post("/attendance/cancel")
async def cancel_attendance(payload: SessionRequest, ctx: AdminContext) -> dict[str, object]:
    """Abandon a session without finalising it."""
    services, teacher = ctx
    result = await services.attendance.cancel_session(teacher.id, payload.session_id)
    return {"message": result.message}


@router.get("/attendance/session/{session_id}")
async def attendance_session(session_id: int, ctx: AdminContext) -> dict[str, object]:
    """Full state of one session, for the AI chat attendance board."""
    services, teacher = ctx
    session = await services.attendance.get_session_view(teacher.id, session_id)
    return session.model_dump(mode="json")


@router.get("/attendance/since-payment")
async def attendance_since_payment(
    ctx: AdminContext,
    class_id: int = Query(description="Class to summarise."),
) -> ClassAttendanceSinceOutput:
    """Per-student attendance for every day since the last payment."""
    services, teacher = ctx
    return await services.tuition.attendance_since_payment(teacher.id, class_id)


# --------------------------------------------------------------------- reports


@router.get("/reports/tuition")
async def tuition_report(
    ctx: AdminContext,
    class_name: str | None = Query(default=None, description="Class filter; omit for all."),
    period: ReportPeriod = Query(default=ReportPeriod.THIS_MONTH),
    start_date: str | None = Query(default=None),
    end_date: str | None = Query(default=None),
) -> TuitionReportOutput:
    """Money earned and days taught over a period."""
    services, teacher = ctx
    return await services.tuition.tuition_report(
        teacher.id,
        TuitionReportInput(
            class_name=class_name,
            period=period,
            start_date=start_date,
            end_date=end_date,
        ),
    )


# --------------------------------------------------------------------- tuition


@router.get("/tuition/status")
async def tuition_status(
    ctx: AdminContext,
    class_id: int = Query(description="Class to load payment status for."),
) -> list[StudentTuitionStatusRow]:
    """Per-student Not yet / Completed status for one class."""
    services, teacher = ctx
    return await services.tuition.student_status_rows(teacher.id, class_id)


@router.post("/tuition/mark-completed")
async def tuition_mark_completed(
    payload: MarkCompletedRequest, ctx: AdminContext
) -> dict[str, object]:
    """Settle every outstanding day for one student."""
    services, teacher = ctx
    updated = await services.tuition.mark_student_completed(
        teacher.id, payload.class_id, payload.student_id
    )
    return {"message": f"Marked {updated} unpaid day(s) completed.", "updated": updated}


# -------------------------------------------------------------------- schedule


@router.get("/schedule")
async def schedule(
    ctx: AdminContext,
    class_id: int = Query(description="Class whose timetable to return."),
) -> dict[str, object]:
    """Weekly slots and extra classes for one class."""
    services, teacher = ctx
    rules = await services.schedule.list_rules(teacher.id, class_id)
    extras = await services.schedule.list_extras(teacher.id, class_id)
    return {
        "rules": [rule.model_dump(mode="json") for rule in rules],
        "extras": [extra.model_dump(mode="json") for extra in extras],
    }


@router.post("/schedule/rule", status_code=status.HTTP_201_CREATED)
async def add_schedule_rule(payload: ScheduleRuleRequest, ctx: AdminContext) -> dict[str, object]:
    """Add one recurring weekly slot."""
    services, teacher = ctx
    await services.schedule.add_rule(
        teacher.id, payload.class_id, payload.weekday, payload.start_time, payload.end_time
    )
    return {"message": "Weekly slot added."}


@router.post("/schedule/rule/remove")
async def remove_schedule_rule(payload: RemoveRuleRequest, ctx: AdminContext) -> dict[str, object]:
    """Remove one weekly slot."""
    services, teacher = ctx
    await services.schedule.remove_rule(teacher.id, payload.class_id, payload.rule_id)
    return {"message": "Weekly slot removed."}


@router.post("/schedule/extra", status_code=status.HTTP_201_CREATED)
async def add_extra_class(payload: ExtraSessionRequest, ctx: AdminContext) -> dict[str, object]:
    """Add one one-off extra class."""
    services, teacher = ctx
    note = (payload.note or "").strip() or None
    await services.schedule.add_extra(
        teacher.id,
        payload.class_id,
        payload.session_date,
        payload.start_time,
        payload.end_time,
        note,
    )
    return {"message": "Extra class added."}


@router.get("/schedule/month")
async def schedule_month(
    ctx: AdminContext,
    year: int = Query(description="Calendar year."),
    month: int = Query(ge=1, le=12, description="Calendar month, 1-12."),
) -> list[ScheduleOccurrence]:
    """Every scheduled occurrence in one month, across all classes."""
    services, teacher = ctx
    return await services.schedule.month_occurrences(teacher.id, year, month)


# ------------------------------------------------------------------- dashboard


@router.get("/dashboard/summary")
async def dashboard_summary(ctx: AdminContext) -> TuitionStatusSummary:
    """Completed versus unpaid tuition across every class."""
    services, teacher = ctx
    return await services.tuition.status_summary(teacher.id)


@router.get("/activity")
async def recent_activity(ctx: AdminContext) -> list[dict[str, object]]:
    """Newest changes across classes, students, attendance and tuition."""
    services, teacher = ctx
    entries = await services.activity.recent(teacher.id)
    return [
        {
            "kind": entry.kind.value,
            "badge": entry.kind.badge,
            "text": entry.text,
            "occurred_at": entry.occurred_at.isoformat(),
            "class_name": entry.class_name,
        }
        for entry in entries
    ]


# ------------------------------------------------------------------------ chat


@router.post("/chat")
async def chat(payload: ChatRequest, ctx: AdminContext) -> dict[str, object]:
    """Send one message to the assistant and return its reply."""
    services, teacher = ctx
    runtime = get_web_runtime()
    text = payload.message.strip()[:1500]
    if not text:
        return {"reply": ""}
    state = await runtime.conversations.get_or_create(WEB_CHAT_ID, teacher.id)
    reply = await runtime.agent.run(text, state=state, services=services)
    await runtime.conversations.save(state)
    return {"reply": reply.text}


@router.get("/chat/board")
async def chat_board(ctx: AdminContext) -> dict[str, object] | None:
    """The attendance session currently in the assistant's focus, if any."""
    services, teacher = ctx
    runtime = get_web_runtime()
    state = await runtime.conversations.get(WEB_CHAT_ID)
    if state is None or state.focus_session_id is None:
        result = await services.attendance.get_state(
            teacher.id, GetAttendanceStateInput(class_name=None)
        )
        session = result.session
    else:
        try:
            session = await services.attendance.get_session_view(
                teacher.id, state.focus_session_id
            )
        except AppError:
            session = None
    return session.model_dump(mode="json") if session else None
