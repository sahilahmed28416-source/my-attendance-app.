import streamlit as st
import pandas as pd
from openpyxl import load_workbook
import io

st.set_page_config(page_title="SafeTech Attendance System", layout="wide")

# Custom Styling
st.markdown("""
    <style>
    .main-title {text-align:center; background-color:#003366; color:white; padding:15px; border-radius:10px;}
    .stDataFrame {border: 2px solid #003366; border-radius: 10px;}
    </style>
    <h1 class='main-title'>SAFETECH PRECAST - MASTER APP</h1>
    """, unsafe_allow_html=True)

uploaded_file = st.file_uploader("Upload your Master Excel File", type=["xlsx"])

if uploaded_file:
    # File ko read karna
    file_bytes = uploaded_file.read()
    
    # --- 1. NEW WORKER ADD KARNE KA LOGIC ---
    st.sidebar.header("➕ Add New Worker")
    with st.sidebar.form("add_worker"):
        id_w = st.text_input("Emp ID")
        name_w = st.text_input("Name")
        desig_w = st.text_input("Designation")
        dept_w = st.text_input("Department")
        submit = st.form_submit_button("Add to All 12 Months")
    
    if submit and id_w:
        wb = load_workbook(io.BytesIO(file_bytes))
        for sheet in wb.sheetnames:
            if sheet != "At Record":
                ws = wb[sheet]
                # Last row dhoondna jahan data khatam ho raha hai
                new_row = ws.max_row + 1
                ws.cell(row=new_row, column=1).value = new_row - 13 # Srl No
                ws.cell(row=new_row, column=2).value = id_w
                ws.cell(row=new_row, column=3).value = name_w
                ws.cell(row=new_row, column=4).value = desig_w
                ws.cell(row=new_row, column=5).value = dept_w
        
        output = io.BytesIO()
        wb.save(output)
        file_bytes = output.getvalue()
        st.sidebar.success(f"Worker {id_w} added to all sheets!")

    # --- 2. DISPLAY WORKER LIST (Row 13 Headers) ---
    xls = pd.ExcelFile(io.BytesIO(file_bytes))
    months = [m for m in xls.sheet_names if m != "At Record"]
    sel_month = st.selectbox("📅 Select Month to View", months)
    
    # Aapki file mein Row 13 header hai, isliye skiprows=12
    df = pd.read_excel(io.BytesIO(file_bytes), sheet_name=sel_month, skiprows=12)
    df = df.dropna(subset=['Emp ID']) # Sirf kaam ka data dikhane ke liye

    st.subheader(f"📋 Worker List - {sel_month}")
    st.dataframe(df, use_container_width=True, hide_index=True)

    # --- 3. ATTENDANCE ENTRY (Bina Excel chhede) ---
    st.divider()
    st.subheader("🚀 Bulk Attendance Update")
    c1, c2, c3 = st.columns([2,1,1])
    with c1:
        paste_ids = st.text_area("Paste IDs (T00747, T00222...)")
    with c2:
        day_val = st.number_input("Select Day", 1, 31)
    with c3:
        status_val = st.selectbox("Status", ["DP", "NP", "DA", "NA", "L", "T", "ST", "WO"])

    if st.button("Update Attendance Now"):
        wb = load_workbook(io.BytesIO(file_bytes))
        ws = wb[sel_month]
        id_list = [x.strip().upper() for x in paste_ids.replace(',', ' ').split()]
        
        # Column G is Day 1 (Index 7), isliye Day + 6
        target_col = 6 + day_val
        
        for r in range(14, ws.max_row + 1):
            val = str(ws.cell(row=r, column=2).value).strip().upper()
            if val in id_list:
                ws.cell(row=r, column=target_col).value = status_val
        
        out = io.BytesIO()
        wb.save(out)
        file_bytes = out.getvalue()
        st.success("Attendance updated successfully!")
        st.rerun()

    # --- 4. DOWNLOAD ---
    st.download_button("📥 Download Final Excel", file_bytes, "SafeTech_Attendance_Updated.xlsx")

else:
    st.info("Bhai, file upload karo, sab sahi dikhega.")
