import streamlit as st
import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import PatternFill, Alignment, Font
import io
from datetime import datetime

# --- PAGE SETUP ---
st.set_page_config(page_title="SafeTech Workforce Management", layout="wide")

# Custom Styling
st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    .stTabs [data-baseweb="tab-list"] { gap: 24px; }
    .stTabs [data-baseweb="tab"] { height: 50px; white-space: pre-wrap; background-color: #f0f2f6; border-radius: 4px 4px 0px 0px; gap: 1px; padding-top: 10px; }
    .stTabs [aria-selected="true"] { background-color: #1E3A8A; color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# Logo
try:
    st.sidebar.image("3810b91a7e82de2cb2273cb3494b93cbc0589111", width=150)
except:
    st.sidebar.title("SAFETECH PRECAST")

st.markdown("<h1 style='text-align:center; color:#1E3A8A;'>🏗️ SAFETECH ATTENDANCE & WORKER DATABASE</h1>", unsafe_allow_html=True)

uploaded_file = st.file_uploader("Upload Master Excel File", type=["xlsx"])

if uploaded_file:
    file_bytes = uploaded_file.read()
    
    # --- 1. WORKER MANAGEMENT (ADD OPTION WAPAS AA GAYA) ---
    st.sidebar.header("⚙️ Admin Controls")
    with st.sidebar.expander("➕ Add New Worker to System", expanded=False):
        with st.form("add_worker_form"):
            new_id = st.text_input("Employee ID (e.g. T00123)")
            new_name = st.text_input("Full Name")
            new_desig = st.text_input("Designation")
            new_dept = st.text_input("Department")
            new_shift = st.selectbox("Base Status (Shift)", ["Day Shift", "Night Shift"])
            new_join = st.date_input("Joining Date", datetime.now())
            submit_new = st.form_submit_button("Register Worker")

    if submit_new and new_id:
        wb = load_workbook(io.BytesIO(file_bytes))
        for sheet in wb.sheetnames:
            if sheet != "At Record":
                ws = wb[sheet]
                # Finding next empty row from Row 15
                r = 15
                while ws.cell(row=r, column=2).value is not None:
                    r += 1
                
                ws.cell(row=r, column=1).value = r - 14      # Srl No
                ws.cell(row=r, column=2).value = new_id      # Emp ID
                ws.cell(row=r, column=3).value = new_name    # Name
                ws.cell(row=r, column=4).value = new_desig   # Desig
                ws.cell(row=r, column=5).value = new_dept    # Dept
                ws.cell(row=r, column=6).value = new_join    # Joining
                # Base Status Column (AL)
                ws.cell(row=r, column=38).value = "D" if "Day" in new_shift else "N"
        
        out = io.BytesIO()
        wb.save(out)
        file_bytes = out.getvalue()
        st.sidebar.success(f"Worker {new_id} added successfully!")

    # --- 2. DATA PROCESSING ---
    xls = pd.ExcelFile(io.BytesIO(file_bytes))
    months = [m for m in xls.sheet_names if m != "At Record"]
    selected_month = st.selectbox("📅 Select Monthly Register", months)

    # Error handling for Column Names
    try:
        # Aapki sheet mein Row 13 par header hai
        df_raw = pd.read_excel(io.BytesIO(file_bytes), sheet_name=selected_month, skiprows=12)
        
        # Cleanup: Remove spaces from column names
        df_raw.columns = [str(c).strip() for c in df_raw.columns]
        
        # KEYERROR FIX: Check if 'Emp ID' exists, if not, find the column that looks like it
        id_col = 'Emp ID'
        if id_col not in df_raw.columns:
            # Try to find any column containing 'ID'
            possible_cols = [c for c in df_raw.columns if 'ID' in c.upper()]
            if possible_cols: id_col = possible_cols[0]

        # Display Data
        df_active = df_raw[df_raw[id_col].notna()].copy()
        st.subheader(f"Attendance View: {selected_month}")
        st.dataframe(df_active, use_container_width=True, hide_index=True)

    except Exception as e:
        st.error(f"Sheet Error: Header Row 13 mein problem hai. Details: {e}")
        df_active = pd.DataFrame()

    # --- 3. BULK ATTENDANCE & SHIFT LOGIC ---
    st.divider()
    st.header(f"🚀 Operations for {selected_month}")
    
    t1, t2 = st.tabs(["⚡ Bulk Attendance Update", "📊 Worker Status Checker"])
    
    with t1:
        c1, c2, c3 = st.columns([2, 1, 1])
        with c1:
            paste_area = st.text_area("Paste Employee IDs (Separated by space or newline)", height=150)
        with c2:
            date_num = st.number_input("Select Date (1-31)", 1, 31)
            shift_opt = st.radio("Current Shift Mode", ["Day (DP/DA)", "Night (NP/NA)"])
        with c3:
            if "Day" in shift_opt:
                status_val = st.selectbox("Status", ["DP", "DA", "L", "T", "WO", "ST"])
            else:
                status_val = st.selectbox("Status", ["NP", "NA", "L", "T", "WO", "ST"])
            
        if st.button("Apply to Register"):
            if paste_area:
                wb = load_workbook(io.BytesIO(file_bytes))
                ws = wb[selected_month]
                id_list = [idx.strip().upper() for idx in paste_area.replace(',', ' ').split()]
                
                # Column G (7) is Day 1
                col_target = 6 + date_num
                
                count = 0
                for row_idx in range(15, ws.max_row + 1):
                    cell_val = str(ws.cell(row=row_idx, column=2).value).strip().upper()
                    if cell_val in id_list:
                        ws.cell(row=row_idx, column=col_target).value = status_val
                        # Highlight cell
                        ws.cell(row=row_idx, column=col_target).fill = PatternFill(start_color="B7E1CD", fill_type="solid")
                        count += 1
                
                out = io.BytesIO()
                wb.save(out)
                file_bytes = out.getvalue()
                st.success(f"Updated {count} records successfully!")
                st.rerun()

    with t2:
        if not df_active.empty:
            # Base Status (Shift) Check (Assuming column 38/AL holds shift)
            st.write("Base Status is managed in the Master Excel (Column AL).")
            search = st.text_input("Quick Search (Name/ID)")
            if search:
                res = df_active[df_active.apply(lambda r: search.lower() in str(r).lower(), axis=1)]
                st.dataframe(res)

    # --- 4. DOWNLOAD ---
    st.divider()
    st.download_button(
        "📥 Download Updated SafeTech Master",
        file_bytes,
        file_name=f"SafeTech_Attendance_Final.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

else:
    st.info("Bhai, SafeTech Master Attendance file upload kijiye.")
