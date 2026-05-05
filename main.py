
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Attendance App", layout="wide")

st.title("📊 Smart Attendance App")

# ==== SIDEBAR ====
st.sidebar.header("➕ Add New Worker")

new_id = st.sidebar.text_input("Employee ID")
new_name = st.sidebar.text_input("Name")
new_desig = st.sidebar.text_input("Designation")
new_dept = st.sidebar.text_input("Department")
new_doj = st.sidebar.text_input("Date of Joining")
new_status = st.sidebar.selectbox("Base Status", ["D", "N", "L", "R", "T", "ST"])

add_worker = st.sidebar.button("Add Worker")

# ==== MAIN ====

uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx"])

st.subheader("📝 Daily Entry (Important)")

col1, col2, col3 = st.columns(3)

with col1:
    day_ids = st.text_area("Day Shift (D) IDs (comma separated)")

with col2:
    night_ids = st.text_area("Night Shift (N) IDs")

with col3:
    absent_ids = st.text_area("Absent IDs")

# ==== FUNCTIONS ====

def convert_to_dict(text, status):
    result = {}
    if text:
        ids = text.split(",")
        for i in ids:
            result[i.strip()] = status
    return result


def get_status(emp_id, entry, base_status):

    if base_status in ["R", "T", "ST"]:
        return base_status

    if base_status == "L":
        if entry == "D":
            return "DP"
        if entry == "N":
            return "NP"
        if entry == "A":
            return "NA"
        return "L"

    if entry == "D":
        return "DP"

    if entry == "N":
        return "NP"

    if entry == "A":
        return "DA" if base_status == "D" else "NA"

    return "DP" if base_status == "D" else "NP"


# ==== PROCESS ====

if uploaded_file:

    df = pd.read_excel(uploaded_file)

    # Add worker
    if add_worker:
        new_row = {
            "Emp ID": new_id,
            "Name": new_name,
            "Designation": new_desig,
            "Department": new_dept,
            "DOJ": new_doj,
            "Base": new_status
        }
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        st.success("✅ Worker Added")

    if st.button("🚀 Generate Report"):

        day_dict = convert_to_dict(day_ids, "D")
        night_dict = convert_to_dict(night_ids, "N")
        absent_dict = convert_to_dict(absent_ids, "A")

        all_entries = {**day_dict, **night_dict, **absent_dict}

        results = []

        for i, row in df.iterrows():

            emp_id = str(row["Emp ID"]).strip()
            base = row.get("Base", "D")

            entry = all_entries.get(emp_id)

            status = get_status(emp_id, entry, base)

            results.append(status)

        df["Today Status"] = results

        # Add Srl No
        df.insert(0, "Srl No", range(1, len(df)+1))

        st.dataframe(df)

        # Download
        file = "FINAL_REPORT.xlsx"
        df.to_excel(file, index=False)

        with open(file, "rb") as f:
            st.download_button("📥 Download Report", f)

        st.success("✅ Done!")
