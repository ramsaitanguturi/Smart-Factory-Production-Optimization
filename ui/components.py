"""
Reusable UI Components and Plotly Visualizations for Smart Factory Dashboard
"""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from typing import Dict, Any, List, Optional
from config import STATUS_NORMAL, STATUS_WARNING, STATUS_CRITICAL, STATUS_MAINTENANCE, STATUS_FAILED


def render_header(sim_time_hrs: float = 0.0, alerts_count: int = 0):
    """Renders the top Industrial SCADA Control Room Header Bar."""
    st.markdown(f"""
    <div class="scada-header">
        <div>
            <h1 class="scada-title">🏭 SMART FACTORY OPERATIONS COMMAND CENTER</h1>
            <div class="scada-subtitle">INDUSTRY 4.0 CLOSED-LOOP AI PRODUCTION OPTIMIZATION & PREDICTIVE MAINTENANCE</div>
        </div>
        <div style="display: flex; gap: 15px; align-items: center;">
            <div style="background: rgba(15,23,42,0.8); border: 1px solid #334155; padding: 6px 14px; border-radius: 8px; text-align: right;">
                <div style="font-size: 0.68rem; color: #94a3b8; font-family: monospace;">SIMULATION CLOCK</div>
                <div style="font-size: 1.15rem; font-weight: 700; color: #38bdf8; font-family: 'JetBrains Mono';">T + {sim_time_hrs:.1f} hrs</div>
            </div>
            <div style="background: rgba(15,23,42,0.8); border: 1px solid {'#ef4444' if alerts_count > 0 else '#10b981'}; padding: 6px 14px; border-radius: 8px; text-align: center;">
                <div style="font-size: 0.68rem; color: #94a3b8; font-family: monospace;">ACTIVE ALERTS</div>
                <div style="font-size: 1.15rem; font-weight: 700; color: {'#f87171' if alerts_count > 0 else '#34d399'}; font-family: 'JetBrains Mono';">{alerts_count} ACTIVE</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_kpi_row(machines: List[Dict[str, Any]], orders: List[Dict[str, Any]]):
    """Renders top factory KPI metric cards."""
    total_machines = len(machines)
    avg_health = sum(m["health_score"] for m in machines) / max(1, total_machines)
    at_risk_count = sum(1 for m in machines if m["failure_prob"] > 0.30 or m["health_score"] < 65.0)
    
    total_orders = len(orders)
    delayed_orders = sum(1 for o in orders if o.get("is_delayed", 0) == 1)
    
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    with c1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Average Health</div>
            <div class="kpi-value" style="color: {'#34d399' if avg_health >= 80 else '#fbbf24' if avg_health >= 55 else '#f87171'};">{avg_health:.1f}%</div>
            <div class="kpi-sub">{total_machines} Connected Machines</div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Machines At Risk</div>
            <div class="kpi-value" style="color: {'#f87171' if at_risk_count > 0 else '#34d399'};">{at_risk_count}</div>
            <div class="kpi-sub">{total_machines - at_risk_count} Nominal States</div>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Active Orders</div>
            <div class="kpi-value" style="color: #38bdf8;">{total_orders}</div>
            <div class="kpi-sub">Across 3 Cell Types</div>
        </div>
        """, unsafe_allow_html=True)
    with c4:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Delayed Orders</div>
            <div class="kpi-value" style="color: {'#f87171' if delayed_orders > 0 else '#34d399'};">{delayed_orders}</div>
            <div class="kpi-sub">{((delayed_orders/total_orders)*100 if total_orders else 0):.0f}% of Backlog</div>
        </div>
        """, unsafe_allow_html=True)
    with c5:
        # Approximate current load kW
        cur_power = sum(m.get("power_kw", m.get("nominal_power_kw", 25.0) * 0.75) for m in machines)
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Current Factory Load</div>
            <div class="kpi-value" style="color: #fbbf24;">{cur_power:.1f} kW</div>
            <div class="kpi-sub">Peak Cap: 157.0 kW</div>
        </div>
        """, unsafe_allow_html=True)
    with c6:
        # Factory Overall Equipment Effectiveness (OEE) estimate
        oee = (avg_health * 0.45) + ((1.0 - (delayed_orders / max(1, total_orders))) * 55.0)
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Factory OEE Index</div>
            <div class="kpi-value" style="color: {'#34d399' if oee >= 85 else '#38bdf8' if oee >= 70 else '#f87171'};">{oee:.1f}%</div>
            <div class="kpi-sub">Industry Target: 85%</div>
        </div>
        """, unsafe_allow_html=True)


def render_gauge_chart(value: float, title: str, min_val: float, max_val: float,
                       warn_thresh: float, crit_thresh: float, unit: str = "",
                       reverse_hazard: bool = False) -> go.Figure:
    """Renders a sleek circular sensor gauge with dark industrial theme."""
    if not reverse_hazard:
        steps = [
            {'range': [min_val, warn_thresh], 'color': "rgba(16, 185, 129, 0.25)"},
            {'range': [warn_thresh, crit_thresh], 'color': "rgba(245, 158, 11, 0.25)"},
            {'range': [crit_thresh, max_val], 'color': "rgba(239, 68, 68, 0.35)"}
        ]
        bar_color = "#ef4444" if value >= crit_thresh else "#f59e0b" if value >= warn_thresh else "#10b981"
    else:
        steps = [
            {'range': [min_val, crit_thresh], 'color': "rgba(239, 68, 68, 0.35)"},
            {'range': [crit_thresh, warn_thresh], 'color': "rgba(245, 158, 11, 0.25)"},
            {'range': [warn_thresh, max_val], 'color': "rgba(16, 185, 129, 0.25)"}
        ]
        bar_color = "#ef4444" if value <= crit_thresh else "#f59e0b" if value <= warn_thresh else "#10b981"

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={'text': f"<b style='font-size:14px; color:#cbd5e1;'>{title}</b><br><span style='font-size:11px; color:#94a3b8;'>{unit}</span>"},
        number={'font': {'color': '#f8fafc', 'family': 'JetBrains Mono', 'size': 24}},
        gauge={
            'axis': {'range': [min_val, max_val], 'tickcolor': "#64748b", 'tickwidth': 1},
            'bar': {'color': bar_color, 'thickness': 0.28},
            'bgcolor': "rgba(15, 23, 42, 0.8)",
            'borderwidth': 1,
            'bordercolor': "#334155",
            'steps': steps,
        }
    ))
    fig.update_layout(
        height=180,
        margin=dict(l=15, r=15, t=35, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        font={'color': "#e2e8f0"}
    )
    return fig


def render_telemetry_history_chart(df: pd.DataFrame, machine_id: str) -> go.Figure:
    """Renders multi-sensor live time-series with temperature and vibration."""
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
        line=dict(color="#06b6d4", width=2.5),
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
        title=dict(text=f"Live Sensor Telemetry Stream: {machine_id}", font=dict(color="#f1f5f9", size=15)),
        paper_bgcolor="rgba(15, 23, 42, 0.6)",
        plot_bgcolor="rgba(15, 23, 42, 0.8)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(color="#cbd5e1")),
        height=320,
        margin=dict(l=40, r=40, t=50, b=30),
        xaxis=dict(title="Telemetry Step", gridcolor="#1e293b", color="#94a3b8"),
        yaxis=dict(title=dict(text="Temperature (°C)", font=dict(color="#f97316")), tickfont=dict(color="#f97316"), gridcolor="#1e293b"),
        yaxis2=dict(title=dict(text="Vibration (mm/s)", font=dict(color="#06b6d4")), tickfont=dict(color="#06b6d4"), overlaying="y", side="right"),
        yaxis3=dict(title=dict(text="Power (kW)", font=dict(color="#a855f7")), tickfont=dict(color="#a855f7"), overlaying="y", side="right", position=0.95, showgrid=False),
    )
    return fig


def render_gantt_chart(orders: List[Dict[str, Any]], title: str = "Production Schedule Timeline") -> go.Figure:
    """Renders an interactive Gantt chart of scheduled production orders."""
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
        
        # Color coding by delay risk and priority
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
    # Sort machines
    df = df.sort_values(by=["Machine", "Start"])

    color_map = {
        "ON TRACK": "#10b981",
        "MODERATE RISK": "#f59e0b",
        "CRITICAL DELAY RISK": "#ef4444"
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
        paper_bgcolor="rgba(15, 23, 42, 0.7)",
        plot_bgcolor="rgba(15, 23, 42, 0.9)",
        height=380,
        margin=dict(l=60, r=30, t=50, b=30),
        font=dict(color="#e2e8f0"),
        xaxis=dict(title="Schedule Timeline (Hours from start)", gridcolor="#1e293b", color="#94a3b8", tickformat="%H:%M\nT+%d d"),
        yaxis=dict(title="", gridcolor="#1e293b", color="#e2e8f0", autorange="reversed"),
        legend=dict(orientation="h", y=1.08, x=0.5, xanchor="center", font=dict(color="#cbd5e1"))
    )
    return fig


def render_before_after_comparison(baseline: Dict[str, Any], optimized: Dict[str, Any], improvements: Dict[str, Any]):
    """Renders the comprehensive Before vs. After optimization comparison cards and metrics."""
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
            <div style="font-size: 1.1rem; color: #94a3b8; text-decoration: line-through;">Before: {base_tard:.1f} hrs</div>
            <div style="font-size: 1.6rem; font-weight: 700; color: #34d399; font-family: monospace;">After: {opt_tard:.1f} hrs</div>
            <div class="improvement-badge">▼ {saved_tard:.1f} hrs Delay Saved</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        base_risk = baseline.get("high_risk_assignments", 0)
        opt_risk = optimized.get("high_risk_assignments", 0)
        avoided_risk = improvements.get("high_risk_jobs_avoided", 0)
        st.markdown(f"""
        <div class="comparison-box">
            <div class="kpi-label">Jobs on Degraded Machines</div>
            <div style="font-size: 1.1rem; color: #94a3b8; text-decoration: line-through;">Before: {base_risk} jobs</div>
            <div style="font-size: 1.6rem; font-weight: 700; color: {'#34d399' if opt_risk == 0 else '#fbbf24'}; font-family: monospace;">After: {opt_risk} jobs</div>
            <div class="improvement-badge">▼ {avoided_risk} High-Risk Avoided</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        base_del_orders = baseline.get("delayed_orders_count", 0)
        opt_del_orders = optimized.get("delayed_orders_count", 0)
        del_prevented = improvements.get("delayed_orders_prevented", 0)
        st.markdown(f"""
        <div class="comparison-box">
            <div class="kpi-label">Late Orders Count</div>
            <div style="font-size: 1.1rem; color: #94a3b8; text-decoration: line-through;">Before: {base_del_orders} orders</div>
            <div style="font-size: 1.6rem; font-weight: 700; color: {'#34d399' if opt_del_orders == 0 else '#fbbf24'}; font-family: monospace;">After: {opt_del_orders} orders</div>
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
            <div style="font-size: 1.1rem; color: #94a3b8; text-decoration: line-through;">Before: {base_energy:.1f} kWh</div>
            <div style="font-size: 1.6rem; font-weight: 700; color: #38bdf8; font-family: monospace;">After: {opt_energy:.1f} kWh</div>
            <div class="improvement-badge">▼ {saved_energy:.1f} kWh Conserved</div>
        </div>
        """, unsafe_allow_html=True)
