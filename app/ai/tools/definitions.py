"""Registration of every tool the language model may call.

Handlers here are deliberately thin: they unpack the context, call one service
method and hand the result back.  All validation, authorisation and business
logic stays in the service layer, so the exact same behaviour is available to
the REST API and to the tests without going through a model.
"""

from __future__ import annotations

from app.ai.tools.registry import ToolContext, ToolRegistry
from app.schemas.attendance import (
    CancelAttendanceInput,
    FinishAttendanceInput,
    FinishAttendanceOutput,
    GetAttendanceStateInput,
    GetAttendanceStateOutput,
    MarkRemainingInput,
    MarkRemainingOutput,
    StartAttendanceInput,
    StartAttendanceOutput,
    UpdateAttendanceInput,
    UpdateAttendanceOutput,
)
from app.schemas.classroom import (
    ClassInfoInput,
    ClassInfoOutput,
    CreateClassInput,
    CreateClassOutput,
    DeleteClassInput,
    DeleteClassOutput,
    ListClassesInput,
    ListClassesOutput,
    RenameClassInput,
    RenameClassOutput,
)
from app.schemas.common import OperationResult
from app.schemas.reports import (
    AttendanceReportInput,
    AttendanceReportOutput,
    MonthlySummaryInput,
    MonthlySummaryOutput,
    StudentAttendanceReportInput,
    StudentAttendanceReportOutput,
    StudentsByStatusInput,
    StudentsByStatusOutput,
)
from app.schemas.student import (
    AddStudentInput,
    AddStudentOutput,
    ListStudentsInput,
    ListStudentsOutput,
    RemoveStudentInput,
    RemoveStudentOutput,
    SearchStudentInput,
    SearchStudentOutput,
    UpdateStudentInput,
    UpdateStudentOutput,
)
from app.schemas.tuition import (
    SetClassTuitionFeeInput,
    SetClassTuitionFeeOutput,
    TeachingDaysReportInput,
    TeachingDaysReportOutput,
    TuitionReportInput,
    TuitionReportOutput,
)

#: Key under which a handler publishes the attendance session it just touched,
#: so the presentation layer can render or refresh the attendance board.
EMIT_ATTENDANCE_SESSION = "attendance_session"
#: Key set when a session was finalised or abandoned, clearing the focus.
EMIT_ATTENDANCE_CLOSED = "attendance_closed"


# ------------------------------------------------------------------ classes --


async def _create_class(context: ToolContext, payload: CreateClassInput) -> CreateClassOutput:
    return await context.services.classes.create_class(context.teacher_id, payload)


async def _rename_class(context: ToolContext, payload: RenameClassInput) -> RenameClassOutput:
    return await context.services.classes.rename_class(context.teacher_id, payload)


async def _delete_class(context: ToolContext, payload: DeleteClassInput) -> DeleteClassOutput:
    result = await context.services.classes.delete_class(context.teacher_id, payload)
    context.focus_class_id = None
    context.focus_session_id = None
    return result


async def _list_classes(context: ToolContext, _: ListClassesInput) -> ListClassesOutput:
    return await context.services.classes.list_classes(context.teacher_id)


async def _class_info(context: ToolContext, payload: ClassInfoInput) -> ClassInfoOutput:
    return await context.services.classes.get_class_info(context.teacher_id, payload)


# ----------------------------------------------------------------- students --


async def _add_student(context: ToolContext, payload: AddStudentInput) -> AddStudentOutput:
    return await context.services.students.add_student(context.teacher_id, payload)


async def _remove_student(context: ToolContext, payload: RemoveStudentInput) -> RemoveStudentOutput:
    return await context.services.students.remove_student(context.teacher_id, payload)


async def _update_student(context: ToolContext, payload: UpdateStudentInput) -> UpdateStudentOutput:
    return await context.services.students.update_student(context.teacher_id, payload)


async def _list_students(context: ToolContext, payload: ListStudentsInput) -> ListStudentsOutput:
    return await context.services.students.list_students(context.teacher_id, payload)


async def _search_student(context: ToolContext, payload: SearchStudentInput) -> SearchStudentOutput:
    return await context.services.students.search_student(context.teacher_id, payload)


# --------------------------------------------------------------- attendance --


async def _start_attendance(
    context: ToolContext, payload: StartAttendanceInput
) -> StartAttendanceOutput:
    result = await context.services.attendance.start_attendance(context.teacher_id, payload)
    context.focus_class_id = result.session.class_id
    context.focus_session_id = result.session.session_id
    context.emitted[EMIT_ATTENDANCE_SESSION] = result.session
    return result


async def _update_attendance(
    context: ToolContext, payload: UpdateAttendanceInput
) -> UpdateAttendanceOutput:
    return await context.services.attendance.update_attendance(
        context.teacher_id, payload, preferred_class_id=context.focus_class_id
    )


async def _mark_remaining(context: ToolContext, payload: MarkRemainingInput) -> MarkRemainingOutput:
    return await context.services.attendance.mark_remaining(
        context.teacher_id, payload, preferred_class_id=context.focus_class_id
    )


async def _finish_attendance(
    context: ToolContext, payload: FinishAttendanceInput
) -> FinishAttendanceOutput:
    result = await context.services.attendance.finish_attendance(
        context.teacher_id, payload, preferred_class_id=context.focus_class_id
    )
    context.focus_session_id = None
    context.emitted[EMIT_ATTENDANCE_CLOSED] = True
    return result


async def _cancel_attendance(
    context: ToolContext, payload: CancelAttendanceInput
) -> OperationResult:
    result = await context.services.attendance.cancel_attendance(
        context.teacher_id, payload, preferred_class_id=context.focus_class_id
    )
    context.focus_session_id = None
    context.emitted[EMIT_ATTENDANCE_CLOSED] = True
    return result


async def _attendance_state(
    context: ToolContext, payload: GetAttendanceStateInput
) -> GetAttendanceStateOutput:
    return await context.services.attendance.get_state(
        context.teacher_id, payload, preferred_class_id=context.focus_class_id
    )


# ------------------------------------------------------------------ reports --


async def _attendance_report(
    context: ToolContext, payload: AttendanceReportInput
) -> AttendanceReportOutput:
    return await context.services.reports.attendance_report(context.teacher_id, payload)


async def _student_report(
    context: ToolContext, payload: StudentAttendanceReportInput
) -> StudentAttendanceReportOutput:
    return await context.services.reports.student_attendance_report(context.teacher_id, payload)


async def _monthly_summary(
    context: ToolContext, payload: MonthlySummaryInput
) -> MonthlySummaryOutput:
    return await context.services.reports.monthly_summary(context.teacher_id, payload)


async def _students_by_status(
    context: ToolContext, payload: StudentsByStatusInput
) -> StudentsByStatusOutput:
    return await context.services.reports.students_by_status(context.teacher_id, payload)


# ------------------------------------------------------------------- tuition --


async def _set_class_tuition_fee(
    context: ToolContext, payload: SetClassTuitionFeeInput
) -> SetClassTuitionFeeOutput:
    return await context.services.tuition.set_class_tuition_fee(context.teacher_id, payload)


async def _tuition_report(
    context: ToolContext, payload: TuitionReportInput
) -> TuitionReportOutput:
    return await context.services.tuition.tuition_report(context.teacher_id, payload)


async def _teaching_days_report(
    context: ToolContext, payload: TeachingDaysReportInput
) -> TeachingDaysReportOutput:
    return await context.services.tuition.teaching_days_report(context.teacher_id, payload)


def build_registry() -> ToolRegistry:
    """Create a registry populated with every available tool.

    Returns:
        A fully wired :class:`ToolRegistry`.  Cheap to build, so callers may
        create one per process or per request.
    """
    registry = ToolRegistry()

    registry.register(
        "create_class",
        (
            "Create a new class for the teacher. Use when they ask to create, add or "
            "open a class. Pass daily_tuition_fee on this same call when they also "
            "give a fee — do not use set_class_tuition_fee until the class exists."
        ),
        CreateClassInput,
        _create_class,
    )
    registry.register(
        "rename_class",
        "Rename an existing class.",
        RenameClassInput,
        _rename_class,
    )
    registry.register(
        "delete_class",
        (
            "Delete a class together with its students and attendance history. "
            "Destructive: call it once without 'confirm' to obtain the confirmation "
            "prompt, then again with confirm=true after the teacher agrees."
        ),
        DeleteClassInput,
        _delete_class,
    )
    registry.register(
        "list_classes",
        (
            "List every class the teacher owns, including student counts and each "
            "class's daily tuition fee. Use for 'list my classes', 'show classes "
            "and tuition fees', or 'what fee does each class have'."
        ),
        ListClassesInput,
        _list_classes,
    )
    registry.register(
        "get_class_info",
        (
            "Show details about one named class, including attendance activity and "
            "its daily tuition fee."
        ),
        ClassInfoInput,
        _class_info,
    )

    registry.register(
        "add_student",
        (
            "Enrol a new student into a class roster. Use for 'add student …', "
            "'register … to class …', or 'student … with code …'. Requires class_name, "
            "full_name, and student_code. Do not use for attendance marking."
        ),
        AddStudentInput,
        _add_student,
    )
    registry.register(
        "remove_student",
        (
            "Remove a student from their class, deleting their attendance history. "
            "Destructive: call once without 'confirm', then again with confirm=true "
            "after the teacher agrees."
        ),
        RemoveStudentInput,
        _remove_student,
    )
    registry.register(
        "update_student",
        "Change a student's name, student ID or contact details. Only send the fields "
        "that should change.",
        UpdateStudentInput,
        _update_student,
    )
    registry.register(
        "list_students",
        "List every student in a class.",
        ListStudentsInput,
        _list_students,
    )
    registry.register(
        "search_student",
        "Find students by a partial name or student ID, optionally within one class.",
        SearchStudentInput,
        _search_student,
    )

    registry.register(
        "start_attendance",
        (
            "Open an attendance session for a class so the teacher can start marking "
            "students. Defaults to today. Also use when the teacher says they are teaching "
            "or will teach a class today, for example 'today I teach SE401'. The bot shows "
            "tap-to-mark buttons afterwards."
        ),
        StartAttendanceInput,
        _start_attendance,
    )
    registry.register(
        "update_attendance",
        (
            "Mark attendance for a student who is already enrolled. Use for "
            "'John absent', 'Alice late', or 'David present'. Requires status. "
            "Never use this to add a new student to a class."
        ),
        UpdateAttendanceInput,
        _update_attendance,
    )
    registry.register(
        "mark_remaining_students",
        "Apply one status to every student who has not been marked yet in the open session.",
        MarkRemainingInput,
        _mark_remaining,
    )
    registry.register(
        "finish_attendance",
        (
            "Finalise the open attendance session and return a summary. Use for 'done', "
            "'finish attendance' or 'that's everyone'. Students left unmarked are recorded "
            "with default_status_for_unmarked."
        ),
        FinishAttendanceInput,
        _finish_attendance,
    )
    registry.register(
        "cancel_attendance",
        "Abandon the open attendance session without saving it as final.",
        CancelAttendanceInput,
        _cancel_attendance,
    )
    registry.register(
        "get_attendance_state",
        "Check whether an attendance session is currently open and who has been marked.",
        GetAttendanceStateInput,
        _attendance_state,
    )

    registry.register(
        "attendance_report",
        (
            "Attendance totals (present/absent/late counts) for a class, or for every "
            "class, over a period. Use for 'attendance report for SE401' or 'how was "
            "attendance this week'. Not for listing classes or their tuition fees — "
            "use list_classes for that. Omit class_name to cover every class."
        ),
        AttendanceReportInput,
        _attendance_report,
    )
    registry.register(
        "student_attendance_report",
        "One student's attendance record over a period, including a day-by-day history.",
        StudentAttendanceReportInput,
        _student_report,
    )
    registry.register(
        "monthly_attendance_summary",
        "Per-student attendance totals for one class over a month, worst attendance first.",
        MonthlySummaryInput,
        _monthly_summary,
    )
    registry.register(
        "list_students_by_status",
        (
            "List every time a status was recorded in a period. Use for 'who was absent "
            "today' or 'how many students were absent this week'."
        ),
        StudentsByStatusInput,
        _students_by_status,
    )

    registry.register(
        "set_class_tuition_fee",
        (
            "Set the daily tuition fee for a class in VND. Every student is charged this "
            "amount for each day they attend (present or late). Absent days are free."
        ),
        SetClassTuitionFeeInput,
        _set_class_tuition_fee,
    )
    registry.register(
        "tuition_report",
        (
            "Calculate tuition *owed from attendance* over a period. Students are "
            "charged the class daily fee for each attended day; absent days cost "
            "nothing. Use for 'tuition for SE401 this month' or 'how much do "
            "students owe in July'. To list configured daily fees, use list_classes "
            "instead."
        ),
        TuitionReportInput,
        _tuition_report,
    )
    registry.register(
        "teaching_days_report",
        (
            "Count how many days the teacher held class (completed attendance sessions) "
            "over a period, broken down by class."
        ),
        TeachingDaysReportInput,
        _teaching_days_report,
    )

    return registry
