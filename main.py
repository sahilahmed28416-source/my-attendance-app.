import streamlit as st
import pandas as pd

st.set_page_config(page_title="Attendance App", layout="wide")

st.title("📊 SAFETECH Attendance System")

# ===== UI ALWAYS VISIBLE =====
month = st.selectbox("Select Month", [
    "January","February","March","April","May","June",
    "July","August","September","October","November","December"
])

day = st.number_input("Select Day", 1, 31, 1)
is_sunday = st.checkbox("Sunday / WO")

st.subheader("📝 Daily Entry (Comma separated IDs)")

col1, col2, col3 = st.columns(3)

with col1:
    d_ids = st.text_area("Day Shift (D)")

with col2:
    n_ids = st.text_area("Night Shift (N)")

with col3:
    a_ids = st.text_area("Absent (A)")

uploaded_file = st.file_uploader("Upload Excel (optional)", type=["xlsx"])

# ===== DEFAULT DATA =====
df = pd.DataFrame({
    "Emp ID": ["T00001","T00002","T00003"],
    "Name": ["Worker1","Worker2","Worker3"],
    "Designation": ["Worker","Worker","Worker"],
    "Department": ["Production","Production","Production"],
    "Joining": ["01-01-2024","01-01-2024","01-01-2024"],
    "Base": ["D","N","D"]
})

# ===== LOAD EXCEL =====
if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file)
    except:
        st.error("⚠️ Excel format issue")

# ===== LOGIC =====
def get_status(emp_id, base):
    emp_id = str(emp_id).strip()

    if emp_id in d_ids:
        return "D6" if is_sunday else "DP"

    if emp_id in n_ids:
        return "N6" if is_sunday else "NP"

    if emp_id in a_ids:
        if is_s
