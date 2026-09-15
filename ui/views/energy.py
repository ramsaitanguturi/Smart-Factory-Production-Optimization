"""
Energy Prediction & Analytics View
Monitors real-time power draw (kW), cumulative energy usage (kWh),
real-time and forecasted load profiles, and degradation-induced energy waste with Dark/Light theme support.
"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from typing import Dict, Any, List, Optional
from config import MACHINES, ENERGY_PEAK_TARIFF, ENERGY_OFFPEAK_TARIFF
from ui.styles import get_theme_palette


def render_energy_view(simulator, db, theme: Optional[str] = None):
    current_theme = (theme or st.session_state.get("theme", "dark")).lower()
    pal = get_theme_palette(current_theme)

    st.markdown("""
    <div class="section-banner">
        <span>⚡</span> FACTORY ENERGY CONSUMPTION & POWER DEMAND FORECAST
    </div>
    """, unsafe_allow_html=True)

    machines = db.get_machines()
    orders = db.get_orders()

    # Machine-level power aggregation
    machine_powers = []
    total_active_kw = 0.0
    total_degradation_loss_kwh = 0.0
    peak_cap = sum(m.get("nominal_power_kw", 25.0) for m in machines)

    for m in machines:
        mid = m["machine_id"]
        telem = simulator.latest_telemetry.get(mid, {})
        pwr = telem.get("power_kw", m.get("idle_power_kw", 3.0))
        health = m["health_score"]
        
        # Friction penalty kWh
        wear_penalty_pct = max(0.0, (100.0 - health) / 100.0) * 22.0
        extra_kwh = (pwr * (wear_penalty_pct / 100.0)) * 8.0  # over 8-hr shift
        total_degradation_loss_kwh += extra_kwh
        total_active_kw += pwr

        sim_h = simulator.simulation_time_hrs % 24.0
        current_tariff = ENERGY_PEAK_TARIFF if (14.0 <= sim_h <= 19.0) else ENERGY_OFFPEAK_TARIFF

        machine_powers.append({
            "Machine": mid,
            "Name": m["name"],
            "Type": m["type"],
            "Current Power (kW)": round(pwr, 2),
            "Health (%)": health,
            "Degradation Penalty (%)": f"+{wear_penalty_pct:.1f}%",
            "Est Shift kWh": round(pwr * 8.0, 1),
            "Est Shift Cost ($)": round(pwr * 8.0 * current_tariff, 2)
        })

    # Summary Metrics Row
    sim_hour = simulator.simulation_time_hrs % 24.0
    is_peak = (14.0 <= sim_hour <= 19.0)
    current_rate = ENERGY_PEAK_TARIFF if is_peak else ENERGY_OFFPEAK_TARIFF
    cum_kwh = getattr(simulator, "cumulative_energy_kwh", 0.0)
    cum_cost = getattr(simulator, "cumulative_cost_usd", 0.0)

    ec1, ec2, ec3, ec4 = st.columns(4)
    with ec1:
        st.metric("Total Factory Load", f"{total_active_kw:.1f} kW", f"Peak Cap: {peak_cap:.1f} kW")
    with ec2:
        st.metric("Cumulative Energy Consumed", f"{cum_kwh:.1f} kWh", f"Clock: T + {simulator.simulation_time_hrs:.1f} hrs")
    with ec3:
        tariff_label = f"Peak: ${current_rate:.2f}/kWh" if is_peak else f"Off-Peak: ${current_rate:.2f}/kWh"
        st.metric("Cumulative Energy Cost", f"${cum_cost:.2f}", tariff_label)
    with ec4:
        st.metric("Degradation Energy Loss", f"{total_degradation_loss_kwh:.1f} kWh", "Extra Wear Friction", delta_color="inverse")

    st.markdown("---")

    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown("##### 🥧 Real-Time Power Distribution by Machine")
        df_pwr = pd.DataFrame(machine_powers)
        fig_donut = px.pie(
            df_pwr,
            values="Current Power (kW)",
            names="Machine",
            hole=0.45,
            color_discrete_sequence=px.colors.sequential.Tealgrn
        )
        fig_donut.update_layout(
            paper_bgcolor=pal["paper_bg"],
            font=dict(color=pal["text_secondary"]),
            height=320,
            margin=dict(l=20, r=20, t=30, b=20)
        )
        st.plotly_chart(fig_donut, use_container_width=True)

    with col_right:
        st.markdown("##### 📈 24-Hour Projected Load Profile vs. Tariff Window")
        hours = list(range(24))
        # Schedule-informed dynamic diurnal load curve
        base_curve = [
            round(total_active_kw * (0.55 if h < 6 else 1.08 if 8 <= h <= 17 else 0.75), 1)
            for h in hours
        ]
        
        fig_line = go.Figure()
        fig_line.add_trace(go.Scatter(
            x=hours,
            y=base_curve,
            mode="lines+markers",
            name="Forecasted Load (kW)",
            line=dict(color=pal["accent_blue"], width=3)
        ))
        
        # Highlight peak tariff window (14:00 to 19:00)
        fig_line.add_vrect(
            x0=14, x1=19,
            fillcolor="rgba(239, 68, 68, 0.2)",
            layer="below", line_width=1,
            line_color="rgba(239, 68, 68, 0.5)",
            annotation_text=f"PEAK TARIFF (${ENERGY_PEAK_TARIFF:.2f}/kWh)",
            annotation_position="top left",
            annotation_font=dict(color=pal["accent_red"], size=10)
        )

        # Simulation Time indicator line
        fig_line.add_vline(
            x=sim_hour,
            line_dash="dash",
            line_color=pal["accent_green"],
            line_width=2,
            annotation_text=f"CURRENT CLOCK (T+{simulator.simulation_time_hrs:.1f}h)",
            annotation_position="bottom right",
            annotation_font=dict(color=pal["accent_green"], size=10)
        )

        fig_line.update_layout(
            paper_bgcolor=pal["paper_bg"],
            plot_bgcolor=pal["plot_bg"],
            font=dict(color=pal["text_secondary"]),
            height=320,
            margin=dict(l=40, r=20, t=30, b=30),
            xaxis=dict(title="Hour of Day (0 - 23)", gridcolor=pal["grid_color"], color=pal["text_muted"]),
            yaxis=dict(title="Power (kW)", gridcolor=pal["grid_color"], color=pal["text_muted"])
        )
        st.plotly_chart(fig_line, use_container_width=True)

    # Machine Energy Metrics Table
    st.markdown("##### 📋 Machine Energy Diagnostics Table")
    st.dataframe(df_pwr, use_container_width=True, hide_index=True)
