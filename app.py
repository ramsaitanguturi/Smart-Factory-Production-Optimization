"""
AI-Based Smart Factory Production Optimization and Predictive Maintenance System
Main Streamlit Application Entry Point with Dual Light & Dark Theme Support
"""
import sys
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import streamlit as st

# Streamlit Page Configuration
st.set_page_config(
    page_title="Smart Factory Operations Center | Industry 4.0",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

from ui.styles import apply_custom_styles, get_theme_palette
from ui.components import render_header, render_kpi_row
from database.db_manager import DatabaseManager
from simulation.factory_simulator import FactorySimulator
import importlib
import ui.views.overview
importlib.reload(ui.views.overview)
from ui.views.overview import render_overview_view
from ui.views.maintenance import render_maintenance_view
from ui.views.production import render_production_view
from ui.views.energy import render_energy_view
from ui.views.optimizer import render_optimizer_view
from ui.views.whatif import render_whatif_view
from ui.views.model_metrics import render_model_metrics_view


def get_system_instances():
    """Initializes and caches singleton database and simulator instances in session state."""
    if "db" not in st.session_state:
        st.session_state["db"] = DatabaseManager()
    if "simulator" not in st.session_state:
        st.session_state["simulator"] = FactorySimulator(db=st.session_state["db"])
    return st.session_state["simulator"], st.session_state["db"]


def _on_theme_change():
    choice = st.session_state.get("sidebar_theme_radio", "Dark")
    st.session_state["theme"] = "light" if "Light" in choice else "dark"


def main():
    # Pre-sync theme state if user interacted with sidebar toggle
    if "sidebar_theme_radio" in st.session_state:
        st.session_state["theme"] = "light" if "Light" in st.session_state["sidebar_theme_radio"] else "dark"
    elif "theme" not in st.session_state:
        st.session_state["theme"] = "dark"

    current_theme = st.session_state["theme"]
    pal = get_theme_palette(current_theme)

    # Inject Custom Industrial SCADA Styles (Theme-Aware)
    st.markdown(apply_custom_styles(theme=current_theme), unsafe_allow_html=True)

    simulator, db = get_system_instances()

    # Sidebar Navigation & Industrial Controls
    with st.sidebar:
        st.markdown(f"""
        <div style="text-align: center; padding: 10px 0 14px 0; border-bottom: 1px solid {pal['border_color']};">
            <div style="font-size: 2.2rem;">🏭</div>
            <div style="font-size: 1.15rem; font-weight: 700; color: {pal['accent_blue']}; font-family: 'JetBrains Mono';">SMART FACTORY 4.0</div>
            <div style="font-size: 0.72rem; color: {pal['text_muted']};">CLOSED-LOOP OPTIMIZATION</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("### 🎨 Theme Selector")
        theme_mode = st.radio(
            "Dashboard Theme:",
            ["🌙 Dark SCADA", "☀️ Clean Light"],
            index=0 if current_theme == "dark" else 1,
            horizontal=True,
            label_visibility="collapsed",
            key="sidebar_theme_radio",
            on_change=_on_theme_change
        )

        st.markdown("---")
        st.markdown("### 🧭 Control Navigation")
        nav_choice = st.radio(
            "Select Operational View:",
            [
                "🏭 Factory Overview & Twin",
                "🛠️ Predictive Maintenance",
                "📋 Production Orders Queue",
                "⚡ Energy & Power Analytics",
                "🧠 AI Production Optimizer",
                "🧪 What-If Simulation & Demo",
                "📊 ML Governance & Metrics"
            ],
            index=0
        )

        st.markdown("---")
        st.markdown("### ⚙️ Simulation Master Clock")
        
        sim_col1, sim_col2 = st.columns(2)
        with sim_col1:
            if st.button("⏩ Step +0.5h", use_container_width=True):
                simulator.step(time_delta_hrs=0.5)
                st.rerun()
        with sim_col2:
            if st.button("⏩ Step +2.0h", use_container_width=True):
                simulator.step(time_delta_hrs=2.0)
                st.rerun()

        if st.button("🔄 Reset Factory State", use_container_width=True):
            db.reset_to_defaults()
            simulator.reset()
            st.session_state.pop("last_optimization_result", None)
            st.session_state.pop("guided_opt_result", None)
            st.success("Factory reset to nominal state!")
            st.rerun()

        st.markdown("---")
        st.markdown(f"""
        <div style="font-size: 0.75rem; color: {pal['text_muted']}; line-height: 1.4;">
            <b>Industry 4.0 Closed-Loop Stack</b><br>
            • Telemetry: Physics Simulator<br>
            • AI PdM: XGBoost & Random Forest<br>
            • Optimizer: Google OR-Tools CP-SAT<br>
            • Data: SQLite Engine<br>
            • UI: Streamlit & Plotly
        </div>
        """, unsafe_allow_html=True)

    # Fetch live state for top headers & KPIs
    machines = db.get_machines()
    orders = db.get_orders()
    active_alerts = sum(1 for m in machines if m["status"] in ("WARNING", "CRITICAL", "FAILED"))

    # Render Header and Top KPI Bar
    render_header(sim_time_hrs=simulator.simulation_time_hrs, alerts_count=active_alerts, theme=current_theme)
    render_kpi_row(machines=machines, orders=orders, theme=current_theme)
    st.markdown("<div style='margin-bottom: 12px;'></div>", unsafe_allow_html=True)

    # View Router
    if nav_choice == "🏭 Factory Overview & Twin":
        render_overview_view(simulator, db, theme=current_theme)
    elif nav_choice == "🛠️ Predictive Maintenance":
        render_maintenance_view(simulator, db, theme=current_theme)
    elif nav_choice == "📋 Production Orders Queue":
        render_production_view(simulator, db)
    elif nav_choice == "⚡ Energy & Power Analytics":
        render_energy_view(simulator, db, theme=current_theme)
    elif nav_choice == "🧠 AI Production Optimizer":
        render_optimizer_view(simulator, db, theme=current_theme)
    elif nav_choice == "🧪 What-If Simulation & Demo":
        render_whatif_view(simulator, db, theme=current_theme)
    elif nav_choice == "📊 ML Governance & Metrics":
        render_model_metrics_view(theme=current_theme)


if __name__ == "__main__":
    main()
