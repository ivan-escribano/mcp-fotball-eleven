# MCP Eleven

---

## High-Level Overview

### What is it?

```
┌─────────────────────────────────────────────────────────┐
│                     MCP Eleven                          │
│                                                         │
│   "Lewandowski stats?"  ──>  AI assistant  ──>  Data    │
│                                                         │
│   You talk.             The AI searches.   You get      │
│                                            real stats.  │
└─────────────────────────────────────────────────────────┘
```

- An AI-powered football scouting tool. You describe what you need in plain language, the system returns real player stats.
- Built on **MCP** (Model Context Protocol) — a standard that lets AI assistants (Claude, VSCode, Cursor) call external tools.
- Covers **20+ leagues**: Premier League, La Liga, Bundesliga, Serie A, Ligue 1, Champions League, MLS, and more.

> Like Google for football stats, but you talk to it instead of typing filters.

**Synthesis:**
You ask in natural language. The AI calls MCP Eleven. MCP Eleven queries the database. You get real stats back. No forms, no filters, no SQL.

---

### Who is it for?

```
┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│   Scouts     │   │  Coaches /   │   │  Football    │
│              │   │  Analysts    │   │  Fans        │
│ "Find a CB   │   │ "Top assist  │   │ "Best GK    │
│  under 25    │   │  providers   │   │  saves in   │
│  in LaLiga"  │   │  in PL"      │   │  Serie A?"  │
└──────────────┘   └──────────────┘   └──────────────┘
        │                 │                   │
        └─────────────────┼───────────────────┘
                          ▼
                   ┌──────────────┐
                   │  MCP Eleven  │
                   │  answers all │
                   └──────────────┘
```

- **Scouts** — discover players matching specific profiles (position, age, stats, league)
- **Coaches / analysts** — quick access to performance data without spreadsheets
- **Anyone with an AI assistant** — just talk, get stats

**Synthesis:**
If you care about football data and use AI tools, this is for you. Zero technical knowledge required on the user side.

---

### What can you search?

```
┌─────────────────────────────────────────────────┐
│              40+ Stats Available                 │
│                                                  │
│  ATTACK     │  CREATIVE   │  DEFENSE            │
│  goals      │  key passes │  tackles             │
│  assists    │  crosses    │  interceptions       │
│  xG, shots  │  long balls │  clearances          │
│             │             │                      │
│  PASSING    │  DUELS      │  GOALKEEPING         │
│  accuracy   │  ground     │  saves               │
│  final 3rd  │  aerial     │  claims, punches     │
└─────────────────────────────────────────────────┘
```

- **40+ filters** organized by area: attacking, creative, passing, defensive, duels, discipline, goalkeeping
- All filters are optional. Use min/max. Combine freely.
- Sort by any stat, limit results.

**Synthesis:**
Name it, filter it. Goals, assists, tackles, saves — any stat, any league, any combination.

---

## Tech Overview

### The 3 Pipelines

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

Three separate processes. Each independent. Together they make the system work.

**Synthesis:**
Pipeline 1 fills the database. Pipeline 2 deploys the server. Pipeline 3 answers questions. That's the whole system.

---

### Pipeline 1 — Ingest (Loading Data)

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

**Synthesis:**
Scrape. Clean. Store. Run once per data update. The database is ready to be queried.

---

### Pipeline 2 — Build & Deploy

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

**Synthesis:**
Push code. GitHub builds. Azure deploys. Zero manual steps. Server is live.

---

### Pipeline 3 — Serve Requests (How It Works)

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

**Synthesis:**
User talks. AI decides what to search. MCP Eleven fetches from the database. AI presents the answer. All automatic.

---

### Project Structure

```
mcp-eleven/
│
├── main.py              # Entry point — FastMCP server + tool
│
├── config/
│   ├── settings.py      # Host, port, env vars
│   ├── database.py      # DB connection (SQLite or Azure SQL)
│   └── leagues.py       # Supported leagues config
│
├── model/
│   ├── player.py        # Player stats schema (SQLModel)
│   ├── filters.py       # Search filters (40+ optional fields)
│   └── api_key.py       # API key model
│
├── db/
│   └── database.py      # Query engine (get_players, save)
│
├── auth/
│   └── middleware.py     # API key validation
│
├── scripts/
│   ├── load_data.py     # Ingest pipeline (scrape + save)
│   └── create_api_key.py
│
├── utils/
│   └── normalize_player_stats.py
│
├── data/                # Local SQLite storage
├── .github/workflows/   # CI/CD pipeline
└── Dockerfile           # Container config
```

- **main.py** — the whole server in one file. Defines the MCP tool, middleware, health check.
- **config/** — everything about where and how to connect.
- **model/** — what a player looks like, what filters exist, what an API key is.

**Synthesis:**
Small project. One tool. One database. One server. Config, models, database, auth — each in its own folder. Clean separation.

---

### Key Tech Stack

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

- **FastMCP** turns a Python function into an AI-callable tool
- **SQLModel** maps Python classes to database tables (type-safe, no raw SQL)
- **ScraperFC** pulls Sofascore stats without browser automation

**Synthesis:**
FastMCP exposes the tool. SQLModel handles data. ScraperFC feeds it. Docker + Azure runs it. GitHub Actions automates deployment.
