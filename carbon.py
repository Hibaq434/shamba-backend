# carbon.py
# GLAM Team — Shamba Agricultural OS
# Carbon Estimation based on IPCC emission factors

def estimate_carbon(water_usage_litres, farm_size_acres, energy_kwh=0):
    water_emissions  = water_usage_litres * 0.0003
    land_emissions   = farm_size_acres * 0.5
    energy_emissions = energy_kwh * 0.4
    total_carbon_kg  = water_emissions + land_emissions + energy_emissions
    return round(total_carbon_kg, 2)

def get_carbon_grade(carbon_kg):
    if carbon_kg < 1.5:
        return "A", "Low carbon footprint - excellent!"
    elif carbon_kg < 3.0:
        return "B", "Moderate carbon footprint - room to improve"
    else:
        return "C", "High carbon footprint - action needed"

if __name__ == "__main__":
    carbon = estimate_carbon(water_usage_litres=5000, farm_size_acres=2)
    grade, message = get_carbon_grade(carbon)
    print(f"Carbon footprint: {carbon} kg CO2")
    print(f"Grade: {grade} — {message}")