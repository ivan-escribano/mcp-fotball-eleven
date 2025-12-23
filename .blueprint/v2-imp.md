1. Crear API KEY manual y meterla en la BBDD
   Qué hay que construir

Una tabla api_keys en la base de datos.

Un script/command interno para generar una key y guardarla.

Requisitos mínimos

Guardar hash de la key (no la key en texto plano).

Campos recomendados:

id (PK)

name (string para identificar cliente/piloto)

key_hash (unique)

calls_count (int, default 0)

created_at

last_used_at (nullable)

Entregable para el dev

Migración SQL para crear la tabla.

Script tipo python scripts/create_api_key.py --name "pilot-club-x" que:

genera key aleatoria

hashea con APIKEY_SALT

inserta name + key_hash

imprime la key (solo una vez)

2. Seguimiento de API KEY: cuántas veces se usa + “loggers” (mínimo viable)
   Qué hay que construir

Validación de API key en todas las requests que lleguen al servidor MCP (por header HTTP x-api-key).

Incrementar contador de uso.

Requisitos mínimos

Middleware HTTP (o wrapper global) que:

lee x-api-key

hashea

busca en api_keys

si no existe → 401/403

si existe → calls_count += 1 y last_used_at = now()

continúa la request

Logging mínimo (sin tabla extra)

Log estructurado por request con al menos:

api_key_id o name

path/tool_name

status_code

duration_ms

Esto puede ir a stdout para que App Service lo capture.

Entregable para el dev:

Middleware implementado.

Logs en formato JSON (recomendado) para poder filtrar en Azure.

3. Deploy en Azure App Service
   Qué hay que construir

Desplegar el servicio MCP como Web App con HTTPS público.

Configurar variables de entorno.

Activar logs.

Requisitos mínimos

Método recomendado: App Service con Docker (más reproducible).

Variables de entorno obligatorias:

DATABASE_URL (con SSL si aplica)

APIKEY_SALT

Config:

habilitar “Application Logging” (console logs)

health endpoint simple (GET /health → 200)

Entregable para el dev:

Dockerfile (si no existe)

pipeline de deploy (GitHub Actions o manual)

guía de configuración en App Service (env vars + logs + health check)

4. Migración de SQLite a una base de datos SQL en Azure
   Qué hay que construir

Crear base de datos SQL remota (recomendado: Azure Database for PostgreSQL o Azure SQL).

Crear tablas equivalentes a SQLite.

Importar datos.

Requisitos mínimos

Definir el esquema final:

opción MVP: una tabla “ancha” players_stats con:

claves: season, competition, player_id

columnas de metadata: equipo, posición, minutos

54 métricas como columnas numéricas

Migración de datos:

Script que lea SQLite y haga bulk insert en la DB cloud (batch 500–2000 filas)

Alternativa: export SQLite → CSV → import (si es más rápido para el dev)

Entregable para el dev:

Script migrate_sqlite_to_postgres.py (o a Azure SQL) ejecutable localmente.

Índices mínimos para rendimiento:

(season), (competition), (player_id), (position), (minutes_played) según filtros de get_players

Verificación:

contar filas antes/después

query de sample para comprobar integridad

5. Loggers: registro de uso por key (dos niveles, elegir uno)
   Nivel A (lo que tú pides ahora: contador simple)

Ya cubierto con calls_count en tabla api_keys.

Logs en stdout con api_key_id/name y request info.

Nivel B (si queréis trazabilidad real por request)

Crear tabla api_usage para guardar cada llamada:

api_key_id, ts, tool_name/path, status_code, duration_ms

Insert “best-effort” (que un fallo de log no tumbe la request).

Entregable para el dev:

Implementar Nivel A sí o sí.

Nivel B opcional si necesitas auditoría o facturación futura.

Orden de ejecución recomendado (para no bloquearse)

Crear DB SQL en Azure + esquema (api_keys + players_stats)

Migrar datos SQLite → SQL

Implementar API key middleware + contador

Desplegar en App Service con env vars

Activar logs y validar con llamadas reales
