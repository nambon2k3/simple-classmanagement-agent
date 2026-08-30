# Graph Report - simple-classmanagement-agent  (2026-08-30)

## Corpus Check
- 124 files · ~51,959 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1766 nodes · 4715 edges · 87 communities (78 shown, 9 thin omitted)
- Extraction: 88% EXTRACTED · 12% INFERRED · 0% AMBIGUOUS · INFERRED: 589 edges (avg confidence: 0.52)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `1f756474`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- AttendanceStatus
- exceptions.py
- register_exception_handlers
- TuitionChargeRepository
- AttendanceService
- AttendanceRepository
- CreateClassInput
- el
- student_service.py
- Classroom
- admin.py
- ToolOutput
- 20260830_2115_class_images_in_database.py
- activity_service.py
- parse_roster_file
- schemas/attendance.py
- definitions.py
- test_agent.py
- test_registry.py
- test_text.py
- AttendanceSessionStatus
- ClassRepository
- StudentRepository
- ScheduleService
- schedule_service.py
- test_tool_schema.py
- registry.py
- .__init__
- class_service.py
- test_reports.py
- ai/tools/ Registry Validation Boundary
- .flush
- ConversationState
- today
- ollama.py
- Settings
- AdminContext
- container.py
- readiness
- ScheduleRepository
- test_activity_feed.py
- ServiceContainer
- ToolRegistry
- groq.py
- Code Review Skill
- validate_class_image
- env.py
- ToolSpec
- build_openai_tool_schema
- ConversationStore
- attendance_service.py
- wait_for_db.py
- StudentRead
- test_schedule.py
- 20260727_1445_initial_schema.py
- Attendance Session Per Class Per Day
- Grill Me Skill
- validate_meaningful_name
- ScheduleRuleRead
- .__repr__
- schemas/__init__.py
- get_class_icon
- test_attendance_flow.py
- test_student_service.py
- .sync_database_url
- .display_label
- agent.py
- get_web_runtime
- .format
- _dashboard_shell
- conftest.py
- AttendanceSession
- web/__init__.py
- 20260825_0908_schedule_and_tuition_charges.py
- _pg_enum
- _pg_enum
- ClassService
- class-management
- AppError
- .__init__

## God Nodes (most connected - your core abstractions)
1. `AttendanceStatus` - 89 edges
2. `ToolOutput` - 85 edges
3. `ToolInput` - 80 edges
4. `OperationResult` - 56 edges
5. `Classroom` - 53 edges
6. `AttendanceService` - 52 edges
7. `AttendanceRepository` - 50 edges
8. `Student` - 49 edges
9. `today()` - 49 edges
10. `el()` - 49 edges

## Surprising Connections (you probably didn't know these)
- `db PostgreSQL Service` --semantically_similar_to--> `PostgreSQL`  [INFERRED] [semantically similar]
  docker-compose.yml → README.md
- `FakeResponse` --uses--> `AssistantAgent`  [INFERRED]
  tests/integration/test_agent.py → app/ai/agent.py
- `ScriptedClient` --uses--> `AssistantAgent`  [INFERRED]
  tests/integration/test_agent.py → app/ai/agent.py
- `FakeResponse` --uses--> `ConversationState`  [INFERRED]
  tests/integration/test_agent.py → app/ai/memory.py
- `ScriptedClient` --uses--> `ConversationState`  [INFERRED]
  tests/integration/test_agent.py → app/ai/memory.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Two-Axis Parallel Code Review Flow** — _agents_skills_code_review_skill_code_review, _agents_skills_code_review_skill_standards_axis, _agents_skills_code_review_skill_spec_axis, _agents_skills_code_review_skill_parallel_sub_agents, _agents_skills_code_review_skill_fixed_point [EXTRACTED 1.00]
- **Telegram-to-PostgreSQL Request Path** — readme_telegram_layer, readme_ai_agent_layer, readme_tools_registry, readme_services_layer, readme_repositories_layer, readme_postgresql [EXTRACTED 1.00]
- **Docker Compose Deploy Stack** — docker_compose_db, docker_compose_migrate, docker_compose_api [EXTRACTED 1.00]

## Communities (87 total, 9 thin omitted)

### Community 0 - "AttendanceStatus"
Cohesion: 0.08
Nodes (35): AttendanceStatus, Icon used when rendering the status in the UI., Human-readable label, e.g. ``"Late"``., Whether the status contributes to the attendance rate. Late students were in…, How a student was accounted for in a single attendance session., AttendanceEntry, AttendanceSummary, One student's state inside an attendance session. (+27 more)

### Community 1 - "exceptions.py"
Cohesion: 0.07
Nodes (27): http_status_for(), HTTP translation of domain errors. The API surface reuses the same exception…, Map a domain error onto an HTTP status code., AttendanceAlreadyTakenError, AttendanceSessionNotFoundError, ClassAlreadyExistsError, ConfirmationRequiredError, ConflictError (+19 more)

### Community 2 - "register_exception_handlers"
Cohesion: 0.33
Nodes (4): FastAPI, Install the application-wide exception handlers., register_exception_handlers(), HTTP API: health probes and the administrator dashboard.

### Community 3 - "TuitionChargeRepository"
Cohesion: 0.09
Nodes (14): date, datetime, Select, Set the amount on unpaid charges for a class to the current daily fee. Returns:…, Mark every unpaid charge for the student in this class as paid. Returns: Number…, Create or refresh charges after a session is finished. Completed (paid) rows…, Queries over billed attendance days., Every charge attached to one attendance session. (+6 more)

### Community 4 - "AttendanceService"
Cohesion: 0.07
Nodes (31): NoActiveAttendanceSessionError, No attendance session is currently open., AttendanceSessionRead, FinishAttendanceOutput, Summary produced when a session is finalised., Full state of an attendance session., AttendanceService, date (+23 more)

### Community 5 - "AttendanceRepository"
Cohesion: 0.06
Nodes (23): AttendanceRepository, date, Dates a class actually met, oldest first, ignoring cancelled days., Every ``(student_id, date, status)`` mark for a class, oldest first., Total number of attendance sessions ever held for a class., Date of the most recent session for a class, or ``None`` if none., ``(class_id, date, note)`` for finalised teaching days in ``start``..``end``., Fetch one student's record within a session. (+15 more)

### Community 6 - "CreateClassInput"
Cohesion: 0.11
Nodes (20): _create_class(), CreateClassInput, CreateClassOutput, Arguments for ``create_class``., Result of creating a class., Arguments for ``rename_class``., RenameClassInput, The minimal identity used to onboard a teacher. (+12 more)

### Community 7 - "el"
Cohesion: 0.12
Nodes (65): api, apiFetch(), apiUpload(), errorMessage(), boot(), attendanceRate(), fmtDate(), initials() (+57 more)

### Community 8 - "student_service.py"
Cohesion: 0.11
Nodes (23): AmbiguousReferenceError, AmbiguousStudentError, DuplicateStudentError, The student ID is already taken within the class., The reference matched more than one student., A human reference matched several records and needs disambiguation., ImportStudentsOutput, Result of a roster import. (+15 more)

### Community 9 - "Classroom"
Cohesion: 0.12
Nodes (36): AttendanceRecord, Attendance ORM models., The status of one student within one attendance session., Base, IdMixin, Declarative base and shared column mixins., Base class for every ORM model., Surrogate integer primary key. (+28 more)

### Community 10 - "admin.py"
Cohesion: 0.08
Nodes (39): attendance_session(), attendance_since_payment(), class_info(), dashboard_summary(), dashboard_today(), list_classes(), date, get (+31 more)

### Community 11 - "ToolOutput"
Cohesion: 0.09
Nodes (41): Base class for arguments the language model supplies to a tool.…, Treat ``""`` as omitted — local models often send empty strings for optional…, Base class for values a tool returns to the language model., ToolInput, ToolOutput, DateRange, StrEnum, Named date ranges the model can request without doing date arithmetic. Letting… (+33 more)

### Community 12 - "20260830_2115_class_images_in_database.py"
Cohesion: 0.40
Nodes (4): downgrade(), Add deferred image columns persisted with the rest of the database., Remove class image columns., upgrade()

### Community 13 - "activity_service.py"
Cohesion: 0.17
Nodes (10): _is_edit(), Build the recent-activity feed shown on the administrator home page., Whether ``updated`` is late enough after ``created`` to be a real edit., Return the newest changes across classes, students, roll-calls and payments., Completed versus unpaid tuition across every class., format_vnd(), VND formatting helpers., Format an integer amount as Vietnamese đồng with dot thousands separators. (+2 more)

### Community 14 - "parse_roster_file"
Cohesion: 0.12
Nodes (27): _cell_text(), _header_mapping(), parse_roster_file(), Read a student roster out of an uploaded Excel or CSV file. Teachers keep…, Render a spreadsheet cell as text, keeping phone numbers intact., Map a raw table onto roster rows, skipping blanks and reporting gaps., Map column index to field name, or ``None`` when this is not a header., One student parsed out of the uploaded file. (+19 more)

### Community 15 - "schemas/attendance.py"
Cohesion: 0.10
Nodes (33): Attendance read models and tool contracts., Arguments for ``start_attendance``., StartAttendanceInput, Shared Pydantic base classes and reusable field types. These types are the…, Reporting tool contracts., Tuition billing tool contracts., Arguments for ``set_class_tuition_fee``., Arguments for ``tuition_report``. Answers questions like "tuition for SE401 in… (+25 more)

### Community 16 - "definitions.py"
Cohesion: 0.08
Nodes (53): _add_student(), _attendance_report(), _attendance_state(), build_registry(), _cancel_attendance(), _finish_attendance(), _list_classes(), _list_students() (+45 more)

### Community 17 - "test_agent.py"
Cohesion: 0.16
Nodes (28): FakeResponse, make_agent(), Any, The agent's tool-calling loop, driven by a scripted model. The Groq client is…, A model stuck in a tool loop must not spin forever., John absent' works because the focus hint identifies the session., Mimics a Groq ``/chat/completions`` assistant message., Local models often apologise about tools even after they ran. (+20 more)

### Community 18 - "test_registry.py"
Cohesion: 0.13
Nodes (12): context(), crash(), echo(), EchoInput, EchoOutput, explode(), fixture, Tests for the tool registry — the validation boundary around the model. (+4 more)

### Community 19 - "test_text.py"
Cohesion: 0.13
Nodes (27): find_matches(), normalize(), Text normalisation and fuzzy-matching helpers. Teachers refer to students the…, Shorten ``value`` to ``limit`` characters, appending ``suffix`` if cut., Remove diacritics so ``"Nguyễn"`` and ``"Nguyen"`` compare equal., Casefold, strip accents and collapse whitespace for comparison., Return a 0..1 similarity ratio between two normalised strings., Rank ``candidates`` against ``query`` using a tiered matching strategy. Tiers… (+19 more)

### Community 20 - "AttendanceSessionStatus"
Cohesion: 0.12
Nodes (16): AttendanceSessionStatus, StrEnum, Lifecycle of an attendance session., Whether a billed attendance day has been paid., Teacher-facing status, e.g. ``"Not yet"``., TuitionChargeStatus, ActivityRepository, datetime (+8 more)

### Community 21 - "ClassRepository"
Cohesion: 0.13
Nodes (11): ClassRepository, Select, Queries scoped to a single teacher's classes. Every method takes ``teacher_id``…, Fetch one class by id, scoped to its owner., Fetch a class by its name, case-insensitively., Return every class owned by the teacher, alphabetically., Return each class paired with its student count. Uses a single grouped outer…, Fetch one class including its deferred image blob. (+3 more)

### Community 22 - "StudentRepository"
Cohesion: 0.13
Nodes (11): Select, Queries scoped to the students inside a teacher's classes., Base query joining through ``classes`` to enforce ownership., Fetch one student by id, scoped to the owning teacher., Fetch a student together with their class., Fetch a student by their code within one class., Find every student with this code across all of a teacher's classes. Codes are…, Return the roster of a class ordered by name. (+3 more)

### Community 23 - "ScheduleService"
Cohesion: 0.17
Nodes (9): Weekly timetable and extra sessions., date, Delete a one-off extra class., Expand weekly rules and extras onto the days of ``year``/``month``., Return the class or raise if the teacher does not own it., Maintain repeating slots and expand them onto a month calendar., Delete a weekly slot., One-off extra classes for an owned class. (+1 more)

### Community 24 - "schedule_service.py"
Cohesion: 0.18
Nodes (14): A weekly slot or extra session already exists for that class., ScheduleConflictError, ExtraSessionRead, A one-off extra class., _extra_read(), time, Weekly timetable and extra-session business logic., Schedule a one-off extra class. Raises: ScheduleConflictError: If that class… (+6 more)

### Community 25 - "test_tool_schema.py"
Cohesion: 0.15
Nodes (20): build_tool_schema(), Build a JSON schema for a tool's input model. Args: model: The Pydantic model…, _assert_llm(), Colour, Nested, BaseModel, StrEnum, Tests for the Pydantic to JSON-schema converter used by LLM tools. (+12 more)

### Community 26 - "registry.py"
Cohesion: 0.12
Nodes (19): _clip_payload(), _decode_arguments(), _describe_validation_error(), _error(), Tool registry: the only bridge between the language model and the backend. The…, Return a tool by name, or ``None`` when it is not registered., Validate and run a tool call. Args: name: Tool the model asked for. arguments:…, Turn the API's argument payload into a dict. Raises: ToolInputError: If the… (+11 more)

### Community 27 - ".__init__"
Cohesion: 0.40
Nodes (3): Any, Create the error. Args: message: Teacher-safe explanation. Falls back to…, Serialise the error for tool output or an HTTP error body.

### Community 28 - "class_service.py"
Cohesion: 0.07
Nodes (34): _class_info(), _delete_class(), _rename_class(), ClassInfoInput, ClassInfoOutput, ClassRead, DeleteClassInput, DeleteClassOutput (+26 more)

### Community 29 - "test_reports.py"
Cohesion: 0.11
Nodes (26): AttendanceReportInput, MonthlySummaryInput, Arguments for ``student_attendance_report``., Arguments for ``monthly_attendance_summary``., Arguments for ``list_students_by_status``. Answers "who was absent today?" and…, Arguments for ``attendance_report``. Covers "attendance for SE401", "attendance…, StudentAttendanceReportInput, StudentsByStatusInput (+18 more)

### Community 30 - "ai/tools/ Registry Validation Boundary"
Cohesion: 0.12
Nodes (18): api Uvicorn Service, db PostgreSQL Service, migrate Alembic Service, postgres-data Volume, ai/ Agent Layer, Class Management Assistant, ConversationStore Protocol, Layered Architecture (+10 more)

### Community 31 - ".flush"
Cohesion: 0.14
Nodes (8): Fetch a row by primary key, or ``None`` when it does not exist., Persist a new instance and flush so its primary key is populated., Delete an instance and flush the change., Delete by primary key without loading the row. Returns: The number of rows…, Return every row. Intended for small reference tables and tests., Push pending changes to the database without committing., Reload an instance from the database., ModelT

### Community 32 - "ConversationState"
Cohesion: 0.07
Nodes (31): ConversationState, InMemoryConversationStore, Any, How long a conversation survives without activity., Return the live state for a chat, dropping it if it has expired., Persist a conversation and refresh its expiry., Forget a conversation entirely., Drop every expired conversation. Returns: How many conversations were removed.… (+23 more)

### Community 33 - "today"
Cohesion: 0.11
Nodes (37): Per-student attendance matrix for one class over one month., Turn a named period into a concrete inclusive date range. Keeping this in one…, resolve_period(), current_timezone(), format_date(), month_bounds(), parse_date(), date (+29 more)

### Community 34 - "ollama.py"
Cohesion: 0.08
Nodes (40): _first_non_empty(), history_to_messages(), _iter_json_objects(), _looks_like_add_student(), _looks_like_create_class(), new_call_id(), _parse_add_student_from_message(), Any (+32 more)

### Community 35 - "Settings"
Cohesion: 0.07
Nodes (46): Wire the agent to its dependencies. Args: client: Configured Groq client.…, build_groq_client(), get_groq_client(), GroqClient, Groq client construction. Uses the official ``groq`` Python SDK (``AsyncGroq``)…, Return the process-wide Groq client, creating it on first use., Thin async wrapper around the official Groq chat completions SDK., Create the client. Args: api_key: API key from https://console.groq.com/keys… (+38 more)

### Community 36 - "AdminContext"
Cohesion: 0.07
Nodes (42): AdminContext, add_extra_class(), add_schedule_rule(), add_student(), cancel_attendance(), cancel_teaching_day(), complete_teaching_day(), create_class() (+34 more)

### Community 37 - "container.py"
Cohesion: 0.12
Nodes (17): admin_context(), Shared FastAPI dependencies for the administrator API. The web UI operates as a…, Yield the service container and administrator for one request. The surrounding…, A user who owns classes. The teacher is the ownership root of the data model:…, Preferred way to address the teacher., Teacher, Data access for :class:`~app.models.teacher.Teacher`., Queries scoped to teacher accounts. (+9 more)

### Community 38 - "readiness"
Cohesion: 0.18
Nodes (13): liveness(), LivenessResponse, AsyncSession, BaseModel, get, Response, Reply to a liveness probe., Reply to a readiness probe. (+5 more)

### Community 39 - "ScheduleRepository"
Cohesion: 0.07
Nodes (16): date, time, Persist a one-off session., Remove a one-off session., Queries for repeating slots. Extra sessions use the same session., Return active and inactive weekly slots for one class, weekday order., Every active weekly slot owned by the teacher., Fetch one weekly slot belonging to a class. (+8 more)

### Community 40 - "test_activity_feed.py"
Cohesion: 0.14
Nodes (9): ActivityEntry, ActivityKind, StrEnum, Recent-activity read models for the administrator home page., What kind of change an activity entry describes., Two- or three-letter marker shown next to the entry., One thing that happened, newest first in a feed., The recent-activity feed derived from audit timestamps. (+1 more)

### Community 41 - "ServiceContainer"
Cohesion: 0.08
Nodes (13): Student enrolment, updates and reference resolution., The attendance session workflow., Attendance reporting and aggregation., Recent changes across classes, students, attendance and tuition., Lazily builds the service graph for a single unit of work. All services share…, Fall back to the process settings singleton when none was injected., Data access for teacher accounts., Data access for students. (+5 more)

### Community 42 - "ToolRegistry"
Cohesion: 0.20
Nodes (7): BaseModel, Add a tool to the catalogue. Args: name: Name the model will call, e.g.…, Names of every registered tool, in registration order., Holds the tool catalogue and executes calls against it., Create an empty registry., ToolRegistry, ToolHandler

### Community 43 - "groq.py"
Cohesion: 0.17
Nodes (14): Any, Send one chat completion request with optional tools. Args: model: Groq model…, history_to_messages(), model_supports_tool_calling(), Any, Groq conversation adapter. Translates between the internal history format and…, Whether *model* can run the assistant's tool-calling loop., Convert stored history items into OpenAI-style chat messages. Args: history:… (+6 more)

### Community 44 - "Code Review Skill"
Cohesion: 0.32
Nodes (8): Code Review Agent UI, Code Review Skill, Fixed Point Diff Pinning, Parallel Sub-Agents Aggregation, Fowler Smell Baseline, Spec Review Axis, Standards Review Axis, Why Two Axes Separation

### Community 45 - "validate_class_image"
Cohesion: 0.11
Nodes (16): field_validator, ZoneInfo, Resolved :class:`ZoneInfo` for :attr:`timezone`., Normalise a PostgreSQL DSN to the asyncpg driver. Deployment platforms hand out…, Normalise for the official Groq SDK (root URL only). The SDK appends…, class_initials(), Class image helpers: initials fallback and upload validation. Image bytes…, Return the two-character label shown when a class has no image. (+8 more)

### Community 46 - "env.py"
Cohesion: 0.22
Nodes (10): do_run_migrations(), Alembic migration environment. The engine is built from the application…, Emit SQL to stdout without connecting to a database., Run migrations on an already-established synchronous connection., Connect with the async driver and delegate to the sync runner., Entry point for online migrations., run_async_migrations(), run_migrations_offline() (+2 more)

### Community 47 - "ToolSpec"
Cohesion: 0.19
Nodes (9): Any, Render every tool as a function declaration dict., Render the whole catalogue for OpenAI-compatible tool calling., Render the whole catalogue in the legacy OpenAI Responses API format., A single callable exposed to the language model., Render this tool as a function declaration dict., Render this tool for OpenAI-compatible chat tool calling (Groq/Ollama)., Render this tool in the legacy OpenAI Responses API format. (+1 more)

### Community 48 - "build_openai_tool_schema"
Cohesion: 0.25
Nodes (10): build_openai_tool_schema(), _inline_refs(), Any, BaseModel, Convert Pydantic models into JSON schemas for LLM function tools. Providers…, Build a strict-mode JSON schema for legacy OpenAI tool definitions., Replace every ``$ref`` with a copy of the definition it points at., Prune to the allowed keyword subset and enforce object rules. (+2 more)

### Community 49 - "ConversationStore"
Cohesion: 0.22
Nodes (6): ConversationStore, Storage for :class:`ConversationState`, keyed by chat id., Return the live state for a chat, or ``None`` if absent or expired., Persist a conversation, refreshing its expiry., Forget a conversation entirely., Protocol

### Community 50 - "attendance_service.py"
Cohesion: 0.20
Nodes (9): AttendanceSessionClosedError, EmptyClassError, The class exists but has no students enrolled., The session is closed and can no longer be edited., _count_statuses(), _names_with_status(), Attendance workflow business logic. The workflow is driven by database state…, Tally attendance statuses across records. (+1 more)

### Community 51 - "wait_for_db.py"
Cohesion: 0.36
Nodes (7): _db_host_port(), main(), Wait for Docker DNS + PostgreSQL, then exec Alembic. The migrate service can…, Block until *host* resolves or *timeout* seconds elapse., Block until PostgreSQL accepts a connection., wait_for_database(), wait_for_dns()

### Community 52 - "StudentRead"
Cohesion: 0.25
Nodes (8): attendance_today(), list_students(), Roster of one class, ordered by name., Find students by a fragment of name or ID., Today's roster plus today's session, when one exists., search_students(), A student as presented to the teacher., StudentRead

### Community 55 - "Attendance Session Per Class Per Day"
Cohesion: 0.50
Nodes (4): Attendance Session Per Class Per Day, Buttons and Typing Share Implementation, Teacher-Class-Student-Attendance Data Model, Sessions Are Database State

### Community 56 - "Grill Me Skill"
Cohesion: 0.67
Nodes (3): Grill Me Agent UI, Grill Me Skill, Grilling Session

### Community 58 - "validate_meaningful_name"
Cohesion: 0.32
Nodes (4): field_validator, Reject names that carry no alphanumeric content. Args: value: The candidate…, validate_meaningful_name(), field_validator

### Community 59 - "ScheduleRuleRead"
Cohesion: 0.40
Nodes (5): A repeating weekday slot., ScheduleRuleRead, Project a weekly slot onto the dashboard read model., Weekly slots for one owned class., _rule_read()

### Community 61 - "schemas/__init__.py"
Cohesion: 0.50
Nodes (3): NamedEntity, Minimal identity of a record, used inside larger tool responses., Pydantic contracts shared by the service, AI and API layers.

### Community 62 - "get_class_icon"
Cohesion: 0.67
Nodes (3): get_class_icon(), Response, Serve the uploaded image for a class, or 404 when there is none.

### Community 63 - "test_attendance_flow.py"
Cohesion: 0.11
Nodes (33): FinishAttendanceInput, MarkRemainingInput, Arguments for ``update_attendance``., Arguments for ``mark_remaining_students``., Arguments for ``finish_attendance``., UpdateAttendanceInput, The end-to-end attendance workflow., The inline-keyboard path and the conversational path must agree. (+25 more)

### Community 64 - "test_student_service.py"
Cohesion: 0.09
Nodes (35): AddStudentInput, ImportStudentRow, ImportStudentsInput, ListStudentsInput, Student read models and tool contracts., Arguments for ``list_students``., One student from an uploaded roster file., Arguments for enrolling a whole roster at once. (+27 more)

### Community 67 - "agent.py"
Cohesion: 0.10
Nodes (29): AgentReply, AssistantAgent, _clip_for_log(), _final_reply_text(), _message_from_last_tool(), Any, The assistant agent: one user message in, one reply out. Implements the tool-…, Handle one user message. Args: message: What the teacher typed. state: Live… (+21 more)

### Community 70 - "get_web_runtime"
Cohesion: 0.25
Nodes (8): chat(), chat_board(), get_me(), Identity of the administrator plus assistant availability., Send one message to the assistant and return its reply., The attendance session currently in the assistant's focus, if any., get_web_runtime(), Return the process-wide web runtime, creating it on first use.

### Community 72 - "_dashboard_shell"
Cohesion: 0.67
Nodes (3): _dashboard_shell(), Return the single-page dashboard HTML., FileResponse

### Community 73 - "conftest.py"
Cohesion: 0.07
Nodes (34): Database engine, session factory and connection lifecycle., Database, get_session(), Any, AsyncSession, Override the process-wide database. Intended for tests only., FastAPI dependency yielding a transactional session., Owns the async engine and hands out sessions. (+26 more)

### Community 74 - "AttendanceSession"
Cohesion: 0.09
Nodes (15): AttendanceSession, One roll-call for a class on a given calendar day. At most one session may…, Whether records may still be modified., Select, Every session a teacher held on one day, with class preloaded., Fetch a session by id, scoped to the owning teacher., Fetch a session with its records, students and class eagerly loaded., Fetch the currently open session for a class, if any. (+7 more)

### Community 77 - "20260825_0908_schedule_and_tuition_charges.py"
Cohesion: 0.40
Nodes (4): downgrade(), Drop the ledger and schedule tables., Create schedule tables, the tuition ledger, and backfill unpaid charges., upgrade()

### Community 78 - "_pg_enum"
Cohesion: 0.67
Nodes (3): _pg_enum(), Enum, Build a database enum that stores the lower-case member *values*. Without…

### Community 79 - "_pg_enum"
Cohesion: 0.67
Nodes (3): _pg_enum(), Enum, Store enum *values* (``not_yet``) rather than member names.

### Community 81 - "ClassService"
Cohesion: 0.07
Nodes (23): ClassNotFoundError, The teacher has no class with the requested name., No student matched the reference the teacher used., StudentNotFoundError, Wire the service to its collaborators. Args: attendance_repository: Access to…, ClassService, Update the free-text description of an owned class., Replace the class image stored on the class row. (+15 more)

### Community 94 - "AppError"
Cohesion: 0.12
Nodes (33): ChatRequest, CompleteDayRequest, DescriptionRequest, ExtraSessionRequest, FinishRequest, MarkCompletedRequest, MarkRemainingRequest, MarkStatusRequest (+25 more)

## Knowledge Gaps
- **12 isolated node(s):** `PAGES`, `class-management`, `Fowler Smell Baseline`, `Fixed Point Diff Pinning`, `Code Review Agent UI` (+7 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **9 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `AttendanceStatus` connect `AttendanceStatus` to `AttendanceService`, `AttendanceRepository`, `Classroom`, `admin.py`, `AttendanceSession`, `ToolOutput`, `schemas/attendance.py`, `definitions.py`, `test_agent.py`, `attendance_service.py`, `AttendanceSessionStatus`, `test_reports.py`, `AppError`, `test_attendance_flow.py`?**
  _High betweenness centrality (0.074) - this node is a cross-community bridge._
- **Why does `Settings` connect `Settings` to `.sync_database_url`, `agent.py`, `container.py`, `readiness`, `conftest.py`, `ServiceContainer`, `validate_class_image`?**
  _High betweenness centrality (0.053) - this node is a cross-community bridge._
- **Why does `get_logger()` connect `Settings` to `AttendanceStatus`, `exceptions.py`, `ollama.py`, `agent.py`, `container.py`, `student_service.py`, `ToolOutput`, `activity_service.py`, `attendance_service.py`, `schedule_service.py`, `registry.py`, `class_service.py`?**
  _High betweenness centrality (0.042) - this node is a cross-community bridge._
- **Are the 47 inferred relationships involving `AttendanceStatus` (e.g. with `ChatRequest` and `CompleteDayRequest`) actually correct?**
  _`AttendanceStatus` has 47 INFERRED edges - model-reasoned connections that need verification._
- **Are the 71 inferred relationships involving `ToolOutput` (e.g. with `ActivityEntry` and `ActivityKind`) actually correct?**
  _`ToolOutput` has 71 INFERRED edges - model-reasoned connections that need verification._
- **Are the 69 inferred relationships involving `ToolInput` (e.g. with `AttendanceEntry` and `AttendanceSessionRead`) actually correct?**
  _`ToolInput` has 69 INFERRED edges - model-reasoned connections that need verification._
- **Are the 42 inferred relationships involving `OperationResult` (e.g. with `AttendanceEntry` and `AttendanceSessionRead`) actually correct?**
  _`OperationResult` has 42 INFERRED edges - model-reasoned connections that need verification._