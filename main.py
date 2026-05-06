import streamlit as st
import pandas as pd
from openpyxl import load_workbook
import io

st.set_page_config(page_title="SafeTech Attendance Pro", layout="wide")

st.markdown("<h1 style='text-align:center; background-color:#1E3A8A; color:white; padding:10px; border-radius:10px;'>SAFETECH PRECAST - ATTENDANCE SYSTEM</h1>", unsafe_allow_html=True)

uploaded_file = st.file_uploader("Apni Master Excel File Upload Karein", type=["xlsx"])

if uploaded_file:
    file_bytes = uploaded_file.read()
    
    # --- 1. NEW WORKER ADD KARNA (All Columns Fix) ---
    st.sidebar.header("➕ Add New Worker")
    with st.sidebar.form("worker_form"):
        n_id = st.text_input("Emp ID (T00...)")
        n_fname = st.text_input("First Name")
        n_lname = st.text_input("Last Name")
        n_desig = st.text_input("Designation")
        n_dept = st.text_input("Department")
        n_join = st.date_input("Joining Date")
        submit_w = st.form_submit_button("Add Worker")

    if submit_w and n_id:
        wb = load_workbook(io.BytesIO(file_bytes))
        full_name = f"{n_fname} {n_lname}"
        for sheet in wb.sheetnames:
            if sheet != "At Record":
                ws = wb[sheet]
                # Last row dhoondne ka sahi tarika
                next_r = 14
                while ws.cell(row=next_r, column=2).value is not None:
                    next_r += 1
                
                ws.cell(row=next_r, column=1).value = next_r - 13 # Srl No
                ws.cell(row=next_r, column=2).value = n_id       # Emp ID
                ws.cell(row=next_r, column=3).value = full_name  # Name
                ws.cell(row=next_r, column=4).value = n_desig   # Desig
                ws.cell(row=next_r, column=5).value = n_dept    # Dept
                ws.cell(row=next_r, column=6).value = n_join    # Joining
        
        out = io.BytesIO()
        wb.save(out)
        file_bytes = out.getvalue()
        st.sidebar.success(f"Worker {n_id} added!")

    # --- 2. WORKER LIST DISPLAY (Fixing the Blank Screen) ---
    xls = pd.ExcelFile(io.BytesIO(file_bytes))
    months = [m for m in xls.sheet_names if m != "At Record"]
    sel_month = st.selectbox("📅 Select Month", months)
    
    # Header Row 13 (skiprows=12)
    df = pd.read_excel(io.BytesIO(file_bytes), sheet_name=sel_month, skiprows=12)
    
    # Column names clean karna taaki matching sahi ho
    df.columns = [str(c).strip() for c in df.columns]
    
    # Sirf wahi data dikhana jahan Emp ID column B (index 1) mein ho
    df_display = df[df['Emp ID'].notna()]

    st.subheader(f"📋 Worker List - {sel_month}")
    st.dataframe(df_display, use_container_width=True, hide_index=True)

    # --- 3. BULK ATTENDANCE (Excel logic) ---
    st.divider()
    st.subheader("🚀 Bulk Update Attendance")
    col1, col2, col3 = st.columns([2,1,1])
    with col1:
        paste_area = st.text_area("Paste IDs here")
    with col2:
        day_num = st.number_input("Day", 1, 31)
    with col3:
        status_val = st.selectbox("Status", ["DP", "NP", "DA", "NA", "L", "T", "ST", "WO"])

    if st.button("Apply to Register"):
        wb = load_workbook(io.BytesIO(file_bytes))
        ws = wb[sel_month]
        id_list = [i.strip().upper() for i in paste_area.replace(',', ' ').split()]
        
        # Column G is Day 1
        t_col = 6 + day_num
        
        for r in range(14, ws.max_row + 1):
            eid = str(ws.cell(row=r, column=2).value).strip().upper()
            if eid in id_list:
                ws.cell(row=r, column=t_col).value = status_val
        
        out = io.BytesIO()
        wb.save(out)
        file_bytes = out.getvalue()
        st.success("Attendance Updated!")
        st.rerun()

    st.download_button("📥 Download Updated Excel", file_bytes, "SafeTech_Attendance.xlsx")
else:
    st.info("Bhai, Master Excel file upload karo.")
