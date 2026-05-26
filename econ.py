import streamlit as st
import pandas as pd
import numpy as np
import time

# ==========================================
# BACKWARD COMPATIBILITY FUNCTION FOR RERUN
# ==========================================
# This function automatically detects your Streamlit version to prevent AttributeError
def safe_rerun():
    if hasattr(st, "rerun"):
        st.rerun()
    else:
        st.experimental_rerun()

# ==========================================
# 1. INTERNAL SYNTHETIC DATA GENERATOR (Zero-File Dependency)
# ==========================================
@st.cache_data
def get_internal_data():
    np.random.seed(42)
    n_samples = 1000
    vehicle_ids = [f"TR-{np.random.randint(10,81)}{np.random.choice(['A','B'])}{np.random.choice(['A','B'])}{np.random.randint(100,999)}" for _ in range(n_samples)]
    vehicle_types = np.random.choice(['ICE', 'EV'], size=n_samples, p=[0.7, 0.3])
    ages = np.random.randint(1, 15, size=n_samples)
    appointment_statuses = np.random.choice(['Scheduled_OnTime', 'No_Show', 'No_Appointment_Unlawful'], size=n_samples, p=[0.75, 0.10, 0.15])
    tolerance_days_left = np.random.randint(-15, 7, size=n_samples)
    
    df = pd.DataFrame({
        'Vehicle_ID': vehicle_ids,
        'Vehicle_Type': vehicle_types,
        'Age': ages,
        'Appointment_Status': appointment_statuses,
        'Tolerance_Days_Left': tolerance_days_left,
        'NOx_Emissions': np.where(vehicle_types == 'ICE', 45 + ages * 4 + np.random.normal(0, 8, n_samples), np.nan),
        'Insulation_Resistance_M_Ohm': np.where(vehicle_types == 'EV', np.random.uniform(250, 900, n_samples), np.nan),
        'Max_Cell_Temp_C': np.where(vehicle_types == 'EV', 28 + ages * 0.8 + np.random.normal(0, 2, n_samples), np.nan),
        'Inspection_Result': ['Pass'] * n_samples
    })
    
    # Inject fraud and defect rules
    df.loc[(df['Vehicle_Type'] == 'ICE') & (df['Age'] > 10), 'NOx_Emissions'] += 200
    df.loc[(df['Vehicle_Type'] == 'ICE') & (df['NOx_Emissions'] > 100), 'Inspection_Result'] = 'Fail_Emission_Fraud'
    
    df.loc[(df['Vehicle_Type'] == 'EV') & (df['Age'] > 11), 'Insulation_Resistance_M_Ohm'] = 45
    df.loc[(df['Vehicle_Type'] == 'EV') & (df['Insulation_Resistance_M_Ohm'] < 100), 'Inspection_Result'] = 'Fail_EV_Safety'
    
    return df

df_vehicles = get_internal_data()

# ==========================================
# 2. STREAMLIT UI - DIGITAL TWIN PLATFORM
# ==========================================
st.markdown("<h1 style='text-align: center; color: #1E3A8A;'>🌐 Cyber-Physical Digital Twin Platform for Vehicle Inspection Networks</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>HGS Macro-Data Stream, Dynamic Appointment Fines, and Station-Level Bottleneck Optimization</p>", unsafe_allow_html=True)
st.hr()

# Session State Configuration (Saves state between reruns)
if 'ice_q' not in st.session_state: st.session_state.ice_q = 4
if 'ev_q' not in st.session_state: st.session_state.ev_q = 9
if 'hybrid' not in st.session_state: st.session_state.hybrid = False

col1, col2, col3 = st.columns(3)

# --- COLUMN 1: MACRO TELEMETRY (HGS STREAM) ---
with col1:
    st.subheader("🛣️ HGS Gantry Live Telemetry")
    st.write("Real-time vehicle detection and compliance checks from highway sensors:")
    
    run_hgs = st.button("Trigger HGS Data Stream", key="hgs_btn")
    
    if run_hgs:
        sample = df_vehicles.sample(4)
        for idx, row in sample.iterrows():
            if row['Appointment_Status'] == 'No_Appointment_Unlawful' and row['Tolerance_Days_Left'] < 0:
                st.error(f"❌ {row['Vehicle_ID']}: Inspection Expired ({abs(row['Tolerance_Days_Left'])} days)! Automated Fine Issued.")
            elif row['Appointment_Status'] == 'No_Show':
                st.warning(f"⚠️ {row['Vehicle_ID']}: Missed Appointment (No-Show)! Capacity Block Penalty Applied.")
            else:
                st.success(f"✅ {row['Vehicle_ID']}: Valid/Scheduled Route.")
                if row['Vehicle_Type'] == 'ICE': st.session_state.ice_q += 1
                else: st.session_state.ev_q += 1

# --- COLUMN 2: STATION QUEUE & BOTTLENECK SIMULATION ---
with col2:
    st.subheader("🏢 In-Station Queue Status")
    ev_wait = st.session_state.ev_q * 16 / (2 if st.session_state.hybrid else 1)
    
    st.metric(label="ICE (Conventional) Queue Length", value=f"{st.session_state.ice_q} Vehicles")
    st.metric(label="EV (Electric Vehicle) Queue Length", value=f"{st.session_state.ev_q} Vehicles", delta=f"Est. Wait Time: {ev_wait:.0f} mins", delta_color="inverse" if ev_wait > 30 else "normal")
    
    st.subheader("🤖 Digital Twin Decision Support")
    if st.session_state.ev_q >= 6 and not st.session_state.hybrid:
        st.error("⚠️ CRITICAL BOTTLENECK: EV queue exceeds threshold! Reassignment of Lane-2 is highly recommended.")
        if st.button("Deploy Lane-2 to Flexible Hybrid Mode"):
            st.session_state.hybrid = True
            safe_rerun()
    elif st.session_state.hybrid:
        st.success("🔄 Flexible Hybrid Mode Active: Lane-2 processing both ICE & EV.")
        if st.button("Deactivate Hybrid Mode"):
            st.session_state.hybrid = False
            safe_rerun()
            
    if st.button("Process Vehicles (Advance Simulation)"):
        if st.session_state.ice_q > 0: st.session_state.ice_q -= 1
        if st.session_state.ev_q > 0: st.session_state.ev_q -= (2 if st.session_state.hybrid else 1)
        safe_rerun()

# --- COLUMN 3: CYBER-PHYSICAL TESTING ROOM ---
with col3:
    st.subheader("🔬 Diagnostic Testing Cell")
    if st.button("Inspect Next Vehicle in Queue"):
        car = df_vehicles.sample(1).iloc[0]
        st.code(f"Plate ID: {car['Vehicle_ID']}\nType: {car['Vehicle_Type']}")
        
        if car['Vehicle_Type'] == 'ICE':
            st.info("📊 Gas Analyzer & OBD Cross-Reference")
            st.write(f"Physical NOx Emissions: {car['NOx_Emissions']:.1f} ppm")
            
            if car['Inspection_Result'] == 'Fail_Emission_Fraud':
                st.error("🚨 EMISSION FRAUD DETECTED! OBD clear but physical emissions exceed legal thresholds. ECU Remap/AdBlue Defeat Software Active. REJECTED.")
            else:
                st.success("✅ Emission profiles within legal standards.")
        else:
            st.info("⚡ High-Voltage Insulation & Thermal Scan")
            st.write(f"Insulation Resistance: {car['Insulation_Resistance_M_Ohm']:.1f} MΩ")
            
            if car['Inspection_Result'] == 'Fail_EV_Safety':
                st.error("🚨 EV SAFETY HAZARD! Critical insulation breakdown or cell overheating splayed (Thermal Runaway Risk). VEHICLE REJECTED.")
            else:
                st.success("✅ Battery pack high-voltage integrity verified.")

st.hr()
# Native Streamlit Chart (No Plotly Dependency Error)
st.subheader("📊 Network Inspection Statistics (Jury Analytics Hub)")
summary_data = df_vehicles['Inspection_Result'].value_counts()
st.bar_chart(summary_data)