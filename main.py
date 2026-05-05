# =========================
# MAIN UI (FIXED)
# =========================

st.title("🏗 SAFETECH ATTENDANCE SYSTEM")

month = st.selectbox("Select Month", [
    "January","February","March","April","May","June",
    "July","August","September","October","November","December"
])

day = st.number_input("Select Day", 1, 31, 1)
is_sunday = st.checkbox("Sunday / WO")

st.subheader("📝 Daily Entry")

col1, col2, col3 = st.columns(3)

with col1:
    day_ids = st.text_area("Day Shift IDs (D)")

with col2:
    night_ids = st.text_area("Night Shift IDs (N)")

with col3:
    absent_ids = st.text_area("Absent IDs (A)")

uploaded_file = st.sidebar.file_uploader("Upload Excel", type=["xlsx"])


# =========================
# LOAD DATA
# =========================

if uploaded_file:
    df = pd.read_excel(uploaded_file, sheet_name=0, skiprows=12)
    df.columns = df.columns.astype(str).str.strip()
else:
    # Dummy data (so UI works)
    df = pd.DataFrame({
        "Emp ID": ["T00001","T00002","T00003"],
        "Emp Name": ["Test 1","Test 2","Test 3"],
        "Designation": ["Worker","Worker","Worker"],
        "Department": ["Prod","Prod","Prod"],
        "Joining": ["01-01-2024","01-01-2024","01-01-2024"],
        "Base": ["D","N","D"]
    })


# =========================
# PROCESS BUTTON
# =========================

if st.button("🚀 Generate Attendance"):

    daily_entries = []

    if day_ids:
        for i in day_ids.split(","):
            daily_entries.append(f"{i.strip()}-D")

    if night_ids:
        for i in night_ids.split(","):
            daily_entries.append(f"{i.strip()}-N")

    if absent_ids:
        for i in absent_ids.split(","):
            daily_entries.append(f"{i.strip()}")

    col_name = f"{month[:3]}-{day}"

    df[col_name] = df.apply(
        lambda row: get_status(
            row.get("Emp ID"),
            row.get("Base", "D"),
            daily_entries,
            is_sunday
        ),
        axis=1
    )

    df.insert(0, "Srl No", range(1, len(df)+1))

    st.success("✅ Attendance Generated")
    st.dataframe(df, use_container_width=True)

    file = f"{month}_Attendance.xlsx"
    df.to_excel(file, index=False)

    with open(file, "rb") as f:
        st.download_button("📥 Download", f)
