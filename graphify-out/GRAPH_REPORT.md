# Graph Report - class-management  (2026-08-25)

## Corpus Check
- 124 files · ~55,517 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1854 nodes · 4911 edges · 98 communities (87 shown, 11 thin omitted)
- Extraction: 88% EXTRACTED · 12% INFERRED · 0% AMBIGUOUS · INFERRED: 601 edges (avg confidence: 0.52)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `9eb2f526`
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
- 20260728_1615_add_daily_tuition_fee.py
- .get_by_telegram_id
- .format
- .sync_database_url
- format_vnd
- TeacherService
- validate_meaningful_name
- ._blank_strings_become_none
- _load_snapshot
- .display_label
- .get_by_telegram_id
- .tuition
- test_schedule.py
- validate_meaningful_name
- .add_extra
- _details
- _calendar
- PersistentLoop
- services
- rewrite_create_class_intent
- .mark_remaining
- .sync_database_url
- 20260825_0908_schedule_and_tuition_charges.py
- _pg_enum
- _pg_enum
- client
- .get_by_id
- _describe_validation_error
- .paid_through_per_student
- class-management
- .names
- .__init__
- ._drop_empty_details
- .__init__
- ActivityKind
- .__init__

## God Nodes (most connected - your core abstractions)
1. `AttendanceStatus` - 95 edges
2. `ToolOutput` - 85 edges
3. `ToolInput` - 80 edges
4. `OperationResult` - 56 edges
5. `Classroom` - 51 edges
6. `Settings` - 50 edges
7. `AttendanceRepository` - 49 edges
8. `Student` - 48 edges
9. `ServiceContainer` - 47 edges
10. `AttendanceService` - 45 edges

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

## Communities (98 total, 11 thin omitted)

### Community 0 - "attendance_service.py"
Cohesion: 0.06
Nodes (62): AttendanceHistoryEntry, AttendanceReportInput, AttendanceReportOutput, MonthlySummaryInput, MonthlySummaryOutput, Reporting tool contracts., Arguments for ``student_attendance_report``., A single dated status in a student's history. (+54 more)

### Community 1 - "AttendanceStatus"
Cohesion: 0.11
Nodes (34): build_application(), _on_startup(), _purge_conversations(), Application, DEFAULT_TYPE, Telegram application assembly.  Builds the ``python-telegram-bot`` application,, Publish the command menu and schedule conversation clean-up., Drop conversations that have been idle past their TTL. (+26 more)

### Community 2 - "tuition_service.py"
Cohesion: 0.10
Nodes (21): AssistantAgent, Runs the model's tool-calling loop for one conversation turn., Wire the agent to its dependencies.          Args:             client: Configure, build_groq_client(), get_groq_client(), GroqClient, Return the process-wide Groq client, creating it on first use., Thin async wrapper around the official Groq chat completions SDK. (+13 more)

### Community 3 - "AttendanceService"
Cohesion: 0.08
Nodes (14): datetime, Select, Set the amount on unpaid charges for a class to the current daily fee., Mark every unpaid charge for the student in this class as paid.          Returns, Create or refresh charges after a session is finished.          Completed (paid), Queries over billed attendance days., Every charge attached to one attendance session., Charges for students in one class, with student and session loaded. (+6 more)

### Community 4 - "Student"
Cohesion: 0.08
Nodes (26): AttendanceSessionClosedError, NoActiveAttendanceSessionError, No attendance session is currently open., The session is closed and can no longer be edited., AttendanceService, _count_statuses(), date, Record one student's status in the active session.          Raises: (+18 more)

### Community 5 - "AttendanceRepository"
Cohesion: 0.05
Nodes (27): AttendanceRepository, date, Select, Dates a class actually met, oldest first, ignoring cancelled days., Every ``(student_id, date, status)`` mark for a class, oldest first., Total number of attendance sessions ever held for a class., Date of the most recent session for a class, or ``None`` if none., Every session a teacher held on one day, with class preloaded. (+19 more)

### Community 6 - "ToolOutput"
Cohesion: 0.06
Nodes (40): AI layer: intent understanding and tool dispatch.  Nothing in this package touch, ConversationState, ConversationStore, InMemoryConversationStore, Any, Short-lived conversation state.  The assistant needs just enough memory to make, Create the store.          Args:             ttl_seconds: Idle lifetime of a con, How long a conversation survives without activity. (+32 more)

### Community 7 - "get_settings"
Cohesion: 0.13
Nodes (23): CallbackParseError, encode_mark(), encode_page(), encode_simple(), parse_attendance_callback(), ValueError, The callback payload did not match any known action., Encode a "set this student's status" button. (+15 more)

### Community 8 - "ToolRegistry"
Cohesion: 0.09
Nodes (39): attendance_today(), list_students(), Roster of one class, ordered by name., Today's roster plus today's session, when one exists., OperationResult, Generic acknowledgement for tools that only mutate state., Base class for arguments the language model supplies to a tool.      ``extra="fo, ToolInput (+31 more)

### Community 9 - "commands.py"
Cohesion: 0.09
Nodes (47): AttendanceRecord, AttendanceSession, Attendance ORM models., One roll-call for a class on a given calendar day.      At most one session may, Whether records may still be modified., The status of one student within one attendance session., Base, IdMixin (+39 more)

### Community 10 - "StudentService"
Cohesion: 0.13
Nodes (17): Recent-activity read models for the administrator home page., ClassRead, A class as presented to the teacher., AppModel, NamedEntity, BaseModel, Shared Pydantic base classes and reusable field types.  These types are the cont, Minimal identity of a record, used inside larger tool responses. (+9 more)

### Community 11 - "test_keyboards.py"
Cohesion: 0.11
Nodes (27): DateRange, StrEnum, Named date ranges the model can request without doing date arithmetic.      Lett, The concrete range a report was computed over., ReportPeriod, AttendanceMark, ClassAttendanceSinceOutput, ClassTeachingDaysRow (+19 more)

### Community 12 - "test_agent.py"
Cohesion: 0.15
Nodes (12): No student matched the reference the teacher used., StudentNotFoundError, Student enrolment, updates and reference resolution., Return every student plausibly referred to by ``reference``., Remove a student and their attendance history.          Raises:             Conf, Update a student's details, changing only the fields supplied.          Raises:, Find students matching a name fragment or ID.          Unlike :meth:`resolve`, s, Resolve an optional class name to an id, keeping ``None`` as-is. (+4 more)

### Community 13 - "test_tool_schema.py"
Cohesion: 0.18
Nodes (6): http_status_for(), Map a domain error onto an HTTP status code., parametrize, HTTP surface: health probes, the webhook receiver and error mapping., test_domain_errors_map_to_sensible_status_codes(), test_error_serialisation_is_safe_to_return()

### Community 14 - "test_reports.py"
Cohesion: 0.12
Nodes (27): _cell_text(), _header_mapping(), parse_roster_file(), Read a student roster out of an uploaded Excel or CSV file.  Teachers keep roste, Render a spreadsheet cell as text, keeping phone numbers intact., Map a raw table onto roster rows, skipping blanks and reporting gaps., Map column index to field name, or ``None`` when this is not a header., One student parsed out of the uploaded file. (+19 more)

### Community 15 - "conftest.py"
Cohesion: 0.17
Nodes (25): Arguments for ``start_attendance``., StartAttendanceInput, Arguments for ``tuition_report``.      Answers questions like "tuition for SE401, TuitionReportInput, Return the current local calendar date.      Args:         tz: Timezone to resol, today(), test_attendance_can_be_recorded_for_a_past_date(), test_get_session_for_date_does_not_return_another_day() (+17 more)

### Community 16 - "AppError"
Cohesion: 0.11
Nodes (40): _add_student(), _attendance_report(), _attendance_state(), build_registry(), _cancel_attendance(), _class_info(), _create_class(), _delete_class() (+32 more)

### Community 17 - "exceptions.py"
Cohesion: 0.13
Nodes (32): AssistantError, The assistant could not complete the turn., FakeResponse, make_agent(), Any, fixture, The agent's tool-calling loop, driven by a scripted model.  The Groq client is f, A model stuck in a tool loop must not spin forever. (+24 more)

### Community 18 - "definitions.py"
Cohesion: 0.13
Nodes (12): context(), crash(), echo(), EchoInput, EchoOutput, explode(), fixture, Tests for the tool registry — the validation boundary around the model. (+4 more)

### Community 19 - "test_registry.py"
Cohesion: 0.13
Nodes (27): find_matches(), normalize(), normalize_code(), Text normalisation and fuzzy-matching helpers.  Teachers refer to students the w, Remove diacritics so ``"Nguyễn"`` and ``"Nguyen"`` compare equal., Casefold, strip accents and collapse whitespace for comparison., Canonical form for identifiers such as student codes and class names., Return a 0..1 similarity ratio between two normalised strings. (+19 more)

### Community 20 - "messages.py"
Cohesion: 0.08
Nodes (25): AttendanceStatus, Icon used when rendering the status in Telegram., Human-readable label, e.g. ``"Late"``., Whether the status contributes to the attendance rate.          Late students we, How a student was accounted for in a single attendance session., Count records per status within a single session., AttendanceSummary, Counts of each status within a session or a date range. (+17 more)

### Community 21 - "test_text.py"
Cohesion: 0.12
Nodes (11): ClassRepository, Select, Queries scoped to a single teacher's classes.      Every method takes ``teacher_, Fetch one class by id, scoped to its owner., Fetch a class by its name, case-insensitively., Return every class owned by the teacher, alphabetically., Return each class paired with its student count.          Uses a single grouped, Fetch a class with its student collection eagerly loaded. (+3 more)

### Community 22 - "today"
Cohesion: 0.11
Nodes (13): Select, Queries scoped to the students inside a teacher's classes., Base query joining through ``classes`` to enforce ownership., Fetch one student by id, scoped to the owning teacher., Fetch a student together with their class., Fetch a student by their code within one class., Find every student with this code across all of a teacher's classes.          Co, Return the roster of a class ordered by name. (+5 more)

### Community 23 - "StudentRepository"
Cohesion: 0.09
Nodes (31): class_info(), Detailed settings for one class., ClassInfoInput, ClassInfoOutput, CreateClassInput, DeleteClassInput, Class read models and tool contracts., Arguments for ``get_class_info``. (+23 more)

### Community 24 - "test_attendance_flow.py"
Cohesion: 0.05
Nodes (48): ClassNotFoundError, The teacher has no class with the requested name., A weekly slot or extra session already exists for that class., ScheduleConflictError, ClassExtraSession, A one-off extra class on a specific calendar date., date, time (+40 more)

### Community 25 - "class_service.py"
Cohesion: 0.11
Nodes (25): Tool catalogue and the validation boundary around it., _clip_payload(), _decode_arguments(), _error(), Any, Tool registry: the only bridge between the language model and the backend.  The, Return a tool by name, or ``None`` when it is not registered., Render every tool as a function declaration dict. (+17 more)

### Community 26 - "ClassService"
Cohesion: 0.40
Nodes (5): current_timezone(), datetime, ZoneInfo, Date and time helpers.  Attendance is anchored to the teacher's local calendar d, The configured application timezone.

### Community 27 - "agent.py"
Cohesion: 0.24
Nodes (11): _clip_for_log(), _final_reply_text(), _message_from_last_tool(), Any, Handle one user message.          Args:             message: What the teacher ty, Call Groq, translating transport failures.          Raises:             Assistan, Render a value for logs without dumping unbounded model output., Compact success/error summary for the model's tool-call outcome. (+3 more)

### Community 28 - "test_api.py"
Cohesion: 0.14
Nodes (23): AttendanceSessionStatus, Lifecycle of an attendance session., AttendanceEntry, CancelAttendanceInput, FinishAttendanceOutput, GetAttendanceStateInput, GetAttendanceStateOutput, MarkRemainingInput (+15 more)

### Community 29 - "._owned"
Cohesion: 0.15
Nodes (20): build_tool_schema(), Build a JSON schema for a tool's input model.      Args:         model: The Pyda, _assert_llm(), Colour, Nested, BaseModel, StrEnum, Tests for the Pydantic to JSON-schema converter used by LLM tools. (+12 more)

### Community 30 - "formatting.py"
Cohesion: 0.12
Nodes (18): api Uvicorn Service, db PostgreSQL Service, migrate Alembic Service, postgres-data Volume, ai/ Agent Layer, Class Management Assistant, ConversationStore Protocol, Layered Architecture (+10 more)

### Community 31 - "ollama.py"
Cohesion: 0.14
Nodes (8): Fetch a row by primary key, or ``None`` when it does not exist., Persist a new instance and flush so its primary key is populated., Delete an instance and flush the change., Delete by primary key without loading the row.          Returns:             The, Return every row.  Intended for small reference tables and tests., Push pending changes to the database without committing., Reload an instance from the database., ModelT

### Community 32 - "student_service.py"
Cohesion: 0.11
Nodes (60): actions(), api, apiFetch(), apiUpload(), attendanceRate(), boot(), channelItem(), CLASS_CHANNELS (+52 more)

### Community 33 - "ai/tools/ Registry Validation Boundary"
Cohesion: 0.22
Nodes (13): _iter_json_objects(), new_call_id(), Ollama conversation adapter.  Translates between the internal history format sha, Pull tool-call JSON out of plain content when the model narrated it., Create a stable-enough identifier for a function call within one turn., Fix common local-model JSON mistakes before ``json.loads``., Yield top-level ``{...}`` slices, respecting string escaping., Return a normalised tool call when *blob* looks like one. (+5 more)

### Community 34 - "Settings"
Cohesion: 0.17
Nodes (14): Any, Send one chat completion request with optional tools.          Args:, history_to_messages(), model_supports_tool_calling(), Any, Groq conversation adapter.  Translates between the internal history format and t, Whether *model* can run the assistant's tool-calling loop., Convert stored history items into OpenAI-style chat messages.      Args: (+6 more)

### Community 35 - "ServiceContainer"
Cohesion: 0.15
Nodes (18): admin_context(), Shared FastAPI dependencies for the administrator API.  The web UI operates as a, Yield the service container and administrator for one request.      The surround, configure_logging(), Install the root log handler.      Safe to call more than once; existing handler, get_database(), Return the process-wide :class:`Database`, creating it on first use., create_app() (+10 more)

### Community 36 - "BaseRepository"
Cohesion: 0.05
Nodes (69): AdminContext, add_extra_class(), add_schedule_rule(), add_student(), attendance_session(), attendance_since_payment(), cancel_attendance(), chat() (+61 more)

### Community 37 - "callbacks.py"
Cohesion: 0.08
Nodes (21): A bot user who owns classes.      The teacher is the ownership root of the data, Preferred way to address the teacher in bot replies., Teacher, Data access for :class:`~app.models.teacher.Teacher`., Queries scoped to teacher accounts., Look up the teacher behind a Telegram user id.          Args:             telegr, TeacherRepository, Service composition root.  Wiring lives here rather than inside the services the (+13 more)

### Community 38 - "readiness"
Cohesion: 0.18
Nodes (13): liveness(), LivenessResponse, AsyncSession, BaseModel, get, Response, Reply to a liveness probe., Reply to a readiness probe. (+5 more)

### Community 40 - "env.py"
Cohesion: 0.19
Nodes (10): The assistant agent: one user message in, one reply out.  Implements the tool-ca, Groq client construction.  Uses the official ``groq`` Python SDK (``AsyncGroq``), Health and readiness endpoints., Telegram webhook endpoint.  Used when ``TELEGRAM_MODE=webhook``.  The route does, Centralised application configuration.  All runtime configuration is read from e, get_logger(), Logging configuration.  Provides a single :func:`configure_logging` entry point, Return a module-scoped logger.      Thin wrapper over :func:`logging.getLogger` (+2 more)

### Community 41 - "ConversationState"
Cohesion: 0.24
Nodes (12): history_to_messages(), Any, Convert stored history items into Ollama chat messages.      Args:         histo, Separate function calls from assistant text in an Ollama chat response.      Arg, split_response(), Tests for the Ollama conversation adapter., test_history_to_messages_includes_system_prompt_and_tool_round_trip(), test_split_response_falls_back_to_json_content() (+4 more)

### Community 42 - "validate_meaningful_name"
Cohesion: 0.20
Nodes (13): _apply(), _entry_name(), handle_attendance_callback(), DEFAULT_TYPE, Update, Inline-keyboard callback handlers.  Button presses bypass the language model ent, Name of a student inside a rendered session, for the toast message., Apply an attendance button press and redraw the board. (+5 more)

### Community 43 - "Code Review Skill"
Cohesion: 0.21
Nodes (13): parse_date(), Coerce a user- or model-supplied value into a :class:`~datetime.date`.      Acce, Tests for date parsing and range helpers., test_format_date_is_human_readable(), test_month_bounds_handle_december(), test_month_bounds_handle_february(), test_parse_iso_date(), test_parse_none_can_be_rejected() (+5 more)

### Community 44 - "services"
Cohesion: 0.32
Nodes (8): Code Review Agent UI, Code Review Skill, Fixed Point Diff Pinning, Parallel Sub-Agents Aggregation, Fowler Smell Baseline, Spec Review Axis, Standards Review Axis, Why Two Axes Separation

### Community 45 - ".names"
Cohesion: 0.11
Nodes (14): field_validator, ZoneInfo, Normalise for the official Groq SDK (root URL only).          The SDK appends ``, Blocking DSN, required by Alembic's migration runner., Resolved :class:`ZoneInfo` for :attr:`timezone`., Whether the process is running in the production environment., Strongly typed application settings.      Attributes are populated from environm, Normalise a PostgreSQL DSN to the asyncpg driver.          Deployment platforms (+6 more)

### Community 46 - "PermissionDeniedError"
Cohesion: 0.22
Nodes (10): do_run_migrations(), Alembic migration environment.  The engine is built from the application ``Setti, Emit SQL to stdout without connecting to a database., Run migrations on an already-established synchronous connection., Connect with the async driver and delegate to the sync runner., Entry point for online migrations., run_async_migrations(), run_migrations_offline() (+2 more)

### Community 47 - "get_session"
Cohesion: 0.20
Nodes (15): class_icon_data_uri(), class_initials(), icon_dir(), Class rail avatars: an uploaded image, or the first two characters of the name., Return the two-character label shown when a class has no image., Directory that stores uploaded class icons., Return a data URI for the class icon, if one has been uploaded., Replace any existing icon for this class with the uploaded file. (+7 more)

### Community 48 - "telegram_webhook"
Cohesion: 0.22
Nodes (5): datetime, ``(name, created_at, updated_at)`` for the newest-touched classes., ``(name, code, class_name, created_at, updated_at)`` for recent students., ``(class_name, status, opened_at, closed_at)`` for recent roll-calls., ``(student_name, class_name, days, amount_vnd, completed_at)`` per payment.

### Community 49 - ".__init__"
Cohesion: 0.40
Nodes (4): PermissionDeniedError, The caller does not own, and may not touch, the target resource., Enforce the optional allow-list from configuration., Return the teacher for a Telegram user, creating them on first use.          Pro

### Community 50 - "20260727_1445_initial_schema.py"
Cohesion: 0.20
Nodes (11): AmbiguousReferenceError, AmbiguousStudentError, AttendanceSessionNotFoundError, EmptyClassError, NotFoundError, Domain exception hierarchy.  Services raise these instead of leaking driver or O, The class exists but has no students enrolled., The reference matched more than one student. (+3 more)

### Community 51 - ".list_with_student_counts"
Cohesion: 0.12
Nodes (17): Any, post, Request, Accept one update from Telegram and hand it to the bot application.      Args:, telegram_webhook(), get_settings(), Return the process-wide settings singleton.      Cached so that ``.env`` parsing, Fall back to the process settings singleton when none was injected. (+9 more)

### Community 52 - "Attendance Session Per Class Per Day"
Cohesion: 0.25
Nodes (10): build_openai_tool_schema(), _inline_refs(), Any, BaseModel, Convert Pydantic models into JSON schemas for LLM function tools.  Providers val, Build a strict-mode JSON schema for legacy OpenAI tool definitions., Replace every ``$ref`` with a copy of the definition it points at., Prune to the allowed keyword subset and enforce object rules. (+2 more)

### Community 53 - "Grill Me Skill"
Cohesion: 0.22
Nodes (7): AppError, Any, Base class for every expected, user-recoverable domain failure., Create the error.          Args:             message: Teacher-safe explanation., Serialise the error for tool output or an HTTP error body., Return a developer-facing representation including the error code., Exception

### Community 55 - ".get_by_telegram_id"
Cohesion: 0.50
Nodes (4): Attendance Session Per Class Per Day, Buttons and Typing Share Implementation, Teacher-Class-Student-Attendance Data Model, Sessions Are Database State

### Community 56 - ".format"
Cohesion: 0.67
Nodes (3): Grill Me Agent UI, Grill Me Skill, Grilling Session

### Community 58 - ".sync_database_url"
Cohesion: 0.32
Nodes (4): field_validator, Reject names that carry no alphanumeric content.      Args:         value: The c, validate_meaningful_name(), field_validator

### Community 59 - "format_vnd"
Cohesion: 0.38
Nodes (5): FastAPI, HTTP translation of domain errors.  The API surface reuses the same exception hi, Install the application-wide exception handlers., register_exception_handlers(), HTTP API: health probes and the Telegram webhook receiver.

### Community 60 - "TeacherService"
Cohesion: 0.33
Nodes (6): handle_error(), _notify(), DEFAULT_TYPE, Global error handler.  Nothing that reaches here should ever be shown verbatim t, Log an unhandled exception and tell the teacher something useful., Best-effort reply to whoever triggered the failure.

### Community 61 - "validate_meaningful_name"
Cohesion: 0.12
Nodes (20): _close_board(), handle_message(), DEFAULT_TYPE, Update, Strip the buttons from a board whose session has ended., Route a plain-text message through the assistant., classroom(), _configure_environment() (+12 more)

### Community 63 - "_load_snapshot"
Cohesion: 0.14
Nodes (28): FinishAttendanceInput, Arguments for ``update_attendance``., Arguments for ``finish_attendance``., UpdateAttendanceInput, Finalise the active session, defaulting anyone still unmarked.          Raises:, The end-to-end attendance workflow., The inline-keyboard path and the conversational path must agree., start() (+20 more)

### Community 64 - ".display_label"
Cohesion: 0.10
Nodes (24): DuplicateStudentError, The student ID is already taken within the class., AddStudentInput, Arguments for ``search_student``., Arguments for ``add_student``., Arguments for ``update_student``.      Only the fields that are supplied are cha, SearchStudentInput, UpdateStudentInput (+16 more)

### Community 65 - ".get_by_telegram_id"
Cohesion: 0.22
Nodes (9): _first_non_empty(), _looks_like_add_student(), _parse_add_student_from_message(), Map a mis-chosen attendance mark onto ``add_student`` when enrolling.      Local, Heuristic: teacher wants to enrol a new student, not mark attendance., Best-effort scrape of enrolment fields from the teacher's message., rewrite_add_student_intent(), test_rewrite_add_student_intent_maps_attendance_tool() (+1 more)

### Community 66 - ".tuition"
Cohesion: 0.33
Nodes (6): AttendanceAlreadyTakenError, ClassAlreadyExistsError, ConflictError, The teacher already owns a class with that name., Attendance for that class and date is already complete., The request clashes with the current state of the data.

### Community 67 - "test_schedule.py"
Cohesion: 0.32
Nodes (6): get_web_runtime(), Long-lived collaborators shared by the web UI's HTTP handlers.  The FastAPI proc, Assistant collaborators shared by every web request., Build the runtime from application settings.          Args:             settings, Return the process-wide web runtime, creating it on first use., WebRuntime

### Community 68 - "validate_meaningful_name"
Cohesion: 0.33
Nodes (6): history(), date, fixture, Run one complete attendance session on ``day``., Three days of attendance: today and the two days before., record_day()

### Community 69 - ".add_extra"
Cohesion: 0.40
Nodes (4): JsonFormatter, Render log records as single-line JSON for log aggregators., Serialise a log record, merging in any ``extra`` fields., LogRecord

### Community 70 - "_details"
Cohesion: 0.50
Nodes (3): BaseModel, Add a tool to the catalogue.          Args:             name: Name the model wil, ToolHandler

### Community 71 - "_calendar"
Cohesion: 0.43
Nodes (6): Whether to ignore the model's words and show the tool result instead., _should_use_tool_message_instead(), Tests for post-tool reply selection., test_empty_reply_after_tools_should_use_tool_message(), test_normal_summary_is_kept(), test_refusal_phrases_are_detected()

### Community 73 - "services"
Cohesion: 0.09
Nodes (21): Database engine, session factory and connection lifecycle., Database, get_session(), Any, AsyncSession, Async database engine and session management.  The :class:`Database` object owns, Override the process-wide database.  Intended for tests only., FastAPI dependency yielding a transactional session. (+13 more)

### Community 74 - "rewrite_create_class_intent"
Cohesion: 0.33
Nodes (6): _looks_like_create_class(), Map a mis-chosen fee update onto ``create_class`` when the teacher asked to crea, Heuristic: teacher is asking to create/add a new class., rewrite_create_class_intent(), test_rewrite_create_class_intent_maps_fee_tool(), test_rewrite_does_not_map_add_tuition_fee_to_create_class()

### Community 76 - ".sync_database_url"
Cohesion: 0.10
Nodes (34): AgentReply, The outcome of a single user turn., AttendanceSessionRead, Full state of an attendance session., clip(), Trim a message to Telegram's maximum length., Render the live attendance message body.      The whole roster is listed regardl, render_attendance_session() (+26 more)

### Community 77 - "20260825_0908_schedule_and_tuition_charges.py"
Cohesion: 0.40
Nodes (4): downgrade(), Drop the ledger and schedule tables., Create schedule tables, the tuition ledger, and backfill unpaid charges., upgrade()

### Community 78 - "_pg_enum"
Cohesion: 0.67
Nodes (3): _pg_enum(), Enum, Build a database enum that stores the lower-case member *values*.      Without `

### Community 79 - "_pg_enum"
Cohesion: 0.67
Nodes (3): _pg_enum(), Enum, Store enum *values* (``not_yet``) rather than member names.

### Community 80 - "client"
Cohesion: 0.50
Nodes (4): AsyncClient, client(), fixture, An HTTP client bound to the app without running its lifespan.      Skipping the

### Community 81 - ".get_by_id"
Cohesion: 0.05
Nodes (43): ConfirmationRequiredError, A destructive action was requested without explicit confirmation.      Raised ra, ActivityEntry, One thing that happened, newest first in a feed., Result of updating a class tuition fee., One student's tuition over a date range., SetClassTuitionFeeOutput, StudentTuitionRow (+35 more)

### Community 84 - "_describe_validation_error"
Cohesion: 0.67
Nodes (3): _describe_validation_error(), Summarise a validation failure in language the model can act on., PydanticValidationError

### Community 94 - ".__init__"
Cohesion: 0.12
Nodes (28): ChatRequest, DescriptionRequest, ExtraSessionRequest, FinishRequest, MarkCompletedRequest, MarkRemainingRequest, MarkStatusRequest, BaseModel (+20 more)

### Community 95 - "ActivityKind"
Cohesion: 0.11
Nodes (15): ActivityKind, StrEnum, What kind of change an activity entry describes., Two- or three-letter marker shown next to the entry., Arguments for ``set_class_tuition_fee``., SetClassTuitionFeeInput, The recent-activity feed derived from audit timestamps., test_feed_reports_attendance_and_payments() (+7 more)

## Knowledge Gaps
- **19 isolated node(s):** `api`, `STATUSES`, `WEEKDAYS`, `MONTHS`, `PERIODS` (+14 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **11 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `AttendanceStatus` connect `messages.py` to `attendance_service.py`, `BaseRepository`, `AttendanceRepository`, `Student`, `get_settings`, `validate_meaningful_name`, `commands.py`, `validate_meaningful_name`, `test_keyboards.py`, `.sync_database_url`, `conftest.py`, `exceptions.py`, `test_api.py`, `.__init__`, `_load_snapshot`?**
  _High betweenness centrality (0.092) - this node is a cross-community bridge._
- **Why does `Settings` connect `.names` to `AttendanceStatus`, `tuition_service.py`, `ServiceContainer`, `test_schedule.py`, `.add_extra`, `readiness`, `callbacks.py`, `env.py`, `services`, `.sync_database_url`, `.list_with_student_counts`?**
  _High betweenness centrality (0.055) - this node is a cross-community bridge._
- **Why does `get_settings()` connect `.list_with_student_counts` to `AttendanceStatus`, `tuition_service.py`, `ServiceContainer`, `test_schedule.py`, `callbacks.py`, `readiness`, `ToolOutput`, `env.py`, `services`, `.names`, `PermissionDeniedError`, `test_tool_schema.py`, `exceptions.py`, `ClassService`?**
  _High betweenness centrality (0.050) - this node is a cross-community bridge._
- **Are the 48 inferred relationships involving `AttendanceStatus` (e.g. with `ChatRequest` and `DescriptionRequest`) actually correct?**
  _`AttendanceStatus` has 48 INFERRED edges - model-reasoned connections that need verification._
- **Are the 71 inferred relationships involving `ToolOutput` (e.g. with `ActivityEntry` and `ActivityKind`) actually correct?**
  _`ToolOutput` has 71 INFERRED edges - model-reasoned connections that need verification._
- **Are the 69 inferred relationships involving `ToolInput` (e.g. with `AttendanceEntry` and `AttendanceSessionRead`) actually correct?**
  _`ToolInput` has 69 INFERRED edges - model-reasoned connections that need verification._
- **Are the 42 inferred relationships involving `OperationResult` (e.g. with `AttendanceEntry` and `AttendanceSessionRead`) actually correct?**
  _`OperationResult` has 42 INFERRED edges - model-reasoned connections that need verification._