import asyncio

from app.config import settings
from app.hue import HueClient

COLORS: dict[str, list[float]] = {
    "red": [0.6750, 0.3220],
    "white": [0.3127, 0.3290],
    "blue": [0.1540, 0.0806],
}
COLOR_SEQUENCE = ["red", "white", "blue"]

_animation_lock = asyncio.Lock()
_animation_running = False


def is_running() -> bool:
    return _animation_running


async def cycle_together(hue: HueClient) -> None:
    # transitiontime is in units of 100ms, so step_duration 1.0s = 10
    transition = int(settings.step_duration * 10)
    elapsed = 0.0
    step = 0
    while elapsed < settings.animation_duration:
        color_name = COLOR_SEQUENCE[step % 3]
        xy = COLORS[color_name]
        await asyncio.gather(
            *(hue.set_light(lid, xy, transition=transition) for lid in hue.light_ids)
        )
        await asyncio.sleep(settings.step_duration)
        elapsed += settings.step_duration
        step += 1


async def chase(hue: HueClient) -> None:
    transition = int(settings.step_duration * 10)
    elapsed = 0.0
    step = 0
    while elapsed < settings.animation_duration:
        tasks = []
        for i, lid in enumerate(hue.light_ids):
            color_idx = (step + i) % 3
            xy = COLORS[COLOR_SEQUENCE[color_idx]]
            tasks.append(hue.set_light(lid, xy, transition=transition))
        await asyncio.gather(*tasks)
        await asyncio.sleep(settings.step_duration)
        elapsed += settings.step_duration
        step += 1


async def run_animation(hue: HueClient, pattern: str) -> None:
    global _animation_running
    if _animation_lock.locked():
        return
    async with _animation_lock:
        _animation_running = True
        try:
            await hue.save_states()
            if pattern == "chase":
                await chase(hue)
            else:
                await cycle_together(hue)
        finally:
            await hue.restore_states()
            _animation_running = False
