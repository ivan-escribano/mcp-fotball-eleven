
https://github.com/user-attachments/assets/9ce7fbdb-6fd6-4981-b439-9f26476f974a
# MCP Eleven

> MCP Eleven is an open-source MCP server that connects to any MCP client (Claude, Cursor, VSCode) and turns natural language into football data analysis. Just describe what you're looking for, and the server translates your query into structured database operations across 40+ player stats and 20+ leagues. From there, you can dive into deep scouting analysis, generate comparisons, or export everything into Excel, PDF, Word and more. No SQL, no filters, no scraping, just ask.

![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python&logoColor=white)
![FastMCP](https://img.shields.io/badge/FastMCP-2.13.3-green)
![SQLModel](https://img.shields.io/badge/SQLModel-0.0.27-orange)
![Azure](https://img.shields.io/badge/Azure-Deployed-0078D4?logo=microsoftazure&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-yellow)


https://github.com/user-attachments/assets/54d2aaa3-bd35-411b-aad1-27599455b108

---

## What it solves

Football stats are scattered across websites, locked behind complex filters, and impossible to query conversationally. MCP Eleven turns any AI assistant (Claude, VSCode, Cursor) into a football scouting tool just describe what you're looking for, and get real stats back instantly.

---

## Architecture

### Ingest Pipeline

![Ingest Pipeline](docs/diagrams/mcp-ingest-pipeline.png)

### Build & Deploy Pipeline

![Build & Deploy Pipeline](docs/diagrams/mcp-buil-pipeline.png)

### Client Request Flow

![Client Request Flow](docs/diagrams/mcp-client-response.png)

See [`docs/architecture.md`](docs/architecture.md) for detailed pipeline breakdowns and sequence diagrams.

---

## Quick Start

### 1. Clone and install

```bash
git clone https://github.com/your-username/mcp-eleven.git
cd mcp-eleven
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env with your values
```

`.env.example`:

```env
APIKEY_SALT=your-random-salt-here
HOST=0.0.0.0
PORT=8000

# Database mode:
# - Local SQLite (default): leave DATABASE_URL commented out → uses data/mcp_eleven.db
# - Azure SQL (production): uncomment and set your connection string
# DATABASE_URL=mssql+pyodbc://user:pass@server.database.windows.net:1433/dbname?driver=ODBC+Driver+18+for+SQL+Server
```

> **Local development uses SQLite by default.** No extra setup needed — the database file is created automatically at `data/mcp_eleven.db` when you load data. To switch to Azure SQL for production, uncomment `DATABASE_URL` and set your connection string.

### 3. Load data

```bash
python scripts/load_data.py
```

### 4. Create an API key

```bash
python scripts/create_api_key.py
```

### 5. Run the server

```bash
python main.py
```

Server starts at `http://localhost:8000`. Health check at `/health`.

### 6. Connect from an MCP client

The recommended MCP client for local development is **Claude Desktop**.

#### Claude Desktop (Recommended)

Claude Desktop only supports MCP servers over **stdio** — it launches servers as child processes. Since MCP Eleven runs as an HTTP server, you need [`mcp-remote`](https://www.npmjs.com/package/mcp-remote) to bridge the connection. `mcp-remote` wraps your HTTP server into the stdio interface that Claude Desktop expects.

> **Prerequisite:** Node.js must be installed (for `npx`).

Edit your Claude Desktop config file:

- **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
- **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "mcp-eleven": {
      "command": "npx",
      "args": [
        "mcp-remote@latest",
        "http://localhost:8000/mcp?api_key=YOUR_API_KEY",
        "--allow-http"
      ]
    }
  }
}
```

> `--allow-http` is required because the server runs on `http://` locally (not `https://`).

Then **fully restart Claude Desktop** (quit from the system tray, not just close the window). Make sure the server is running before you open Claude Desktop.

#### VSCode / Cursor (Direct HTTP)

Clients that support HTTP transport natively don't need the `mcp-remote` bridge:

```json
{
  "mcpServers": {
    "mcp-eleven": {
      "url": "http://localhost:8000/mcp?api_key=YOUR_API_KEY"
    }
  }
}
```

---

## Usage Example

**You ask** (in Claude, VSCode, or any MCP client):

> "Top 5 scorers in La Liga this season"

**The AI calls** `search_players` with:

```json
{
  "league": "La Liga",
  "season": "25/26",
  "order_by": "goals",
  "order_direction": "DESC",
  "limit": 5
}
```

**You get back** real stats:

| Player   | Team        | Goals | Assists | xG   | Minutes |
| -------- | ----------- | ----- | ------- | ---- | ------- |
| Player A | Real Madrid | 18    | 5       | 16.2 | 2340    |
| Player B | Barcelona   | 15    | 8       | 14.8 | 2100    |
| ...      | ...         | ...   | ...     | ...  | ...     |

All 40+ stats are available: shots, dribbles, passes, tackles, duels, saves, cards, and more.

---

## Tech Stack

| Component     | Technology                        | Purpose                        |
| ------------- | --------------------------------- | ------------------------------ |
| Language      | Python 3.12                       | Core runtime                   |
| MCP Framework | FastMCP 2.13.3                    | Exposes tools to AI assistants |
| ORM           | SQLModel 0.0.27                   | Type-safe database operations  |
| Data Source   | ScraperFC 3.4.0 (Sofascore)       | Football statistics            |
| Database      | SQLite (local) / Azure SQL (prod) | Player stats storage           |
| Auth          | API key (hashed + tracked)        | Access control                 |
| Container     | Docker                            | Reproducible deployment        |
| CI/CD         | GitHub Actions                    | Auto build + deploy on push    |
| Hosting       | Azure App Service                 | Production server              |

---

## Leagues Supported

| Top 5          | Continental       | Americas          | Other             |
| -------------- | ----------------- | ----------------- | ----------------- |
| Premier League | Champions League  | MLS               | Saudi Pro League  |
| La Liga        | Europa League     | Copa Libertadores | Turkish Super Lig |
| Bundesliga     | Conference League | Argentina Liga    | World Cup         |
| Serie A        | Euros             | USL Championship  | Women's World Cup |
| Ligue 1        |                   | Liga 1 Peru       | Gold Cup          |

---

## Project Structure

```
mcp-eleven/
├── main.py              # MCP server + search_players tool
├── config/
│   ├── settings.py      # Host, port, env vars
│   ├── database.py      # DB connection (SQLite / Azure SQL)
│   └── leagues.py       # Supported leagues
├── model/
│   ├── player.py        # Player stats schema (40+ fields)
│   ├── filters.py       # Search filters (all optional)
│   └── api_key.py       # API key model
├── db/
│   └── database.py      # Query engine
├── auth/
│   └── middleware.py     # API key validation
├── scripts/
│   ├── load_data.py     # Data ingestion pipeline
│   └── create_api_key.py
├── utils/
│   └── normalize_player_stats.py
├── data/                # Local SQLite storage
├── .github/workflows/   # CI/CD pipeline
├── Dockerfile           # Production container
└── requirements.txt
```

---

## Documentation

- [`docs/overview.md`](docs/overview.md) — High-level overview: what it is, who it's for, how it works
- [`docs/architecture.md`](docs/architecture.md) — Technical deep-dive: pipelines, project structure, security

---

## Roadmap

- [ ] Add position-based filtering
- [ ] Player comparison tool
- [ ] Historical season-over-season tracking
- [ ] Streaming responses for large queries

---

## License

MIT

---

## Connect with me

[![LinkedIn](https://img.shields.io/badge/LinkedIn-0A66C2?logo=linkedin&logoColor=white)](https://www.linkedin.com/in/ivan-escribano-dev)
[![Email](https://img.shields.io/badge/Email-D14836?logo=gmail&logoColor=white)](mailto:ivanescribano1998@gmail.com)
[![X](https://img.shields.io/badge/X-000000?logo=x&logoColor=white)](https://x.com/IvanEscribano98)
[![GitHub](https://img.shields.io/badge/GitHub-181717?logo=github&logoColor=white)](https://github.com/ivan-escribano)
[![Substack](https://img.shields.io/badge/Substack-FF6719?logo=substack&logoColor=white)](https://ivanescribano.substack.com)
[![Medium](https://img.shields.io/badge/Medium-000000?logo=medium&logoColor=white)](https://medium.com/@ivanescribano1998)
