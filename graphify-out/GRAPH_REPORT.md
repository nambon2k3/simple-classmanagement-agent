# Graph Report - simple-classmanagement-agent  (2026-07-28)

## Corpus Check
- 93 files · ~37,457 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1343 nodes · 3547 edges · 80 communities (62 shown, 18 thin omitted)
- Extraction: 87% EXTRACTED · 13% INFERRED · 0% AMBIGUOUS · INFERRED: 460 edges (avg confidence: 0.53)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `93b7b5c4`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- attendance_service.py
- AttendanceStatus
- tuition_service.py
- AttendanceService
- Student
- AttendanceRepository
- ToolOutput
- get_settings
- ToolRegistry
- commands.py
- StudentService
- test_keyboards.py
- test_agent.py
- test_tool_schema.py
- test_reports.py
- conftest.py
- AppError
- exceptions.py
- definitions.py
- test_registry.py
- messages.py
- test_text.py
- today
- StudentRepository
- test_attendance_flow.py
- class_service.py
- ClassService
- agent.py
- test_api.py
- ._owned
- formatting.py
- ollama.py
- student_service.py
- ai/tools/ Registry Validation Boundary
- Settings
- ServiceContainer
- BaseRepository
- callbacks.py
- readiness
- ValueError
- env.py
- ConversationState
- validate_meaningful_name
- Code Review Skill
- services
- .names
- PermissionDeniedError
- get_session
- telegram_webhook
- .__init__
- 20260727_1445_initial_schema.py
- .list_with_student_counts
- Attendance Session Per Class Per Day
- Grill Me Skill
- .get_by_telegram_id
- .format
- ConversationStore
- .sync_database_url
- format_vnd
- TeacherService
- class-management
- .get_by_id
- .chat
- .register
- .extend_history
- _pg_enum
- .__repr__
- .display_label
- .display_name
- .add_record
- .get_record
- .list_records
- ._drop_empty_details

## God Nodes (most connected - your core abstractions)
1. `AttendanceStatus` - 80 edges
2. `ToolOutput` - 74 edges
3. `ToolInput` - 72 edges
4. `OperationResult` - 53 edges
5. `AttendanceRepository` - 47 edges
6. `ToolContext` - 44 edges
7. `Settings` - 43 edges
8. `AttendanceService` - 43 edges
9. `Student` - 41 edges
10. `get_settings()` - 38 edges

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

## Communities (80 total, 18 thin omitted)

### Community 0 - "attendance_service.py"
Cohesion: 0.16
Nodes (12): No student matched the reference the teacher used., StudentNotFoundError, FinishAttendanceOutput, Summary produced when a session is finalised., _count_statuses(), _names_with_status(), Attendance workflow business logic. The workflow is driven by database state…, Finalise the active session, defaulting anyone still unmarked. Raises:… (+4 more)

### Community 1 - "AttendanceStatus"
Cohesion: 0.08
Nodes (37): AttendanceStatus, Enumerations shared by the ORM models, schemas and AI tool contracts., Icon used when rendering the status in Telegram., Human-readable label, e.g. ``"Late"``., Whether the status contributes to the attendance rate. Late students were in…, How a student was accounted for in a single attendance session., Build a summary from per-status counts. Args: counts: Number of records per…, AttendanceHistoryEntry (+29 more)

### Community 2 - "tuition_service.py"
Cohesion: 0.11
Nodes (30): DateRange, StrEnum, Named date ranges the model can request without doing date arithmetic. Letting…, The concrete range a report was computed over., ReportPeriod, ClassTeachingDaysRow, ClassTuitionSummary, field_validator (+22 more)

### Community 3 - "AttendanceService"
Cohesion: 0.08
Nodes (28): AttendanceSessionClosedError, NoActiveAttendanceSessionError, No attendance session is currently open., The session is closed and can no longer be edited., AttendanceSession, One roll-call for a class on a given calendar day. At most one session may…, Whether records may still be modified., Fetch the currently open session for a class, if any. (+20 more)

### Community 4 - "Student"
Cohesion: 0.15
Nodes (26): AttendanceRecord, Attendance ORM models., The status of one student within one attendance session., Base, IdMixin, Declarative base and shared column mixins., Base class for every ORM model., Surrogate integer primary key. (+18 more)

### Community 5 - "AttendanceRepository"
Cohesion: 0.07
Nodes (21): AttendanceRepository, date, Select, Total number of attendance sessions ever held for a class., Date of the most recent session for a class, or ``None`` if none., Every session a teacher held on one day, with class preloaded., Count records per status within a single session., Count records per status for a class over a date range. (+13 more)

### Community 6 - "ToolOutput"
Cohesion: 0.11
Nodes (27): CancelAttendanceInput, GetAttendanceStateOutput, MarkRemainingOutput, Result of bulk-marking the unmarked students., Arguments for ``cancel_attendance``., The currently open session, if there is one., ClassRead, ListClassesInput (+19 more)

### Community 7 - "get_settings"
Cohesion: 0.10
Nodes (29): Health and readiness endpoints., Telegram webhook endpoint. Used when ``TELEGRAM_MODE=webhook``. The route does…, get_settings(), Centralised application configuration. All runtime configuration is read from…, Return the process-wide settings singleton. Cached so that ``.env`` parsing and…, configure_logging(), get_logger(), JsonFormatter (+21 more)

### Community 8 - "ToolRegistry"
Cohesion: 0.09
Nodes (30): Tool catalogue and the validation boundary around it., _clip_payload(), _decode_arguments(), _describe_validation_error(), _error(), Any, Tool registry: the only bridge between the language model and the backend. The…, Return a tool by name, or ``None`` when it is not registered. (+22 more)

### Community 9 - "commands.py"
Cohesion: 0.13
Nodes (29): Attach every handler in priority order., _register_handlers(), attendance_command(), classes_command(), help_command(), DEFAULT_TYPE, Update, Slash-command handlers. Commands are shortcuts, not the primary interface:… (+21 more)

### Community 10 - "StudentService"
Cohesion: 0.15
Nodes (14): DuplicateStudentError, The student ID is already taken within the class., ListStudentsOutput, Return every student plausibly referred to by ``reference``., Enrol a new student into a class. Raises: ClassNotFoundError: If the target…, Remove a student and their attendance history. Raises:…, Update a student's details, changing only the fields supplied. Raises:…, List the roster of one class. (+6 more)

### Community 11 - "test_keyboards.py"
Cohesion: 0.09
Nodes (41): AttendanceEntry, AttendanceSessionRead, AttendanceSummary, One student's state inside an attendance session., Counts of each status within a session or a date range., Share of students who were in the room (present or late), 0..1., Full state of an attendance session., build_attendance_keyboard() (+33 more)

### Community 12 - "test_agent.py"
Cohesion: 0.18
Nodes (24): FakeResponse, make_agent(), Any, The agent's tool-calling loop, driven by a scripted model. The Ollama client is…, A model stuck in a tool loop must not spin forever., John absent' works because the focus hint identifies the session., Mimics an Ollama ``/api/chat`` JSON body., Stands in for :class:`~app.ai.client.OllamaClient`. (+16 more)

### Community 13 - "test_tool_schema.py"
Cohesion: 0.11
Nodes (28): build_openai_tool_schema(), build_tool_schema(), _inline_refs(), Any, BaseModel, Convert Pydantic models into JSON schemas for local LLM function tools. Local…, Build a JSON schema for a tool's input model. Args: model: The Pydantic model…, Build a strict-mode JSON schema for legacy OpenAI tool definitions. (+20 more)

### Community 14 - "test_reports.py"
Cohesion: 0.12
Nodes (26): AttendanceReportInput, Arguments for ``student_attendance_report``., Arguments for ``list_students_by_status``. Answers "who was absent today?" and…, Arguments for ``attendance_report``. Covers "attendance for SE401", "attendance…, StudentAttendanceReportInput, StudentsByStatusInput, Turn a named period into a concrete inclusive date range. Keeping this in one…, resolve_period() (+18 more)

### Community 15 - "conftest.py"
Cohesion: 0.12
Nodes (15): Database, Any, Override the process-wide database. Intended for tests only., Owns the async engine and hands out sessions., Create the engine and session factory. Args: settings: Configuration supplying…, Pool tuning that only applies to real server-backed databases. SQLite (used by…, The underlying async engine., Factory used to create new sessions. (+7 more)

### Community 16 - "AppError"
Cohesion: 0.22
Nodes (7): AppError, Any, Base class for every expected, user-recoverable domain failure., Create the error. Args: message: Teacher-safe explanation. Falls back to…, Serialise the error for tool output or an HTTP error body., Return a developer-facing representation including the error code., Exception

### Community 17 - "exceptions.py"
Cohesion: 0.10
Nodes (26): FastAPI, HTTP translation of domain errors. The API surface reuses the same exception…, Install the application-wide exception handlers., register_exception_handlers(), HTTP API: health probes and the Telegram webhook receiver., AmbiguousReferenceError, AmbiguousStudentError, AttendanceAlreadyTakenError (+18 more)

### Community 18 - "definitions.py"
Cohesion: 0.14
Nodes (34): _add_student(), _attendance_report(), _attendance_state(), build_registry(), _cancel_attendance(), _class_info(), _create_class(), _delete_class() (+26 more)

### Community 19 - "test_registry.py"
Cohesion: 0.13
Nodes (12): context(), crash(), echo(), EchoInput, EchoOutput, explode(), fixture, Tests for the tool registry — the validation boundary around the model. (+4 more)

### Community 20 - "messages.py"
Cohesion: 0.17
Nodes (16): _close_board(), handle_message(), DEFAULT_TYPE, Message, Update, Natural-language message handler. This is the primary interface: the teacher…, Draw the board, editing the existing one when possible., Strip the buttons from a board whose session has ended. (+8 more)

### Community 21 - "test_text.py"
Cohesion: 0.13
Nodes (27): find_matches(), normalize(), normalize_code(), Text normalisation and fuzzy-matching helpers. Teachers refer to students the…, Remove diacritics so ``"Nguyễn"`` and ``"Nguyen"`` compare equal., Casefold, strip accents and collapse whitespace for comparison., Canonical form for identifiers such as student codes and class names., Return a 0..1 similarity ratio between two normalised strings. (+19 more)

### Community 22 - "today"
Cohesion: 0.11
Nodes (31): Create the store. Args: ttl_seconds: Idle lifetime of a conversation. Defaults…, current_timezone(), format_date(), month_bounds(), parse_date(), date, ZoneInfo, Date and time helpers. Attendance is anchored to the teacher's local calendar… (+23 more)

### Community 23 - "StudentRepository"
Cohesion: 0.13
Nodes (11): Select, Queries scoped to the students inside a teacher's classes., Base query joining through ``classes`` to enforce ownership., Fetch one student by id, scoped to the owning teacher., Fetch a student together with their class., Fetch a student by their code within one class., Find every student with this code across all of a teacher's classes. Codes are…, Return the roster of a class ordered by name. (+3 more)

### Community 24 - "test_attendance_flow.py"
Cohesion: 0.08
Nodes (53): AttendanceSessionStatus, StrEnum, Lifecycle of an attendance session., FinishAttendanceInput, GetAttendanceStateInput, MarkRemainingInput, Attendance read models and tool contracts., Arguments for ``update_attendance``. (+45 more)

### Community 25 - "class_service.py"
Cohesion: 0.06
Nodes (44): ClassInfoInput, ClassInfoOutput, CreateClassInput, CreateClassOutput, DeleteClassInput, DeleteClassOutput, ListClassesOutput, Class read models and tool contracts. (+36 more)

### Community 26 - "ClassService"
Cohesion: 0.13
Nodes (12): ClassRepository, Queries scoped to a single teacher's classes. Every method takes ``teacher_id``…, Number of students enrolled in a class., Wire the service to its collaborators. Args: attendance_repository: Access to…, ClassService, Create, rename, delete and inspect a teacher's classes. Also owns…, Wire the service to its data sources. Args: class_repository: Access to the…, Service composition root. Wiring lives here rather than inside the services… (+4 more)

### Community 27 - "agent.py"
Cohesion: 0.13
Nodes (21): AgentReply, AssistantAgent, _clip_for_log(), _message_from_last_tool(), Any, The assistant agent: one user message in, one reply out. Implements the tool-…, Call Ollama, translating transport failures. Raises: AssistantError: If the…, Render a value for logs without dumping unbounded model output. (+13 more)

### Community 28 - "test_api.py"
Cohesion: 0.12
Nodes (12): http_status_for(), Map a domain error onto an HTTP status code., ClassNotFoundError, The teacher has no class with the requested name., client(), AsyncClient, fixture, parametrize (+4 more)

### Community 29 - "._owned"
Cohesion: 0.20
Nodes (5): Select, Fetch one class by id, scoped to its owner., Fetch a class by its name, case-insensitively., Return every class owned by the teacher, alphabetically., Fetch a class with its student collection eagerly loaded.

### Community 30 - "formatting.py"
Cohesion: 0.20
Nodes (15): clip(), escape_html(), Rendering helpers for Telegram messages. Two parse modes are used deliberately:…, Render the final summary shown when a session is completed., Escape a dynamic value for Telegram's HTML parse mode., Trim a message to Telegram's maximum length., Icon for a status, or a hollow marker when the student is unmarked., One-line tally, e.g. ``✅ 18 ❌ 2 🟡 1 ⬜ 3``. (+7 more)

### Community 31 - "ollama.py"
Cohesion: 0.11
Nodes (30): history_to_messages(), _iter_json_objects(), _looks_like_create_class(), new_call_id(), Any, Ollama conversation adapter. Translates between the internal history format…, Map a mis-chosen fee update onto ``create_class`` when the teacher asked to…, Heuristic: teacher is asking to create/add a new class. (+22 more)

### Community 32 - "student_service.py"
Cohesion: 0.08
Nodes (37): AddStudentInput, AddStudentOutput, ListStudentsInput, Student read models and tool contracts., Result of updating a student., Arguments for ``list_students``., Arguments for ``search_student``., Students matching a search. (+29 more)

### Community 33 - "ai/tools/ Registry Validation Boundary"
Cohesion: 0.12
Nodes (18): api Uvicorn Service, db PostgreSQL Service, migrate Alembic Service, postgres-data Volume, ai/ Agent Layer, Class Management Assistant, ConversationStore Protocol, Layered Architecture (+10 more)

### Community 34 - "Settings"
Cohesion: 0.08
Nodes (31): Wire the agent to its dependencies. Args: client: Configured Ollama client.…, build_ollama_client(), get_ollama_client(), OllamaClient, Ollama client construction. Isolated from the agent so that timeouts and the…, Thin async wrapper around Ollama's ``/api/chat`` endpoint., Create the client. Args: base_url: Ollama server root, e.g.…, Close the underlying HTTP client. (+23 more)

### Community 35 - "ServiceContainer"
Cohesion: 0.07
Nodes (17): Tuition fee settings and billing reports., Lazily builds the service graph for a single unit of work. All services share…, Fall back to the process settings singleton when none was injected., Data access for teacher accounts., Data access for classes., Data access for students., Data access for attendance sessions, records and aggregates., Onboarding and authorisation of Telegram users. (+9 more)

### Community 36 - "BaseRepository"
Cohesion: 0.14
Nodes (12): BaseRepository, AsyncSession, CRUD primitives shared by every concrete repository. Subclasses set…, Bind the repository to a unit of work. Args: session: The active transactional…, Fetch a row by primary key, or ``None`` when it does not exist., Persist a new instance and flush so its primary key is populated., Delete an instance and flush the change., Delete by primary key without loading the row. Returns: The number of rows… (+4 more)

### Community 37 - "callbacks.py"
Cohesion: 0.20
Nodes (13): _apply(), _entry_name(), handle_attendance_callback(), DEFAULT_TYPE, Update, Inline-keyboard callback handlers. Button presses bypass the language model…, Name of a student inside a rendered session, for the toast message., Apply an attendance button press and redraw the board. (+5 more)

### Community 38 - "readiness"
Cohesion: 0.18
Nodes (13): liveness(), LivenessResponse, AsyncSession, BaseModel, Reply to a liveness probe., Reply to a readiness probe., Report that the process is up. Deliberately dependency-free: an orchestrator…, Report whether the service can actually serve traffic. (+5 more)

### Community 39 - "ValueError"
Cohesion: 0.22
Nodes (5): field_validator, ZoneInfo, Resolved :class:`ZoneInfo` for :attr:`timezone`., Normalise a PostgreSQL DSN to the asyncpg driver. Deployment platforms hand out…, ValueError

### Community 40 - "env.py"
Cohesion: 0.22
Nodes (10): do_run_migrations(), Alembic migration environment. The engine is built from the application…, Emit SQL to stdout without connecting to a database., Run migrations on an already-established synchronous connection., Connect with the async driver and delegate to the sync runner., Entry point for online migrations., run_async_migrations(), run_migrations_offline() (+2 more)

### Community 41 - "ConversationState"
Cohesion: 0.09
Nodes (28): ConversationState, InMemoryConversationStore, Short-lived conversation state. The assistant needs just enough memory to make…, How long a conversation survives without activity., Return the live state for a chat, dropping it if it has expired., Persist a conversation and refresh its expiry., Forget a conversation entirely., Drop every expired conversation. Returns: How many conversations were removed.… (+20 more)

### Community 42 - "validate_meaningful_name"
Cohesion: 0.33
Nodes (4): field_validator, Reject names that carry no alphanumeric content. Args: value: The candidate…, validate_meaningful_name(), field_validator

### Community 43 - "Code Review Skill"
Cohesion: 0.32
Nodes (8): Code Review Agent UI, Code Review Skill, Fixed Point Diff Pinning, Parallel Sub-Agents Aggregation, Fowler Smell Baseline, Spec Review Axis, Standards Review Axis, Why Two Axes Separation

### Community 44 - "services"
Cohesion: 0.22
Nodes (10): _configure_environment(), AsyncSession, fixture, Three students enrolled in :func:`classroom`., Pin configuration for the whole test session. Environment variables win over…, A transactional session, committed when the test body succeeds., Service container bound to the test session., roster() (+2 more)

### Community 46 - "PermissionDeniedError"
Cohesion: 0.40
Nodes (4): PermissionDeniedError, The caller does not own, and may not touch, the target resource., Return the teacher for a Telegram user, creating them on first use. Profile…, Enforce the optional allow-list from configuration.

### Community 47 - "get_session"
Cohesion: 0.24
Nodes (8): get_session(), AsyncSession, FastAPI dependency yielding a transactional session., Yield a session inside a transaction (unit of work). The transaction is…, identity_from(), Open a unit of work and resolve the teacher behind an update. Everything a…, Project a Telegram user onto the identity the service layer expects., TelegramUser

### Community 48 - "telegram_webhook"
Cohesion: 0.33
Nodes (6): Any, Accept one update from Telegram and hand it to the bot application. Args:…, telegram_webhook(), Header, post, Request

### Community 52 - "Attendance Session Per Class Per Day"
Cohesion: 0.50
Nodes (4): Attendance Session Per Class Per Day, Buttons and Typing Share Implementation, Teacher-Class-Student-Attendance Data Model, Sessions Are Database State

### Community 53 - "Grill Me Skill"
Cohesion: 0.67
Nodes (3): Grill Me Agent UI, Grill Me Skill, Grilling Session

### Community 57 - "ConversationStore"
Cohesion: 0.22
Nodes (6): ConversationStore, Storage for :class:`ConversationState`, keyed by chat id., Return the live state for a chat, or ``None`` if absent or expired., Persist a conversation, refreshing its expiry., Forget a conversation entirely., Protocol

### Community 59 - "format_vnd"
Cohesion: 0.28
Nodes (6): Set the daily tuition fee charged per attended day for every student., format_vnd(), VND formatting helpers., Format an integer amount as Vietnamese đồng with dot thousands separators., Tests for VND formatting., test_format_vnd_uses_dot_thousands_separator()

### Community 60 - "TeacherService"
Cohesion: 0.40
Nodes (5): Queries scoped to teacher accounts., TeacherRepository, Maps a Telegram account onto a teacher record. This is the application's…, Wire the service to its data source. Args: teacher_repository: Access to the…, TeacherService

### Community 69 - ".chat"
Cohesion: 0.40
Nodes (3): Any, AsyncClient, Send one non-streaming chat request with optional tools. Args: model: Ollama…

### Community 70 - ".register"
Cohesion: 0.50
Nodes (3): BaseModel, Add a tool to the catalogue. Args: name: Name the model will call, e.g.…, ToolHandler

## Knowledge Gaps
- **11 isolated node(s):** `class-management`, `Fowler Smell Baseline`, `Fixed Point Diff Pinning`, `Code Review Agent UI`, `Grilling Session` (+6 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **18 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `AttendanceRepository` connect `AttendanceRepository` to `attendance_service.py`, `AttendanceStatus`, `tuition_service.py`, `AttendanceService`, `Student`, `ServiceContainer`, `.add_record`, `.get_record`, `.list_records`, `test_attendance_flow.py`, `class_service.py`, `ClassService`?**
  _High betweenness centrality (0.090) - this node is a cross-community bridge._
- **Why does `AttendanceStatus` connect `AttendanceStatus` to `attendance_service.py`, `tuition_service.py`, `AttendanceService`, `Student`, `AttendanceRepository`, `ToolOutput`, `callbacks.py`, `test_keyboards.py`, `test_agent.py`, `test_reports.py`, `definitions.py`, `test_attendance_flow.py`, `formatting.py`?**
  _High betweenness centrality (0.085) - this node is a cross-community bridge._
- **Why does `Settings` connect `Settings` to `ClassService`, `ServiceContainer`, `readiness`, `ValueError`, `get_settings`, `conftest.py`, `.sync_database_url`, `agent.py`, `TeacherService`?**
  _High betweenness centrality (0.059) - this node is a cross-community bridge._
- **Are the 37 inferred relationships involving `AttendanceStatus` (e.g. with `AttendanceRecord` and `AttendanceSession`) actually correct?**
  _`AttendanceStatus` has 37 INFERRED edges - model-reasoned connections that need verification._
- **Are the 61 inferred relationships involving `ToolOutput` (e.g. with `AttendanceEntry` and `AttendanceSessionRead`) actually correct?**
  _`ToolOutput` has 61 INFERRED edges - model-reasoned connections that need verification._
- **Are the 61 inferred relationships involving `ToolInput` (e.g. with `AttendanceEntry` and `AttendanceSessionRead`) actually correct?**
  _`ToolInput` has 61 INFERRED edges - model-reasoned connections that need verification._
- **Are the 39 inferred relationships involving `OperationResult` (e.g. with `AttendanceEntry` and `AttendanceSessionRead`) actually correct?**
  _`OperationResult` has 39 INFERRED edges - model-reasoned connections that need verification._