"""Add class schedules, extra sessions and a tuition charge ledger.

Revision ID: 20260825_0908
Revises: 20260728_1615
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "20260825_0908"
down_revision = "20260728_1615"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create schedule tables, the tuition ledger, and backfill unpaid charges."""
    op.create_table(
        "class_schedule_rules",
        sa.Column("class_id", sa.BigInteger().with_variant(sa.Integer(), "sqlite"), nullable=False),
        sa.Column("weekday", sa.SmallInteger(), nullable=False),
        sa.Column("start_time", sa.Time(), nullable=False),
        sa.Column("end_time", sa.Time(), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column(
            "id",
            sa.BigInteger().with_variant(sa.Integer(), "sqlite"),
            autoincrement=True,
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["class_id"],
            ["classes.id"],
            name=op.f("fk_class_schedule_rules_class_id_classes"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_class_schedule_rules")),
        sa.UniqueConstraint(
            "class_id",
            "weekday",
            "start_time",
            name="uq_class_schedule_rules_class_id_weekday_start_time",
        ),
    )
    op.create_index(
        op.f("ix_class_schedule_rules_class_id"),
        "class_schedule_rules",
        ["class_id"],
        unique=False,
    )

    op.create_table(
        "class_extra_sessions",
        sa.Column("class_id", sa.BigInteger().with_variant(sa.Integer(), "sqlite"), nullable=False),
        sa.Column("session_date", sa.Date(), nullable=False),
        sa.Column("start_time", sa.Time(), nullable=False),
        sa.Column("end_time", sa.Time(), nullable=False),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column(
            "id",
            sa.BigInteger().with_variant(sa.Integer(), "sqlite"),
            autoincrement=True,
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["class_id"],
            ["classes.id"],
            name=op.f("fk_class_extra_sessions_class_id_classes"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_class_extra_sessions")),
        sa.UniqueConstraint(
            "class_id",
            "session_date",
            name="uq_class_extra_sessions_class_id_session_date",
        ),
    )
    op.create_index(
        op.f("ix_class_extra_sessions_class_id"),
        "class_extra_sessions",
        ["class_id"],
        unique=False,
    )

    tuition_status = postgresql.ENUM(
        "not_yet", "completed", name="tuition_charge_status", create_type=False
    )
    tuition_status.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "tuition_charges",
        sa.Column(
            "student_id", sa.BigInteger().with_variant(sa.Integer(), "sqlite"), nullable=False
        ),
        sa.Column(
            "session_id", sa.BigInteger().with_variant(sa.Integer(), "sqlite"), nullable=False
        ),
        sa.Column("amount_vnd", sa.Integer(), server_default="0", nullable=False),
        sa.Column("status", tuition_status, nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "id",
            sa.BigInteger().with_variant(sa.Integer(), "sqlite"),
            autoincrement=True,
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["student_id"],
            ["students.id"],
            name=op.f("fk_tuition_charges_student_id_students"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["session_id"],
            ["attendance_sessions.id"],
            name=op.f("fk_tuition_charges_session_id_attendance_sessions"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_tuition_charges")),
        sa.UniqueConstraint(
            "student_id",
            "session_id",
            name="uq_tuition_charges_student_id_session_id",
        ),
    )
    op.create_index(op.f("ix_tuition_charges_student_id"), "tuition_charges", ["student_id"])
    op.create_index(op.f("ix_tuition_charges_session_id"), "tuition_charges", ["session_id"])

    op.execute(
        sa.text(
            """
            INSERT INTO tuition_charges (
                student_id, session_id, amount_vnd, status, completed_at, created_at, updated_at
            )
            SELECT
                attendance_records.student_id,
                attendance_records.session_id,
                classes.daily_tuition_fee,
                'not_yet',
                NULL,
                now(),
                now()
            FROM attendance_records
            JOIN attendance_sessions
                ON attendance_sessions.id = attendance_records.session_id
            JOIN classes
                ON classes.id = attendance_sessions.class_id
            WHERE attendance_sessions.status = 'completed'
              AND attendance_records.status IN ('present', 'late')
            """
        )
    )


def downgrade() -> None:
    """Drop the ledger and schedule tables."""
    op.drop_index(op.f("ix_tuition_charges_session_id"), table_name="tuition_charges")
    op.drop_index(op.f("ix_tuition_charges_student_id"), table_name="tuition_charges")
    op.drop_table("tuition_charges")
    sa.Enum(name="tuition_charge_status").drop(op.get_bind(), checkfirst=True)
    op.drop_index(op.f("ix_class_extra_sessions_class_id"), table_name="class_extra_sessions")
    op.drop_table("class_extra_sessions")
    op.drop_index(op.f("ix_class_schedule_rules_class_id"), table_name="class_schedule_rules")
    op.drop_table("class_schedule_rules")
