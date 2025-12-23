from datetime import datetime

import pandas as pd
from sqlmodel import SQLModel, Session, create_engine, select, delete

from config import DB_URL
from model import PlayerStatsFilters, PlayerStats
from utils import normalize_column_name

engine = create_engine(DB_URL)


def initialize_database():
    """Initialize the SQLite database and create necessary tables."""

    # Create all table=True models in SQLITE
    SQLModel.metadata.create_all(engine)

    print("✅ Database initialized")


def save_players(df: pd.DataFrame, league: str, season: str):
    """Normalize and save players data to the database."""

    df_clean = df.copy()
    df_clean.columns = [normalize_column_name(col) for col in df_clean.columns]

    df_clean["league"] = league
    df_clean["season"] = season
    df_clean["updated_at"] = datetime.now().isoformat()

    # Open session delete old data for league + season before update
    with Session(engine) as session:
        session.exec(
            delete(PlayerStats).where(
                PlayerStats.league == league,
                PlayerStats.season == season
            )
        )
        session.commit()
        print(f"Deleted old data for {league} {season}")

    # Raw connection insert DataFrame directly
    with engine.connect() as connection:
        df_clean.to_sql("player_stats", connection,
                        if_exists="append", index=False)
        connection.commit()

    print(f"✅ {len(df_clean)} players from {league} saved")


def get_players(filters: PlayerStatsFilters) -> list[dict]:
    """Search players based on filters."""
    with Session(engine) as session:
        query_select = select(PlayerStats)

        # Get only filters in the model/schema
        query_filters = filters.model_dump(exclude_none=True,  exclude={
            "order_by", "order_direction", "limit"})

        # Build WHERE conditions in the SELECT query
        for filter_field, filter_value in query_filters.items():
            # Get the true name of property min_goals -> goals
            column_name = filter_field.removeprefix(
                "min_").removeprefix("max_")

            # Look for this attribute in schema: ej:"goals" exist?
            column = getattr(PlayerStats, column_name, None)

            if column is None:
                continue

            if isinstance(filter_value, str):
                # Build "LIKE" ops match strings
                query_select = query_select.where(
                    column.contains(filter_value))

            elif filter_field.startswith("max_"):
                # Build "below to x number" ops
                query_select = query_select.where(column <= filter_value)

            elif filter_field.startswith("min_"):
                # Build "greater than x number" ops
                query_select = query_select.where(column >= filter_value)

            else:
                continue

        # Build how to show results order + limit
        order_column = getattr(PlayerStats, filters.order_by, None)

        if order_column is not None:
            if filters.order_direction == "DESC":
                query_select = query_select.order_by(order_column.desc())
            else:
                query_select = query_select.order_by(order_column.asc())

        query_select = query_select.limit(filters.limit)

        results = session.exec(query_select).all()
        return [result.model_dump() for result in results]
