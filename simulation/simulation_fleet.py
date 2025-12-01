import pandas as pd
import time
import requests
import random
import json

# CONFIGURATION
API_URL = "http://localhost:8000/predict"
# If you haven't downloaded the NASA data yet, set this to TRUE to generate fake data
USE_FAKE_DATA = True 
DATA_FILE_PATH = "data/train_FD001.txt" # Path to NASA dataset if you have it

def generate_fake_sensor_data(vehicle_id):
    """
    Generates random sensor data if no CSV is available.
    Simulates a degrading engine (temp goes up over time).
    """
    # Simulate gradual heating up
    base_temp = 380 + random.randint(-10, 50) 
    
    return {
        "vehicle_id": vehicle_id,
        "sensor_1": 6000.0 + random.uniform(-50, 50),   # RPM
        "sensor_2": 0.02 + random.uniform(0, 0.05),     # Vibration
        "sensor_3": float(base_temp),                   # Temperature (Critical Feature)
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }

def read_and_stream_csv(csv_path):
    """
    Reads the NASA dataset and streams it.
    """
    try:
        # NASA dataset usually has space-separated values and no header
        # Columns: [unit_number, time_in_cycles, setting1, setting2, setting3, s1, s2... s21]
        # We map specific columns to our sensor names
        df = pd.read_csv(csv_path, sep=" ", header=None)
        df = df.dropna(axis=1, how='all') # Clean up weird spaces
        
        print(f"Loaded dataset with {len(df)} rows.")
        
        for index, row in df.iterrows():
            payload = {
                "vehicle_id": f"VEHICLE_{int(row[0])}",
                "sensor_1": float(row[5]),  # Column 5 is a sensor in NASA data
                "sensor_2": float(row[6]),
                "sensor_3": float(row[7]),  # Mapping specific columns
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            yield payload
            
    except FileNotFoundError:
        print("❌ CSV File not found. Switching to FAKE DATA mode.")
        global USE_FAKE_DATA
        USE_FAKE_DATA = True

def run_simulation():
    print("-------------------------------------------------")
    print(f"🚀 STARTING FLEET SIMULATION -> Targeting {API_URL}")
    print("-------------------------------------------------")

    vehicle_ids = ["TRUCK-A", "TRUCK-B", "TRUCK-C"]
    
    # If using CSV, we create a generator
    csv_generator = None
    if not USE_FAKE_DATA:
        csv_generator = read_and_stream_csv(DATA_FILE_PATH)

    try:
        while True:
            # 1. GET DATA (From CSV or Fake Generator)
            if USE_FAKE_DATA:
                # Pick a random truck and generate data
                vid = random.choice(vehicle_ids)
                data = generate_fake_sensor_data(vid)
            else:
                # Get next row from CSV
                try:
                    data = next(csv_generator)
                except StopIteration:
                    print("End of CSV file.")
                    break
                except TypeError: # Fallback if generator failed
                     vid = random.choice(vehicle_ids)
                     data = generate_fake_sensor_data(vid)

            # 2. SEND DATA TO API
            try:
                response = requests.post(API_URL, json=data)
                
                # 3. PROCESS RESPONSE
                if response.status_code == 200:
                    result = response.json()
                    
                    # Pretty Print Logic
                    status_icon = "✅"
                    if result['maintenance_required']:
                        status_icon = "🚨"
                    
                    print(f"[{data['timestamp']}] {status_icon} {result['vehicle_id']} | "
                          f"Temp: {data['sensor_3']:.1f} | "
                          f"RUL: {result['predicted_rul']} | "
                          f"Action: {result['action_taken']}")
                else:
                    print(f"Error: API returned {response.status_code}")

            except requests.exceptions.ConnectionError:
                print("❌ Could not connect to API. Is 'app.py' running?")
                break

            # 4. SLEEP (Simulate real-time delay)
            time.sleep(1) # Send 1 data point every second

    except KeyboardInterrupt:
        print("\n🛑 Simulation Stopped.")

if __name__ == "__main__":
    run_simulation()