"""
Connects Virginia's farm_health_model.pkl + the carbon formula + Gemini
recommendations to the rest of the backend.

NOTE FOR VIRGINIA (read this before sending the .pkl file):
The training script in the AI guide reuses a single LabelEncoder across the
crop_type / irrigation_level / soil_moisture columns and never saves it. That
means the integer codes the model learned during training aren't recoverable
on the backend side, and predictions will be wrong unless we agree on a fixed
mapping ahead of time.

This file defines that fixed mapping below (CROP_TYPE_MAP, IRRIGATION_MAP,
SOIL_MOISTURE_MAP, HEALTH_LABELS). Please retrain your model using these
exact codes instead of letting LabelEncoder pick them based on alphabetical
order of whatever happens to be in your CSV — otherwise "maize" might mean
0 in your training data and 3 here, and the model's predictions will be
silently wrong even though nothing throws an error.

Easiest fix on your end: instead of LabelEncoder, do
    df['crop_type'] = df['crop_type'].str.lower().map(CROP_TYPE_MAP)
(copy the dicts from this file) before training, so both sides agree.
"""

import os
import pickle
from pathlib import Path

MODEL_PATH = Path(__file__).parent / "farm_health_model.pkl"

# --- Fixed category mappings (must match what Virginia trains on) ---
CROP_TYPE_MAP = {
    "maize": 0, "beans": 1, "wheat": 2, "rice": 3, "sorghum": 4,
    "cassava": 5, "potato": 6, "tomato": 7, "coffee": 8, "tea": 9,
}
IRRIGATION_MAP = {"low": 0, "medium": 1, "high": 2}
SOIL_MOISTURE_MAP = {"dry": 0, "moderate": 1, "wet": 2}
HEALTH_LABELS = {0: "dry", 1: "healthy", 2: "moderate"}  # confirm order matches Virginia's training

_model = None
if MODEL_PATH.exists():
    with open(MODEL_PATH, "rb") as f:
        _model = pickle.load(f)


def predict_health(
    crop_type: str, farm_size_acres: float, irrigation_level: str, soil_moisture: str
) -> str:
    """Runs Virginia's model if farm_health_model.pkl is present next to this
    file. Otherwise falls back to a simple rule so the API keeps working
    while the model isn't ready yet — drop the .pkl in and it's used
    automatically, no code changes needed."""
    if _model is not None:
        crop_code = CROP_TYPE_MAP.get(crop_type.lower(), -1)
        irrigation_code = IRRIGATION_MAP.get(irrigation_level.lower(), -1)
        moisture_code = SOIL_MOISTURE_MAP.get(soil_moisture.lower(), -1)
        prediction = _model.predict([[crop_code, farm_size_acres, irrigation_code, moisture_code]])
        return HEALTH_LABELS.get(int(prediction[0]), "moderate")

    # --- Fallback stub (rule-based), used until the real model is dropped in ---
    moisture = soil_moisture.lower()
    irrigation = irrigation_level.lower()
    if moisture == "dry" and irrigation == "low":
        return "dry"
    if moisture == "wet" or irrigation == "high":
        return "healthy"
    return "moderate"


def estimate_carbon(water_usage_litres: float, farm_size_acres: float, energy_kwh: float = 0) -> float:
    """Carbon estimation formula from IPCC factors (Section 3.2 of the AI guide)."""
    water_emissions = water_usage_litres * 0.0003   # kg CO2 per litre
    land_emissions = farm_size_acres * 0.5           # kg CO2 per acre
    energy_emissions = energy_kwh * 0.4              # kg CO2 per kWh
    return round(water_emissions + land_emissions + energy_emissions, 2)


def get_recommendation(health_status: str, crop_type: str, carbon_kg: float) -> str:
    """Calls Gemini for farmer-friendly advice. Falls back to a canned
    message if GEMINI_API_KEY isn't set or the call fails, so a flaky
    connection during the demo doesn't take down the whole response."""
    api_key = os.getenv("GEMINI_API_KEY")
    fallback = (
        f"Your {crop_type} farm is currently {health_status}. "
        "Check soil moisture regularly and adjust irrigation as needed."
    )
    if not api_key:
        return fallback

    try:
        import google.generativeai as genai

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-pro")
        prompt = f"""
        A farmer in East Africa is growing {crop_type}.
        Their farm health status is: {health_status}.
        Their estimated carbon footprint is: {carbon_kg} kg CO2.
        Give 3 short, practical recommendations in simple English.
        Keep each recommendation under 20 words.
        """
        response = model.generate_content(prompt)
        return response.text
    except Exception:
        return fallback