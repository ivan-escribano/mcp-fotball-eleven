Hay que mejorar donde buscar:

- Capology el mejor sitio para salario
- Tarnsfermarkt para traspasos y valor de mercado
- Periódicos deportivos para lesiones, premios y entrevistas
- Wikipedia para datos generales (fecha de nacimiento, nacionalidad, posición)
- Redes sociales para personalidad (Twitter, Instagram)

PLAYER_SEARCH_CATEGORIES = {
"market_and_contract": "market value salary contract 2025",
"injuries": "injury history 2024 2025",
"transfers": "transfer history career path",
"awards": "awards trophies individual titles",
"interviews_and_quotes": "interview quotes declarations 2025",
}

lo de 2024 y 2025 no es accurate, hay que quitarlo ya que ahora mismo estamos en 2026, como podriamos implementar el tema de fechas mejor?

---

Periódicos deportivos por liga — Top 3

Premier League (Inglaterra)

1. BBC Sport — bbc.com/sport
2. The Guardian — theguardian.com
3. Sky Sports — skysports.com

La Liga (España)

1. Marca — marca.com
2. AS — as.com
3. Mundo Deportivo — mundodeportivo.com

Serie A (Italia)

1. Gazzetta dello Sport — gazzetta.it
2. Corriere dello Sport — corrieredellosport.it
3. Tuttosport — tuttosport.com

Bundesliga (Alemania)

1. Kicker — kicker.de
2. Bild — bild.de
3. Sport1 — sport1.de

Ligue 1 (Francia)

1. L'Équipe — lequipe.fr
2. RMC Sport — rmcsport.bfmtv.com
3. Foot Mercato — footmercato.net

---

Cómo aplicarlo por categoría

Cada categoría necesita un rango diferente:

Categoría: market_and_contract
Estrategia: time_range="month"
Por qué: El valor de mercado cambia constantemente
────────────────────────────────────────
Categoría: injuries
Estrategia: topic="news", days=180
Por qué: Quieres lesiones recientes, no de hace 5 años
────────────────────────────────────────
Categoría: transfers
Estrategia: Sin filtro de fecha
Por qué: El historial completo es relevante
────────────────────────────────────────
Categoría: awards
Estrategia: time_range="year"
Por qué: Premios de la temporada actual
────────────────────────────────────────
Categoría: interviews_and_quotes
Estrategia: topic="news", days=90
Por qué: Declaraciones recientes

Así eliminamos el año hardcodeado del suffix y dejamos que Tavily filtre por fecha de verdad.

¿Quieres que aplique todo esto (dominios + fechas) a web_search.py?

Sources:

- https://docs.tavily.com/documentation/api-reference/endpoint/search
- https://help.tavily.com/articles/3347142954-best-practices
- https://community.tavily.com/t/addition-of-time-range-parameter-in-search-tool/40

---

## Mejora 3: Añadir @mcp.prompt para estructurar la presentación

**Problema:** Cuando el LLM recibe los datos crudos de `get_player_context`, no tiene instrucciones de cómo organizarlos. Cada vez los presenta diferente.

**Solución:** Añadir un `@mcp.prompt` que le diga al LLM cómo estructurar la info como un informe de scouting profesional.

**Archivo:** `main.py`

```python
@mcp.prompt
def player_context_report() -> str:
    """How to present get_player_context data as a scouting report."""
    return (
        "You are a professional football scout presenting player context data.\n\n"
        "Structure the report as follows:\n"
        "1) Player overview: name, team, nationality, age, position.\n"
        "2) Market value and contract situation (source + date).\n"
        "3) Injury history as risk assessment: low / medium / high.\n"
        "4) Transfer history as career trajectory timeline.\n"
        "5) Awards and titles in bullet points.\n"
        "6) Notable quote that reveals mentality.\n"
        "7) Always cite the source URL for each piece of information.\n\n"
        "Keep it concise. No fluff. Data first, opinion second."
    )
```

**Cómo se usa:** El usuario selecciona el prompt `player_context_report` en Claude Desktop (botón "+") antes de hacer preguntas sobre jugadores. Claude seguirá esa estructura automáticamente.

**Estado:** ✅ Aplicado

---

Creo que el tema de prompts tendria que estar en un archivo aparte, algo como `prompts.py` para mantener el código organizado.

el tema de la config del websearch también, podríamos tener un `config.py` donde definamos las fuentes y las estrategias de búsqueda por categoría, así el `web_search.py` solo se encarga de ejecutar la búsqueda según esa configuración.
