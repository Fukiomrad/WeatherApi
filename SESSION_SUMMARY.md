# Weather API — Session Summary

## Current state
A working Flask weather API running via Docker Compose with Redis caching.

## How to run
```
cd C:\Users\ardad\Desktop\WeatherAPI
docker compose up -d
```
Then visit `http://localhost:5000/weather?city=London`

## Files created
| File | Purpose |
|---|---|
| `app.py` | Flask app — endpoint, Redis cache, Visual Crossing API call |
| `requirements.txt` | Python dependencies |
| `Dockerfile` | Container image for the Flask app |
| `docker-compose.yml` | Runs Redis + Flask app |
| `.env` | API key and Redis URL (not committed) |
| `.env.example` | Template for env vars |

## What we built (step-by-step)
1. **Minimal Flask app** — single `/weather?city=` endpoint, returns temp + conditions
2. **Environment variables** — moved API key out of code into `.env`
3. **Error handling** — 400 (no city), 404 (bad city), 502 (API down)
4. **Redis caching** — stores results for 12 hours, avoids repeated API calls

## What's left (from Plan.txt)
- Rate limiting (5 req/min per IP)

## API key
Visual Crossing: `FVDBM3M7MAQU7VNZH5DVYLXGC`
