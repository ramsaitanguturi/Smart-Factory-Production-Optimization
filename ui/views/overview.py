"""
Factory Floor Overview & Digital Twin View
Displays industrial workstations, live machine states, telemetry badges,
and floor-wide status indicators with Dark and Light theme adaptation.
"""
import streamlit as st
import pandas as pd
from typing import Dict, Any, List, Optional
from config import STATUS_NORMAL, STATUS_WARNING, STATUS_CRITICAL, STATUS_MAINTENANCE, STATUS_FAILED
from ui.styles import get_theme_palette


def render_overview_view(simulator, db, theme: Optional[str] = None):
    current_theme = (theme or st.session_state.get("theme", "dark")).lower()
    pal = get_theme_palette(current_theme)

    st.markdown("""
    <div class="section-banner">
        <span>🏭</span> DIGITAL TWIN: FACTORY FLOOR WORKSTATIONS & CELL MATRIX
    </div>
    """, unsafe_allow_html=True)

    # Machine Cells Display
    machines = db.get_machines()
    orders = db.get_orders()
    
    # Map assigned orders to machines
    orders_by_machine = {}
    for o in orders:
        mid = o.get("assigned_machine_id")
        if mid:
            orders_by_machine.setdefault(mid, []).append(o)

    # Group machines into rows of 3 columns
    for row_idx in range(0, len(machines), 3):
        cols = st.columns(3)
        for col_idx, m in enumerate(machines[row_idx:row_idx+3]):
            mid = m["machine_id"]
            status = m["status"]
            health = m["health_score"]
            fail_prob = m["failure_prob"]
            op_hours = m["operating_hours"]
            telem = simulator.latest_telemetry.get(mid, {})

            # CSS status classes
            status_class = "status-normal"
            badge_class = "badge-normal"
            dot_class = "dot-normal"

            if status == STATUS_WARNING:
                status_class = "status-warning"
                badge_class = "badge-warning"
                dot_class = "dot-warning"
            elif status in (STATUS_CRITICAL, STATUS_FAILED):
                status_class = "status-critical"
                badge_class = "badge-critical"
                dot_class = "dot-critical"
            elif status == STATUS_MAINTENANCE:
                status_class = "status-normal"
                badge_class = "badge-maintenance"
                dot_class = "dot-normal"

            m_orders = orders_by_machine.get(mid, [])
            health_clr = pal["accent_green"] if health >= 80 else pal["accent_amber"] if health >= 55 else pal["accent_red"]
            fail_clr = pal["accent_red"] if fail_prob > 0.4 else pal["accent_amber"] if fail_prob > 0.15 else pal["accent_green"]

            card_html = f"""<div class="machine-card {status_class}">
<div style="display: flex; justify-content: space-between; align-items: flex-start;">
<div>
<span style="font-size: 0.72rem; color: {pal['text_muted']}; font-family: monospace;">{m['type']}</span>
<div style="font-size: 1.15rem; font-weight: 700; color: {pal['text_primary']}; margin-top: 2px;">{m['name']}</div>
<div style="font-size: 0.78rem; color: {pal['text_muted']}; font-family: monospace;">ID: {mid}</div>
</div>
<span class="badge-status {badge_class}">
<span class="pulse-dot {dot_class}"></span> {status}
</span>
</div>
<div style="margin: 12px 0 8px 0;">
<div style="display: flex; justify-content: space-between; font-size: 0.8rem; margin-bottom: 4px;">
<span style="color: {pal['text_muted']};">Health Index</span>
<span style="font-weight: 700; color: {health_clr}; font-family: monospace;">{health:.1f}%</span>
</div>
<div style="background: {pal['track_bg']}; border-radius: 4px; height: 6px; overflow: hidden;">
<div style="width: {health}%; background: {health_clr}; height: 100%;"></div>
</div>
</div>
<div class="sub-stat-box">
<div>
<span style="color: {pal['text_muted']};">Failure Risk:</span>
<span style="font-weight: 700; color: {fail_clr}; font-family: monospace;"> {(fail_prob*100):.1f}%</span>
</div>
<div>
<span style="color: {pal['text_muted']};">Op Hours:</span>
<span style="font-family: monospace; color: {pal['text_secondary']};"> {op_hours:.0f} h</span>
</div>
<div>
<span style="color: {pal['text_muted']};">Temp:</span>
<span style="font-family: monospace; color: {pal['accent_red'] if telem.get('temperature', 60) > 85 else pal['text_secondary']};"> {telem.get('temperature', 62.0):.1f}°C</span>
</div>
<div>
<span style="color: {pal['text_muted']};">Vib:</span>
<span style="font-family: monospace; color: {pal['accent_red'] if telem.get('vibration', 1.2) > 3.5 else pal['text_secondary']};"> {telem.get('vibration', 1.3):.2f} mm/s</span>
</div>
<div>
<span style="color: {pal['text_muted']};">Power:</span>
<span style="font-family: monospace; color: {pal['text_secondary']};"> {telem.get('power_kw', 18.0):.1f} kW</span>
</div>
<div>
<span style="color: {pal['text_muted']};">Orders:</span>
<span style="font-family: monospace; color: {pal['accent_blue']};"> {len(m_orders)}</span>
</div>
</div>
<div style="margin-top: 8px; font-size: 0.72rem; color: {pal['text_muted']}; font-style: italic;">
{telem.get('primary_cause', 'Normal Operation')}
</div>
</div>"""
            with cols[col_idx]:
                st.markdown(card_html, unsafe_allow_html=True)

    # Floor Operations Bar
    st.markdown("""
    <div class="section-banner">
        <span>⚙️</span> SHOP FLOOR TELEMETRY FEED & CONTROLS
    </div>
    """, unsafe_allow_html=True)
    
    target_machine_ids = [m["machine_id"] for m in machines] if machines else ["M1-CNC-01"]
    anom_options = {
        "COOLANT_FAILURE": "🔥 Heat / Coolant Failure",
        "BEARING_WEAR": "⚡ Bearing Harmonic Wear",
        "MOTOR_MISALIGN": "⚙️ Motor Misalignment",
        "CATASTROPHIC_FAILURE": "💥 Sudden Breakdown"
    }

    ctl_c1, ctl_c2, ctl_c3, ctl_c4 = st.columns([1.4, 1.3, 1.8, 2.0])
    with ctl_c1:
        if st.button("⏩ Step (+0.5h)", use_container_width=True, help="Advance simulation time by 30 minutes"):
            simulator.step(time_delta_hrs=0.5)
            st.rerun()
    with ctl_c2:
        if st.button("🔄 Refresh Telemetry", use_container_width=True, help="Fetch latest telemetry readings"):
            simulator.step(time_delta_hrs=0.1)
            st.rerun()
    with ctl_c3:
        selected_mid = st.selectbox(
            "Target Machine",
            options=target_machine_ids,
            index=0,
            key="overview_ctrl_target_machine",
            label_visibility="collapsed",
            help="Select target workstation"
        )
    with ctl_c4:
        selected_anom = st.selectbox(
            "Anomaly Type",
            options=list(anom_options.keys()),
            format_func=lambda k: anom_options[k],
            index=0,
            key="overview_ctrl_anom_type",
            label_visibility="collapsed",
            help="Select anomaly pattern to simulate"
        )

    act_c1, act_c2 = st.columns([1, 1])
    short_id = selected_mid.split("-")[0] if "-" in selected_mid else selected_mid
    anom_tag = anom_options.get(selected_anom, "Anomaly").split(" ")[1]
    with act_c1:
        if st.button(f"⚠️ Simulate {anom_tag} Anomaly on {short_id} ({selected_mid})", use_container_width=True):
            simulator.inject_anomaly(selected_mid, selected_anom)
            st.warning(f"Injected {anom_options[selected_anom]} on {selected_mid}! Sensor telemetry will spike.")
            st.rerun()
    with act_c2:
        if st.button(f"🛠️ Perform Maintenance on {short_id} ({selected_mid})", use_container_width=True):
            simulator.perform_maintenance(selected_mid)
            st.success(f"Maintenance performed! {selected_mid} restored to healthy status.")
            st.rerun()

    # Recent Telemetry Log Table
    st.markdown("##### 📡 Real-time Sensor Data Stream (Latest 12 Readings)")
    recent_telem = db.get_recent_telemetry(limit=12)
    if not recent_telem.empty:
        st.dataframe(
            recent_telem[[
                "timestamp", "machine_id", "temperature", "vibration",
                "rpm", "pressure", "power_kw", "health_score", "failure_prob", "status"
            ]],
            use_container_width=True,
            hide_index=True
        )
