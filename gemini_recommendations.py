# gemini_recommendations.py
# GLAM Team — Shamba Agricultural OS
# AYSC Hackathon 2026 — Virginia Muranga, AI & Data Analyst

import os
from dotenv import load_dotenv

load_dotenv()

# ── GROQ (active) ────────────────────────────────────────────────────
from groq import Groq
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# ── GEMINI (uncomment when key arrives) ─────────────────────────────
# from google import genai
# client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def get_recommendation(health_status, crop_type, carbon_kg, farm_size):
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

    # ── GROQ response (active) ───────────────────────────────────────
    response = client.chat.completions.create(
        model=os.getenv("GROQ_MODEL"),
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

    # ── GEMINI response (uncomment when key arrives) ─────────────────
    # response = client.models.generate_content(
    #     model=os.getenv("GEMINI_MODEL"),
    #     contents=prompt
    # )
    # return response.text


if __name__ == "__main__":
    print("Testing recommendations...\n")
    advice = get_recommendation(
        health_status="moderate",
        crop_type="maize",
        carbon_kg=2.5,
        farm_size=2
    )
    print("Recommendations:")
    print(advice)