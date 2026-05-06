import streamlit as st
import pandas as pd
from openpyxl import load_workbook
import io
from datetime import datetime

st.set_page_config(page_title="SafeTech Master Pro", layout="wide")

st.markdown("<h1 style='text-align:center; background-color:#003366; color:white; padding:10px; border-radius:10px;'>SAFETECH PRECAST - OFFICIAL SYSTEM</h1>", unsafe_allow_html=True)

uploaded_file = st.file_uploader("Apni Original SafeTech Excel Upload Karein", type=["xlsx"])

if uploaded_file:
    file_bytes = uploaded_file.read()
    
    # --- 1. NEW WORKER SECTION (Exact Column Mapping B to F) ---
    st.sidebar.header("➕ Add New Worker")
    with st.sidebar.form("worker_form"):
        n_id = st.text_input("Emp ID (B Column)")
        n_fname = st.text_input("First Name")
        n_lname = st.text_input("Last Name")
        n_desig = st.text_input("Designation (D Column)")
        n_dept = st.text_input("Department (E Column)")
        n_join = st.date_input("Joining Date (F Column)", datetime.now())
        submit_w = st.form_submit_button("Add to All Months")

    if submit_w and n_id:
        wb = load_workbook(io.BytesIO(file_bytes))
        full_name = f"{n_fname} {n_lname}".strip()
        for sheet in wb.sheetnames:
            if sheet != "At Record":
                ws = wb[sheet]
                # Sahi row dhoondna (Row 14 ke baad pehli khali jagah)
                r = 14
                while ws.cell(row=r, column=2).value is not None:
                    r += 1
                
                ws.cell(row=r, column=1).value = r - 13      # A: Srl No
                ws.cell(row=r, column=2).value = n_id        # B: Emp ID
                ws.cell(row=r, column=3).value = full_name   # C: Emp Name
                ws.cell(row=r, column=4).value = n_desig     # D: Designation
                ws.cell(row=r, column=5).value = n_dept      # E: Department
                ws.cell(row=r, column=6).value = n_join      # F: Joining
        
        out = io.BytesIO()
        wb.save(out)
        file_bytes = out.getvalue()
        st.sidebar.success(f"Worker {n_id} added perfectly!")

    # --- 2. WORKER LIST DISPLAY (Using Row 13 Headers) ---
    xls = pd.ExcelFile(io.BytesIO(file_bytes))
    months = [m for m in xls.sheet_names if m != "At Record"]
    sel_month = st.selectbox("📅 Select Month", months)
    
    # Row 13 in Excel is index 12 for pandas
    df = pd.read_excel(io.BytesIO(file_bytes), sheet_name=sel_month, skiprows=12)
    
    # Filter: Sirf wahi rows jahan Column B (Emp ID) khali nahi hai
    if 'Emp ID' in df.columns:
        df_display = df[df['Emp ID'].notna()]
        st.subheader(f"📋 Worker List - {sel_month}")
        st.dataframe(df_display, use_container_width=True, hide_index=True)
    else:
        st.error("Sheet structure match nahi kar raha. Header Row 13 check karein.")

    # --- 3. BULK ATTENDANCE (Column G onwards) ---
    st.divider()
    st.subheader("🚀 Bulk Attendance Update")
    c1, c2, c3 = st.columns([2, 1, 1])
    with c1:
        pasted_ids = st.text_area("IDs Paste Karein (T00...)")
    with c2:
        day_input = st.number_input("Enter Day (1-31)", 1, 31)
    with c3:
        status_choice = st.selectbox("Status", ["DP", "NP", "DA", "NA", "L", "T", "ST", "WO"])

    if st.button("Apply Attendance"):
        wb = load_workbook(io.BytesIO(file_bytes))
        ws = wb[sel_month]
        id_list = [i.strip().upper() for i in pasted_ids.replace(',', ' ').split()]
        
        # Date 1 Column G (7) par hai, isliye Day + 6
        target_col = 6 + day_input
        
        updated_count = 0
        for r in range(14, ws.max_row + 1):
            eid_in_cell = str(ws.cell(row=r, column=2).value).strip().upper()
            if eid_in_cell in id_list:
                ws.cell(row=r, column=target_col).value = status_choice
                updated_count += 1
        
        out = io.BytesIO()
        wb.save(out)
        file_bytes = out.getvalue()
        st.success(f"Success: {updated_count} workers updated for Day {day_input}!")
        st.rerun()

    # --- 4. DOWNLOAD ---
    st.download_button("📥 Download Final Excel", file_bytes, "SafeTech_Updated_Attendance.xlsx")

else:
    st.info("Bhai, apni original Master Excel file upload karein.")
