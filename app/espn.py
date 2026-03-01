from dataclasses import dataclass

import httpx

SCOREBOARD_URL = "https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard"
BILLS_ABBREVIATION = "BUF"


@dataclass
class GameInfo:
    bills_score: int
    opponent_score: int
    opponent_name: str
    game_state: str  # "pre", "in", "post"
    status_detail: str


async def get_bills_game_info(client: httpx.AsyncClient) -> GameInfo | None:
    resp = await client.get(SCOREBOARD_URL, timeout=10.0)
    resp.raise_for_status()
    data = resp.json()

    for event in data.get("events", []):
        for competition in event.get("competitions", []):
            competitors = competition.get("competitors", [])
            bills_team = None
            opponent_team = None
            for comp in competitors:
                if comp.get("team", {}).get("abbreviation") == BILLS_ABBREVIATION:
                    bills_team = comp
                else:
                    opponent_team = comp

            if bills_team and opponent_team:
                return GameInfo(
                    bills_score=int(bills_team.get("score", 0)),
                    opponent_score=int(opponent_team.get("score", 0)),
                    opponent_name=opponent_team["team"]["displayName"],
                    game_state=event["status"]["type"]["state"],
                    status_detail=event["status"]["type"].get("shortDetail", ""),
                )
    return None
