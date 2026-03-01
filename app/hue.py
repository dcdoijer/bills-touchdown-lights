from __future__ import annotations

import httpx

from app.config import settings


class HueClient:
    def __init__(self) -> None:
        self.base_url = f"http://{settings.hue_bridge_ip}/api/{settings.hue_api_key}"
        self.light_ids: list[str] = list(settings.hue_light_ids)
        self._client: httpx.AsyncClient | None = None
        self._saved_states: dict[str, dict] = {}

    async def get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(timeout=5.0)
        return self._client

    async def close(self) -> None:
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    async def save_states(self) -> None:
        client = await self.get_client()
        self._saved_states = {}
        for lid in self.light_ids:
            try:
                resp = await client.get(f"{self.base_url}/lights/{lid}")
                data = resp.json()
                self._saved_states[lid] = data.get("state", {})
            except Exception:
                pass

    async def restore_states(self) -> None:
        client = await self.get_client()
        for lid, state in self._saved_states.items():
            body: dict = {"on": state.get("on", True)}
            if state.get("colormode") == "xy":
                body["xy"] = state["xy"]
            elif state.get("colormode") == "ct":
                body["ct"] = state["ct"]
            body["bri"] = state.get("bri", 254)
            body["transitiontime"] = 10  # 1 second smooth restore
            try:
                await client.put(f"{self.base_url}/lights/{lid}/state", json=body)
            except Exception:
                pass

    async def set_light(
        self, light_id: str, xy: list[float], bri: int = 254, transition: int = 0
    ) -> None:
        client = await self.get_client()
        try:
            await client.put(
                f"{self.base_url}/lights/{light_id}/state",
                json={"on": True, "xy": xy, "bri": bri, "transitiontime": transition},
            )
        except Exception:
            pass
