# Wikipedia Time Machine

A project for Area 3, **"System-versioned tables: history for free"**, for the [MariaDB Student Database Projects, 2026-09](https://mariadb.org/bachelor_hackathon_2026-09/).

**Team:** Zakaria Deraoui · Alice Ragni · Xiyuan Zhang · Anara Yusifzada

> **Status:** Work in progress.  
> The database schema and initial Node.js project foundation are implemented. Data ingestion, the web application, validation, testing, and benchmarking are still under development.

---

## 1. Project idea

Wikipedia keeps the complete revision history of its articles. This makes it a useful real-world dataset for exploring temporal databases.

MariaDB supports **system-versioned tables**, which automatically preserve previous versions of rows:

```sql
CREATE TABLE t (...) WITH SYSTEM VERSIONING;

SELECT *
FROM t
FOR SYSTEM_TIME AS OF TIMESTAMP '2024-01-01 00:00:00';
```

This project investigates the question:

> **Can MariaDB system-versioned tables be used to build a "time machine" for Wikipedia history?**

The important complication is that two different notions of time are involved.

- **Application time** — when a revision was actually valid on Wikipedia.
- **System time** — when our MariaDB database stored or changed its knowledge of that revision.

Wikipedia revision timestamps therefore cannot simply be replaced by database system time. The project explores how MariaDB's application-time periods and system versioning can be combined into a **bitemporal model**.

The final goal is to allow a user to choose a Wikipedia article and a point in time and reconstruct the version that was valid at that moment.

---

## 2. Current progress

The project is being developed incrementally. The current repository has completed the initial database and project-foundation work.

| Component | Status |
|---|---|
| Project requirements | Implemented |
| MariaDB core schema | Implemented |
| Application-time article history | Implemented |
| System-versioned article history | Implemented |
| System-versioned `page_mirror` | Implemented |
| Clean database bootstrap | Verified |
| Node.js project foundation | Implemented |
| Environment configuration | Implemented |
| JavaScript linting | In progress |
| Node.js database runtime | Planned |
| Wikipedia article resolution | Planned |
| Revision ingestion | Planned |
| Mirror replay | Planned |
| Temporal validation | Planned |
| Web application | Planned |
| Automated tests | Planned |
| Benchmarks | Planned |
| Docker environment | Planned |

No final experimental results or benchmark numbers are reported yet.

---

## 3. Temporal model

The database currently implements two related temporal approaches.

### 3.1 Application-time history

`article_history` represents when a particular Wikipedia revision was valid:

```text
revision A        revision B        revision C
    │                 │                 │
    ▼                 ▼                 ▼

T1 ─────────────── T2 ─────────────── T3 ───────────────► time

A: [T1, T2)
B: [T2, T3)
C: [T3, ∞)
```

Each row contains:

```text
article_id
rev_id
valid_from
valid_to
row_start
row_end
```

`valid_from` and `valid_to` represent **Wikipedia time**.

`row_start` and `row_end` represent **MariaDB system time**.

This makes `article_history` bitemporal:

```text
Application time:
"When was this revision valid on Wikipedia?"

System time:
"When did our database believe this interval was correct?"
```

The schema uses:

```sql
PERIOD FOR valid_period (valid_from, valid_to)
```

together with:

```sql
WITH SYSTEM VERSIONING
```

and prevents overlapping validity intervals for the same article.

---

### 3.2 System-time mirror

The project also contains a second model called:

```text
page_mirror
```

The idea is different.

Instead of storing every Wikipedia revision as an application-time interval, `page_mirror` keeps one current row per article and lets MariaDB preserve previous rows automatically through:

```sql
WITH SYSTEM VERSIONING
```

The intended future experiment is to replay Wikipedia revisions chronologically while setting the MariaDB session clock to the corresponding Wikipedia revision time.

Then a query such as:

```sql
SELECT *
FROM page_mirror
FOR SYSTEM_TIME AS OF TIMESTAMP '2023-06-01 12:00:00';
```

can be compared with the authoritative application-time result.

This replay and comparison have **not yet been implemented and validated**.

---

## 4. Current database schema

The formal schema is defined by three migrations.

### `001_core_schema.sql`

Defines the core data model, including:

```text
domains
articles
ingestion_runs
sync_checkpoints
article_sync_state
content_chunks
revision_texts
revisions
```

The schema separates several concepts:

```text
article identity
      │
      ├── Wikipedia revision events
      │
      ├── revision content
      │
      └── ingestion state
```

Some tables, including `articles` and `article_sync_state`, use system versioning so that changes to database knowledge can be audited automatically.

---

### `002_article_history.sql`

Defines the main bitemporal table:

```text
article_history
```

Conceptually:

```text
articles
    │
    ├──── revisions
    │
    └──── article_history
              │
              ├── application time
              └── system time
```

A row means:

> Revision `rev_id` represented the visible state of article `article_id` during `[valid_from, valid_to)`.

---

### `003_page_mirror.sql`

Defines:

```text
page_mirror
mirror_replays
```

`page_mirror` is a system-versioned projection intended for replay experiments.

Its historical rows are partitioned using:

```sql
PARTITION BY SYSTEM_TIME
```

The authoritative historical reconstruction will remain based on `article_history`; the mirror is intended as an independent experimental comparison.

---

## 5. Current architecture

At the current stage, the implemented architecture is:

```text
                      MariaDB
                         │
          ┌──────────────┼──────────────┐
          │              │              │
       articles      revisions    ingestion state
          │
          ├──────── article_history
          │             │
          │             ├── application time
          │             └── system time
          │
          └──────── page_mirror
                        │
                        └── system-versioned history
```

The Node.js application layer is being built next.

The intended future data flow is:

```text
Wikipedia API
      │
      ▼
Article resolution
      │
      ▼
Revision ingestion
      │
      ▼
MariaDB temporal model
      │
      ├── application-time reconstruction
      │
      └── system-time replay
      │
      ▼
Validation
      │
      ▼
Repository / service layer
      │
      ▼
Web interface
```

Only the database foundation and initial Node.js project foundation are currently implemented.

---

## 6. Repository structure

The repository is still evolving. The currently relevant structure is:

```text
.
├── README.md
├── package.json
├── package-lock.json
├── .env.example
├── .gitignore
│
├── db/
│   └── migrations/
│       ├── 001_core_schema.sql
│       ├── 002_article_history.sql
│       └── 003_page_mirror.sql
│
├── docs/
│   └── requirement.md
│
├── scripts/
│   └── ...
│
└── sql/
    └── ...
```

The final project is expected to grow additional modules for database access, Wikipedia ingestion, temporal queries, validation, testing, benchmarking, and the web application.

Those directories will be added as their corresponding functionality is implemented rather than created in advance.

---

## 7. Development setup

### Requirements

Current development requires:

- MariaDB 13
- Node.js 20.11 or newer
- npm

Check the installed versions with:

```bash
mariadb --version
node --version
npm --version
```

---

### Environment variables

Copy the example configuration:

```bash
cp .env.example .env
```

Then configure the local MariaDB connection in `.env`:

```env
DB_HOST=127.0.0.1
DB_PORT=3306
DB_NAME=wikipedia_time_machine
DB_USER=wiki_user
DB_PASSWORD=your_password
```

The real `.env` file must never be committed.

---

### Database setup

Create a fresh development database:

```sql
CREATE DATABASE wikipedia_time_machine
    CHARACTER SET utf8mb4;

USE wikipedia_time_machine;
```

From the MariaDB client, apply the migrations in order:

```sql
SOURCE db/migrations/001_core_schema.sql;
SOURCE db/migrations/002_article_history.sql;
SOURCE db/migrations/003_page_mirror.sql;
```

The migrations are currently intended to be applied once to a fresh database.

A Node.js migration runner will be added later.

---

### Node.js setup

Install the current project dependencies:

```bash
npm install
```

The Node.js application layer is still under development.

---

## 8. Research questions

The project will investigate several questions as implementation progresses:

1. Why is MariaDB system time alone insufficient to represent imported Wikipedia history?
2. How can application time and system time be combined to form a useful bitemporal model?
3. Can a replayed system-versioned table reproduce the same historical answers as the application-time model?
4. How does system-versioned history grow as more revisions are stored?
5. When does `PARTITION BY SYSTEM_TIME` improve query or retention behaviour?
6. What are the storage implications of keeping many historical document versions?
7. What are the practical limitations of using temporal tables for a Wikipedia-like workload?

Claims will be added to this README only after they have been implemented, tested, and measured.

---

## 9. Development roadmap

```text
Phase 0 — Baseline & Repository Audit
    ✅ repository and schema audit
    ✅ formal schema baseline
    ✅ clean bootstrap verification
    ✅ local database alignment

Phase 1 — Project Foundation
    ✅ Node.js project initialization
    ✅ environment configuration
    ◐ JavaScript tooling

Phase 2 — Database Foundation / Runtime
    ☐ database configuration
    ☐ connection pool
    ☐ migration runner

Phase 3 — Wikipedia Integration
    ☐ article catalogue
    ☐ MediaWiki API client
    ☐ title resolution

Phase 4 — Revision Ingestion
    ☐ revision metadata
    ☐ revision content
    ☐ resumable ingestion

Phase 5 — Temporal Processing
    ☐ application-time timeline construction
    ☐ system-time mirror replay
    ☐ temporal validation

Phase 6 — Query and Application Layer
    ☐ repositories
    ☐ services
    ☐ HTTP application

Phase 7 — Interface
    ☐ article selection
    ☐ historical reconstruction
    ☐ revision comparison
    ☐ temporal query views

Phase 8 — Quality and Research
    ☐ automated tests
    ☐ benchmarks
    ☐ partitioning experiments
    ☐ final documentation
```

The roadmap reflects the intended direction of the project and will be updated as functionality is completed.

---

## 10. Team

| Name |
|---|
| Zakaria Deraoui |
| Alice Ragni |
| Xiyuan Zhang |
| Anara Yusifzada |

Built for the MariaDB Student Database Projects at Constructor University, 2026-09, Area 3.
