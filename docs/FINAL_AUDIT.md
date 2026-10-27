# Smart Factory Production Optimization: Comprehensive Final Audit
## Exhaustive Codebase Inventory, Defect Classification & Verification Checklist

---

### Executive Summary

This audit represents an exhaustive, multi-disciplinary review of the **Smart Factory Production Optimization & Predictive Maintenance System** covering software engineering, industrial optimization, machine learning integrity, database persistence, and academic defense rigor.

Every subsystem, source file, database operation, mathematical model, and user interface component has been inspected. All defects identified in `BUGS_AND_SOLUTIONS.md` have been cross-referenced against the active code to verify whether fixes are present, complete, and mathematically sound. New defects, edge cases, and synchronization vulnerabilities identified during this audit have been cataloged with concrete remediation steps.

---

## 1. System Inventory & Architecture Trace

### 1.1 Source File & Component Inventory

| Component / File | Subsystem | Purpose & Data Flow Role |
| :--- | :--- | :--- |
| `config.py` | Configuration | Master system constants, 6 machine specifications, nominal/alarm sensor thresholds, product catalog, priority weights, and time-of-use tariffs ($0.28 vs $0.11/kWh). |
| `app.py` | UI Entry Point | Main Streamlit application runner, sidebar navigation, master simulation clock controls, theme switcher (`Dark SCADA` vs. `Clean Light`), and top-level KPI header bar. |
| `database/schema.sql` | Persistence DDL | Relational SQLite schema defining 5 core tables (`machines`, `telemetry`, `production_orders`, `maintenance_logs`, `optimization_history`) with indices and foreign keys. |
| `database/db_manager.py` | Persistence DAO | Context-managed SQLite connection pool (`PRAGMA foreign_keys = ON;`, `PRAGMA journal_mode = WAL;`), CRUD operations, collision-free order ID generation, batch telemetry writes, and database resets. |
| `data_generator/telemetry_generator.py` | Physics Engine | Physics-grounded synthetic telemetry generator modeling thermal dissipation lag, bearing harmonic resonance, hydraulic pressure drift, mechanical wear overhead, and balanced training set generation ($N=8000$). |
| `models/pdm_model.py` | ML Inference | Inference wrapper for serialized XGBoost binary failure classifier and Random Forest Remaining Useful Life (RUL) regressor, with analytical rule-based fallbacks. |
| `models/energy_model.py` | Physics Modeling | Workload- and wear-dependent power demand estimation, 24-hour diurnal power profile projection, and continuous interval calculus for time-of-use peak tariff calculation. |
| `models/delay_model.py` | Risk Prognostics | Sigmoid-based customer delivery deadline delay probability and expected tardiness calculation factoring in machine unreliability exposure and buffer slack. |
| `models/saved/` | Serialized Artifacts | `pdm_classifier.joblib`, `pdm_rul_regressor.joblib`, and `pdm_metrics.joblib` containing trained parameters and validation statistics. |
| `simulation/factory_simulator.py` | Digital Twin Runtime | Discrete simulation clock manager, machine degradation state machine (`NORMAL`, `WARNING`, `CRITICAL`, `MAINTENANCE`, `FAILED`), anomaly injector, maintenance countdowns, and order execution progress engine. |
| `optimization/scheduler.py` | Mathematical Solver | Google OR-Tools CP-SAT multi-objective constraint programming engine balancing weighted tardiness, machine unreliability risk penalties, nominal energy costs, makespan, and baseline FIFO comparative evaluation. |
| `ui/styles.py` | Presentation Layer | Industrial SCADA styling with dual-theme CSS palettes, glassmorphic containers, status badges, and animated pulse indicators. |
| `ui/components.py` | Visualization | Reusable Plotly gauge charts, multi-axis time-series streams, interactive Gantt timelines, KPI metric cards, and Before vs. After comparison cards. |
| `ui/views/overview.py` | Dashboard View | Digital Twin 6-machine shop floor layout, live status cards, 1-click anomaly and maintenance injection controls, and recent telemetry feed. |
| `ui/views/maintenance.py` | Dashboard View | Workstation PdM diagnostic studio with 5 circular physical dials, RUL prognosis, historical sensor trend charts, and prescriptive maintenance action buttons. |
| `ui/views/production.py` | Dashboard View | Production order backlog table, priority/status filtering, delay risk alerts, and new production order creation modal. |
| `ui/views/energy.py` | Dashboard View | Power draw distribution donut chart, 24-hour factory load curve with peak tariff overlay, degradation energy friction waste tracking. |
| `ui/views/optimizer.py` | Dashboard View | Production scheduler execution studio, Before vs. After comparison cards, Gantt chart, and machine reallocation difference table. |
| `ui/views/whatif.py` | Dashboard View | 10-step guided closed-loop Industry 4.0 demonstration stepper and interactive multi-scenario sandbox. |
| `ui/views/model_metrics.py` | Dashboard View | ML model governance, confusion matrix heatmap, feature importance rankings, RUL regression metrics, and on-demand browser retraining pipeline. |
| `train_models.py` | ML Pipeline | Standalone script for synthetic dataset generation, training XGBoost classifier and Random Forest regressor, computing validation metrics, and serializing models. |
| `test_system.py` | Automated Testing | End-to-end regression and verification suite containing 21 automated unit and integration tests. |
| `capture_all_screenshots.py`| Automation | Headless Chromium automation script via Playwright for capturing pixel-perfect documentation screenshots. |

---

## 2. End-to-End Data Flow Architecture

The data flow within the system forms a complete closed-loop cyber-physical control cycle:

```
[Physics Telemetry Generator] 
       │ (Raw physical sensor readings: Temp, Vib, RPM, Pres, Power)
       ▼
[Factory Simulator Engine] ────► [SQLite Telemetry Store (WAL Mode)]
       │ (State Machine: Normal, Warning, Critical, Maint, Failed)
       ▼
[AI Predictive Models]
       ├── XGBoost Classifier ──► P(failure), Health Score (0-100%)
       ├── Random Forest ────────► Remaining Useful Life (RUL hrs)
       └── Delay Risk Model ─────► Delay Probability & Slack Buffer
       │
       ▼ (Condition & Risk Signals)
[Google OR-Tools CP-SAT Optimizer]
       │ (Multi-objective optimization: Tardiness + Risk Penalty + Energy + Makespan)
       ▼
[Optimal Machine Allocation & Schedule] ────► [SQLite Orders Store]
       │
       ▼ (Shop Floor Adaptation)
[Digital Twin SCADA UI (Streamlit)] ◄──── [Operator Feedback & Maintenance]
```

---

## 3. Verification Checklist of Previously Reported Defects (BUGS_AND_SOLUTIONS.md)

| Bug ID | Severity | Description | Current Code Status | Verification Outcome |
| :--- | :--- | :--- | :--- | :--- |
| **BUG-01** | CRITICAL | Order progress never decremented or completed in `step()` | Partially Fixed | Logic decrements active order, but edge cases existed in future order eligibility. |
| **BUG-02** | HIGH | Discretization flaw in peak tariff calculation | Fixed in Model, Gap in Sim | `energy_model.py` uses continuous overlap; however, `factory_simulator.py` step cost used discrete sample. |
| **BUG-03** | HIGH | SQLite Foreign Keys disabled & excessive connection churn | Verified Fixed | `PRAGMA foreign_keys = ON;` is enabled in `get_connection()`; batch write implemented. |
| **BUG-04** | HIGH | All-failed machine cell deadlock in CP-SAT | Verified Fixed | Replaced hard filter with heavy penalty ($50,000) so orders are never dropped. |
| **BUG-05** | MEDIUM | Incomplete factory reset leaves clock running | Verified Fixed | `simulator.reset()` purges clock, anomaly buffers, and restores nominal state. |
| **BUG-06** | MEDIUM | Delay model conflates "Late" with "At Risk" | Verified Fixed | `is_delayed` (lateness: slack < 0) disentangled from `is_at_risk` (risk: prob > 0.50). |
| **BUG-07** | MEDIUM | Gantt chart displays calendar dates instead of hours | Verified Fixed | Configured `tickformat="%H:%M\nT+%d d"` for clear relative time offsets. |
| **BUG-08** | MEDIUM | Order ID primary key collisions on manual creation | Verified Fixed | `get_next_order_id()` inspects max numeric suffix; insertion return status checked. |
| **BUG-09** | LOW | `playwright` missing from `requirements.txt` | Verified Fixed | Added `playwright>=1.40.0` to `requirements.txt`. |
| **BUG-10** | LOW | Joblib / NumPy 2.x array shape mutation deprecation | Verified Fixed | Deprecation warnings filtered in `pdm_model.py` and `test_system.py`. |
| **BUG-11** | HIGH | Parallel order execution on single-capacity machine | Partially Fixed | Orders grouped by machine; however, line 353 fell back to `sched[0]` when no order was eligible. |
| **BUG-12** | HIGH | Completed orders rescheduled with zero duration | Verified Fixed | `[o for o in orders if o.get("status") != "Completed"]` filters completed orders in baseline and solver. |
| **BUG-13** | MEDIUM | Incomplete reset in What-If guided demo flow | Verified Fixed | Step 1 reset invokes `simulator.reset()` and clears optimization session state. |
| **BUG-14** | MEDIUM | Asymmetric machine risk accounting | Verified Fixed | Standardized `is_machine_high_risk()` static method used identically in baseline and solver. |
| **BUG-15** | LOW | Synthetic RUL decoupled from physics | Verified Fixed | Grounded RUL in continuous degradation formula coupled to health proxy and operating hours. |
| **BUG-16** | CRITICAL | `NameError: name 'status_badge' is not defined` in production view | Verified Fixed | Extracted table generation into `build_orders_table()` with deterministic status badge logic. |

---

## 4. Defect Classification & New Audit Findings

### Critical Severity Defects (Must be fixed for operational validity)

#### AUDIT-CRIT-01: Premature Execution of Future Orders via Fallback Bypass in `step()`
- **Subsystem**: Factory Simulation (`simulation/factory_simulator.py`, lines 351–357)
- **Defect Description**:
  ```python
  sched = [o for o in m_orders if o["status"] == "Scheduled"]
  sched.sort(key=lambda o: (float(o.get("scheduled_start_hrs", 0.0)), float(o.get("deadline_hrs", 999.0))))
  eligible = [o for o in sched if float(o.get("scheduled_start_hrs", 0.0)) <= self.simulation_time_hrs]
  current_order = eligible[0] if eligible else sched[0] if sched else None
  ```
  When no scheduled order on a machine has reached its scheduled start time (`eligible` is empty because all orders are scheduled for future hours, e.g., $T+12\text{h}$), the fallback `else sched[0]` selects the future order immediately.
- **Root Cause**: An incorrect fallback was retained from an earlier draft that bypassed the start-time eligibility check.
- **Impact**: Future orders scheduled hours or days ahead begin processing immediately while the machine is simulated as idle in lines 104–112 (idle power draw), violating schedule integrity.
- **Remediation**: Remove `sched[0]` fallback: `current_order = eligible[0] if eligible else None`.

#### AUDIT-CRIT-02: Lost Machine Time on Multi-Hour Simulation Steps
- **Subsystem**: Factory Simulation (`simulation/factory_simulator.py`, lines 358–378)
- **Defect Description**: If an order has $0.5\text{h}$ remaining and the user steps the simulation by $+2.0\text{h}$, the order completes, but the loop terminates for that machine on that tick. The remaining $1.5\text{h}$ of available machine processing capacity during that step is lost.
- **Impact**: Fast-forwarding simulation ticks causes machine throughput to under-report relative to elapsed simulation hours.
- **Remediation**: Implement a multi-job progression loop per machine that carries forward remaining step time to subsequent eligible queued orders.

---

### High Severity Defects (Affects core optimization & calculations)

#### AUDIT-HIGH-01: Point-in-Time Discrete Tariff Calculation in `step()` Cumulative Cost
- **Subsystem**: Energy Analytics (`simulation/factory_simulator.py`, lines 311–313)
- **Defect Description**:
  ```python
  sim_h = self.simulation_time_hrs % 24.0
  step_tariff = ENERGY_PEAK_TARIFF if (14.0 <= sim_h <= 19.0) else ENERGY_OFFPEAK_TARIFF
  self.cumulative_cost_usd += (step_kwh * step_tariff)
  ```
  While `models/energy_model.py` was fixed to use exact continuous interval overlap, `step()` in the simulator evaluated the tariff using a single discrete sample at the end of the step.
- **Impact**: Stepping across tariff boundaries (e.g. from 13.0h to 15.0h) charges the entire 2-hour energy consumption at the peak tariff ($0.28/kWh) rather than splitting between off-peak and peak.
- **Remediation**: Use exact continuous peak ratio calculation for the step interval `[sim_time - delta, sim_time]`.

#### AUDIT-HIGH-02: Absence of Simulation Clock Awareness in Production Scheduler
- **Subsystem**: Production Scheduling (`optimization/scheduler.py`, line 210)
- **Defect Description**:
  `s = model.NewIntVar(0, HORIZON_UNITS, f"s_{oid}_{mid}")`
  The decision variable allows start times beginning at $0.0$, regardless of current simulation time.
- **Impact**: When an operator re-optimizes the factory at $T = 6.0\text{h}$, the optimizer schedules jobs to start at $T = 0.0\text{h}$ (in the past relative to the simulation clock).
- **Remediation**: Add `current_time: float = 0.0` parameter to `optimize_schedule` and `build_naive_baseline_schedule`, enforcing $s \ge \text{current\_time}$.

#### AUDIT-HIGH-03: In-Progress Status Inconsistency on Machine Reallocation
- **Subsystem**: Optimization & Database (`optimization/scheduler.py` line 362, `database/db_manager.py` line 244)
- **Defect Description**: When an in-flight order on a degraded machine is reallocated to a backup machine where it is scheduled to start in the future ($s > \text{current\_time}$), leaving its status as `In-Progress` causes single-machine concurrency violations on the backup workstation.
- **Remediation**: Update order status to `'Scheduled'` when reassigned with a future start time.

---

### Medium Severity Defects (Visual, semantic, and boundary handling)

#### AUDIT-MED-01: Negative Late Orders Badge Formatting in Comparison Cards
- **Subsystem**: UI Components (`ui/components.py`, line 348)
- **Defect Description**: When the optimizer intentionally trades off minor tardiness on a low-priority job to avoid a catastrophic machine breakdown on an expensive machine, `del_prevented` can be negative (e.g., -1). The UI rendered `▼ -1 Late Orders Prevented` in green.
- **Remediation**: Handle zero and negative deltas gracefully with appropriate semantic labeling (e.g., `▲ 1 Delayed for Machine Protection` in amber).

#### AUDIT-MED-02: Input Validation Gaps in `DatabaseManager.add_order()`
- **Subsystem**: Database (`database/db_manager.py`, lines 198–214)
- **Defect Description**: `add_order()` did not validate that `quantity > 0`, `processing_time_hrs > 0`, and `deadline_hrs > 0`.
- **Remediation**: Add validation assertions and reject non-positive values before executing SQL statements.

#### AUDIT-MED-03: Missing Machine Downtime Awareness During Maintenance in CP-SAT
- **Subsystem**: Optimization (`optimization/scheduler.py`)
- **Defect Description**: If a workstation is currently undergoing maintenance with $1.5\text{h}$ remaining, CP-SAT could schedule an order to start immediately on that machine at $T = 0$.
- **Remediation**: Incorporate remaining maintenance duration into machine earliest start time bounds.

---

### Low Severity Defects (Cleanliness, documentation, and configuration)

#### AUDIT-LOW-01: Discrepancy Between Documented ML Metrics and Serialized Model Metrics
- **Subsystem**: Documentation (`README.md`, `PROJECT_REPORT.md`, `ui/views/model_metrics.py`)
- **Defect Description**: Documented metrics reported an older benchmark ($R^2 = 0.59$, $\text{RMSE} = 150.8\text{h}$, accuracy $99.94\%$), whereas the active serialized model artifact (`pdm_metrics.joblib`) achieves $R^2 = 0.997$, $\text{RMSE} = 12.27\text{h}$, accuracy $99.69\%$.
- **Remediation**: Synchronize all documentation, tables, and fallback default dictionaries with the verified serialized model metrics.

#### AUDIT-LOW-02: Missing SQLite Temporary File Patterns in `.gitignore`
- **Subsystem**: Git Configuration (`.gitignore`)
- **Defect Description**: SQLite WAL mode creates `*.db-wal` and `*.db-shm` temporary files during runtime that were not explicitly listed in `.gitignore`.
- **Remediation**: Add `*.db-wal`, `*.db-shm`, and `*.db-journal` to `.gitignore`.

---

## 5. Audit Summary by Severity

| Severity Level | Count | Action Required |
| :--- | :--- | :--- |
| **Critical** | 2 | Immediate code fix in simulation order progression and eligibility logic. |
| **High** | 3 | Fix continuous step tariff integration, schedule clock awareness, and reallocation state transitions. |
| **Medium** | 3 | Fix comparison card badge sign handling, DB input validation, and maintenance downtime bounds. |
| **Low** | 2 | Synchronize ML metrics documentation and update `.gitignore`. |
| **Total** | **10** | Comprehensive remediation plan established. |
