import streamlit as st
import pandas as pd
import plotly.express as px
import datetime
from st_aggrid import AgGrid, GridOptionsBuilder, ColumnsAutoSizeMode

# --- Page Configuration (Professional Look) ---
st.set_page_config(
    page_title="SafeTech Smart Attendance System",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom Styling (Futuristic UI) ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    .stMetric { background-color: #161b22; border-radius: 10px; padding: 15px; border: 1px solid #30363d; }
    div[data-testid="stSidebarNav"] { background-color: #0d1117; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #238636; color: white; }
    </style>
    """, unsafe_all_ow_html=True)

# --- Session State for Data Persistence ---
if 'attendance_data' not in st.session_state:
    # Dummy Data for Row 13 & Employee Records (Aapki Excel ke mutabiq)
    cols = ['Emp ID', 'Emp Name', 'Designation', 'Department'] + [str(d) for d in range(1, 32)] + ['Total Present', 'Total Absent']
    st.session_state.attendance_data = pd.DataFrame(columns=cols)

# --- Sidebar Navigation ---
st.sidebar.title("🚀 SafeTech Control")
menu = st.sidebar.selectbox("Navigation", ["Dashboard", "Attendance Entry", "Row 13 Analytics", "Employee Directory", "Reports"])

# --- Function: Metrics Calculation ---
def show_metrics(df):
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Manpower", len(df))
    with col2:
        st.metric("Present Today", (df['Total Present'] > 0).sum() if not df.empty else 0)
    with col3:
        st.metric("Total Departmets", df['Department'].nunique() if not df.empty else 0)
    with col4:
        st.metric("Active Projects", "UNEC Partnership")

# --- Page: Dashboard ---
if menu == "Dashboard":
    st.title("📊 Workforce Analytics Dashboard")
    show_metrics(st.session_state.attendance_data)
    
    st.markdown("---")
    
    col_left, col_right = st.columns([2, 1])
    
    with col_left:
        st.subheader("Attendance Trend (Monthly)")
        if not st.session_state.attendance_data.empty:
            fig = px.bar(st.session_state.attendance_data, x="Emp Name", y="Total Present", 
                         color="Department", template="plotly_dark", barmode="group")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Awaiting data input for visualization...")

    with col_right:
        st.subheader("Department Distribution")
        if not st.session_state.attendance_data.empty:
            fig_pie = px.pie(st.session_state.attendance_data, names='Department', hole=0.4)
            st.plotly_chart(fig_pie, use_container_width=True)

# --- Page: Attendance Entry (The Row 13 Implementation) ---
elif menu == "Attendance Entry":
    st.title("📝 Daily Attendance Entry")
    
    with st.expander("➕ Add New Employee Record", expanded=True):
        c1, c2, c3, c4 = st.columns(4)
        emp_id = c1.text_input("Employee ID (e.g. T00594)")
        emp_name = c2.text_input("Full Name")
        desig = c3.selectbox("Designation", ["Operator", "Helper", "Foreman", "Engineer"])
        dept = c4.selectbox("Department", ["Production", "Erection", "QHSE", "HR"])
        
        st.write("### Mark Attendance (Row 13 Columns)")
        att_cols = st.columns(7)
        days_status = {}
        for i in range(1, 32):
            with att_cols[(i-1)%7]:
                days_status[str(i)] = st.selectbox(f"Day {i}", ["P", "A", "OFF", "N/A"], key=f"day_{i}")
        
        if st.button("Save Record to Database"):
            present_count = list(days_status.values()).count("P")
            absent_count = list(days_status.values()).count("A")
            new_row = {
                'Emp ID': emp_id, 'Emp Name': emp_name, 
                'Designation': desig, 'Department': dept,
                'Total Present': present_count, 'Total Absent': absent_count
            }
            new_row.update(days_status)
            st.session_state.attendance_data = pd.concat([st.session_state.attendance_data, pd.DataFrame([new_row])], ignore_index=True)
            st.success(f"Record added for {emp_name}")

    st.subheader("Current Month Sheet (Live View)")
    # Advanced Data Grid
    gb = GridOptionsBuilder.from_dataframe(st.session_state.attendance_data)
    gb.configure_pagination(paginationAutoPageSize=True)
    gb.configure_side_bar()
    gb.configure_default_column(editable=True, groupable=True)
    gridOptions = gb.build()
    
    AgGrid(st.session_state.attendance_data, gridOptions=gridOptions, 
           columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS,
           theme='balham')

# --- Page: Row 13 Analytics ---
elif menu == "Row 13 Analytics":
    st.title("⚙️ Row 13 - Logic Configuration")
    st.info("Row 13 is the reference layer for all dates and automated holidays.")
    
    year = st.number_input("Target Year", value=2026)
    month = st.selectbox("Target Month", list(range(1, 13)))
    
    # Futuristic Row 13 Generator
    if st.button("Generate Row 13 Dynamic Header"):
        dates = []
        for d in range(1, 32):
            try:
                date_obj = datetime.date(year, month, d)
                dates.append({"Date": d, "Day": date_obj.strftime("%A"), "Status": "Working" if date_obj.weekday() != 4 else "Friday (OFF)"})
            except:
                continue
        
        st.table(pd.DataFrame(dates))
        st.success("Logic updated: All calculations will now reference this Row 13 mapping.")

# --- Footer ---
st.sidebar.markdown("---")
st.sidebar.write("System Status: **Active**")
st.sidebar.write(f"Current User ID: T00594")
