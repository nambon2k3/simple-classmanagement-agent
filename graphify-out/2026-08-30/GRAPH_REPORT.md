# Graph Report - simple-classmanagement-agent  (2026-08-30)

## Corpus Check
- 124 files · ~51,270 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1752 nodes · 4675 edges · 85 communities (73 shown, 12 thin omitted)
- Extraction: 87% EXTRACTED · 13% INFERRED · 0% AMBIGUOUS · INFERRED: 589 edges (avg confidence: 0.52)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `1f756474`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- report_service.py
- exceptions.py
- register_exception_handlers
- TuitionChargeRepository
- AttendanceService
- AttendanceRepository
- InMemoryConversationStore
- el
- OperationResult
- attendance_service.py
- schemas/schedule.py
- ToolOutput
- 20260830_2115_class_images_in_database.py
- format_vnd
- parse_roster_file
- StartAttendanceInput
- definitions.py
- test_agent.py
- test_registry.py
- test_text.py
- datetime
- ._owned
- StudentRepository
- ExtraSessionRead
- .add_extra
- test_tool_schema.py
- ToolRegistry
- .__init__
- class_service.py
- timedelta
- ai/tools/ Registry Validation Boundary
- .flush
- ConversationState
- resolve_period
- ollama.py
- get_settings
- admin.py
- ServiceContainer
- readiness
- .get_extra_on_date
- ActivityKind
- today
- .register
- RenameClassOutput
- Code Review Skill
- Settings
- env.py
- validate_class_image
- client
- ConversationStore
- .get_rule_by_slot
- wait_for_db.py
- .paid_through_per_student
- ._blank_strings_become_none
- 20260727_1445_initial_schema.py
- Attendance Session Per Class Per Day
- Grill Me Skill
- validate_meaningful_name
- .__repr__
- conftest.py
- test_attendance_flow.py
- test_student_service.py
- .label
- .display_label
- agent.py
- get_web_runtime
- .format
- _dashboard_shell
- Database
- .is_open
- web/__init__.py
- 20260825_0908_schedule_and_tuition_charges.py
- _pg_enum
- _pg_enum
- ClassService
- class-management
- AttendanceStatus
- .__init__

## God Nodes (most connected - your core abstractions)
1. `AttendanceStatus` - 88 edges
2. `ToolOutput` - 85 edges
3. `ToolInput` - 80 edges
4. `OperationResult` - 56 edges
5. `Classroom` - 53 edges
6. `AttendanceRepository` - 50 edges
7. `Student` - 49 edges
8. `AttendanceService` - 49 edges
9. `el()` - 48 edges
10. `today()` - 47 edges

## Surprising Connections (you probably didn't know these)
- `db PostgreSQL Service` --semantically_similar_to--> `PostgreSQL`  [INFERRED] [semantically similar]
  docker-compose.yml → README.md
- `FakeResponse` --uses--> `ConversationState`  [INFERRED]
  tests/integration/test_agent.py → app/ai/memory.py
- `ScriptedClient` --uses--> `ConversationState`  [INFERRED]
  tests/integration/test_agent.py → app/ai/memory.py
- `test_groq_tools_are_built_from_the_registry()` --calls--> `build_registry()`  [EXTRACTED]
  tests/integration/test_agent.py → app/ai/tools/definitions.py
- `EchoInput` --uses--> `ToolContext`  [INFERRED]
  tests/unit/test_registry.py → app/ai/tools/registry.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Two-Axis Parallel Code Review Flow** — _agents_skills_code_review_skill_code_review, _agents_skills_code_review_skill_standards_axis, _agents_skills_code_review_skill_spec_axis, _agents_skills_code_review_skill_parallel_sub_agents, _agents_skills_code_review_skill_fixed_point [EXTRACTED 1.00]
- **Telegram-to-PostgreSQL Request Path** — readme_telegram_layer, readme_ai_agent_layer, readme_tools_registry, readme_services_layer, readme_repositories_layer, readme_postgresql [EXTRACTED 1.00]
- **Docker Compose Deploy Stack** — docker_compose_db, docker_compose_migrate, docker_compose_api [EXTRACTED 1.00]

## Communities (85 total, 12 thin omitted)

### Community 0 - "report_service.py"
Cohesion: 0.06
Nodes (51): AttendanceSummary, Counts of each status within a session or a date range., Share of students who were in the room (present or late), 0..1., Build a summary from per-status counts. Args: counts: Number of records per…, AttendanceHistoryEntry, AttendanceReportInput, AttendanceReportOutput, MonthlySummaryInput (+43 more)

### Community 1 - "exceptions.py"
Cohesion: 0.07
Nodes (31): http_status_for(), HTTP translation of domain errors. The API surface reuses the same exception…, Map a domain error onto an HTTP status code., AmbiguousReferenceError, AmbiguousStudentError, AppError, AttendanceAlreadyTakenError, AttendanceSessionNotFoundError (+23 more)

### Community 2 - "register_exception_handlers"
Cohesion: 0.33
Nodes (4): FastAPI, Install the application-wide exception handlers., register_exception_handlers(), HTTP API: health probes and the administrator dashboard.

### Community 3 - "TuitionChargeRepository"
Cohesion: 0.09
Nodes (13): datetime, Select, Set the amount on unpaid charges for a class to the current daily fee. Returns:…, Mark every unpaid charge for the student in this class as paid. Returns: Number…, Create or refresh charges after a session is finished. Completed (paid) rows…, Queries over billed attendance days., Every charge attached to one attendance session., Charges for students in one class, with student and session loaded. (+5 more)

### Community 4 - "AttendanceService"
Cohesion: 0.06
Nodes (36): AttendanceSessionClosedError, NoActiveAttendanceSessionError, No attendance session is currently open., The session is closed and can no longer be edited., AttendanceSessionRead, FinishAttendanceOutput, Summary produced when a session is finalised., Full state of an attendance session. (+28 more)

### Community 5 - "AttendanceRepository"
Cohesion: 0.05
Nodes (28): AttendanceRepository, date, Select, Dates a class actually met, oldest first, ignoring cancelled days., Every ``(student_id, date, status)`` mark for a class, oldest first., Total number of attendance sessions ever held for a class., Date of the most recent session for a class, or ``None`` if none., Every session a teacher held on one day, with class preloaded. (+20 more)

### Community 6 - "InMemoryConversationStore"
Cohesion: 0.24
Nodes (12): InMemoryConversationStore, Forget a conversation entirely., Process-local conversation store with time-based expiry. Suitable for a single-…, Current instant as a timezone-aware UTC datetime., utc_now(), Tests for conversation memory and its expiry rules., test_a_different_teacher_in_the_same_chat_starts_fresh(), test_clear_forgets_the_conversation() (+4 more)

### Community 7 - "el"
Cohesion: 0.13
Nodes (63): api, apiFetch(), apiUpload(), errorMessage(), boot(), attendanceRate(), fmtDate(), initials() (+55 more)

### Community 8 - "OperationResult"
Cohesion: 0.07
Nodes (45): DuplicateStudentError, The student ID is already taken within the class., AttendanceEntry, One student's state inside an attendance session., OperationResult, Generic acknowledgement for tools that only mutate state., AddStudentOutput, ImportStudentRow (+37 more)

### Community 9 - "attendance_service.py"
Cohesion: 0.10
Nodes (49): AttendanceRecord, AttendanceSession, Attendance ORM models., One roll-call for a class on a given calendar day. At most one session may…, The status of one student within one attendance session., Base, IdMixin, Declarative base and shared column mixins. (+41 more)

### Community 10 - "schemas/schedule.py"
Cohesion: 0.18
Nodes (14): date, Every scheduled occurrence in one month, across all classes., Copy each occurrence with ``completed`` set from finished attendance days., Collapse same-class slots on one day into a single dashboard row., schedule_month(), _today_class_rows(), _with_completion(), Schedule read models used by the administrator dashboard. (+6 more)

### Community 11 - "ToolOutput"
Cohesion: 0.07
Nodes (47): Recent-activity read models for the administrator home page., ListClassesInput, ``list_classes`` takes no arguments., AppModel, NamedEntity, BaseModel, Shared Pydantic base classes and reusable field types. These types are the…, Minimal identity of a record, used inside larger tool responses. (+39 more)

### Community 12 - "20260830_2115_class_images_in_database.py"
Cohesion: 0.40
Nodes (4): downgrade(), Add deferred image columns persisted with the rest of the database., Remove class image columns., upgrade()

### Community 13 - "format_vnd"
Cohesion: 0.10
Nodes (14): ActivityEntry, One thing that happened, newest first in a feed., _is_edit(), Whether ``updated`` is late enough after ``created`` to be a real edit., Return the newest changes across classes, students, roll-calls and payments., Set the daily tuition fee charged per attended day for every student., Completed versus unpaid tuition across every class., Per-student payment status for one owned class. (+6 more)

### Community 14 - "parse_roster_file"
Cohesion: 0.12
Nodes (27): _cell_text(), _header_mapping(), parse_roster_file(), Read a student roster out of an uploaded Excel or CSV file. Teachers keep…, Render a spreadsheet cell as text, keeping phone numbers intact., Map a raw table onto roster rows, skipping blanks and reporting gaps., Map column index to field name, or ``None`` when this is not a header., One student parsed out of the uploaded file. (+19 more)

### Community 15 - "StartAttendanceInput"
Cohesion: 0.09
Nodes (34): FinishAttendanceInput, Arguments for ``finish_attendance``., Arguments for ``start_attendance``., StartAttendanceInput, Arguments for ``set_class_tuition_fee``., Arguments for ``tuition_report``. Answers questions like "tuition for SE401 in…, SetClassTuitionFeeInput, TuitionReportInput (+26 more)

### Community 16 - "definitions.py"
Cohesion: 0.11
Nodes (40): AgentReply, The outcome of a single user turn., AI layer: intent understanding and tool dispatch. Nothing in this package…, _add_student(), _attendance_report(), _attendance_state(), build_registry(), _cancel_attendance() (+32 more)

### Community 17 - "test_agent.py"
Cohesion: 0.08
Nodes (47): AssistantAgent, _clip_for_log(), _final_reply_text(), _message_from_last_tool(), Any, Handle one user message. Args: message: What the teacher typed. state: Live…, Call Groq, translating transport failures. Raises: AssistantError: If the…, Render a value for logs without dumping unbounded model output. (+39 more)

### Community 18 - "test_registry.py"
Cohesion: 0.13
Nodes (12): context(), crash(), echo(), EchoInput, EchoOutput, explode(), fixture, Tests for the tool registry — the validation boundary around the model. (+4 more)

### Community 19 - "test_text.py"
Cohesion: 0.12
Nodes (29): find_matches(), normalize(), normalize_code(), Text normalisation and fuzzy-matching helpers. Teachers refer to students the…, Shorten ``value`` to ``limit`` characters, appending ``suffix`` if cut., Remove diacritics so ``"Nguyễn"`` and ``"Nguyen"`` compare equal., Casefold, strip accents and collapse whitespace for comparison., Canonical form for identifiers such as student codes and class names. (+21 more)

### Community 20 - "datetime"
Cohesion: 0.22
Nodes (5): datetime, ``(name, created_at, updated_at)`` for the newest-touched classes., ``(name, code, class_name, created_at, updated_at)`` for recent students., ``(class_name, status, opened_at, closed_at)`` for recent roll-calls., ``(student_name, class_name, days, amount_vnd, completed_at)`` per payment.…

### Community 21 - "._owned"
Cohesion: 0.17
Nodes (6): Select, Fetch one class by id, scoped to its owner., Fetch a class by its name, case-insensitively., Return every class owned by the teacher, alphabetically., Fetch one class including its deferred image blob., Fetch a class with its student collection eagerly loaded.

### Community 22 - "StudentRepository"
Cohesion: 0.08
Nodes (19): No student matched the reference the teacher used., StudentNotFoundError, Select, Queries scoped to the students inside a teacher's classes., Base query joining through ``classes`` to enforce ownership., Fetch one student by id, scoped to the owning teacher., Fetch a student together with their class., Fetch a student by their code within one class. (+11 more)

### Community 23 - "ExtraSessionRead"
Cohesion: 0.40
Nodes (5): ExtraSessionRead, A one-off extra class., _extra_read(), Project a one-off session onto the dashboard read model., One-off extra classes for an owned class.

### Community 24 - ".add_extra"
Cohesion: 0.09
Nodes (17): A weekly slot or extra session already exists for that class., ScheduleConflictError, A repeating weekday slot., ScheduleRuleRead, date, time, Schedule a one-off extra class. Raises: ScheduleConflictError: If that class…, Expand weekly rules and extras onto the days of ``year``/``month``. (+9 more)

### Community 25 - "test_tool_schema.py"
Cohesion: 0.11
Nodes (30): build_openai_tool_schema(), build_tool_schema(), _inline_refs(), Any, BaseModel, Convert Pydantic models into JSON schemas for LLM function tools. Providers…, Build a JSON schema for a tool's input model. Args: model: The Pydantic model…, Build a strict-mode JSON schema for legacy OpenAI tool definitions. (+22 more)

### Community 26 - "ToolRegistry"
Cohesion: 0.08
Nodes (32): _clip_payload(), _decode_arguments(), _describe_validation_error(), _error(), Any, Tool registry: the only bridge between the language model and the backend. The…, Return a tool by name, or ``None`` when it is not registered., Names of every registered tool, in registration order. (+24 more)

### Community 27 - ".__init__"
Cohesion: 0.40
Nodes (3): Any, Create the error. Args: message: Teacher-safe explanation. Falls back to…, Serialise the error for tool output or an HTTP error body.

### Community 28 - "class_service.py"
Cohesion: 0.06
Nodes (46): ConfirmationRequiredError, A destructive action was requested without explicit confirmation. Raised rather…, ClassInfoInput, ClassInfoOutput, ClassRead, CreateClassInput, CreateClassOutput, DeleteClassInput (+38 more)

### Community 29 - "timedelta"
Cohesion: 0.20
Nodes (8): How long a conversation survives without activity., Create the store. Args: ttl_seconds: Idle lifetime of a conversation. Defaults…, test_attendance_can_be_recorded_for_a_past_date(), test_get_session_for_date_does_not_return_another_day(), history(), fixture, Three days of attendance: today and the two days before., timedelta

### Community 30 - "ai/tools/ Registry Validation Boundary"
Cohesion: 0.12
Nodes (18): api Uvicorn Service, db PostgreSQL Service, migrate Alembic Service, postgres-data Volume, ai/ Agent Layer, Class Management Assistant, ConversationStore Protocol, Layered Architecture (+10 more)

### Community 31 - ".flush"
Cohesion: 0.14
Nodes (8): Fetch a row by primary key, or ``None`` when it does not exist., Persist a new instance and flush so its primary key is populated., Delete an instance and flush the change., Delete by primary key without loading the row. Returns: The number of rows…, Return every row. Intended for small reference tables and tests., Push pending changes to the database without committing., Reload an instance from the database., ModelT

### Community 32 - "ConversationState"
Cohesion: 0.11
Nodes (14): ConversationState, Any, Return the live state for a chat, dropping it if it has expired., Persist a conversation and refresh its expiry., Drop every expired conversation. Returns: How many conversations were removed.…, Return the live conversation for a chat, creating one if needed., Everything remembered between two messages in one chat., Mark the conversation as active right now. (+6 more)

### Community 33 - "resolve_period"
Cohesion: 0.11
Nodes (28): Open (or resume) the attendance session for a class on a date. Raises:…, Turn a named period into a concrete inclusive date range. Keeping this in one…, resolve_period(), format_date(), month_bounds(), parse_date(), date, Coerce a user- or model-supplied value into a :class:`~datetime.date`. Accepts… (+20 more)

### Community 34 - "ollama.py"
Cohesion: 0.06
Nodes (54): Any, Send one chat completion request with optional tools. Args: model: Groq model…, history_to_messages(), model_supports_tool_calling(), Any, Groq conversation adapter. Translates between the internal history format and…, Whether *model* can run the assistant's tool-calling loop., Convert stored history items into OpenAI-style chat messages. Args: history:… (+46 more)

### Community 35 - "get_settings"
Cohesion: 0.12
Nodes (26): Short-lived conversation state. The assistant needs just enough memory to make…, Health and readiness endpoints., get_settings(), Centralised application configuration. All runtime configuration is read from…, Return the process-wide settings singleton. Cached so that ``.env`` parsing and…, configure_logging(), get_logger(), JsonFormatter (+18 more)

### Community 36 - "admin.py"
Cohesion: 0.05
Nodes (77): AdminContext, add_extra_class(), add_schedule_rule(), add_student(), attendance_session(), attendance_since_payment(), attendance_today(), cancel_attendance() (+69 more)

### Community 37 - "ServiceContainer"
Cohesion: 0.04
Nodes (49): admin_context(), Shared FastAPI dependencies for the administrator API. The web UI operates as a…, Yield the service container and administrator for one request. The surrounding…, A user who owns classes. The teacher is the ownership root of the data model:…, Preferred way to address the teacher., Teacher, ActivityRepository, Read-only queries that feed the recent-activity list. (+41 more)

### Community 38 - "readiness"
Cohesion: 0.18
Nodes (13): liveness(), LivenessResponse, AsyncSession, BaseModel, get, Response, Reply to a liveness probe., Reply to a readiness probe. (+5 more)

### Community 39 - ".get_extra_on_date"
Cohesion: 0.40
Nodes (3): date, Extra sessions whose date falls in ``[start, end)``., Look up an extra session by class and calendar day.

### Community 40 - "ActivityKind"
Cohesion: 0.40
Nodes (4): ActivityKind, StrEnum, What kind of change an activity entry describes., Two- or three-letter marker shown next to the entry.

### Community 41 - "today"
Cohesion: 0.16
Nodes (16): build_system_prompt(), System prompt construction. The prompt is assembled per turn so the model…, Assemble the system prompt for one turn. Args: state: The live conversation,…, current_timezone(), datetime, ZoneInfo, Date and time helpers. Attendance is anchored to the teacher's local calendar…, The configured application timezone. (+8 more)

### Community 42 - ".register"
Cohesion: 0.50
Nodes (3): BaseModel, Add a tool to the catalogue. Args: name: Name the model will call, e.g.…, ToolHandler

### Community 43 - "RenameClassOutput"
Cohesion: 0.50
Nodes (3): Result of renaming a class., RenameClassOutput, Rename an existing class. Raises: ClassNotFoundError: If the current name does…

### Community 44 - "Code Review Skill"
Cohesion: 0.32
Nodes (8): Code Review Agent UI, Code Review Skill, Fixed Point Diff Pinning, Parallel Sub-Agents Aggregation, Fowler Smell Baseline, Spec Review Axis, Standards Review Axis, Why Two Axes Separation

### Community 45 - "Settings"
Cohesion: 0.10
Nodes (16): field_validator, ZoneInfo, Blocking DSN, required by Alembic's migration runner., Resolved :class:`ZoneInfo` for :attr:`timezone`., Whether the process is running in the production environment., Strongly typed application settings. Attributes are populated from environment…, Normalise a PostgreSQL DSN to the asyncpg driver. Deployment platforms hand out…, Normalise for the official Groq SDK (root URL only). The SDK appends… (+8 more)

### Community 46 - "env.py"
Cohesion: 0.22
Nodes (10): do_run_migrations(), Alembic migration environment. The engine is built from the application…, Emit SQL to stdout without connecting to a database., Run migrations on an already-established synchronous connection., Connect with the async driver and delegate to the sync runner., Entry point for online migrations., run_async_migrations(), run_migrations_offline() (+2 more)

### Community 47 - "validate_class_image"
Cohesion: 0.26
Nodes (10): class_initials(), Class image helpers: initials fallback and upload validation. Image bytes…, Return the two-character label shown when a class has no image., Return the MIME type for a valid class image upload. Raises: ValueError: If the…, validate_class_image(), parametrize, test_class_initials(), test_validate_class_image_accepts_png() (+2 more)

### Community 48 - "client"
Cohesion: 0.50
Nodes (4): AsyncClient, client(), fixture, An HTTP client bound to the app without running its lifespan.

### Community 49 - "ConversationStore"
Cohesion: 0.22
Nodes (6): ConversationStore, Storage for :class:`ConversationState`, keyed by chat id., Return the live state for a chat, or ``None`` if absent or expired., Persist a conversation, refreshing its expiry., Forget a conversation entirely., Protocol

### Community 51 - "wait_for_db.py"
Cohesion: 0.36
Nodes (7): _db_host_port(), main(), Wait for Docker DNS + PostgreSQL, then exec Alembic. The migrate service can…, Block until *host* resolves or *timeout* seconds elapse., Block until PostgreSQL accepts a connection., wait_for_database(), wait_for_dns()

### Community 55 - "Attendance Session Per Class Per Day"
Cohesion: 0.50
Nodes (4): Attendance Session Per Class Per Day, Buttons and Typing Share Implementation, Teacher-Class-Student-Attendance Data Model, Sessions Are Database State

### Community 56 - "Grill Me Skill"
Cohesion: 0.67
Nodes (3): Grill Me Agent UI, Grill Me Skill, Grilling Session

### Community 58 - "validate_meaningful_name"
Cohesion: 0.32
Nodes (4): field_validator, Reject names that carry no alphanumeric content. Args: value: The candidate…, validate_meaningful_name(), field_validator

### Community 61 - "conftest.py"
Cohesion: 0.14
Nodes (19): Override the process-wide database. Intended for tests only., set_database(), classroom(), _configure_environment(), database(), AsyncSession, fixture, Shared pytest fixtures. Integration tests run against a real (SQLite) database… (+11 more)

### Community 63 - "test_attendance_flow.py"
Cohesion: 0.11
Nodes (33): CancelAttendanceInput, GetAttendanceStateInput, MarkRemainingInput, Attendance read models and tool contracts., Arguments for ``update_attendance``., Arguments for ``mark_remaining_students``., Arguments for ``cancel_attendance``., Arguments for ``get_attendance_state``. (+25 more)

### Community 64 - "test_student_service.py"
Cohesion: 0.13
Nodes (19): AddStudentInput, Arguments for ``add_student``., Arguments for ``update_student``. Only the fields that are supplied are…, UpdateStudentInput, Student management and reference resolution against a real database., The same person's name in two classes is only ambiguous across both., test_add_student(), test_ambiguity_is_resolved_by_narrowing_to_a_class() (+11 more)

### Community 67 - "agent.py"
Cohesion: 0.11
Nodes (18): The assistant agent: one user message in, one reply out. Implements the tool-…, Whether to ignore the model's words and show the tool result instead., Wire the agent to its dependencies. Args: client: Configured Groq client.…, _should_use_tool_message_instead(), build_groq_client(), get_groq_client(), GroqClient, Groq client construction. Uses the official ``groq`` Python SDK (``AsyncGroq``)… (+10 more)

### Community 70 - "get_web_runtime"
Cohesion: 0.40
Nodes (5): get_web_runtime(), Assistant collaborators shared by every web request., Build the runtime from application settings. Args: settings: Configuration to…, Return the process-wide web runtime, creating it on first use., WebRuntime

### Community 72 - "_dashboard_shell"
Cohesion: 0.67
Nodes (3): _dashboard_shell(), Return the single-page dashboard HTML., FileResponse

### Community 73 - "Database"
Cohesion: 0.11
Nodes (15): Database engine, session factory and connection lifecycle., Database, get_session(), Any, AsyncSession, FastAPI dependency yielding a transactional session., Owns the async engine and hands out sessions., Create the engine and session factory. Args: settings: Configuration supplying… (+7 more)

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
Nodes (20): ClassNotFoundError, The teacher has no class with the requested name., Wire the service to its collaborators. Args: attendance_repository: Access to…, ClassService, Update the free-text description of an owned class., Replace the class image stored on the class row., Return ``(bytes, mime)`` for the class image, or ``None`` if unset., Create, rename, delete and inspect a teacher's classes. Also owns… (+12 more)

### Community 94 - "AttendanceStatus"
Cohesion: 0.10
Nodes (38): ChatRequest, CompleteDayRequest, DescriptionRequest, ExtraSessionRequest, FinishRequest, MarkCompletedRequest, MarkRemainingRequest, MarkStatusRequest (+30 more)

## Knowledge Gaps
- **12 isolated node(s):** `PAGES`, `class-management`, `Fowler Smell Baseline`, `Fixed Point Diff Pinning`, `Code Review Agent UI` (+7 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **12 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `AttendanceStatus` connect `AttendanceStatus` to `report_service.py`, `admin.py`, `AttendanceRepository`, `AttendanceService`, `OperationResult`, `attendance_service.py`, `today`, `ToolOutput`, `StartAttendanceInput`, `definitions.py`, `test_agent.py`, `test_attendance_flow.py`?**
  _High betweenness centrality (0.075) - this node is a cross-community bridge._
- **Why does `Settings` connect `Settings` to `agent.py`, `get_settings`, `ServiceContainer`, `readiness`, `get_web_runtime`, `Database`, `definitions.py`, `test_agent.py`, `conftest.py`?**
  _High betweenness centrality (0.061) - this node is a cross-community bridge._
- **Why does `ServiceContainer` connect `ServiceContainer` to `report_service.py`, `TuitionChargeRepository`, `AttendanceService`, `AttendanceRepository`, `get_settings`, `Settings`, `ClassService`, `StudentRepository`, `conftest.py`?**
  _High betweenness centrality (0.042) - this node is a cross-community bridge._
- **Are the 47 inferred relationships involving `AttendanceStatus` (e.g. with `ChatRequest` and `CompleteDayRequest`) actually correct?**
  _`AttendanceStatus` has 47 INFERRED edges - model-reasoned connections that need verification._
- **Are the 71 inferred relationships involving `ToolOutput` (e.g. with `ActivityEntry` and `ActivityKind`) actually correct?**
  _`ToolOutput` has 71 INFERRED edges - model-reasoned connections that need verification._
- **Are the 69 inferred relationships involving `ToolInput` (e.g. with `AttendanceEntry` and `AttendanceSessionRead`) actually correct?**
  _`ToolInput` has 69 INFERRED edges - model-reasoned connections that need verification._
- **Are the 42 inferred relationships involving `OperationResult` (e.g. with `AttendanceEntry` and `AttendanceSessionRead`) actually correct?**
  _`OperationResult` has 42 INFERRED edges - model-reasoned connections that need verification._