# MCP Eleven — Architecture

---

## The 3 Pipelines

```
┌─────────────────────────────────────────────────────────────────────┐
│                        MCP Eleven — Big Picture                     │
│                                                                     │
│   PIPELINE 1            PIPELINE 2             PIPELINE 3           │
│   Ingest Data           Build & Deploy         Serve Requests       │
│                                                                     │
│   Scraper               MCP Server code        User asks question   │
│      ↓                     ↓                      ↓                 │
│   Raw stats             Docker image           AI calls MCP tool    │
│      ↓                     ↓                      ↓                 │
│   Clean + normalize     Push to Azure          Query database       │
│      ↓                     ↓                      ↓                 │
│   Save to DB            App goes live          Return stats         │
│                                                                     │
│   (runs once/update)    (runs on git push)     (runs per question)  │
└─────────────────────────────────────────────────────────────────────┘
```

- Three separate processes. Each independent. Together they make the system work.
- Pipeline 1 fills the database. Pipeline 2 deploys the server. Pipeline 3 answers questions.
- That's the whole system.

**Synthesis:**
Ingest, deploy, serve. Three pipelines, each with one job. Learn them separately.

---

## Pipeline 1 — Ingest (Loading Data)

```
┌──────────────────┐     ┌──────────────────┐     ┌──────────────┐
│  Python Scraper  │     │  Pandas          │     │  Database    │
│  (ScraperFC)     │────>│  Clean +         │────>│              │
│                  │     │  Normalize       │     │  SQLite      │
│  Sofascore API   │     │                  │     │  (local)     │
│  20+ leagues     │     │  Column names    │     │     or       │
│  All positions   │     │  Data types      │     │  Azure SQL   │
│                  │     │  Deduplication   │     │  (prod)      │
└──────────────────┘     └──────────────────┘     └──────────────┘

scripts/load_data.py  ──>  utils/normalize  ──>  db/database.py
```

- **ScraperFC** pulls raw stats from Sofascore for each league + season
- **Pandas** cleans column names, fixes types, removes duplicates
- **Result** saved to SQLite (local dev) or Azure SQL (production)

> Like filling a warehouse before opening a store. You load the shelves once, then serve customers from stock.

### How to run it

```
python scripts/load_data.py --league laliga --season 2024
```

Replaces old data for that league/season. Safe to re-run.

**Synthesis:**
Scrape. Clean. Store. Run once per data update. The database is ready to be queried.

---

## Pipeline 2 — Build & Deploy

```
┌──────────────────┐     ┌──────────────────┐     ┌──────────────┐
│  Python          │     │  Docker          │     │  Azure       │
│  MCP Server      │────>│  Image           │────>│              │
│                  │     │                  │     │  Container   │
│  main.py         │     │  Dockerfile      │     │  Registry    │
│  FastMCP tools   │     │  All deps        │     │      ↓       │
│  Auth middleware  │     │  Locked versions │     │  App Service │
└──────────────────┘     └──────────────────┘     └──────────────┘

git push main  ──>  GitHub Actions  ──>  Azure (live)
```

- **On every push to main**, GitHub Actions builds a Docker image
- Image is pushed to **Azure Container Registry**
- Azure App Service pulls the new image and restarts

> Like a factory assembly line. Code goes in, a running server comes out. Automatic.

### The CI/CD flow

```
Developer pushes code
        ↓
GitHub Actions triggers (.github/workflows/deploy.yml)
        ↓
docker build  ──>  docker push to ACR
        ↓
Azure App Service detects new image
        ↓
Server restarts with new code
```

**Synthesis:**
Push code. GitHub builds. Azure deploys. Zero manual steps. Server is live.

---

## Pipeline 3 — Serve Requests (How It Works)

```
  User                MCP Client           LLM              MCP Server        Database
   │                (Claude/VSCode)                        (MCP Eleven)      (Azure SQL)
   │                     │                  │                  │                 │
   │  "Lewandowski       │                  │                  │                 │
   │   stats?"           │                  │                  │                 │
   │ ──────────────────> │                  │                  │                 │
   │                     │  Message +       │                  │                 │
   │                     │  available tools │                  │                 │
   │                     │ ───────────────> │                  │                 │
   │                     │                  │                  │                 │
   │                     │                  │ "I need          │                 │
   │                     │                  │  search_players" │                 │
   │                     │                  │                  │                 │
   │                     │                  │  Call tool +     │                 │
   │                     │                  │  filter params   │                 │
   │                     │                  │ ───────────────> │                 │
   │                     │                  │                  │  SQL query      │
   │                     │                  │                  │ ──────────────> │
   │                     │                  │                  │                 │
   │                     │                  │                  │  Stats JSON     │
   │                     │                  │                  │ <────────────── │
   │                     │                  │  Stats JSON      │                 │
   │                     │                  │ <─────────────── │                 │
   │                     │                  │                  │                 │
   │                     │  Final answer    │                  │                 │
   │                     │ <─────────────── │                  │                 │
   │  "Lewandowski has   │                  │                  │                 │
   │   15 goals, 4       │                  │                  │                 │
   │   assists..."       │                  │                  │                 │
   │ <────────────────── │                  │                  │                 │
```

- **User asks** in natural language via any MCP client (Claude, VSCode, Cursor)
- **LLM reads** the available tools, decides to call `search_players` with filters
- **MCP Server queries** the database, returns JSON. LLM formats the answer for the user.

> Like ordering at a restaurant. You tell the waiter (AI) what you want. The waiter tells the kitchen (MCP server). Kitchen checks the fridge (database). Plate comes back ready.

### What happens inside the MCP Server

```
Incoming tool call: search_players(filters)
        ↓
API key middleware validates the request  (auth/middleware.py)
        ↓
Filters parsed into PlayerStatsFilters    (model/filters.py)
        ↓
SQL query built dynamically               (db/database.py)
        ↓
Results returned as list of dicts
        ↓
JSON sent back to LLM
```

**Synthesis:**
User talks. AI decides what to search. MCP Eleven fetches from the database. AI presents the answer. All automatic.

---

## Project Structure

```
mcp-eleven/
│
├── main.py                  # Entry point — FastMCP server + search_players tool
│
├── config/
│   ├── settings.py          # Host, port, env vars
│   ├── database.py          # DB connection (SQLite or Azure SQL)
│   └── leagues.py           # Supported leagues config
│
├── model/
│   ├── player.py            # Player stats schema (SQLModel — 40+ fields)
│   ├── filters.py           # Search filters (min/max for every stat)
│   └── api_key.py           # API key model
│
├── db/
│   └── database.py          # Query engine (get_players, save_players)
│
├── auth/
│   └── middleware.py         # API key validation (hash-based, usage tracking)
│
├── scripts/
│   ├── load_data.py         # Ingest pipeline (scrape + clean + save)
│   └── create_api_key.py    # Generate new API keys
│
├── utils/
│   └── normalize_player_stats.py  # Column name normalization
│
├── data/                    # Local SQLite storage
├── .github/workflows/       # CI/CD (deploy.yml)
└── Dockerfile               # Container config for production
```

- **main.py** — the whole server in one file. Defines the MCP tool, auth middleware, health check.
- **config/** — everything about where and how to connect (DB, host, leagues).
- **model/** — what a player looks like, what filters exist, what an API key is.

**Synthesis:**
Small project. One tool. One database. One server. Config, models, database, auth — each in its own folder. Clean separation.

---

## Key Tech Stack

```
┌────────────────────────────────────────────────────┐
│                                                    │
│  Python 3.12  ──>  FastMCP  ──>  SQLModel          │
│  (language)       (MCP framework)  (ORM)           │
│                                                    │
│  ScraperFC    ──>  Pandas   ──>  Azure SQL         │
│  (data source)    (cleaning)     (production DB)   │
│                                                    │
│  Docker       ──>  GitHub Actions ──> Azure        │
│  (packaging)      (CI/CD)           (hosting)      │
│                                                    │
└────────────────────────────────────────────────────┘
```

- **FastMCP** turns a Python function into an AI-callable tool. One decorator = one tool.
- **SQLModel** maps Python classes to database tables. Type-safe, no raw SQL.
- **ScraperFC** pulls Sofascore stats without browser automation.

**Synthesis:**
FastMCP exposes the tool. SQLModel handles data. ScraperFC feeds it. Docker + Azure runs it. GitHub Actions automates deployment.

---

## Security

```
┌──────────────────────────────────────────────────┐
│                 Request Flow                      │
│                                                   │
│  Client sends request                             │
│       ↓                                           │
│  API key checked (URL param or header)            │
│       ↓                                           │
│  Key hashed ──> compared to stored hash           │
│       ↓                                           │
│  Valid? ──> proceed     Invalid? ──> reject        │
│       ↓                                           │
│  Usage tracked (call count, last used)            │
└──────────────────────────────────────────────────┘
```

- Every request needs an API key (`?api_key=sk_xxx` or header)
- Keys are **hashed** — never stored in plain text
- Usage is tracked for auditing (number of calls, last used timestamp)

**Synthesis:**
No key, no access. Keys are hashed. Usage is logged. Simple and secure.
