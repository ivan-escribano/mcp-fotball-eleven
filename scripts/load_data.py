from ScraperFC.sofascore import Sofascore

from config import LEAGUES_TO_LOAD
from db import initialize_database, save_players


def load_league_data(season: str, league: str):
    """Load data for a single league/season."""
    print(f"📥 Loading {league} {season}...")

    scraper = Sofascore()

    players_df = scraper.scrape_player_league_stats(season, league)

    save_players(players_df, league=league, season=season)

    print(f"✅ {league} {season} loaded")


def load_all_data():
    """Load all configured leagues from LEAGUES_TO_LOAD."""
    initialize_database()

    for config in LEAGUES_TO_LOAD:
        try:
            load_league_data(config["season"], config["league"])
        except (ValueError, KeyError, RuntimeError) as e:
            print(f"❌ Error loading {config['league']}: {e}")

    print("\n🎉 All data loaded!")


if __name__ == "__main__":
    load_all_data()
