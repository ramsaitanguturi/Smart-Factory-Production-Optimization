-- Smart Factory Database Schema (SQLite)

CREATE TABLE IF NOT EXISTS machines (
    machine_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    type TEXT NOT NULL,
    nominal_power_kw REAL NOT NULL CHECK(nominal_power_kw > 0),
    idle_power_kw REAL NOT NULL CHECK(idle_power_kw >= 0),
    max_rpm REAL NOT NULL CHECK(max_rpm >= 0),
    hourly_cost REAL NOT NULL CHECK(hourly_cost >= 0),
    status TEXT NOT NULL DEFAULT 'NORMAL',
    health_score REAL NOT NULL DEFAULT 100.0 CHECK(health_score >= 0.0 AND health_score <= 100.0),
    failure_prob REAL NOT NULL DEFAULT 0.02 CHECK(failure_prob >= 0.0 AND failure_prob <= 1.0),
    operating_hours REAL NOT NULL DEFAULT 0.0 CHECK(operating_hours >= 0.0),
    total_cycles INTEGER NOT NULL DEFAULT 0 CHECK(total_cycles >= 0),
    last_maintenance TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS telemetry (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    machine_id TEXT NOT NULL,
    temperature REAL NOT NULL,
    vibration REAL NOT NULL,
    rpm REAL NOT NULL,
    pressure REAL NOT NULL,
    power_kw REAL NOT NULL,
    health_score REAL NOT NULL CHECK(health_score >= 0.0 AND health_score <= 100.0),
    failure_prob REAL NOT NULL CHECK(failure_prob >= 0.0 AND failure_prob <= 1.0),
    status TEXT NOT NULL,
    FOREIGN KEY(machine_id) REFERENCES machines(machine_id)
);

CREATE TABLE IF NOT EXISTS production_orders (
    order_id TEXT PRIMARY KEY,
    product_code TEXT NOT NULL,
    product_name TEXT NOT NULL,
    quantity INTEGER NOT NULL CHECK(quantity > 0),
    processing_time_hrs REAL NOT NULL CHECK(processing_time_hrs >= 0.0),
    required_machine_type TEXT NOT NULL,
    priority TEXT NOT NULL,
    deadline_hrs REAL NOT NULL CHECK(deadline_hrs >= 0.0),
    status TEXT NOT NULL DEFAULT 'Pending',
    assigned_machine_id TEXT,
    scheduled_start_hrs REAL DEFAULT 0.0 CHECK(scheduled_start_hrs >= 0.0),
    scheduled_end_hrs REAL DEFAULT 0.0 CHECK(scheduled_end_hrs >= 0.0),
    delay_risk_prob REAL DEFAULT 0.0 CHECK(delay_risk_prob >= 0.0 AND delay_risk_prob <= 1.0),
    is_delayed INTEGER DEFAULT 0 CHECK(is_delayed IN (0, 1)),
    energy_kwh_predicted REAL DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(assigned_machine_id) REFERENCES machines(machine_id)
);

CREATE TABLE IF NOT EXISTS maintenance_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    machine_id TEXT NOT NULL,
    event_type TEXT NOT NULL,
    description TEXT,
    duration_hrs REAL NOT NULL,
    cost REAL NOT NULL,
    health_restored_to REAL NOT NULL,
    FOREIGN KEY(machine_id) REFERENCES machines(machine_id)
);

CREATE TABLE IF NOT EXISTS optimization_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_orders INTEGER NOT NULL,
    solver_status TEXT NOT NULL,
    solve_time_ms REAL NOT NULL,
    tardiness_before REAL NOT NULL,
    tardiness_after REAL NOT NULL,
    energy_before REAL NOT NULL,
    energy_after REAL NOT NULL,
    risk_before REAL NOT NULL,
    risk_after REAL NOT NULL,
    notes TEXT
);

CREATE INDEX IF NOT EXISTS idx_telemetry_machine_time ON telemetry(machine_id, timestamp);
CREATE INDEX IF NOT EXISTS idx_orders_status ON production_orders(status);
