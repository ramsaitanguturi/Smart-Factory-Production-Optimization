"""
Production Management View
Manage production orders backlog, track completion, create new orders,
and monitor AI delay risk predictions.
"""
import streamlit as st
import pandas as pd
from typing import Dict, Any, List, Optional
from config import PRODUCTS, PRIORITY_WEIGHTS


def build_orders_table(filtered_orders: List[Dict[str, Any]]) -> pd.DataFrame:
    """Formats raw order dictionaries into a clean, display-ready DataFrame."""
    table_rows = []
    for o in filtered_orders:
        delay_risk = float(o.get("delay_risk_prob") or 0.0)
        is_del = int(o.get("is_delayed") or 0)
        
        status_val = o.get("status", "Pending")
        if status_val == "Completed":
            display_status = "✅ Completed"
        elif status_val == "In-Progress":
            display_status = "⚙️ In-Progress"
        elif status_val == "Scheduled":
            display_status = "📅 Scheduled"
        else:
            display_status = "⏳ Pending"

        # Determine schedule risk badge
        if status_val == "Completed":
            status_badge = "⚠️ LATE" if is_del else "✅ ON TIME"
        elif is_del:
            status_badge = "⚠️ LATE"
        elif delay_risk > 0.50:
            status_badge = "⚠️ AT RISK"
        else:
            status_badge = "✅ ON TIME"

        table_rows.append({
            "Order ID": o["order_id"],
            "Product": o["product_name"],
            "Quantity": o["quantity"],
            "Machine Type": o["required_machine_type"],
            "Priority": o["priority"],
            "Remaining Time (hrs)": f"{float(o.get('processing_time_hrs') or 0.0):.1f} h",
            "Start Time": f"T + {float(o.get('scheduled_start_hrs') or 0.0):.1f} h",
            "Deadline": f"T + {float(o.get('deadline_hrs') or 0.0):.1f} h",
            "Assigned Machine": o.get("assigned_machine_id") or "Unassigned",
            "Status": display_status,
            "Delay Risk (%)": f"{delay_risk*100:.1f}%",
            "Schedule Risk": status_badge,
            "Energy (kWh)": round(float(o.get("energy_kwh_predicted") or 0.0), 1)
        })
    return pd.DataFrame(table_rows)


def render_production_view(simulator, db, theme: Optional[str] = None):
    st.markdown("""
    <div class="section-banner">
        <span>📋</span> PRODUCTION ORDERS QUEUE & DELAY RISK MANAGEMENT
    </div>
    """, unsafe_allow_html=True)

    orders = db.get_orders()

    # Filter row
    f_col1, f_col2, f_col3 = st.columns([2, 2, 3])
    with f_col1:
        prio_filter = st.multiselect("Filter by Priority:", ["Urgent", "High", "Medium", "Low"], default=["Urgent", "High", "Medium", "Low"])
    with f_col2:
        valid_statuses = ["In-Progress", "Scheduled", "Pending", "Completed"]
        present_statuses = list(set(o.get("status", "Pending") for o in orders))
        status_options = [s for s in valid_statuses if s in present_statuses] + [s for s in present_statuses if s not in valid_statuses]
        if not status_options:
            status_options = valid_statuses
        status_filter = st.multiselect("Filter by Status:", status_options, default=status_options)

    filtered_orders = [
        o for o in orders
        if o.get("priority") in prio_filter and o.get("status") in status_filter
    ]

    with f_col3:
        n_tot = len(filtered_orders)
        n_prog = sum(1 for o in filtered_orders if o.get("status") == "In-Progress")
        n_del = sum(1 for o in filtered_orders if o.get("is_delayed", 0) == 1)
        mc1, mc2, mc3 = st.columns(3)
        with mc1:
            st.metric("Total Shown", n_tot)
        with mc2:
            st.metric("In-Progress", n_prog)
        with mc3:
            st.metric("Delayed", n_del, delta=f"-{n_del}" if n_del > 0 else "0", delta_color="inverse")

    # Render Table
    if filtered_orders:
        df_orders = build_orders_table(filtered_orders)
        st.dataframe(df_orders, use_container_width=True, hide_index=True)
    else:
        st.info("No orders matching current filter criteria.")

    # Create New Production Order Section
    st.markdown("""
    <div class="section-banner">
        <span>➕</span> DISPATCH NEW PRODUCTION ORDER
    </div>
    """, unsafe_allow_html=True)

    with st.form("new_order_form"):
        c1, c2, c3 = st.columns(3)
        with c1:
            prod_names = {p["code"]: f"{p['name']} ({p['machine_type']})" for p in PRODUCTS}
            selected_pcode = st.selectbox("Product Catalog", options=list(prod_names.keys()), format_func=lambda x: prod_names[x])
            qty = st.number_input("Batch Quantity (Units)", min_value=1, max_value=500, value=25, step=5)
        with c2:
            p_obj = next(p for p in PRODUCTS if p["code"] == selected_pcode)
            proc_time = st.number_input("Required Processing Time (hrs)", min_value=0.5, max_value=24.0, value=float(p_obj["base_time_hrs"]), step=0.5)
            prio = st.selectbox("Order Priority", ["Low", "Medium", "High", "Urgent"], index=2)
        with c3:
            deadline = st.number_input("Delivery Deadline (hrs from now)", min_value=1.0, max_value=72.0, value=12.0, step=1.0)
            new_oid = db.get_next_order_id()
            submit_btn = st.form_submit_button("🚀 Submit Order to Shop Floor Backlog", use_container_width=True)

        if submit_btn:
            success = db.add_order(
                order_id=new_oid,
                product_code=p_obj["code"],
                product_name=p_obj["name"],
                quantity=qty,
                processing_time_hrs=proc_time,
                required_machine_type=p_obj["machine_type"],
                priority=prio,
                deadline_hrs=deadline
            )
            if success:
                st.success(f"Production Order {new_oid} successfully queued for scheduling!")
                st.rerun()
            else:
                st.error(f"Failed to queue order {new_oid}: ID conflict or database error.")
