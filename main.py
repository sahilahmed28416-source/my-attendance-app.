import streamlit as st
import pandas as pd
import datetime
import calendar
from st_aggrid import AgGrid, GridOptionsBuilder, ColumnsAutoSizeMode

# --- Page Config ---
st.set_page_config(page_title="SafeTech Smart Attendance", layout="wide")

# Custom CSS for Professional Table Look
st.markdown("""
    <style>
    .reportview-container .main .block-container { padding-top: 2rem; }
    th { background-color: #2c3e50 !important; color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# --- Logic: Dynamic Row 13 Generator ---
def get_month_days(year, month):
    num_days = calendar.monthrange(year, month)[1]
    days_list = []
    for day in range(1, num_days + 1):
        date_obj = datetime.date(year, month, day)
        days_list.append({
            "Date": day,
            "DayName": date_obj.strftime('%a') # Thu, Fri, etc.
        })
    return days_list

# --- Sidebar ---
st.sidebar.title("🛠️ SafeTech Admin")
selected_month = st.sidebar.selectbox("Select Month", list(calendar.month_name)[1:], index=datetime.datetime.now().month-1)
selected_year = st.sidebar.number_input("Year", value=2026)
month_num = list(calendar.month_name).index(selected_month)

# --- Data Structure ---
# Based on your image: Srl No, Emp ID, Name, Designation, Dept, Joining, [1-31], DA/NA, DP/NP
month_days = get_month_days(selected_year, month_num)
day_cols = [f"{d['Date']}\n({d['DayName']})" for d in month_days]
base_cols = ['Srl No', 'Emp ID', 'Emp Name', 'Designation', 'Department', 'Joining Date']
final_cols = base_cols + day_cols + ['DA/NA', 'DP/NP']

if 'master_df' not in st.session_state:
    st.session_state.master_df = pd.DataFrame(columns=final_cols)

# --- UI Layout ---
st.title(f"📊 Monthly Attendance: {selected_month} {selected_year}")

# Metrics section (matching your sheet's top summary)
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Manpower", "779") # Example value from your photo
c2.metric("Total Present", "317")
c3.metric("Total Absent", "9")
c4.metric("On Leave", "99")

st.write("---")

# --- Attendance Table (The Main Grid) ---
st.subheader("Attendance Master Sheet (Row 13 Style)")

gb = GridOptionsBuilder.from_dataframe(st.session_state.master_df)
gb.configure_default_column(editable=True, resizable=True, width=100)
gb.configure_column("Emp Name", width=200, pinned='left')
gb.configure_column("Emp ID", width=100, pinned='left')

# Logic for Auto-Calculation (DP/NP)
# Yahan hum logic daal sakte hain jo 'P' ya 'D' count kare
grid_options = gb.build()

grid_response = AgGrid(
    st.session_state.master_df,
    gridOptions=grid_options,
    data_return_mode='AS_INPUT',
    update_mode='MODEL_CHANGED',
    fit_columns_on_grid_load=False,
    theme='alpine', # Professional theme
)

# --- Add New Worker ---
with st.expander("➕ Add New Worker"):
    with st.form("new_worker"):
        cc1, cc2, cc3 = st.columns(3)
        new_id = cc1.text_input("Emp ID")
        new_name = cc2.text_input("Emp Name")
        new_dept = cc3.selectbox("Department", ["Production", "Erection", "QHSE", "HR"])
        
        if st.form_submit_button("Add to Sheet"):
            new_row = pd.DataFrame([{ "Emp ID": new_id, "Emp Name": new_name, "Department": new_dept }])
            st.session_state.master_df = pd.concat([st.session_state.master_df, new_row], ignore_index=True)
            st.rerun()

st.sidebar.markdown("---")
st.sidebar.info(f"System Status: Active")
