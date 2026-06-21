# Shamba Backend (FastAPI)

Backend for the Shamba hackathon project. Handles auth, the farm health
assessment endpoint, and historical data for the Trends page.

## Setup

```bash
cd shamba-backend
python3 -m venv venv
  # Linux/Mac  
source venv/bin/activate  
# Windows
venv\Scripts\activate  
pip install -r requirements.txt

cp .env.example .env              # then fill in SECRET_KEY and GEMINI_API_KEY
```

Run it:

```bash
uvicorn main:app --reload --port 8000
```




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
not JSON)  Use `username` (= the email) and
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
curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"name":"Jane","email":"jane@example.com","password":"secret123"}'

# Save the access_token from the response, then:
TOKEN="paste-token-here"

curl -X POST http://localhost:8000/api/assess-farm \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"crop_type":"maize","farm_size_acres":2.5,"irrigation_level":"medium","soil_moisture":"moderate","water_usage_litres":5000}'

curl http://localhost:8000/api/farm-history \ 
-H "Authorization: Bearer $TOKEN"
```

## Deployment

Currently runs locally.

