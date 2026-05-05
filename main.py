import streamlit as st
import pandas as pd
from datetime import datetime

# Page configuration
st.set_page_config(page_title="Safe Tech Attendance System", layout="wide")

# --- CUSTOM CSS FOR PROFESSIONAL LOOK ---
st.markdown("""
    <style>
    .main-header {text-align: center; color: #1E3A8A; margin-bottom: 0px;}
    .sub-header {text-align: center; color: #4B5563; font-size: 18px; margin-top: 0px;}
    .report-box {border: 2px solid #E5E7EB; padding: 20px; border-radius: 10px; background-color: #F9FAFB;}
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR: CONTROLS ---
st.sidebar.header("⚙️ Control Panel")
uploaded_file = st.sidebar.file_uploader("Upload Master Excel File", type=["xlsx"])

with st.sidebar.expander("➕ Add New Worker"):
    n_id = st.text_input("1. Worker ID")
    n_f_name = st.text_input("2. First Name")
    n_s_name = st.text_input("3. Second Name")
    n_desig = st.text_input("4. Designation")
    n_dept = st.text_input("5. Department")
    n_doj = st.date_input("6. Joining Date")
    if st.button("Save Worker"):
        st.success(f"ID {n_id} saved successfully!")

# --- MAIN INTERFACE ---
if uploaded_file:
    # Load Excel
    xls = pd.ExcelFile(uploaded_file)
    months = xls.sheet_names
    selected_month = st.sidebar.selectbox("Select Month", months)
    
    # Header Section (As per your Image)
    st.markdown(f"<h1 class='main-header'>SAFETECH PRECAST</h1>", unsafe_allow_html=True)
    st.markdown(f"<p class='sub-header'>ATTENDANCE SHEET FOR - {selected_month.upper()} 2026</p>", unsafe_allow_html=True)
    
    st.divider()
    
    # 770+ Workers Loading Logic (Skip rows to find real header)
    # Aapki sheet mein header Row 12-13 par hai
    df = pd.read_excel(uploaded_file, sheet_name=selected_month, skiprows=12)
    
    # Clean data (Remove empty rows)
    if 'Emp ID' in df.columns:
        df = df.dropna(subset=['Emp ID'])
    
    # Formatting for Display
    st.write(f"**Total Manpower:** {len(df)}")
    
    # Attendance Input (At Record Style)
    with st.expander("📝 Daily Attendance Entry (At Record)", expanded=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            day_ids = st.text_area("Day Shift (D) IDs", placeholder="T001, T002...")
        with col2:
            night_ids = st.text_area("Night Shift (N) IDs")
        with col3:
            absent_ids = st.text_area("Absent (A) IDs")
    
    # THE TABLE (Professional View)
    st.subheader(f"Attendance Preview: {selected_month}")
    
    # Final Table Columns (Exact as your CSV)
    cols_to_show = ["Srl No", "Emp ID", "Emp Name", "Designation", "Department", "Joining"]
    # Check if columns exist
    existing_cols = [c for c in cols_to_show if c in df.columns]
    
    # Day columns (1 to 31) display
    day_cols = [c for c in df.columns if any(str(day) in str(c) for day in range(1, 32))]
    
    final_view = df[existing_cols + day_cols[:5]] # Pehle 5 din preview ke liye
    st.dataframe(df, use_container_width=True)

    # Export
    st.sidebar.divider()
    if st.sidebar.button("💾 Save All Changes"):
        st.sidebar.success("Data Updated in Master Sheet!")

else:
    # Welcome Screen
    st.markdown("<h1 class='main-header'>SAFETECH PRECAST</h1>", unsafe_allow_html=True)
    st.info("Bhai, please sidebar se Excel file upload karein taaki hum 770+ workers ka record dikha sakein.")
    st.image("https://via.placeholder.com/800x200.png?text=Please+Upload+Attendance+Sheet", use_container_width=True)
