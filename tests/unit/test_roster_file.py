"""Reading student rosters out of Excel and CSV uploads."""

from __future__ import annotations

import io

import pytest
from openpyxl import Workbook

from app.utils.roster_file import RosterFileError, parse_roster_file


def _xlsx(rows: list[list[object]]) -> bytes:
    workbook = Workbook()
    sheet = workbook.active
    for row in rows:
        sheet.append(row)
    buffer = io.BytesIO()
    workbook.save(buffer)
    return buffer.getvalue()


def test_excel_with_headers_maps_columns_by_name() -> None:
    data = _xlsx(
        [
            ["Student ID", "Full name", "Email", "Phone", "Note"],
            ["SE001", "Nguyen Van A", "a@example.com", 909123456, "Front row"],
        ]
    )
    parsed = parse_roster_file("roster.xlsx", data)

    assert parsed.problems == []
    assert len(parsed.rows) == 1
    row = parsed.rows[0]
    assert (row.student_code, row.full_name) == ("SE001", "Nguyen Van A")
    assert row.email == "a@example.com"
    assert row.phone == "909123456"
    assert row.note == "Front row"


def test_headers_in_any_order_and_vietnamese_names() -> None:
    data = _xlsx([["Họ tên", "Mã số"], ["Tran Thi B", "SE002"]])
    parsed = parse_roster_file("roster.xlsx", data)

    assert (parsed.rows[0].student_code, parsed.rows[0].full_name) == ("SE002", "Tran Thi B")


def test_file_without_headers_falls_back_to_column_order() -> None:
    data = _xlsx([["SE001", "Nguyen Van A"], ["SE002", "John Smith"]])
    parsed = parse_roster_file("roster.xlsx", data)

    assert [row.student_code for row in parsed.rows] == ["SE001", "SE002"]
    assert [row.full_name for row in parsed.rows] == ["Nguyen Van A", "John Smith"]


def test_csv_is_supported_and_incomplete_rows_are_reported() -> None:
    data = b"Student ID,Full name\nSE001,Nguyen Van A\n,Missing code\n"
    parsed = parse_roster_file("roster.csv", data)

    assert [row.student_code for row in parsed.rows] == ["SE001"]
    assert parsed.problems == ["Row 3: missing student ID."]


def test_blank_rows_are_ignored() -> None:
    data = b"Student ID,Full name\nSE001,Nguyen Van A\n,\nSE002,John Smith\n"
    parsed = parse_roster_file("roster.csv", data)

    assert [row.student_code for row in parsed.rows] == ["SE001", "SE002"]
    assert parsed.problems == []


def test_unsupported_extension_is_rejected() -> None:
    with pytest.raises(RosterFileError, match="xlsx"):
        parse_roster_file("roster.pdf", b"whatever")


def test_empty_file_is_rejected() -> None:
    with pytest.raises(RosterFileError, match="no rows"):
        parse_roster_file("roster.csv", b"")


def test_sheet_without_a_name_column_is_rejected() -> None:
    with pytest.raises(RosterFileError, match="name column"):
        parse_roster_file("roster.csv", b"Only one column\nvalue\n")
