# Class Management Assistant

An AI-powered Telegram bot that lets teachers run their classes by talking
normally, instead of navigating menus:

```
Teacher   Create class SE401
Bot       Class SE401 created.

Teacher   Add Nguyen Van A (SE001) to SE401
Bot       Added Nguyen Van A (SE001) to SE401.

Teacher   Take attendance for SE401
Bot       Here's SE401 — tap to mark.
          [⬜ Alice Nguyen] [✅] [❌] [🟡]
          [⬜ John Smith  ] [✅] [❌] [🟡]
          ...

Teacher   John absent
Bot       John Smith marked absent. 1 student still unmarked.

Teacher   Done
Bot       Attendance saved — 2 present, 1 absent. Attendance rate: 67%.
```

---

## Contents

- [Architecture](#architecture)
- [Quick start](#quick-start)
- [Configuration](#configuration)
- [What the assistant can do](#what-the-assistant-can-do)
- [Project layout](#project-layout)
- [Design decisions](#design-decisions)
- [Development](#development)
- [Deployment](#deployment)
- [Extending the system](#extending-the-system)

---

## Architecture

The central rule is that **the language model never touches the database**. Its
entire capability surface is a catalogue of typed tools; every one of those
tools is a thin wrapper over a service, and the service does the validating,
the authorising and the writing.

```
        Telegram            Browser (HTML/CSS/JS)
           │                     │  fetch() → JSON
           ▼                     ▼
   ┌───────────────────┐  ┌─────────────────┐
   │ telegram/         │  │ api/ + web/     │  transport only
   └─────────┬─────────┘  └────────┬────────┘
             │                     │
     ┌───────┴────────┐            │  buttons and forms skip the model
     ▼                │            │
┌─────────┐           │            │
│  ai/    │           │            │
│  agent  │           │            │
└────┬────┘           │            │
     │ tool call      │            │
     ▼                ▼            ▼
┌──────────────────┐
│ ai/tools/registry│  ← validation boundary (Pydantic, ownership, errors)
└────┬─────────────┘
     │
     ▼
┌────────────────────────┐
│ services/              │  all business rules live here
└──────────┬─────────────┘
           ▼
┌────────────────────────┐
│ repositories/          │  the only place that builds SQL
└──────────┬─────────────┘
           ▼
      PostgreSQL
```

**What each layer may do**

| Layer | Responsibility | Explicitly not allowed to |
| --- | --- | --- |
| `telegram/` | Route updates, render messages, build keyboards | Contain business rules |
| `api/` + `web/` | Expose services as JSON, serve the HTML/CSS/JS dashboard | Contain business rules |
| `ai/` | Understand intent, choose tools, phrase replies | Touch the database or decide policy |
| `ai/tools/` | Validate arguments, dispatch, serialise errors | Implement behaviour |
| `services/` | Business rules, validation, authorisation | Build SQL, know about Telegram |
| `repositories/` | Queries and aggregation | Contain business rules |
| `models/` | Schema and relationships | Contain behaviour beyond projections |

Because the tools are only wrappers, every capability is reachable without a
model at all — which is exactly how the test suite drives them.

---

## Quick start

### With Docker (recommended)

```bash
cp .env.example .env
# Fill in TELEGRAM_BOT_TOKEN (from @BotFather) and GROQ_API_KEY (from GroqCloud).

docker compose up --build
```

This starts PostgreSQL, applies migrations, and runs the API, the bot in
polling mode, and the web dashboard — all in one process on port 8000. Open
http://localhost:8000, or message the Telegram bot and send `/start`.

### Locally with Pipenv

```bash
pipenv install --dev
cp .env.example .env          # fill in your tokens

docker compose up -d db       # or point DATABASE_URL at your own PostgreSQL
pipenv run alembic upgrade head
pipenv run uvicorn app.main:app --reload
```

The bot starts alongside the API, and the same process serves the dashboard at
`/`. Health checks live at `/health/live` and `/health/ready`; API docs at
`/docs` outside production.

### Web dashboard

A Discord-style administrator dashboard built with plain HTML, CSS and
JavaScript (no build step), served by FastAPI from `app/web/static/` and backed
by the JSON API under `/api`. The layout mirrors Discord: a server rail of class
icons on the far left, a channel sidebar (students, attendance, reports,
class-info) beside it, the main content pane, and a contextual right sidebar
(the member list, today's attendance summary, class details, and so on).

There is no login: it attaches to the existing teacher in the database (or
creates a local admin), and the AI chat calls the Groq LLM API with the same
tools as the rest of the app.

```bash
pipenv install --dev
docker compose up -d db
pipenv run alembic upgrade head
pipenv run uvicorn app.main:app --reload
```

Open http://localhost:8000. With Docker, `docker compose up --build` serves it
on the same port.

---

## Configuration

Everything is read once, through `app/core/config.py`; nothing else in the
codebase reads `os.environ`. See [`.env.example`](.env.example) for the full
list. The settings that matter most:

| Variable | Default | Why you would change it |
| --- | --- | --- |
| `TELEGRAM_BOT_TOKEN` | — | Required. From `@BotFather`. |
| `GROQ_API_KEY` | — | Required. From [GroqCloud API Keys](https://console.groq.com/keys). |
| `GROQ_MODEL` | `llama-3.3-70b-versatile` | Any Groq model with tool calling. |
| `GROQ_TIMEOUT_SECONDS` | `120` | HTTP timeout for Groq requests. |
| `DATABASE_URL` | local PostgreSQL | The `+asyncpg` driver is added for you if you omit it. |
| `TIMEZONE` | `UTC` | **Set this.** It decides what "today" means for attendance and reports. |
| `TELEGRAM_MODE` | `polling` | `webhook` for production behind a public URL. |
| `TELEGRAM_ALLOWED_USER_IDS` | `[]` (open) | Lock the bot to specific Telegram accounts. |
| `CONVERSATION_TTL_SECONDS` | `1800` | How long "John absent" keeps working without repeating the class. |
| `MAX_TOOL_ITERATIONS` | `8` | Safety valve on a model that loops. |

---

## What the assistant can do

**Classes** — create, rename, delete (with confirmation), list, describe.

**Students** — add, remove (with confirmation), update, list, search. Each
student belongs to exactly one class, and student IDs are unique within a
class.

**Attendance** — open a session for a class and date, mark students present /
absent / late / excused by tapping or typing, bulk-mark the rest, finish with a
summary, or cancel. At most one session exists per class per day.

**Reports** — attendance by date or period, by class, by student (with a
day-by-day history), a monthly per-student summary ranked worst-first, and
"who was absent today / this week".

**Tuition** — set a daily fee per class (VND). Each student is charged that
fee for every attended day (present or late); absent and excused days are free.
Ask for tuition totals or teaching-day counts over any period.

The twenty-three tools backing these are registered in
[`app/ai/tools/definitions.py`](app/ai/tools/definitions.py).

### Referring to students the way people talk

`resolve()` in `StudentService` narrows candidates in SQL, then applies tiered
matching: exact code → exact name → first-name or prefix → substring → fuzzy.
Accents are ignored, so `nguyen thi b` finds `Nguyễn Thị B`. When a reference
matches several students, the service raises an error carrying the candidates,
and the assistant asks which one was meant — it never guesses.

### Error handling

Services raise typed domain errors. The registry converts them into structured
results the model can read:

```json
{ "error": "class_not_found",
  "message": "You don't have a class called 'GHOST'.",
  "details": { "available_classes": ["SE401"] } }
```

The model rephrases the message naturally. Unexpected exceptions are logged in
full and replaced with a bland apology, so a stack trace can never reach a
teacher. Destructive actions raise `confirmation_required` on the first call,
so deletion always takes a confirmed second step.

---

## Project layout

```
app/
├── ai/
│   ├── agent.py            tool-calling loop over the Responses API
│   ├── client.py           Groq client construction
│   ├── memory.py           conversation state + TTL expiry
│   ├── prompts.py          system prompt assembly
│   └── tools/
│       ├── definitions.py  the tool catalogue
│       ├── registry.py     validation boundary and dispatch
│       └── schema.py       Pydantic → strict JSON Schema
├── api/                    JSON API, health probes, Telegram webhook, error mapping
├── core/                   config, logging, exception hierarchy
├── database/               engine and session lifecycle
├── models/                 SQLAlchemy 2.0 ORM models
├── repositories/           all SQL
├── schemas/                Pydantic contracts (tool inputs and outputs)
├── services/               business rules
│   └── container.py        composition root
├── telegram/               handlers, keyboards, rendering
├── web/                    runtime + static HTML/CSS/JS dashboard
├── utils/                  date and text helpers
└── main.py                 FastAPI app + bot lifecycle
```

### Data model

```
Teacher ──< Class ──< Student
               │         │
               └──< AttendanceSession ──< AttendanceRecord >── Student
```

Constraints that carry business meaning:

- one class name per teacher, case-insensitively (functional unique index);
- one student code per class;
- **one attendance session per class per day** — this is what turns a second
  "take attendance for SE401" into a friendly "already done today";
- one record per student per session.

Deletes cascade at the database level, and relationships use
`passive_deletes=True` so the ORM does not load children just to delete them.

---

## Design decisions

**The model gets no identity.** `teacher_id` travels in the tool *context*, not
in tool arguments, so the model has no way to name another teacher. Every
repository query filters by ownership in its `WHERE` clause.

**Sessions are database state, not chat state.** An attendance session is
"active" because a row says `open`. Conversation memory only supplies a hint
about which class is in focus. Restart the bot mid-roll-call and nothing is
lost; let the context expire and the teacher just names the class again.

**Buttons and typing share one implementation.** Each attendance operation has
a conversational entry point (resolve the session from a name or hint) and a
direct one (take a session id), both delegating to the same private method. The
two paths cannot drift apart.

**Strict tool schemas, generated not written.** `ai/tools/schema.py` converts
each Pydantic model into the conservative JSON Schema subset local LLMs accept:
`$ref`s inlined, every property required, `additionalProperties: false`,
validation keywords stripped. Nothing is lost by stripping them, because the
arguments are re-validated against the real model before any service runs —
the schema is a hint, not the enforcement boundary.

**Two parse modes, on purpose.** Messages the application composes are sent as
HTML, where every dynamic value can be escaped with certainty. Free text from
the model is sent as Markdown with a plain-text fallback, because escaping the
model's own formatting would show teachers literal asterisks.

**A known trade-off:** the database transaction stays open across the model
round trip, because tools need it mid-loop. That is fine at this scale; a
high-traffic deployment would give each tool call its own session. The comment
in `telegram/handlers/messages.py` says so at the call site.

---

## Development

```bash
pipenv install --dev

pipenv run pytest                 # 165 tests
pipenv run pytest tests/unit -q   # fast, no database
pipenv run ruff check app tests
pipenv run ruff format app tests
```

### How the tests are built

Integration tests run against a real SQLite database with foreign keys enabled,
so the SQL the repositories build is genuinely exercised and cascade deletes
really cascade. Only the Groq client is faked — `tests/integration/test_agent.py`
replays scripted model responses through the real registry, real services and a
real database, which is what proves the loop end to end:

| Suite | Covers |
| --- | --- |
| `unit/test_tool_schema.py` | Every registered tool emits a valid strict schema |
| `unit/test_registry.py` | Bad JSON, missing and hallucinated arguments, domain vs. unexpected errors |
| `unit/test_keyboards.py` | Callback round-trips, the 64-byte limit, pagination |
| `unit/test_text.py` | Each matching tier, accents, ambiguity |
| `unit/test_memory.py` | TTL expiry, history trimming, purging |
| `integration/test_attendance_flow.py` | The whole workflow, including cross-teacher isolation |
| `integration/test_agent.py` | Tool loop, iteration limit, follow-up context |
| `integration/test_reports.py` | Period resolution and aggregation |

### Migrations

```bash
pipenv run alembic revision --autogenerate -m "describe the change"
pipenv run alembic upgrade head
pipenv run alembic downgrade -1
```

`alembic/env.py` reads the DSN from `Settings`, so migrations and the app can
never disagree about which database they are using.

---

## Deployment

`docker compose up --build` runs three things: PostgreSQL, a one-shot `migrate`
service, and the API. The API waits for migrations to complete successfully, so
a deploy cannot start against a stale schema. The image is multi-stage, installs
with `pipenv install --deploy` (which fails if `Pipfile.lock` is out of date),
and runs as an unprivileged user.

### Webhook mode

```env
TELEGRAM_MODE=webhook
TELEGRAM_WEBHOOK_URL=https://your-domain.example/telegram/webhook
TELEGRAM_WEBHOOK_SECRET=a-long-random-string
```

The webhook is registered on startup. The route authenticates the secret
header, enqueues the update and returns immediately, so Telegram never retries
an update that is already being handled.

---

## Extending the system

The seams that were left deliberately open:

| You want to | Do this |
| --- | --- |
| Add a capability | Add a service method, a Pydantic input/output pair, and one `registry.register(...)` line. No prompt surgery needed. |
| Run more than one bot process | Implement the `ConversationStore` protocol over Redis. Nothing outside `ai/memory.py` changes. |
| Support multiple schools | Add a `School` table and a nullable FK on `Teacher`. Ownership is already scoped through the teacher, so no query logic changes shape. |
| Add roles and permissions | Extend `TeacherService`, which is the single authentication boundary. |
| Import a roster from Excel | Add a service that calls `StudentService.add_student` per row; the validation and duplicate handling already exist. |
| Notify parents | Add contact fields to `Student` and a notifier invoked from `_finalise` in `AttendanceService`. |

New capabilities appear to the model automatically, because the prompt
describes *behaviour* and the catalogue describes *tools*.
