# Nasa_spare

# 🚛 Real-Time Predictive Maintenance & Automated Supply Chain

![Python](https://img.shields.io/badge/Python-3.9-blue) ![FastAPI](https://img.shields.io/badge/FastAPI-Serving-green) ![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-red) ![Docker](https://img.shields.io/badge/Docker-Infrastructure-blue) ![Redpanda](https://img.shields.io/badge/Redpanda-Streaming-orange)

### 📖 Project Overview
This project is an **End-to-End MLOps system** designed for the automotive industry. It goes beyond simple "failure prediction" by automating the **Action Layer** of the supply chain.

It simulates a fleet of trucks streaming sensor data in real-time. The system predicts **Remaining Useful Life (RUL)**, diagnoses specific component failures (Brakes vs. Engine), and checks a live Inventory Database. **If a part is out of stock, the system automatically triggers a supplier order.**

### 🏗️ Architecture
The project uses a **Modern Data Stack** optimized for local development (Codespaces friendly):

1.  **Data Source:** NASA Turbofan Jet Engine Dataset / Live Simulation.
2.  **Streaming:** **Redpanda** (Kafka-compatible, lightweight) for data ingestion.
3.  **Model Registry:** **MLflow** for tracking model versions.
4.  **Serving Layer:** **FastAPI** acts as the central brain, handling predictions and business logic.
5.  **User Interface:** **Streamlit** provides an interactive Command Center for fleet managers.

---

### 📂 Directory Structure
```text
auto-spare-parts-mlops/
├── .devcontainer/          # GitHub Codespaces configuration
├── data/                   # Raw datasets (NASA Turbofan)
│   └── download_data.py    # Script to fetch data from Kaggle
├── serving/
│   └── app.py              # FastAPI (The Brain: Prediction + Inventory Logic)
├── simulation/
│   └── simulate_fleet.py   # Kafka Producer (The Vehicle Simulator)
├── dashboard.py            # Streamlit UI (The Control Center)
├── docker-compose.yaml     # Infrastructure (Redpanda, MLflow, Redis)
└── requirements.txt        # Python dependencies
```

---

### ⚡ Prerequisite Setup
You need **Docker** and **Python 3.9+** installed. If using GitHub Codespaces, this is pre-installed.

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/your-username/auto-spare-parts-mlops.git
    cd auto-spare-parts-mlops
    ```

2.  **Install Python Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Start Infrastructure (Redpanda & MLflow)**
    This spins up the Message Broker and Model Registry in the background.
    ```bash
    docker-compose up -d
    ```

---

### 🚀 How to Run the Project
To see the full system in action, you will need **Two Terminal Windows**.

#### Step 1: Start the "Brain" (API)
Open **Terminal 1** and run the FastAPI server. This handles the logic.
```bash
python serving/app.py
```
*   *Status:* You will see `Uvicorn running on http://0.0.0.0:8000`

#### Step 2: Start the "Control Center" (Dashboard)
Open **Terminal 2** and run the Streamlit dashboard.
```bash
streamlit run dashboard.py
```
*   *Status:* A browser tab will open (or click the URL printed in the terminal).

---

### 🎮 Demo Scenarios
Use the Dashboard to simulate real-world fleet problems.

#### Scenario 1: The Healthy Truck 🟢
1.  Enter Vehicle ID: `TRUCK-001`
2.  Set **Temperature** to `350` (Safe).
3.  Set **Vibration** to `0.02` (Safe).
4.  Click **Analyze Vehicle Health**.
    *   **Result:** System Healthy. No Inventory used.

#### Scenario 2: Brake Failure (Inventory Available) 🟡
1.  Set **Temperature** to `350` (Safe).
2.  Set **Vibration** to `0.8` (High - Danger!).
3.  Ensure Sidebar Inventory for **PART_BRAKE_PAD** is `> 0`.
4.  Click **Analyze**.
    *   **Result:** Maintenance Required.
    *   **Action:** `✅ High Vibration: Reserved PART_BRAKE_PAD`.
    *   *Note:* Watch the Sidebar inventory count drop!

#### Scenario 3: Engine Overheat (Out of Stock) 🔴
1.  Go to Sidebar: Set **PART_ENGINE_BELT** to `0` and click **Update**.
2.  Set **Temperature** to `480` (Overheating).
3.  Set **Vibration** to `0.02` (Safe).
4.  Click **Analyze**.
    *   **Result:** Critical Failure.
    *   **Action:** `🚨 Overheating: PART_ENGINE_BELT OUT OF STOCK. Auto-order Triggered.`
    *   *Check Terminal 1:* You will see the background task contacting the Supplier API.

---

### 🛠️ Tech Stack Details
*   **FastAPI:** Chosen for its asynchronous capabilities (handling `BackgroundTasks` for supplier ordering without blocking the UI).
*   **Redpanda:** Used instead of Apache Kafka because it is written in C++, requires no Zookeeper, and uses 1/3 of the RAM (ideal for Codespaces/Laptops).
*   **Streamlit:** Allows for rapid prototyping of the interactive frontend without needing React/HTML knowledge.

### 🔮 Future Improvements
*   Replace simulated logic with an **LSTM Deep Learning Model** trained on the NASA dataset.
*   Connect the "Supplier API" to a real email service (SendGrid) to send actual emails.
*   Deploy to Kubernetes using Helm Charts.