from typing import Optional, Literal
from pydantic import BaseModel, Field

# Valid league names for Sofascore
LeagueName = Literal[
    "EPL", "La Liga", "Bundesliga", "Serie A", "Ligue 1",
    "Champions League", "Europa League", "Europa Conference League", "Euros",
    "Turkish Super Lig",
    "Argentina Liga Profesional", "Argentina Copa de la Liga Profesional",
    "Copa Libertadores", "Liga 1 Peru",
    "MLS", "USL Championship", "USL1", "USL2", "Gold Cup",
    "Saudi Pro League",
    "World Cup", "Women's World Cup"
]


class PlayerStatsFilters(BaseModel):
    """
    Flexible filter model used in the MCP server to allow the LLM
    to decide which attributes to apply when querying player statistics.
    All fields are optional for maximum freedom.
    """

    # ------------------------------------------------------------
    # IDENTITY (text search with LIKE)
    # ------------------------------------------------------------

    player: Optional[str] = Field(
        default=None,
        description="Player name to search for. Supports partial matching (e.g., 'Messi' finds 'Lionel Messi')."
    )
    team: Optional[str] = Field(
        default=None,
        description="Team name to filter by. Supports partial matching (e.g., 'Madrid' finds 'Real Madrid')."
    )
    league: Optional[LeagueName] = Field(
        default="La Liga",
        description="League name. Valid options: EPL, La Liga, Bundesliga, Serie A, Ligue 1."
    )
    season: Optional[str] = Field(
        default="25/26",
        description="Season identifier (e.g., '25/26', '24/25')."
    )

    # ------------------------------------------------------------
    # PLAYING TIME (min only - we want players with enough minutes)
    # ------------------------------------------------------------

    min_appearances: Optional[int] = Field(
        default=None,
        description="Minimum appearances. Use to filter regular starters (e.g., 10+ means consistent selection)."
    )
    min_minutes_played: Optional[int] = Field(
        default=None,
        description="Minimum minutes played. Use 900 for ~10 games, 2500+ for regular starter."
    )

    # ------------------------------------------------------------
    # OFFENSIVE STATS (min - we want high scorers)
    # ------------------------------------------------------------

    min_goals: Optional[int] = Field(
        default=None,
        description="Minimum goals scored. Top scorers have 15+ per season."
    )
    min_assists: Optional[int] = Field(
        default=None,
        description="Minimum assists. Elite creators have 10+ per season."
    )
    min_expected_goals: Optional[float] = Field(
        default=None,
        description="Minimum xG. Compare with actual goals: xG > goals = poor finisher, xG < goals = clinical."
    )
    min_total_shots: Optional[int] = Field(
        default=None,
        description="Minimum total shots. Strikers typically have 50+ per season."
    )
    min_shots_on_target: Optional[int] = Field(
        default=None,
        description="Minimum shots on target. Good ratio is 40%+ of total shots."
    )
    min_goal_conversion_percentage: Optional[float] = Field(
        default=None,
        description="Minimum goal conversion %. Above 15% is good, 20%+ is elite."
    )
    min_key_passes: Optional[int] = Field(
        default=None,
        description="Minimum key passes. 50+ per season is elite for playmakers."
    )
    min_big_chances_created: Optional[int] = Field(
        default=None,
        description="Minimum big chances created. 10+ per season is world-class."
    )
    max_big_chances_missed: Optional[int] = Field(
        default=None,
        description="Maximum big chances missed. Low values = clinical finisher."
    )
    max_offsides: Optional[int] = Field(
        default=None,
        description="Maximum offsides. Low values = good timing in runs."
    )

    # ------------------------------------------------------------
    # DRIBBLING & BALL CONTROL (min for good, max for bad)
    # ------------------------------------------------------------

    min_successful_dribbles: Optional[int] = Field(
        default=None,
        description="Minimum successful dribbles. 50+ is elite for wingers."
    )
    min_successful_dribbles_percentage: Optional[float] = Field(
        default=None,
        description="Minimum dribble success %. Above 50% is good, 60%+ is excellent."
    )
    max_dispossessed: Optional[int] = Field(
        default=None,
        description="Maximum times dispossessed. Low values = good ball retention."
    )
    min_was_fouled: Optional[int] = Field(
        default=None,
        description="Minimum times fouled. High values = players who draw fouls."
    )

    # ------------------------------------------------------------
    # PASSING (min - we want good passers)
    # ------------------------------------------------------------

    min_accurate_passes: Optional[int] = Field(
        default=None,
        description="Minimum accurate passes. 1000+ is elite for midfielders."
    )
    min_accurate_passes_percentage: Optional[float] = Field(
        default=None,
        description="Minimum pass accuracy %. Above 85% is good, 90%+ is elite."
    )
    min_accurate_final_third_passes: Optional[int] = Field(
        default=None,
        description="Minimum accurate passes in attacking third."
    )
    min_pass_to_assist: Optional[int] = Field(
        default=None,
        description="Minimum pre-assists (passes leading to the assist)."
    )
    min_accurate_crosses: Optional[int] = Field(
        default=None,
        description="Minimum accurate crosses. Essential for wingers/fullbacks."
    )
    min_accurate_crosses_percentage: Optional[float] = Field(
        default=None,
        description="Minimum cross accuracy %. Above 25% is decent, 35%+ is very good."
    )
    min_accurate_long_balls: Optional[int] = Field(
        default=None,
        description="Minimum accurate long balls. Important for ball-playing defenders."
    )
    min_accurate_long_balls_percentage: Optional[float] = Field(
        default=None,
        description="Minimum long ball accuracy %. Above 50% is excellent."
    )

    # ------------------------------------------------------------
    # DEFENSIVE (min for good actions, max for errors)
    # ------------------------------------------------------------

    min_tackles: Optional[int] = Field(
        default=None,
        description="Minimum tackles. 50+ is very good for defensive players."
    )
    min_interceptions: Optional[int] = Field(
        default=None,
        description="Minimum interceptions. 30+ shows good game reading."
    )
    min_clearances: Optional[int] = Field(
        default=None,
        description="Minimum clearances. 80+ is high for center-backs."
    )
    max_fouls: Optional[int] = Field(
        default=None,
        description="Maximum fouls committed. Low values = clean player."
    )
    max_dribbled_past: Optional[int] = Field(
        default=None,
        description="Maximum times dribbled past. Low values = solid 1v1 defender."
    )
    max_error_lead_to_goal: Optional[int] = Field(
        default=None,
        description="Maximum errors leading to goal. Use 0 for reliable defenders."
    )
    max_error_lead_to_shot: Optional[int] = Field(
        default=None,
        description="Maximum errors leading to shot. Low values = reliable."
    )

    # ------------------------------------------------------------
    # DUELS (min - we want dominant players)
    # ------------------------------------------------------------

    min_ground_duels_won: Optional[int] = Field(
        default=None,
        description="Minimum ground duels won."
    )
    min_ground_duels_won_percentage: Optional[float] = Field(
        default=None,
        description="Minimum ground duel success %. Above 55% is good."
    )
    min_aerial_duels_won: Optional[int] = Field(
        default=None,
        description="Minimum aerial duels won. 50+ is very good."
    )
    min_aerial_duels_won_percentage: Optional[float] = Field(
        default=None,
        description="Minimum aerial duel success %. Above 60% is dominant."
    )
    min_total_duels_won: Optional[int] = Field(
        default=None,
        description="Minimum total duels won."
    )
    min_total_duels_won_percentage: Optional[float] = Field(
        default=None,
        description="Minimum overall duel success %. Above 55% is solid."
    )

    # ------------------------------------------------------------
    # DISCIPLINE (max - we want disciplined players)
    # ------------------------------------------------------------

    max_yellow_cards: Optional[int] = Field(
        default=None,
        description="Maximum yellow cards. 0-3 is clean, 8+ is concerning."
    )
    max_red_cards: Optional[int] = Field(
        default=None,
        description="Maximum red cards. Use 0 for no send-offs."
    )

    # ------------------------------------------------------------
    # GOALKEEPER (min for saves, max for goals conceded)
    # ------------------------------------------------------------

    min_saves: Optional[int] = Field(
        default=None,
        description="Minimum saves. 80+ per season is high workload."
    )
    min_saved_shots_from_inside_the_box: Optional[int] = Field(
        default=None,
        description="Minimum saves from inside the box."
    )
    min_saved_shots_from_outside_the_box: Optional[int] = Field(
        default=None,
        description="Minimum saves from outside the box."
    )
    max_goals_conceded_inside_the_box: Optional[int] = Field(
        default=None,
        description="Maximum goals conceded from inside box."
    )
    max_goals_conceded_outside_the_box: Optional[int] = Field(
        default=None,
        description="Maximum goals conceded from outside box."
    )
    min_high_claims: Optional[int] = Field(
        default=None,
        description="Minimum high claims. 20+ shows aerial dominance."
    )
    min_successful_runs_out: Optional[int] = Field(
        default=None,
        description="Minimum successful runs out. Important for sweeper-keepers."
    )
    min_punches: Optional[int] = Field(
        default=None,
        description="Minimum punches to clear danger."
    )
    max_runs_out: Optional[int] = Field(
        default=None,
        description="Minimum total runs out of goal."
    )

    # ------------------------------------------------------------
    # RESULTS CONTROL (sorting and pagination)
    # ------------------------------------------------------------

    order_by: Optional[str] = Field(
        default="assists",
        description="Column to sort by (e.g., 'assists', 'big_chances_created', 'accurate_passes', 'goals', 'tackles', 'saves')"
    )
    order_direction: Literal["ASC", "DESC"] = Field(
        default="DESC",
        description="Sort direction: 'DESC' (highest first, default) or 'ASC' (lowest first)"
    )

    limit: int = Field(
        default=10,
        description="Maximum number of results to return (1-100)",
        ge=1,
        le=100
    )
