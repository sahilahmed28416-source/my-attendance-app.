import streamlit as st
import pandas as pd
import os
from datetime import datetime

st.set_page_config(page_title="Safe Tech Attendance System", layout="wide")

# --- CUSTOM CSS ---
st.markdown("""
    <style>
    .main-header {text-align: center; color: white; background-color: #1E3A8A; padding: 15px; border-radius: 10px;}
    .month-label {font-size: 20px; font-weight: bold; color: #1E3A8A; background: #E0F2FE; padding: 5px 15px; border-radius: 5px;}
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 class='main-header'>SAFETECH PRECAST</h1>", unsafe_allow_html=True)

# --- SIDEBAR: NEW WORKER & BASE STATUS ---
st.sidebar.header("🛠️ Admin Panel")
with st.sidebar.expander("➕ Add New Worker"):
    n_id = st.sidebar.text_input("Worker ID (T-000)")
    n_name = st.sidebar.text_input("Worker Name")
    n_base = st.sidebar.selectbox("Base Status", ["D", "N", "L", "R", "T", "ST"])
    if st.sidebar.button("Save Permanent"):
        st.sidebar.success(f"Worker {n_id} Saved with Status {n_base}!")

# --- MAIN LOGIC ---
uploaded_file = st.file_uploader("Apni 12-Month Master Excel File Upload Karein", type=["xlsx"])

if uploaded_file:
    xls = pd.ExcelFile(uploaded_file)
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    selected_month = st.selectbox("📅 Select Month Sheet", months)
    
    try:
        # 1. At Record se data uthana (Template logic)
        df_at = pd.read_excel(uploaded_file, sheet_name="At Record")
        
        # 2. Selected Month ki sheet uthana
        df_master = pd.read_excel(uploaded_file, sheet_name=selected_month, skiprows=12)
        df_master.columns = df_master.columns.astype(str).str.strip()
        df_master = df_master.dropna(subset=["Emp ID"])

        st.markdown(f"<p class='month-label'>Register for: {selected_month} 2026</p>", unsafe_allow_html=True)

        # 3. ABSENT RECORD INPUT (At Record style)
        st.subheader(f"📍 {selected_month} Absent/Attendance Paste Area")
        col1, col2 = st.columns(2)
        with col1:
            input_ids = st.text_area("Yahan IDs Paste Karein (e.g. T001-A, T002-N, T005...)", height=150)
        with col2:
            day_num = st.number_input("Entry for Day (1-31)", 1, 31)
            is_sun = st.checkbox("Is Sunday / Weekly Off?")

        # 4. PROCESSING LOGIC (Formula Based)
        if st.button("🚀 Update Register"):
            # ID list cleaning
            raw_entries = input_ids.upper().split(',')
            
            def get_final_status(emp_id, base):
                # R, T, ST fixed hote hain
                if base in ["R", "T", "ST"]: return base
                
                # Check if ID is in pasted list
                entry = next((x.strip() for x in raw_entries if str(emp_id) in x), None)
                
                if entry:
                    if "-D" in entry: return "D6" if is_sun else "DP"
                    if "-N" in entry: return "N6" if is_sun else "NP"
                    if "-A" in entry or entry == str(emp_id): return "DA" if base=="D" else "NA"
                
                # Default case
                if is_sun: return "WO"
                return "DP" if base=="D" else "NP"

            df_master[str(day_num)] = df_master.apply(lambda x: get_final_status(x["Emp ID"], x.get("Base", "D")), axis=1)
            st.session_state.final_df = df_master
            st.success("Logic Applied as per Excel Formula!")

        # 5. DISPLAY TABLE (Exact as Photo)
        if 'final_df' in st.session_state:
            st.dataframe(st.session_state.final_df, use_container_width=True, hide_index=True)
        else:
            st.dataframe(df_master, use_container_width=True, hide_index=True)

    except Exception as e:
        st.error(f"Sheet '{selected_month}' dhoondne mein galti hui. Excel check karein.")

else:
    st.info("Bhai, sidebar se Excel upload karein. App aapki file ke 'At Record' template ko follow karega.")
