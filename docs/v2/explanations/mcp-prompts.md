# @mcp.prompt — Explicación detallada

## Qué es

Un prompt MCP es una plantilla de instrucciones que le dices al cliente (Claude Desktop) sobre cómo debe presentar los datos que recibe de tus herramientas. Es como darle un manual: "cuando recibas estos datos, preséntalos así".

## Cómo funciona

1. Defines una función con `@mcp.prompt` que devuelve un string con instrucciones
2. Claude Desktop lo detecta automáticamente al conectarse
3. El usuario lo selecciona con el botón "+" en Claude Desktop
4. Claude recibe esas instrucciones como contexto antes de llamar a tus tools

## Sintaxis básica

```python
@mcp.prompt
def nombre_del_prompt() -> str:
    """Descripción corta de qué hace este prompt."""
    return "Las instrucciones que seguirá el LLM..."
```

## Con parámetros

```python
@mcp.prompt
def analisis(tipo: str = "resumen") -> str:
    """Genera un análisis personalizado."""
    return f"Haz un {tipo} de los datos recibidos."
```

## Con múltiples mensajes

```python
from fastmcp.prompts import Message

@mcp.prompt
def conversacion() -> list[Message]:
    return [
        Message("Eres un scout profesional de fútbol."),
        Message("Entendido, estoy listo.", role="assistant"),
    ]
```

## Tipos de retorno válidos

| Tipo | Cuándo usarlo |
|------|--------------|
| `str` | Instrucciones simples en un solo bloque |
| `Message` | Un solo mensaje con rol específico (user/assistant) |
| `list[Message]` | Conversación con varios mensajes |

## Diferencia con @mcp.tool

- `@mcp.tool` → El LLM **ejecuta** una acción (buscar jugadores, consultar DB)
- `@mcp.prompt` → El LLM **recibe instrucciones** sobre cómo comportarse

Un tool hace cosas. Un prompt guía cómo presentar lo que hizo.

## Fuentes

- [FastMCP Prompts docs](https://gofastmcp.com/servers/prompts)
- [Expanding FastMCP with Prompts and Resources](https://medium.com/@tkadeethum/expanding-fastmcp-with-prompts-and-resources-for-smarter-research-assistants-7bded4d1e35f)
