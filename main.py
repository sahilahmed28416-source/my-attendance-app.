import streamlit as st
import pandas as pd
from openpyxl import load_workbook
import io

st.set_page_config(page_title="SafeTech Attendance Pro", layout="wide")

st.markdown("<h1 style='text-align:center; background-color:#1E3A8A; color:white; padding:10px; border-radius:10px;'>SAFETECH ATTENDANCE SYSTEM</h1>", unsafe_allow_html=True)

uploaded_file = st.file_uploader("Apni Master Excel File Upload Karein", type=["xlsx"])

if uploaded_file:
    file_bytes = uploaded_file.read()
    
    # 1. SIDEBAR: NEW WORKER ADD KARNA
    st.sidebar.header("➕ Add New Worker")
    with st.sidebar.form("worker_form"):
        new_id = st.text_input("Worker ID (e.g. T00800)")
        new_name = st.text_input("Full Name")
        new_dept = st.text_input("Department")
        new_desig = st.text_input("Designation")
        submit_worker = st.form_submit_button("Add Worker to File")

    if submit_worker and new_id:
        wb = load_workbook(io.BytesIO(file_bytes))
        for sheet_name in wb.sheetnames:
            if sheet_name != "At Record":
                ws = wb[sheet_name]
                last_row = ws.max_row + 1
                ws.cell(row=last_row, column=1).value = last_row - 13 # Srl No
                ws.cell(row=last_row, column=2).value = new_id
                ws.cell(row=last_row, column=3).value = new_name
                ws.cell(row=last_row, column=4).value = new_desig
                ws.cell(row=last_row, column=5).value = new_dept
        
        out = io.BytesIO()
        wb.save(out)
        file_bytes = out.getvalue()
        st.sidebar.success(f"Worker {new_id} added successfully!")

    # 2
