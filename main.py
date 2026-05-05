import streamlit as st
import pandas as pd
import os
from datetime import datetime

# Page Configuration
st.set_page_config(page_title="Safe Tech Attendance System", layout="wide")

# Database setup
DB_FILE = "safetech_workers.csv"

def load_data():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE, dtype={"Emp ID": str})
    return pd.DataFrame(columns=["Srl No", "Emp ID", "Emp Name", "Designation", "Department", "Joining", "Base"])

# --- ATTENDANCE LOGIC (Your Professional Formula) ---
def calculate_attendance(emp_id, base, at_record_entries, is_sunday):
    if base in ["R", "T", "ST"]: return base
    
    # ID search in 'At Record'
    id_str = str(emp_id).strip().upper()
    match = next((str(e).upper() for e in at_record_entries if id_str in str(e).upper()), None)
    
    if match:
        if any(suffix in match for suffix in ["-D", " D", "D"]): return "D6" if is_sunday else "DP"
        if any(suffix in match for suffix in ["-N", " N", "N"]): return "N6" if is_sunday else "NP"
        if any(suffix in match for suffix in ["-A", " A", "A"]) or match == id_str:
            return "DA" if base == "D" else "NA"
            
    if is_sunday: return "WO"
    return "DP" if base == "D" else "NP"

# --- SIDEBAR: ADMIN & ADD WORKER ---
st.sidebar.markdown("<h2 style='color: #1E3A8A;'>🛠️ Admin Panel</h2>", unsafe_allow_html=True)

with st.sidebar.expander("➕ Add New Worker", expanded=False):
    f_name = st.text_input("First Name")
    s_name = st.text_input("Second Name")
    w_id = st.text_input("Worker ID No")
    w_desig = st.text_input("Designation")
    w_dept = st.text_input("Department")
    w_doj = st.date_input("Joining Date", datetime.now())
    w_base = st.selectbox("Base Status", ["D", "N", "R", "T", "ST"])
    
    if st.button("Save Permanent"):
        if w_id and f_name:
            current_db = load_data()
            new_worker = pd.DataFrame([[len(current_db)+1, w_id, f"{f_name} {s_name}", w_desig, w_dept, w_doj, w_base]], 
                                     columns=["Srl No", "Emp ID", "Emp Name", "Designation", "Department", "Joining", "Base"])
            pd.concat([current_db, new_worker]).to_csv(DB_FILE, index=False)
            st.success("Worker Added!")
            st.rerun()

st.sidebar.divider()
uploaded_file = st.sidebar.file_uploader("Upload Master Excel", type=["xlsx"])

# --- MAIN INTERFACE (Exact as your Photo) ---
st.markdown("<h1 style='text-align: center; color: white; background-color: #1E3A8A; padding: 10px; border-radius: 10px;'>SAFETECH PRECAST</h1>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align: center; font-size: 20px; font-weight: bold;'>MONTHLY ATTENDANCE REGISTER - 2026</p>", unsafe_allow_html=True)

if uploaded_file:
    try:
        xls = pd.ExcelFile(uploaded_file)
        month_list = xls.sheet_names
        selected_month = st.selectbox("Select Month Sheet", [m for m in month_list if m != 'At Record'])
        
        # Load Data
        df_master = pd.read_excel(uploaded_file, sheet_name=selected_month, skiprows=12)
        df_master.columns = df_master.columns.astype(str).str.strip()
        df_master = df_master.dropna(subset=["Emp ID"])
        
        df_at = pd.read_excel(uploaded_file, sheet_name="At Record")
        df_at.columns = df_at.columns.astype(str).str.strip()

        col1, col2 = st.columns(2)
        day_val = col1.number_input("Select Day (1-31)", 1, 31)
        is_sun = col2.checkbox("Is Today Sunday?")

        if st.button("🚀 Run Company Logic"):
            # Get IDs from 'At Record' for that day
            daily_data = df_at.iloc[:, day_val + 4].dropna().astype(str).tolist()
            
            df_master[str(day_val)] = df_master.apply(
                lambda r: calculate_attendance(r.get("Emp ID", ""), r.get("Base", "D"), daily_data, is_sun), axis=1
            )
            st.session_state.processed = df_master
            st.success("Attendance Updated!")

        # Show Results
        display_df = st.session_state.processed if 'processed' in st.session_state else df_master
        st.write(f"Showing Records for: **{selected_month}** | Total Workers: **{len(display_df)}**")
        st.dataframe(display_df, use_container_width=True, hide_index=True)

    except Exception as e:
        st.error(f"Excel Load Error: {e}. Make sure sheets 'At Record' and '{selected_month}' are correct.")

else:
    # Initial View with Saved Workers
    db = load_data()
    if not db.empty:
        st.write("### Current Worker Database")
        st.dataframe(db, use_container_width=True)
    else:
        st.info("Bhai, sidebar se Excel upload karke 'At Record' logic start karein ya naya worker add karein.")
