"""
AI Production Optimizer Studio View
Runs Google OR-Tools CP-SAT multi-objective schedule optimization,
renders interactive Gantt timeline charts, and displays Before vs. After comparison metrics with Dark/Light theme support.
"""
import streamlit as st
import pandas as pd
from typing import Optional
from ui.components import render_gantt_chart, render_before_after_comparison
from optimization.scheduler import ProductionScheduler


def render_optimizer_view(simulator, db, theme: Optional[str] = None):
    current_theme = (theme or st.session_state.get("theme", "dark")).lower()

    st.markdown("""
    <div class="section-banner">
        <span>🧠</span> AI PRODUCTION SCHEDULING & MULTI-OBJECTIVE OPTIMIZATION
    </div>
    """, unsafe_allow_html=True)

    scheduler = ProductionScheduler(db=db)
    orders = db.get_orders()
    machines = db.get_machines()

    st.markdown("""
    The **OR-Tools CP-SAT Mathematical Optimization Engine** solves a multi-objective constraint programming model:
    - **Objective 1**: Minimize Weighted Tardiness (prioritizing high-priority and urgent orders before their deadlines)
    - **Objective 2**: Minimize Machine Failure Risk Exposure (penalizing job assignment to degraded or failing machines)
    - **Objective 3**: Minimize Total Factory Energy Consumption and Avoid Peak Load Spikes
    """)

    opt_col1, opt_col2, opt_col3 = st.columns([2, 2, 2], vertical_alignment="bottom")
    with opt_col1:
        time_limit = st.slider("Solver Time Limit (seconds):", min_value=1.0, max_value=10.0, value=3.0, step=1.0)
    with opt_col2:
        commit_to_db = st.checkbox("Commit Optimized Schedule to Database", value=True)
    with opt_col3:
        run_opt_btn = st.button("🚀 Run AI Production Optimization", use_container_width=True, type="primary")

    # If button clicked or session state has previous results
    if run_opt_btn or "last_optimization_result" in st.session_state:
        if run_opt_btn:
            with st.spinner("Solving multi-objective CP-SAT constraint formulation..."):
                res = scheduler.optimize_schedule(
                    orders=orders,
                    machines=machines,
                    max_solve_time_sec=time_limit,
                    commit_to_db=commit_to_db
                )
                st.session_state["last_optimization_result"] = res
                st.success(f"Optimal schedule computed in {res['solve_time_ms']} ms! Status: {res['solver_status']}")
        
        res = st.session_state["last_optimization_result"]
        baseline = res["baseline"]
        optimized = res["optimized"]
        improvements = res["improvements"]

        # Before vs After Comparison Summary Cards
        render_before_after_comparison(baseline, optimized, improvements, theme=current_theme)

        # Interactive Gantt Chart
        st.markdown("##### 📅 Optimized Shop Floor Schedule Gantt Chart")
        st.plotly_chart(
            render_gantt_chart(optimized["scheduled_orders"], title="AI-Optimized Multi-Machine Production Schedule", theme=current_theme),
            use_container_width=True
        )

        # Baseline vs Optimized Comparison Details
        st.markdown("##### 🔍 Schedule Assignment Comparison: Before (Naive FIFO) vs. After (AI Optimized)")
        
        base_map = {o["order_id"]: o for o in baseline["scheduled_orders"]}
        comp_rows = []
        for opt_o in optimized["scheduled_orders"]:
            oid = opt_o["order_id"]
            base_o = base_map.get(oid, {})
            
            comp_rows.append({
                "Order ID": oid,
                "Product": opt_o.get("product_name", ""),
                "Priority": opt_o["priority"],
                "Machine (Before)": base_o.get("assigned_machine_id", "None"),
                "Machine (After)": opt_o["assigned_machine_id"],
                "Reallocated?": "🔄 YES" if base_o.get("assigned_machine_id") != opt_o["assigned_machine_id"] else "— SAME",
                "Delay Risk (Before)": f"{(base_o.get('delay_risk_prob', 0)*100):.0f}%",
                "Delay Risk (After)": f"{(opt_o.get('delay_risk_prob', 0)*100):.0f}%",
                "Scheduled End (After)": f"{opt_o['scheduled_end_hrs']:.1f} h",
                "Deadline": f"{opt_o['deadline_hrs']:.1f} h",
                "Status": "⚠️ LATE" if opt_o.get("is_delayed") else "✅ ON TIME"
            })

        st.dataframe(pd.DataFrame(comp_rows), use_container_width=True, hide_index=True)
    else:
        # Show initial unoptimized baseline
        baseline = scheduler.build_naive_baseline_schedule(orders, machines)
        st.info("Showing current unoptimized baseline schedule. Click 'Run AI Production Optimization' above to generate an optimized schedule!")
        st.plotly_chart(
            render_gantt_chart(baseline["scheduled_orders"], title="Current Naive Baseline Schedule (Unoptimized)", theme=current_theme),
            use_container_width=True
        )
