"""
Smart Factory System Configuration
Defines machine specs, sensor baseline & alarm thresholds, order categories,
and optimization weights.
"""
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "database" / "factory.db"
MODELS_DIR = BASE_DIR / "models" / "saved"
MODELS_DIR.mkdir(parents=True, exist_ok=True)

# Machine Definitions (6 industrial machines across 3 workstation types)
MACHINES = {
    "M1-CNC-01": {
        "name": "5-Axis CNC Mill Alpha",
        "type": "CNC_MILL",
        "nominal_power_kw": 24.0,
        "idle_power_kw": 3.2,
        "max_rpm": 12000,
        "hourly_cost": 85.0,
        "capabilities": ["Milling", "Drilling", "Facing", "Contouring"],
    },
    "M2-CNC-02": {
        "name": "5-Axis CNC Mill Beta",
        "type": "CNC_MILL",
        "nominal_power_kw": 22.5,
        "idle_power_kw": 3.0,
        "max_rpm": 10000,
        "hourly_cost": 80.0,
        "capabilities": ["Milling", "Drilling", "Facing", "Contouring"],
    },
    "M3-ROB-01": {
        "name": "Robotic Welder & Cell 1",
        "type": "ROBOTIC_ARM",
        "nominal_power_kw": 18.0,
        "idle_power_kw": 2.5,
        "max_rpm": 3600,
        "hourly_cost": 65.0,
        "capabilities": ["Welding", "Joint Assembly", "Fastening"],
    },
    "M4-ROB-02": {
        "name": "Robotic Welder & Cell 2",
        "type": "ROBOTIC_ARM",
        "nominal_power_kw": 19.5,
        "idle_power_kw": 2.6,
        "max_rpm": 3600,
        "hourly_cost": 68.0,
        "capabilities": ["Welding", "Joint Assembly", "Fastening"],
    },
    "M5-INJ-01": {
        "name": "Hydraulic Injection Press A",
        "type": "INJECTION_MOLD",
        "nominal_power_kw": 35.0,
        "idle_power_kw": 5.0,
        "max_rpm": 1800,
        "hourly_cost": 95.0,
        "capabilities": ["Plastic Injection", "Molding", "Curing"],
    },
    "M6-INJ-02": {
        "name": "Hydraulic Injection Press B",
        "type": "INJECTION_MOLD",
        "nominal_power_kw": 38.0,
        "idle_power_kw": 5.4,
        "max_rpm": 1800,
        "hourly_cost": 100.0,
        "capabilities": ["Plastic Injection", "Molding", "Curing"],
    },
}

# Sensor Nominal Ranges & Critical Alarm Thresholds
SENSOR_SPECS = {
    "temperature": {
        "unit": "°C",
        "nominal_min": 50.0,
        "nominal_max": 75.0,
        "warning_threshold": 85.0,
        "critical_threshold": 105.0,
    },
    "vibration": {
        "unit": "mm/s RMS",
        "nominal_min": 0.8,
        "nominal_max": 2.2,
        "warning_threshold": 3.8,
        "critical_threshold": 5.5,
    },
    "rpm": {
        "unit": "RPM",
        "nominal_variation_pct": 0.05,
        "warning_drop_pct": 0.15,
        "critical_drop_pct": 0.30,
    },
    "pressure": {
        "unit": "bar",
        "nominal_min": 90.0,
        "nominal_max": 120.0,
        "warning_threshold": 75.0,
        "critical_threshold": 60.0,
    },
    "power": {
        "unit": "kW",
        "warning_overload_pct": 1.25,
        "critical_overload_pct": 1.50,
    },
}

# Machine Status Enums
STATUS_NORMAL = "NORMAL"
STATUS_WARNING = "WARNING"
STATUS_CRITICAL = "CRITICAL"
STATUS_MAINTENANCE = "MAINTENANCE"
STATUS_FAILED = "FAILED"

STATUS_COLORS = {
    STATUS_NORMAL: "#10b981",       # Emerald green
    STATUS_WARNING: "#f59e0b",      # Amber orange
    STATUS_CRITICAL: "#ef4444",     # Crimson red
    STATUS_MAINTENANCE: "#3b82f6",   # Blue
    STATUS_FAILED: "#7f1d1d",       # Dark Maroon
}

# Product Catalog
PRODUCTS = [
    {"code": "PRD-AERO-01", "name": "Titanium Turbine Blade", "machine_type": "CNC_MILL", "base_time_hrs": 4.5, "base_kwh": 95.0},
    {"code": "PRD-AUTO-02", "name": "EV Chassis Sub-frame", "machine_type": "ROBOTIC_ARM", "base_time_hrs": 3.0, "base_kwh": 52.0},
    {"code": "PRD-POLY-03", "name": "Precision Polymer Enclosure", "machine_type": "INJECTION_MOLD", "base_time_hrs": 2.5, "base_kwh": 82.0},
    {"code": "PRD-AERO-04", "name": "Inconel Exhaust Nozzle", "machine_type": "CNC_MILL", "base_time_hrs": 5.0, "base_kwh": 110.0},
    {"code": "PRD-AUTO-05", "name": "Battery Pack Modular Tray", "machine_type": "ROBOTIC_ARM", "base_time_hrs": 3.5, "base_kwh": 60.0},
    {"code": "PRD-MED-06", "name": "Medical Venturi Manifold", "machine_type": "INJECTION_MOLD", "base_time_hrs": 2.0, "base_kwh": 65.0},
]

# Order Priorities
PRIORITY_WEIGHTS = {
    "Low": 1,
    "Medium": 2,
    "High": 4,
    "Urgent": 8,
}

# Energy Pricing ($/kWh)
ENERGY_PEAK_TARIFF = 0.28   # Peak hours (14:00 - 19:00)
ENERGY_OFFPEAK_TARIFF = 0.11 # Off-peak hours
