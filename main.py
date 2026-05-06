import streamlit as st
import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import PatternFill
import io
from datetime import datetime

# --- CONFIG & UI ---
st.set_page_config(page_title="SafeTech Ultimate System", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #f4f7f6; }
    .main-header { text-align:center; background-color:#1E3A8A; color:white; padding:20px; border-radius:15px; margin-bottom:20px; }
    .stButton>button { width: 100%; border-radius: 8px; background-color: #1E3A8A; color: white; font-weight: bold; }
    .sidebar-box { background-color: #ffffff; padding: 15px; border-radius: 10px; border: 1px solid #ddd; }
    </style>
    """, unsafe_allow_html=True)

# Logo
try:
    st.sidebar.image("3810b91a7e82de2cb2273cb3494b93cbc0589111", width=160)
except:
    st.sidebar.markdown("### 🏗️ SAFETECH PRECAST")

st.markdown("<div class='main-header'><h1>SAFETECH WORKFORCE PRO SYSTEM v4.0</h1></div>", unsafe_allow_html=True)

uploaded_file = st.file_uploader("📂 Upload Karein SafeTech Master Attendance File (.xlsx)", type=["xlsx"])

if uploaded_file:
    file_bytes = uploaded_file.read()
    
    # --- 1. NEW WORKER SECTION (AB EKDOM PERFECT) ---
    st.sidebar.header("👤 Employee Management")
    with st.sidebar.expander("➕ Register New Worker", expanded=True):
        with st.form("worker_reg"):
            n_id = st.text_input("Emp ID (e.g. T00770)")
            n_name = st.text_input("Full Name")
            n_des = st.text_input("Designation")
            n_dep = st.text_input("Department")
            n_shift = st.selectbox("Base Status (Shift)", ["Day Shift (D)", "Night Shift (N)"])
            n_date = st.date_input("Joining Date", datetime.now())
            sub_w = st.form_submit_button("Save to Database")

    if sub_w and n_id:
        wb = load_workbook(io.BytesIO(file_bytes))
        shift_val = "D" if "Day" in n_shift else "N"
        for sheet in wb.sheetnames:
            if sheet != "At Record":
                ws = wb[sheet]
                r = 15 # Row 15 se data start
                while ws.cell(row=r, column=2).value is not None:
                    r += 1
                ws.cell(row=r, column=1).value = r - 14
                ws.cell(row=r, column=2).value = n_id.strip().upper()
                ws.cell(row=r, column=3).value = n_name.strip()
                ws.cell(row=r, column=4).value = n_des.strip()
                ws.cell(row=r, column=5).value = n_dep.strip()
                ws.cell(row=r, column=6).value = n_date
                ws.cell(row=r, column=38).value = shift_val # Column AL for Base Status
        
        out = io.BytesIO()
        wb.save(out)
        file_bytes = out.getvalue()
        st.sidebar.success(f"Worker {n_id} Added in All Months!")

    # --- 2. DYNAMIC DATA LOADING (KEYERROR FIX) ---
    xls = pd.ExcelFile(io.BytesIO(file_bytes))
    months = [m for m in xls.sheet_names if m != "At Record"]
    sel_month = st.selectbox("📅 Select Attendance Month", months)

    # Smart Loading: Row 13 ko detect karke columns clean karega
    df_raw = pd.read_excel(io.BytesIO(file_bytes), sheet_name=sel_month, skiprows=12)
    df_raw.columns = [str(c).strip() for c in df_raw.columns] # Sabhi spaces khatam!

    # ID Column dhoondne ka tarika (Flexible)
    id_col = next((c for c in df_raw.columns if "ID" in c.upper()), None)

    if id_col:
        df_active = df_raw[df_raw[id_col].notna()].copy()
        st.subheader(f"📋 Register: {sel_month}")
        st.dataframe(df_active, use_container_width=True, hide_index=True)

        # --- 3. BULK ATTENDANCE (MONTH & DATE WISE) ---
        st.divider()
        st.header(f"⚡ Attendance Panel - {sel_month}")
        
        c1, c2, c3 = st.columns([2, 1, 1])
        with c1:
            ids_area = st.text_area("Paste IDs (Separated by space or enter)", height=150)
        with c2:
            target_dt = st.number_input("Enter Date (1-31)", 1, 31)
            shift_mode = st.radio("Work Mode", ["Day (DP/DA)", "Night (NP/NA)"])
        with c3:
            s_list = ["DP", "DA", "L", "T", "WO", "ST"] if "Day" in shift_mode else ["NP", "NA", "L", "T", "WO", "ST"]
            final_status = st.selectbox("Select Attendance Status", s_list)

        if st.button("🚀 Apply Bulk Update"):
            if ids_area:
                wb = load_workbook(io.BytesIO(file_bytes))
                ws = wb[sel_month]
                list_of_ids = [i.strip().upper() for i in ids_area.replace(',', ' ').split()]
                target_col = 6 + target_dt # Column G is Day 1
                
                updated_count = 0
                for r in range(15, ws.max_row + 1):
                    val = str(ws.cell(row=r, column=2).value).strip().upper()
                    if val in list_of_ids:
                        ws.cell(row=r, column=target_col).value = final_status
                        ws.cell(row=r, column=target_col).fill = PatternFill(start_color="B7E1CD", fill_type="solid")
                        updated_count += 1
                
                out = io.BytesIO()
                wb.save(out)
                file_bytes = out.getvalue()
                st.success(f"Success! {updated_count} workers updated for Date {target_dt}")
                st.rerun()

        # --- 4. DOWNLOAD ---
        st.divider()
        st.download_button("📥 DOWNLOAD FINAL SAFETECH EXCEL", file_bytes, f"SafeTech_Updated_{sel_month}.xlsx")
    else:
        st.error("Bhai, sheet mein 'Emp ID' column nahi mil raha. Please check karein ki Row 13 mein headers hain ya nahi.")

else:
    st.info("Bhai, pehle apni Master Excel file upload karein.")
