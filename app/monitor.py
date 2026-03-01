from __future__ import annotations

import asyncio
import logging

import httpx

from app import animations
from app.config import settings
from app.espn import get_bills_game_info
from app.hue import HueClient

logger = logging.getLogger(__name__)


class AppState:
    def __init__(self) -> None:
        self.monitoring_active: bool = False
        self.current_pattern: str = settings.default_pattern
        self.last_known_score: int | None = None
        self.game_status: str = "Monitoring off"
        self.monitor_task: asyncio.Task | None = None


async def game_monitor_loop(state: AppState, hue: HueClient) -> None:
    async with httpx.AsyncClient() as client:
        while True:
            try:
                game = await get_bills_game_info(client)

                if game is None:
                    state.game_status = "No Bills game found today"
                    state.last_known_score = None
                    await asyncio.sleep(settings.espn_poll_interval_nogame)
                    continue

                if game.game_state == "pre":
                    state.game_status = f"Upcoming: Bills vs {game.opponent_name}"
                    state.last_known_score = None
                    await asyncio.sleep(settings.espn_poll_interval_pregame)
                    continue

                if game.game_state == "post":
                    state.game_status = (
                        f"Final: Bills {game.bills_score} - "
                        f"{game.opponent_name} {game.opponent_score}"
                    )
                    state.last_known_score = None
                    await asyncio.sleep(3600)
                    continue

                # Game is live
                state.game_status = (
                    f"LIVE: Bills {game.bills_score} - "
                    f"{game.opponent_name} {game.opponent_score} "
                    f"({game.status_detail})"
                )

                # Touchdown detection
                if (
                    state.last_known_score is not None
                    and game.bills_score - state.last_known_score >= 6
                ):
                    logger.info(
                        "Touchdown detected! Score went from %d to %d",
                        state.last_known_score,
                        game.bills_score,
                    )
                    asyncio.create_task(
                        animations.run_animation(hue, state.current_pattern)
                    )

                state.last_known_score = game.bills_score
                await asyncio.sleep(settings.espn_poll_interval_live)

            except asyncio.CancelledError:
                raise
            except Exception as e:
                logger.exception("Error polling ESPN")
                state.game_status = f"Error polling ESPN: {e}"
                await asyncio.sleep(30)
