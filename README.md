# AI-Based Smart Factory Production Optimization & Predictive Maintenance System

[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)
[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/)
[![Google OR-Tools](https://img.shields.io/badge/OR--Tools-9.15-orange.svg)](https://developers.google.com/optimization)
[![XGBoost](https://img.shields.io/badge/XGBoost-3.4-green.svg)](https://xgboost.readthedocs.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-purple.svg)](LICENSE)
[![Status: Production Ready](https://img.shields.io/badge/Status-Industrial%20Grade-brightgreen.svg)]()

An enterprise-grade, software-only **Industry 4.0 Digital Twin and Operational Decision Support System**. It integrates physics-informed machine degradation simulation, Machine Learning predictive maintenance (PdM), Remaining Useful Life (RUL) regression, production order delay risk forecasting, load-dependent dynamic energy modeling, and **Google OR-Tools CP-SAT multi-objective mathematical optimization**.

> 📖 **Looking for the deep technical walkthrough?** Check out the exhaustive [Detailed Operational Guide (GUIDE.md)](GUIDE.md) explaining how every subsystem, mathematical formula, physics equation, and ML model works in detail.

---

## 📸 System Showcase & Visual Tour

### 1. Digital Twin Factory Overview
*Real-time shop floor supervision of 6 industrial workstations across CNC, Robotic Assembly, and Hydraulic Injection cells.*

![Digital Twin Factory Overview](docs/screenshots/01_factory_overview.png)

---

### 2. AI Predictive Maintenance (PdM) & Diagnostic Gauges
*Sub-second failure probability estimation via XGBoost, Remaining Useful Life (RUL) regression via Random Forest, circular physical telemetry gauges, and prescriptive root-cause diagnostics.*

![Predictive Maintenance Studio](docs/screenshots/02_predictive_maintenance.png)

![Physical Sensor Gauges](docs/screenshots/02b_pdm_sensor_gauges.png)

---

### 3. AI Multi-Objective Production Optimizer & Gantt Schedule
*Constraint programming engine (Google OR-Tools CP-SAT) balancing tardiness, machine risk exposure, and energy tariffs. Displays quantitative Before vs. After metrics and dynamic shop floor Gantt timelines.*

![AI Production Optimizer](docs/screenshots/05_ai_production_optimizer.png)

![Optimized Gantt Schedule](docs/screenshots/05b_optimized_gantt_schedule.png)

---

### 4. Production Orders Queue & Backlog
*Job prioritization, machine compatibility matrices, cycle times, and real-time machine unreliability exposure risk scoring.*

![Production Orders Queue](docs/screenshots/03_production_orders.png)

---

### 5. Energy Consumption & Tariff Analytics
*Load-factor energy curves, mechanical wear friction penalties, peak-rate window avoidance ($0.28/kWh vs. $0.11/kWh), and 24-hour shop floor power profiles.*

![Energy and Power Analytics](docs/screenshots/04_energy_analytics.png)

---

### 6. What-If Simulation & 10-Step Guided Flow
*Automated end-to-end demonstration flow showing real-time closed-loop self-healing when mechanical anomalies are injected into the shop floor.*

![What-If Simulation Stepper](docs/screenshots/06_whatif_simulation.png)

![What-If Scenario Sandbox](docs/screenshots/07_whatif_sandbox.png)

---

### 7. ML Governance & Diagnostic Metrics
*Validation curves, confusion matrices, ROC-AUC curves, and feature importance rankings for predictive models.*

![ML Governance and Metrics](docs/screenshots/08_ml_governance_metrics.png)

---

## 🔄 Complete Industry 4.0 Closed-Loop Workflow

The application demonstrates the complete automated Industry 4.0 lifecycle:

$$\text{Physics Telemetry} \longrightarrow \text{Real-Time Monitoring} \longrightarrow \text{AI ML Prediction} \longrightarrow \text{Risk Detection} \longrightarrow \text{OR-Tools Optimization} \longrightarrow \text{Automated Decision} \longrightarrow \text{Factory Adaptation} \longrightarrow \text{Digital Twin UI}$$

```mermaid
graph TD
    A[Physics Telemetry Generator] -->|Temperature, Vibration, Pressure, Power| B[(SQLite Telemetry Store)]
    B --> C[Real-Time SCADA Digital Twin]
    B --> D[XGBoost Failure Predictor]
    B --> E[Random Forest RUL Regressor]
    D -->|Failure Probability P > 0.35| F[Risk Escalation Engine]
    E -->|RUL < 48 Hours| F
    G[Production Order Queue] --> H[Delay Risk Model]
    F --> I[Google OR-Tools CP-SAT Optimizer]
    G --> I
    J[Time-of-Use Energy Tariff Model] --> I
    I -->|Optimal Schedule & Machine Assignment| K[Automated Factory Rescheduling]
    K --> L[Shop Floor Adaptation & Maintenance Dispatch]
    L --> C
```

---

## 🌟 Core System Subsystems

### 1. Smart Factory Simulation (Digital Twin)
- **6 Industrial Workstations Across 3 Manufacturing Cell Types**:
  - `M1-CNC-01` & `M2-CNC-02`: High-precision 5-Axis CNC Milling Machines
  - `M3-ROB-01` & `M4-ROB-02`: Industrial Robotic Welding & Automated Assembly Arms
  - `M5-INJ-01` & `M6-INJ-02`: Heavy Hydraulic Injection Presses
- **High-Fidelity Physics-Based Telemetry**:
  - Temperature (°C), Vibration (mm/s RMS), Motor Spindle Speed (RPM), Hydraulic Pressure (bar), and Power Draw (kW).
  - Realistic stochastic noise, Weibull wear accumulation, thermal dissipation lag, and bearing harmonic resonance.
- **Dynamic State Machine**: `NORMAL`, `WARNING`, `CRITICAL`, `MAINTENANCE`, `FAILED`.

### 2. Predictive Maintenance (PdM) & Machine Health
- **XGBoost Classifier**: Predicts failure probability ($0.0$ to $1.0$) with calibrated decision boundaries.
- **Random Forest Regressor**: Predicts Remaining Useful Life (RUL in operating hours).
- **Prescriptive Diagnostics**: Root-cause detection (Coolant Loss, Bearing Wear, Overstrain, Tool Wear).
- **Physical Sensor Gauges**: Real-time circular dials with warning and critical alarm thresholds.

### 3. Production Order Management & Delay Prediction
- **Order Backlog**: Product codes, batch quantities, processing times, machine compatibility constraints, deadlines, and priorities (`Low`, `Medium`, `High`, `Urgent`).
- **Delay Risk Predictor**: Calculates tardiness probability based on machine unreliability exposure, queue bottlenecks, and deadline slack buffers.

### 4. Energy Consumption & Power Analytics
- **Machine Power Curves**: Baseline idle power + load-factor scaling + mechanical wear friction penalties.
- **Peak Tariff Avoidance**: Differentiates peak-tariff windows ($0.28/kWh from 14:00 to 19:00) vs. off-peak rates ($0.11/kWh).
- **24-Hour Factory Power Forecast**: Projected kWh and energy cost estimation.

### 5. Multi-Objective AI Scheduling Optimizer (Google OR-Tools CP-SAT)
- Formulates constraint programming / mixed integer scheduling:
  $$\min \sum_{j} w_j \cdot \text{Tardiness}_j + \sum_{j,m} x_{jm} \cdot \left(\text{RiskPenalty}_m + \text{EnergyCost}_m\right) + \alpha \cdot \text{Makespan}$$
- **Multi-Objective Trade-offs**:
  1. Minimize Order Delays (prioritizing urgent customer deadlines).
  2. Evacuate orders from high-risk or degraded machines ($P(\text{failure}) > 0.35$).
  3. Balance machine utilization and minimize power consumption.
- **Quantified Before vs. After Comparison**: Delays eliminated, late orders prevented, jobs shifted away from degraded machines, and kWh conserved.

### 6. What-If Simulation & 10-Step Demonstration Stepper
- Guided step-by-step presentation flow with one-click transitions:
  1. *Nominal baseline operation*
  2. *Continuous simulation run*
  3. *Anomaly injection on M1-CNC-01 (coolant loss + vibration surge)*
  4. *AI detects failure probability spike*
  5. *Machine transitions to CRITICAL alarm state*
  6. *Orders on M1 flag high delay risk*
  7. *Automated OR-Tools CP-SAT reschedule triggered*
  8. *Orders reallocated to healthy peer M2-CNC-02*
  9. *Before vs. After comparison metrics displayed*
  10. *Autonomous closed-loop adaptation verified*

---

## 🏗️ Project Architecture

```
Smart Factory Production Optimization/
├── config.py                 # System specs, machine profiles, sensor thresholds, catalog
├── app.py                    # Main Streamlit industrial SCADA dashboard
├── train_models.py           # Standalone ML training & evaluation script
├── test_system.py            # Automated end-to-end verification suite
├── capture_all_screenshots.py# Playwright automated screenshot generator
├── GUIDE.md                  # Comprehensive technical operation & architecture handbook
├── database/
│   ├── schema.sql            # SQLite schema (machines, telemetry, orders, logs, history)
│   └── db_manager.py         # SQLite connection manager & CRUD operations
├── data_generator/
│   └── telemetry_generator.py# Physics-based synthetic data generator
├── models/
│   ├── pdm_model.py          # Predictive maintenance classifier & RUL inference
│   ├── delay_model.py        # Order delay probability model
│   ├── energy_model.py       # Energy consumption & cost estimation model
│   └── saved/                # Serialized model artifacts (.joblib)
├── simulation/
│   └── factory_simulator.py  # Runtime state machine, step progression, anomaly injector
├── optimization/
│   └── scheduler.py          # Google OR-Tools CP-SAT multi-objective scheduler
├── docs/
│   └── screenshots/          # High-resolution dashboard screenshots
└── ui/
    ├── styles.py             # Industrial SCADA dark-mode CSS styling
    ├── components.py         # Plotly gauges, multi-axis charts, Gantt timelines, KPI cards
    └── views/
        ├── overview.py       # Digital Twin factory floor layout
        ├── maintenance.py    # PdM studio, sensor streams, overhaul actions
        ├── production.py     # Production order queue & dispatch form
        ├── energy.py         # Power analytics & 24h load profile
        ├── optimizer.py      # Production scheduler studio & Before/After diff
        ├── whatif.py         # What-If sandbox & 10-step guided demo
        └── model_metrics.py  # Confusion matrix, ROC-AUC, feature importances
```

---

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.10, 3.11, or 3.12
- `pip` package manager
- Google Chrome or Microsoft Edge (for automated screenshot generation)

### 2. Installation
Clone or navigate to the project directory and install the required dependencies:

```bash
pip install streamlit plotly scikit-learn xgboost ortools pandas numpy scipy playwright
```

### 3. Train Machine Learning Models (Optional - Pre-trained Artifacts Included)
To retrain the XGBoost classifier and Random Forest RUL regressor on 8,000 synthetic records:

```bash
python train_models.py
```

*Results achieved during training:*
- **Accuracy:** 99.94%
- **Precision:** 100.00%
- **Recall:** 99.55%
- **F1-Score:** 99.77%
- **ROC-AUC:** 1.0000
- **RUL RMSE:** 150.8 hours

### 4. Run Automated Tests
Verify all subsystems (Database, Physics Telemetry, PdM Inference, Simulator, OR-Tools Solver):

```bash
python test_system.py
```

### 5. Launch the Dashboard Locally
Run the Streamlit application:

```bash
streamlit run app.py
```

Access the interface in your browser at:
`http://localhost:8501`

### ☁️ 6. Deploy to Streamlit Community Cloud
This repository is pre-configured for one-click deployment on **Streamlit Community Cloud**:
1. Push this repository to your **GitHub** account.
2. Visit [share.streamlit.io](https://share.streamlit.io/) and log in with GitHub.
3. Click **"New app"** and fill in the details:
   - **Repository:** `your-username/Smart-Factory-Production-Optimization`
   - **Branch:** `main`
   - **Main file path:** `app.py`
4. Under **Advanced settings**, set Python version to `3.11` (or `3.12`).
5. Click **"Deploy!"**
   - The platform will automatically install packages from `requirements.txt`, system dependencies from `packages.txt`, and apply the industrial theme from `.streamlit/config.toml`.
   - SQLite auto-initializes and pre-trained XGBoost / Random Forest models are loaded out-of-the-box.

---

## 📊 Evaluation & Machine Learning Diagnostics

| Metric | Score | Description |
| :--- | :--- | :--- |
| **Accuracy** | **99.94%** | Test set classification accuracy |
| **Precision** | **100.00%** | Zero false alarms under nominal conditions |
| **Recall** | **99.55%** | Captures 99.5%+ of impending degradation events |
| **ROC-AUC** | **1.0000** | Perfect separation across decision thresholds |
| **Solver Speed** | **< 50 ms** | Google OR-Tools CP-SAT optimal schedule convergence |

### Top Predictive Feature Importances:
1. **Vibration (mm/s RMS)**: ~48.6% (Bearing wear, spindle eccentricity)
2. **Temperature (°C)**: ~27.8% (Coolant loss, thermal dissipation failure)
3. **Pressure (bar)**: ~12.4% (Hydraulic seal degradation)
4. **Operating Hours**: ~8.6% (Weibull fatigue accumulation)
5. **Power Draw (kW)**: ~1.6% (Mechanical friction overhead)

---

## 📚 In-Depth Documentation
For a complete, comprehensive, and exhaustive architectural breakdown, mathematical specifications, and scenario execution tutorials, read [GUIDE.md](GUIDE.md).

---

## 📜 License
MIT License. Built for Industry 4.0 simulation, research, and enterprise demonstration.
