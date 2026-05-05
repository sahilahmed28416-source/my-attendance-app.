import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Safe Tech Attendance Pro", layout="wide")

DB_FILE = "attendance_db.csv"

def load_db():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE, dtype={"Emp ID": str})
    return pd.DataFrame(columns=["Srl No", "Emp ID", "Emp Name", "Designation", "Department", "Joining"])

if 'db' not in st.session_state:
    st.session_state.db = load_db()

# --- SIDEBAR ---
st.sidebar.title("🛠️ Safe Tech Admin")

# BULK UPLOAD SECTION (Yahan error theek kiya hai)
st.sidebar.subheader("📤 Upload Master Excel")
uploaded_file = st.sidebar.file_uploader("Apni 770 workers wali file yahan dalein", type=["xlsx"])

if uploaded_file:
    if st.sidebar.button("Import All Workers"):
        try:
            # Row 13 se read karna (Skip 12 rows) kyunki aapki file waise hi hai
            df_xl = pd.read_excel(uploaded_file, skiprows=12)
            
            # Sirf kaam ke columns ko filter karna
            req_cols = ["Srl No", "Emp ID", "Emp Name", "Designation", "Department", "Joining"]
            
            # Agar columns ke naam match nahi karte toh unhe dhoondna
            available_cols = [c for c in req_cols if c in df_xl.columns]
            
            if "Emp ID" in available_cols:
                final_data = df_xl[available_cols].dropna(subset=["Emp ID"])
                final_data["Emp ID"] = final_data["Emp ID"].astype(str)
                
                # Database mein save karna
                st.session_state.db = final_data
                st.session_state.db.to_csv(DB_FILE, index=False)
                st.sidebar.success(f"✅ {len(final_data)} Workers Load Ho Gaye!")
                st.rerun()
            else:
                st.sidebar.error("Error: Excel mein 'Emp ID' column nahi mila!")
        except Exception as e:
            st.sidebar.error(f"Error: {e}")

# --- MAIN INTERFACE (Photo Jaisa) ---
st.markdown("<h1 style='text-align: center; color: white; background-color: #1E3A8A; padding: 10px; border-radius: 10px;'>SAFETECH PRECAST</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #4B5563; font-size: 20px;'>MONTHLY ATTENDANCE REGISTER - 2026</p>", unsafe_allow_html=True)
st.divider()

if not st.session_state.db.empty:
    df_display = st.session_state.db.copy()
    
    # 30-31 dinon ke empty columns banana jaisa aapne manga tha
    for i in range(1, 32):
        df_display[str(i)] = ""
    
    st.write(f"Total Workers in Register: **{len(df_display)}**")
    st.dataframe(df_display, use_container_width=True, hide_index=True)
    
    # Download button
    csv = df_display.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download Full Register", csv, "Safetech_Attendance.csv")
else:
    st.info("Bhai, sidebar se Excel file upload karke 'Import' button dabayein taaki 770 log show hon.")
