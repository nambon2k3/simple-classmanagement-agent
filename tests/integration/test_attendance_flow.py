"""The end-to-end attendance workflow."""

from __future__ import annotations

from datetime import timedelta

import pytest

from app.core.exceptions import (
    AmbiguousReferenceError,
    AttendanceAlreadyTakenError,
    AttendanceSessionClosedError,
    EmptyClassError,
    NoActiveAttendanceSessionError,
    StudentNotFoundError,
)
from app.models.enums import AttendanceSessionStatus, AttendanceStatus
from app.schemas.attendance import (
    CancelAttendanceInput,
    FinishAttendanceInput,
    GetAttendanceStateInput,
    MarkRemainingInput,
    StartAttendanceInput,
    UpdateAttendanceInput,
)
from app.schemas.classroom import CreateClassInput
from app.schemas.student import AddStudentInput
from app.utils.datetime_utils import today


async def start(services, teacher, class_name: str = "SE401"):
    return await services.attendance.start_attendance(
        teacher.id, StartAttendanceInput(class_name=class_name)
    )


async def test_starting_a_session_lists_the_whole_roster(services, teacher, roster):
    result = await start(services, teacher)
    assert result.resumed is False
    assert len(result.session.entries) == 3
    assert result.session.summary.unmarked == 3
    assert all(entry.status is None for entry in result.session.entries)


async def test_cannot_take_attendance_for_an_empty_class(services, teacher, classroom):
    with pytest.raises(EmptyClassError):
        await start(services, teacher)


async def test_starting_twice_resumes_the_same_session(services, teacher, roster):
    first = await start(services, teacher)
    second = await start(services, teacher)
    assert second.resumed is True
    assert second.session.session_id == first.session.session_id


async def test_marking_a_student_by_first_name(services, teacher, roster):
    await start(services, teacher)
    result = await services.attendance.update_attendance(
        teacher.id, UpdateAttendanceInput(student="John", status=AttendanceStatus.ABSENT)
    )
    assert result.status is AttendanceStatus.ABSENT
    assert result.summary.absent == 1
    assert result.summary.unmarked == 2


async def test_marking_the_same_student_twice_overwrites(services, teacher, roster):
    await start(services, teacher)
    for status in (AttendanceStatus.ABSENT, AttendanceStatus.LATE):
        result = await services.attendance.update_attendance(
            teacher.id, UpdateAttendanceInput(student="SE002", status=status)
        )
    assert result.summary.late == 1
    assert result.summary.absent == 0


async def test_marking_needs_no_class_name_once_a_session_is_open(services, teacher, roster):
    await start(services, teacher)
    result = await services.attendance.update_attendance(
        teacher.id,
        UpdateAttendanceInput(student="Alice", status=AttendanceStatus.LATE, class_name=None),
    )
    assert result.summary.late == 1


async def test_marking_without_a_session_is_rejected(services, teacher, roster):
    with pytest.raises(NoActiveAttendanceSessionError):
        await services.attendance.update_attendance(
            teacher.id, UpdateAttendanceInput(student="John", status=AttendanceStatus.ABSENT)
        )


async def test_a_student_outside_the_class_cannot_be_marked(services, teacher, roster):
    await services.classes.create_class(teacher.id, CreateClassInput(name="AI202"))
    await services.students.add_student(
        teacher.id,
        AddStudentInput(class_name="AI202", full_name="Outsider Person", student_code="AI001"),
    )
    await start(services, teacher)
    with pytest.raises(StudentNotFoundError):
        await services.attendance.update_attendance(
            teacher.id,
            UpdateAttendanceInput(student="Outsider Person", status=AttendanceStatus.ABSENT),
        )


async def test_two_open_sessions_require_disambiguation(services, teacher, roster):
    await services.classes.create_class(teacher.id, CreateClassInput(name="AI202"))
    await services.students.add_student(
        teacher.id,
        AddStudentInput(class_name="AI202", full_name="Second Class Person", student_code="AI001"),
    )
    await start(services, teacher, "SE401")
    await start(services, teacher, "AI202")

    with pytest.raises(AmbiguousReferenceError) as error:
        await services.attendance.resolve_active_session(teacher.id)
    assert set(error.value.details["open_classes"]) == {"SE401", "AI202"}


async def test_the_focus_hint_disambiguates_two_open_sessions(services, teacher, roster, classroom):
    await services.classes.create_class(teacher.id, CreateClassInput(name="AI202"))
    await services.students.add_student(
        teacher.id,
        AddStudentInput(class_name="AI202", full_name="Second Class Person", student_code="AI001"),
    )
    await start(services, teacher, "SE401")
    await start(services, teacher, "AI202")

    session = await services.attendance.resolve_active_session(
        teacher.id, preferred_class_id=classroom.id
    )
    assert session.class_id == classroom.id


async def test_mark_remaining_fills_in_everyone_left(services, teacher, roster):
    await start(services, teacher)
    await services.attendance.update_attendance(
        teacher.id, UpdateAttendanceInput(student="John", status=AttendanceStatus.ABSENT)
    )
    result = await services.attendance.mark_remaining(
        teacher.id, MarkRemainingInput(status=AttendanceStatus.PRESENT)
    )
    assert result.updated == 2
    assert result.summary.unmarked == 0
    assert result.summary.present == 2


async def test_finishing_defaults_unmarked_students_to_present(services, teacher, roster):
    await start(services, teacher)
    await services.attendance.update_attendance(
        teacher.id, UpdateAttendanceInput(student="John", status=AttendanceStatus.ABSENT)
    )
    await services.attendance.update_attendance(
        teacher.id, UpdateAttendanceInput(student="Alice", status=AttendanceStatus.LATE)
    )

    result = await services.attendance.finish_attendance(teacher.id, FinishAttendanceInput())
    assert result.summary.present == 1
    assert result.summary.absent == 1
    assert result.summary.late == 1
    assert result.summary.unmarked == 0
    assert result.absent_students == ["John Smith"]
    assert result.late_students == ["Alice Nguyen"]
    assert result.summary.attendance_rate == pytest.approx(2 / 3)


async def test_a_finished_session_cannot_be_edited(services, teacher, roster):
    await start(services, teacher)
    await services.attendance.finish_attendance(teacher.id, FinishAttendanceInput())
    with pytest.raises(NoActiveAttendanceSessionError):
        await services.attendance.update_attendance(
            teacher.id, UpdateAttendanceInput(student="John", status=AttendanceStatus.ABSENT)
        )


async def test_taking_attendance_twice_in_a_day_is_refused(services, teacher, roster):
    await start(services, teacher)
    await services.attendance.finish_attendance(teacher.id, FinishAttendanceInput())
    with pytest.raises(AttendanceAlreadyTakenError) as error:
        await start(services, teacher)
    assert error.value.details["class_name"] == "SE401"


async def test_a_completed_session_can_be_reopened_on_request(services, teacher, roster):
    await start(services, teacher)
    await services.attendance.finish_attendance(teacher.id, FinishAttendanceInput())

    result = await services.attendance.start_attendance(
        teacher.id, StartAttendanceInput(class_name="SE401", reopen=True)
    )
    assert result.resumed is True
    assert result.session.status is AttendanceSessionStatus.OPEN


async def test_attendance_can_be_recorded_for_a_past_date(services, teacher, roster):
    yesterday = today() - timedelta(days=1)
    result = await services.attendance.start_attendance(
        teacher.id,
        StartAttendanceInput(class_name="SE401", session_date=yesterday.isoformat()),
    )
    assert result.session.session_date == yesterday


async def test_get_session_for_date_does_not_return_another_day(services, teacher, roster):
    yesterday = today() - timedelta(days=1)
    old = await services.attendance.start_attendance(
        teacher.id,
        StartAttendanceInput(class_name="SE401", session_date=yesterday.isoformat()),
    )
    assert await services.attendance.get_session_for_date(teacher.id, "SE401", today()) is None
    loaded = await services.attendance.get_session_for_date(teacher.id, "SE401", yesterday)
    assert loaded is not None
    assert loaded.session_id == old.session.session_id
    assert loaded.session_date == yesterday


async def test_cancelling_leaves_nothing_final(services, teacher, roster):
    await start(services, teacher)
    await services.attendance.cancel_attendance(teacher.id, CancelAttendanceInput())

    state = await services.attendance.get_state(teacher.id, GetAttendanceStateInput())
    assert state.has_active_session is False

    # A cancelled day can be started again without the "already taken" error.
    again = await start(services, teacher)
    assert again.session.status is AttendanceSessionStatus.OPEN


async def test_state_reports_the_open_session(services, teacher, roster):
    started = await start(services, teacher)
    state = await services.attendance.get_state(teacher.id, GetAttendanceStateInput())
    assert state.has_active_session is True
    assert state.session.session_id == started.session.session_id


async def test_buttons_and_typing_reach_the_same_session(services, teacher, roster):
    """The inline-keyboard path and the conversational path must agree."""
    started = await start(services, teacher)
    student_id = started.session.entries[0].student_id

    view = await services.attendance.set_status_by_ids(
        teacher.id, started.session.session_id, student_id, AttendanceStatus.LATE
    )
    assert view.summary.late == 1

    typed = await services.attendance.update_attendance(
        teacher.id,
        UpdateAttendanceInput(
            student=started.session.entries[0].student_code, status=AttendanceStatus.PRESENT
        ),
    )
    assert typed.summary.late == 0
    assert typed.summary.present == 1


async def test_buttons_cannot_touch_a_closed_session(services, teacher, roster):
    started = await start(services, teacher)
    await services.attendance.finish_session(teacher.id, started.session.session_id)

    with pytest.raises(AttendanceSessionClosedError):
        await services.attendance.set_status_by_ids(
            teacher.id,
            started.session.session_id,
            started.session.entries[0].student_id,
            AttendanceStatus.ABSENT,
        )


async def test_complete_teaching_day_marks_every_student_present(services, teacher, roster, classroom):
    result = await services.attendance.complete_teaching_day(teacher.id, classroom.id)
    assert result.summary.present == 3
    assert result.summary.absent == 0
    assert result.summary.unmarked == 0
    loaded = await services.attendance.get_session_for_date(teacher.id, "SE401", today())
    assert loaded is not None
    assert loaded.status is AttendanceSessionStatus.COMPLETED
    assert all(entry.status is AttendanceStatus.PRESENT for entry in loaded.entries)


async def test_complete_teaching_day_overwrites_existing_absences(services, teacher, roster, classroom):
    await start(services, teacher)
    await services.attendance.update_attendance(
        teacher.id, UpdateAttendanceInput(student="John", status=AttendanceStatus.ABSENT)
    )
    result = await services.attendance.complete_teaching_day(teacher.id, classroom.id)
    assert result.summary.present == 3
    assert result.summary.absent == 0
    assert result.absent_students == []


async def test_complete_teaching_day_refuses_an_already_finished_day(services, teacher, roster, classroom):
    await services.attendance.complete_teaching_day(teacher.id, classroom.id)
    with pytest.raises(AttendanceAlreadyTakenError):
        await services.attendance.complete_teaching_day(teacher.id, classroom.id)


async def test_cancel_teaching_day_marks_every_student_absent(services, teacher, roster, classroom):
    result = await services.attendance.cancel_teaching_day(teacher.id, classroom.id)
    assert result.summary.present == 0
    assert result.summary.absent == 3
    loaded = await services.attendance.get_session_for_date(teacher.id, "SE401", today())
    assert loaded is not None
    assert loaded.status is AttendanceSessionStatus.COMPLETED
    assert all(entry.status is AttendanceStatus.ABSENT for entry in loaded.entries)
    _completed, cancelled = await services.attendance.finalised_class_days(
        teacher.id, today(), today()
    )
    assert (classroom.id, today()) in cancelled


async def test_cancel_teaching_day_overwrites_existing_presents(services, teacher, roster, classroom):
    await start(services, teacher)
    await services.attendance.update_attendance(
        teacher.id, UpdateAttendanceInput(student="John", status=AttendanceStatus.PRESENT)
    )
    result = await services.attendance.cancel_teaching_day(teacher.id, classroom.id)
    assert result.summary.absent == 3
    assert result.summary.present == 0


async def test_cancel_teaching_day_refuses_an_already_finished_day(services, teacher, roster, classroom):
    await services.attendance.complete_teaching_day(teacher.id, classroom.id)
    with pytest.raises(AttendanceAlreadyTakenError):
        await services.attendance.cancel_teaching_day(teacher.id, classroom.id)


async def test_buttons_cannot_reach_another_teachers_session(services, teacher, roster):
    from app.schemas.teacher import TeacherIdentity

    started = await start(services, teacher)
    intruder = await services.teachers.get_or_create(
        TeacherIdentity(telegram_id=555, full_name="Intruder")
    )
    with pytest.raises(NoActiveAttendanceSessionError):
        await services.attendance.set_status_by_ids(
            intruder.id,
            started.session.session_id,
            started.session.entries[0].student_id,
            AttendanceStatus.ABSENT,
        )
