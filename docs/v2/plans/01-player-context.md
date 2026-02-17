# Spec 1: Player Deep Context — Plan de Implementación

## Contexto

**Qué vamos a hacer:** Crear una nueva herramienta MCP llamada `get_player_context` que busca información en tiempo real sobre jugadores de fútbol usando Tavily (motor de búsqueda web).

**Por qué:** Las estadísticas solas no cuentan toda la historia. Un scout necesita saber:

- Cuánto vale el jugador y su situación contractual
- Si tiene historial de lesiones
- De dónde viene y sus traspasos anteriores
- Qué ha ganado (premios, títulos)
- Qué tipo de personalidad tiene (entrevistas, declaraciones)

**Cómo funciona:** El tool hace 5 búsquedas web categorizadas (mercado, lesiones, traspasos, premios, entrevistas) con 3 resultados cada una. Devuelve 15 resultados totales sin procesar — el LLM decide qué es relevante según lo que preguntó el usuario.

---

## Paso 1: Instalar Tavily

### 1.1 Instalar dependencia

```bash
pip install tavily-python
```

### 1.2 Actualizar requirements.txt

```bash
pip freeze > requirements.txt
```

---

## Paso 2: Configuración

### 2.1 Añadir API key a `.env`

**Archivo:** `.env`

```env
# Creado - API key de Tavily para búsqueda web
TAVILY_API_KEY=tvly-xxxxxxxxxxxxxx
```

> Consigue tu API key gratis en: https://tavily.com

### 2.2 Actualizar `config/settings.py`

**Archivo:** `config/settings.py`

```python
from os import getenv
from dotenv import load_dotenv

load_dotenv()

HOST = getenv("HOST", "0.0.0.0")
PORT = int(getenv("PORT", 8000))
APIKEY_SALT = getenv("APIKEY_SALT", "default-salt")

# Creado - Configuración de Tavily
TAVILY_API_KEY = getenv("TAVILY_API_KEY")
```

### 2.3 Exportar desde `config/__init__.py`

**Archivo:** `config/__init__.py`

```python
# Actualizado - Exportar TAVILY_API_KEY
from .settings import HOST, PORT, APIKEY_SALT, TAVILY_API_KEY
from .database import engine
from .leagues import LEAGUES_TO_LOAD

__all__ = [
    "HOST",
    "PORT",
    "APIKEY_SALT",
    "TAVILY_API_KEY",  # Creado
    "engine",
    "LEAGUES_TO_LOAD"
]
```

---

## Paso 3: Crear módulo `services/`

### 3.1 Estructura de carpetas

```
mcp-eleven/
├── services/              # Creado - Nuevo módulo
│   ├── __init__.py       # Creado
│   └── web_search.py     # Creado
```

### 3.2 Crear `services/__init__.py`

**Archivo:** `services/__init__.py`

```python
# Creado - Exportar funciones de búsqueda web
from .web_search import search_player_context

__all__ = ["search_player_context"]
```

### 3.3 Crear `services/web_search.py`

**Archivo:** `services/web_search.py`

```python
# Creado - Lógica de búsqueda web con Tavily
from tavily import TavilyClient
from config import TAVILY_API_KEY

# Inicializar cliente de Tavily
tavily_client = TavilyClient(api_key=TAVILY_API_KEY)

# 5 categorías de búsqueda para contexto de jugadores
PLAYER_SEARCH_CATEGORIES = {
    "market_and_contract": "market value salary contract 2025",
    "injuries": "injury history 2024 2025",
    "transfers": "transfer history career path",
    "awards": "awards trophies individual titles",
    "interviews_and_quotes": "interview quotes declarations 2025",
}


def search_player_context(player_name: str, team: str = None) -> dict:
    """
    Busca contexto web sobre un jugador en 5 categorías diferentes.

    Args:
        player_name: Nombre del jugador
        team: Equipo actual (opcional, mejora precisión)

    Returns:
        dict con player, team y context (5 categorías × 3 resultados = 15 totales)
    """
    # Construir query base
    base_query = f"{player_name} {team}" if team else player_name

    # Ejecutar búsquedas en todas las categorías
    context = {}
    for category, suffix in PLAYER_SEARCH_CATEGORIES.items():
        query = f"{base_query} {suffix}"
        result = tavily_client.search(query, max_results=3)
        context[category] = result.get("results", [])

    return {
        "player": player_name,
        "team": team,
        "context": context
    }
```

---

## Paso 4: Registrar herramienta MCP en `main.py`

### 4.1 Importar el servicio

**Archivo:** `main.py`

Añade después de las otras importaciones (línea ~12):

```python
# Actualizado - Importar búsqueda de contexto
from services import search_player_context
```

### 4.2 Crear el tool

Añade después de la función `search_players` (línea ~70):

```python
# Creado - Herramienta para obtener contexto profundo de jugadores
@mcp.tool
def get_player_context(player_name: str, team: str = None) -> dict:
    """
    Get deep context about a football player: market value, salary,
    injuries, transfers, awards, interviews and personal history.
    Uses web search to gather real-time information.

    Examples:
    - get_player_context("Erling Haaland", "Manchester City")
    - get_player_context("Kylian Mbappé")
    """
    try:
        return search_player_context(player_name, team)
    except Exception as e:
        return {"error": str(e)}
```

---

## Paso 5: Verificación

### 5.1 Reiniciar el servidor

```bash
python main.py
```

Deberías ver:

```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 5.2 Probar desde Claude Desktop

**Pregunta de ejemplo:**

> "Busca información sobre Erling Haaland del Manchester City"

**Comportamiento esperado:**

1. Claude Desktop llama a `get_player_context("Erling Haaland", "Manchester City")`
2. El tool devuelve 15 resultados web organizados en 5 categorías
3. Claude Desktop presenta la información de forma legible

**Categorías devueltas:**

- `market_and_contract`: Valor de mercado, salario, contrato
- `injuries`: Historial de lesiones
- `transfers`: Historia de traspasos
- `awards`: Premios y títulos
- `interviews_and_quotes`: Declaraciones recientes

### 5.3 Verificar logs

Si hay errores, revisa:

```bash
# Ver que Tavily esté configurado
python -c "from config import TAVILY_API_KEY; print(TAVILY_API_KEY)"

# Ver que el módulo se importe correctamente
python -c "from services import search_player_context; print(search_player_context)"
```

---

## Resumen de Cambios

| Acción          | Archivo                  | Descripción                      |
| --------------- | ------------------------ | -------------------------------- |
| **Creado**      | `services/__init__.py`   | Exporta funciones del módulo     |
| **Creado**      | `services/web_search.py` | Lógica de búsqueda con Tavily    |
| **Actualizado** | `config/settings.py`     | Añade `TAVILY_API_KEY`           |
| **Actualizado** | `config/__init__.py`     | Exporta `TAVILY_API_KEY`         |
| **Actualizado** | `main.py`                | Importa servicio y registra tool |
| **Actualizado** | `.env`                   | Añade API key de Tavily          |
| **Actualizado** | `requirements.txt`       | Añade `tavily-python`            |

---

## Próximos Pasos

Una vez implementado Spec 1, puedes continuar con:

- **Spec 2:** Team Context (reutiliza el módulo `services/` que acabas de crear)
- **Spec 3A:** Resources (ejemplos de queries)
- **Spec 3B:** Prompt (guía de presentación)
- **Spec 4:** Video Highlights (también reutiliza Tavily)

---

## Notas Técnicas

**¿Por qué Tavily?**

- No hay APIs públicas confiables para Transfermarkt, salarios o lesiones
- Tavily devuelve resultados limpios y estructurados
- Una sola dependencia cubre todas las necesidades de búsqueda web

**¿Por qué devolver datos crudos?**

- El LLM (Claude) es mejor procesando y filtrando información que cualquier lógica hardcodeada
- Cada pregunta del usuario necesita datos diferentes
- Más flexible y fácil de mantener

**¿Cuánto cuesta?**

- Tavily tiene plan gratuito: 1000 búsquedas/mes
- Este tool hace 5 búsquedas por llamada
- 200 consultas de jugadores gratis al mes
