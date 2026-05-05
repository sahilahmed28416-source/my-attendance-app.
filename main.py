import streamlit as st
import pandas as pd
from openpyxl import load_workbook
import io

st.set_page_config(page_title="SafeTech Master App", layout="wide")

st.markdown("<h1 style='text-align:center; background-color:#1E3A8A; color:white; padding:10px; border-radius:10px;'>SAFETECH ATTENDANCE & HR SYSTEM</h1>", unsafe_allow_html=True)

uploaded_file = st.file_uploader("Apni Master Excel File Upload Karein", type=["xlsx"])

if uploaded_file:
    # File ko memory mein load karna
    file_bytes = uploaded_file.read()
    
    # 1. SIDEBAR: NEW WORKER ADD KARNA
    st.sidebar.header("➕ Add New Worker")
    with st.sidebar.form("worker_form"):
        new_id = st.text_input("Worker ID (e.g. T00800)")
        new_name = st.text_input("Full Name")
        new_dept = st.text_input("Department")
        new_desig = st.text_input("Designation")
        submit_worker = st.form_submit_button("Add to All Sheets")

    if submit_worker:
        wb = load_workbook(io.BytesIO(file_bytes))
        # Har month ki sheet mein naya worker add karna
        for sheet_name in wb.sheetnames:
            ws = wb[sheet_name]
            # Pehli khali row dhoondna (Emp ID column mein)
            last_row = ws.max_row + 1
            ws.cell(row=last_row, column=2).value = new_id  # Column B: Emp ID
            ws.cell(row=last_row, column=3).value = new_name # Column C: Name
            ws.cell(row=last_row, column=4).value = new_desig # Column D: Desig
            ws.cell(row=last_row, column=5).value = new_dept # Column E: Dept
        
        # Save updated workbook back to memory
        out = io.BytesIO()
        wb.save(out)
        file_bytes = out.getvalue()
        st.sidebar.success(f"Worker {new_id} saari sheets mein add ho gaya!")

    # 2. MAIN AREA: ATTENDANCE ENTRY (AT RECORD LOGIC)
    wb_view = load_workbook(io.BytesIO(file_bytes))
    months = [m for m in wb_view.sheetnames if m != "At Record"]
    selected_month = st.selectbox("📅 Select Month", months)
    
    st.subheader(f"📍 {selected_month} Attendance Entry")
    col1, col2 = st.columns(2)
    with col1:
        ids_pasted = st.text_area("IDs Paste Karein (e.g. T00747, T00222)", height=150)
    with col2:
        target_day = st.number_input("Day (1-31)", 1, 31)
        status_to_apply = st.selectbox("Status", ["DP", "NP", "DA", "NA", "L", "T", "ST", "WO"])

    if st.button("🚀 Update Register"):
        wb = load_workbook(io.BytesIO(file_bytes))
        ws = wb[selected_month]
        input_list = [i.strip().upper() for i in ids_pasted.replace(',', ' ').split()]
        
        # Column dhoondna (Jan/Feb sheets mein dates Column G se shuru hoti hain)
        # 1st date Column G (index 7) par hai, toh Day 1 = Col 7, Day 2 = Col 8...
        target_col = 6 + target_day 
        
        count = 0
        for row in range(14, ws.max_row + 1): # Row 14 se data shuru hai
            emp_id_cell = ws.cell(row=row, column=2).value # Column B is Emp ID
            if str(emp_id_cell).strip().upper() in input_list:
                ws.cell(row=row, column=target_col).value = status_to_apply
                count += 1
        
        out = io.BytesIO()
        wb.save(out)
        file_bytes = out.getvalue()
        st.success(f"Done! {count} workers ki attendance update ho gayi.")

    # 3. DOWNLOAD UPDATED FILE
    st.download_button(
        label="📥 Download Updated Master Excel",
        data=file_bytes,
        file_name="SafeTech_Master_Attendance.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

else:
    st.info("Bhai, apni original 12-month wali Excel file upload karein.")
