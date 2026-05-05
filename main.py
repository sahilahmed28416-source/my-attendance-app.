import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Safe Tech Attendance Pro", layout="wide")

DB_FILE = "attendance_db.csv"

# --- 1. CORE LOGIC FUNCTION (Exactly as your Formula) ---
def calculate_status(emp_id, base_status, daily_entries, is_sunday):
    # R, T, ST are fixed
    if base_status in ["R", "T", "ST"]:
        return base_status
    
    # Check what is written in "At Record" for this ID
    # daily_entries is a list of strings from the column
    entry = next((e for e in daily_entries if str(emp_id) in str(e)), None)
    
    # Logic if ID is found in "At Record"
    if entry:
        entry = str(entry).upper()
        if "-D" in entry or " D" in entry:
            return "D6" if is_sunday else "DP"
        if "-N" in entry or " N" in entry:
            return "N6" if is_sunday else "NP"
        if "-A" in entry or " A" in entry or str(emp_id) == entry.strip():
            return "DA" if base_status == "D" else "NA"
    
    # Logic if ID NOT found (Default Presence)
    if is_sunday:
        return "WO"
    return "DP" if base_status == "D" else "NP"

# --- 2. INTERFACE ---
st.markdown("<h1 style='text-align: center; color: white; background-color: #1E3A8A; padding: 10px; border-radius: 10px;'>SAFETECH PRECAST</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #4B5563; font-size: 20px;'>SMART ATTENDANCE LOGIC SYSTEM</p>", unsafe_allow_html=True)

# Sidebar for Upload
st.sidebar.title("📤 Data Source")
uploaded_file = st.sidebar.file_uploader("Upload Master Excel", type=["xlsx"])

if uploaded_file:
    # Load Master Data (770 Workers)
    xls = pd.ExcelFile(uploaded_file)
    # Load Jan as example or first sheet
    df = pd.read_excel(uploaded_file, sheet_name=0, skiprows=12)
    df = df.dropna(subset=["Emp ID"])
    
    # Load "At Record" for attendance inputs
    try:
        at_record = pd.read_excel(uploaded_file, sheet_name="At Record")
    except:
        st.error("Error: 'At Record' sheet nahi mili!")
        at_record = None

    if at_record is not None:
        st.sidebar.success("Excel & At Record Loaded!")
        
        # Select Day to process
        day_to_process = st.selectbox("Select Day to View/Update (1-31)", range(1, 32))
        is_sun = st.checkbox("Is this Sunday?")

        if st.button("🚀 Apply Excel Logic"):
            # Get entries from "At Record" for the selected day's column
            # (Assuming columns match days)
            daily_entries = at_record.iloc[:, day_to_process + 5].dropna().tolist()
            
            results = []
            for _, row in df.iterrows():
                status = calculate_status(row["Emp ID"], row.get("Base", "D"), daily_entries, is_sun)
                results.append(status)
            
            df[str(day_to_process)] = results
            st.session_state.master_df = df
            st.success(f"Day {day_to_process} Processed with Pro Logic!")

    # Display Table
    if 'master_df' in st.session_state:
        st.dataframe(st.session_state.master_df, use_container_width=True)
    else:
        st.dataframe(df, use_container_width=True)

else:
    st.info("Bhai, please Excel file upload karein jisme 'At Record' aur 'Jan' dono sheets hon.")
