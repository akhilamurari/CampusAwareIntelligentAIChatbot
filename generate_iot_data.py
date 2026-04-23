import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# ─── Config ────────────────────────────────────────────
# Expanded from 11 to 17 rooms
ROOMS = [
    # Libraries
    "Library-L1", "Library-L2", "Library-L3",
    # Labs
    "Lab-101", "Lab-102", "Lab-203",
    "Lab-301", "Lab-302",           # ← NEW labs
    # Lecture Halls
    "Lecture-Hall-A", "Lecture-Hall-B",
    "Lecture-Hall-C",               # ← NEW lecture hall
    # Study Rooms
    "Study-Room-1", "Study-Room-2",
    "Study-Room-3",                 # ← NEW study room
    # Other Spaces
    "Cafeteria",
    "Meeting-Room-1",               # ← NEW meeting room
    "Student-Lounge",               # ← NEW student lounge
]

DAYS = 30          # how many days of data
INTERVAL_MINS = 15 # reading every 15 minutes

# ─── Helpers ───────────────────────────────────────────
def is_occupied(hour, room):
    """Simulate occupancy based on time of day and room type"""
    if "Library" in room:
        return 8 <= hour <= 21
    elif "Cafeteria" in room:
        return hour in [8, 9, 12, 13, 17, 18]
    elif "Lecture" in room:
        return hour in [9, 10, 11, 13, 14, 15, 16]
    elif "Meeting" in room:
        return hour in [9, 10, 11, 13, 14, 15, 16]
    elif "Lounge" in room:
        return 9 <= hour <= 20
    else:
        return 8 <= hour <= 20

def generate_reading(room, timestamp):
    hour = timestamp.hour
    occupied = is_occupied(hour, room)
    occ_factor = 1.0 if occupied else 0.1

    # ── Sprint 4: Added air_quality_index as new sensor type ──
    co2 = round(np.random.normal(400 + occ_factor * 600, 80), 2)
    humidity = round(np.random.normal(45 + occ_factor * 10, 5), 2)
    noise = round(np.random.normal(30 + occ_factor * 25, 5), 2)

    # Air quality index based on CO2 and humidity (new sensor)
    if co2 < 600:
        air_quality = "Good"
    elif co2 < 800:
        air_quality = "Moderate"
    elif co2 < 1000:
        air_quality = "Poor"
    else:
        air_quality = "Very Poor"

    return {
        "timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
        "room_id": room,
        "temperature_c": round(np.random.normal(22 + occ_factor * 3, 1.5), 2),
        "humidity_pct": humidity,
        "co2_ppm": co2,
        "noise_db": noise,
        "light_lux": round(np.random.normal(100 + occ_factor * 400, 50), 2),
        "occupancy": 1 if occupied else 0,
        "air_quality": air_quality,   # ← NEW sensor type
    }

# ─── Generate Data ─────────────────────────────────────
records = []
start = datetime.now() - timedelta(days=DAYS)

for day in range(DAYS):
    for room in ROOMS:
        current = start + timedelta(days=day)
        current = current.replace(hour=0, minute=0, second=0)
        while current.date() == (start + timedelta(days=day)).date():
            records.append(generate_reading(room, current))
            current += timedelta(minutes=INTERVAL_MINS)

# ─── Save ──────────────────────────────────────────────
df = pd.DataFrame(records)
df.to_csv("data/iot_sensor_data.csv", index=False)
print(f"✅ Generated {len(df)} records for {len(ROOMS)} rooms over {DAYS} days")
print(f"📊 Rooms: {ROOMS}")
print(f"📊 Columns: {list(df.columns)}")
print(df.head())
print(df.describe())