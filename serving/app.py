import uvicorn
from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import random
import time

app = FastAPI(title="Auto Spare Parts System", version="3.0")

# Enable CORS for Streamlit
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- GLOBAL STATE (For Dashboard Visualization) ---
latest_vehicle_state = {
    "vehicle_id": "Waiting...",
    "timestamp": "N/A",
    "sensors": {},
    "prediction": {},
    "action": "N/A"
}

# --- DATABASE ---
inventory_db = {
    "PART_BRAKE_PAD": 5,
    "PART_ENGINE_BELT": 10,
    "PART_FILTER": 20
}

# --- MODELS ---
class SensorReadings(BaseModel):
    vehicle_id: str
    sensor_1: float
    sensor_2: float
    sensor_3: float
    timestamp: str

class InventoryUpdate(BaseModel):
    quantity: int

# --- LOGIC ---
def call_supplier_api(part_id: str, quantity: int):
    time.sleep(1) # Simulate network
    print(f"⚡ [SUPPLIER] ORDER SENT: {quantity} x {part_id}")

@app.get("/")
def health_check():
    return {"status": "active", "inventory": inventory_db}

@app.get("/live_stream")
def get_live_stream():
    """Endpoint for Dashboard to fetch the latest streamed data point"""
    return latest_vehicle_state

@app.post("/inventory/update")
def update_inventory(part_name: str, update: InventoryUpdate):
    if part_name not in inventory_db:
        raise HTTPException(status_code=404, detail="Part not found")
    inventory_db[part_name] = update.quantity
    return {"message": "Updated", "inventory": inventory_db}

@app.post("/predict")
async def predict_maintenance(data: SensorReadings, background_tasks: BackgroundTasks):
    global latest_vehicle_state

    # 1. Prediction Logic (Simulated Model)
    # Thresholds: Temp > 400 OR Vib > 0.5
    is_overheating = data.sensor_3 > 400
    is_vibrating = data.sensor_2 > 0.5
    
    if is_overheating or is_vibrating:
        predicted_rul = random.randint(5, 20) # Critical
    else:
        predicted_rul = random.randint(100, 200) # Healthy

    maintenance_required = predicted_rul < 30
    action_msg = "No Action Needed"

    # 2. Business Logic
    if maintenance_required:
        if is_overheating and is_vibrating:
            part_needed = "PART_FILTER"
            reason = "Major Failure"
        elif is_overheating:
            part_needed = "PART_ENGINE_BELT"
            reason = "Overheating"
        else:
            part_needed = "PART_BRAKE_PAD"
            reason = "Vibration"
            
        # Inventory Check
        stock = inventory_db.get(part_needed, 0)
        if stock > 0:
            inventory_db[part_needed] -= 1
            action_msg = f"✅ {reason}: Reserved {part_needed}"
        else:
            background_tasks.add_task(call_supplier_api, part_needed, 1)
            action_msg = f"🚨 {reason}: {part_needed} OUT OF STOCK. Ordered."

    # 3. Save State for Dashboard
    latest_vehicle_state = {
        "vehicle_id": data.vehicle_id,
        "timestamp": data.timestamp,
        "sensors": {"temp": data.sensor_3, "vib": data.sensor_2},
        "prediction": {"rul": predicted_rul, "maintenance": maintenance_required},
        "action": action_msg
    }

    return {
        "vehicle_id": data.vehicle_id,
        "predicted_rul": predicted_rul,
        "action_taken": action_msg,
        "inventory_snapshot": inventory_db.copy()
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
