# Shamba Backend (FastAPI)

Backend for the Shamba hackathon project. Handles auth, the farm health
assessment endpoint, and historical data for the Trends page.

## Setup

```bash
cd shamba-backend
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env              # then fill in SECRET_KEY and GEMINI_API_KEY
```

Run it:

```bash
uvicorn main:app --reload --port 8000
```

Interactive docs (test everything here without writing frontend code first):
`http://localhost:8000/docs`

The database is SQLite (`shamba.db`), created automatically on first run —
no separate DB setup needed for the hackathon.

## Dropping in Virginia's model

Put `farm_health_model.pkl` directly in this folder (same level as
`main.py`) and restart the server. `ai_logic.py` picks it up automatically.
Until then, a simple rule-based stub answers `/assess-farm` so the rest of
the team isn't blocked.

**Before Virginia trains the final model**, make sure she uses the same
crop/irrigation/moisture → integer mapping defined at the top of
`ai_logic.py`. The original training script's `LabelEncoder` approach
doesn't save its mapping, so without agreeing on fixed codes the model's
predictions will be silently wrong (no error, just bad answers) once it's
hooked up to this backend.

## API Reference

### POST /api/auth/signup
```json
// request
{ "name": "Jane Wanjiru", "email": "jane@example.com", "password": "secret123" }

// response
{ "access_token": "eyJ...", "token_type": "bearer" }
```

### POST /api/auth/login
Content-Type: `application/x-www-form-urlencoded` (standard OAuth2 form,
not JSON) — Vanessa's login form should POST `username` (= the email) and
`password` as form fields.
```
// response
{ "access_token": "eyJ...", "token_type": "bearer" }
```

For every endpoint below, send the token as a header:
`Authorization: Bearer <access_token>`

### POST /api/assess-farm
```json
// request
{
  "crop_type": "maize",
  "farm_size_acres": 2.5,
  "irrigation_level": "medium",
  "soil_moisture": "moderate",
  "water_usage_litres": 5000
}

// response
{
  "health_status": "moderate",
  "carbon_estimate": 2.75,
  "recommendations": "...",
  "timestamp": "2026-06-21T10:32:00"
}
```
This also saves the assessment to the database, tied to the logged-in farmer.

### GET /api/farm-history
Returns a list of all past assessments for the logged-in farmer, newest
first — this is what feeds Vanessa's TrendsPage.
```json
[
  {
    "crop_type": "maize",
    "farm_size_acres": 2.5,
    "irrigation_level": "medium",
    "soil_moisture": "moderate",
    "health_status": "moderate",
    "carbon_estimate": 2.75,
    "recommendations": "...",
    "timestamp": "2026-06-21T10:32:00"
  }
]
```

## Quick test with curl

```bash
# Sign up
curl -X POST localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"name":"Jane","email":"jane@example.com","password":"secret123"}'

# Save the access_token from the response, then:
TOKEN="paste-token-here"

curl -X POST localhost:8000/api/assess-farm \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"crop_type":"maize","farm_size_acres":2.5,"irrigation_level":"medium","soil_moisture":"moderate","water_usage_litres":5000}'

curl localhost:8000/api/farm-history -H "Authorization: Bearer $TOKEN"
```

## Notes for the team

- **Nicole / Vanessa:** login is form-encoded, not JSON (that's a FastAPI/
  OAuth2 convention) — everything else is plain JSON. Store the token
  (e.g. in React state or a context, not localStorage if you want it to
  survive only the session) and attach it as a Bearer header on every
  request after login.
- **Gemini calls fail gracefully** — if `GEMINI_API_KEY` isn't set or the
  network/API hiccups during the demo, `/assess-farm` still returns a
  sensible fallback recommendation instead of erroring out.
- CORS is wide open (`allow_origins=["*"]`) for fast iteration. Fine for a
  hackathon demo; not something to ship as-is beyond that.