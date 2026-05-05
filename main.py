import streamlit as st
import pandas as pd
import os
from datetime import datetime

st.set_page_config(page_title="Safe Tech Attendance Pro", layout="wide")

DB_FILE = "worker_database.csv"

# =========================
# 🔥 STATUS LOGIC (FINAL)
# =========================
def get_status(emp_id, base_status, daily_entries, is_sunday):

    emp_id = str(emp_id).strip().upper()

    entry = None
    for e in daily_entries:
        e = str(e).upper()
        if emp_id in e:
            entry = e
            break

    # Special
    if base_status in ["R", "T", "ST"]:
        return base_status

    # Leave logic
    if base_status == "L":
        if entry:
            if "D" in entry: return "DP"
            if "N" in entry: return "NP"
            if "DA" in entry: return "DA"
            if "NA" in entry: return "NA"
            if "A" in entry: return "NA"
        return "L"

    # Detect entry
    if entry:
        if "D" in entry:
            return "D6" if is_sunday else "DP"

        if "N" in entry:
            return "N6" if is_sunday else "NP"

        if "A" in entry or entry == emp_id:
            return "DA" if base_status == "D" else "NA"

    # No entry
    if is_sunday:
        return "WO"

    return "DP" if base_status == "D" else "NP"


# =========================
# SIDEBAR
# =========================
st.sidebar.header("➕ Add Worker")

f_name = st.sidebar.text_input("First Name")
s_name = st.sidebar.text_input("Second Name")
w_id = st.sidebar.text_input("Worker ID")
w_desig = st.sidebar.text_input("Designation")
w_dept = st.sidebar.text_input("Department")
w_doj = st.sidebar.date_input("Joining Date", datetime.now())
w_base = st.sidebar.selectbox("Base Status", ["D", "N", "L", "R", "T", "ST"])

if st.sidebar.button("Save Worker"):
    if w_id and f_name:
        new_data = pd.DataFrame([[w_id, f"{f_name} {s_name}", w_desig, w_dept, w_doj, w_base]],
            columns=["Emp ID", "Emp Name", "Designation", "Department", "Joining", "Base"])

        if os.path.exists(DB_FILE):
            new_data.to_csv(DB_FILE, mode='a', header=False, index=False)
        else:
            new_data.to_csv(DB_FILE, index=False)

        st.sidebar.success("Worker Saved!")
    else:
        st.sidebar.error("ID & Name required")

st.sidebar.divider()
uploaded
