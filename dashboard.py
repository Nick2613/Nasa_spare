import streamlit as st
import requests
import time
import datetime

API_URL = "http://localhost:8000"

st.set_page_config(page_title="Auto MLOps Center", layout="wide")
st.title("🚛 Intelligent Fleet Command Center")

# --- SIDEBAR: INVENTORY ---
st.sidebar.header("🏭 Warehouse Manager")
try:
    inv_resp = requests.get(f"{API_URL}/")
    current_inventory = inv_resp.json().get("inventory", {})
except:
    st.error("API Offline. Run 'python serving/app.py'")
    current_inventory = {}

for part, qty in current_inventory.items():
    st.sidebar.markdown(f"**{part}**")
    new_qty = st.sidebar.number_input("Qty", value=qty, min_value=0, key=f"in_{part}_{qty}")
    if st.sidebar.button(f"Update {part}", key=f"btn_{part}"):
        requests.post(f"{API_URL}/inventory/update", params={"part_name": part}, json={"quantity": new_qty})
        st.rerun()

st.sidebar.markdown("---")

# --- LIVE STREAM TOGGLE ---
st.subheader("📡 Data Source Selector")
mode = st.radio("Select Mode:", ["Manual Inspection", "Live NASA Data Stream"], horizontal=True)

if mode == "Manual Inspection":
    col1, col2 = st.columns(2)
    with col1:
        temp = st.slider("Engine Temp (Sensor 3)", 300.0, 500.0, 350.0)
    with col2:
        vib = st.slider("Vibration (Sensor 2)", 0.0, 1.0, 0.02)
    
    if st.button("Analyze Vehicle"):
        payload = {
            "vehicle_id": "MANUAL-TEST", 
            "sensor_1": 6000, 
            "sensor_2": vib, 
            "sensor_3": temp, 
            "timestamp": datetime.datetime.now().isoformat()
        }
        resp = requests.post(f"{API_URL}/predict", json=payload).json()
        
        st.info(f"Action: {resp['action_taken']}")
        st.metric("RUL", resp['predicted_rul'])
        st.json(resp['inventory_snapshot'])

elif mode == "Live NASA Data Stream":
    st.info("Reading live data from 'serving/app.py'...")
    
    # Auto-Refresh Loop
    placeholder = st.empty()
    
    try:
        live_data = requests.get(f"{API_URL}/live_stream").json()
        
        with placeholder.container():
            c1, c2, c3 = st.columns(3)
            c1.metric("Vehicle ID", live_data['vehicle_id'])
            
            sensors = live_data.get('sensors', {})
            c2.metric("Temp", f"{sensors.get('temp', 0):.1f} °C")
            c2.metric("Vibration", f"{sensors.get('vib', 0):.3f}")
            
            c3.metric("RUL", live_data.get('prediction', {}).get('rul', 'N/A'))
            
            st.warning(f"System Action: {live_data['action']}")
            
            st.subheader("Live Inventory Impact")
            st.json(requests.get(f"{API_URL}/").json()['inventory'])

        time.sleep(1)
        st.rerun()
        
    except Exception as e:
        st.error(f"Waiting for stream... {e}")
