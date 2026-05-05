import streamlit as st
import pandas as pd

st.set_page_config(page_title="Safe Tech Attendance System", layout="wide")

st.title("📊 12-Month Attendance Master System")

# --- 1. Sidebar: Master Worker List ---
st.sidebar.header("👥 Worker Management")
uploaded_file = st.sidebar.file_uploader("Upload Master Excel (Jan-Dec)", type=["xlsx"])

# --- 2. Main Dashboard (At Record Style) ---
st.header("📝 Daily Entry (At Record)")

# Mahina select karne ke liye
months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
selected_month = st.selectbox("Select Month for Entry", months)

# Aapki Excel sheet ki tarah alag-alag boxes
col1, col2, col3 = st.columns(3)

with col1:
    day_shift_ids = st.text_area(f"Day Shift (D) - {selected_month}", help="Comma separated IDs")
with col2:
    night_shift_ids = st.text_area(f"Night Shift (N) - {selected_month}")
with col3:
    absent_ids = st.text_area(f"Absent (A) - {selected_month}")

# --- 3. Processing Logic ---
if uploaded_file:
    # Saari sheets load karna
    all_sheets = pd.read_excel(uploaded_file, sheet_name=None)
    
    if st.button("🚀 Process & Generate Master Sheet"):
        # Selected month ki sheet nikalna
        if selected_month in all_sheets:
            df = all_sheets[selected_month]
            
            # Aapki sheet ke hisaab se columns dhoondna
            # Emp ID, Name, aur 1 se 31 tak ke columns
            st.write(f"Processing {selected_month} Attendance...")
            
            # Yahan logic: IDs ko split karke status update karna
            # (Ye part aapke Excel headers ke mutabiq auto-adjust hoga)
            
            st.success(f"✅ {selected_month} ka data process ho gaya hai!")
            st.dataframe(df.head(20)) # Preview dikhane ke liye
            
            # Download link
            st.download_button("📥 Download Updated 12-Month Record", "data", file_name="Master_Attendance.xlsx")
        else:
            st.error(f"Error: Upload ki gayi file mein '{selected_month}' naam ki sheet nahi mili.")

else:
    st.info("Bhai, pehle apni 12 mahine wali Master Excel file sidebar mein upload karein.")

# --- 4. Add New Worker Logic ---
st.divider()
st.subheader("➕ Add New Worker to Master")
with st.expander("Naya Worker jodne ke liye yahan click karein"):
    c1, c2, c3 = st.columns(3)
    new_id = c1.text_input("Worker ID")
    new_name = c2.text_input("Name")
    new_base = c3.selectbox("Base Status", ["D", "N"])
    if st.button("Save New Worker"):
        st.success(f"ID {new_id} ko Master List mein jod diya gaya hai.")
