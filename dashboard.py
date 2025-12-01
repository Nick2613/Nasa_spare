import streamlit as st
import requests
import datetime

# CONFIGURATION
API_URL = "http://localhost:8000"

st.set_page_config(page_title="Auto MLOps Control Center", layout="wide")
st.title("🚛 Intelligent Fleet & Inventory Command Center")

# --- FETCH LATEST DATA AT START ---
try:
    response = requests.get(f"{API_URL}/")
    current_inventory = response.json().get("inventory", {})
except:
    st.error("⚠️ API is offline. Run 'python serving/app.py'")
    current_inventory = {}

# --- SIDEBAR: INVENTORY MANAGER ---
st.sidebar.header("🏭 Warehouse Manager")

# We iterate through the database items
for part, qty in current_inventory.items():
    st.sidebar.markdown(f"**{part}**")
    
    # TRICK: Add 'qty' to the key. If API changes, the widget resets!
    new_qty = st.sidebar.number_input(
        f"Stock Level", 
        value=qty, 
        min_value=0, 
        key=f"input_{part}_{qty}"  # <--- THIS IS THE MAGIC FIX
    )
    
    # Update Button Logic
    if st.sidebar.button(f"Update {part}", key=f"btn_{part}"):
        try:
            requests.post(f"{API_URL}/inventory/update", 
                          params={"part_name": part}, 
                          json={"quantity": new_qty})
            st.toast(f"✅ Updated {part} to {new_qty}!")
            import time
            time.sleep(0.5) # Give API a moment
            st.rerun() # Force page reload to show new values
        except Exception as e:
            st.sidebar.error(f"Failed: {e}")

st.sidebar.markdown("---")

# --- MAIN PAGE: VEHICLE ANALYSIS ---
st.header("🔧 Manual Vehicle Inspection")

col1, col2, col3 = st.columns(3)
with col1:
    vehicle_id = st.text_input("Vehicle ID", value="TRUCK-100")
with col2:
    sensor_temp = st.slider("Engine Temperature (Sensor 3)", 300.0, 600.0, 511.6)
with col3:
    sensor_vib = st.slider("Vibration Level (Sensor 2)", 0.0, 1.0, 0.02)

if st.button("🔍 Analyze Vehicle Health", use_container_width=True):
    
    payload = {
        "vehicle_id": vehicle_id,
        "sensor_1": 6000,
        "sensor_2": sensor_vib,
        "sensor_3": sensor_temp,
        "timestamp": datetime.datetime.now().isoformat()
    }
    
    try:
        resp = requests.post(f"{API_URL}/predict", json=payload)
        data = resp.json()
        
        # Display Logic
        st.divider()
        c1, c2 = st.columns([1, 2])
        
        with c1:
            st.metric("Predicted RUL", f"{data['predicted_rul']} Days")
            if data['maintenance_required']:
                st.error("MAINTENANCE REQUIRED")
            else:
                st.success("SYSTEM HEALTHY")
                
        with c2:
            st.subheader("Action Log")
            st.info(f"System Decision: {data['action_taken']}")
            
            # Show the "Live" inventory from the response
            st.json(data['inventory_snapshot'])

        # NOTE TO USER
        if data['maintenance_required']:
            st.warning("⚠️ Part consumed! Click 'Rerun' or press 'R' to sync the Sidebar.")

    except Exception as e:
        st.error(f"Connection Error: {e}")