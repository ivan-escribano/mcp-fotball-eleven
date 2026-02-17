# MCP Eleven

---

## What is it?

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

## Who is it for?

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

## What can you search?

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

## How does it work? (simplified)

```
  User                AI Assistant          MCP Eleven           Database
   │                  (Claude/VSCode)       (this server)        (stats)
   │                       │                    │                   │
   │  "Top scorers         │                    │                   │
   │   in La Liga"         │                    │                   │
   │ ────────────────────> │                    │                   │
   │                       │  call tool +       │                   │
   │                       │  filters           │                   │
   │                       │ ─────────────────> │                   │
   │                       │                    │  query            │
   │                       │                    │ ────────────────> │
   │                       │                    │  stats JSON       │
   │                       │                    │ <──────────────── │
   │                       │  stats JSON        │                   │
   │                       │ <───────────────── │                   │
   │  "Here are the top    │                    │                   │
   │   scorers: ..."       │                    │                   │
   │ <──────────────────── │                    │                   │
```

- You ask in natural language via any MCP client (Claude, VSCode, Cursor)
- The AI decides what to search and calls MCP Eleven automatically
- MCP Eleven queries the database and returns results. The AI formats the answer for you.

> Like ordering at a restaurant. You tell the waiter (AI) what you want. The waiter tells the kitchen (MCP Eleven). Kitchen checks the fridge (database). Plate comes back ready.

**Synthesis:**
User talks. AI decides what to search. MCP Eleven fetches from the database. AI presents the answer. All automatic.

---

## Where does it run?

```
┌─────────────────────┐          ┌─────────────────────┐
│      LOCAL           │          │     PRODUCTION       │
│                      │          │                      │
│  Your machine        │          │  Azure cloud         │
│  SQLite database     │          │  Azure SQL database  │
│  For development     │          │  Docker container    │
│                      │          │  Auto-deployed       │
└─────────────────────┘          └─────────────────────┘
```

- **Locally**: runs on your machine with SQLite. Fast to develop and test.
- **Production**: Docker container on Azure, backed by Azure SQL. Auto-deployed on every push via GitHub Actions.

**Synthesis:**
Develop locally with SQLite. Deploy to Azure with Docker. Same code, different database.
