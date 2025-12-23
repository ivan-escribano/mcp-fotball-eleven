mcp-scout-football/
│
├── main.py # Servidor MCP + tool
├── requirements.txt # Dependencias
│
├── data/
│ └── players.db # SQLite (se crea automático)
│
├── scripts/
│ └── load_data.py # Carga datos a SQLite
│
└── db/
├── **init**.py
└── database.py # Conexión + queries

Pasos
Crear estructura de carpetas: Generar directorios (data, scripts, db), crear requirements.txt con dependencias (fastmcp, ScraperFC, pandas), y db/**init**.py.

Crear capa de base de datos: Implementar db/database.py con función init_db() para crear tabla players, save_players(df) para guardar DataFrame, y get_players(league, position, limit) para consultar.

Crear script de carga: Implementar scripts/load_data.py que haga scraping de Sofascore con ScraperFC y guarde los datos en SQLite.

Crear servidor MCP: Implementar main.py con FastMCP exponiendo la tool get_players(league, position, limit) que consulta SQLite y devuelve lista de jugadores.

Probar el flujo completo: Cargar datos con python scripts/load_data.py --league laliga, luego probar el MCP server.

PASO 1 - Cargar datos (una vez):
┌──────────────────┐ ┌──────────────┐ ┌─────────────┐
│ scripts/ │ │ ScraperFC │ │ data/ │
│ load_data.py │ ──► │ (Sofascore) │ ──► │ players.db │
└──────────────────┘ └──────────────┘ └─────────────┘

PASO 2 - Consultar (cada petición):
┌──────────┐ ┌──────────┐ ┌─────────────┐ ┌──────────────┐
│ Usuario │ ──► │ LLM │ ──► │ main.py │ ──► │ players.db │
│ │ │ │ │ (MCP tool) │ │ (consulta) │
└──────────┘ └──────────┘ └─────────────┘ └──────────────┘
│
▼
Lista de jugadores
