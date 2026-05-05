import streamlit as st
import pandas as pd
from datetime import datetime
import os

# Page configuration
st.set_page_config(page_title="Safe Tech Attendance Pro", layout="wide")

# --- INITIALIZE DATABASE ---
# Hum ek local file banayenge taaki data permanent save rahe
DB_FILE = "attendance_db.csv"

def load_db():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE, dtype={"Emp ID": str})
    else:
        # Initial columns exact as per your CSV/Photo
        return pd.DataFrame(columns=["Srl No", "Emp ID", "Emp Name", "Designation", "Department", "Joining", "Base Status"])

def save_to_db(df):
    df.to_csv(DB_FILE, index=False)

# Load data into session state
if 'db' not in st.session_state:
    st.session_state.db = load_db()

# --- SIDEBAR: ADMIN CONTROLS ---
st.sidebar.markdown(
    """
    <style>
    .sidebar-header {
        font-size: 20px;
        color: #1E3A8A;
        font-weight: bold;
        text-align: center;
        background-color: #DBEAFE;
        padding: 10px;
        border-radius: 5px;
    }
    </style>
    """, unsafe_allow_html=True
)
st.sidebar.markdown('<p class="sidebar-header">🛠️ SAFE TECH CONTROLS</p>', unsafe_allow_html=True)

# 1. Option to Bulk Upload via Excel (Keep as backup)
st.sidebar.subheader("📤 Bulk Upload Workers")
uploaded_file = st.sidebar.file_uploader("Upload Excel (Srl No, Emp ID, Name cols)", type=["xlsx"])

if uploaded_file:
    # Try to clean Excel based on your provided format
    df_xl = pd.read_excel(uploaded_file, skiprows=12) # Skip headers as before
    df_xl = df_xl.dropna(subset=["Emp ID"])
    df_xl["Emp ID"] = df_xl["Emp ID"].astype(str)
    
    if st.sidebar.button("Append to Database"):
        new_df = pd.concat([st.session_state.db, df_xl[["Srl No", "Emp ID", "Emp Name", "Designation", "Department", "Joining"]]], ignore_index=True).drop_duplicates(subset=["Emp ID"])
        st.session_state.db = new_df
        save_to_db(new_df)
        st.sidebar.success(f"Workers added! Total now: {len(new_df)}")

st.sidebar.divider()

# 2. Add New Worker Form (Permanent Saving)
with st.sidebar.expander("➕ Add Single Worker Manually", expanded=False):
    c1, c2 = st.columns(2)
    new_f_name = c1.text_input("1. First Name")
    new_s_name = c2.text_input("2. Second Name")
    new_id = st.text_input("3. Worker ID No")
    new_desig = st.text_input("4. Designation")
    new_dept = st.text_input("5. Department")
    new_doj = st.date_input("6. Joining Date", datetime.now())
    new_base = st.selectbox("Base Status", ["D", "N"])
    
    if st.button("Save Permanent"):
        if new_id and new_f_name:
            # Check for duplicate
            if new_id in st.session_state.db["Emp ID"].values:
                st.error(f"Error: ID {new_id} already exists!")
            else:
                full_name = f"{new_f_name} {new_s_name}".strip()
                srl_no = len(st.session_state.db) + 1
                new_row = pd.DataFrame([{
                    "Srl No": srl_no,
                    "Emp ID": str(new_id),
                    "Emp Name": full_name,
                    "Designation": new_desig,
                    "Department": new_dept,
                    "Joining": new_doj.strftime('%Y-%m-%d'),
                    "Base Status": new_base
                }])
                updated_db = pd.concat([st.session_state.db, new_row], ignore_index=True)
                st.session_state.db = updated_db
                save_to_db(updated_db)
                st.success(f"Worker {full_name} saved permanently!")
        else:
            st.error("ID and First Name required!")

# --- MAIN INTERFACE (Exact as Photo) ---
st.markdown(
    """
    <style>
    .header-box {text-align: center; color: white; background-color: #1E3A8A; padding: 10px; border-radius: 5px; margin-bottom: 0px;}
    .sub-header {text-align: center; color: #4B5563; font-size: 18px; margin-top: 5px;}
    </style>
    """, unsafe_allow_html=True
)

st.markdown('<h1 class="header-box">SAFETECH PRECAST</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">MONTHLY ATTENDANCE REGISTER - 2026</p>', unsafe_allow_html=True)
st.divider()

if not st.session_state.db.empty:
    df = st.session_state.db.copy()
    
    # Header display columns as requested in photo
    display_cols = ["Srl No", "Emp ID", "Emp Name", "Designation", "Department", "Joining"]
    
    # Calculate Days in current Month
    month_days = pd.period_range(start=datetime.now(), periods=1, freq='M')[0].days_in_month
    
    # 3. Create Status Columns (1 to Month End)
    # Filling with empty strings for initial display
    for day in range(1, month_days + 1):
        df[str(day)] = "" # Empty for 'P', 'A', 'D', 'N' entry

    # Create Summary Columns (Total P, Total A)
    df["Total Present"] = 0
    df["Total Absent"] = 0

    st.write(f"Total Workers in System: **{len(df)}**")
    
    # THE TABLE (Exact Column Layout from Photo)
    with st.spinner("Loading Professional Register View..."):
        st.dataframe(df, use_container_width=True, hide_index=True)
        
    # Download Button
    st.divider()
    csv_master = df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download This Master Sheet (CSV)", csv_master, "Safetech_Master.csv", "text/csv")
    st.info("Tip: Ye downloaded file CSV format mein hogi. Excel mein kholkar 'Save As' .xlsx kar sakte hain.")

else:
    st.markdown("<h3 style='text-align:center;'>Welcome to Safetech Pro</h3>", unsafe_allow_html=True)
    st.info("Sidebar se 'Add Single Worker' karein ya apni Excel file upload karein taaki hum system load kar sakein.")
    st.image("https://via.placeholder.com/1000x300.png?text=Please+Initialize+Worker+Database", use_container_width=True)
