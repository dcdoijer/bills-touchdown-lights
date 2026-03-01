# Bills Touchdown Lights

A Python application that monitors live Buffalo Bills games and triggers a red, white, and blue Philips Hue light animation when the Bills score a touchdown. Runs as a Docker container on a Synology NAS with a simple web UI for control.

## Features

- **Touchdown detection** — polls the ESPN API during live Bills games and triggers lights on score increases
- **Two animation patterns** — cycle together (all lights in unison) or chase (staggered wave)
- **Smooth color transitions** — lights fade through red, white, and blue for 30 seconds, then restore to their previous state
- **Web UI** — test the animation, toggle game monitoring, and switch patterns from your browser
- **Docker ready** — deploy with docker-compose on a Synology NAS (or any Docker host)

## Setup

### 1. Find your Hue Bridge IP

```bash
curl https://discovery.meethue.com/
```

### 2. Generate an API key

Press the physical button on your Hue Bridge, then within 30 seconds run:

```bash
curl -X POST http://<BRIDGE_IP>/api \
  -H "Content-Type: application/json" \
  -d '{"devicetype":"bills_touchdown_lights#synology"}'
```

Copy the `username` value from the response — this is your API key.

### 3. Find your light IDs

```bash
curl http://<BRIDGE_IP>/api/<API_KEY>/lights | python3 -m json.tool
```

Note the numeric IDs of the color-capable lights you want to use.

### 4. Configure

Create a `.env` file in the project directory:

```env
BTL_HUE_BRIDGE_IP=192.168.1.100
BTL_HUE_API_KEY=your-api-key-here
BTL_HUE_LIGHT_IDS=["1","2","3"]
```

### 5. Deploy

```bash
docker-compose up -d --build
```

Open `http://<HOST_IP>:8080` in your browser.

## Configuration

All settings can be overridden via environment variables (prefix `BTL_`):

| Variable | Default | Description |
|----------|---------|-------------|
| `BTL_HUE_BRIDGE_IP` | `192.168.1.100` | Hue Bridge IP address |
| `BTL_HUE_API_KEY` | — | Hue Bridge API key |
| `BTL_HUE_LIGHT_IDS` | `["1","2","3"]` | JSON array of light IDs |
| `BTL_DEFAULT_PATTERN` | `cycle_together` | Default animation (`cycle_together` or `chase`) |
| `BTL_ANIMATION_DURATION` | `30.0` | Animation length in seconds |
| `BTL_STEP_DURATION` | `1.0` | Time per color step in seconds |
| `BTL_ESPN_POLL_INTERVAL_LIVE` | `10` | Polling interval during live games (seconds) |

## Tech Stack

- Python 3.9+ / FastAPI / uvicorn
- httpx (async HTTP for ESPN API and Hue Bridge REST API)
- pydantic-settings (configuration)
- Docker
