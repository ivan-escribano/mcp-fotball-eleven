# Spec 2: Team Context — Plan de Implementación

## Contexto

**Qué vamos a hacer:** Crear una herramienta MCP llamada `get_team_context` que busca info en tiempo real sobre un equipo usando Tavily.

**Por qué:** Recomendar un jugador sin entender el equipo que lo busca no tiene sentido. Un scout necesita saber formación, estilo, fichajes y forma actual.

**Cómo funciona:** 4 búsquedas web categorizadas con Tavily. Devuelve todo crudo, el LLM presenta lo relevante.

**Sin dependencias nuevas.** Reutiliza Tavily de Spec 1, misma estructura.

---

## Paso 1: Actualizar `services/web_search/config.py`

Añadir categorías de búsqueda para equipos:

```python
# Created - Team search categories
TEAM_SEARCH_CATEGORIES = {
    "tactics_and_formation": {
        "suffix": "formation tactics playing style",
        "time_range": "month",
    },
    "coach_profile": {
        "suffix": "coach manager style philosophy",
        "time_range": "year",
    },
    "transfer_targets": {
        "suffix": "transfer targets rumours signings",
        "topic": "news",
    },
    "league_position": {
        "suffix": "standings results recent form",
        "topic": "news",
    },
}
```

---

## Paso 2: Añadir `search_team_context` en `services/web_search/search.py`

Mismo patrón que `search_player_context`:

```python
def search_team_context(team: str, league: str = None) -> dict:
    base_query = f"{team} {league}" if league else team

    context = {}
    for category, cat_config in TEAM_SEARCH_CATEGORIES.items():
        search_params = {
            "query": f"{base_query} {cat_config['suffix']}",
            "max_results": 3,
        }

        if "topic" in cat_config:
            search_params["topic"] = cat_config["topic"]
        if "time_range" in cat_config:
            search_params["time_range"] = cat_config["time_range"]

        result = tavily_client.search(**search_params)
        context[category] = result.get("results", [])

    return {"team": team, "league": league, "context": context}
```

---

## Paso 3: Añadir prompt en `services/web_search/prompts.py`

```python
TEAM_CONTEXT_PROMPT = """
Get tactical, market and performance context for a football team.
Uses web search to gather real-time information.

Examples:
- get_team_context("Real Madrid", "La Liga")
- get_team_context("Manchester City")

Present results as a clear team analysis report:

1) FORMATION & TACTICS: primary formation, playing style, defensive approach.
2) COACH: name, philosophy, strengths/weaknesses.
3) TRANSFERS: recent signings, rumoured targets, positions being reinforced.
4) CURRENT FORM: league position, recent results, goals scored vs conceded.
5) SUMMARY: 2-3 sentences — team strengths, weaknesses, and what type of player would improve them.

Rules: cite source URLs as [Source](url). If no data found, write 'No data available'.
Use tables and bullets, not long paragraphs.
"""
```

---

## Paso 4: Exportar desde `services/`

Actualizar `services/web_search/__init__.py` y `services/__init__.py` para exportar `search_team_context` y `TEAM_CONTEXT_PROMPT`.

---

## Paso 5: Registrar tool en `main.py`

```python
@mcp.tool(description=TEAM_CONTEXT_PROMPT)
def get_team_context(team: str, league: str = None) -> dict:
    try:
        return {
            "instructions": TEAM_CONTEXT_PROMPT,
            **search_team_context(team, league),
        }
    except Exception as e:
        return {"error": str(e)}
```

---

## Resumen de Cambios

| Acción      | Archivo                           | Descripción                      |
| ----------- | --------------------------------- | -------------------------------- |
| **Updated** | `services/web_search/config.py`   | Añade `TEAM_SEARCH_CATEGORIES`   |
| **Updated** | `services/web_search/search.py`   | Añade `search_team_context`      |
| **Updated** | `services/web_search/prompts.py`  | Añade `TEAM_CONTEXT_PROMPT`      |
| **Updated** | `services/web_search/__init__.py` | Exporta nuevas funciones         |
| **Updated** | `services/__init__.py`            | Exporta nuevas funciones         |
| **Updated** | `main.py`                         | Registra `get_team_context`      |

No se toca `db/database.py`. Solo web search.
