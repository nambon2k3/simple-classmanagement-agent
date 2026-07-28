# Graph Report - simple-classmanagement-agent  (2026-07-28)

## Corpus Check
- 93 files · ~36,875 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1331 nodes · 3522 edges · 69 communities (57 shown, 12 thin omitted)
- Extraction: 87% EXTRACTED · 13% INFERRED · 0% AMBIGUOUS · INFERRED: 460 edges (avg confidence: 0.53)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `93b7b5c4`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- ._finalise
- AttendanceStatus
- ReportPeriod
- AttendanceService
- Student
- AttendanceRepository
- definitions.py
- Settings
- ToolRegistry
- bot.py
- .resolve
- attendance_service.py
- build_registry
- test_tool_schema.py
- test_reports.py
- Database
- AppError
- exceptions.py
- test_tuition.py
- ToolContext
- messages.py
- test_text.py
- today
- StudentRepository
- test_attendance_flow.py
- CreateClassInput
- class_service.py
- ConversationState
- test_api.py
- ._owned
- AttendanceSessionRead
- split_response
- test_student_service.py
- ai/tools/ Registry Validation Boundary
- timedelta
- ListStudentsInput
- .flush
- ClassAlreadyExistsError
- readiness
- ValueError
- env.py
- InMemoryConversationStore
- validate_meaningful_name
- Code Review Skill
- conftest.py
- .names
- PermissionDeniedError
- TeacherIdentity
- telegram_webhook
- .__init__
- 20260727_1445_initial_schema.py
- .list_with_student_counts
- Attendance Session Per Class Per Day
- Grill Me Skill
- .get_by_telegram_id
- .format
- .__init__
- .sync_database_url
- .finish_attendance
- ._blank_strings_become_none
- class-management
- .get_by_id

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

## Communities (69 total, 12 thin omitted)

### Community 0 - "._finalise"
Cohesion: 0.14
Nodes (9): _count_statuses(), _names_with_status(), Finalise a known session, for Telegram inline buttons., Return the currently open session, if there is one., Project a session plus its roster onto the output schema. Every student in the…, Close a session and build its summary., Tally attendance statuses across records., Names of students holding a particular status, alphabetically. (+1 more)

### Community 1 - "AttendanceStatus"
Cohesion: 0.08
Nodes (39): _monthly_summary(), _student_report(), AttendanceStatus, StrEnum, Icon used when rendering the status in Telegram., Human-readable label, e.g. ``"Late"``., Whether the status contributes to the attendance rate. Late students were in…, How a student was accounted for in a single attendance session. (+31 more)

### Community 2 - "ReportPeriod"
Cohesion: 0.13
Nodes (23): _teaching_days_report(), DateRange, StrEnum, Named date ranges the model can request without doing date arithmetic. Letting…, The concrete range a report was computed over., ReportPeriod, ClassTeachingDaysRow, ClassTuitionSummary (+15 more)

### Community 3 - "AttendanceService"
Cohesion: 0.10
Nodes (16): No student matched the reference the teacher used., StudentNotFoundError, AttendanceService, Record one student's status in the active session. Raises:…, Mark a student by primary key, for Telegram inline buttons. Raises:…, Apply one status to every student not marked yet., Abandon the active session without finalising it., Abandon a known session, for Telegram inline buttons. (+8 more)

### Community 4 - "Student"
Cohesion: 0.10
Nodes (36): AttendanceRecord, AttendanceSession, Attendance ORM models., One roll-call for a class on a given calendar day. At most one session may…, Whether records may still be modified., The status of one student within one attendance session., Base, IdMixin (+28 more)

### Community 5 - "AttendanceRepository"
Cohesion: 0.05
Nodes (26): AttendanceRepository, date, Select, Total number of attendance sessions ever held for a class., Date of the most recent session for a class, or ``None`` if none., Every session a teacher held on one day, with class preloaded., Fetch one student's record within a session., Every record in a session, with students preloaded, ordered by name. (+18 more)

### Community 6 - "definitions.py"
Cohesion: 0.08
Nodes (62): _cancel_attendance(), _class_info(), _delete_class(), _list_classes(), Registration of every tool the language model may call. Handlers here are…, _search_student(), _start_attendance(), CancelAttendanceInput (+54 more)

### Community 7 - "Settings"
Cohesion: 0.08
Nodes (40): build_ollama_client(), get_ollama_client(), Ollama client construction. Isolated from the agent so that timeouts and the…, Create an Ollama client configured from application settings., Return the process-wide Ollama client, creating it on first use., Health and readiness endpoints., Telegram webhook endpoint. Used when ``TELEGRAM_MODE=webhook``. The route does…, get_settings() (+32 more)

### Community 8 - "ToolRegistry"
Cohesion: 0.09
Nodes (30): _clip_payload(), _decode_arguments(), _describe_validation_error(), _error(), Any, Tool registry: the only bridge between the language model and the backend. The…, Return a tool by name, or ``None`` when it is not registered., Render every tool as a function declaration dict. (+22 more)

### Community 9 - "bot.py"
Cohesion: 0.07
Nodes (50): build_application(), _on_startup(), _purge_conversations(), Application, DEFAULT_TYPE, Telegram application assembly. Builds the ``python-telegram-bot`` application,…, Publish the command menu and schedule conversation clean-up., Drop conversations that have been idle past their TTL. (+42 more)

### Community 10 - ".resolve"
Cohesion: 0.13
Nodes (13): DuplicateStudentError, The student ID is already taken within the class., Return every student plausibly referred to by ``reference``., Enrol a new student into a class. Raises: ClassNotFoundError: If the target…, Remove a student and their attendance history. Raises:…, Update a student's details, changing only the fields supplied. Raises:…, List the roster of one class., Find students matching a name fragment or ID. Unlike :meth:`resolve`, several… (+5 more)

### Community 11 - "attendance_service.py"
Cohesion: 0.08
Nodes (45): _attendance_state(), _mark_remaining(), AttendanceSessionStatus, Enumerations shared by the ORM models, schemas and AI tool contracts., Lifecycle of an attendance session., AttendanceEntry, AttendanceSummary, FinishAttendanceOutput (+37 more)

### Community 12 - "build_registry"
Cohesion: 0.13
Nodes (32): build_registry(), _create_class(), _finish_attendance(), Create a registry populated with every available tool. Returns: A fully wired…, _update_attendance(), FakeResponse, make_agent(), Any (+24 more)

### Community 13 - "test_tool_schema.py"
Cohesion: 0.10
Nodes (31): build_openai_tool_schema(), build_tool_schema(), _inline_refs(), Any, BaseModel, Convert Pydantic models into JSON schemas for local LLM function tools. Local…, Build a JSON schema for a tool's input model. Args: model: The Pydantic model…, Build a strict-mode JSON schema for legacy OpenAI tool definitions. (+23 more)

### Community 14 - "test_reports.py"
Cohesion: 0.10
Nodes (29): _attendance_report(), _students_by_status(), AttendanceReportInput, Arguments for ``list_students_by_status``. Answers "who was absent today?" and…, Arguments for ``attendance_report``. Covers "attendance for SE401", "attendance…, StudentsByStatusInput, Turn a named period into a concrete inclusive date range. Keeping this in one…, resolve_period() (+21 more)

### Community 15 - "Database"
Cohesion: 0.09
Nodes (19): Database engine, session factory and connection lifecycle., Database, get_session(), Any, AsyncSession, FastAPI dependency yielding a transactional session., Owns the async engine and hands out sessions., Create the engine and session factory. Args: settings: Configuration supplying… (+11 more)

### Community 16 - "AppError"
Cohesion: 0.10
Nodes (20): http_status_for(), FastAPI, HTTP translation of domain errors. The API surface reuses the same exception…, Map a domain error onto an HTTP status code., Install the application-wide exception handlers., register_exception_handlers(), HTTP API: health probes and the Telegram webhook receiver., AppError (+12 more)

### Community 17 - "exceptions.py"
Cohesion: 0.11
Nodes (20): AmbiguousReferenceError, AmbiguousStudentError, AttendanceAlreadyTakenError, AttendanceSessionClosedError, ConflictError, EmptyClassError, NoActiveAttendanceSessionError, Domain exception hierarchy. Services raise these instead of leaking driver or… (+12 more)

### Community 18 - "test_tuition.py"
Cohesion: 0.15
Nodes (17): _set_class_tuition_fee(), _tuition_report(), Arguments for ``set_class_tuition_fee``., Arguments for ``tuition_report``. Answers questions like "tuition for SE401 in…, SetClassTuitionFeeInput, TuitionReportInput, Delegate fee updates to the class service., fee_class() (+9 more)

### Community 19 - "ToolContext"
Cohesion: 0.12
Nodes (15): Tool catalogue and the validation boundary around it., Everything a tool needs beyond its own arguments. Passing the teacher id…, ToolContext, context(), crash(), echo(), EchoInput, EchoOutput (+7 more)

### Community 20 - "messages.py"
Cohesion: 0.19
Nodes (14): _close_board(), handle_message(), DEFAULT_TYPE, Message, Update, Natural-language message handler. This is the primary interface: the teacher…, Load a session for rendering, tolerating one that has gone away., Draw the board, editing the existing one when possible. (+6 more)

### Community 21 - "test_text.py"
Cohesion: 0.13
Nodes (25): find_matches(), normalize(), Text normalisation and fuzzy-matching helpers. Teachers refer to students the…, Remove diacritics so ``"Nguyễn"`` and ``"Nguyen"`` compare equal., Casefold, strip accents and collapse whitespace for comparison., Return a 0..1 similarity ratio between two normalised strings., Rank ``candidates`` against ``query`` using a tiered matching strategy. Tiers…, similarity() (+17 more)

### Community 22 - "today"
Cohesion: 0.16
Nodes (21): current_timezone(), parse_date(), date, ZoneInfo, Date and time helpers. Attendance is anchored to the teacher's local calendar…, The configured application timezone., Return the current local calendar date. Args: tz: Timezone to resolve the date…, Coerce a user- or model-supplied value into a :class:`~datetime.date`. Accepts… (+13 more)

### Community 23 - "StudentRepository"
Cohesion: 0.11
Nodes (13): Select, Queries scoped to the students inside a teacher's classes., Base query joining through ``classes`` to enforce ownership., Fetch one student by id, scoped to the owning teacher., Fetch a student together with their class., Fetch a student by their code within one class., Find every student with this code across all of a teacher's classes. Codes are…, Return the roster of a class ordered by name. (+5 more)

### Community 24 - "test_attendance_flow.py"
Cohesion: 0.15
Nodes (27): FinishAttendanceInput, Arguments for ``update_attendance``., Arguments for ``finish_attendance``., UpdateAttendanceInput, The end-to-end attendance workflow., The inline-keyboard path and the conversational path must agree., start(), test_a_completed_session_can_be_reopened_on_request() (+19 more)

### Community 25 - "CreateClassInput"
Cohesion: 0.15
Nodes (15): _rename_class(), CreateClassInput, Arguments for ``create_class``., Arguments for ``rename_class``., RenameClassInput, test_the_focus_hint_disambiguates_two_open_sessions(), test_two_open_sessions_require_disambiguation(), Class management behaviour against a real database. (+7 more)

### Community 26 - "class_service.py"
Cohesion: 0.05
Nodes (45): ConfirmationRequiredError, A destructive action was requested without explicit confirmation. Raised rather…, ClassRepository, Queries scoped to a single teacher's classes. Every method takes ``teacher_id``…, Number of students enrolled in a class., Queries scoped to teacher accounts., TeacherRepository, ClassService (+37 more)

### Community 27 - "ConversationState"
Cohesion: 0.06
Nodes (38): AgentReply, AssistantAgent, _clip_for_log(), Any, The assistant agent: one user message in, one reply out. Implements the tool-…, Call Ollama, translating transport failures. Raises: AssistantError: If the…, Render a value for logs without dumping unbounded model output., Compact success/error summary for the model's tool-call outcome. (+30 more)

### Community 28 - "test_api.py"
Cohesion: 0.15
Nodes (8): ClassNotFoundError, The teacher has no class with the requested name., client(), AsyncClient, fixture, HTTP surface: health probes, the webhook receiver and error mapping., An HTTP client bound to the app without running its lifespan. Skipping the…, test_error_serialisation_is_safe_to_return()

### Community 29 - "._owned"
Cohesion: 0.20
Nodes (5): Select, Fetch one class by id, scoped to its owner., Fetch a class by its name, case-insensitively., Return every class owned by the teacher, alphabetically., Fetch a class with its student collection eagerly loaded.

### Community 30 - "AttendanceSessionRead"
Cohesion: 0.08
Nodes (45): AttendanceSessionRead, Full state of an attendance session., clip(), escape_html(), Rendering helpers for Telegram messages. Two parse modes are used deliberately:…, Render the final summary shown when a session is completed., Escape a dynamic value for Telegram's HTML parse mode., Trim a message to Telegram's maximum length. (+37 more)

### Community 31 - "split_response"
Cohesion: 0.15
Nodes (20): history_to_messages(), _iter_json_objects(), new_call_id(), Any, Ollama conversation adapter. Translates between the internal history format…, Pull tool-call JSON out of plain content when the model narrated it., Yield top-level ``{...}`` slices, respecting string escaping., Return a normalised tool call when *blob* looks like one. (+12 more)

### Community 32 - "test_student_service.py"
Cohesion: 0.12
Nodes (20): _add_student(), _update_student(), AddStudentInput, Arguments for ``add_student``., Arguments for ``update_student``. Only the fields that are supplied are…, UpdateStudentInput, Student management and reference resolution against a real database., The same person's name in two classes is only ambiguous across both. (+12 more)

### Community 33 - "ai/tools/ Registry Validation Boundary"
Cohesion: 0.12
Nodes (18): api Uvicorn Service, db PostgreSQL Service, migrate Alembic Service, postgres-data Volume, ai/ Agent Layer, Class Management Assistant, ConversationStore Protocol, Layered Architecture (+10 more)

### Community 34 - "timedelta"
Cohesion: 0.22
Nodes (7): Create the store. Args: ttl_seconds: Idle lifetime of a conversation. Defaults…, How long a conversation survives without activity., test_attendance_can_be_recorded_for_a_past_date(), history(), fixture, Three days of attendance: today and the two days before., timedelta

### Community 35 - "ListStudentsInput"
Cohesion: 0.25
Nodes (9): _list_students(), _remove_student(), ListStudentsInput, Arguments for ``list_students``., Arguments for ``remove_student``., RemoveStudentInput, test_list_students_is_ordered_by_name(), test_remove_deletes_the_student() (+1 more)

### Community 36 - ".flush"
Cohesion: 0.14
Nodes (8): Fetch a row by primary key, or ``None`` when it does not exist., Persist a new instance and flush so its primary key is populated., Delete an instance and flush the change., Delete by primary key without loading the row. Returns: The number of rows…, Return every row. Intended for small reference tables and tests., Push pending changes to the database without committing., Reload an instance from the database., ModelT

### Community 37 - "ClassAlreadyExistsError"
Cohesion: 0.22
Nodes (7): ClassAlreadyExistsError, The teacher already owns a class with that name., _class_read(), Rename an existing class. Raises: ClassNotFoundError: If the current name does…, List every class the teacher owns, with student counts., Project a classroom ORM row onto the teacher-facing read model., Create a new class for the teacher. Raises: ClassAlreadyExistsError: If a class…

### Community 38 - "readiness"
Cohesion: 0.18
Nodes (13): liveness(), LivenessResponse, AsyncSession, BaseModel, Reply to a liveness probe., Reply to a readiness probe., Report that the process is up. Deliberately dependency-free: an orchestrator…, Report whether the service can actually serve traffic. (+5 more)

### Community 39 - "ValueError"
Cohesion: 0.15
Nodes (8): BaseModel, Add a tool to the catalogue. Args: name: Name the model will call, e.g.…, field_validator, ZoneInfo, Resolved :class:`ZoneInfo` for :attr:`timezone`., Normalise a PostgreSQL DSN to the asyncpg driver. Deployment platforms hand out…, ToolHandler, ValueError

### Community 40 - "env.py"
Cohesion: 0.22
Nodes (10): do_run_migrations(), Alembic migration environment. The engine is built from the application…, Emit SQL to stdout without connecting to a database., Run migrations on an already-established synchronous connection., Connect with the async driver and delegate to the sync runner., Entry point for online migrations., run_async_migrations(), run_migrations_offline() (+2 more)

### Community 41 - "InMemoryConversationStore"
Cohesion: 0.10
Nodes (21): InMemoryConversationStore, Return the live state for a chat, dropping it if it has expired., Persist a conversation and refresh its expiry., Forget a conversation entirely., Drop every expired conversation. Returns: How many conversations were removed.…, Return the live conversation for a chat, creating one if needed., Mark the conversation as active right now., Whether the conversation has been idle for longer than ``ttl``. (+13 more)

### Community 42 - "validate_meaningful_name"
Cohesion: 0.33
Nodes (4): field_validator, Reject names that carry no alphanumeric content. Args: value: The candidate…, validate_meaningful_name(), field_validator

### Community 43 - "Code Review Skill"
Cohesion: 0.32
Nodes (8): Code Review Agent UI, Code Review Skill, Fixed Point Diff Pinning, Parallel Sub-Agents Aggregation, Fowler Smell Baseline, Spec Review Axis, Standards Review Axis, Why Two Axes Separation

### Community 44 - "conftest.py"
Cohesion: 0.17
Nodes (15): Override the process-wide database. Intended for tests only., set_database(), classroom(), _configure_environment(), database(), AsyncSession, fixture, Shared pytest fixtures. Integration tests run against a real (SQLite) database… (+7 more)

### Community 46 - "PermissionDeniedError"
Cohesion: 0.40
Nodes (4): PermissionDeniedError, The caller does not own, and may not touch, the target resource., Return the teacher for a Telegram user, creating them on first use. Profile…, Enforce the optional allow-list from configuration.

### Community 47 - "TeacherIdentity"
Cohesion: 0.22
Nodes (8): A teacher account as exposed by the API., The minimal identity used to onboard a teacher from a Telegram update., TeacherIdentity, TeacherRead, test_a_teacher_cannot_reach_another_teachers_class(), test_two_teachers_may_use_the_same_class_name(), test_reports_never_leak_another_teachers_data(), test_one_teacher_cannot_resolve_anothers_student()

### Community 48 - "telegram_webhook"
Cohesion: 0.33
Nodes (6): Any, Accept one update from Telegram and hand it to the bot application. Args:…, telegram_webhook(), Header, post, Request

### Community 52 - "Attendance Session Per Class Per Day"
Cohesion: 0.50
Nodes (4): Attendance Session Per Class Per Day, Buttons and Typing Share Implementation, Teacher-Class-Student-Attendance Data Model, Sessions Are Database State

### Community 53 - "Grill Me Skill"
Cohesion: 0.67
Nodes (3): Grill Me Agent UI, Grill Me Skill, Grilling Session

## Knowledge Gaps
- **11 isolated node(s):** `class-management`, `Fowler Smell Baseline`, `Fixed Point Diff Pinning`, `Code Review Agent UI`, `Grilling Session` (+6 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **12 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `AttendanceStatus` connect `AttendanceStatus` to `._finalise`, `ReportPeriod`, `AttendanceService`, `Student`, `AttendanceRepository`, `definitions.py`, `attendance_service.py`, `build_registry`, `test_reports.py`, `exceptions.py`, `test_tuition.py`, `test_attendance_flow.py`, `AttendanceSessionRead`?**
  _High betweenness centrality (0.085) - this node is a cross-community bridge._
- **Why does `AttendanceRepository` connect `AttendanceRepository` to `AttendanceStatus`, `AttendanceService`, `Student`, `attendance_service.py`, `StudentRepository`, `class_service.py`?**
  _High betweenness centrality (0.074) - this node is a cross-community bridge._
- **Why does `ServiceContainer` connect `class_service.py` to `AttendanceStatus`, `AttendanceService`, `AttendanceRepository`, `Settings`, `bot.py`, `conftest.py`, `Database`, `messages.py`, `StudentRepository`, `AttendanceSessionRead`?**
  _High betweenness centrality (0.055) - this node is a cross-community bridge._
- **Are the 37 inferred relationships involving `AttendanceStatus` (e.g. with `AttendanceRecord` and `AttendanceSession`) actually correct?**
  _`AttendanceStatus` has 37 INFERRED edges - model-reasoned connections that need verification._
- **Are the 61 inferred relationships involving `ToolOutput` (e.g. with `AttendanceEntry` and `AttendanceSessionRead`) actually correct?**
  _`ToolOutput` has 61 INFERRED edges - model-reasoned connections that need verification._
- **Are the 61 inferred relationships involving `ToolInput` (e.g. with `AttendanceEntry` and `AttendanceSessionRead`) actually correct?**
  _`ToolInput` has 61 INFERRED edges - model-reasoned connections that need verification._
- **Are the 39 inferred relationships involving `OperationResult` (e.g. with `AttendanceEntry` and `AttendanceSessionRead`) actually correct?**
  _`OperationResult` has 39 INFERRED edges - model-reasoned connections that need verification._