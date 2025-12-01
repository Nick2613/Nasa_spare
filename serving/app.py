import uvicorn
from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import random
import time

# --- 1. APP CONFIGURATION ---
app = FastAPI(
    title="Auto Spare Parts Intelligent System",
    description="Real-time RUL prediction and automated ordering logic",
    version="2.0"
)

# Allow connections from Streamlit (Cross-Origin Resource Sharing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 2. MOCK DATABASE (IN-MEMORY) ---
# In a real app, this would be SQLite or PostgreSQL
inventory_db = {
    "PART_BRAKE_PAD": 5,
    "PART_ENGINE_BELT": 10,
    "PART_FILTER": 20
}

# --- 3. DATA MODELS ---
class SensorReadings(BaseModel):
    vehicle_id: str
    sensor_1: float  # RPM
    sensor_2: float  # Vibration (0.0 to 1.0)
    sensor_3: float  # Temperature (300 to 600)
    timestamp: str

class InventoryUpdate(BaseModel):
    quantity: int

# --- 4. HELPER FUNCTIONS ---
def call_supplier_api(part_id: str, quantity: int):
    """
    Simulates a background API call to an external supplier (e.g., Bosch).
    """
    time.sleep(2) # Simulate network delay
    print(f"\n⚡ [SUPPLIER API] ORDER PLACED: {quantity} x {part_id}")
    print(f"   -> Status: Confirmed | ETA: 24 Hours\n")

# --- 5. API ENDPOINTS ---

@app.get("/")
def health_check():
    """Returns system status and current inventory levels."""
    return {"status": "active", "inventory": inventory_db}

@app.post("/inventory/update")
def update_inventory(part_name: str, update: InventoryUpdate):
    """Allows the Dashboard to manually update stock levels."""
    if part_name not in inventory_db:
        raise HTTPException(status_code=404, detail="Part not found in database")
    
    inventory_db[part_name] = update.quantity
    return {"message": f"Updated {part_name} to {update.quantity}", "current_stock": inventory_db}

@app.post("/predict")
async def predict_maintenance(data: SensorReadings, background_tasks: BackgroundTasks):
    """
    The Core Logic:
    1. Check Sensor Data (Simulation).
    2. Predict RUL (Model).
    3. Diagnose specific failure (Business Logic).
    4. Check Inventory & Order Parts (Automation).
    """
    
    # --- A. PREDICTION LAYER (Simulating the ML Model) ---
    # Define thresholds for "Failure"
    THRESHOLD_TEMP = 400.0  # Overheating
    THRESHOLD_VIB = 0.2     # Unstable Vibration
    
    is_overheating = data.sensor_3 > THRESHOLD_TEMP
    is_vibrating = data.sensor_2 > THRESHOLD_VIB
    
    # If sensors are bad, RUL is low (Critical)
    if is_overheating or is_vibrating:
        predicted_rul = random.randint(5, 20) 
    else:
        predicted_rul = random.randint(100, 200)

    maintenance_required = predicted_rul < 30
    action_msg = "No Action Needed"
    
    # --- B. DIAGNOSTIC LAYER (The "Brain") ---
    if maintenance_required:
        part_needed = "PART_UNKNOWN"
        
        # Logic: Map Symptoms to Parts
        if is_overheating and is_vibrating:
             # If everything is shaking and hot -> Major Service
             part_needed = "PART_FILTER"
             reason = "Major Service (Heat + Vib)"
             
        elif is_overheating:
             # Heat usually indicates friction or belt issues
             part_needed = "PART_ENGINE_BELT"
             reason = "Overheating Detected"
             
        elif is_vibrating:
             # Vibration usually indicates brake or suspension issues
             part_needed = "PART_BRAKE_PAD"
             reason = "High Vibration Detected"
        
        # --- C. INVENTORY LAYER (The "Action") ---
        stock = inventory_db.get(part_needed, 0)
        
        if stock > 0:
            # We have it! Reserve it.
            inventory_db[part_needed] -= 1
            action_msg = f"✅ {reason}: Reserved {part_needed} (Remaining: {inventory_db[part_needed]})"
        else:
            # We don't have it! Order it.
            # We use background_tasks so the UI doesn't freeze waiting for the supplier
            background_tasks.add_task(call_supplier_api, part_needed, 1)
            action_msg = f"🚨 {reason}: {part_needed} OUT OF STOCK. Auto-order Triggered."

    # Return the full package to the Dashboard
    return {
        "vehicle_id": data.vehicle_id,
        "predicted_rul": predicted_rul,
        "maintenance_required": maintenance_required,
        "action_taken": action_msg,
        "inventory_snapshot": inventory_db.copy() # Send updated stock back to UI
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)