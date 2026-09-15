"""
Reusable UI Components and Plotly Visualizations for Smart Factory Dashboard
Supports both Dark Mode and Light Mode with adaptive palettes.
"""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from typing import Dict, Any, List, Optional
from config import STATUS_NORMAL, STATUS_WARNING, STATUS_CRITICAL, STATUS_MAINTENANCE, STATUS_FAILED
from ui.styles import get_theme_palette


def _resolve_theme(theme: Optional[str] = None) -> str:
    """Helper to resolve current active theme from parameter or st.session_state."""
    if theme is not None and theme.strip():
        return theme.strip().lower()
    if hasattr(st, "session_state") and "theme" in st.session_state:
        return str(st.session_state["theme"]).strip().lower()
    return "dark"


def render_header(sim_time_hrs: float = 0.0, alerts_count: int = 0, theme: Optional[str] = None):
    """Renders the top Industrial SCADA Control Room Header Bar adapted to current theme."""
    current_theme = _resolve_theme(theme)
    pal = get_theme_palette(current_theme)
    is_light = (current_theme == "light")

    alert_border = "#dc2626" if alerts_count > 0 else (pal["accent_green"] if is_light else "#10b981")
    alert_color = "#dc2626" if alerts_count > 0 else (pal["accent_green"] if is_light else "#34d399")
    alert_bg = "rgba(254, 242, 242, 0.9)" if (alerts_count > 0 and is_light) else (
        "rgba(240, 253, 244, 0.9)" if is_light else "rgba(15, 23, 42, 0.8)"
    )

    st.markdown(f"""
    <div class="scada-header">
        <div>
            <h1 class="scada-title">🏭 SMART FACTORY OPERATIONS COMMAND CENTER</h1>
            <div class="scada-subtitle">INDUSTRY 4.0 CLOSED-LOOP AI PRODUCTION OPTIMIZATION & PREDICTIVE MAINTENANCE</div>
        </div>
        <div style="display: flex; gap: 15px; align-items: center;">
            <div style="background: {pal['header_clock_bg']}; border: 1px solid {pal['header_clock_border']}; padding: 6px 14px; border-radius: 8px; text-align: right;">
                <div style="font-size: 0.68rem; color: {pal['text_muted']}; font-family: monospace;">SIMULATION CLOCK</div>
                <div style="font-size: 1.15rem; font-weight: 700; color: {pal['header_clock_val']}; font-family: 'JetBrains Mono';">T + {sim_time_hrs:.1f} hrs</div>
            </div>
            <div style="background: {alert_bg}; border: 1px solid {alert_border}; padding: 6px 14px; border-radius: 8px; text-align: center;">
                <div style="font-size: 0.68rem; color: {pal['text_muted']}; font-family: monospace;">ACTIVE ALERTS</div>
                <div style="font-size: 1.15rem; font-weight: 700; color: {alert_color}; font-family: 'JetBrains Mono';">{alerts_count} ACTIVE</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_kpi_row(machines: List[Dict[str, Any]], orders: List[Dict[str, Any]], theme: Optional[str] = None):
    """Renders top factory KPI metric cards adapted to current theme."""
    current_theme = _resolve_theme(theme)
    pal = get_theme_palette(current_theme)

    total_machines = len(machines)
    avg_health = sum(m["health_score"] for m in machines) / max(1, total_machines)
    at_risk_count = sum(1 for m in machines if m["failure_prob"] > 0.30 or m["health_score"] < 65.0)
    
    total_orders = len(orders)
    delayed_orders = sum(1 for o in orders if o.get("is_delayed", 0) == 1)

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    with c1:
        health_color = pal["accent_green"] if avg_health >= 80 else pal["accent_amber"] if avg_health >= 55 else pal["accent_red"]
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Average Health</div>
            <div class="kpi-value" style="color: {health_color};">{avg_health:.1f}%</div>
            <div class="kpi-sub">{total_machines} Connected Machines</div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        risk_color = pal["accent_red"] if at_risk_count > 0 else pal["accent_green"]
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Machines At Risk</div>
            <div class="kpi-value" style="color: {risk_color};">{at_risk_count}</div>
            <div class="kpi-sub">{total_machines - at_risk_count} Nominal States</div>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Active Orders</div>
            <div class="kpi-value" style="color: {pal['accent_blue']};">{total_orders}</div>
            <div class="kpi-sub">Across 3 Cell Types</div>
        </div>
        """, unsafe_allow_html=True)
    with c4:
        delayed_color = pal["accent_red"] if delayed_orders > 0 else pal["accent_green"]
        pct_del = (delayed_orders / total_orders * 100) if total_orders else 0
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Delayed Orders</div>
            <div class="kpi-value" style="color: {delayed_color};">{delayed_orders}</div>
            <div class="kpi-sub">{pct_del:.0f}% of Backlog</div>
        </div>
        """, unsafe_allow_html=True)
    with c5:
        cur_power = sum(m.get("power_kw", m.get("nominal_power_kw", 25.0) * 0.75) for m in machines)
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Current Factory Load</div>
            <div class="kpi-value" style="color: {pal['accent_amber']};">{cur_power:.1f} kW</div>
            <div class="kpi-sub">Peak Cap: 157.0 kW</div>
        </div>
        """, unsafe_allow_html=True)
    with c6:
        oee = (avg_health * 0.45) + ((1.0 - (delayed_orders / max(1, total_orders))) * 55.0)
        oee_color = pal["accent_green"] if oee >= 85 else pal["accent_blue"] if oee >= 70 else pal["accent_red"]
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Factory OEE Index</div>
            <div class="kpi-value" style="color: {oee_color};">{oee:.1f}%</div>
            <div class="kpi-sub">Industry Target: 85%</div>
        </div>
        """, unsafe_allow_html=True)


def render_gauge_chart(value: float, title: str, min_val: float, max_val: float,
                       warn_thresh: float, crit_thresh: float, unit: str = "",
                       reverse_hazard: bool = False, theme: Optional[str] = None) -> go.Figure:
    """Renders a sleek circular sensor gauge with dark/light adaptive theme."""
    current_theme = _resolve_theme(theme)
    pal = get_theme_palette(current_theme)

    if not reverse_hazard:
        steps = [
            {'range': [min_val, warn_thresh], 'color': "rgba(16, 185, 129, 0.22)"},
            {'range': [warn_thresh, crit_thresh], 'color': "rgba(245, 158, 11, 0.25)"},
            {'range': [crit_thresh, max_val], 'color': "rgba(239, 68, 68, 0.30)"}
        ]
        bar_color = pal["accent_red"] if value >= crit_thresh else pal["accent_amber"] if value >= warn_thresh else pal["accent_green"]
    else:
        steps = [
            {'range': [min_val, crit_thresh], 'color': "rgba(239, 68, 68, 0.30)"},
            {'range': [crit_thresh, warn_thresh], 'color': "rgba(245, 158, 11, 0.25)"},
            {'range': [warn_thresh, max_val], 'color': "rgba(16, 185, 129, 0.22)"}
        ]
        bar_color = pal["accent_red"] if value <= crit_thresh else pal["accent_amber"] if value <= warn_thresh else pal["accent_green"]

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={'text': f"<b style='font-size:14px; color:{pal['text_primary']};'>{title}</b><br><span style='font-size:11px; color:{pal['text_muted']};'>{unit}</span>"},
        number={'font': {'color': pal["text_primary"], 'family': 'JetBrains Mono', 'size': 24}},
        gauge={
            'axis': {'range': [min_val, max_val], 'tickcolor': pal["tick_color"], 'tickwidth': 1},
            'bar': {'color': bar_color, 'thickness': 0.28},
            'bgcolor': pal["gauge_bg"],
            'borderwidth': 1,
            'bordercolor': pal["gauge_border"],
            'steps': steps,
        }
    ))
    fig.update_layout(
        height=210,
        margin=dict(l=15, r=15, t=55, b=15),
        paper_bgcolor="rgba(0,0,0,0)",
        font={'color': pal["text_secondary"]}
    )
    return fig


def render_telemetry_history_chart(df: pd.DataFrame, machine_id: str, theme: Optional[str] = None) -> go.Figure:
    """Renders multi-sensor live time-series with temperature, vibration, and power."""
    current_theme = _resolve_theme(theme)
    pal = get_theme_palette(current_theme)

    fig = go.Figure()
    if df.empty:
        return fig

    # Temperature on Primary Y Axis
    fig.add_trace(go.Scatter(
        x=df.index,
        y=df["temperature"],
        name="Temperature (°C)",
        line=dict(color="#f97316", width=2.5),
        mode="lines+markers",
        marker=dict(size=4)
    ))

    # Vibration on Secondary Y Axis
    fig.add_trace(go.Scatter(
        x=df.index,
        y=df["vibration"],
        name="Vibration (mm/s)",
        yaxis="y2",
        line=dict(color=pal["accent_cyan"], width=2.5),
        mode="lines+markers",
        marker=dict(size=4)
    ))

    # Power kW on Y Axis 3
    fig.add_trace(go.Scatter(
        x=df.index,
        y=df["power_kw"],
        name="Power (kW)",
        yaxis="y3",
        line=dict(color="#a855f7", width=1.8, dash="dot"),
        mode="lines"
    ))

    fig.update_layout(
        title=dict(text=f"Live Sensor Telemetry Stream: {machine_id}", font=dict(color=pal["text_primary"], size=15)),
        paper_bgcolor=pal["paper_bg"],
        plot_bgcolor=pal["plot_bg"],
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(color=pal["text_secondary"])),
        height=320,
        margin=dict(l=40, r=40, t=50, b=30),
        xaxis=dict(title="Telemetry Step", gridcolor=pal["grid_color"], color=pal["text_muted"]),
        yaxis=dict(title=dict(text="Temperature (°C)", font=dict(color="#f97316")), tickfont=dict(color="#f97316"), gridcolor=pal["grid_color"]),
        yaxis2=dict(title=dict(text="Vibration (mm/s)", font=dict(color=pal["accent_cyan"])), tickfont=dict(color=pal["accent_cyan"]), overlaying="y", side="right"),
        yaxis3=dict(title=dict(text="Power (kW)", font=dict(color="#a855f7")), tickfont=dict(color="#a855f7"), overlaying="y", side="right", position=0.95, showgrid=False),
    )
    return fig


def render_gantt_chart(orders: List[Dict[str, Any]], title: str = "Production Schedule Timeline", theme: Optional[str] = None) -> go.Figure:
    """Renders an interactive Gantt chart of scheduled production orders adapted to theme."""
    current_theme = _resolve_theme(theme)
    pal = get_theme_palette(current_theme)

    if not orders:
        fig = go.Figure()
        fig.update_layout(title="No scheduled orders to display.")
        return fig

    rows = []
    for o in orders:
        mid = o.get("assigned_machine_id", "Unassigned")
        start = float(o.get("scheduled_start_hrs", 0.0))
        end = float(o.get("scheduled_end_hrs", start + float(o.get("processing_time_hrs", 3.0))))
        delay_prob = float(o.get("delay_risk_prob", 0.0))
        prio = o.get("priority", "Medium")
        
        if delay_prob > 0.60 or o.get("is_delayed", 0) == 1:
            status_tag = "CRITICAL DELAY RISK"
        elif delay_prob > 0.30:
            status_tag = "MODERATE RISK"
        else:
            status_tag = "ON TRACK"

        rows.append({
            "Machine": mid,
            "Order": f"{o['order_id']} ({o.get('product_code', '')})",
            "Start": start,
            "Finish": end,
            "Duration": end - start,
            "Deadline": float(o.get("deadline_hrs", 0.0)),
            "Priority": prio,
            "StatusTag": status_tag,
            "DelayRisk": delay_prob
        })

    df = pd.DataFrame(rows)
    df = df.sort_values(by=["Machine", "Start"])

    color_map = {
        "ON TRACK": pal["accent_green"],
        "MODERATE RISK": pal["accent_amber"],
        "CRITICAL DELAY RISK": pal["accent_red"]
    }

    fig = px.timeline(
        df,
        x_start=pd.to_datetime(df["Start"], unit="h", origin=pd.Timestamp("2026-01-01")),
        x_end=pd.to_datetime(df["Finish"], unit="h", origin=pd.Timestamp("2026-01-01")),
        y="Machine",
        color="StatusTag",
        color_discrete_map=color_map,
        hover_data=["Order", "Priority", "Duration", "Deadline", "DelayRisk"],
        title=title
    )

    fig.update_layout(
        title=dict(text=title, font=dict(color=pal["title_color"], size=15)),
        paper_bgcolor=pal["paper_bg"],
        plot_bgcolor=pal["plot_bg"],
        height=380,
        margin=dict(l=60, r=30, t=50, b=30),
        font=dict(color=pal["text_secondary"]),
        xaxis=dict(title="Schedule Timeline (Hours from start)", gridcolor=pal["grid_color"], color=pal["text_muted"], tickformat="%H:%M\nT+%d d"),
        yaxis=dict(title="", gridcolor=pal["grid_color"], color=pal["text_primary"], autorange="reversed"),
        legend=dict(orientation="h", y=1.08, x=0.5, xanchor="center", font=dict(color=pal["text_secondary"]))
    )
    return fig


def render_before_after_comparison(baseline: Dict[str, Any], optimized: Dict[str, Any], improvements: Dict[str, Any], theme: Optional[str] = None):
    """Renders the comprehensive Before vs. After optimization comparison cards and metrics."""
    current_theme = _resolve_theme(theme)
    pal = get_theme_palette(current_theme)

    st.markdown("""
    <div class="section-banner">
        <span>⚡</span> AI PRODUCTION OPTIMIZATION RESULTS: BEFORE VS. AFTER COMPARISON
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        base_tard = baseline.get("total_tardiness_weighted", 0.0)
        opt_tard = optimized.get("total_tardiness_weighted", 0.0)
        saved_tard = improvements.get("delay_saved_hrs", 0.0)
        st.markdown(f"""
        <div class="comparison-box">
            <div class="kpi-label">Weighted Tardiness (Delay)</div>
            <div style="font-size: 1.1rem; color: {pal['text_muted']}; text-decoration: line-through;">Before: {base_tard:.1f} hrs</div>
            <div style="font-size: 1.6rem; font-weight: 700; color: {pal['accent_green']}; font-family: monospace;">After: {opt_tard:.1f} hrs</div>
            <div class="improvement-badge">▼ {saved_tard:.1f} hrs Delay Saved</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        base_risk = baseline.get("high_risk_assignments", 0)
        opt_risk = optimized.get("high_risk_assignments", 0)
        avoided_risk = improvements.get("high_risk_jobs_avoided", 0)
        risk_after_color = pal["accent_green"] if opt_risk == 0 else pal["accent_amber"]
        st.markdown(f"""
        <div class="comparison-box">
            <div class="kpi-label">Jobs on Degraded Machines</div>
            <div style="font-size: 1.1rem; color: {pal['text_muted']}; text-decoration: line-through;">Before: {base_risk} jobs</div>
            <div style="font-size: 1.6rem; font-weight: 700; color: {risk_after_color}; font-family: monospace;">After: {opt_risk} jobs</div>
            <div class="improvement-badge">▼ {avoided_risk} High-Risk Avoided</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        base_del_orders = baseline.get("delayed_orders_count", 0)
        opt_del_orders = optimized.get("delayed_orders_count", 0)
        del_prevented = improvements.get("delayed_orders_prevented", 0)
        del_after_color = pal["accent_green"] if opt_del_orders == 0 else pal["accent_amber"]
        st.markdown(f"""
        <div class="comparison-box">
            <div class="kpi-label">Late Orders Count</div>
            <div style="font-size: 1.1rem; color: {pal['text_muted']}; text-decoration: line-through;">Before: {base_del_orders} orders</div>
            <div style="font-size: 1.6rem; font-weight: 700; color: {del_after_color}; font-family: monospace;">After: {opt_del_orders} orders</div>
            <div class="improvement-badge">▼ {del_prevented} Late Orders Prevented</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        base_energy = baseline.get("total_energy_kwh", 0.0)
        opt_energy = optimized.get("total_energy_kwh", 0.0)
        saved_energy = improvements.get("energy_saved_kwh", 0.0)
        st.markdown(f"""
        <div class="comparison-box">
            <div class="kpi-label">Total Energy Consumption</div>
            <div style="font-size: 1.1rem; color: {pal['text_muted']}; text-decoration: line-through;">Before: {base_energy:.1f} kWh</div>
            <div style="font-size: 1.6rem; font-weight: 700; color: {pal['accent_blue']}; font-family: monospace;">After: {opt_energy:.1f} kWh</div>
            <div class="improvement-badge">▼ {saved_energy:.1f} kWh Conserved</div>
        </div>
        """, unsafe_allow_html=True)
