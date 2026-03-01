from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Hue Bridge
    hue_bridge_ip: str = "192.168.1.100"
    hue_api_key: str = ""
    hue_light_ids: list[str] = ["1", "2", "3"]

    # Animation
    default_pattern: str = "cycle_together"
    animation_duration: float = 30.0
    step_duration: float = 1.0

    # ESPN polling intervals (seconds)
    espn_poll_interval_live: int = 10
    espn_poll_interval_pregame: int = 60
    espn_poll_interval_nogame: int = 300

    # Server
    host: str = "0.0.0.0"
    port: int = 8080

    model_config = {"env_prefix": "BTL_"}


settings = Settings()
