import streamlit as st
import pandas as pd
import numpy as np
import os

st.set_page_config(layout="wide", page_title="National Digital Twin Pipeline")

def safe_rerun():
    if hasattr(st, "rerun"):
        st.rerun()
    else:
        st.experimental_rerun()

# ====================================================================
# MASTER DATASET GENERATOR
# ====================================================================
DATASET_PATH = "national_traffic_db.csv"

@st.cache_data
def generate_national_master_dataset():
    if not os.path.exists(DATASET_PATH):
        np.random.seed(2026)
        n_records = 1000
        
        vehicle_ids = [f"TR-{np.random.randint(10,81)}{np.random.choice(['A','B','C'])}{np.random.choice(['A','B','C'])}{np.random.randint(100,999)}" for _ in range(n_records)]
        vehicle_types = np.random.choice(['ICE', 'EV', 'Heavy_Duty'], size=n_records, p=[0.60, 0.25, 0.15])
        ages = np.random.randint(1, 15, size=n_records)
        cities = np.random.choice(['Istanbul', 'Ankara', 'Izmir', 'Bursa', 'Antalya'], size=n_records)
        hgs_gantry_zones = [f"Gantry-{city[:3].upper()}-{np.random.randint(1,5)}" for city in cities]
        months_since_last_inspection = np.random.randint(1, 36, size=n_records)
        has_chassis_accident = np.random.choice([True, False], size=n_records, p=[0.15, 0.85])
        past_inspection_km = np.random.randint(15000, 220000, size=n_records)
        hgs_monthly_gantry_hits = np.random.randint(8, 150, size=n_records)
        hgs_est_total_km = past_inspection_km + (hgs_monthly_gantry_hits * months_since_last_inspection * 15)
        
        live_nox = []
        live_isolation = []
        ai_failure_risk = []
        
        for i in range(n_records):
            v_type = vehicle_types[i]
            age = ages[i]
            accident = has_chassis_accident[i]
            km = hgs_est_total_km[i]
            months = months_since_last_inspection[i]
            
            base_risk = (age * 2.5) + (km / 8500) + (months * 0.9)
            if accident: base_risk += 40.0
            
            if v_type == 'ICE':
                nox = 40.0 + (age * 5) + (km / 4000)
                if accident: nox += 80.0
                live_nox.append(round(nox, 1))
                live_isolation.append(np.nan)
            elif v_type == 'Heavy_Duty':
                nox_hd = 90.0 + (age * 12) + (km / 2000)
                if accident: nox_hd += 180.0
                live_nox.append(round(nox_hd, 1))
                live_isolation.append(np.nan)
                base_risk += 12.0
            else:
                isolation = 750.0 - (age * 18) - (km / 2500)
                if accident: isolation = float(np.random.randint(15, 65))
                live_isolation.append(round(max(isolation, 12.0), 1))
                live_nox.append(np.nan)
                
            ai_failure_risk.append(round(min(base_risk, 99.5), 1))

        df = pd.DataFrame({
            'Vehicle_ID': vehicle_ids, 'Vehicle_Class': vehicle_types, 'Age_Years': ages,
            'Current_City': cities, 'HGS_Gantry_Zone': hgs_gantry_zones,
            'Last_Inspection_KM': past_inspection_km, 'Months_Since_Last_Inspection': months_since_last_inspection,
            'HGS_Est_Total_KM': hgs_est_total_km, 'Major_Chassis_Accident': has_chassis_accident,
            'AI_Calculated_Risk_Pct': ai_failure_risk, 'Measured_NOx_ppm': live_nox,
            'Measured_Isolation_M_Ohm': live_isolation
        })
        df.to_csv(DATASET_PATH, index=False)

generate_national_master_dataset()
df_national_master = pd.read_csv(DATASET_PATH)

# Regional Capacities
if 'station_capacities' not in st.session_state:
    st.session_state.station_capacities = {
        'Istanbul_Central': {'Status': 'CRITICAL', 'Load': '92%', 'Base_Fee': '$90', 'Promo': '0%'},
        'Ankara_Hub': {'Status': 'BALANCED', 'Load': '54%', 'Base_Fee': '$85', 'Promo': '15%'},
        'Izmir_West': {'Status': 'OPTIMAL', 'Load': '31%', 'Base_Fee': '$80', 'Promo': '25%'},
        'Bursa_East': {'Status': 'BALANCED', 'Load': '62%', 'Base_Fee': '$85', 'Promo': '10%'},
        'Antalya_South': {'Status': 'OPTIMAL', 'Load': '24%', 'Base_Fee': '$75', 'Promo': '30%'}
    }

if 'pointer' not in st.session_state: st.session_state.pointer = 0
if 'network_intercept_logs' not in st.session_state: st.session_state.network_intercept_logs = []

# ====================================================================
# UI DESIGN
# ====================================================================
st.markdown("<h2 style='text-align: center; color: #1E3A8A;'>🌐 National Cyber-Physical Transportation & Inspection Twin</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #555;'>Macro Network Load-Balancing, Dynamic Toll Incentives, and Risk-Based Predictive Recalls</p>", unsafe_allow_html=True)
st.divider()

col_left, col_right = st.columns([1.5, 1.5], gap="large")

# --------------------------------------------------------------------
# SOL SÜTUN: HGS AKIŞI VE AKILLI YÖNLENDİRME
# --------------------------------------------------------------------
with col_left:
    st.markdown("### 🛣️ 1. National Highway Gantry Stream & AI Routing Engine")
    st.caption("Processes vehicle batches passing through various cities. Uses predictive risk modeling and real-time station load maps to route traffic dynamically away from bottleneck points.")
    
    if st.button("📡 Scan National Highway Traffic (Process Next Fleet)", type="primary", use_container_width=True):
        start = st.session_state.pointer
        end = start + 6
        batch = df_national_master.iloc[start:end]
        st.session_state.pointer = end if end < len(df_national_master) else 0
        
        for _, car in batch.iterrows():
            v_id = car['Vehicle_ID']
            v_class = car['Vehicle_Class']
            city = car['Current_City']
            risk = car['AI_Calculated_Risk_Pct']
            months = car['Months_Since_Last_Inspection']
            
            target_station = f"{city}_Central" if city in ['Istanbul', 'Ankara'] else (f"{city}_West" if city=='Izmir' else (f"{city}_East" if city=='Bursa' else f"{city}_South"))
            station_info = st.session_state.station_capacities.get(target_station, {'Status': 'BALANCED', 'Promo': '10%'})
            
            if months > 24:
                directive = "🔴 EXPIRED: Citation issued via HGS."
            elif risk > 75.0:
                directive = f"🚨 PREDICTIVE RECALL: Risk {risk}%! Diverted."
            elif station_info['Status'] == 'CRITICAL':
                directive = f"🔀 REROUTED: Station full. Sent to alternative zone with {station_info['Promo']} discount."
            else:
                directive = "✅ COMPLIANT: Cleared on transit grid."
                
            st.session_state.network_intercept_logs.insert(0, {
                "Plate ID": v_id,
                "Class": v_class,
                "Location": f"{city}",
                "HGS KM": f"{car['HGS_Est_Total_KM']:,} KM",
                "Crash": "Yes" if car['Major_Chassis_Accident'] else "No",
                "Risk": f"{risk}%",
                "Twin Action": directive
            })
        safe_rerun()

    if st.session_state.network_intercept_logs:
        st.dataframe(pd.DataFrame(st.session_state.network_intercept_logs).head(5), use_container_width=True, hide_index=True)
    else:
        st.code("Distributed highway infrastructure online. Awaiting data ingestion...", language="markdown")

    st.write("---")
    st.markdown("#### 🏢 Cross-Regional Facility Capacities")
    capacity_df = pd.DataFrame.from_dict(st.session_state.station_capacities, orient='index').reset_index().rename(columns={'index': 'Station Node'})
    st.table(capacity_df)

# --------------------------------------------------------------------
# SAĞ SÜTUN: YÜKSEK RİSKLİ ARAÇLAR MÜDAHALE PANELİ VE SENSÖR ODASI
# --------------------------------------------------------------------
with col_right:
    st.markdown("### ⚠️ 2. High-Risk Vehicle Intervention Room")
    st.caption("Filters live vehicle registries from the dataset with crashes, heavy mileage, and dynamic failure/fire risk > 75%.")
    
    # Filter vehicles with risk > 75%
    high_risk_fleet = df_national_master[df_national_master['AI_Calculated_Risk_Pct'] > 75.0].head(5)
    
    display_risk_df = high_risk_fleet[['Vehicle_ID', 'Vehicle_Class', 'HGS_Est_Total_KM', 'Major_Chassis_Accident', 'AI_Calculated_Risk_Pct']]
    st.dataframe(display_risk_df, use_container_width=True, hide_index=True)
    
    # Dropdown plate selector
    selected_target = st.selectbox("🎯 Select a High-Risk Vehicle Plate to Intervene:", high_risk_fleet['Vehicle_ID'].tolist())
    
    c1, c2 = st.columns(2)
    with c1:
        if st.button("✉️ Send Compulsory Emergency SMS", use_container_width=True):
            st.toast(f"SMS Sent to {selected_target}: 'Critical technical anomaly predicted. Book inspection within 48h to prevent registration suspension!'", icon="✉️")
    with c2:
        if st.button("🛑 Lock HGS Gantry / Issue Fine", use_container_width=True):
            st.toast(f"HGS Blacklist Active for {selected_target}! Automated fine logged at next highway toll.", icon="🚨")

    st.write("---")
    
    # DIAGNOSTIC TESTING CELL
    st.markdown("### 🔬 3. National Diagnostic Validation Grid")
    if st.button("🧪 Pull Selected High-Risk Unit into Hardware Scanner", use_container_width=True):
        test_car = df_national_master[df_national_master['Vehicle_ID'] == selected_target].iloc[0]
        
        st.markdown(f"**Inspecting Asset:** `{test_car['Vehicle_ID']}` | **Class:** {test_car['Vehicle_Class']} | **Risk Index:** {test_car['AI_Calculated_Risk_Pct']}%")
        
        if test_car['Vehicle_Class'] in ['ICE', 'Heavy_Duty']:
            st.markdown("**Sensor Output: Gas Chromatography Diagnostics**")
            st.metric(label="LIVE NOx EMISSIONS", value=f"{test_car['Measured_NOx_ppm']} ppm", help="Binek Limit: 150 ppm, Heavy Duty: 300 ppm")
            if test_car['Measured_NOx_ppm'] > 150.0:
                st.error("🚨 **VERDICT: CRITICAL FAIL (Euro 6 Violation)**\n\nHigh mileage/accident strains caused catalyst poisoning or software bypass detection.")
            else:
                st.success("✅ **VERDICT: PASS**")
        else: # EV
            st.markdown("**Sensor Output: ECE-R100 Isolation Ohmmeter Scan**")
            st.metric(label="LIVE PACK DIELECTRIC RESISTANCE", value=f"{test_car['Measured_Isolation_M_Ohm']} MΩ", help="Danger Threshold: < 100.0 MΩ")
            if test_car['Measured_Isolation_M_Ohm'] < 100.0:
                st.error("🚨 **VERDICT: EMERGENCY SAFETY FAIL (High Thermal Runaway Risk)**\n\nECE-R100 isolation parameters breached due to structural chassis accident.")
            else:
                st.success("✅ **VERDICT: PASS**")