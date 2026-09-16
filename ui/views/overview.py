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

    # High-visibility Status Badge Legend matching GUIDE.md specifications
    st.markdown(f"""
    <div class="status-legend-bar">
        <span style="font-weight: 700; color: {pal['text_primary']}; margin-right: 4px;">Status Guide:</span>
        <span class="status-legend-item"><span class="badge-status badge-normal"><span class="pulse-dot dot-normal"></span> NORMAL</span> <span style="color: {pal['text_muted']}; font-size: 0.75rem;">(Safe)</span></span>
        <span class="status-legend-item"><span class="badge-status badge-warning"><span class="pulse-dot dot-warning"></span> WARNING</span> <span style="color: {pal['text_muted']}; font-size: 0.75rem;">(Elevated)</span></span>
        <span class="status-legend-item"><span class="badge-status badge-critical"><span class="pulse-dot dot-critical"></span> CRITICAL</span> <span style="color: {pal['text_muted']}; font-size: 0.75rem;">(Pulsing Risk)</span></span>
        <span class="status-legend-item"><span class="badge-status badge-failed"><span class="pulse-dot dot-failed"></span> FAILED</span> <span style="color: {pal['text_muted']}; font-size: 0.75rem;">(Halted)</span></span>
        <span class="status-legend-item"><span class="badge-status badge-maintenance"><span class="pulse-dot dot-maintenance"></span> MAINTENANCE</span> <span style="color: {pal['text_muted']}; font-size: 0.75rem;">(Offline)</span></span>
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
            elif status == STATUS_CRITICAL:
                status_class = "status-critical"
                badge_class = "badge-critical"
                dot_class = "dot-critical"
            elif status == STATUS_FAILED:
                status_class = "status-failed"
                badge_class = "badge-failed"
                dot_class = "dot-failed"
            elif status == STATUS_MAINTENANCE:
                status_class = "status-maintenance"
                badge_class = "badge-maintenance"
                dot_class = "dot-maintenance"

            m_orders = orders_by_machine.get(mid, [])
            health_clr = pal["accent_green"] if health >= 80 else pal["accent_amber"] if health >= 55 else pal["accent_red"]
            fail_clr = pal["accent_red"] if fail_prob > 0.4 else pal["accent_amber"] if fail_prob > 0.15 else pal["accent_green"]

            # Status descriptive subtitle
            if status == STATUS_MAINTENANCE:
                rem = getattr(simulator, "maintenance_remaining", {}).get(mid, 2.0)
                status_sub = f"🔧 Technician Overhaul: {rem:.1f}h remaining"
            elif status == STATUS_CRITICAL:
                crit_h = getattr(simulator, "critical_runtime_hrs", {}).get(mid, 0.0)
                status_sub = f"⚠️ CRITICAL: {crit_h:.1f}h unmaintained (Imminent Failure)"
            elif status == STATUS_FAILED:
                status_sub = "🛑 HALTED: Spindle Seized - Requires Overhaul"
            else:
                status_sub = telem.get('primary_cause', 'Normal Operation')

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
<span style="font-family: monospace; color: {pal['accent_red'] if telem.get('temperature', 60.0) > 85 else pal['text_secondary']};"> {telem.get('temperature', 60.0):.1f}°C</span>
</div>
<div>
<span style="color: {pal['text_muted']};">Vib:</span>
<span style="font-family: monospace; color: {pal['accent_red'] if telem.get('vibration', 1.2) > 3.5 else pal['text_secondary']};"> {telem.get('vibration', 1.2):.2f} mm/s</span>
</div>
<div>
<span style="color: {pal['text_muted']};">Power:</span>
<span style="font-family: monospace; color: {pal['text_secondary']};"> {telem.get('power_kw', m.get('idle_power_kw', 3.0)):.1f} kW</span>
</div>
<div>
<span style="color: {pal['text_muted']};">Orders:</span>
<span style="font-family: monospace; color: {pal['accent_blue']};"> {len(m_orders)}</span>
</div>
</div>
<div style="margin-top: 8px; font-size: 0.72rem; color: {pal['text_muted']}; font-style: italic;">
{status_sub}
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
    
    # Display persistent action feedback if set
    if "overview_feedback" in st.session_state and st.session_state["overview_feedback"]:
        fb_type, fb_msg = st.session_state.pop("overview_feedback")
        if fb_type == "warning":
            st.warning(fb_msg)
        elif fb_type == "success":
            st.success(fb_msg)
        elif fb_type == "error":
            st.error(fb_msg)

    target_machine_ids = [m["machine_id"] for m in machines] if machines else ["M1-CNC-01"]
    short_map = {mid: mid.split("-")[0] for mid in target_machine_ids}

    ctl_c1, ctl_c2, ctl_c3, ctl_c4 = st.columns([1.4, 1.4, 2.0, 2.0], vertical_alignment="center")
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
            "Target Workstation",
            options=target_machine_ids,
            format_func=lambda x: f"🎯 Machine: {x}",
            index=0,
            key="overview_ctrl_target_machine",
            label_visibility="collapsed"
        )
    with ctl_c4:
        short_id = short_map.get(selected_mid, selected_mid)
        if st.button(f"🛠️ Restore {short_id} ({selected_mid})", use_container_width=True, help=f"Clear active anomalies & restore {selected_mid} to healthy status"):
            simulator.perform_maintenance(selected_mid)
            msg = f"🛠️ Maintenance performed! {selected_mid} restored to healthy status (98.5% health)."
            st.session_state["overview_feedback"] = ("success", msg)
            try:
                st.toast(msg, icon="🛠️")
            except Exception:
                pass
            st.rerun()

    muted_clr = pal["text_muted"]
    blue_clr = pal["accent_blue"]
    st.markdown(f"<div style='font-size: 0.78rem; color: {muted_clr}; margin: 8px 0 4px 2px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;'>⚡ 1-Click Status Simulation & Anomalies for <span style='color: {blue_clr};'>{selected_mid}</span>:</div>", unsafe_allow_html=True)

    anom_c1, anom_c2, anom_c3, anom_c4, anom_c5 = st.columns(5)
    with anom_c1:
        if st.button("🔥 Coolant Spike", use_container_width=True, help=f"Inject rapid overheating and pressure loss on {selected_mid} (CRITICAL Red)"):
            simulator.inject_anomaly(selected_mid, "COOLANT_FAILURE")
            msg = f"🔥 Injected Coolant Failure anomaly on {selected_mid}! Spindle overheating -> CRITICAL state."
            st.session_state["overview_feedback"] = ("warning", msg)
            try:
                st.toast(msg, icon="🔥")
            except Exception:
                pass
            st.rerun()
    with anom_c2:
        if st.button("⚡ Bearing Wear", use_container_width=True, help=f"Inject severe vibration surge on {selected_mid} (WARNING Amber)"):
            simulator.inject_anomaly(selected_mid, "BEARING_WEAR")
            msg = f"⚡ Injected Bearing Wear anomaly on {selected_mid}! Vibration surging -> WARNING state."
            st.session_state["overview_feedback"] = ("warning", msg)
            try:
                st.toast(msg, icon="⚡")
            except Exception:
                pass
            st.rerun()
    with anom_c3:
        if st.button("⚙️ Motor Misalign", use_container_width=True, help=f"Inject RPM fluctuation on {selected_mid} (WARNING Amber)"):
            simulator.inject_anomaly(selected_mid, "MOTOR_MISALIGN")
            msg = f"⚙️ Injected Motor Misalignment on {selected_mid}! RPM deviating -> WARNING state."
            st.session_state["overview_feedback"] = ("warning", msg)
            try:
                st.toast(msg, icon="⚙️")
            except Exception:
                pass
            st.rerun()
    with anom_c4:
        if st.button("💥 Breakdown", use_container_width=True, help=f"Trigger critical emergency halt on {selected_mid} (FAILED Dark Red)"):
            simulator.inject_anomaly(selected_mid, "CATASTROPHIC_FAILURE")
            msg = f"💥 Injected Catastrophic Breakdown on {selected_mid}! Machine halted -> FAILED state."
            st.session_state["overview_feedback"] = ("error", msg)
            try:
                st.toast(msg, icon="💥")
            except Exception:
                pass
            st.rerun()
    with anom_c5:
        if st.button("🔧 Maintenance", use_container_width=True, help=f"Place {selected_mid} offline for 2.0h overhaul (MAINTENANCE Blue)"):
            simulator.set_maintenance(selected_mid, in_maintenance=True)
            msg = f"🔧 {selected_mid} is now offline for 2.0h overhaul. Step simulation clock (+0.5h or +2.0h) to progress, or click Restore to finish immediately."
            st.session_state["overview_feedback"] = ("success", msg)
            try:
                st.toast(msg, icon="🔧")
            except Exception:
                pass
            st.rerun()

    # Recent Telemetry Log Table
    st.markdown("##### 📡 Real-time Sensor Data Stream (Latest 12 Readings)")
    recent_telem = db.get_recent_telemetry(limit=12)
    if not recent_telem.empty:
        status_emoji_map = {
            "NORMAL": "🟢 NORMAL",
            "WARNING": "🟡 WARNING",
            "CRITICAL": "🔴 CRITICAL",
            "FAILED": "🛑 FAILED",
            "MAINTENANCE": "🔵 MAINTENANCE"
        }
        display_df = recent_telem[[
            "timestamp", "machine_id", "temperature", "vibration",
            "rpm", "pressure", "power_kw", "health_score", "failure_prob", "status"
        ]].copy()
        display_df["status"] = display_df["status"].apply(lambda s: status_emoji_map.get(str(s).upper(), str(s)))
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True
        )
