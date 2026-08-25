# Graph Report - class-management  (2026-08-25)

## Corpus Check
- 142 files · ~64,263 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 2087 nodes · 5745 edges · 92 communities (84 shown, 8 thin omitted)
- Extraction: 89% EXTRACTED · 11% INFERRED · 0% AMBIGUOUS · INFERRED: 619 edges (avg confidence: 0.52)
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
- .get_by_id
- class-management
- .__init__
- ActivityKind
- .__init__

## God Nodes (most connected - your core abstractions)
1. `AttendanceStatus` - 99 edges
2. `ToolOutput` - 85 edges
3. `ToolInput` - 80 edges
4. `ServiceContainer` - 66 edges
5. `OperationResult` - 56 edges
6. `Settings` - 54 edges
7. `call()` - 53 edges
8. `today()` - 53 edges
9. `Classroom` - 51 edges
10. `get_settings()` - 49 edges

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

## Communities (92 total, 8 thin omitted)

### Community 0 - "attendance_service.py"
Cohesion: 0.07
Nodes (55): AttendanceSessionStatus, AttendanceStatus, StrEnum, Icon used when rendering the status in Telegram., Human-readable label, e.g. ``"Late"``., Whether the status contributes to the attendance rate.          Late students we, Lifecycle of an attendance session., How a student was accounted for in a single attendance session. (+47 more)

### Community 1 - "AttendanceStatus"
Cohesion: 0.06
Nodes (66): build_application(), _on_startup(), _purge_conversations(), Application, DEFAULT_TYPE, Telegram application assembly.  Builds the ``python-telegram-bot`` application,, Publish the command menu and schedule conversation clean-up., Drop conversations that have been idle past their TTL. (+58 more)

### Community 2 - "tuition_service.py"
Cohesion: 0.04
Nodes (54): AssistantAgent, The assistant agent: one user message in, one reply out.  Implements the tool-ca, Runs the model's tool-calling loop for one conversation turn., Wire the agent to its dependencies.          Args:             client: Configure, build_groq_client(), get_groq_client(), GroqClient, Groq client construction.  Uses the official ``groq`` Python SDK (``AsyncGroq``) (+46 more)

### Community 3 - "AttendanceService"
Cohesion: 0.08
Nodes (15): date, datetime, Select, Set the amount on unpaid charges for a class to the current daily fee., Mark every unpaid charge for the student in this class as paid.          Returns, Create or refresh charges after a session is finished.          Completed (paid), Queries over billed attendance days., Every charge attached to one attendance session. (+7 more)

### Community 4 - "Student"
Cohesion: 0.07
Nodes (32): AttendanceSessionClosedError, EmptyClassError, NoActiveAttendanceSessionError, The class exists but has no students enrolled., No attendance session is currently open., The session is closed and can no longer be edited., AttendanceService, _count_statuses() (+24 more)

### Community 5 - "AttendanceRepository"
Cohesion: 0.05
Nodes (27): AttendanceRepository, date, Select, Dates a class actually met, oldest first, ignoring cancelled days., Every ``(student_id, date, status)`` mark for a class, oldest first., Total number of attendance sessions ever held for a class., Date of the most recent session for a class, or ``None`` if none., Every session a teacher held on one day, with class preloaded. (+19 more)

### Community 6 - "ToolOutput"
Cohesion: 0.15
Nodes (16): InMemoryConversationStore, Create the store.          Args:             ttl_seconds: Idle lifetime of a con, How long a conversation survives without activity., Forget a conversation entirely., Process-local conversation store with time-based expiry.      Suitable for a sin, Current instant as a timezone-aware UTC datetime., utc_now(), Tests for conversation memory and its expiry rules. (+8 more)

### Community 7 - "get_settings"
Cohesion: 0.06
Nodes (65): Enumerations shared by the ORM models, schemas and AI tool contracts., AttendanceEntry, AttendanceSessionRead, One student's state inside an attendance session., Full state of an attendance session., clip(), escape_html(), Rendering helpers for Telegram messages.  Two parse modes are used deliberately: (+57 more)

### Community 8 - "ToolRegistry"
Cohesion: 0.11
Nodes (25): CancelAttendanceInput, Arguments for ``cancel_attendance``., OperationResult, Generic acknowledgement for tools that only mutate state., ImportStudentRow, ImportStudentsInput, ImportStudentsOutput, ListStudentsInput (+17 more)

### Community 9 - "commands.py"
Cohesion: 0.09
Nodes (45): AttendanceRecord, AttendanceSession, Attendance ORM models., One roll-call for a class on a given calendar day.      At most one session may, Whether records may still be modified., The status of one student within one attendance session., Base, IdMixin (+37 more)

### Community 10 - "StudentService"
Cohesion: 0.07
Nodes (38): ActivityEntry, Recent-activity read models for the administrator home page., One thing that happened, newest first in a feed., Schedule read models used by the administrator dashboard., One calendar cell entry generated from a weekly rule or an extra session., ScheduleOccurrence, _calendar(), _create_class() (+30 more)

### Community 11 - "test_keyboards.py"
Cohesion: 0.06
Nodes (52): Base class for values a tool returns to the language model., ToolOutput, DateRange, StrEnum, Named date ranges the model can request without doing date arithmetic.      Lett, The concrete range a report was computed over., ReportPeriod, AttendanceMark (+44 more)

### Community 12 - "test_agent.py"
Cohesion: 0.13
Nodes (12): Return every student plausibly referred to by ``reference``., Enrol a new student into a class.          Raises:             ClassNotFoundErro, Enrol a whole roster, skipping rows that clash instead of failing.          A sp, Remove a student and their attendance history.          Raises:             Conf, Update a student's details, changing only the fields supplied.          Raises:, List the roster of one class., Find students matching a name fragment or ID.          Unlike :meth:`resolve`, s, Resolve an optional class name to an id, keeping ``None`` as-is. (+4 more)

### Community 13 - "test_tool_schema.py"
Cohesion: 0.13
Nodes (10): http_status_for(), Map a domain error onto an HTTP status code., AsyncClient, client(), fixture, parametrize, HTTP surface: health probes, the webhook receiver and error mapping., An HTTP client bound to the app without running its lifespan.      Skipping the (+2 more)

### Community 14 - "test_reports.py"
Cohesion: 0.12
Nodes (27): _cell_text(), _header_mapping(), parse_roster_file(), Read a student roster out of an uploaded Excel or CSV file.  Teachers keep roste, Render a spreadsheet cell as text, keeping phone numbers intact., Map a raw table onto roster rows, skipping blanks and reporting gaps., Map column index to field name, or ``None`` when this is not a header., One student parsed out of the uploaded file. (+19 more)

### Community 15 - "conftest.py"
Cohesion: 0.07
Nodes (57): FinishAttendanceInput, Arguments for ``finish_attendance``., Arguments for ``start_attendance``., StartAttendanceInput, Turn a named period into a concrete inclusive date range.      Keeping this in o, resolve_period(), format_date(), month_bounds() (+49 more)

### Community 16 - "AppError"
Cohesion: 0.09
Nodes (48): _add_student(), _attendance_report(), _attendance_state(), build_registry(), _cancel_attendance(), _class_info(), _create_class(), _delete_class() (+40 more)

### Community 17 - "exceptions.py"
Cohesion: 0.13
Nodes (32): AssistantError, The assistant could not complete the turn., FakeResponse, make_agent(), Any, fixture, The agent's tool-calling loop, driven by a scripted model.  The Groq client is f, A model stuck in a tool loop must not spin forever. (+24 more)

### Community 18 - "definitions.py"
Cohesion: 0.13
Nodes (12): context(), crash(), echo(), EchoInput, EchoOutput, explode(), fixture, Tests for the tool registry — the validation boundary around the model. (+4 more)

### Community 19 - "test_registry.py"
Cohesion: 0.13
Nodes (25): find_matches(), normalize(), T, Text normalisation and fuzzy-matching helpers.  Teachers refer to students the w, Remove diacritics so ``"Nguyễn"`` and ``"Nguyen"`` compare equal., Casefold, strip accents and collapse whitespace for comparison., Return a 0..1 similarity ratio between two normalised strings., Rank ``candidates`` against ``query`` using a tiered matching strategy.      Tie (+17 more)

### Community 20 - "messages.py"
Cohesion: 0.50
Nodes (4): identity_from(), Open a unit of work and resolve the teacher behind an update.          Everythin, Project a Telegram user onto the identity the service layer expects., TelegramUser

### Community 21 - "test_text.py"
Cohesion: 0.14
Nodes (10): ClassRepository, Select, Queries scoped to a single teacher's classes.      Every method takes ``teacher_, Fetch one class by id, scoped to its owner., Fetch a class by its name, case-insensitively., Return every class owned by the teacher, alphabetically., Return each class paired with its student count.          Uses a single grouped, Fetch a class with its student collection eagerly loaded. (+2 more)

### Community 22 - "today"
Cohesion: 0.13
Nodes (11): Select, Queries scoped to the students inside a teacher's classes., Base query joining through ``classes`` to enforce ownership., Fetch one student by id, scoped to the owning teacher., Fetch a student together with their class., Fetch a student by their code within one class., Find every student with this code across all of a teacher's classes.          Co, Return the roster of a class ordered by name. (+3 more)

### Community 23 - "StudentRepository"
Cohesion: 0.09
Nodes (28): ClassInfoInput, CreateClassInput, DeleteClassInput, field_validator, Class read models and tool contracts., Arguments for ``get_class_info``., Arguments for ``create_class``., Arguments for ``rename_class``. (+20 more)

### Community 24 - "test_attendance_flow.py"
Cohesion: 0.07
Nodes (32): A weekly slot or extra session already exists for that class., ScheduleConflictError, AppModel, BaseModel, Base model with the conventions used across the application., ExtraSessionRead, A repeating weekday slot., A one-off extra class. (+24 more)

### Community 25 - "class_service.py"
Cohesion: 0.06
Nodes (39): _clip_payload(), _decode_arguments(), _describe_validation_error(), _error(), Any, BaseModel, Tool registry: the only bridge between the language model and the backend.  The, Add a tool to the catalogue.          Args:             name: Name the model wil (+31 more)

### Community 26 - "ClassService"
Cohesion: 0.22
Nodes (8): build_system_prompt(), System prompt construction.  The prompt is assembled per turn so the model alway, Assemble the system prompt for one turn.      Args:         state: The live conv, current_timezone(), datetime, ZoneInfo, Date and time helpers.  Attendance is anchored to the teacher's local calendar d, The configured application timezone.

### Community 27 - "agent.py"
Cohesion: 0.24
Nodes (11): _clip_for_log(), _final_reply_text(), _message_from_last_tool(), Any, Handle one user message.          Args:             message: What the teacher ty, Call Groq, translating transport failures.          Raises:             Assistan, Render a value for logs without dumping unbounded model output., Compact success/error summary for the model's tool-call outcome. (+3 more)

### Community 28 - "test_api.py"
Cohesion: 0.09
Nodes (37): ClassRead, A class as presented to the teacher., _list_classes(), main(), Streamlit application shell: Discord-style class workspace., Configure the page and open the administrator workspace., bootstrap_admin(), current_channel() (+29 more)

### Community 29 - "._owned"
Cohesion: 0.11
Nodes (30): build_openai_tool_schema(), build_tool_schema(), _inline_refs(), Any, BaseModel, Convert Pydantic models into JSON schemas for LLM function tools.  Providers val, Build a JSON schema for a tool's input model.      Args:         model: The Pyda, Build a strict-mode JSON schema for legacy OpenAI tool definitions. (+22 more)

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
Cohesion: 0.13
Nodes (14): get_loop(), PersistentLoop, T, One asyncio loop on a daemon thread, for the life of the process.      ``asyncio, Start the background loop and wait until it is ready., Run ``loop.run_forever`` on this worker thread., Schedule ``coro`` on the background loop and wait for the result., Return the process-wide Streamlit loop, creating it on first use. (+6 more)

### Community 36 - "BaseRepository"
Cohesion: 0.09
Nodes (33): AdminContext, add_extra_class(), add_schedule_rule(), add_student(), cancel_attendance(), create_class(), delete_class(), finish_attendance() (+25 more)

### Community 37 - "callbacks.py"
Cohesion: 0.06
Nodes (48): admin_context(), Shared FastAPI dependencies for the administrator API.  The web UI operates as a, Yield the service container and administrator for one request.      The surround, A bot user who owns classes.      The teacher is the ownership root of the data, Preferred way to address the teacher in bot replies., Teacher, Look up the teacher behind a Telegram user id.          Args:             telegr, Return the teacher the Streamlit dashboard should operate as.          Prefers t (+40 more)

### Community 38 - "readiness"
Cohesion: 0.18
Nodes (13): liveness(), LivenessResponse, AsyncSession, BaseModel, get, Response, Reply to a liveness probe., Reply to a readiness probe. (+5 more)

### Community 40 - "env.py"
Cohesion: 0.10
Nodes (29): _maybe_show_board(), Natural-language chat page backed by the Groq LLM API.  The page itself contains, If an attendance session is in focus, show the tap-to-mark board., Chat with the Groq-hosted language model, using the app's tool catalogue., Send one user message, store the reply, and rerun., One user message through the agent, inside a single database transaction., render_chat_page(), _run_turn() (+21 more)

### Community 41 - "ConversationState"
Cohesion: 0.24
Nodes (12): history_to_messages(), Any, Convert stored history items into Ollama chat messages.      Args:         histo, Separate function calls from assistant text in an Ollama chat response.      Arg, split_response(), Tests for the Ollama conversation adapter., test_history_to_messages_includes_system_prompt_and_tool_round_trip(), test_split_response_falls_back_to_json_content() (+4 more)

### Community 42 - "validate_meaningful_name"
Cohesion: 0.12
Nodes (22): attendance_session(), attendance_since_payment(), class_info(), dashboard_summary(), list_classes(), get, JSON API backing the HTML/CSS/JS administrator dashboard.  Every route is a thin, Every class the administrator owns, with icon availability. (+14 more)

### Community 43 - "Code Review Skill"
Cohesion: 0.15
Nodes (19): _open_today(), Start or resume today's session for the focused class., _create_form(), _details(), _manage_form(), Class CRUD page.  Every action is a thin call into ClassService., Rename, set fee, or delete a selected class., Class info for one named class. (+11 more)

### Community 44 - "services"
Cohesion: 0.32
Nodes (8): Code Review Agent UI, Code Review Skill, Fixed Point Diff Pinning, Parallel Sub-Agents Aggregation, Fowler Smell Baseline, Spec Review Axis, Standards Review Axis, Why Two Axes Separation

### Community 45 - ".names"
Cohesion: 0.10
Nodes (15): field_validator, ZoneInfo, Normalise for the official Groq SDK (root URL only).          The SDK appends ``, Blocking DSN, required by Alembic's migration runner., Resolved :class:`ZoneInfo` for :attr:`timezone`., Whether the process is running in the production environment., Strongly typed application settings.      Attributes are populated from environm, Normalise a PostgreSQL DSN to the asyncpg driver.          Deployment platforms (+7 more)

### Community 46 - "PermissionDeniedError"
Cohesion: 0.22
Nodes (10): do_run_migrations(), Alembic migration environment.  The engine is built from the application ``Setti, Emit SQL to stdout without connecting to a database., Run migrations on an already-established synchronous connection., Connect with the async driver and delegate to the sync runner., Entry point for online migrations., run_async_migrations(), run_migrations_offline() (+2 more)

### Community 47 - "get_session"
Cohesion: 0.17
Nodes (16): get_class_icon(), Response, Serve the uploaded rail icon for a class, or 404 when there is none., class_icon_data_uri(), icon_dir(), Class rail avatars: an uploaded image, or the first two characters of the name., Directory that stores uploaded class icons., Return a data URI for the class icon, if one has been uploaded. (+8 more)

### Community 48 - "telegram_webhook"
Cohesion: 0.19
Nodes (8): ActivityRepository, datetime, Read-only queries that feed the recent-activity list., ``(name, created_at, updated_at)`` for the newest-touched classes., ``(name, code, class_name, created_at, updated_at)`` for recent students., ``(class_name, status, opened_at, closed_at)`` for recent roll-calls., ``(student_name, class_name, days, amount_vnd, completed_at)`` per payment., Wire the service to its data source.

### Community 49 - ".__init__"
Cohesion: 0.16
Nodes (11): PermissionDeniedError, The caller does not own, and may not touch, the target resource., Queries scoped to teacher accounts., TeacherRepository, Data access for teacher accounts., Onboarding and authorisation of Telegram users., Enforce the optional allow-list from configuration., Ownership boundary for teacher accounts.      Telegram onboarding still goes thr (+3 more)

### Community 50 - "20260727_1445_initial_schema.py"
Cohesion: 0.33
Nodes (6): Any, post, Request, Accept one update from Telegram and hand it to the bot application.      Args:, telegram_webhook(), Header

### Community 51 - ".list_with_student_counts"
Cohesion: 0.36
Nodes (7): _db_host_port(), main(), Wait for Docker DNS + PostgreSQL, then exec Alembic.  The migrate service can st, Block until *host* resolves or *timeout* seconds elapse., Block until PostgreSQL accepts a connection., wait_for_database(), wait_for_dns()

### Community 52 - "Attendance Session Per Class Per Day"
Cohesion: 0.18
Nodes (16): AttendanceReportInput, Arguments for ``list_students_by_status``.      Answers "who was absent today?", Arguments for ``attendance_report``.      Covers "attendance for SE401", "attend, StudentsByStatusInput, Reporting behaviour, including period resolution., test_a_multi_day_report_aggregates_every_session(), test_a_report_over_a_quiet_period_is_empty_not_an_error(), test_a_report_without_a_class_covers_every_class() (+8 more)

### Community 53 - "Grill Me Skill"
Cohesion: 0.16
Nodes (9): ConversationState, Any, Persist a conversation and refresh its expiry., Return the live conversation for a chat, creating one if needed., Everything remembered between two messages in one chat., Mark the conversation as active right now., Append items and trim the history to the most recent ``limit``.          Trimmin, Forget the attendance session, e.g. after it has been finalised. (+1 more)

### Community 55 - ".get_by_telegram_id"
Cohesion: 0.50
Nodes (4): Attendance Session Per Class Per Day, Buttons and Typing Share Implementation, Teacher-Class-Student-Attendance Data Model, Sessions Are Database State

### Community 56 - ".format"
Cohesion: 0.67
Nodes (3): Grill Me Agent UI, Grill Me Skill, Grilling Session

### Community 60 - "TeacherService"
Cohesion: 0.17
Nodes (8): AI layer: intent understanding and tool dispatch.  Nothing in this package touch, ConversationStore, Short-lived conversation state.  The assistant needs just enough memory to make, Storage for :class:`ConversationState`, keyed by chat id., Return the live state for a chat, or ``None`` if absent or expired., Persist a conversation, refreshing its expiry., Forget a conversation entirely., Protocol

### Community 61 - "validate_meaningful_name"
Cohesion: 0.21
Nodes (11): classroom(), _configure_environment(), AsyncSession, fixture, Shared pytest fixtures.  Integration tests run against a real (SQLite) database, A class named ``SE401`` owned by :func:`teacher`., Three students enrolled in :func:`classroom`., Pin configuration for the whole test session.      Environment variables win ove (+3 more)

### Community 62 - "._blank_strings_become_none"
Cohesion: 0.25
Nodes (8): attendance_today(), list_students(), Roster of one class, ordered by name., Find students by a fragment of name or ID., Today's roster plus today's session, when one exists., search_students(), A student as presented to the teacher., StudentRead

### Community 63 - "_load_snapshot"
Cohesion: 0.14
Nodes (29): GetAttendanceStateInput, MarkRemainingInput, Arguments for ``update_attendance``., Arguments for ``mark_remaining_students``., Arguments for ``get_attendance_state``., UpdateAttendanceInput, The end-to-end attendance workflow., The inline-keyboard path and the conversational path must agree. (+21 more)

### Community 64 - ".display_label"
Cohesion: 0.11
Nodes (22): AddStudentInput, Arguments for ``search_student``., Arguments for ``add_student``., Arguments for ``update_student``.      Only the fields that are supplied are cha, SearchStudentInput, UpdateStudentInput, Student management and reference resolution against a real database., The same person's name in two classes is only ambiguous across both. (+14 more)

### Community 65 - ".get_by_telegram_id"
Cohesion: 0.22
Nodes (9): _first_non_empty(), _looks_like_add_student(), _parse_add_student_from_message(), Map a mis-chosen attendance mark onto ``add_student`` when enrolling.      Local, Heuristic: teacher wants to enrol a new student, not mark attendance., Best-effort scrape of enrolment fields from the teacher's message., rewrite_add_student_intent(), test_rewrite_add_student_intent_maps_attendance_tool() (+1 more)

### Community 66 - ".tuition"
Cohesion: 0.08
Nodes (15): date, time, Persist a one-off session., Remove a one-off session., Queries for repeating slots.  Extra sessions use the same session., Return active and inactive weekly slots for one class, weekday order., Every active weekly slot owned by the teacher., Fetch one weekly slot belonging to a class. (+7 more)

### Community 67 - "test_schedule.py"
Cohesion: 0.25
Nodes (8): chat(), chat_board(), get_me(), Identity of the administrator plus assistant availability., Send one message to the assistant and return its reply., The attendance session currently in the assistant's focus, if any., get_web_runtime(), Return the process-wide web runtime, creating it on first use.

### Community 68 - "validate_meaningful_name"
Cohesion: 0.33
Nodes (3): Return the live state for a chat, dropping it if it has expired., Drop every expired conversation.          Returns:             How many conversa, Whether the conversation has been idle for longer than ``ttl``.

### Community 69 - ".add_extra"
Cohesion: 0.40
Nodes (5): import_roster(), Request, Replace a class's rail icon with the uploaded image bytes., Parse an uploaded roster file and enrol its students., upload_class_icon()

### Community 70 - "_details"
Cohesion: 0.13
Nodes (26): _add_extra_class(), _add_weekly_slot(), _class_info(), _details(), _edit_class(), _mark_completed(), dialog, Class info channel: details, timetable, extra sessions and tuition status. (+18 more)

### Community 71 - "_calendar"
Cohesion: 0.43
Nodes (6): Whether to ignore the model's words and show the tool result instead., _should_use_tool_message_instead(), Tests for post-tool reply selection., test_empty_reply_after_tools_should_use_tool_message(), test_normal_summary_is_kept(), test_refusal_phrases_are_detected()

### Community 73 - "services"
Cohesion: 0.05
Nodes (50): FastAPI, HTTP translation of domain errors.  The API surface reuses the same exception hi, Install the application-wide exception handlers., register_exception_handlers(), HTTP API: health probes and the Telegram webhook receiver., Health and readiness endpoints., Telegram webhook endpoint.  Used when ``TELEGRAM_MODE=webhook``.  The route does, configure_logging() (+42 more)

### Community 74 - "rewrite_create_class_intent"
Cohesion: 0.33
Nodes (6): _looks_like_create_class(), Map a mis-chosen fee update onto ``create_class`` when the teacher asked to crea, Heuristic: teacher is asking to create/add a new class., rewrite_create_class_intent(), test_rewrite_create_class_intent_maps_fee_tool(), test_rewrite_does_not_map_add_tuition_fee_to_create_class()

### Community 76 - ".sync_database_url"
Cohesion: 0.33
Nodes (6): AgentReply, The outcome of a single user turn., Load a session for rendering, tolerating one that has gone away., Decide whether the attendance board needs drawing or refreshing.      Runs insid, _resolve_board(), _safe_session_view()

### Community 77 - "20260825_0908_schedule_and_tuition_charges.py"
Cohesion: 0.40
Nodes (4): downgrade(), Drop the ledger and schedule tables., Create schedule tables, the tuition ledger, and backfill unpaid charges., upgrade()

### Community 78 - "_pg_enum"
Cohesion: 0.67
Nodes (3): _pg_enum(), Enum, Build a database enum that stores the lower-case member *values*.      Without `

### Community 79 - "_pg_enum"
Cohesion: 0.67
Nodes (3): _pg_enum(), Enum, Store enum *values* (``not_yet``) rather than member names.

### Community 81 - ".get_by_id"
Cohesion: 0.04
Nodes (63): AmbiguousReferenceError, AmbiguousStudentError, AttendanceAlreadyTakenError, AttendanceSessionNotFoundError, ClassAlreadyExistsError, ClassNotFoundError, ConfirmationRequiredError, ConflictError (+55 more)

### Community 94 - ".__init__"
Cohesion: 0.10
Nodes (35): ChatRequest, DescriptionRequest, ExtraSessionRequest, FinishRequest, MarkCompletedRequest, MarkRemainingRequest, MarkStatusRequest, BaseModel (+27 more)

### Community 95 - "ActivityKind"
Cohesion: 0.40
Nodes (4): ActivityKind, StrEnum, What kind of change an activity entry describes., Two- or three-letter marker shown next to the entry.

## Knowledge Gaps
- **19 isolated node(s):** `api`, `STATUSES`, `WEEKDAYS`, `MONTHS`, `PERIODS` (+14 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **8 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `ServiceContainer` connect `tuition_service.py` to `attendance_service.py`, `AttendanceStatus`, `AttendanceService`, `Student`, `AttendanceRepository`, `get_settings`, `StudentService`, `messages.py`, `test_text.py`, `today`, `test_attendance_flow.py`, `test_api.py`, `ServiceContainer`, `callbacks.py`, `env.py`, `Code Review Skill`, `.names`, `telegram_webhook`, `.__init__`, `validate_meaningful_name`, `.tuition`, `_details`, `.sync_database_url`, `.get_by_id`?**
  _High betweenness centrality (0.074) - this node is a cross-community bridge._
- **Why does `AttendanceStatus` connect `attendance_service.py` to `Student`, `AttendanceRepository`, `get_settings`, `ToolRegistry`, `commands.py`, `validate_meaningful_name`, `test_keyboards.py`, `StudentService`, `env.py`, `conftest.py`, `.get_by_id`, `exceptions.py`, `Attendance Session Per Class Per Day`, `.__init__`, `_load_snapshot`?**
  _High betweenness centrality (0.068) - this node is a cross-community bridge._
- **Why does `Settings` connect `.names` to `AttendanceStatus`, `tuition_service.py`, `ServiceContainer`, `readiness`, `services`, `.sync_database_url`, `.get_by_id`, `.__init__`, `validate_meaningful_name`?**
  _High betweenness centrality (0.057) - this node is a cross-community bridge._
- **Are the 48 inferred relationships involving `AttendanceStatus` (e.g. with `ChatRequest` and `DescriptionRequest`) actually correct?**
  _`AttendanceStatus` has 48 INFERRED edges - model-reasoned connections that need verification._
- **Are the 71 inferred relationships involving `ToolOutput` (e.g. with `ActivityEntry` and `ActivityKind`) actually correct?**
  _`ToolOutput` has 71 INFERRED edges - model-reasoned connections that need verification._
- **Are the 69 inferred relationships involving `ToolInput` (e.g. with `AttendanceEntry` and `AttendanceSessionRead`) actually correct?**
  _`ToolInput` has 69 INFERRED edges - model-reasoned connections that need verification._
- **Are the 19 inferred relationships involving `ServiceContainer` (e.g. with `Settings` and `ActivityRepository`) actually correct?**
  _`ServiceContainer` has 19 INFERRED edges - model-reasoned connections that need verification._