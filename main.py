import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="SafeTech Attendance Pro", layout="wide")

# --- UI Styling ---
st.markdown("""
    <style>
    .main-header {text-align: center; color: white; background-color: #003366; padding: 20px; border-radius: 15px; margin-bottom: 20px;}
    .stButton>button {width: 100%; background-color: #003366; color: white; border-radius: 10px; height: 3em;}
    </style>
    <h1 class='main-header'>SAFETECH PRECAST - ATTENDANCE SYSTEM</h1>
    """, unsafe_allow_html=True)

# --- App Logic ---
uploaded_file = st.file_uploader("Upload your Master Excel File", type=["xlsx"])

if uploaded_file:
    # 1. Load the Excel
    xls = pd.ExcelFile(uploaded_file)
    months = xls.sheet_names
    selected_month = st.sidebar.selectbox("📅 Select Month", [m for m in months if m != "At Record"])
    
    # 2. Read Data (Skip summary rows to reach headers at Row 13)
    # Note: Excel indexing starts at 0, Row 13 in Excel is index 12
    df = pd.read_excel(uploaded_file, sheet_name=selected_month, skiprows=12)
    
    # Clean column names
    df.columns = [str(c).strip() for c in df.columns]
    df = df.dropna(subset=["Emp ID"]) # Faltu rows hatane ke liye

    # --- Sidebar Controls ---
    st.sidebar.subheader("📍 Attendance Input")
    target_date = st.sidebar.selectbox("Target Date", [str(i) for i in range(1, 32)])
    status_type = st.sidebar.radio("Attendance Status", ["DP (Day Present)", "NP (Night Present)", "DA (Day Absent)", "NA (Night Absent)", "L (Leave)", "ST", "T"])
    
    id_input = st.sidebar.text_area("Paste Employee IDs (Space or Comma separated)")

    if st.sidebar.button("Update Attendance"):
        # Process IDs
        input_ids = [id.strip().upper() for id in id_input.replace(',', ' ').split()]
        
        if target_date in df.columns:
            # Update matching IDs
            mask = df['Emp ID'].astype(str).str.upper().isin(input_ids)
            df.loc[mask, target_date] = status_type.split(' ')[0]
            st.success(f"Success! Updated {mask.sum()} workers for Date {target_date}")
        else:
            st.error(f"Date '{target_date}' column not found in this sheet!")

    # --- Dashboard Summary ---
    st.subheader(f"📊 Live Preview: {selected_month} 2026")
    
    # Simple Metrics
    col1, col2, col3, col4 = st.columns(4)
    if target_date in df.columns:
        col1.metric("Total Workers", len(df))
        col2.metric(f"Present (D/N) on {target_date}", df[target_date].isin(['DP', 'NP']).sum())
        col3.metric(f"Absent (DA/NA) on {target_date}", df[target_date].isin(['DA', 'NA']).sum())
        col4.metric("On Leave", df[target_date].isin(['L']).sum())

    # --- Interactive Table ---
    st.dataframe(df, use_container_width=True, hide_index=True)

    # --- Export ---
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name=selected_month)
    
    st.download_button(
        label="📥 Download Updated Excel",
        data=buffer.getvalue(),
        file_name=f"Updated_Attendance_{selected_month}.xlsx",
        mime="application/vnd.ms-excel"
    )

else:
    st.warning("Bhai, pehle apni Excel file upload karo.")
