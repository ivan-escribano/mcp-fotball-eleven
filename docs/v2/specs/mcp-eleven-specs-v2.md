# MCP Eleven v2 — Feature Specs

> De buscador de stats a herramienta de scouting profesional.

---

## Tabla de contenidos

- [Spec 1: Player Deep Context](#spec-1-player-deep-context)
- [Spec 2: Team Context](#spec-2-team-context)
- [Spec 3A: Resources — Ejemplos de queries y glosario](#spec-3a-resources--ejemplos-de-queries-y-glosario)
- [Spec 3B: Prompt — Presentación de resultados](#spec-3b-prompt--presentación-de-resultados)
- [Spec 4: Video Highlights](#spec-4-video-highlights)

---

## Spec 1: Player Deep Context

### 1. Contexto general y descripción

Nuevo MCP tool `get_player_context` que busca información en tiempo real sobre cualquier jugador de fútbol profesional usando Tavily como motor de búsqueda web.

El problema que resuelve es que las stats solas no cuentan la historia completa de un jugador. Un scout necesita saber cuánto vale, si está lesionado, de dónde viene, qué ha ganado y qué tipo de personalidad tiene antes de tomar una decisión.

El tool ejecuta 5 búsquedas web categorizadas (mercado, lesiones, traspasos, premios, entrevistas) con 3 resultados cada una. Devuelve todo crudo sin parsear — el LLM cliente decide qué es relevante según lo que preguntó el usuario.

Tavily porque no existen APIs públicas fiables para Transfermarkt, salarios ni lesiones. Una sola dependencia cubre todo.

Este tool crea el módulo `services/` que Spec 2 (Team Context) reutilizará con búsquedas diferentes.

### 2. Snippets esenciales

**Lógica core del servicio:**

```python
# services/web_search.py

from tavily import TavilyClient
from config import TAVILY_API_KEY

tavily_client = TavilyClient(api_key=TAVILY_API_KEY)

PLAYER_SEARCH_CATEGORIES = {
    "market_and_contract": "market value salary contract 2025",
    "injuries": "injury history 2024 2025",
    "transfers": "transfer history career path",
    "awards": "awards trophies individual titles",
    "interviews_and_quotes": "interview quotes declarations 2025",
}


def search_player_context(player_name: str, team: str = None) -> dict:
    base_query = f"{player_name} {team}" if team else player_name

    context = {}
    for category, suffix in PLAYER_SEARCH_CATEGORIES.items():
        result = tavily_client.search(f"{base_query} {suffix}", max_results=3)
        context[category] = result.get("results", [])

    return {"player": player_name, "team": team, "context": context}
```

**Tool registration:**

```python
# main.py

@mcp.tool()
def get_player_context(player_name: str, team: str = None) -> dict:
    """
    Get deep context about a football player: market value, salary,
    injuries, transfers, awards, interviews and personal history.
    Uses web search to gather real-time information.
    """
    return search_player_context(player_name, team)
```

### 3. Resumen

**Qué hay que hacer:** instalar `tavily-python`, añadir `TAVILY_API_KEY` a config y `.env`, crear `services/web_search.py` con la lógica de búsqueda, registrar el tool en `main.py`.

**Estructura nueva:** carpeta `services/` con `__init__.py` y `web_search.py`.

**Return:** JSON con `player`, `team`, y `context` (5 categorías × 3 resultados = 15 resultados web crudos de Tavily sin transformar).

---

## Spec 2: Team Context

### 1. Contexto general y descripción

Nuevo MCP tool `get_team_context` que combina dos fuentes: datos agregados de tu propia DB (stats de jugadores que ya tienes) + búsqueda web con Tavily para contexto táctico y de mercado.

El problema que resuelve es que recomendar un jugador sin entender el equipo que lo busca no tiene sentido. Un scout necesita saber qué formación usa el entrenador, qué estilo de juego tiene, qué posiciones necesitan refuerzo y cómo rinde el equipo actualmente.

La parte interna es gratuita y rápida: agregas goals, assists, minutes de todos los jugadores del equipo en tu DB y sacas top performers. La parte externa (Tavily) cubre lo que no puedes calcular: formación, estilo del entrenador, fichajes rumoreados, posición en liga.

Reutiliza `services/web_search.py` creado en Spec 1, añadiendo una nueva función.

### 2. Snippets esenciales

**Agregación desde la DB:**

```python
# db/database.py (nueva función)

def get_team_stats(team: str, league: str = None, season: str = "25/26") -> dict:
    with Session(engine) as session:
        query = select(PlayerStats).where(PlayerStats.team.contains(team))

        if league:
            query = query.where(PlayerStats.league == league)
        query = query.where(PlayerStats.season == season)

        players = session.exec(query).all()

        if not players:
            return {"team": team, "found": False}

        return {
            "team": team,
            "league": league,
            "season": season,
            "squad_size": len(players),
            "total_goals": sum(p.goals or 0 for p in players),
            "total_assists": sum(p.assists or 0 for p in players),
            "top_scorer": max(players, key=lambda p: p.goals or 0).player,
            "top_assister": max(players, key=lambda p: p.assists or 0).player,
            "most_minutes": max(players, key=lambda p: p.minutes_played or 0).player,
        }
```

**Categorías de búsqueda web para equipos:**

```python
# services/web_search.py (nueva función)

TEAM_SEARCH_CATEGORIES = {
    "tactics_and_formation": "formation tactics playing style 2025",
    "coach_profile": "coach manager style philosophy",
    "transfer_targets": "transfer targets rumours signings 2025",
    "league_position": "standings results recent form 2025",
}


def search_team_context(team: str, league: str = None) -> dict:
    base_query = f"{team} {league}" if league else team

    context = {}
    for category, suffix in TEAM_SEARCH_CATEGORIES.items():
        result = tavily_client.search(f"{base_query} {suffix}", max_results=3)
        context[category] = result.get("results", [])

    return context
```

**Tool que combina ambas fuentes:**

```python
# main.py

@mcp.tool()
def get_team_context(team: str, league: str = None, season: str = "25/26") -> dict:
    """
    Get tactical, market and performance context for a football team.
    Combines internal stats from the database with real-time web search
    for formation, coach style, transfer targets and league position.
    """
    internal = get_team_stats(team, league, season)
    external = search_team_context(team, league)

    return {
        "team": team,
        "league": league,
        "season": season,
        "squad_overview": internal,
        "web_context": external,
    }
```

### 3. Resumen

**Qué hay que hacer:** nueva función `get_team_stats` en `db/database.py` para agregar stats del equipo desde la DB, nueva función `search_team_context` en `services/web_search.py` con 4 categorías de búsqueda Tavily, y registrar el tool en `main.py` combinando ambas fuentes.

**Dos fuentes, un tool:** datos internos (squad size, goles totales, top performers) + datos externos (formación, estilo entrenador, fichajes, posición en liga). 4 categorías web × 3 resultados = 12 resultados de Tavily + agregados de DB.

**Sin dependencias nuevas:** reutiliza Tavily de Spec 1 y la DB que ya tienes.

---

## Spec 3A: Resources — Ejemplos de queries y glosario

### 1. Contexto general y descripción

Crear resources estáticos que el cliente MCP pueda consultar para saber cómo usar `search_players` correctamente.

Todo en `main.py`, sin archivos nuevos ni dependencias. El cliente descubre los resources vía `resources/list` y lee los que necesita vía `resources/read`.

### 2. Snippets esenciales

**Ejemplos de queries por perfil de jugador:**

```python
@mcp.resource("mcp-eleven://examples/clinical-striker")
def example_clinical_striker() -> dict:
    """Example query to find a clinical striker."""
    return {
        "description": "Clinical striker with high conversion rate",
        "tool": "search_players",
        "input": {
            "league": "La Liga",
            "position": "Forward",
            "min_goals": 10,
            "min_goal_conversion_percentage": 18
        }
    }


@mcp.resource("mcp-eleven://examples/creative-midfielder")
def example_creative_midfielder() -> dict:
    """Example query to find a creative midfielder."""
    return {
        "description": "Creative midfielder with vision and goal threat",
        "tool": "search_players",
        "input": {
            "league": "Premier League",
            "position": "Midfielder",
            "min_assists": 8,
            "min_key_passes_per_avg": 2.0,
            "min_goals": 5
        }
    }


@mcp.resource("mcp-eleven://examples/ball-playing-cb")
def example_ball_playing_cb() -> dict:
    """Example query to find a ball-playing centre-back."""
    return {
        "description": "Centre-back comfortable with the ball",
        "tool": "search_players",
        "input": {
            "league": "Bundesliga",
            "position": "Defender",
            "min_accurate_passes_percentage": 88,
            "min_minutes_played": 1500
        }
    }


@mcp.resource("mcp-eleven://examples/pressing-forward")
def example_pressing_forward() -> dict:
    """Example query to find a high-pressing forward."""
    return {
        "description": "Forward who presses and recovers possession",
        "tool": "search_players",
        "input": {
            "position": "Forward",
            "min_ball_recoveries": 3.0,
            "min_duels_won_percentage": 50
        }
    }
```

**Glosario de stats:**

```python
@mcp.resource("mcp-eleven://stats-glossary")
def stats_glossary() -> dict:
    """What each stat means and what values are considered good."""
    return {
        "xG": {
            "name": "Expected Goals",
            "description": "Probability that a shot becomes a goal based on shot characteristics",
            "good_value": "> 0.15 per shot"
        },
        "goal_conversion_percentage": {
            "name": "Goal Conversion Rate",
            "description": "Percentage of shots that result in goals",
            "good_value": "> 18% is clinical, > 25% is elite"
        },
        "key_passes_per_avg": {
            "name": "Key Passes per Game",
            "description": "Passes that directly lead to a shot",
            "good_value": "> 2.0 is creative, > 3.0 is elite"
        },
        "accurate_passes_percentage": {
            "name": "Pass Accuracy",
            "description": "Percentage of completed passes",
            "good_value": "> 85% for midfielders, > 90% for CBs"
        },
        "duels_won_percentage": {
            "name": "Duels Won",
            "description": "Percentage of 1v1 duels won (aerial + ground)",
            "good_value": "> 55% is strong, > 65% is dominant"
        }
    }
```

**Ligas disponibles:**

```python
@mcp.resource("mcp-eleven://available-leagues")
def available_leagues() -> dict:
    """Leagues available in the database with their exact names."""
    return {
        "leagues": [
            "La Liga", "Premier League", "Serie A",
            "Bundesliga", "Ligue 1", "Primeira Liga",
            "Eredivisie", "Super Lig", "Championship",
            # ... resto de LEAGUES_TO_LOAD
        ],
        "current_season": "25/26",
        "note": "Use exact league names when filtering"
    }
```

### 3. Resumen

**Qué hay que hacer:** añadir ~6-7 decoradores `@mcp.resource()` en `main.py`.

**Sin archivos nuevos ni dependencias.** El cliente consulta `resources/list` → ve todos los resources → lee los que necesita con `resources/read`.

---

## Spec 3B: Prompt — Presentación de resultados

### 1. Contexto general y descripción

Crear un prompt MCP que guíe al cliente sobre cómo presentar los datos de cualquier tool de MCP Eleven como un informe de scouting profesional.

Compatible con Claude Desktop (botón "+") y cualquier cliente que soporte MCP Prompts.

### 2. Snippets esenciales

```python
@mcp.prompt()
def scouting_report() -> str:
    """How to present MCP Eleven data as a professional scouting report."""
    return (
        "You are a professional football scout presenting data from MCP Eleven.\n\n"
        "For search_players results:\n"
        "1) One-line summary: total results found and filters applied.\n"
        "2) Table with the most relevant stats for the query context.\n"
        "3) Highlight 1-2 standout players with brief reasoning.\n"
        "4) If fewer than 3 results, suggest broadening filters.\n\n"
        "For get_player_context results:\n"
        "1) Lead with market value and contract situation.\n"
        "2) Injury history as a risk assessment (low/medium/high).\n"
        "3) Transfer history as career trajectory.\n"
        "4) Include a notable quote that reveals mentality.\n\n"
        "For get_team_context results:\n"
        "1) Formation and tactical style first.\n"
        "2) Squad strengths and weaknesses from internal stats.\n"
        "3) Transfer targets and market activity.\n"
        "4) Current form and league position."
    )
```

### 3. Resumen

**Qué hay que hacer:** añadir un solo `@mcp.prompt()` en `main.py`.

**Cubre los 3 tools principales:** `search_players`, `get_player_context`, `get_team_context`.

**Uso:** el cliente lo consulta vía `prompts/get` con nombre `scouting_report` y usa las instrucciones como system context al llamar a los tools.

---

## Spec 4: Video Highlights

### 1. Contexto general y descripción

Tool que busca 5-10 videos de highlights de un jugador usando Tavily. Devuelve lista de URLs con título y fuente. El cliente decide cómo presentarlos.

Reutiliza Tavily de Spec 1 con `include_domains` para filtrar solo plataformas de video.

### 2. Snippets esenciales

**Lógica de búsqueda:**

```python
# services/web_search.py (nueva función)

def search_player_highlights(player_name: str, team: str = None, max_results: int = 5) -> dict:
    base_query = f"{player_name} {team}" if team else player_name
    query = f"{base_query} highlights goals skills 2024 2025"

    result = tavily_client.search(
        query=query,
        max_results=max_results,
        include_domains=[
            "youtube.com",
            "instagram.com",
            "tiktok.com",
            "facebook.com",
            "dailymotion.com",
        ],
    )

    return {
        "player": player_name,
        "team": team,
        "videos": [
            {
                "title": r.get("title", ""),
                "url": r.get("url", ""),
                "source": r.get("url", "").split("/")[2] if r.get("url") else "",
            }
            for r in result.get("results", [])
        ],
    }
```

**Tool registration:**

```python
# main.py

@mcp.tool()
def get_player_highlights(player_name: str, team: str = None, max_results: int = 5) -> dict:
    """Get 5-10 highlight videos of a football player from YouTube, Instagram, TikTok and other sources."""
    return search_player_highlights(player_name, team, max_results)
```

### 3. Resumen

**Qué hay que hacer:** una función nueva en `services/web_search.py` y un tool nuevo en `main.py`.

**Sin dependencias nuevas:** reutiliza Tavily de Spec 1.

**Return:** lista plana de videos con título, URL y fuente. `include_domains` filtra solo plataformas de video.
