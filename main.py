import streamlit as st
import pandas as pd

st.set_page_config(page_title="Attendance App", layout="wide")

st.title("✅ Attendance System (Working)")

# ===== ALWAYS VISIBLE UI =====
month = st.selectbox("Select Month", ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"])
day = st.number_input("Select Day", 1, 31, 1)
is_sunday = st.checkbox("Sunday / WO")

st.subheader("Enter IDs")

col1, col2, col3 = st.columns(3)

with col1:
    d_ids = st.text_area("Day IDs (D)")

with col2:
    n_ids = st.text_area("Night IDs (N)")

with col3:
    a_ids = st.text_area("Absent IDs (A)")

uploaded_file = st.file_uploader("Upload Excel (optional)", type=["xlsx"])

# ===== DUMMY DATA (so UI NEVER empty) =====
df = pd.DataFrame({
    "Emp ID": ["T00001","T00002
