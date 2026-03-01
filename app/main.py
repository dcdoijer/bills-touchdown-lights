import asyncio
import logging

from fastapi import FastAPI
from fastapi.responses import FileResponse

from app import animations
from app.hue import HueClient
from app.monitor import AppState, game_monitor_loop

logging.basicConfig(level=logging.INFO)

app = FastAPI(title="Bills Touchdown Lights")
state = AppState()
hue = HueClient()


@app.on_event("shutdown")
async def shutdown() -> None:
    if state.monitor_task and not state.monitor_task.done():
        state.monitor_task.cancel()
    await hue.close()


@app.get("/")
async def root() -> FileResponse:
    return FileResponse("app/static/index.html")


@app.get("/api/status")
async def get_status() -> dict:
    return {
        "monitoring_active": state.monitoring_active,
        "current_pattern": state.current_pattern,
        "game_status": state.game_status,
        "animation_running": animations.is_running(),
    }


@app.post("/api/test")
async def test_animation() -> dict:
    asyncio.create_task(animations.run_animation(hue, state.current_pattern))
    return {"status": "animation_triggered"}


@app.post("/api/monitor/start")
async def start_monitoring() -> dict:
    if state.monitoring_active:
        return {"status": "already_running"}
    state.monitoring_active = True
    state.last_known_score = None
    state.game_status = "Starting monitor..."
    state.monitor_task = asyncio.create_task(game_monitor_loop(state, hue))
    return {"status": "started"}


@app.post("/api/monitor/stop")
async def stop_monitoring() -> dict:
    if not state.monitoring_active:
        return {"status": "not_running"}
    state.monitoring_active = False
    if state.monitor_task and not state.monitor_task.done():
        state.monitor_task.cancel()
    state.monitor_task = None
    state.game_status = "Monitoring off"
    state.last_known_score = None
    return {"status": "stopped"}


@app.post("/api/pattern")
async def set_pattern(pattern: str) -> dict:
    if pattern in ("cycle_together", "chase"):
        state.current_pattern = pattern
    return {"pattern": state.current_pattern}
