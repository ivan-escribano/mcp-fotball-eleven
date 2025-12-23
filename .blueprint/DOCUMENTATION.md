# MCP Scout Football - Documentación Técnica

---

## 1. Descripción del Proyecto

### ¿Qué es?

Un **MCP Server especializado en scouting de fútbol** que transforma peticiones en lenguaje natural en búsquedas estructuradas de jugadores.

### Propósito

Permitir a usuarios escribir peticiones como:

> "Quiero un central zurdo, rápido, con buena salida de balón, de 28–32 años y unos 10M, máximo 5 jugadores en LaLiga"

y obtener automáticamente:

- **Los jugadores que mejor encajan** en ese perfil
- **Estadísticas relevantes** (pases progresivos, tackles, intercepciones, etc.)
- **Valor de mercado aproximado**
- **Explicación clara** de por qué encajan

### ¿Cómo funciona?

El MCP server actúa como **motor de análisis central**:

1. Consulta datos reales (Sofascore + Transfermarkt) vía ScraperFC
2. Filtra y procesa según el perfil solicitado
3. Calcula un score de encaje ajustado al rol
4. Devuelve candidatos ordenados y explicados

**El usuario no necesita**:

- Abrir múltiples webs
- Filtrar manualmente
- Cruzar estadísticas
- Entender métricas avanzadas

Basta describir lo que busca y el sistema hace el resto.

---

## 2. Flujo de Cliente (No Técnico)

### Paso a Paso

1. **Usuario escriba una solicitud en lenguaje natural**

   - Describe el tipo de jugador: posición, estilo, edad, rango de precio, liga

2. **LLM interpreta la intención**

   - Extrae requisitos clave (perfil deseado)
   - Decide llamar a la tool del MCP server

3. **MCP server realiza la búsqueda**

   - Consulta datos reales en Sofascore y Transfermarkt
   - Calcula qué jugadores encajan mejor

4. **MCP devuelve candidatos filtrados**

   - Lista reducida de jugadores ordenados
   - Con datos relevantes y score de encaje

5. **LLM presenta resultado al usuario**
   - Explica claramente por qué encajan
   - Traduce datos a lenguaje comprensible

### Esquema Mental ASCII - Flujo de Cliente

```
┌─────────────────────────────────────────────────────────────────────┐
│                        FLUJO DE CLIENTE                              │
└─────────────────────────────────────────────────────────────────────┘

    [1] USUARIO
    └─> "Quiero un central zurdo, rápido,
         28–32 años, ~10M, LaLiga"
        │
        ▼
    [2] LLM (INTERPRETACIÓN)
    └─> • Entiende intención
        • Extrae requisitos
        • Decide usar MCP tool
        │
        ▼
    [3] MCP TOOL: find_players_for_profile()
    └─> Recibe JSON estructurado
        {
          league: "laliga",
          profile_id: "ball_playing_cb",
          age_min: 28,
          age_max: 32,
          target_market_value_m: 10,
          max_results: 5
        }
        │
        ▼
    [4] MCP SERVER (BÚSQUEDA)
    └─> • Consulta Sofascore (stats)
        • Consulta Transfermarkt (edad, valor)
        • Calcula scores
        • Filtra por criterios
        │
        ▼
    [5] MCP DEVUELVE RESULTADO
    └─> JSON con top jugadores:
        {
          players: [
            {
              name: "Jugador X",
              team: "Sevilla FC",
              age: 30,
              market_value_m: 9.8,
              score: 0.91,
              stats: {...},
              reasons: [...]
            }
          ]
        }
        │
        ▼
    [6] LLM (PRESENTACIÓN)
    └─> • Lee resultado
        • Genera explicación clara
        • Adapta lenguaje al usuario
        │
        ▼
    [7] USUARIO VE
    └─> Informe final:
        • Top 5 centrales recomendados
        • Por qué encajan
        • Edad, equipo, valor, stats clave

```

---

## 3. Flujo Técnico

### Pipeline Interno

```
┌─────────────────────────────────────────────────────────────────────┐
│                      FLUJO TÉCNICO COMPLETO                         │
└─────────────────────────────────────────────────────────────────────┘

FASE 1: ENTRADA Y PREPARACIÓN
═══════════════════════════════

    Input JSON (del LLM):
    ┌──────────────────────────────┐
    │ {                            │
    │   "league": "laliga",        │
    │   "year": "2024",            │
    │   "profile_id": "ball_playing_cb",
    │   "age_min": 28,             │
    │   "age_max": 32,             │
    │   "preferred_foot": "left",  │
    │   "target_market_value_m": 10,
    │   "tolerance_pct": 30,       │
    │   "max_results": 5           │
    │ }                            │
    └──────────────────────────────┘
           │
           ▼

FASE 2: CARGA DE CONFIGURACIÓN
════════════════════════════════

    MCP Server carga Resources:
    ┌────────────────────────────────────┐
    │ defender_profiles.json             │
    │ └─> Pesos y métricas del perfil    │
    │     (ball_playing_cb):             │
    │     • prog_passes_p90: 0.4         │
    │     • pass_completion: 0.2         │
    │     • tackles_p90: 0.2             │
    │     • interceptions_p90: 0.2       │
    │                                    │
    │ metrics_dictionary.json            │
    │ └─> Definiciones de métricas       │
    └────────────────────────────────────┘
           │
           ▼

FASE 3: SCRAPING - SOFASCORE
══════════════════════════════

    ScraperFC.sofascore:
    ┌────────────────────────────────────┐
    │ scrape_player_league_stats(        │
    │   year="2024",                     │
    │   league="laliga",                 │
    │   accumulation="per90"             │
    │ )                                  │
    └────────────────────────────────────┘
           │
           ▼
    DataFrame Sofascore:
    ┌────────────────────────────────────┐
    │ name | team | tackles_p90 |        │
    │      |      | prog_passes | ...    │
    │ (500+ jugadores)                   │
    └────────────────────────────────────┘
           │
           ▼

FASE 4: FILTRO INICIAL
═══════════════════════

    Filters:
    • position == "CB"
    • minutes_played >= MIN_MINUTES
    • preferred_foot == "left"

    Resultado: ~40–80 jugadores
           │
           ▼

FASE 5: CÁLCULO DE SCORE
═════════════════════════

    Para cada jugador:
    ┌────────────────────────────────┐
    │ score = w1*norm(prog_passes) + │
    │         w2*norm(pass_compl) +  │
    │         w3*norm(tackles) +     │
    │         w4*norm(interceps)     │
    │ (pesos desde profile JSON)     │
    └────────────────────────────────┘

    Ordenar por score DESC
    Seleccionar top 30 (intermediate)
           │
           ▼

FASE 6: SCRAPING - TRANSFERMARKT
═════════════════════════════════════

    ScraperFC.transfermarkt:
    ┌────────────────────────────────────┐
    │ scrape_players(                    │
    │   year="2024",                     │
    │   league="laliga"                  │
    │ )                                  │
    └────────────────────────────────────┘
           │
           ▼
    DataFrame Transfermarkt:
    ┌────────────────────────────────────┐
    │ name | team | age | market_value   │
    │      |      |     | position | ... │
    │ (todos los jugadores de la liga)   │
    └────────────────────────────────────┘
           │
           ▼

FASE 7: MERGE DATASETS
═══════════════════════

    Inner Join: Sofascore + Transfermarkt
    ON: (name, team)

    Resultado: PlayerSnapshot enriquecido
    ┌────────────────────────────────────┐
    │ PlayerSnapshot:                    │
    │ • name, team                       │
    │ • age, market_value_m              │
    │ • stats (tackles, passes, etc)     │
    │ • score                            │
    └────────────────────────────────────┘
           │
           ▼

FASE 8: FILTROS FINALES
════════════════════════

    Filters:
    • age_min <= age <= age_max
    • target_mv * (1-tol) <= mv <= target_mv * (1+tol)

    Reordenar por score DESC
    Seleccionar max_results (5)
           │
           ▼

FASE 9: GENERACIÓN DE OUTPUT
══════════════════════════════

    Para cada jugador final:
    • Calcular "reasons" (por qué encaja)
    • Compilar stats relevantes
    • Crear response JSON

    Output JSON:
    ┌──────────────────────────────────┐
    │ {                                │
    │   "league": "laliga",            │
    │   "search_criteria": {...},      │
    │   "players": [                   │
    │     {                            │
    │       "name": "Jugador X",       │
    │       "team": "Sevilla FC",      │
    │       "age": 30,                 │
    │       "market_value_m": 9.8,     │
    │       "score": 0.91,             │
    │       "stats": {                 │
    │         "tackles_p90": 3.2,      │
    │         "prog_passes": 5.1,      │
    │         ...                      │
    │       },                         │
    │       "reasons": [               │
    │         "Excelente en..."        │
    │         "Score de encaje..."     │
    │       ]                          │
    │     }                            │
    │   ]                              │
    │ }                                │
    └──────────────────────────────────┘
           │
           ▼

RETORNO AL LLM
═══════════════

    LLM recibe JSON
    ↓
    Genera respuesta explicada
    ↓
    Usuario ve informe final

```

---

## 4. Librerías Necesarias

### 4.1. **ScraperFC** - Datos Reales

Librería para scraping de datos futbolísticos.

#### Sofascore (Rendimiento)

```python
from ScraperFC.sofascore import Sofascore

# Obtener stats por 90 minutos de todos los jugadores de una liga
scrape_player_league_stats(
    year=2024,
    league="laliga",
    accumulation="per90",
    selected_positions=["CB"]
)
```

**Datos que aporta**:

- `tackles_p90`: Despejes por 90 min
- `prog_passes_p90`: Pases progresivos por 90 min
- `pass_completion_pct`: Precisión de pase
- `interceptions_p90`: Intercepciones por 90 min
- `aerial_duels_won_pct`: Duelos aéreos ganados
- Y +50 métricas más

#### Transfermarkt (Mercado)

```python
from ScraperFC.transfermarkt import Transfermarkt

# Obtener datos económicos y personales
scrape_players(
    year=2024,
    league="laliga"
)
```

**Datos que aporta**:

- `name`: Nombre del jugador
- `team`: Equipo actual
- `age`: Edad
- `market_value_m`: Valor de mercado (millones €)
- `position`: Posición
- `foot`: Pie predominante (left/right)
- `contract_expiry`: Fecha de expiración

### 4.2. **Pandas** - Procesamiento de Datos

```python
import pandas as pd

# Operaciones clave:
df = pd.DataFrame(...)
df_filtered = df[df['position'] == 'CB']
df_merged = pd.merge(df_sofascore, df_transfermarkt, on=['name', 'team'])
df_sorted = df_merged.sort_values('score', ascending=False)
```

### 4.3. **Pydantic** (Opcional) - Validación de Esquemas

```python
from pydantic import BaseModel
from typing import List

class PlayerSnapshot(BaseModel):
    name: str
    team: str
    age: int
    market_value_m: float
    score: float
    stats: dict
    reasons: List[str]

class ScoutingResponse(BaseModel):
    league: str
    players: List[PlayerSnapshot]
```

### 4.4. **FastMCP** - Exposición del MCP Server

```python
from fastmcp import FastMCP

mcp = FastMCP("Scout Football")

@mcp.tool
def find_players_for_profile(input_json: dict) -> dict:
    """Tool principal del servidor"""
    pass
```

### 4.5. **JSON** - Configuración y Output

```python
import json

# Cargar perfiles de defensa
with open('resources/defender_profiles.json', 'r') as f:
    profiles = json.load(f)

# Cargar diccionario de métricas
with open('resources/metrics_dictionary.json', 'r') as f:
    metrics = json.load(f)
```

---

## 5. FastMCP: Tools, Resources y Prompts

### 5.1. Tools

#### **Tool Principal: `find_players_for_profile`**

**Propósito**: Buscar jugadores que encajan en un perfil específico.

**Input Schema**:

```json
{
  "league": {
    "type": "string",
    "description": "Liga objetivo (laliga, premierleague, serieA, bundl, ligue1)",
    "enum": ["laliga", "premierleague", "serieA", "bundlesliga", "ligue1"]
  },
  "year": {
    "type": "integer",
    "description": "Temporada (ej: 2024)",
    "default": 2024
  },
  "profile_id": {
    "type": "string",
    "description": "ID del perfil de defensa (ball_playing_cb, aggressive_cb, aerialWinner_cb, etc.)",
    "enum": [
      "ball_playing_cb",
      "aggressive_cb",
      "aerial_winner_cb",
      "balanced_cb"
    ]
  },
  "age_min": {
    "type": "integer",
    "description": "Edad mínima",
    "default": 20
  },
  "age_max": {
    "type": "integer",
    "description": "Edad máxima",
    "default": 35
  },
  "preferred_foot": {
    "type": "string",
    "description": "Pie predominante (left, right, both)",
    "enum": ["left", "right", "both"],
    "default": "both"
  },
  "target_market_value_m": {
    "type": "number",
    "description": "Valor de mercado objetivo en millones €",
    "default": 15
  },
  "market_value_tolerance_pct": {
    "type": "integer",
    "description": "Tolerancia de precio en porcentaje (±)",
    "default": 30
  },
  "max_results": {
    "type": "integer",
    "description": "Máximo de jugadores a retornar",
    "default": 5,
    "minimum": 1,
    "maximum": 20
  }
}
```

**Output Schema**:

```json
{
  "league": "laliga",
  "search_criteria": {
    "profile": "ball_playing_cb",
    "age_range": "28-32",
    "price_range": "7-13M€",
    "foot": "left"
  },
  "total_candidates": 42,
  "results_returned": 5,
  "players": [
    {
      "rank": 1,
      "name": "Jugador X",
      "team": "Sevilla FC",
      "age": 30,
      "market_value_m": 9.8,
      "position": "CB",
      "foot": "left",
      "score": 0.91,
      "stats": {
        "tackles_p90": 3.2,
        "prog_passes_p90": 5.1,
        "pass_completion_pct": 87.5,
        "interceptions_p90": 2.1,
        "aerial_duels_won_pct": 64.3,
        "minutes_played": 2520
      },
      "reasons": [
        "Excelente distribución de balón (87.5% precisión)",
        "Alto volumen de pases progresivos (5.1 p90)",
        "Defensa sólida (3.2 tackles p90)",
        "Score de encaje: 0.91/1.0"
      ]
    }
  ]
}
```

---

### 5.2. Resources

Resources son archivos estáticos que el LLM puede leer para entender mejor qué perfiles existen.

#### **Resource 1: `defender_profiles.json`**

Define tipos de defensa y pesos de las métricas para cada perfil.

```json
{
  "ball_playing_cb": {
    "name": "Central con Salida de Balón",
    "description": "Defensa especializado en construcción desde atrás, buena precisión de pase",
    "metrics": {
      "prog_passes_p90": 0.4,
      "pass_completion_pct": 0.2,
      "tackles_p90": 0.2,
      "interceptions_p90": 0.2
    }
  },
  "aggressive_cb": {
    "name": "Central Agresivo",
    "description": "Defensa que presiona alto, muchos despejes e intercepciones",
    "metrics": {
      "tackles_p90": 0.35,
      "interceptions_p90": 0.35,
      "aerial_duels_won_pct": 0.2,
      "pass_completion_pct": 0.1
    }
  },
  "aerial_winner_cb": {
    "name": "Central Ganador Aéreo",
    "description": "Especialista en duelos aéreos, fuerte defensivamente",
    "metrics": {
      "aerial_duels_won_pct": 0.4,
      "tackles_p90": 0.3,
      "interceptions_p90": 0.2,
      "pass_completion_pct": 0.1
    }
  },
  "balanced_cb": {
    "name": "Central Equilibrado",
    "description": "Defensa versátil con buenas prestaciones en todas las áreas",
    "metrics": {
      "tackles_p90": 0.25,
      "interceptions_p90": 0.25,
      "prog_passes_p90": 0.25,
      "pass_completion_pct": 0.25
    }
  }
}
```

#### **Resource 2: `metrics_dictionary.json`**

Diccionario que explica cada métrica para el LLM.

```json
{
  "tackles_p90": {
    "name": "Despejes por 90 minutos",
    "description": "Número de despejes realizados en 90 minutos de juego",
    "importance_for_defenders": "Alta",
    "range": "0-8"
  },
  "prog_passes_p90": {
    "name": "Pases Progresivos por 90 minutos",
    "description": "Pases que avanzan el balón hacia el área contraria en 90 minutos",
    "importance_for_defenders": "Media",
    "range": "0-10"
  },
  "pass_completion_pct": {
    "name": "Precisión de Pase (%)",
    "description": "Porcentaje de pases completados exitosamente",
    "importance_for_defenders": "Media",
    "range": "60-95"
  },
  "interceptions_p90": {
    "name": "Intercepciones por 90 minutos",
    "description": "Número de balones interceptados en 90 minutos",
    "importance_for_defenders": "Alta",
    "range": "0-6"
  },
  "aerial_duels_won_pct": {
    "name": "Duelos Aéreos Ganados (%)",
    "description": "Porcentaje de duelos aéreos ganados",
    "importance_for_defenders": "Alta",
    "range": "40-80"
  }
}
```

#### **Resource 3: `leagues_reference.json`**

Referencia de ligas disponibles.

```json
{
  "laliga": {
    "name": "LaLiga (España)",
    "country": "Spain",
    "available_seasons": [2020, 2021, 2022, 2023, 2024],
    "total_teams": 20
  },
  "premierleague": {
    "name": "Premier League (Inglaterra)",
    "country": "England",
    "available_seasons": [2020, 2021, 2022, 2023, 2024],
    "total_teams": 20
  },
  "serieA": {
    "name": "Serie A (Italia)",
    "country": "Italy",
    "available_seasons": [2020, 2021, 2022, 2023, 2024],
    "total_teams": 20
  },
  "bundlesliga": {
    "name": "Bundesliga (Alemania)",
    "country": "Germany",
    "available_seasons": [2020, 2021, 2022, 2023, 2024],
    "total_teams": 18
  },
  "ligue1": {
    "name": "Ligue 1 (Francia)",
    "country": "France",
    "available_seasons": [2020, 2021, 2022, 2023, 2024],
    "total_teams": 20
  }
}
```

---

### 5.3. Prompts

#### **System Prompt para el Agente LLM**

Instrucciones que recibe el LLM para usar correctamente el MCP server.

````
## Role
Eres un asistente especializado en scouting de fútbol con acceso a herramientas para análisis de rendimiento y mercado.

## Capabilities
- Acceso a una herramienta: find_players_for_profile()
- Acceso a resources: defender_profiles.json, metrics_dictionary.json, leagues_reference.json
- Puedes consultar datos reales de rendimiento (Sofascore) y valor de mercado (Transfermarkt)

## Instructions for User Requests

### Cuando el usuario describe un perfil de jugador:

1. **Identifica los requisitos clave:**
   - Posición (siempre son defensas centrales para MVP)
   - Estilo o rol (ball-playing, aggressive, aerial winner, balanced)
   - Rango de edad (edad mínima y máxima)
   - Valor de mercado objetivo
   - Liga preferida
   - Pie dominante (opcional)
   - Máximo número de resultados

2. **Mapea el perfil a un profile_id:**
   Consulta defender_profiles.json para encontrar el perfil más cercano:
   - "ball_playing_cb" → "buen pase", "distribución", "salida de balón"
   - "aggressive_cb" → "agresivo", "tackle", "presión"
   - "aerial_winner_cb" → "aéreo", "cabezazo", "duelos aéreos"
   - "balanced_cb" → "versátil", "equilibrado", "completo"

3. **Construye el input JSON:**
   ```json
   {
     "league": "...",
     "year": 2024,
     "profile_id": "...",
     "age_min": ...,
     "age_max": ...,
     "preferred_foot": "...",
     "target_market_value_m": ...,
     "market_value_tolerance_pct": 30,
     "max_results": ...
   }
````

4. **Llama a la tool:**
   Siempre usa find_players_for_profile() cuando el usuario pida búsquedas de jugadores.
   No intentes inventar datos; depende del MCP server.

5. **Procesa el resultado:**
   - Lee la respuesta JSON
   - Extrae stats clave
   - Interpreta el score
   - Genera una explicación clara en lenguaje natural

### Formato de respuesta final:

Presenta los jugadores así:

```
# Top [N] Centrales Recomendados

## 1. Nombre del Jugador | Equipo | Edad
- **Valor de mercado:** X.XM€
- **Score de encaje:** 0.XX/1.00
- **Estadísticas clave:**
  - Tackles p90: X.X
  - Pases progresivos: X.X
  - Precisión de pase: XX%
- **Por qué encaja:**
  - Razón 1
  - Razón 2
  - Razón 3
```

## Important Rules

- Si el usuario no especifica liga, pregunta cuál prefiere
- Si no especifica rango de edad, usa default: 20-35 años
- Si no especifica presupuesto, usa default: ~15M€ (±30%)
- Siempre devuelve entre 3-5 jugadores como máximo para claridad
- Si el servidor retorna 0 resultados, explica por qué (criterios muy restrictivos)

```

#### **Prompt para Interpretación de Entrada del Usuario**

```

Cuando el usuario escriba una solicitud como:

"Quiero un central zurdo, rápido, con buena salida de balón,
de 28–32 años y unos 10M en LaLiga, máximo 5 jugadores"

Extrae automáticamente:

- "central" → position = "CB" (ya fijo para MVP)
- "zurdo" → preferred_foot = "left"
- "rápido" → velocidad (métrica considerada en algunos perfiles)
- "buena salida de balón" → profile_id = "ball_playing_cb"
- "28–32 años" → age_min = 28, age_max = 32
- "~10M" → target_market_value_m = 10
- "LaLiga" → league = "laliga"
- "máximo 5 jugadores" → max_results = 5

Si algún parámetro no está claro, pide aclaración.

```

---

## Resumen de Integración

| Componente | Ubicación | Propósito |
|-----------|-----------|----------|
| **Tool** | MCP Server | `find_players_for_profile()` busca y filtra jugadores |
| **Resources** | MCP Server | Perfiles, métricas, referencias de ligas |
| **System Prompt** | Cliente LLM | Guía al LLM en interpretación y uso de tools |
| **User Prompts** | Cliente LLM | Instrucciones para mapear lenguaje natural a JSON |
| **Libraries** | Backend | ScraperFC, Pandas, Pydantic, FastMCP |

---

## Próximos Pasos

1. ✅ Documentación (Este archivo)
2. ⏳ Implementar estructura de carpetas
3. ⏳ Crear modelos Pydantic
4. ⏳ Implementar tool `find_players_for_profile()`
5. ⏳ Crear archivo `main.py` con FastMCP
6. ⏳ Agregar recursos JSON
7. ⏳ Testear con datos reales
```
