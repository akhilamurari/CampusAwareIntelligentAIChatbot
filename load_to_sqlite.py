import sqlite3
import pandas as pd
import os
 
# ─── Config ─────────────────────────────
CSV_PATH = "data/iot_sensor_data.csv"
DB_PATH = "data/campus.db"
 
# ─── Load CSV ───────────────────────────
print("🔄 Loading CSV...")
df = pd.read_csv(CSV_PATH)
print(f"✅ Loaded {len(df)} records from CSV")
 
# ─── Connect to SQLite ──────────────────
print("🔄 Creating SQLite database...")
os.makedirs("data", exist_ok=True)
conn = sqlite3.connect(DB_PATH)
 
# ─── Create Table ───────────────────────
conn.execute("""
    CREATE TABLE IF NOT EXISTS room_telemetry (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp DATETIME,
        room_id TEXT,
        temperature_c REAL,
        humidity_pct REAL,
        co2_ppm REAL,
        noise_db REAL,
        light_lux REAL,
        occupancy INTEGER
    )
""")
print("✅ Table created")
 
# ─── Load Data ──────────────────────────
df.to_sql("room_telemetry", conn,
          if_exists="replace",
          index=False)
print(f"✅ Loaded {len(df)} records into SQLite")
 
# ─── Verify ─────────────────────────────
print("\n🔍 Running test queries...")
 
# Test 1: Count records
count = conn.execute("SELECT COUNT(*) FROM room_telemetry").fetchone()[0]
print(f"Total records: {count}")
 
# Test 2: High CO2 rooms
print("\nRooms with high CO2 (>1000 ppm):")
result = conn.execute("""
    SELECT room_id, ROUND(AVG(co2_ppm), 2) as avg_co2
    FROM room_telemetry
    WHERE co2_ppm > 1000
    GROUP BY room_id
    ORDER BY avg_co2 DESC
    LIMIT 5
""").fetchall()
for row in result:
    print(f"  {row[0]}: {row[1]} ppm")
 
# Test 3: Most occupied room
print("\nMost occupied rooms:")
result = conn.execute("""
    SELECT room_id, SUM(occupancy) as total_occupied
    FROM room_telemetry
    GROUP BY room_id
    ORDER BY total_occupied DESC
    LIMIT 3
""").fetchall()
for row in result:
    print(f"  {row[0]}: {row[1]} hours occupied")
 
conn.close()
print("\n✅ SQLite database setup complete!")
print(f"💾 Database saved to: {DB_PATH}")