import streamlit as st
import pandas as pd
import plotly.express as px
import datetime
from st_aggrid import AgGrid, GridOptionsBuilder, ColumnsAutoSizeMode

# --- Page Configuration ---
st.set_page_config(
    page_title="SafeTech Smart Attendance System",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom Styling ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    .stMetric { background-color: #161b22; border-radius: 10px; padding: 15px; border: 1px solid #30363d; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #238636; color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- Session State Initialization ---
if 'attendance_data' not in st.session_state:
    cols = ['Emp ID', 'Emp Name', 'Designation', 'Department'] + [str(d) for d in range(1, 32)] + ['Total Present', 'Total Absent']
    st.session_state.attendance_data = pd.DataFrame(columns=cols)

# --- Sidebar ---
st.sidebar.title("🚀 SafeTech Control")
menu = st.sidebar.selectbox("Navigation", ["Dashboard", "Attendance Entry", "Row 13 Analytics"])

# --- Page: Dashboard ---
if menu == "Dashboard":
    st.title("📊 Workforce Analytics Dashboard")
    df = st.session_state.attendance_data
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Manpower", len(df))
    col2.metric("Departments", df['Department'].nunique() if not df.empty else 0)
    col3.metric("Status", "Active")

    if not df.empty:
        fig = px.bar(df, x="Emp Name", y="Total Present", color="Department", template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data available yet.")

# --- Page: Attendance Entry ---
elif menu == "Attendance Entry":
    st.title("📝 Daily Attendance Entry")
    
    with st.expander("➕ Add New Employee Record", expanded=True):
        c1, c2, c3, c4 = st.columns(4)
        emp_id = c1.text_input("Employee ID")
        emp_name = c2.text_input("Full Name")
        desig = c3.selectbox("Designation", ["Operator", "Helper", "Foreman", "Engineer"])
        dept = c4.selectbox("Department", ["Production", "Erection", "QHSE", "HR"])
        
        st.write("### Mark Attendance (1-31)")
        days_status = {}
        # Display inputs in a grid
        for i in range(1, 32):
            days_status[str(i)] = "P" # Default value

        if st.button("Save Record"):
            if emp_id and emp_name:
                new_row = {
                    'Emp ID': emp_id, 'Emp Name': emp_name, 
                    'Designation': desig, 'Department': dept,
                    'Total Present': 1, 'Total Absent': 0 # Dummy calc for now
                }
                new_row.update(days_status)
                st.session_state.attendance_data = pd.concat([st.session_state.attendance_data, pd.DataFrame([new_row])], ignore_index=True)
                st.success(f"Record added for {emp_name}")
            else:
                st.error("Bhai Emp ID aur Name to likho!")

    st.subheader("Live Attendance Sheet")
    if not st.session_state.attendance_data.empty:
        gb = GridOptionsBuilder.from_dataframe(st.session_state.attendance_data)
        gb.configure_default_column(editable=True, groupable=True)
        gridOptions = gb.build()
        
        # FIXED: Changed ColumnsAutoSizeMode to a valid attribute
        AgGrid(
            st.session_state.attendance_data, 
            gridOptions=gridOptions, 
            columns_auto_size_mode=ColumnsAutoSizeMode.FIT_ALL_COLUMNS_TO_VIEW,
            theme='alpine' # 'alpine' looks more professional than 'balham'
        )

# --- Page: Row 13 Analytics ---
elif menu == "Row 13 Analytics":
    st.title("⚙️ Row 13 Configuration")
    year = st.number_input("Year", value=2026)
    month = st.selectbox("Month", list(range(1, 13)))
    
    if st.button("Generate Header"):
        st.write(f"Generating Row 13 logic for {month}/{year}...")
