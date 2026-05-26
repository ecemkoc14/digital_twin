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
# SOLUTION 1: COMPREHENSIVE NATIONAL MASTER DATASET GENERATOR
# ====================================================================
DATASET_PATH = "national_traffic_db.csv"

@st.cache_data
def generate_national_master_dataset():
    """Generates a rich, legally grounded national vehicle registry database."""
    if not os.path.exists(DATASET_PATH):
        np.random.seed(2026)  # Standardized simulation seed
        n_records = 2000
        
        # 1. Identity & Structural Tags
        vehicle_ids = [f"TR-{np.random.randint(10,81)}{np.random.choice(['A','B','C'])}{np.random.choice(['A','B','C'])}{np.random.randint(100,999)}" for _ in range(n_records)]
        vehicle_types = np.random.choice(['ICE', 'EV', 'Heavy_Duty'], size=n_records, p=[0.60, 0.25, 0.15])
        ages = np.random.randint(1, 15, size=n_records)
        
        # 2. Geo-Location & Routing Infrastructure
        cities = np.random.choice(['Istanbul', 'Ankara', 'Izmir', 'Bursa', 'Antalya'], size=n_records)
        hgs_gantry_zones = [f"Gantry-{city[:3].upper()}-{np.random.randint(1,5)}" for city in cities]
        
        # 3. Structural Risk & Timeline Factors
        months_since_last_inspection = np.random.randint(1, 36, size=n_records) # >24 months means inspection is legally expired
        has_chassis_accident = np.random.choice([True, False], size=n_records, p=[0.12, 0.88])
        
        # 4. Historical vs HGS Estimated Mileage
        past_inspection_km = np.random.randint(15000, 220000, size=n_records)
        hgs_monthly_gantry_hits = np.random.randint(8, 150, size=n_records)
        # Calculate dynamic estimated total KM using past data and current HGS velocity markers
        hgs_est_total_km = past_inspection_km + (hgs_monthly_gantry_hits * months_since_last_inspection * 15)
        
        # 5. Physics and Safety Parameters based on Euro 6 & ECE-R100
        live_nox = []
        live_isolation = []
        ai_failure_risk = []
        
        for i in range(n_records):
            v_type = vehicle_types[i]
            age = ages[i]
            accident = has_chassis_accident[i]
            km = hgs_est_total_km[i]
            months = months_since_last_inspection[i]
            
            # Formulating Scientific Risk Vectors
            base_risk = (age * 2.2) + (km / 9000) + (months * 0.8)
            if accident: base_risk += 35.0
            
            if v_type == 'ICE':
                nox = 40.0 + (age * 5) + (km / 4000)
                if accident: nox += 80.0
                if months > 24: nox += 50.0 # Poorly maintained
                live_nox.append(round(nox, 1))
                live_isolation.append(np.nan)
                
            elif v_type == 'Heavy_Duty':
                # Commercial trucks generate significantly higher NOx under strain
                nox_hd = 90.0 + (age * 12) + (km / 2000)
                if accident: nox_hd += 180.0
                live_nox.append(round(nox_hd, 1))
                live_isolation.append(np.nan)
                base_risk += 10.0 # Commercial fleets carry higher baseline failure scores
                
            else: # EV Architecture
                isolation = 750.0 - (age * 18) - (km / 2500)
                if accident: 
                    isolation = float(np.random.randint(15, 65)) # ECE-R100 Isolation Breakdown
                    base_risk += 25.0
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

# ====================================================================
# SIMULATED DISTRIBUTED NETWORK STATION CAPACITIES
# ====================================================================
# Digital Twin tracks network capacities across regions to avoid localized queues
if 'station_capacities' not in st.session_state:
    st.session_state.station_capacities = {
        'Istanbul_Central': {'Status': 'CRITICAL', 'Load': '92%', 'Base_Fee': '$90', 'Off_Peak_Discount': '0%'},
        'Ankara_Hub': {'Status': 'BALANCED', 'Load': '54%', 'Base_Fee': '$85', 'Off_Peak_Discount': '15%'},
        'Izmir_West': {'Status': 'OPTIMAL', 'Load': '31%', 'Base_Fee': '$80', 'Off_Peak_Discount': '25% (Promo Active)'},
        'Bursa_East': {'Status': 'BALANCED', 'Load': '62%', 'Base_Fee': '$85', 'Off_Peak_Discount': '10%'},
        'Antalya_South': {'Status': 'OPTIMAL', 'Load': '24%', 'Base_Fee': '$75', 'Off_Peak_Discount': '30% (Promo Active)'}
    }

if 'pointer' not in st.session_state: st.session_state.pointer = 0
if 'network_intercept_logs' not in st.session_state: st.session_state.network_intercept_logs = []
if 'total_diverted_incentives' not in st.session_state: st.session_state.total_diverted_incentives = 0

# ====================================================================
# UI DESIGN - MACRO DISTRIBUTED TWIN OPERATION ROOM
# ====================================================================
st.markdown("<h2 style='text-align: center; color: #1E3A8A;'>🌐 National Cyber-Physical Transportation & Inspection Twin</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #555;'>Macro Network Load-Balancing, Dynamic Toll Incentives, and Risk-Based Predictive Recalls</p>", unsafe_allow_html=True)
st.divider()

# Left-Right Flow Layout
col_left, col_right = st.columns([1.6, 1.4], gap="large")

# --------------------------------------------------------------------
# LEFT SIDE: REGIONAL TRAFFIC INTERCEPTION & DYNAMIC INCENTIVE ROUTING
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
            
            # Fetch target city's localized station status
            target_station = f"{city}_Central" if city in ['Istanbul', 'Ankara'] else (f"{city}_West" if city=='Izmir' else (f"{city}_East" if city=='Bursa' else f"{city}_South"))
            station_info = st.session_state.station_capacities.get(target_station, {'Status': 'BALANCED', 'Off_Peak_Discount': '10%'})
            
            # CORE DIGITAL TWIN LOAD-BALANCING ALGORITHM
            if months > 24:
                # Legal Enforcements
                directive = "🔴 EXPIRED DEADLINE: Automated citation issued. Booking lock applied."
            elif risk > 75.0 and months > 11:
                # Scientific Predictive Recall
                directive = f"🚨 PREDICTIVE SAFETY RECALL: Risk {risk}% due to structural crash history. Diverted immediately."
                st.session_state.total_diverted_incentives += 1
            elif station_info['Status'] == 'CRITICAL':
                # Network Load-Balancing Optimization
                directive = f"🔀 BOTTLENECK ROUTING: {city} Center is full. Rerouted to adjacent off-peak slot for {station_info['Off_Peak_Discount']} price reduction."
                st.session_state.total_diverted_incentives += 1
            else:
                directive = "✅ SYSTEM COMPLIANT: Vehicle cleared on national transit grid."
                
            st.session_state.network_intercept_logs.insert(0, {
                "Plate ID": v_id,
                "Class": v_class,
                "HGS Location": f"{city} ({car['HGS_Gantry_Zone']})",
                "HGS Est. Mileage": f"{car['HGS_Est_Total_KM']:,} KM",
                "Chassis Crash": "Yes" if car['Major_Chassis_Accident'] else "No",
                "Months Active": months,
                "Failure Risk": f"{risk}%",
                "Twin System Action": directive
            })
        safe_rerun()

    st.markdown("**Real-Time Distributed Ingestion Feed:**")
    if st.session_state.network_intercept_logs:
        st.dataframe(pd.DataFrame(st.session_state.network_intercept_logs).head(6), use_container_width=True, hide_index=True)
    else:
        st.code("Distributed highway infrastructure online. Awaiting data ingestion...", language="markdown")

# --------------------------------------------------------------------
# RIGHT SIDE: NATIONAL STATION LOAD REGISTRY & SIMULATED SENSOR CHAMBER
# --------------------------------------------------------------------
with col_right:
    st.markdown("### 🏢 2. Cross-Regional Facility Capacities")
    st.caption("Live operational load conditions of distributed state inspection facilities monitored by the Twin.")
    
    # Render regional grid map data
    capacity_df = pd.DataFrame.from_dict(st.session_state.station_capacities, orient='index').reset_index().rename(columns={'index': 'Station Node'})
    st.table(capacity_df)
    
    st.metric(label="Total Network Balances / Incentives Distributed", value=f"{st.session_state.total_diverted_incentives} Actions", delta="Throughput Optimization Efficiency")
    
    st.divider()
    
    # ----------------------------------------------------------------
    # HARDWARE DIAGNOSTICS CELL
    # ----------------------------------------------------------------
    st.markdown("### 🔬 3. National Diagnostic Validation Grid")
    st.caption("Pulls a specific high-risk vehicle flagged by the national HGS routing network into a hardware validation bay.")
    
    if st.button("🧪 Sample High-Scrutiny Unit for Physical Verification", use_container_width=True):
        # Sample directly from our custom database to verify the scientific data integrity
        test_car = df_national_master.sample(1).iloc[0]
        
        st.markdown(f"**Inspecting Asset:** `{test_car['Vehicle_ID']}` | **Class:** {test_car['Vehicle_Class']} | **Risk Index:** {test_car['AI_Calculated_Risk_Pct']}%")
        st.write(f"• Registry Origin: `{test_car['Current_City']}` | Historical Crash Record: `{test_car['Major_Chassis_Accident']}`")
        st.write("---")
        
        if test_car['Vehicle_Class'] in ['ICE', 'Heavy_Duty']:
            st.markdown("**Sensor Diagnostic Output: Gas Chromatography Diagnostics**")
            st.metric(label="LIVE NOx EMISSIONS", value=f"{test_car['Measured_NOx_ppm']} ppm", help="Standard Binek Limit: 150 ppm, Heavy Duty Limit: 300 ppm")
            
            if test_car['Vehicle_Class'] == 'Heavy_Duty' and test_car['Measured_NOx_ppm'] > 300.0:
                st.error("🚨 **VERDICT: FAIL (Commercial Fleet Emission Violation)**\n\nHeavy Duty catalytic reduction unit is poisoned or SCR urea line is mechanically severed due to historical kaza/km strains.")
            elif test_car['Vehicle_Class'] == 'ICE' and test_car['Measured_NOx_ppm'] > 150.0:
                st.error("🚨 **VERDICT: FAIL (Euro 6 Violation)**\n\nBenek catalyst failure or defeat chip detected.")
            else:
                st.success("✅ **VERDICT: PASS**\n\nExhaust toxicity footprints comply with environmental thresholds.")
                
        else: # EV Class
            st.markdown("**Sensor Diagnostic Output: ECE-R100 Isolation Ohmmeter Scan**")
            st.metric(label="LIVE PACK DIELECTRIC RESISTANCE", value=f"{test_car['Measured_Isolation_M_Ohm']} MΩ", help="Regulatory Danger Threshold: < 100.0 MΩ")
            
            if test_car['Measured_Isolation_M_Ohm'] < 100.0:
                st.error("🚨 **VERDICT: EMERGENCY SAFETY FAIL (High Thermal Runaway Risk)**\n\nECE-R100 isolation parameters breached. Historical chassis crash profile has compromised internal cell envelope sealing.")
            else:
                st.success("✅ **VERDICT: PASS**\n\nHigh-voltage pack structural insulation parameters secure.")