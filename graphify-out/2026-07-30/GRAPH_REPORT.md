# Graph Report - class-management  (2026-07-30)

## Corpus Check
- 97 files · ~38,814 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1395 nodes · 3658 edges · 80 communities (62 shown, 18 thin omitted)
- Extraction: 87% EXTRACTED · 13% INFERRED · 0% AMBIGUOUS · INFERRED: 468 edges (avg confidence: 0.53)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `70ca03e0`
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
1. `AttendanceStatus` - 82 edges
2. `ToolOutput` - 74 edges
3. `ToolInput` - 72 edges
4. `OperationResult` - 53 edges
5. `AttendanceRepository` - 47 edges
6. `ToolContext` - 44 edges
7. `AttendanceService` - 43 edges
8. `Settings` - 42 edges
9. `Student` - 41 edges
10. `get_settings()` - 38 edges

## Surprising Connections (you probably didn't know these)
- `db PostgreSQL Service` --semantically_similar_to--> `PostgreSQL`  [INFERRED] [semantically similar]
  docker-compose.yml → README.md
- `FakeResponse` --uses--> `AssistantAgent`  [INFERRED]
  tests/integration/test_agent.py → app/ai/agent.py
- `_ScriptedAio` --uses--> `AssistantAgent`  [INFERRED]
  tests/integration/test_agent.py → app/ai/agent.py
- `ScriptedClient` --uses--> `AssistantAgent`  [INFERRED]
  tests/integration/test_agent.py → app/ai/agent.py
- `_ScriptedModels` --uses--> `AssistantAgent`  [INFERRED]
  tests/integration/test_agent.py → app/ai/agent.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Two-Axis Parallel Code Review Flow** — _agents_skills_code_review_skill_code_review, _agents_skills_code_review_skill_standards_axis, _agents_skills_code_review_skill_spec_axis, _agents_skills_code_review_skill_parallel_sub_agents, _agents_skills_code_review_skill_fixed_point [EXTRACTED 1.00]
- **Telegram-to-PostgreSQL Request Path** — readme_telegram_layer, readme_ai_agent_layer, readme_tools_registry, readme_services_layer, readme_repositories_layer, readme_postgresql [EXTRACTED 1.00]
- **Docker Compose Deploy Stack** — docker_compose_db, docker_compose_migrate, docker_compose_api [EXTRACTED 1.00]

## Communities (80 total, 18 thin omitted)

### Community 0 - "attendance_service.py"
Cohesion: 0.09
Nodes (26): AttendanceSessionStatus, StrEnum, Lifecycle of an attendance session., AttendanceEntry, AttendanceSummary, FinishAttendanceOutput, GetAttendanceStateInput, MarkRemainingOutput (+18 more)

### Community 1 - "AttendanceStatus"
Cohesion: 0.06
Nodes (57): Build a summary from per-status counts.          Args:             counts: Numbe, AttendanceHistoryEntry, AttendanceReportInput, AttendanceReportOutput, MonthlySummaryInput, MonthlySummaryOutput, Reporting tool contracts., Arguments for ``student_attendance_report``. (+49 more)

### Community 2 - "tuition_service.py"
Cohesion: 0.07
Nodes (41): ClassAlreadyExistsError, The teacher already owns a class with that name., ClassRepository, Queries scoped to a single teacher's classes.      Every method takes ``teacher_, ClassTuitionSummary, Tuition billing tool contracts., Arguments for ``set_class_tuition_fee``., Result of updating a class tuition fee. (+33 more)

### Community 3 - "AttendanceService"
Cohesion: 0.09
Nodes (21): AttendanceAlreadyTakenError, NoActiveAttendanceSessionError, Attendance for that class and date is already complete., No attendance session is currently open., AttendanceService, Record one student's status in the active session.          Raises:, Mark a student by primary key, for Telegram inline buttons.          Raises:, Apply one status to every student not marked yet. (+13 more)

### Community 4 - "Student"
Cohesion: 0.13
Nodes (29): AttendanceRecord, Attendance ORM models., The status of one student within one attendance session., Base, IdMixin, Declarative base and shared column mixins., Base class for every ORM model., Surrogate integer primary key. (+21 more)

### Community 5 - "AttendanceRepository"
Cohesion: 0.10
Nodes (15): AttendanceRepository, date, Total number of attendance sessions ever held for a class., Date of the most recent session for a class, or ``None`` if none., Count records per status for a class over a date range., Count records per status for one student over a date range., A student's day-by-day statuses over a range, oldest first., Per-student, per-status counts for a class over a range.          Powers the mon (+7 more)

### Community 6 - "ToolOutput"
Cohesion: 0.10
Nodes (35): CancelAttendanceInput, GetAttendanceStateOutput, Result of marking one student., Arguments for ``cancel_attendance``., The currently open session, if there is one., UpdateAttendanceOutput, ClassInfoOutput, ClassRead (+27 more)

### Community 7 - "get_settings"
Cohesion: 0.08
Nodes (37): Health and readiness endpoints., Telegram webhook endpoint.  Used when ``TELEGRAM_MODE=webhook``.  The route does, get_settings(), Centralised application configuration.  All runtime configuration is read from e, Whether the process is running in the production environment., Return the process-wide settings singleton.      Cached so that ``.env`` parsing, Strongly typed application settings.      Attributes are populated from environm, Settings (+29 more)

### Community 8 - "ToolRegistry"
Cohesion: 0.08
Nodes (30): Tool catalogue and the validation boundary around it., _clip_payload(), _decode_arguments(), _error(), Any, Tool, Tool registry: the only bridge between the language model and the backend.  The, Return a tool by name, or ``None`` when it is not registered. (+22 more)

### Community 9 - "commands.py"
Cohesion: 0.14
Nodes (29): Attach every handler in priority order., _register_handlers(), handle_attendance_callback(), DEFAULT_TYPE, Update, Apply an attendance button press and redraw the board., attendance_command(), classes_command() (+21 more)

### Community 10 - "StudentService"
Cohesion: 0.15
Nodes (17): AddStudentInput, Arguments for ``add_student``., Arguments for ``update_student``.      Only the fields that are supplied are cha, UpdateStudentInput, Student management and reference resolution against a real database., The same person's name in two classes is only ambiguous across both., test_add_student(), test_ambiguity_is_resolved_by_narrowing_to_a_class() (+9 more)

### Community 11 - "test_keyboards.py"
Cohesion: 0.08
Nodes (41): AttendanceStatus, Enumerations shared by the ORM models, schemas and AI tool contracts., Icon used when rendering the status in Telegram., Human-readable label, e.g. ``"Late"``., Whether the status contributes to the attendance rate.          Late students we, How a student was accounted for in a single attendance session., Count records per status within a single session., Inline-keyboard callback handlers.  Button presses bypass the language model ent (+33 more)

### Community 12 - "test_agent.py"
Cohesion: 0.11
Nodes (40): AssistantError, The assistant could not complete the turn., FunctionCall, _build_gemini_response(), _content_texts(), FakeResponse, _first_function_response(), make_agent() (+32 more)

### Community 13 - "test_tool_schema.py"
Cohesion: 0.10
Nodes (31): build_openai_tool_schema(), build_tool_schema(), _inline_refs(), Any, BaseModel, Convert Pydantic models into JSON schemas for local LLM function tools.  Local L, Build a JSON schema for a tool's input model.      Args:         model: The Pyda, Build a strict-mode JSON schema for legacy OpenAI tool definitions. (+23 more)

### Community 14 - "test_reports.py"
Cohesion: 0.16
Nodes (9): AttendanceSession, One roll-call for a class on a given calendar day.      At most one session may, Whether records may still be modified., Select, Every session a teacher held on one day, with class preloaded., Fetch a session by id, scoped to the owning teacher., Fetch a session with its records, students and class eagerly loaded., Fetch the currently open session for a class, if any. (+1 more)

### Community 15 - "conftest.py"
Cohesion: 0.08
Nodes (26): Database, Any, AsyncSession, Override the process-wide database.  Intended for tests only., Owns the async engine and hands out sessions., Create the engine and session factory.          Args:             settings: Conf, Pool tuning that only applies to real server-backed databases.          SQLite (, The underlying async engine. (+18 more)

### Community 16 - "AppError"
Cohesion: 0.13
Nodes (12): AppError, PermissionDeniedError, Any, Base class for every expected, user-recoverable domain failure., Create the error.          Args:             message: Teacher-safe explanation., Serialise the error for tool output or an HTTP error body., Return a developer-facing representation including the error code., The caller does not own, and may not touch, the target resource. (+4 more)

### Community 17 - "exceptions.py"
Cohesion: 0.09
Nodes (28): FastAPI, HTTP translation of domain errors.  The API surface reuses the same exception hi, Install the application-wide exception handlers., register_exception_handlers(), HTTP API: health probes and the Telegram webhook receiver., AmbiguousReferenceError, AmbiguousStudentError, AttendanceSessionClosedError (+20 more)

### Community 18 - "definitions.py"
Cohesion: 0.15
Nodes (32): _add_student(), _attendance_report(), _attendance_state(), build_registry(), _cancel_attendance(), _class_info(), _create_class(), _delete_class() (+24 more)

### Community 19 - "test_registry.py"
Cohesion: 0.12
Nodes (15): ClassNotFoundError, The teacher has no class with the requested name., test_error_serialisation_is_safe_to_return(), context(), crash(), echo(), EchoInput, EchoOutput (+7 more)

### Community 20 - "messages.py"
Cohesion: 0.12
Nodes (29): AttendanceSessionRead, Full state of an attendance session., clip(), Trim a message to Telegram's maximum length., Render the live attendance message body.      The whole roster is listed regardl, render_attendance_session(), _close_board(), handle_message() (+21 more)

### Community 21 - "test_text.py"
Cohesion: 0.12
Nodes (28): Return every student plausibly referred to by ``reference``., find_matches(), normalize(), normalize_code(), Text normalisation and fuzzy-matching helpers.  Teachers refer to students the w, Remove diacritics so ``"Nguyễn"`` and ``"Nguyen"`` compare equal., Casefold, strip accents and collapse whitespace for comparison., Canonical form for identifiers such as student codes and class names. (+20 more)

### Community 22 - "today"
Cohesion: 0.18
Nodes (13): DateRange, StrEnum, Named date ranges the model can request without doing date arithmetic.      Lett, The concrete range a report was computed over., ReportPeriod, ClassTeachingDaysRow, field_validator, Teaching-day count for one class. (+5 more)

### Community 23 - "StudentRepository"
Cohesion: 0.12
Nodes (12): Select, Queries scoped to the students inside a teacher's classes., Base query joining through ``classes`` to enforce ownership., Fetch one student by id, scoped to the owning teacher., Fetch a student together with their class., Fetch a student by their code within one class., Find every student with this code across all of a teacher's classes.          Co, Return the roster of a class ordered by name. (+4 more)

### Community 24 - "test_attendance_flow.py"
Cohesion: 0.06
Nodes (68): How long a conversation survives without activity., FinishAttendanceInput, Arguments for ``update_attendance``., Arguments for ``finish_attendance``., Arguments for ``start_attendance``., StartAttendanceInput, UpdateAttendanceInput, Arguments for ``tuition_report``.      Answers questions like "tuition for SE401 (+60 more)

### Community 25 - "class_service.py"
Cohesion: 0.09
Nodes (24): ClassInfoInput, CreateClassInput, DeleteClassInput, Arguments for ``get_class_info``., Arguments for ``create_class``., Arguments for ``rename_class``., Arguments for ``delete_class``., RenameClassInput (+16 more)

### Community 27 - "agent.py"
Cohesion: 0.20
Nodes (13): _clip_for_log(), _final_reply_text(), _message_from_last_tool(), Any, GenerateContentResponse, Tool, Handle one user message.          Args:             message: What the teacher ty, Call Gemini, translating transport failures.          Raises:             Assist (+5 more)

### Community 28 - "test_api.py"
Cohesion: 0.14
Nodes (9): http_status_for(), Map a domain error onto an HTTP status code., client(), AsyncClient, fixture, parametrize, HTTP surface: health probes, the webhook receiver and error mapping., An HTTP client bound to the app without running its lifespan.      Skipping the (+1 more)

### Community 29 - "._owned"
Cohesion: 0.20
Nodes (5): Select, Fetch one class by id, scoped to its owner., Fetch a class by its name, case-insensitively., Return every class owned by the teacher, alphabetically., Fetch a class with its student collection eagerly loaded.

### Community 30 - "formatting.py"
Cohesion: 0.20
Nodes (13): escape_html(), Rendering helpers for Telegram messages.  Two parse modes are used deliberately:, Render the final summary shown when a session is completed., Escape a dynamic value for Telegram's HTML parse mode., Icon for a status, or a hollow marker when the student is unmarked., One-line tally, e.g. ``✅ 18  ❌ 2  🟡 1  ⬜ 3``., One roster line: icon, name and student code., _render_entry() (+5 more)

### Community 31 - "ollama.py"
Cohesion: 0.18
Nodes (16): history_to_messages(), Any, Map a mis-chosen fee update onto ``create_class`` when the teacher asked to crea, Convert stored history items into Ollama chat messages.      Args:         histo, Separate function calls from assistant text in an Ollama chat response.      Arg, rewrite_create_class_intent(), split_response(), Tests for the Ollama conversation adapter. (+8 more)

### Community 32 - "student_service.py"
Cohesion: 0.08
Nodes (31): AddStudentOutput, ListStudentsInput, ListStudentsOutput, Student read models and tool contracts., Result of updating a student., Arguments for ``list_students``., Arguments for ``search_student``., Students matching a search. (+23 more)

### Community 33 - "ai/tools/ Registry Validation Boundary"
Cohesion: 0.12
Nodes (18): api Uvicorn Service, db PostgreSQL Service, migrate Alembic Service, postgres-data Volume, ai/ Agent Layer, Class Management Assistant, ConversationStore Protocol, Layered Architecture (+10 more)

### Community 34 - "Settings"
Cohesion: 0.08
Nodes (31): AssistantAgent, Runs the model's tool-calling loop for one conversation turn., Wire the agent to its dependencies.          Args:             client: Configure, build_gemini_client(), GeminiClient, get_gemini_client(), AsyncClient, Gemini client construction.  Isolated from the agent so that timeouts and creden (+23 more)

### Community 35 - "ServiceContainer"
Cohesion: 0.08
Nodes (16): Wire the service to its collaborators.          Args:             attendance_rep, Tuition fee settings and billing reports., Lazily builds the service graph for a single unit of work.      All services sha, Data access for classes., Data access for attendance sessions, records and aggregates., Onboarding and authorisation of Telegram users., Class creation, renaming, deletion and lookup., Student enrolment, updates and reference resolution. (+8 more)

### Community 36 - "BaseRepository"
Cohesion: 0.14
Nodes (12): BaseRepository, AsyncSession, CRUD primitives shared by every concrete repository.      Subclasses set :attr:`, Bind the repository to a unit of work.          Args:             session: The a, Fetch a row by primary key, or ``None`` when it does not exist., Persist a new instance and flush so its primary key is populated., Delete an instance and flush the change., Delete by primary key without loading the row.          Returns:             The (+4 more)

### Community 37 - "callbacks.py"
Cohesion: 0.18
Nodes (11): _apply(), _entry_name(), Name of a student inside a rendered session, for the toast message., Perform the requested action and report what should be rendered.      Args:, handle_error(), _notify(), DEFAULT_TYPE, Log an unhandled exception and tell the teacher something useful. (+3 more)

### Community 38 - "readiness"
Cohesion: 0.18
Nodes (13): liveness(), LivenessResponse, AsyncSession, BaseModel, Reply to a liveness probe., Reply to a readiness probe., Report that the process is up.      Deliberately dependency-free: an orchestrato, Report whether the service can actually serve traffic. (+5 more)

### Community 39 - "ValueError"
Cohesion: 0.25
Nodes (5): field_validator, ZoneInfo, Resolved :class:`ZoneInfo` for :attr:`timezone`., Normalise a PostgreSQL DSN to the asyncpg driver.          Deployment platforms, ValueError

### Community 40 - "env.py"
Cohesion: 0.22
Nodes (10): do_run_migrations(), Alembic migration environment.  The engine is built from the application ``Setti, Emit SQL to stdout without connecting to a database., Run migrations on an already-established synchronous connection., Connect with the async driver and delegate to the sync runner., Entry point for online migrations., run_async_migrations(), run_migrations_offline() (+2 more)

### Community 41 - "ConversationState"
Cohesion: 0.07
Nodes (37): The assistant agent: one user message in, one reply out.  Implements the tool-ca, ConversationState, InMemoryConversationStore, Any, Short-lived conversation state.  The assistant needs just enough memory to make, Create the store.          Args:             ttl_seconds: Idle lifetime of a con, Return the live state for a chat, dropping it if it has expired., Persist a conversation and refresh its expiry. (+29 more)

### Community 42 - "validate_meaningful_name"
Cohesion: 0.33
Nodes (4): field_validator, Reject names that carry no alphanumeric content.      Args:         value: The c, validate_meaningful_name(), field_validator

### Community 43 - "Code Review Skill"
Cohesion: 0.32
Nodes (8): Code Review Agent UI, Code Review Skill, Fixed Point Diff Pinning, Parallel Sub-Agents Aggregation, Fowler Smell Baseline, Spec Review Axis, Standards Review Axis, Why Two Axes Separation

### Community 44 - "services"
Cohesion: 0.21
Nodes (11): history_to_contents(), Any, Content, GenerateContentResponse, Gemini conversation adapter.  Translates between the internal history format sha, Convert stored history items into Gemini ``Content`` messages.      Args:, Separate function calls from assistant text in a Gemini response.      Args:, split_response() (+3 more)

### Community 45 - ".names"
Cohesion: 0.19
Nodes (12): _first_non_empty(), _looks_like_add_student(), _looks_like_create_class(), _parse_add_student_from_message(), Ollama conversation adapter.  Translates between the internal history format sha, Map a mis-chosen attendance mark onto ``add_student`` when enrolling.      Local, Heuristic: teacher wants to enrol a new student, not mark attendance., Best-effort scrape of enrolment fields from the teacher's message. (+4 more)

### Community 46 - "PermissionDeniedError"
Cohesion: 0.20
Nodes (12): _iter_json_objects(), new_call_id(), Pull tool-call JSON out of plain content when the model narrated it., Create a stable-enough identifier for a function call within one turn., Fix common local-model JSON mistakes before ``json.loads``., Yield top-level ``{...}`` slices, respecting string escaping., Return a normalised tool call when *blob* looks like one., Last-resort scrape of tool name + common create/fee fields from broken JSON. (+4 more)

### Community 47 - "get_session"
Cohesion: 0.33
Nodes (5): Yield a session inside a transaction (unit of work).          The transaction is, identity_from(), Open a unit of work and resolve the teacher behind an update.          Everythin, Project a Telegram user onto the identity the service layer expects., TelegramUser

### Community 48 - "telegram_webhook"
Cohesion: 0.33
Nodes (6): Any, Accept one update from Telegram and hand it to the bot application.      Args:, telegram_webhook(), Header, post, Request

### Community 52 - "Attendance Session Per Class Per Day"
Cohesion: 0.50
Nodes (4): Attendance Session Per Class Per Day, Buttons and Typing Share Implementation, Teacher-Class-Student-Attendance Data Model, Sessions Are Database State

### Community 53 - "Grill Me Skill"
Cohesion: 0.67
Nodes (3): Grill Me Agent UI, Grill Me Skill, Grilling Session

### Community 55 - ".get_by_telegram_id"
Cohesion: 0.43
Nodes (6): Whether to ignore the model's words and show the tool result instead., _should_use_tool_message_instead(), Tests for post-tool reply selection., test_empty_reply_after_tools_should_use_tool_message(), test_normal_summary_is_kept(), test_refusal_phrases_are_detected()

### Community 57 - "ConversationStore"
Cohesion: 0.22
Nodes (6): ConversationStore, Storage for :class:`ConversationState`, keyed by chat id., Return the live state for a chat, or ``None`` if absent or expired., Persist a conversation, refreshing its expiry., Forget a conversation entirely., Protocol

### Community 59 - "format_vnd"
Cohesion: 0.50
Nodes (3): AgentReply, The outcome of a single user turn., AI layer: intent understanding and tool dispatch.  Nothing in this package touch

### Community 60 - "TeacherService"
Cohesion: 0.67
Nodes (3): _describe_validation_error(), Summarise a validation failure in language the model can act on., PydanticValidationError

### Community 70 - ".register"
Cohesion: 0.50
Nodes (3): BaseModel, Add a tool to the catalogue.          Args:             name: Name the model wil, ToolHandler

## Knowledge Gaps
- **11 isolated node(s):** `class-management`, `Fowler Smell Baseline`, `Fixed Point Diff Pinning`, `Code Review Agent UI`, `Grilling Session` (+6 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **18 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `AttendanceStatus` connect `test_keyboards.py` to `attendance_service.py`, `AttendanceStatus`, `AttendanceService`, `Student`, `AttendanceRepository`, `ToolOutput`, `test_agent.py`, `test_reports.py`, `definitions.py`, `messages.py`, `today`, `test_attendance_flow.py`, `formatting.py`?**
  _High betweenness centrality (0.095) - this node is a cross-community bridge._
- **Why does `AttendanceRepository` connect `AttendanceRepository` to `attendance_service.py`, `AttendanceStatus`, `tuition_service.py`, `AttendanceService`, `Student`, `ServiceContainer`, `test_keyboards.py`, `.add_record`, `.get_record`, `test_reports.py`, `.list_records`?**
  _High betweenness centrality (0.081) - this node is a cross-community bridge._
- **Why does `ToolRegistry` connect `ToolRegistry` to `Settings`, `.register`, `ConversationState`, `AppError`, `.__init__`, `definitions.py`, `test_registry.py`, `format_vnd`?**
  _High betweenness centrality (0.052) - this node is a cross-community bridge._
- **Are the 39 inferred relationships involving `AttendanceStatus` (e.g. with `AttendanceRecord` and `AttendanceSession`) actually correct?**
  _`AttendanceStatus` has 39 INFERRED edges - model-reasoned connections that need verification._
- **Are the 61 inferred relationships involving `ToolOutput` (e.g. with `AttendanceEntry` and `AttendanceSessionRead`) actually correct?**
  _`ToolOutput` has 61 INFERRED edges - model-reasoned connections that need verification._
- **Are the 61 inferred relationships involving `ToolInput` (e.g. with `AttendanceEntry` and `AttendanceSessionRead`) actually correct?**
  _`ToolInput` has 61 INFERRED edges - model-reasoned connections that need verification._
- **Are the 39 inferred relationships involving `OperationResult` (e.g. with `AttendanceEntry` and `AttendanceSessionRead`) actually correct?**
  _`OperationResult` has 39 INFERRED edges - model-reasoned connections that need verification._