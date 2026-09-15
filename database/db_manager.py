"""
Database Manager for Smart Factory
Handles SQLite operations for machines, telemetry, orders, and maintenance logs.
"""
import sqlite3
import random
import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from contextlib import contextmanager
import pandas as pd

from config import DB_PATH, MACHINES, PRODUCTS, PRIORITY_WEIGHTS


class DatabaseManager:
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.init_db()

    @contextmanager
    def get_connection(self):
        conn = sqlite3.connect(str(self.db_path), timeout=30.0)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA busy_timeout=30000;")
        conn.execute("PRAGMA foreign_keys = ON;")
        try:
            yield conn
        finally:
            conn.close()

    def init_db(self):
        """Initializes tables from schema.sql and seeds initial data if empty."""
        schema_path = Path(__file__).resolve().parent / "schema.sql"
        with self.get_connection() as conn:
            with open(schema_path, "r", encoding="utf-8") as f:
                conn.executescript(f.read())
            
            # Check if machines table is empty
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM machines")
            count = cursor.fetchone()[0]
            if count == 0:
                self._seed_machines(conn)
                self._seed_initial_orders(conn)
                conn.commit()

    def _seed_machines(self, conn: sqlite3.Connection):
        """Seeds the 6 industrial machines defined in config.py."""
        cursor = conn.cursor()
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        for mid, mcfg in MACHINES.items():
            cursor.execute("""
                INSERT INTO machines (
                    machine_id, name, type, nominal_power_kw, idle_power_kw,
                    max_rpm, hourly_cost, status, health_score, failure_prob,
                    operating_hours, total_cycles, last_maintenance, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, 'NORMAL', 98.5, 0.015, ?, ?, ?, ?)
            """, (
                mid,
                mcfg["name"],
                mcfg["type"],
                mcfg["nominal_power_kw"],
                mcfg["idle_power_kw"],
                mcfg["max_rpm"],
                mcfg["hourly_cost"],
                round(random.uniform(450.0, 1800.0), 1),
                random.randint(200, 1500),
                now,
                now
            ))

    def _seed_initial_orders(self, conn: sqlite3.Connection):
        """Seeds realistic initial production orders across machine types."""
        cursor = conn.cursor()
        order_seeds = [
            ("ORD-101", "PRD-AERO-01", 15, 4.5, "CNC_MILL", "High", 12.0),
            ("ORD-102", "PRD-AERO-04", 8, 5.0, "CNC_MILL", "Urgent", 8.0),
            ("ORD-103", "PRD-AERO-01", 20, 6.0, "CNC_MILL", "Medium", 24.0),
            ("ORD-104", "PRD-AERO-04", 12, 5.5, "CNC_MILL", "Low", 36.0),
            ("ORD-201", "PRD-AUTO-02", 40, 3.5, "ROBOTIC_ARM", "Urgent", 10.0),
            ("ORD-202", "PRD-AUTO-05", 25, 4.0, "ROBOTIC_ARM", "High", 16.0),
            ("ORD-203", "PRD-AUTO-02", 50, 4.5, "ROBOTIC_ARM", "Medium", 28.0),
            ("ORD-204", "PRD-AUTO-05", 30, 3.0, "ROBOTIC_ARM", "Low", 32.0),
            ("ORD-301", "PRD-POLY-03", 100, 3.0, "INJECTION_MOLD", "Urgent", 11.0),
            ("ORD-302", "PRD-MED-06", 80, 2.5, "INJECTION_MOLD", "High", 14.0),
            ("ORD-303", "PRD-POLY-03", 150, 4.0, "INJECTION_MOLD", "Medium", 26.0),
            ("ORD-304", "PRD-MED-06", 60, 2.0, "INJECTION_MOLD", "Low", 30.0),
        ]
        prod_map = {p["code"]: p["name"] for p in PRODUCTS}
        for oid, pcode, qty, ptime, mtype, prio, dline in order_seeds:
            cursor.execute("""
                INSERT INTO production_orders (
                    order_id, product_code, product_name, quantity, processing_time_hrs,
                    required_machine_type, priority, deadline_hrs, status,
                    delay_risk_prob, is_delayed, energy_kwh_predicted
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'Pending', 0.05, 0, ?)
            """, (
                oid,
                pcode,
                prod_map.get(pcode, pcode),
                qty,
                ptime,
                mtype,
                prio,
                dline,
                round(ptime * 25.0, 1)
            ))

    # --- Machine Operations ---
    def get_machines(self) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM machines ORDER BY machine_id")
            return [dict(row) for row in cursor.fetchall()]

    def get_machine(self, machine_id: str) -> Optional[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM machines WHERE machine_id = ?", (machine_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def update_machine_state(self, machine_id: str, status: str, health_score: float,
                             failure_prob: float, operating_hours: float):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute("""
                UPDATE machines
                SET status = ?, health_score = ?, failure_prob = ?,
                    operating_hours = ?, updated_at = ?
                WHERE machine_id = ?
            """, (status, health_score, failure_prob, operating_hours, now, machine_id))
            conn.commit()

    # --- Telemetry Operations ---
    def record_telemetry(self, machine_id: str, temp: float, vib: float, rpm: float,
                         pressure: float, power: float, health: float, fail_prob: float,
                         status: str):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO telemetry (
                    machine_id, temperature, vibration, rpm, pressure,
                    power_kw, health_score, failure_prob, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (machine_id, temp, vib, rpm, pressure, power, health, fail_prob, status))
            conn.commit()

    def record_telemetry_batch(self, telemetry_rows: List[tuple]):
        """Batch writes multiple telemetry readings in a single ACID transaction."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.executemany("""
                INSERT INTO telemetry (
                    machine_id, temperature, vibration, rpm, pressure,
                    power_kw, health_score, failure_prob, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, telemetry_rows)
            conn.commit()

    def get_recent_telemetry(self, machine_id: Optional[str] = None, limit: int = 50) -> pd.DataFrame:
        with self.get_connection() as conn:
            if machine_id:
                query = """
                    SELECT * FROM telemetry
                    WHERE machine_id = ?
                    ORDER BY id DESC LIMIT ?
                """
                df = pd.read_sql_query(query, conn, params=(machine_id, limit))
            else:
                query = """
                    SELECT * FROM telemetry
                    ORDER BY id DESC LIMIT ?
                """
                df = pd.read_sql_query(query, conn, params=(limit,))
            if not df.empty:
                df = df.iloc[::-1].reset_index(drop=True)
            return df

    # --- Order Operations ---
    def get_orders(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if status:
                cursor.execute("SELECT * FROM production_orders WHERE status = ? ORDER BY deadline_hrs", (status,))
            else:
                cursor.execute("SELECT * FROM production_orders ORDER BY deadline_hrs")
            return [dict(row) for row in cursor.fetchall()]

    def add_order(self, order_id: str, product_code: str, product_name: str,
                  quantity: int, processing_time_hrs: float, required_machine_type: str,
                  priority: str, deadline_hrs: float) -> bool:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    INSERT INTO production_orders (
                        order_id, product_code, product_name, quantity, processing_time_hrs,
                        required_machine_type, priority, deadline_hrs, status
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'Pending')
                """, (order_id, product_code, product_name, quantity, processing_time_hrs,
                      required_machine_type, priority, deadline_hrs))
                conn.commit()
                return True
            except sqlite3.IntegrityError:
                return False

    def get_next_order_id(self) -> str:
        """Generates a collision-free sequential order ID based on maximum existing order number."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT order_id FROM production_orders")
            rows = cursor.fetchall()
            max_num = 100
            for r in rows:
                oid = r[0]
                try:
                    parts = oid.split("-")
                    if len(parts) >= 2 and parts[-1].isdigit():
                        num = int(parts[-1])
                        if num > max_num:
                            max_num = num
                except Exception:
                    pass
            return f"ORD-{max_num + 1}"

    def update_order_assignment(self, order_id: str, machine_id: str, start_hrs: float,
                                end_hrs: float, delay_risk: float, is_delayed: int,
                                energy_kwh: float):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE production_orders
                SET assigned_machine_id = ?, scheduled_start_hrs = ?, scheduled_end_hrs = ?,
                    delay_risk_prob = ?, is_delayed = ?, energy_kwh_predicted = ?,
                    status = CASE WHEN status = 'Pending' THEN 'Scheduled' ELSE status END
                WHERE order_id = ?
            """, (machine_id, start_hrs, end_hrs, delay_risk, is_delayed, energy_kwh, order_id))
            conn.commit()

    def update_order_status(self, order_id: str, status: str):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE production_orders SET status = ? WHERE order_id = ?", (status, order_id))
            conn.commit()

    # --- Maintenance Operations ---
    def log_maintenance(self, machine_id: str, event_type: str, description: str,
                        duration_hrs: float, cost: float, health_restored_to: float = 98.0):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute("""
                INSERT INTO maintenance_logs (
                    timestamp, machine_id, event_type, description, duration_hrs, cost, health_restored_to
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (now, machine_id, event_type, description, duration_hrs, cost, health_restored_to))
            
            # Reset machine health and status
            cursor.execute("""
                UPDATE machines
                SET status = 'NORMAL', health_score = ?, failure_prob = 0.015,
                    last_maintenance = ?, updated_at = ?
                WHERE machine_id = ?
            """, (health_restored_to, now, now, machine_id))
            conn.commit()

    def get_maintenance_logs(self, limit: int = 20) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM maintenance_logs ORDER BY id DESC LIMIT ?", (limit,))
            return [dict(row) for row in cursor.fetchall()]

    # --- Optimization History ---
    def record_optimization_run(self, total_orders: int, solver_status: str,
                                solve_time_ms: float, tardiness_before: float,
                                tardiness_after: float, energy_before: float,
                                energy_after: float, risk_before: float,
                                risk_after: float, notes: str = ""):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO optimization_history (
                    total_orders, solver_status, solve_time_ms,
                    tardiness_before, tardiness_after, energy_before, energy_after,
                    risk_before, risk_after, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (total_orders, solver_status, solve_time_ms, tardiness_before,
                  tardiness_after, energy_before, energy_after, risk_before, risk_after, notes))
            conn.commit()

    def reset_to_defaults(self):
        """Clears and re-seeds database to pristine state."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM telemetry")
            cursor.execute("DELETE FROM maintenance_logs")
            cursor.execute("DELETE FROM optimization_history")
            cursor.execute("DELETE FROM production_orders")
            cursor.execute("DELETE FROM machines")
            self._seed_machines(conn)
            self._seed_initial_orders(conn)
            conn.commit()
