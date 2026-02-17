# search_player_context — Explicación detallada

**Archivo:** `services/web_search.py`

---

## Qué hace

Esta función recibe el nombre de un jugador y devuelve información de internet organizada en 5 categorías. Es como si hicieras 5 búsquedas en Google, cada una enfocada en un tema diferente.

---

## Línea por línea

### Firma de la función

```python
def search_player_context(player_name: str, team: str = None) -> dict:
```

- `player_name: str` — Obligatorio. El nombre del jugador (ej: "Erling Haaland")
- `team: str = None` — Opcional. Si lo pasas, las búsquedas son más precisas (ej: "Manchester City")
- `-> dict` — Devuelve un diccionario con toda la info

---

### Construir la query base

```python
base_query = f"{player_name} {team}" if team else player_name
```

Si pasas equipo, la búsqueda será `"Erling Haaland Manchester City"`.
Si no, solo `"Erling Haaland"`.

Añadir el equipo ayuda a que Tavily no confunda jugadores con nombres comunes.

---

### El bucle principal

```python
context = {}
for category, suffix in PLAYER_SEARCH_CATEGORIES.items():
    result = tavily_client.search(f"{base_query} {suffix}", max_results=3)
    context[category] = result.get("results", [])
```

**Paso a paso:**

1. `context = {}` — Crea un diccionario vacío donde guardaremos los resultados

2. `for category, suffix in PLAYER_SEARCH_CATEGORIES.items()` — Recorre las 5 categorías. En cada vuelta del bucle tienes:
   - `category` = la clave (ej: `"market_and_contract"`)
   - `suffix` = las palabras clave (ej: `"market value salary contract 2025"`)

3. `tavily_client.search(...)` — Hace la búsqueda web. La query final queda así:
   - Vuelta 1: `"Erling Haaland Manchester City market value salary contract 2025"`
   - Vuelta 2: `"Erling Haaland Manchester City injury history 2024 2025"`
   - Vuelta 3: `"Erling Haaland Manchester City transfer history career path"`
   - Vuelta 4: `"Erling Haaland Manchester City awards trophies individual titles"`
   - Vuelta 5: `"Erling Haaland Manchester City interview quotes declarations 2025"`

4. `max_results=3` — Solo pide 3 resultados por categoría (5 × 3 = 15 totales)

5. `result.get("results", [])` — Saca la lista de resultados de la respuesta de Tavily. Si no hay resultados, devuelve lista vacía `[]`

6. `context[category] = ...` — Guarda los resultados en el diccionario bajo su categoría

---

### El return

```python
return {"player": player_name, "team": team, "context": context}
```

Devuelve un diccionario con:
- `player` — El nombre que buscaste
- `team` — El equipo (o None si no lo pasaste)
- `context` — Los 15 resultados organizados en 5 categorías

---

## Ejemplo de lo que devuelve

```json
{
  "player": "Erling Haaland",
  "team": "Manchester City",
  "context": {
    "market_and_contract": [
      {"title": "Haaland market value...", "url": "https://...", "content": "..."},
      {"title": "...", "url": "...", "content": "..."},
      {"title": "...", "url": "...", "content": "..."}
    ],
    "injuries": [
      {"title": "...", "url": "...", "content": "..."},
      ...
    ],
    "transfers": [...],
    "awards": [...],
    "interviews_and_quotes": [...]
  }
}
```

---

## Por qué se devuelve todo "crudo"

No filtramos ni procesamos los resultados de Tavily. ¿Por qué?

- El LLM (Claude) es mucho mejor decidiendo qué es relevante según la pregunta del usuario
- Si alguien pregunta "¿está lesionado Haaland?", Claude se enfocará en la categoría `injuries`
- Si alguien pregunta "¿cuánto vale?", se enfocará en `market_and_contract`
- Nosotros solo le damos toda la información, él decide qué mostrar
