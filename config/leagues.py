from enum import Enum


class SofascoreLeague(Enum):
    """Available leagues in Sofascore (valid names from ScraperFC)"""

    # Top 5 Europe
    PREMIER_LEAGUE = ("EPL", 17)
    LA_LIGA = ("La Liga", 8)
    BUNDESLIGA = ("Bundesliga", 35)
    SERIE_A = ("Serie A", 23)
    LIGUE_1 = ("Ligue 1", 34)

    # UEFA Competitions
    CHAMPIONS_LEAGUE = ("Champions League", 7)
    EUROPA_LEAGUE = ("Europa League", 679)
    CONFERENCE_LEAGUE = ("Europa Conference League", 17015)
    EURO = ("Euros", 1)

    # Other European leagues
    SUPER_LIG = ("Turkish Super Lig", 52)

    # South America
    ARGENTINA_LIGA = ("Argentina Liga Profesional", 155)
    ARGENTINA_COPA = ("Argentina Copa de la Liga Profesional", 13475)
    COPA_LIBERTADORES = ("Copa Libertadores", 384)
    PERU_LIGA_1 = ("Liga 1 Peru", 406)

    # North America
    MLS = ("MLS", 242)
    USL_CHAMPIONSHIP = ("USL Championship", 13363)
    USL_LEAGUE_1 = ("USL1", 13362)
    USL_LEAGUE_2 = ("USL2", 13546)
    GOLD_CUP = ("Gold Cup", 140)

    # Middle East
    SAUDI_PRO_LEAGUE = ("Saudi Pro League", 955)

    # World Cups
    WORLD_CUP = ("World Cup", 16)
    WOMENS_WORLD_CUP = ("Women's World Cup", 290)

    @property
    def league_name(self) -> str:
        return self.value[0]

    @property
    def league_id(self) -> int:
        return self.value[1]


# Data to load (configurable)
LEAGUES_TO_LOAD = [
    {"season": "25/26", "league": SofascoreLeague.PREMIER_LEAGUE.league_name},
    {"season": "25/26", "league": SofascoreLeague.LA_LIGA.league_name},
    {"season": "25/26", "league": SofascoreLeague.BUNDESLIGA.league_name},
    {"season": "25/26", "league": SofascoreLeague.SERIE_A.league_name},
    {"season": "25/26", "league": SofascoreLeague.LIGUE_1.league_name},
]
