import streamlit as st
import pandas as pd
import os

# Page Configuration
st.set_page_config(page_title="Safe Tech Attendance System", layout="wide")

# 1. Data Loading Logic (Updated for Excel)
@st.cache_data
def load_data():
    # APNI FILE KA NAAM YAHA CHECK KAREIN
    file_name = "attendance.xlsx" # <--- Jo naam GitHub par hai wahi yaha likhein
    
    if not os.path.exists(file_name):
        st.error(f"❌ File '{file_name}' GitHub par nahi mili! Check karein ki file upload hai.")
        return pd.DataFrame()
    
    try:
        # Excel read karne ke liye read_excel use karein
        df = pd.read_excel(file_name) 
        df.columns = df.columns.str.strip()
        return df
    except Exception as e:
        st.error(f"❌ Error: {e}")
        return pd.DataFrame()

df = load_data()

if not df.empty:
    st.title("📊 Safe Tech Attendance Dashboard")
    
    # --- Check for Columns ---
    # Agar 'Status' column nahi hai toh error na aaye isliye ye check:
    if 'Status' not in df.columns:
        st.warning("⚠️ Aapki file mein 'Status' column nahi mila. Dashboard metrics kaam nahi karenge.")
        st.dataframe(df) # Sirf data dikha do
    else:
        # Aapka purana filtering aur dashboard logic yahan chal jayega
        st.success("✅ Data load ho gaya hai!")
        st.dataframe(df, use_container_width=True)
else:
    st.info("Intazar... GitHub par file upload karein ya naam check karein.")
