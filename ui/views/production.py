"""
Production Management View
Manage production orders backlog, track completion, create new orders,
and monitor AI delay risk predictions.
"""
import streamlit as st
import pandas as pd
from typing import Dict, Any, List
from config import PRODUCTS, PRIORITY_WEIGHTS


def render_production_view(simulator, db):
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
        status_options = list(set(o.get("status", "Pending") for o in orders))
        status_filter = st.multiselect("Filter by Status:", status_options, default=status_options)

    filtered_orders = [
        o for o in orders
        if o.get("priority") in prio_filter and o.get("status") in status_filter
    ]

    # Render Table
    if filtered_orders:
        table_rows = []
        for o in filtered_orders:
            delay_risk = o.get("delay_risk_prob", 0.0)
            is_del = o.get("is_delayed", 0)
            
            if is_del:
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
                "Duration (hrs)": o["processing_time_hrs"],
                "Deadline (hrs)": o["deadline_hrs"],
                "Assigned Machine": o.get("assigned_machine_id") or "Unassigned",
                "Status": o["status"],
                "Delay Risk (%)": f"{delay_risk*100:.1f}%",
                "Schedule Risk": status_badge,
                "Energy (kWh)": o.get("energy_kwh_predicted", 0.0)
            })
        
        df_orders = pd.DataFrame(table_rows)
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
