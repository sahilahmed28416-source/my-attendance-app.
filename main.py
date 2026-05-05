import streamlit as st
import pandas as pd
import os
from datetime import datetime

st.set_page_config(page_title="Safe Tech Master Attendance", layout="wide")

DB_FILE = "attendance_db.csv"

# --- 1. FUNCTION: EXCEL LOGIC (As per your formula) ---
def get_attendance_status(emp_id, base_status, daily_entries, is_sunday):
    if base_status in ["R", "T", "ST"]: return base_status
    
    # ID search in "At Record" entries
    entry = next((str(e).upper() for e in daily_entries if str(emp_id) in str(e)), None)
    
    if entry:
        if "-D" in entry or " D" in entry or entry.endswith("D"): return "D6" if is_sunday else "DP"
        if "-N" in entry or " N" in entry or entry.endswith("N"): return "N6" if is_sunday else "NP"
        if "-A" in entry or " A" in entry or entry.strip() == str(emp_id):
            return "DA" if base_status == "D" else "NA"
    
    if is_sunday: return "WO"
    return "DP" if base_status == "D" else "NP"

# --- 2. SIDEBAR: ADD & UPLOAD ---
st.sidebar.title("🛠️ Admin Panel")

# Add New Worker (Wapas la diya hai)
with st.sidebar.expander("➕ Add New Worker", expanded=False):
    n_id = st.text_input("Worker ID")
    n_name = st.text_input("Full Name")
    n_desig = st.text_input("Designation")
    n_dept = st.text_input("Department")
    n_doj = st.date_input("Joining Date")
    n_base = st.selectbox("Base Status", ["D", "N"])
    if st.button("Save Worker"):
        if n_id and n_name:
            new_row = pd.DataFrame([{"Srl No": "New", "Emp ID": n_id, "Emp Name": n_name, "Designation": n_desig, "Department": n_dept, "Joining": n_doj, "Base": n_base}])
            if os.path.exists(DB_FILE):
                old_db = pd.read_csv(DB_FILE)
                pd.concat([old_db, new_row]).to_csv(DB_FILE, index=False)
            else:
                new_row.to_csv(DB_FILE, index=False)
            st.success("Worker Added!")

st.sidebar.divider()
uploaded_file = st.sidebar.file_uploader("Upload Master Excel", type=["xlsx"])

# --- 3. MAIN INTERFACE ---
st.markdown("<h1 style='text-align: center; color: white; background-color: #1E3A8A; padding: 10px; border-radius: 10px;'>SAFETECH PRECAST</h1>", unsafe_allow_html=True)

if uploaded_file:
    xls = pd.ExcelFile(uploaded_file)
    # Master Data Load
    df_master = pd.read_excel(uploaded_file, sheet_name=0, skiprows=12).dropna(subset=["Emp ID"])
    
    # At Record Load
    try:
        df_at = pd.read_excel(uploaded_file, sheet_name="At Record")
        st.sidebar.success("Sheet 'At Record' Found!")
    except:
        st.error("Error: 'At Record' sheet nahi mili!")
        df_at = None

    if df_at is not None:
        day = st.number_input("Select Day (1-31)", 1, 31)
        is_sun = st.checkbox("Is Sunday?")
        
        if st.button("🚀 Run Attendance Logic"):
            # Get data from At Record column (Adjusted for your file layout)
            daily_entries = df_at.iloc[:, day + 5].dropna().astype(str).tolist()
            
            # Apply your formula logic
            df_master[f"Day {day}"] = df_master.apply(lambda x: get_attendance_status(x["Emp ID"], x.get("Base", "D"), daily_entries, is_sun), axis=1)
            st.session_state.final_df = df_master
            st.success("Logic Applied!")

    if 'final_df' in st.session_state:
        st.dataframe(st.session_state.final_df, use_container_width=True)
    else:
        st.dataframe(df_master, use_container_width=True)

else:
    st.info("Bhai, sidebar se Excel upload karein. Sab system set hai!")
