"""
Energy Prediction & Analytics View
Monitors real-time power draw (kW), machine-level energy shares,
24-hour forecasted consumption, and degradation-induced energy waste with Dark/Light theme support.
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

    for m in machines:
        mid = m["machine_id"]
        telem = simulator.latest_telemetry.get(mid, {})
        pwr = telem.get("power_kw", m["nominal_power_kw"] * 0.75)
        health = m["health_score"]
        
        # Friction penalty kWh
        wear_penalty_pct = max(0.0, (100.0 - health) / 100.0) * 22.0
        extra_kwh = (pwr * (wear_penalty_pct / 100.0)) * 8.0  # over 8-hr shift
        total_degradation_loss_kwh += extra_kwh
        total_active_kw += pwr

        machine_powers.append({
            "Machine": mid,
            "Name": m["name"],
            "Type": m["type"],
            "Current Power (kW)": round(pwr, 2),
            "Health (%)": health,
            "Degradation Penalty (%)": f"+{wear_penalty_pct:.1f}%",
            "Est Shift kWh": round(pwr * 8.0, 1),
            "Est Shift Cost ($)": round(pwr * 8.0 * ENERGY_OFFPEAK_TARIFF, 2)
        })

    # Summary Metrics Row
    ec1, ec2, ec3, ec4 = st.columns(4)
    with ec1:
        st.metric("Total Factory Load", f"{total_active_kw:.1f} kW", "Peak Cap: 157 kW")
    with ec2:
        projected_24h_kwh = total_active_kw * 24.0
        st.metric("Projected 24-hr Usage", f"{projected_24h_kwh:.1f} kWh", "Baseline: 2,400 kWh")
    with ec3:
        st.metric("Degradation Energy Loss", f"{total_degradation_loss_kwh:.1f} kWh", "Extra Wear Friction", delta_color="inverse")
    with ec4:
        daily_cost = (projected_24h_kwh * 0.16)
        st.metric("Est. Daily Electricity Cost", f"${daily_cost:.2f}", f"Avg Rate: $0.16/kWh")

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
        base_curve = [
            total_active_kw * (0.6 if h < 6 else 1.05 if 8 <= h <= 17 else 0.8)
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
            annotation_text="PEAK TARIFF ($0.28/kWh)",
            annotation_position="top left",
            annotation_font=dict(color=pal["accent_red"], size=10)
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
