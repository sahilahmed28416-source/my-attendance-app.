import streamlit as st
import pandas as pd
import os
from datetime import datetime

st.set_page_config(page_title="Safe Tech Attendance Pro", layout="wide")

# Database file for saving new workers
DB_FILE = "worker_database.csv"

# --- 1. ATTENDANCE LOGIC (Exactly as your Excel Formula) ---
def get_status(emp_id, base_status, daily_entries, is_sunday):
    if base_status in ["R", "T", "ST"]: return base_status
    
    # Cleaning the ID for search
    emp_id_str = str(emp_id).strip().upper()
    entry = next((str(e).upper() for e in daily_entries if emp_id_str in str(e).upper()), None)
    
    if entry:
        if any(x in entry for x in ["-D", " D", "D"]): return "D6" if is_sunday else "DP"
        if any(x in entry for x in ["-N", " N", "N"]): return "N6" if is_sunday else "NP"
        if any(x in entry for x in ["-A", " A", "A"]) or entry == emp_id_str:
            return "DA" if base_status == "D" else "NA"
            
    if is_sunday: return "WO"
    return "DP" if base_status == "D" else "NP"

# --- 2. SIDEBAR: ADD WORKER & UPLOAD ---
st.sidebar.markdown("### 🛠️ ADMIN PANEL")

# Add New Worker System
with st.sidebar.expander("➕ Add New Worker", expanded=False):
    f_name = st.text_input("First Name")
    s_name = st.text_input("Second Name")
    w_id = st.text_input("Worker ID")
    w_desig = st.text_input("Designation")
    w_dept = st.text_input("Department")
    w_doj = st.date_input("Joining Date", datetime.now())
    w_base = st.selectbox("Base Status", ["D", "N", "R", "T", "ST"])
    
    if st.button("Save Worker"):
        if w_id and f_name:
            new_data = pd.DataFrame([[w_id, f"{f_name} {s_name}", w_desig, w_dept, w_doj, w_base]], 
                                    columns=["Emp ID", "Emp Name", "Designation", "Department", "Joining", "Base"])
            if os.path.exists(DB_FILE):
                new_data.to_csv(DB_FILE, mode='a', header=False, index=False)
            else:
                new_data.to_csv(DB_FILE, index=False)
            st.success("Worker Added Permanently!")
        else:
            st.error("ID and Name are required!")

st.sidebar.divider()
uploaded_file = st.sidebar.file_uploader("Upload Master Excel", type=["xlsx"])

# --- 3. MAIN DASHBOARD ---
st.markdown("<h1 style='text-align: center; color: white; background-color: #1E3A8A; padding: 10px; border-radius: 10px;'>SAFETECH PRECAST</h1>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align: center; font-size: 18px;'>Attendance Register - {datetime.now().strftime('%B %Y')}</p>", unsafe_allow_html=True)

if uploaded_file:
    try:
        # Step A: Load Master Sheet (Jan) - Skipping first 12 rows as per your file
        df_master = pd.read_excel(uploaded_file, sheet_name=0, skiprows=12)
        # Cleaning column names to avoid "KeyError"
        df_master.columns = df_master.columns.astype(str).str.strip()
        
        # Step B: Load Attendance Entries (At Record)
        df_at = pd.read_excel(uploaded_file, sheet_name="At Record")
        df_at.columns = df_at.columns.astype(str).str.strip()

        # Day Selection
        selected_day = st.number_input("Select Day (1-31)", 1, 31, value=1)
        is_sunday = st.checkbox("Is Today Sunday / Weekly Off?")

        if st.button("🚀 Process Attendance"):
            # Get IDs from 'At Record' for the specific day column
            # (Adjusting column index based on your sheet layout)
            daily_entries = df_at.iloc[:, selected_day + 4].dropna().astype(str).tolist()
            
            # Apply the Formula Logic
            df_master[f"Day {selected_day}"] = df_master.apply(
                lambda row: get_status(row.get("Emp ID", ""), row.get("Base", "D"), daily_entries, is_sunday), axis=1
            )
            st.session_state.processed_df = df_master
            st.success(f"Day {selected_day} logic applied successfully!")

        # Show Table
        if 'processed_df' in st.session_state:
            st.dataframe(st.session_state.processed_df, use_container_width=True)
        else:
            st.dataframe(df_master.head(770), use_container_width=True)

    except Exception as e:
        st.error(f"Error Loading File: {e}. Please check if 'At Record' sheet exists.")
else:
    st.info("Bhai, sidebar se Excel upload karo. Add Worker system side mein hai!")
