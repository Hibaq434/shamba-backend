"""
ai_logic.py — Shamba Backend
Wraps Virginia's farm_health_model.pkl, carbon formula, and LLM recommendations.

Model takes 10 features (confirmed from model_info.json):
  N, P, K, temperature, humidity, ph, rainfall,
  crop_encoded, irrigation_encoded, soil_moisture_encoded

Active LLM: Groq (set GROQ_API_KEY + GROQ_MODEL in .env)
Fallback:   Gemini (set GEMINI_API_KEY — uncomment section below when key arrives)
"""

import os
import pickle
import numpy as np
from pathlib import Path

MODEL_PATH = Path(__file__).parent / "farm_health_model.pkl"

# ── Agreed category mappings (must match Virginia's training exactly) ──────────
CROP_TYPE_MAP = {
    "maize": 0, "beans": 1, "wheat": 2, "rice": 3, "sorghum": 4,
    "cassava": 5, "potato": 6, "tomato": 7, "coffee": 8, "tea": 9,
}
IRRIGATION_MAP    = {"low": 0, "medium": 1, "high": 2}
SOIL_MOISTURE_MAP = {"dry": 0, "moderate": 1, "wet": 2}
HEALTH_STATUS_MAP = {"healthy": 0, "moderate": 1, "dry": 2}

# Reverse map: model integer output → human label
HEALTH_LABEL_MAP = {v: k for k, v in HEALTH_STATUS_MAP.items()}

# ── Allowed crop list — frontend dropdown must match this exactly ──────────────
ALLOWED_CROPS = list(CROP_TYPE_MAP.keys())

# ── Load model ─────────────────────────────────────────────────────────────────
_model = None
if MODEL_PATH.exists():
    with open(MODEL_PATH, "rb") as f:
        _model = pickle.load(f)


def validate_crop(crop_type: str) -> str:
    """Normalise to lowercase and reject crops not in the agreed 10.
    Raises ValueError with a clear message — caught by the route handler
    and returned as a 400 to the frontend."""
    normalised = crop_type.strip().lower()
    if normalised not in CROP_TYPE_MAP:
        raise ValueError(
            f"Crop '{crop_type}' is not supported. "
            f"Allowed crops: {', '.join(ALLOWED_CROPS)}"
        )
    return normalised


def predict_health(
    N: float, P: float, K: float,
    temperature: float, humidity: float,
    ph: float, rainfall: float,
    crop_type: str, irrigation_level: str, soil_moisture: str,
) -> str:
    """Runs Virginia's model with all 10 features.
    Falls back to a simple rule if the .pkl isn't present yet."""
    crop_type      = crop_type.strip().lower()
    irrigation_level = irrigation_level.strip().lower()
    soil_moisture  = soil_moisture.strip().lower()

    if _model is not None:
        crop_code      = CROP_TYPE_MAP[crop_type]           # already validated upstream
        irrigation_code = IRRIGATION_MAP.get(irrigation_level, 1)
        moisture_code  = SOIL_MOISTURE_MAP.get(soil_moisture, 1)

        features = np.array([[
            N, P, K, temperature, humidity, ph, rainfall,
            crop_code, irrigation_code, moisture_code
        ]])
        raw = int(_model.predict(features)[0])
        return HEALTH_LABEL_MAP.get(raw, "moderate")

    # ── Fallback stub (rule-based) ────────────────────────────────────────────
    if soil_moisture == "dry" and irrigation_level == "low":
        return "dry"
    if soil_moisture == "wet" or irrigation_level == "high":
        return "healthy"
    return "moderate"


def estimate_carbon(water_usage_litres: float, farm_size_acres: float, energy_kwh: float = 0) -> float:
    water_emissions  = water_usage_litres * 0.0003
    land_emissions   = farm_size_acres * 0.5
    energy_emissions = energy_kwh * 0.4
    return round(water_emissions + land_emissions + energy_emissions, 2)


def get_carbon_grade(carbon_kg: float) -> tuple[str, str]:
    if carbon_kg < 1.5:
        return "A", "Low carbon footprint - excellent!"
    elif carbon_kg < 3.0:
        return "B", "Moderate carbon footprint - room to improve"
    return "C", "High carbon footprint - action needed"


def get_recommendation(health_status: str, crop_type: str, carbon_kg: float, farm_size: float) -> str:
    """Tries Groq first, then Gemini, then returns a sensible fallback.
    Neither key is required — the API still works without them for the demo."""
    prompt = f"""
    You are an agricultural advisor for smallholder farmers in East Africa.
    Farm details:
    - Crop: {crop_type}
    - Farm health status: {health_status}
    - Farm size: {farm_size} acres
    - Carbon footprint: {carbon_kg} kg CO2
    Give exactly 3 practical recommendations.
    Rules:
    - Each recommendation must be 1 sentence only
    - Use simple English that a farmer can understand
    - Number them 1, 2, 3
    - Do not use technical jargon
    """
    fallback = (
        f"1. Monitor your {crop_type} farm regularly and check soil moisture levels.\n"
        f"2. Your farm is currently {health_status} — adjust irrigation accordingly.\n"
        f"3. Estimated carbon footprint is {carbon_kg} kg CO2 — consider reducing water usage to lower it."
    )

    # ── Groq (active when GROQ_API_KEY is set) ───────────────────────────────
    groq_key   = os.getenv("GROQ_API_KEY")
    groq_model = os.getenv("GROQ_MODEL", "llama3-8b-8192")
    if groq_key:
        try:
            from groq import Groq
            client = Groq(api_key=groq_key)
            response = client.chat.completions.create(
                model=groq_model,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content
        except Exception:
            pass   # fall through to Gemini or fallback

    # ── Gemini (active when GEMINI_API_KEY is set) ───────────────────────────
    gemini_key = os.getenv("GEMINI_API_KEY")
    if gemini_key:
        try:
            from google import genai
            client = genai.Client(api_key=gemini_key)
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt
            )
            return response.text
        except Exception:
            pass

    return fallback