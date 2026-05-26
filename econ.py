import streamlit as st
import pandas as pd
import numpy as np

# Page Layout Optimization for Side-by-Side Flow
st.set_page_config(layout="wide", page_title="Digital Twin: Dynamic Compliance & Inspection")

def safe_rerun():
    if hasattr(st, "rerun"):
        st.rerun()
    else:
        st.experimental_rerun()

# ====================================================================
# 1. GENERATE INTERNAL NETWORK SYNTHETIC DATA (1000 Vehicles Database)
# ====================================================================
@st.cache_data
def get_network_database():
    np.random.seed(42)
    n_samples = 1000
    vehicle_ids = [f"TR-{np.random.randint(10,81)}{np.random.choice(['A','B'])}{np.random.choice(['A','B'])}{np.random.randint(100,999)}" for _ in range(n_samples)]
    vehicle_types = np.random.choice(['ICE', 'EV'], size=n_samples, p=[0.7, 0.3])
    ages = np.random.randint(1, 15, size=n_samples)
    
    # Behavior Patterns: Compliant, Procrastinator (No Booking), Unreliable (No-Show)
    driver_behaviors = np.random.choice(['Compliant_OffPeak', 'Compliant_Peak', 'No_Booking_Procrastinator', 'No_Show_Risk'], size=n_samples, p=[0.45, 0.30, 0.15, 0.10])
    days_past_deadline = np.random.randint(-15, 10, size=n_samples)
    
    df = pd.DataFrame({
        'Vehicle_ID': vehicle_ids,
        'Vehicle_Type': vehicle_types,
        'Age': ages,
        'Driver_Behavior': driver_behaviors,
        'Days_Past_Deadline': days_past_deadline,
        'NOx_Emissions': np.where(vehicle_types == 'ICE', 45 + ages * 4 + np.random.normal(0, 8, n_samples), np.nan),
        'Insulation_Resistance_M_Ohm': np.where(vehicle_types == 'EV', np.random.uniform(250, 900, n_samples), np.nan),
        'Inspection_Status': ['Pending'] * n_samples
    })
    
    # Injecting real-world anomalies (Frauds & Failures)
    df.loc[(df['Vehicle_Type'] == 'ICE') & (df['Age'] > 10), 'NOx_Emissions'] += 200
    df.loc[(df['Vehicle_Type'] == 'EV') & (df['Age'] > 11), 'Insulation_Resistance_M_Ohm'] = 45
    return df

df_network = get_network_database()

# Initialize Session State Variables to Maintain Simulation State
if 'ice_queue' not in st.session_state: st.session_state.ice_queue = 3
if 'ev_queue' not in st.session_state: st.session_state.ev_queue = 4
if 'station_load' not in st.session_state: st.session_state.station_load = "Balanced"
if 'recovered_slots' not in st.session_state: st.session_state.recovered_slots = 0
if 'hgs_log' not in st.session_state: st.session_state.hgs_log = []

# ====================================================================
# 2. STREAMLIT UI - CYBER-PHYSICAL INFRASTRUCTURE DASHBOARD
# ====================================================================
st.markdown("<h2 style='text-align: center; color: #1E3A8A;'>🌐 Cyber-Physical Inspection Network Digital Twin</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #555;'>HGS Macro-Tracking, Time-Window Tolerance Regulations, and Capacity Block Remediation</p>", unsafe_allow_html=True)
st.divider()

# Setup logical flow panels from left to right
col_hgs, col_station, col_testing = st.columns([1.1, 1.2, 1.1], gap="large")

# --------------------------------------------------------------------
# PANEL 1: HIGHWAY INFRASTRUCTURE (HGS TELEMETRY & ROUTING)
# --------------------------------------------------------------------
with col_hgs:
    st.markdown("### 🛣️ 1. HGS Gantry Tracking & Incentives")
    st.caption("Scans approaching vehicles and routes them based on dynamic load optimization algorithms.")
    
    if st.button("📡 Scan Incoming Highway Traffic", type="primary", use_container_width=True):
        samples = df_network.sample(4)
        current_logs = []
        
        for _, car in samples.iterrows():
            v_id = car['Vehicle_ID']
            behavior = car['Driver_Behavior']
            days_expired = car['Days_Past_Deadline']
            
            if days_expired > 0: # Inspection deadline has passed
                if behavior == 'No_Booking_Procrastinator':
                    current_logs.append(f"🔴 **{v_id} (Fined):** Expired by {days_expired} days with no active booking. Automated electronic fine issued via HGS.")
                elif behavior == 'No_Show_Risk':
                    current_logs.append(f"⚠️ **{v_id} (No-Show Alert):** Missed original slot. Capacity Block Penalty applied. Slot revoked.")
                    st.session_state.recovered_slots += 1 # Critical feature: Dynamic slot recovery triggered
                elif behavior == 'Compliant_OffPeak':
                    current_logs.append(f"🟢 **{v_id} (Incentivized):** Expired but selected Off-Peak via Twin suggestion. Granted 15% toll credit. Queued.")
                    if car['Vehicle_Type'] == 'ICE': st.session_state.ice_queue += 1
                    else: st.session_state.ev_queue += 1
                else:
                    current_logs.append(f"✅ **{v_id} (Scheduled):** Regular peak-hour booking verified. Routed to station.")
                    if car['Vehicle_Type'] == 'ICE': st.session_state.ice_queue += 1
                    else: st.session_state.ev_queue += 1
            else:
                current_logs.append(f"✨ **{v_id} (Compliant):** Registration valid for {abs(days_expired)} days.")
                
        st.session_state.hgs_log = current_logs
        safe_rerun()

    # Communication Feed Terminal
    st.markdown("**Digital Twin Telemetry & SMS Feed:**")
    if st.session_state.hgs_log:
        for log in st.session_state.hgs_log:
            st.markdown(log)
    else:
        st.code("System idling. Awaiting HGS gantry sensor activations...", language="markdown")

# --------------------------------------------------------------------
# PANEL 2: PHYSICAL STATION INFRASTRUCTURE & CAPACITY PLANNING
# --------------------------------------------------------------------
with col_station:
    st.markdown("### 🏢 2. Live Station Buffer Yards")
    st.caption("Visualizing physical queues inside the inspection facility generated by the HGS input feed.")
    
    # Performance Metrics Matrix
    m1, m2 = st.columns(2)
    with m1:
        st.metric(label="Lane 1 Queue (ICE)", value=f"{st.session_state.ice_queue} Vehicles")
    with m2:
        est_wait = st.session_state.ev_queue * 14
        st.metric(label="Lane 2 Queue (EV)", value=f"{st.session_state.ev_queue} Vehicles", delta=f"Est: {est_wait} mins")

    st.divider()
    st.markdown("#### 🔄 Proactive Capacity Recovery Status")
    
    # Capacity Healing System Interaction Loop
    if st.session_state.recovered_slots > 0:
        st.warning(f"💡 **Dynamic Optimization Opportunity:** {st.session_state.recovered_slots} slots were blocked by No-Shows. The system can re-allocate these to upcoming highway drivers.")
        if st.button("⚡ Inject Recovered Slots as 'Urgent Discounts'", use_container_width=True):
            # Simulate real-time recovery by filling empty slots with waiting vehicles, easing station stress
            if st.session_state.ev_queue > 1:
                st.session_state.ev_queue -= 1
                st.session_state.recovered_slots -= 1
                st.toast("Reassigned open slot to a nearby EV vehicle over the HGS network!", icon="⚡")
                safe_rerun()
    else:
        st.success("No capacity leaks detected. All scheduled drivers are currently accounting for their allocated time blocks.")

    if st.button("🚗 Dispatch Inspected Vehicle (Clear Queue)", use_container_width=True):
        if st.session_state.ice_queue > 0: st.session_state.ice_queue -= 1
        if st.session_state.ev_queue > 0: st.session_state.ev_queue -= 1
        safe_rerun()

# --------------------------------------------------------------------
# PANEL 3: DIAGNOSTIC TESTING CELLS (CYBER-PHYSICAL INTERFACE)
# --------------------------------------------------------------------
with col_testing:
    st.markdown("### 🔬 3. Diagnostic Sensor Verification")
    st.caption("Pulls the leading vehicle from the physical lane buffer into the hardware testing cells.")
    
    if st.button("🧪 Process Next In-Line Vehicle", type="secondary", use_container_width=True):
        current_test = df_network.sample(1).iloc[0]
        
        st.markdown(f"**Target Unit ID:** `{current_test['Vehicle_ID']}`")
        st.markdown(f"**Architecture Class:** {current_test['Vehicle_Type']}")
        
        if current_test['Vehicle_Type'] == 'ICE':
            st.markdown("---")
            st.markdown("**Hardware Scan Status: Gas Analyzer & OBD Diagnostics**")
            st.metric(label="Physical NOx Concentration", value=f"{current_test['NOx_Emissions']:.1f} ppm")
            
            if current_test['NOx_Emissions'] > 150:
                st.error("🚨 **VERDICT: FAIL (Emissions Tampering)**\n\nPhysical readings violate OBD digital logs. Illegal ECU override/AdBlue deletion software mapped in engine controllers.")
            else:
                st.success("✅ **VERDICT: PASS**\n\nExhaust toxicity footprints are safely below regional regulatory baselines.")
        else:
            st.markdown("---")
            st.markdown("**Hardware Scan Status: High-Voltage Bus Isolation Grid**")
            st.metric(label="Insulation Resistance", value=f"{current_test['Insulation_Resistance_M_Ohm']:.1f} MΩ")
            
            if current_test['Insulation_Resistance_M_Ohm'] < 100:
                st.error("🚨 **VERDICT: FAIL (HV Safety Hazard)**\n\nSignificant dielectric barrier degradation detected. Substantial thermal runaway or chassis electrification risk.")
            else:
                st.success("✅ **VERDICT: PASS**\n\nHigh-voltage pack containment integrity and structural insulation benchmarks verified successfully.")