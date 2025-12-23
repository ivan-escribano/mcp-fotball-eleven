Plan: Implementación MCP Scout Football con SQLite
Servidor MCP de scouting de fútbol que usa SQLite como caché de datos. Un script carga los datos una vez (scraping) y el servidor MCP consulta desde la base de datos local (rápido).

Pasos
Crear estructura de carpetas y archivos base: Generar directorios (src/, src/models/, src/scrapers/, src/db/, src/core/, resources/, scripts/, data/),

crear requirements.txt con dependencias (fastmcp, ScraperFC, pandas, pydantic), .gitignore y todos los **init**.py.

Crear archivos de recursos JSON: Escribir resources/defender_profiles.json con los 4 perfiles de defensas, resources/metrics_dictionary.json con definiciones de métricas, y resources/leagues_reference.json con ligas disponibles.

Implementar capa de base de datos SQLite: Crear src/db/connection.py con función para conectar y crear tabla players, y src/db/repository.py con métodos save_players(), find_players(), get_all_by_league().

Implementar scrapers: Crear src/scrapers/sofascore.py para obtener stats de rendimiento y src/scrapers/transfermarkt.py para datos de mercado, ambos usando ScraperFC.

Crear script de carga de datos: Implementar scripts/scrape_and_load.py que ejecute scraping de ambas fuentes, limpie y combine datos, y guarde en SQLite. Este script se corre manualmente cuando quieras actualizar datos.

Implementar lógica de negocio: Crear src/core/scoring.py para calcular scores ponderados según perfil, src/core/filters.py para filtrar por edad/valor/pie, y src/core/pipeline.py que orqueste consulta a SQLite → filtrado → scoring → respuesta.

Configurar servidor MCP principal: Reescribir main.py con FastMCP exponiendo la tool find_players_for_profile() que usa el pipeline, y registrar los recursos JSON para que el LLM pueda leerlos.

mcp-scout-football/
│
├── main.py # Servidor MCP principal
├── requirements.txt # Dependencias
├── .gitignore
│
├── data/
│ └── players.db # SQLite (se crea automático)
│
├── scripts/
│ └── scrape_and_load.py # Carga datos a SQLite
│
├── resources/
│ ├── defender_profiles.json
│ ├── metrics_dictionary.json
│ └── leagues_reference.json
│
├── models/
│ ├── **init**.py
│ └── schemas.py # Modelos Pydantic
│
├── db/
│ ├── **init**.py
│ ├── connection.py # Conexión SQLite
│ └── repository.py # CRUD jugadores
│
├── scrapers/
│ ├── **init**.py
│ ├── sofascore.py
│ └── transfermarkt.py
│
└── core/
├── **init**.py
├── filters.py
├── scoring.py
└── pipeline.py

PASO ÚNICO (cuando quieras actualizar datos):
$ python scripts/scrape_and_load.py --league laliga
→ Scrape Sofascore + Transfermarkt
→ Limpia y combina datos
→ Guarda en data/players.db

USO NORMAL (cada vez que el LLM llama):
Usuario → LLM → MCP Tool → Consulta SQLite → Respuesta
(1-2 segundos)
