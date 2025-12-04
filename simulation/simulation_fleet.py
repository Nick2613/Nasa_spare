import pandas as pd
import requests
import time

API_URL = "http://localhost:8000/predict"
DATA_PATH = "data/train_FD001.txt"

def stream_data():
    print(f"🚀 Loading NASA Data from {DATA_PATH}...")
    try:
        # Load NASA data (Space separated)
        df = pd.read_csv(DATA_PATH, sep=r"\s+", header=None)
    except FileNotFoundError:
        print("❌ Data file not found! Run 'python data/download_data.py'")
        return

    # Filter for Engine #1 only (to show degradation)
    engine_data = df[df[0] == 1]
    print(f"📡 Streaming {len(engine_data)} cycles for Engine 1...")

    for index, row in engine_data.iterrows():
        # DATA MAPPING & NORMALIZATION
        # We need to scale NASA data to trigger our API thresholds (Temp > 400)
        
        # NASA Col 8 (Sensor 4) -> Map to Temp (300-450)
        raw_temp = row[8]
        scaled_temp = 320 + (raw_temp - 1300) * 15 
        
        # NASA Col 15 (Sensor 11) -> Map to Vibration (0.1 - 0.8)
        raw_vib = row[15]
        scaled_vib = (raw_vib - 47) / 1.5

        payload = {
            "vehicle_id": f"NASA-ENG-1",
            "sensor_1": float(row[5]),        # RPM
            "sensor_2": abs(float(scaled_vib)), # Vib
            "sensor_3": float(scaled_temp),     # Temp
            "timestamp": time.strftime("%H:%M:%S")
        }

        try:
            requests.post(API_URL, json=payload)
            print(f"Sent Cycle {int(row[1])}: Temp={scaled_temp:.1f} Vib={scaled_vib:.2f}")
        except:
            print("❌ API Down")

        time.sleep(1) # Send 1 data point per second

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
