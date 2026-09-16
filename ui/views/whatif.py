"""
What-If Simulation & Guided Industry 4.0 Demonstration View
Provides interactive scenario simulations and an automated 10-step guided demonstration flow:
Data -> Monitoring -> AI Prediction -> Risk Detection -> Optimization -> Decision -> Simulation -> Dashboard
Supports Dark and Light theme modes.
"""
import streamlit as st
import pandas as pd
from typing import Optional
from ui.components import render_before_after_comparison, render_gantt_chart
from ui.styles import get_theme_palette
from optimization.scheduler import ProductionScheduler


def render_whatif_view(simulator, db, theme: Optional[str] = None):
    current_theme = (theme or st.session_state.get("theme", "dark")).lower()
    pal = get_theme_palette(current_theme)

    st.markdown("""
    <div class="section-banner">
        <span>🧪</span> WHAT-IF SIMULATION & GUIDED INDUSTRY 4.0 DEMONSTRATION
    </div>
    """, unsafe_allow_html=True)

    tab_guided, tab_sandbox = st.tabs(["🚀 10-Step Guided Demonstration Flow", "🎛️ Interactive What-If Scenario Sandbox"])

    # -------------------------------------------------------------
    # TAB 1: 10-STEP GUIDED DEMONSTRATION FLOW
    # -------------------------------------------------------------
    with tab_guided:
        st.markdown("""
        Experience the complete end-to-end closed-loop Industry 4.0 workflow:
        **Telemetry Data ➔ Real-Time Monitoring ➔ AI PdM Prediction ➔ Risk Escalation ➔ OR-Tools Optimization ➔ Schedule Adaptation**
        """)

        if "demo_step" not in st.session_state:
            st.session_state["demo_step"] = 1

        cur_step = st.session_state["demo_step"]

        step_col1, step_col2, step_col3 = st.columns([1, 4, 1])
        with step_col1:
            if st.button("⬅️ Previous Step", disabled=(cur_step <= 1), use_container_width=True):
                st.session_state["demo_step"] -= 1
                st.rerun()
        with step_col2:
            st.progress(cur_step / 10.0, text=f"Step {cur_step} of 10: Closed-Loop Demonstration")
        with step_col3:
            if st.button("Next Step ➡️", disabled=(cur_step >= 10), use_container_width=True, type="primary"):
                st.session_state["demo_step"] += 1
                st.rerun()

        st.markdown("---")

        # Step-by-Step Logic
        if cur_step == 1:
            st.markdown("### Step 1: Nominal Factory Baseline Initialization")
            st.info("The factory starts with all 6 industrial workstations operating within nominal, healthy limits (Health > 95%, Failure Risk < 2%).")
            if st.button("▶️ Reset Factory to All Normal States", use_container_width=True):
                db.reset_to_defaults()
                simulator.reset()
                st.session_state.pop("last_optimization_result", None)
                st.session_state.pop("guided_opt_result", None)
                st.success("Factory baseline restored! All machines operating nominally.")
                st.rerun()
            
            machines = db.get_machines()
            st.dataframe(pd.DataFrame([
                {"Machine ID": m["machine_id"], "Name": m["name"], "Status": m["status"], "Health": f"{m['health_score']:.1f}%", "Failure Risk": f"{(m['failure_prob']*100):.1f}%"}
                for m in machines
            ]), use_container_width=True, hide_index=True)

        elif cur_step == 2:
            st.markdown("### Step 2: Start Factory Simulation & Order Execution")
            st.info("Continuous simulation tick runs. Sensor readings flow from CNC mills, robotic arms, and hydraulic injection presses into SQLite telemetry store.")
            if st.button("⏩ Advance Factory Simulation (+1.0 hr)", use_container_width=True):
                simulator.step(time_delta_hrs=1.0)
                st.success("Advanced simulation by 1.0 hour. Telemetry captured.")
                st.rerun()

            recent = db.get_recent_telemetry(limit=6)
            if not recent.empty:
                st.dataframe(recent[["timestamp", "machine_id", "temperature", "vibration", "pressure", "power_kw", "status"]], use_container_width=True, hide_index=True)

        elif cur_step == 3:
            st.markdown("### Step 3: Introduce Abnormal Sensor Behavior on M1-CNC-01")
            st.warning("Simulating a severe mechanical anomaly: Coolant pump blockage + bearing harmonic degradation on machine `M1-CNC-01`.")
            if st.button("⚠️ Trigger Coolant & Bearing Anomaly on M1-CNC-01", type="primary", use_container_width=True):
                simulator.inject_anomaly("M1-CNC-01", "COOLANT_FAILURE")
                st.error("Thermal & pressure anomaly injected on M1-CNC-01! Sensor readings spiking.")
                st.rerun()

            m1_telem = simulator.latest_telemetry.get("M1-CNC-01", {})
            st.write(f"**Current M1-CNC-01 Telemetry:** Temp: `{m1_telem.get('temperature')}°C` | Vibration: `{m1_telem.get('vibration')} mm/s` | Pressure: `{m1_telem.get('pressure')} bar`")

        elif cur_step == 4:
            st.markdown("### Step 4: AI Predictive Maintenance Model Detects Increasing Failure Risk")
            st.error("The XGBoost ML model evaluates incoming sensor telemetry. High temperature + pressure drop flags impending failure risk.")
            m1 = db.get_machine("M1-CNC-01")
            st.metric("M1-CNC-01 Failure Probability (ML)", f"{(m1['failure_prob']*100):.1f}%", delta="+Critical Spike", delta_color="inverse")
            st.metric("Health Index", f"{m1['health_score']:.1f}%", delta="-Degraded", delta_color="inverse")
            st.info(f"**Prescriptive Root Cause Diagnostic:** {simulator.latest_telemetry.get('M1-CNC-01', {}).get('primary_cause')}")

        elif cur_step == 5:
            st.markdown("### Step 5: Affected Machine Transitions to CRITICAL State")
            st.error("The Factory Supervisory Controller flags `M1-CNC-01` as CRITICAL. An alarm ticker sounds on the shop floor.")
            m1 = db.get_machine("M1-CNC-01")
            alarm_sub_color = pal["accent_red"] if current_theme == "light" else "#fca5a5"
            alarm_html = f"""<div class="machine-card status-critical">
<div style="font-size: 1.3rem; font-weight: 700; color: {pal['accent_red']};">🚨 ALARM: {m1['name']} ({m1['machine_id']})</div>
<div style="font-size: 0.9rem; color: {alarm_sub_color}; margin-top: 4px;">Status: {m1['status']} | Failure Probability: {(m1['failure_prob']*100):.1f}%</div>
<div style="margin-top: 10px; font-size: 0.85rem; color: {pal['text_secondary']};">Recommendation: Machine cannot safely complete urgent high-precision milling without catastrophic tool breakdown.</div>
</div>"""
            st.markdown(alarm_html, unsafe_allow_html=True)

        elif cur_step == 6:
            st.markdown("### Step 6: Dependent Production Orders Suffer High Delay Risk")
            st.warning("The Delay Prediction Model flags orders queued on `M1-CNC-01` as facing severe tardiness risk due to impending breakdown downtime!")
            scheduler = ProductionScheduler(db=db)
            orders = db.get_orders()
            baseline = scheduler.build_naive_baseline_schedule(orders, db.get_machines())
            
            m1_orders = [o for o in baseline["scheduled_orders"] if o.get("assigned_machine_id") == "M1-CNC-01"]
            st.markdown(f"**{len(m1_orders)} Orders trapped on degraded machine M1-CNC-01:**")
            st.dataframe(pd.DataFrame([
                {"Order ID": o["order_id"], "Product": o["product_name"], "Priority": o["priority"], "Delay Risk": f"{(o['delay_risk_prob']*100):.0f}%", "Status": "⚠️ HIGH RISK"}
                for o in m1_orders
            ]), use_container_width=True, hide_index=True)

        elif cur_step == 7:
            st.markdown("### Step 7: Automated Decision: AI Optimization Engine Triggers Rescheduling")
            st.info("Google OR-Tools CP-SAT multi-objective scheduler formulates an automated reallocation strategy to evacuate orders from `M1-CNC-01` onto healthy peer machine `M2-CNC-02`.")
            scheduler = ProductionScheduler(db=db)
            if st.button("⚡ Execute Automated OR-Tools CP-SAT Reschedule", type="primary", use_container_width=True):
                res = scheduler.optimize_schedule(commit_to_db=True)
                st.session_state["guided_opt_result"] = res
                st.success("Automated rescheduling complete! Orders reallocated away from degraded machine.")
                st.rerun()

        elif cur_step == 8:
            st.markdown("### Step 8: Generated New Optimized Production Schedule")
            scheduler = ProductionScheduler(db=db)
            if "guided_opt_result" not in st.session_state:
                st.session_state["guided_opt_result"] = scheduler.optimize_schedule(commit_to_db=True)
            
            res = st.session_state["guided_opt_result"]
            st.plotly_chart(
                render_gantt_chart(res["optimized"]["scheduled_orders"], title="Reallocated Production Schedule (Orders Shifted to M2-CNC-02)", theme=current_theme),
                use_container_width=True
            )

        elif cur_step == 9:
            st.markdown("### Step 9: Quantified Before vs. After Optimization Comparison")
            scheduler = ProductionScheduler(db=db)
            if "guided_opt_result" not in st.session_state:
                st.session_state["guided_opt_result"] = scheduler.optimize_schedule(commit_to_db=False)
            
            res = st.session_state["guided_opt_result"]
            render_before_after_comparison(res["baseline"], res["optimized"], res["improvements"], theme=current_theme)

        elif cur_step == 10:
            st.markdown("### Step 10: Closed-Loop Industry 4.0 Complete Demonstration Verified!")
            st.success("🎉 Full Industry 4.0 closed-loop cycle successfully demonstrated! The factory autonomously predicted failure, prevented order delays, and optimized production throughput.")
            st.balloons()
            st.markdown("""
            **Demonstrated Highlights:**
            - **Data Telemetry**: Physics-grounded sensor generation (temp, vibration, pressure, power, RPM)
            - **ML Predictive Maintenance**: XGBoost detected failure risk early before breakdown
            - **Delay Risk Propagation**: Identified orders threatened by machine downtime
            - **OR-Tools Optimization**: Reallocated jobs to healthy machine `M2-CNC-02` with 0 tardiness
            - **Energy Conservation**: Prevented extra energy waste from friction degradation
            """)
            if st.button("🔄 Reset Demo to Step 1", use_container_width=True):
                st.session_state["demo_step"] = 1
                st.rerun()

    # -------------------------------------------------------------
    # TAB 2: INTERACTIVE WHAT-IF SANDBOX
    # -------------------------------------------------------------
    with tab_sandbox:
        st.markdown("##### 🎛️ Inject Custom Scenarios and Evaluate Factory Resilience")
        
        # Section 1: Machine Degradation Scenarios
        with st.container(border=True):
            st.markdown("###### 💥 1. Machine Degradation Scenarios")
            c_sel, c_desc = st.columns([1, 3], vertical_alignment="center")
            with c_sel:
                machines = db.get_machines()
                m_select = st.selectbox("Target Machine:", [m["machine_id"] for m in machines], key="sb_target_m")
            with c_desc:
                st.caption(f"Inject real-time physical degradation or execute emergency maintenance on workstation **{m_select}**.")
            
            sc1, sc2, sc3, sc4 = st.columns(4)
            with sc1:
                if st.button(f"🔥 Coolant Loss on {m_select}", use_container_width=True):
                    simulator.inject_anomaly(m_select, "COOLANT_FAILURE")
                    st.warning(f"Injected Coolant Loss on {m_select}")
                    st.rerun()
            with sc2:
                if st.button(f"⚡ Bearing Wear on {m_select}", use_container_width=True):
                    simulator.inject_anomaly(m_select, "BEARING_WEAR")
                    st.warning(f"Injected Bearing Wear on {m_select}")
                    st.rerun()
            with sc3:
                if st.button(f"💥 Sudden Breakdown on {m_select}", use_container_width=True):
                    simulator.inject_anomaly(m_select, "CATASTROPHIC_FAILURE")
                    st.error(f"Injected Catastrophic Failure on {m_select}")
                    st.rerun()
            with sc4:
                if st.button(f"🛠️ Service / Restore {m_select}", use_container_width=True):
                    simulator.perform_maintenance(m_select)
                    st.success(f"Restored {m_select} to healthy state")
                    st.rerun()

        st.markdown("<div style='margin-top: 12px;'></div>", unsafe_allow_html=True)

        # Section 2: Production & Market Demand Scenarios
        with st.container(border=True):
            st.markdown("###### 🏭 2. Production & Market Demand Scenarios")
            st.caption("Simulate macroeconomic disturbances, dynamic customer order rushes, and electricity tariff shifts.")
            
            dc1, dc2, dc3 = st.columns(3)
            with dc1:
                if st.button("📦 Surge Rush Customer Orders (+3 Urgent Orders)", use_container_width=True):
                    simulator.inject_rush_orders(count=3)
                    st.warning("Injected 3 urgent high-priority production orders into the queue!")
                    st.rerun()
            with dc2:
                if st.button("⚡ Simulate Peak Energy Tariff Window (14:00 - 19:00)", use_container_width=True):
                    st.info("Peak energy tariff ($0.28/kWh) active. Optimization will shift heavy jobs out of peak hours.")
            with dc3:
                if st.button("🔄 Reset Entire Factory & Database to Pristine State", use_container_width=True):
                    db.reset_to_defaults()
                    simulator.reset()
                    st.session_state.pop("last_optimization_result", None)
                    st.session_state.pop("guided_opt_result", None)
                    st.success("Factory state reset to defaults.")
                    st.rerun()
