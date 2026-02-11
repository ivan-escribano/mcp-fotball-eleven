from sqlmodel import SQLModel, Field, UniqueConstraint
from sqlalchemy import String


class PlayerStats(SQLModel, table=True):
    """Player statistics returned from the database."""

    __tablename__ = "player_stats"
    __table_args__ = (UniqueConstraint("player_id", "league", "season"),)

    id: int | None = Field(default=None, primary_key=True)

    player_id: int
    team_id: int
    player: str = Field(sa_type=String(200))
    team: str = Field(sa_type=String(200))
    league: str = Field(sa_type=String(100))
    season: str = Field(sa_type=String(20))
    appearances: int | None = None
    minutes_played: int | None = None
    goals: int | None = None
    assists: int | None = None
    total_shots: int | None = None
    shots_on_target: int | None = None
    blocked_shots: int | None = None
    big_chances_missed: int | None = None
    goal_conversion_percentage: float | None = None
    key_passes: int | None = None
    big_chances_created: int | None = None
    hit_woodwork: int | None = None
    offsides: int | None = None
    expected_goals: float | None = None
    successful_dribbles: int | None = None
    successful_dribbles_percentage: float | None = None
    dispossessed: int | None = None
    dribbled_past: int | None = None
    accurate_passes: int | None = None
    accurate_passes_percentage: float | None = None
    accurate_final_third_passes: int | None = None
    pass_to_assist: int | None = None
    accurate_crosses: int | None = None
    accurate_crosses_percentage: float | None = None
    accurate_long_balls: int | None = None
    accurate_long_balls_percentage: float | None = None
    tackles: int | None = None
    interceptions: int | None = None
    clearances: int | None = None
    fouls: int | None = None
    was_fouled: int | None = None
    yellow_cards: int | None = None
    red_cards: int | None = None
    error_lead_to_goal: int | None = None
    error_lead_to_shot: int | None = None
    ground_duels_won: int | None = None
    ground_duels_won_percentage: float | None = None
    aerial_duels_won: int | None = None
    aerial_duels_won_percentage: float | None = None
    total_duels_won: int | None = None
    total_duels_won_percentage: float | None = None
    saves: int | None = None
    saved_shots_from_inside_the_box: int | None = None
    saved_shots_from_outside_the_box: int | None = None
    goals_conceded_inside_the_box: int | None = None
    goals_conceded_outside_the_box: int | None = None
    high_claims: int | None = None
    successful_runs_out: int | None = None
    punches: int | None = None
    runs_out: int | None = None
    updated_at: str | None = None
