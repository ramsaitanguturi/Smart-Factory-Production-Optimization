"""
Predictive Maintenance (PdM) Studio View
Deep-dive telemetry inspection, ML failure probability dials,
Remaining Useful Life (RUL) forecasting, and prescriptive maintenance actions with Dark/Light theme support.
"""
import streamlit as st
import pandas as pd
from typing import Optional
from ui.components import render_gauge_chart, render_telemetry_history_chart
from ui.styles import get_theme_palette
from config import STATUS_NORMAL, STATUS_WARNING, STATUS_CRITICAL, STATUS_MAINTENANCE, STATUS_FAILED


def render_maintenance_view(simulator, db, theme: Optional[str] = None):
    current_theme = (theme or st.session_state.get("theme", "dark")).lower()
    pal = get_theme_palette(current_theme)

    st.markdown("""
    <div class="section-banner">
        <span>🛠️</span> PREDICTIVE MAINTENANCE & MACHINE HEALTH DIAGNOSTICS
    </div>
    """, unsafe_allow_html=True)

    machines = db.get_machines()
    machine_options = {m["machine_id"]: f"{m['machine_id']} - {m['name']} ({m['status']})" for m in machines}
    
    selected_mid = st.selectbox(
        "Select Machine to Inspect Telemetry & ML Predictions:",
        options=list(machine_options.keys()),
        format_func=lambda x: machine_options[x]
    )

    m_data = next((m for m in machines if m["machine_id"] == selected_mid), None)
    telem = simulator.latest_telemetry.get(selected_mid, {})

    if m_data and telem:
        # Top Machine Overview Row
        h_col1, h_col2, h_col3 = st.columns([1.5, 1.5, 3])
        
        with h_col1:
            st.plotly_chart(
                render_gauge_chart(
                    value=telem.get("health_score", 95.0),
                    title="Machine Health Index",
                    min_val=0,
                    max_val=100,
                    warn_thresh=65,
                    crit_thresh=35,
                    unit="%",
                    reverse_hazard=True,
                    theme=current_theme
                ),
                use_container_width=True
            )
        
        with h_col2:
            st.plotly_chart(
                render_gauge_chart(
                    value=round(telem.get("failure_prob", 0.02) * 100.0, 1),
                    title="Failure Probability (ML)",
                    min_val=0,
                    max_val=100,
                    warn_thresh=25,
                    crit_thresh=60,
                    unit="% Risk",
                    theme=current_theme
                ),
                use_container_width=True
            )

        with h_col3:
            rul_hours = telem.get("rul_hours", 650.0)
            status = m_data["status"]
            
            m_status_html = f"""<div style="background: {pal['status_box_bg']}; border: 1px solid {pal['status_box_border']}; border-radius: 10px; padding: 16px; height: 180px; display: flex; flex-direction: column; justify-content: space-between; box-shadow: 0 4px 14px rgba(0,0,0,0.08);">
<div>
<div style="display: flex; justify-content: space-between; align-items: center;">
<span style="font-size: 0.8rem; color: {pal['text_muted']}; font-family: monospace;">STATUS & RUL PROGNOSIS</span>
<span class="badge-status {'badge-normal' if status == STATUS_NORMAL else 'badge-warning' if status == STATUS_WARNING else 'badge-critical'}">
{status}
</span>
</div>
<div style="font-size: 1.5rem; font-weight: 700; color: {pal['accent_blue']}; font-family: 'JetBrains Mono'; margin-top: 6px;">
{rul_hours:.0f} Operating Hours
</div>
<div style="font-size: 0.75rem; color: {pal['text_muted']};">Estimated Remaining Useful Life (RUL)</div>
</div>
<div style="background: {pal['sub_box_bg']}; padding: 8px 12px; border-radius: 6px; border-left: 3px solid {pal['sub_box_border']};">
<div style="font-size: 0.72rem; color: {pal['text_muted']}; font-weight: 600;">PRIMARY DEGRADATION CAUSE:</div>
<div style="font-size: 0.82rem; font-weight: 600; color: {pal['text_primary']};">{telem.get('primary_cause', 'Normal Operation')}</div>
</div>
</div>"""
            st.markdown(m_status_html, unsafe_allow_html=True)

        # Telemetry Gauges (5 core sensors)
        st.markdown("##### 📊 Physical Telemetry Sensors")
        g1, g2, g3, g4, g5 = st.columns(5)
        with g1:
            st.plotly_chart(
                render_gauge_chart(telem.get("temperature", 65.0), "Temperature", 30, 130, 85, 105, "°C", theme=current_theme),
                use_container_width=True
            )
        with g2:
            st.plotly_chart(
                render_gauge_chart(telem.get("vibration", 1.4), "Vibration", 0.0, 8.0, 3.5, 5.5, "mm/s RMS", theme=current_theme),
                use_container_width=True
            )
        with g3:
            st.plotly_chart(
                render_gauge_chart(telem.get("rpm", 8000), "Motor Spindle", 0, m_data["max_rpm"], m_data["max_rpm"] * 0.75, m_data["max_rpm"] * 0.45, "RPM", reverse_hazard=True, theme=current_theme),
                use_container_width=True
            )
        with g4:
            st.plotly_chart(
                render_gauge_chart(telem.get("pressure", 105.0), "Hydraulic Pressure", 0, 150, 75, 55, "bar", reverse_hazard=True, theme=current_theme),
                use_container_width=True
            )
        with g5:
            st.plotly_chart(
                render_gauge_chart(telem.get("power_kw", 18.0), "Power Draw", 0, m_data["nominal_power_kw"] * 1.5, m_data["nominal_power_kw"] * 1.15, m_data["nominal_power_kw"] * 1.35, "kW", theme=current_theme),
                use_container_width=True
            )

        # Historical Sensor Trends Chart
        history_df = db.get_recent_telemetry(machine_id=selected_mid, limit=40)
        if not history_df.empty:
            st.plotly_chart(render_telemetry_history_chart(history_df, selected_mid, theme=current_theme), use_container_width=True)

        # Prescriptive Recommendation & Maintenance Actions
        st.markdown("""
        <div class="section-banner">
            <span>💡</span> AI PRESCRIPTIVE MAINTENANCE ACTION
        </div>
        """, unsafe_allow_html=True)

        recom_text = telem.get("recommendation", "Normal operating conditions.")
        st.info(f"**AI Prescriptive Guidance**: {recom_text}")

        act_col1, act_col2, act_col3 = st.columns(3)
        with act_col1:
            if st.button(f"🛠️ Overhaul / Service {selected_mid}", use_container_width=True):
                simulator.perform_maintenance(selected_mid, "Scheduled Preventive Overhaul")
                st.success(f"Overhaul complete for {selected_mid}! Health restored to 98.5%.")
                st.rerun()
        with act_col2:
            if st.button(f"⚠️ Inject Bearing Wear on {selected_mid}", use_container_width=True):
                simulator.inject_anomaly(selected_mid, "BEARING_WEAR")
                st.warning(f"Injected Bearing Wear on {selected_mid}! Vibration will surge.")
                st.rerun()
        with act_col3:
            if st.button(f"🚨 Inject Coolant Loss on {selected_mid}", use_container_width=True):
                simulator.inject_anomaly(selected_mid, "COOLANT_FAILURE")
                st.error(f"Injected Coolant Loss on {selected_mid}! Temperature will escalate.")
                st.rerun()
