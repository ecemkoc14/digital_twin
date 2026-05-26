import streamlit as st
import pandas as pd
import numpy as np
import os
import datetime
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ====================================================================
# PAGE CONFIG
# ====================================================================
st.set_page_config(
    layout="wide",
    page_title="National Cyber-Physical Transportation Twin",
    page_icon="🌐",
    initial_sidebar_state="expanded"
)

# ====================================================================
# GLOBAL CSS — Sleek Dark Cyber Aesthetic
# ====================================================================
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@400;600;800&display=swap');

  html, body, [class*="css"] {
      font-family: 'Syne', sans-serif;
      background-color: #060B14;
      color: #CBD5E1;
  }

  section[data-testid="stSidebar"] {
      background: linear-gradient(180deg, #0A1628 0%, #060B14 100%);
      border-right: 1px solid #1E3A5F;
  }

  h1, h2, h3, h4 { font-family: 'Syne', sans-serif !important; }

  [data-testid="stMetric"] {
      background: linear-gradient(135deg, #0F1E35 0%, #0A1628 100%);
      border: 1px solid #1E3A5F;
      border-radius: 12px;
      padding: 16px !important;
  }
  [data-testid="stMetricValue"] {
      font-family: 'Space Mono', monospace !important;
      font-size: 1.6rem !important;
      color: #38BDF8 !important;
  }
  [data-testid="stMetricLabel"] { color: #64748B !important; font-size: 0.75rem !important; }
  [data-testid="stMetricDelta"] { font-family: 'Space Mono', monospace !important; }

  [data-testid="stDataFrame"] {
      border: 1px solid #1E3A5F;
      border-radius: 8px;
      overflow: hidden;
  }

  .stButton > button {
      font-family: 'Space Mono', monospace !important;
      font-weight: 700;
      letter-spacing: 0.05em;
      border-radius: 6px !important;
      transition: all 0.2s ease;
  }
  .stButton > button[kind="primary"] {
      background: linear-gradient(135deg, #0EA5E9, #2563EB) !important;
      border: none !important;
      box-shadow: 0 0 20px rgba(14,165,233,0.3);
  }
  .stButton > button[kind="primary"]:hover {
      box-shadow: 0 0 30px rgba(14,165,233,0.5);
      transform: translateY(-1px);
  }

  hr { border-color: #1E3A5F !important; }

  .badge-critical { color: #F87171; font-weight: 700; font-family: 'Space Mono', monospace; }
  .badge-warning  { color: #FBBF24; font-weight: 700; font-family: 'Space Mono', monospace; }
  .badge-ok       { color: #34D399; font-weight: 700; font-family: 'Space Mono', monospace; }
  .badge-info     { color: #38BDF8; font-weight: 700; font-family: 'Space Mono', monospace; }

  .section-card {
      background: linear-gradient(135deg, #0F1E35 0%, #0A1628 100%);
      border: 1px solid #1E3A5F;
      border-radius: 14px;
      padding: 20px;
      margin-bottom: 18px;
  }

  .mono { font-family: 'Space Mono', monospace; color: #38BDF8; }

  .audit-entry {
      background: #0A1628;
      border-left: 3px solid #1E3A5F;
      border-radius: 4px;
      padding: 8px 12px;
      margin: 4px 0;
      font-family: 'Space Mono', monospace;
      font-size: 0.72rem;
      color: #64748B;
  }
  .audit-critical { border-left-color: #F87171; color: #FCA5A5; }
  .audit-warning  { border-left-color: #FBBF24; color: #FDE68A; }
  .audit-ok       { border-left-color: #34D399; color: #6EE7B7; }

  .privacy-tag {
      display: inline-block;
      background: #1E3A5F;
      color: #7DD3FC;
      border-radius: 4px;
      padding: 2px 8px;
      font-size: 0.7rem;
      font-family: 'Space Mono', monospace;
      margin: 2px;
  }

  ::-webkit-scrollbar { width: 6px; }
  ::-webkit-scrollbar-track { background: #060B14; }
  ::-webkit-scrollbar-thumb { background: #1E3A5F; border-radius: 3px; }
</style>
""", unsafe_allow_html=True)

# ====================================================================
# HELPERS
# ====================================================================
def safe_rerun():
    if hasattr(st, "rerun"):
        st.rerun()
    else:
        st.experimental_rerun()

def now_ts():
    return datetime.datetime.now().strftime("%H:%M:%S")

def add_audit(message: str, level: str = "info"):
    if 'audit_log' not in st.session_state:
        st.session_state.audit_log = []
    st.session_state.audit_log.insert(0, {
        "ts": now_ts(), "msg": message, "level": level
    })
    st.session_state.audit_log = st.session_state.audit_log[:80]

# ====================================================================
# DATASET
# ====================================================================
DATASET_PATH = "national_traffic_db.csv"

@st.cache_data
def generate_national_master_dataset():
    if os.path.exists(DATASET_PATH):
        return pd.read_csv(DATASET_PATH)

    np.random.seed(2026)
    n = 1000

    vehicle_ids = [
        f"TR-{np.random.randint(10,81)}{np.random.choice(['A','B','C'])}"
        f"{np.random.choice(['A','B','C'])}{np.random.randint(100,999)}"
        for _ in range(n)
    ]
    vehicle_types = np.random.choice(['ICE', 'EV', 'Heavy_Duty'], size=n, p=[0.60, 0.25, 0.15])
    ages           = np.random.randint(1, 15, size=n)
    cities         = np.random.choice(['Istanbul', 'Ankara', 'Izmir', 'Bursa', 'Antalya'], size=n)
    hgs_zones      = [f"Gantry-{c[:3].upper()}-{np.random.randint(1,5)}" for c in cities]
    months_since   = np.random.randint(1, 36, size=n)
    accident       = np.random.choice([True, False], size=n, p=[0.15, 0.85])
    base_km        = np.random.randint(15000, 220000, size=n)
    gantry_hits    = np.random.randint(8, 150, size=n)
    est_km         = base_km + (gantry_hits * months_since * 15)

    live_nox, live_iso, risk_pct, fuel_eff = [], [], [], []

    for i in range(n):
        vt, ag, acc, km, mo = vehicle_types[i], ages[i], accident[i], est_km[i], months_since[i]
        base_risk = (ag * 2.5) + (km / 8500) + (mo * 0.9)
        if acc: base_risk += 40.0

        if vt == 'ICE':
            nox = 40.0 + (ag * 5) + (km / 4000)
            if acc: nox += 80.0
            live_nox.append(round(nox, 1)); live_iso.append(np.nan)
            fuel_eff.append(round(8.5 + ag * 0.3 + (1 if acc else 0), 2))
        elif vt == 'Heavy_Duty':
            nox_hd = 90.0 + (ag * 12) + (km / 2000)
            if acc: nox_hd += 180.0
            live_nox.append(round(nox_hd, 1)); live_iso.append(np.nan)
            base_risk += 12.0
            fuel_eff.append(round(22 + ag * 0.5, 2))
        else:
            iso = 750.0 - (ag * 18) - (km / 2500)
            if acc: iso = float(np.random.randint(15, 65))
            live_nox.append(np.nan)
            live_iso.append(round(max(iso, 12.0), 1))
            fuel_eff.append(round(15 + ag * 0.2, 2))

        risk_pct.append(round(min(base_risk, 99.5), 1))

    df = pd.DataFrame({
        'Vehicle_ID': vehicle_ids, 'Vehicle_Class': vehicle_types, 'Age_Years': ages,
        'Current_City': cities, 'HGS_Gantry_Zone': hgs_zones,
        'Last_Inspection_KM': base_km, 'Months_Since_Last_Inspection': months_since,
        'HGS_Est_Total_KM': est_km, 'Major_Chassis_Accident': accident,
        'AI_Calculated_Risk_Pct': risk_pct, 'Measured_NOx_ppm': live_nox,
        'Measured_Isolation_M_Ohm': live_iso, 'Energy_Consumption': fuel_eff
    })
    df.to_csv(DATASET_PATH, index=False)
    return df

df = generate_national_master_dataset()

# ====================================================================
# SESSION STATE INIT
# ====================================================================
STATION_CAPACITIES_DEFAULT = {
    'Istanbul': {'Status': '🔴 CRITICAL', 'Load_Pct': 92, 'Base_Fee': 90,  'Promo': 0},
    'Ankara':   {'Status': '🟡 BALANCED', 'Load_Pct': 54, 'Base_Fee': 85,  'Promo': 15},
    'Izmir':    {'Status': '🟢 OPTIMAL',  'Load_Pct': 31, 'Base_Fee': 80,  'Promo': 25},
    'Bursa':    {'Status': '🟡 BALANCED', 'Load_Pct': 62, 'Base_Fee': 85,  'Promo': 10},
    'Antalya':  {'Status': '🟢 OPTIMAL',  'Load_Pct': 24, 'Base_Fee': 75,  'Promo': 30},
}

_required_keys = {'Status', 'Load_Pct', 'Base_Fee', 'Promo'}
if (
    'station_capacities' not in st.session_state
    or not isinstance(st.session_state.station_capacities, dict)
    or any(
        not _required_keys.issubset(v.keys())
        for v in st.session_state.station_capacities.values()
    )
):
    st.session_state.station_capacities = STATION_CAPACITIES_DEFAULT

defaults = {
    'pointer': 0,
    'network_intercept_logs': [],
    'audit_log': [],
    'privacy_consents': {},
    'blacklisted': set(),
    'sms_sent': set(),
    'active_tab': 'highway',
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ====================================================================
# SIDEBAR
# ====================================================================
with st.sidebar:
    st.markdown("<h2 style='color:#38BDF8; font-family:Syne,sans-serif; margin-bottom:4px;'>🌐 NCPTT</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color:#475569; font-size:0.72rem; font-family:Space Mono,monospace;'>National Cyber-Physical Transportation Twin v2.1</p>", unsafe_allow_html=True)
    st.divider()

    st.markdown("**System Summary**")
    total      = len(df)
    high_risk  = len(df[df['AI_Calculated_Risk_Pct'] > 75])
    ev_count   = len(df[df['Vehicle_Class'] == 'EV'])
    expired    = len(df[df['Months_Since_Last_Inspection'] > 24])

    st.metric("Total Vehicles", f"{total:,}")
    st.metric("High-Risk Units", f"{high_risk:,}", delta=f"{high_risk/total*100:.1f}% of fleet", delta_color="inverse")
    st.metric("EV Units", f"{ev_count:,}", delta=f"{ev_count/total*100:.1f}%")
    st.metric("Inspection Expired", f"{expired:,}", delta_color="inverse")

    st.divider()
    st.markdown("**Navigation**")
    nav = st.radio("Module", [
        "🛣️ Highway & Routing",
        "⚠️ Intervention Room",
        "🔬 Diagnostic Grid",
        "📊 Analytics Dashboard",
        "🔐 Data Privacy & KVKK",
    ], label_visibility="collapsed")

    st.divider()
    st.markdown("**Blacklist Registry**")
    bl_count = len(st.session_state.blacklisted)
    st.markdown(f"<span class='badge-critical'>{bl_count} vehicles blacklisted</span>", unsafe_allow_html=True)

    if st.session_state.audit_log:
        st.divider()
        st.markdown("**Recent Audit Events**")
        for e in st.session_state.audit_log[:5]:
            css = f"audit-{e['level']}"
            st.markdown(f"<div class='audit-entry {css}'>[{e['ts']}] {e['msg']}</div>", unsafe_allow_html=True)

# ====================================================================
# HEADER
# ====================================================================
st.markdown("""
<div style='text-align:center; padding: 24px 0 8px 0;'>
  <h1 style='font-family:Syne,sans-serif; font-size:2.2rem; font-weight:800;
             background: linear-gradient(90deg, #38BDF8, #818CF8, #34D399);
             -webkit-background-clip: text; -webkit-text-fill-color: transparent;
             margin-bottom:4px;'>
    🌐 National Cyber-Physical Transportation Twin
  </h1>
  <p style='color:#475569; font-family:Space Mono,monospace; font-size:0.78rem; letter-spacing:0.08em;'>
    MACRO NETWORK LOAD-BALANCING · DYNAMIC TOLL INCENTIVES · RISK-BASED PREDICTIVE RECALLS
  </p>
</div>
""", unsafe_allow_html=True)
st.divider()

# ====================================================================
# MODULE 1 — HIGHWAY & ROUTING
# ====================================================================
if nav == "🛣️ Highway & Routing":
    st.markdown("<h3 style='color:#38BDF8;'>🛣️ 1. National Highway Gantry Stream & AI Routing Engine</h3>", unsafe_allow_html=True)
    st.markdown("<p style='color:#64748B; font-size:0.85rem;'>Processes vehicle batches passing through HGS gantry nodes. Predictive risk modeling routes traffic away from overloaded stations dynamically.</p>", unsafe_allow_html=True)

    caps = st.session_state.station_capacities
    k1, k2, k3, k4, k5 = st.columns(5)
    city_cols = [k1, k2, k3, k4, k5]
    for col, (city, info) in zip(city_cols, caps.items()):
        load = info.get('Load_Pct', 50)
        color = "#F87171" if load > 80 else "#FBBF24" if load > 55 else "#34D399"
        col.markdown(f"""
        <div style='background:#0F1E35; border:1px solid #1E3A5F; border-radius:10px;
                    padding:12px 8px; text-align:center; border-top: 3px solid {color};'>
          <div style='font-family:Syne,sans-serif; font-size:0.78rem; color:#94A3B8; margin-bottom:4px;'>{city}</div>
          <div style='font-family:Space Mono,monospace; font-size:1.4rem; color:{color}; font-weight:700;'>{load}%</div>
          <div style='font-size:0.65rem; color:#475569; margin-top:4px;'>${info.get('Base_Fee', 85)} · {info.get('Promo', 0)}% off</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col_scan, col_opts = st.columns([3, 1])
    with col_opts:
        batch_size = st.selectbox("Batch Size", [6, 10, 15, 20], index=0)
        filter_city = st.multiselect("Filter City", list(caps.keys()), default=[])

    with col_scan:
        if st.button("📡 Scan National Highway Traffic (Process Next Fleet)", type="primary", use_container_width=True):
            start = st.session_state.pointer
            end   = start + batch_size
            batch = df.iloc[start:end]
            st.session_state.pointer = end if end < len(df) else 0

            for _, car in batch.iterrows():
                city   = car['Current_City']
                risk   = car['AI_Calculated_Risk_Pct']
                months = car['Months_Since_Last_Inspection']
                info   = caps.get(city, {'Status': '🟡 BALANCED', 'Load_Pct': 50, 'Base_Fee': 85, 'Promo': 10})
                promo  = info.get('Promo', 10)

                if car['Vehicle_ID'] in st.session_state.blacklisted:
                    directive = "🚫 BLACKLISTED: Vehicle flagged — gantry lock enforced."
                    lvl = "critical"
                elif months > 24:
                    directive = "❌ EXPIRED: Citation issued via HGS."
                    lvl = "critical"
                elif risk > 75.0:
                    directive = f"⚠️ RECALL: Risk {risk}%! Diverted to mandatory inspection."
                    lvl = "warning"
                elif info.get('Load_Pct', 50) > 80:
                    directive = f"🔄 REROUTED: Station critical load. {promo}% discount applied."
                    lvl = "warning"
                else:
                    directive = "⚡ COMPLIANT: Cleared on transit grid."
                    lvl = "ok"

                add_audit(f"{car['Vehicle_ID']} [{car['Vehicle_Class']}] {city} → {directive[:40]}", lvl)

                st.session_state.network_intercept_logs.insert(0, {
                    "Plate ID":    car['Vehicle_ID'],
                    "Class":       car['Vehicle_Class'],
                    "City":        city,
                    "Est. KM":     f"{int(car['HGS_Est_Total_KM']):,}",
                    "Accident":    "⚠️ Yes" if car['Major_Chassis_Accident'] else "No",
                    "Risk %":      f"{risk}%",
                    "HGS Action":  directive,
                })
            safe_rerun()

    logs = st.session_state.network_intercept_logs
    if filter_city:
        logs = [l for l in logs if l['City'] in filter_city]

    if logs:
        log_df = pd.DataFrame(logs)
        st.dataframe(log_df.head(12), use_container_width=True, hide_index=True,
                     column_config={
                         "Risk %": st.column_config.TextColumn("Risk %"),
                         "HGS Action": st.column_config.TextColumn("HGS Action", width="large"),
                     })
        c1, c2, c3 = st.columns(3)
        c1.metric("Processed", len(logs))
        c2.metric("Recalled/Expired", sum(1 for l in logs if "RECALL" in l['HGS Action'] or "EXPIRED" in l['HGS Action']))
        c3.metric("Rerouted", sum(1 for l in logs if "REROUTED" in l['HGS Action']))
    else:
        st.code("Distributed highway infrastructure online. Awaiting data ingestion...", language="markdown")

    st.divider()

    st.markdown("<h4 style='color:#E2E8F0;'>🏢 Cross-Regional Facility Capacities</h4>", unsafe_allow_html=True)
    cap_rows = []
    for city, info in caps.items():
        load = info.get('Load_Pct', 50)
        bar_color = "#F87171" if load > 80 else "#FBBF24" if load > 55 else "#34D399"
        cap_rows.append({
            "Station Node":      city,
            "Status":            info.get('Status', '🟡 BALANCED'),
            "Load":              f"{load}%",
            "Base Fee":          f"${info.get('Base_Fee', 85)}",
            "Off-Peak Discount": f"{info.get('Promo', 0)}%",
        })
    st.dataframe(pd.DataFrame(cap_rows), use_container_width=True, hide_index=True)

# ====================================================================
# MODULE 2 — INTERVENTION ROOM
# ====================================================================
elif nav == "⚠️ Intervention Room":
    st.markdown("<h3 style='color:#FBBF24;'>⚠️ 2. High-Risk Vehicle Intervention Room</h3>", unsafe_allow_html=True)
    st.markdown("<p style='color:#64748B; font-size:0.85rem;'>Live vehicle registries filtered by crash history, high mileage, and AI-calculated failure risk > 75%.</p>", unsafe_allow_html=True)

    f1, f2, f3 = st.columns(3)
    with f1: risk_threshold = st.slider("Risk Threshold %", 50, 99, 75)
    with f2: filter_class   = st.multiselect("Vehicle Class", ['ICE', 'EV', 'Heavy_Duty'], default=['ICE','EV','Heavy_Duty'])
    with f3: crash_only     = st.checkbox("Crash History Only", value=False)

    fleet = df[df['AI_Calculated_Risk_Pct'] > risk_threshold]
    if filter_class: fleet = fleet[fleet['Vehicle_Class'].isin(filter_class)]
    if crash_only:   fleet = fleet[fleet['Major_Chassis_Accident'] == True]
    fleet = fleet.sort_values('AI_Calculated_Risk_Pct', ascending=False).head(20)

    st.markdown(f"<p style='color:#FBBF24; font-family:Space Mono,monospace; font-size:0.8rem;'>⚡ {len(fleet)} units match intervention criteria</p>", unsafe_allow_html=True)

    display_cols = ['Vehicle_ID', 'Vehicle_Class', 'Current_City', 'HGS_Est_Total_KM',
                    'Months_Since_Last_Inspection', 'Major_Chassis_Accident', 'AI_Calculated_Risk_Pct']
    st.dataframe(
        fleet[display_cols],
        use_container_width=True, hide_index=True,
        column_config={
            "AI_Calculated_Risk_Pct": st.column_config.ProgressColumn(
                "Risk %", format="%.1f%%", min_value=0, max_value=100
            ),
            "HGS_Est_Total_KM": st.column_config.NumberColumn("Est. KM", format="%d km"),
            "Major_Chassis_Accident": st.column_config.CheckboxColumn("Crash"),
        }
    )

    st.divider()
    selected_target = st.selectbox("🎯 Select Vehicle for Intervention:", fleet['Vehicle_ID'].tolist())

    if selected_target:
        car = df[df['Vehicle_ID'] == selected_target].iloc[0]
        risk_color = "#F87171" if car['AI_Calculated_Risk_Pct'] > 75 else "#FBBF24"

        st.markdown(f"""
        <div class='section-card'>
          <div style='display:flex; gap:24px; flex-wrap:wrap;'>
            <div><div style='color:#475569;font-size:0.7rem;'>PLATE</div>
                 <div class='mono' style='font-size:1.1rem;'>{car['Vehicle_ID']}</div></div>
            <div><div style='color:#475569;font-size:0.7rem;'>CLASS</div>
                 <div style='color:#818CF8;font-weight:700;'>{car['Vehicle_Class']}</div></div>
            <div><div style='color:#475569;font-size:0.7rem;'>CITY</div>
                 <div style='color:#E2E8F0;'>{car['Current_City']}</div></div>
            <div><div style='color:#475569;font-size:0.7rem;'>AGE</div>
                 <div style='color:#E2E8F0;'>{car['Age_Years']} yr</div></div>
            <div><div style='color:#475569;font-size:0.7rem;'>EST. KM</div>
                 <div style='color:#E2E8F0;'>{int(car['HGS_Est_Total_KM']):,}</div></div>
            <div><div style='color:#475569;font-size:0.7rem;'>RISK INDEX</div>
                 <div style='color:{risk_color};font-family:Space Mono,monospace;font-size:1.1rem;font-weight:700;'>
                 {car['AI_Calculated_Risk_Pct']}%</div></div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        ca, cb, cc = st.columns(3)
        with ca:
            if st.button("✉️ Send Emergency SMS", use_container_width=True):
                st.session_state.sms_sent.add(selected_target)
                add_audit(f"SMS dispatched → {selected_target} ({car['Current_City']})", "warning")
                st.toast(f"SMS sent to {selected_target}: 'Critical anomaly predicted. Book inspection within 48h!'", icon="✉️")
        with cb:
            if st.button("🚫 Lock HGS Gantry / Issue Fine", use_container_width=True):
                st.session_state.blacklisted.add(selected_target)
                add_audit(f"HGS LOCK activated → {selected_target}", "critical")
                st.toast(f"HGS Blacklist active for {selected_target}! Fine logged.", icon="🚨")
        with cc:
            if st.button("📋 Generate Intervention Report", use_container_width=True):
                add_audit(f"Intervention report generated → {selected_target}", "info")
                st.toast(f"PDF report queued for {selected_target}", icon="📋")

        if selected_target in st.session_state.blacklisted:
            st.error("🚫 This vehicle is currently BLACKLISTED. HGS gantry lock is active.")
        if selected_target in st.session_state.sms_sent:
            st.warning("✉️ Emergency SMS has been sent to this vehicle's registered owner.")

# ====================================================================
# MODULE 3 — DIAGNOSTIC GRID
# ====================================================================
elif nav == "🔬 Diagnostic Grid":
    st.markdown("<h3 style='color:#34D399;'>🔬 3. National Diagnostic Validation Grid</h3>", unsafe_allow_html=True)

    high_risk_fleet = df[df['AI_Calculated_Risk_Pct'] > 75].sort_values('AI_Calculated_Risk_Pct', ascending=False)
    selected_target = st.selectbox("🎯 Select High-Risk Unit:", high_risk_fleet['Vehicle_ID'].tolist())

    if st.button("🧪 Pull Unit into Hardware Scanner", type="primary", use_container_width=True):
        car = df[df['Vehicle_ID'] == selected_target].iloc[0]

        st.markdown(f"""
        <div class='section-card' style='border-top:3px solid #34D399;'>
          <div style='font-family:Space Mono,monospace; color:#64748B; font-size:0.7rem; margin-bottom:8px;'>
            ASSET INSPECTION REPORT · {now_ts()} UTC
          </div>
          <div style='display:flex; gap:24px; flex-wrap:wrap; margin-bottom:16px;'>
            <div><span style='color:#475569;font-size:0.7rem;'>VEHICLE ID</span><br>
                 <span class='mono' style='font-size:1rem;'>{car['Vehicle_ID']}</span></div>
            <div><span style='color:#475569;font-size:0.7rem;'>CLASS</span><br>
                 <span style='color:#818CF8;font-weight:700;'>{car['Vehicle_Class']}</span></div>
            <div><span style='color:#475569;font-size:0.7rem;'>RISK INDEX</span><br>
                 <span style='color:#F87171;font-family:Space Mono,monospace;font-weight:700;'>{car['AI_Calculated_Risk_Pct']}%</span></div>
            <div><span style='color:#475569;font-size:0.7rem;'>AGE / KM</span><br>
                 <span style='color:#E2E8F0;'>{car['Age_Years']} yr / {int(car['HGS_Est_Total_KM']):,} km</span></div>
            <div><span style='color:#475569;font-size:0.7rem;'>ACCIDENT HISTORY</span><br>
                 <span style='color:{"#F87171" if car["Major_Chassis_Accident"] else "#34D399"};font-weight:700;'>
                 {"⚠️ YES" if car["Major_Chassis_Accident"] else "✅ NO"}</span></div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        if car['Vehicle_Class'] in ['ICE', 'Heavy_Duty']:
            nox = car['Measured_NOx_ppm']
            euro6_limit_ice = 80.0
            euro6_limit_hd  = 460.0
            limit = euro6_limit_ice if car['Vehicle_Class'] == 'ICE' else euro6_limit_hd
            pass_fail = nox <= limit

            st.markdown("<h4 style='color:#94A3B8;'>🧪 Gas Chromatography / FTIR Emissions Diagnostics</h4>", unsafe_allow_html=True)

            m1, m2, m3 = st.columns(3)
            m1.metric("LIVE NOx (ppm)", f"{nox:.1f}", delta=f"{nox - limit:+.1f} vs limit", delta_color="inverse")
            m2.metric("Euro 6 Limit (ppm)", f"{limit:.0f}")
            m3.metric("Exceedance Ratio", f"{nox/limit:.2f}x", delta_color="inverse" if nox > limit else "normal")

            fig = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=nox,
                delta={'reference': limit, 'increasing': {'color': '#F87171'}, 'decreasing': {'color': '#34D399'}},
                gauge={
                    'axis': {'range': [0, max(nox * 1.4, limit * 1.5)], 'tickcolor': '#475569'},
                    'bar': {'color': '#F87171' if not pass_fail else '#34D399'},
                    'steps': [
                        {'range': [0, limit * 0.7],  'color': '#0F2A1A'},
                        {'range': [limit * 0.7, limit], 'color': '#1A2A0A'},
                        {'range': [limit, max(nox * 1.4, limit * 1.5)], 'color': '#2A0F0F'},
                    ],
                    'threshold': {'line': {'color': '#FBBF24', 'width': 3}, 'thickness': 0.8, 'value': limit},
                },
                title={'text': "NOx Emissions (ppm)", 'font': {'color': '#94A3B8'}},
                number={'font': {'color': '#F87171' if not pass_fail else '#34D399', 'family': 'Space Mono'}},
            ))
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                font_color='#94A3B8', height=280, margin=dict(t=40, b=0, l=20, r=20)
            )
            st.plotly_chart(fig, use_container_width=True)

            if not pass_fail:
                st.error(f"""
🚨 **VERDICT: CRITICAL FAIL — Euro 6 Violation**

NOx reading of **{nox:.1f} ppm** exceeds the Euro 6 limit of **{limit:.0f} ppm** by **{nox/limit:.1f}x**.

**Probable Causes:**
- Catalyst poisoning due to high mileage wear ({int(car['HGS_Est_Total_KM']):,} km)
- SCR/DPF system bypass or software manipulation detected
- {'Chassis accident may have damaged exhaust aftertreatment system' if car['Major_Chassis_Accident'] else 'Accelerated engine wear pattern'}

**Required Action:** Mandatory workshop referral · HGS suspension pending repair certificate
                """)
                add_audit(f"EMISSION FAIL {car['Vehicle_ID']}: {nox:.1f}ppm (limit {limit:.0f}ppm)", "critical")
            else:
                st.success(f"✅ **VERDICT: PASS** — NOx {nox:.1f} ppm is within Euro 6 limits ({limit:.0f} ppm).")
                add_audit(f"Emission PASS {car['Vehicle_ID']}: {nox:.1f}ppm", "ok")

            st.markdown("<h5 style='color:#64748B; margin-top:16px;'>Estimated Supplementary Emissions</h5>", unsafe_allow_html=True)
            e1, e2 = st.columns(2)
            e1.metric("Est. CO₂ (g/km)", f"{round(95 + car['Age_Years']*3 + (1 if car['Major_Chassis_Accident'] else 0)*20, 1)}")
            e2.metric("Fuel Efficiency (L/100km)", f"{car['Energy_Consumption']:.1f}")

        else:
            iso   = car['Measured_Isolation_M_Ohm']
            limit = 100.0
            pass_fail = iso >= limit

            st.markdown("<h4 style='color:#94A3B8;'>⚡ ECE-R100 Battery Isolation & Thermal Safety Scan</h4>", unsafe_allow_html=True)

            m1, m2, m3 = st.columns(3)
            m1.metric("Pack Dielectric Resistance", f"{iso:.1f} MΩ", delta=f"{iso - limit:+.1f} vs limit", delta_color="normal" if pass_fail else "inverse")
            m2.metric("ECE-R100 Minimum (MΩ)", f"{limit:.0f}")
            m3.metric("Safety Margin", f"{iso/limit:.2f}x", delta_color="normal" if pass_fail else "inverse")

            fig = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=iso,
                delta={'reference': limit},
                gauge={
                    'axis': {'range': [0, 800], 'tickcolor': '#475569'},
                    'bar': {'color': '#34D399' if pass_fail else '#F87171'},
                    'steps': [
                        {'range': [0, limit], 'color': '#2A0F0F'},
                        {'range': [limit, 300], 'color': '#0F2A1A'},
                        {'range': [300, 800], 'color': '#0A1F2E'},
                    ],
                    'threshold': {'line': {'color': '#FBBF24', 'width': 3}, 'thickness': 0.8, 'value': limit},
                },
                title={'text': "Isolation Resistance (MΩ)", 'font': {'color': '#94A3B8'}},
                number={'font': {'color': '#34D399' if pass_fail else '#F87171', 'family': 'Space Mono'}},
            ))
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                font_color='#94A3B8', height=280, margin=dict(t=40, b=0, l=20, r=20)
            )
            st.plotly_chart(fig, use_container_width=True)

            if not pass_fail:
                st.error(f"""
🚨 **VERDICT: EMERGENCY SAFETY FAIL — ECE-R100 Thermal Runaway Risk**

Isolation resistance **{iso:.1f} MΩ** is critically below the ECE-R100 minimum of **{limit:.0f} MΩ**.

**Probable Causes:**
- {'Structural chassis accident caused battery pack deformation' if car['Major_Chassis_Accident'] else 'Cell degradation from high cycle count'}
- Electrolyte leakage compromising dielectric properties
- BMS failure or ground fault in HV circuit

**Required Action:** Immediate immobilisation · Battery pack forensic inspection required · Fire risk classified HIGH
                """)
                add_audit(f"EV ISOLATION FAIL {car['Vehicle_ID']}: {iso:.1f}MΩ", "critical")
            else:
                st.success(f"✅ **VERDICT: PASS** — Isolation {iso:.1f} MΩ exceeds ECE-R100 minimum ({limit:.0f} MΩ).")
                add_audit(f"EV Isolation PASS {car['Vehicle_ID']}: {iso:.1f}MΩ", "ok")

            st.markdown("<h5 style='color:#64748B; margin-top:16px;'>Battery Health Indicators</h5>", unsafe_allow_html=True)
            e1, e2, e3 = st.columns(3)
            soh = max(20, round(100 - car['Age_Years'] * 3.5 - (20 if car['Major_Chassis_Accident'] else 0), 1))
            e1.metric("Est. Battery SoH %", f"{soh}%", delta_color="normal" if soh > 70 else "inverse")
            e2.metric("Energy Usage (kWh/100km)", f"{car['Energy_Consumption']:.1f}")
            e3.metric("Thermal Risk Level", "HIGH 🔴" if not pass_fail else ("MED 🟡" if soh < 70 else "LOW 🟢"))

# ====================================================================
# MODULE 4 — ANALYTICS DASHBOARD
# ====================================================================
elif nav == "📊 Analytics Dashboard":
    st.markdown("<h3 style='color:#818CF8;'>📊 4. Fleet Analytics Dashboard</h3>", unsafe_allow_html=True)

    t1, t2 = st.tabs(["Fleet Overview", "Emissions & Risk Analysis"])

    with t1:
        r1c1, r1c2, r1c3, r1c4 = st.columns(4)
        r1c1.metric("Total Fleet",      f"{len(df):,}")
        r1c2.metric("Avg. Risk Score",  f"{df['AI_Calculated_Risk_Pct'].mean():.1f}%")
        r1c3.metric("EV Penetration",   f"{len(df[df['Vehicle_Class']=='EV'])/len(df)*100:.1f}%")
        r1c4.metric("Expired Insp.",    f"{len(df[df['Months_Since_Last_Inspection']>24]):,}")

        c1, c2 = st.columns(2)

        with c1:
            class_dist = df['Vehicle_Class'].value_counts().reset_index()
            class_dist.columns = ['Class', 'Count']
            fig = px.pie(class_dist, values='Count', names='Class',
                         color_discrete_sequence=['#38BDF8', '#818CF8', '#34D399'],
                         title="Fleet Composition by Vehicle Class")
            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                               font_color='#94A3B8', title_font_color='#E2E8F0')
            st.plotly_chart(fig, use_container_width=True)

        with c2:
            city_risk = df.groupby('Current_City')['AI_Calculated_Risk_Pct'].mean().reset_index()
            city_risk.columns = ['City', 'Avg Risk']
            fig = px.bar(city_risk, x='City', y='Avg Risk',
                         color='Avg Risk', color_continuous_scale=['#34D399','#FBBF24','#F87171'],
                         title="Average Risk Score by City")
            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                               font_color='#94A3B8', title_font_color='#E2E8F0',
                               coloraxis_showscale=False)
            st.plotly_chart(fig, use_container_width=True)

        fig = px.histogram(df, x='AI_Calculated_Risk_Pct', nbins=40,
                           color='Vehicle_Class',
                           color_discrete_map={'ICE':'#38BDF8','EV':'#34D399','Heavy_Duty':'#F87171'},
                           title="AI Risk Score Distribution by Vehicle Class",
                           barmode='overlay', opacity=0.7)
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                           font_color='#94A3B8', title_font_color='#E2E8F0')
        fig.add_vline(x=75, line_dash="dash", line_color="#FBBF24",
                      annotation_text="Intervention Threshold 75%", annotation_font_color="#FBBF24")
        st.plotly_chart(fig, use_container_width=True)

    with t2:
        c1, c2 = st.columns(2)

        with c1:
            ice_hd = df[df['Vehicle_Class'].isin(['ICE','Heavy_Duty'])].dropna(subset=['Measured_NOx_ppm'])
            fig = px.scatter(ice_hd, x='HGS_Est_Total_KM', y='Measured_NOx_ppm',
                             color='Vehicle_Class', size='AI_Calculated_Risk_Pct',
                             color_discrete_map={'ICE':'#38BDF8','Heavy_Duty':'#F87171'},
                             title="NOx vs Mileage (ICE & Heavy Duty)",
                             labels={'HGS_Est_Total_KM':'Est. KM','Measured_NOx_ppm':'NOx (ppm)'})
            fig.add_hline(y=80,  line_dash="dash", line_color="#FBBF24",
                          annotation_text="Euro 6 ICE Limit", annotation_font_color="#FBBF24")
            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                               font_color='#94A3B8', title_font_color='#E2E8F0')
            st.plotly_chart(fig, use_container_width=True)

        with c2:
            ev_df = df[df['Vehicle_Class'] == 'EV'].dropna(subset=['Measured_Isolation_M_Ohm'])
            fig = px.scatter(ev_df, x='Age_Years', y='Measured_Isolation_M_Ohm',
                             color='Major_Chassis_Accident',
                             color_discrete_map={True:'#F87171', False:'#34D399'},
                             title="EV Isolation Resistance vs Age",
                             labels={'Age_Years':'Age (Years)','Measured_Isolation_M_Ohm':'Isolation (MΩ)'})
            fig.add_hline(y=100, line_dash="dash", line_color="#FBBF24",
                          annotation_text="ECE-R100 Minimum", annotation_font_color="#FBBF24")
            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                               font_color='#94A3B8', title_font_color='#E2E8F0')
            st.plotly_chart(fig, use_container_width=True)

        heat_data = df.groupby(['Current_City','Vehicle_Class'])['Months_Since_Last_Inspection'].mean().unstack(fill_value=0)
        fig = px.imshow(heat_data, color_continuous_scale='RdYlGn_r',
                        title="Avg. Months Since Last Inspection (City × Class)")
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                           font_color='#94A3B8', title_font_color='#E2E8F0')
        st.plotly_chart(fig, use_container_width=True)

# ====================================================================
# MODULE 5 — DATA PRIVACY & KVKK
# ====================================================================
elif nav == "🔐 Data Privacy & KVKK":
    st.markdown("<h3 style='color:#A78BFA;'>🔐 5. Data Privacy & KVKK / GDPR Compliance Module</h3>", unsafe_allow_html=True)
    st.markdown("<p style='color:#64748B; font-size:0.85rem;'>Responsible data governance framework for the national vehicle inspection digital twin. Aligned with KVKK (Law No. 6698) and GDPR principles.</p>", unsafe_allow_html=True)

    st.markdown("<h4 style='color:#E2E8F0; margin-top:24px;'>📂 Data Classification Registry</h4>", unsafe_allow_html=True)
    classification_data = [
        {"Data Field": "Vehicle_ID (Plate)",    "Category": "Personal Data",    "KVKK Class": "Art. 6 General",   "Retention": "5 years", "Masked": "Yes", "Justification": "Traffic safety enforcement"},
        {"Data Field": "HGS_Est_Total_KM",      "Category": "Behavioural",      "KVKK Class": "Art. 6 General",   "Retention": "3 years", "Masked": "No",  "Justification": "Inspection risk modelling"},
        {"Data Field": "Major_Chassis_Accident","Category": "Vehicle Record",    "KVKK Class": "Art. 6 General",   "Retention": "10 years","Masked": "No",  "Justification": "Legal obligation"},
        {"Data Field": "Measured_NOx_ppm",      "Category": "Technical/Env",     "KVKK Class": "Anonymous",        "Retention": "7 years", "Masked": "N/A", "Justification": "Environmental regulation"},
        {"Data Field": "Measured_Isolation_MΩ", "Category": "Technical/Safety",  "KVKK Class": "Anonymous",        "Retention": "7 years", "Masked": "N/A", "Justification": "EV safety regulation"},
        {"Data Field": "AI_Calculated_Risk_Pct","Category": "Derived/Profiling", "KVKK Class": "Art. 11 — Rights", "Retention": "2 years", "Masked": "Yes", "Justification": "Algorithmic accountability"},
        {"Data Field": "Current_City",          "Category": "Location",          "KVKK Class": "Art. 6 General",   "Retention": "1 year",  "Masked": "Yes", "Justification": "Station load balancing"},
        {"Data Field": "HGS_Gantry_Zone",       "Category": "Location Tracking", "KVKK Class": "Art. 6 Special",   "Retention": "6 months","Masked": "Yes", "Justification": "Network routing only"},
    ]
    st.dataframe(pd.DataFrame(classification_data), use_container_width=True, hide_index=True,
                 column_config={"Masked": st.column_config.TextColumn("Anonymised")})

    st.divider()

    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("<h4 style='color:#E2E8F0;'>✅ Consent Management Simulator</h4>", unsafe_allow_html=True)
        sim_plate = st.text_input("Enter Plate ID to check consent status:", value="TR-12ABC345")
        purposes = {
            "Safety Inspection & Risk Scoring":    True,
            "Cross-City Station Load Balancing":   True,
            "Emissions Data Sharing (Government)": True,
            "AI Profiling for Predictive Recall":  False,
            "Third-Party Analytics Partners":       False,
            "SMS/Communication Notifications":     True,
        }

        st.markdown(f"<p style='color:#475569; font-family:Space Mono,monospace; font-size:0.72rem;'>CONSENT RECORD — {sim_plate}</p>", unsafe_allow_html=True)
        for purpose, default in purposes.items():
            key = f"consent_{sim_plate}_{purpose}"
            if key not in st.session_state:
                st.session_state[key] = default
            val = st.checkbox(purpose, value=st.session_state[key], key=key)

        if st.button("💾 Save Consent Record", use_container_width=True):
            add_audit(f"Consent updated for {sim_plate}", "info")
            st.toast(f"Consent record saved for {sim_plate}", icon="✅")

    with col_b:
        st.markdown("<h4 style='color:#E2E8F0;'>⚖️ Subject Rights (KVKK Art. 11)</h4>", unsafe_allow_html=True)

        rights_plate = st.text_input("Plate for Rights Request:", value="TR-12ABC345", key="rights_plate")
        right_type   = st.selectbox("Request Type:", [
            "📋 Access — View all personal data held",
            "✏️ Rectification — Correct inaccurate data",
            "🗑️ Erasure — Delete personal data (Right to be Forgotten)",
            "📤 Portability — Export data in machine-readable format",
            "🚫 Objection — Object to AI profiling / automated decision-making",
            "⏸️ Restriction — Restrict processing pending dispute",
        ])

        if st.button("📨 Submit Rights Request", use_container_width=True):
            add_audit(f"KVKK Rights Request: {right_type[:30]} → {rights_plate}", "warning")
            st.success(f"Request logged. Reference: KVKK-{abs(hash(rights_plate + right_type)) % 99999:05d}. Response within 30 days per Art. 13.")

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""
        <div style='background:#0F1E35; border:1px solid #1E3A5F; border-radius:10px; padding:16px;'>
          <div style='color:#A78BFA; font-family:Space Mono,monospace; font-size:0.72rem; margin-bottom:8px;'>DATA PROTECTION PRINCIPLES APPLIED</div>
          <div style='display:flex; flex-wrap:wrap; gap:6px;'>
            <span class='privacy-tag'>Lawfulness</span>
            <span class='privacy-tag'>Purpose Limitation</span>
            <span class='privacy-tag'>Data Minimisation</span>
            <span class='privacy-tag'>Accuracy</span>
            <span class='privacy-tag'>Storage Limitation</span>
            <span class='privacy-tag'>Integrity & Confidentiality</span>
            <span class='privacy-tag'>Accountability</span>
            <span class='privacy-tag'>Transparency</span>
          </div>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    st.markdown("<h4 style='color:#E2E8F0;'>🔍 Privacy Risk Assessment (DPIA)</h4>", unsafe_allow_html=True)
    dpia_data = [
        {"Processing Activity": "AI Risk Profiling",        "Risk Level": "🔴 HIGH",   "Mitigation": "Explainability module + human review gate",              "Status": "In Progress"},
        {"Processing Activity": "HGS Location Tracking",    "Risk Level": "🟡 MEDIUM", "Mitigation": "Gantry-zone aggregation only, no GPS coordinates",        "Status": "Implemented"},
        {"Processing Activity": "SMS Dispatch",             "Risk Level": "🟡 MEDIUM", "Mitigation": "Consent-gated, opt-out mechanism in place",               "Status": "Implemented"},
        {"Processing Activity": "Cross-City Data Transfer", "Risk Level": "🟡 MEDIUM", "Mitigation": "TLS 1.3 encryption, anonymised station IDs",              "Status": "Implemented"},
        {"Processing Activity": "Third-Party Analytics",    "Risk Level": "🔴 HIGH",   "Mitigation": "Explicit opt-in consent required, DPA required",           "Status": "Pending"},
        {"Processing Activity": "Long-term KM Retention",   "Risk Level": "🟢 LOW",    "Mitigation": "Aggregated only after retention period, k-anonymity applied","Status": "Implemented"},
    ]
    st.dataframe(pd.DataFrame(dpia_data), use_container_width=True, hide_index=True)

    st.divider()

    st.markdown("<h4 style='color:#E2E8F0;'>🤖 AI Model Card — Risk Scoring Engine</h4>", unsafe_allow_html=True)
    mc1, mc2 = st.columns(2)
    with mc1:
        st.markdown("""
        <div class='section-card'>
          <div style='color:#A78BFA; font-family:Space Mono,monospace; font-size:0.7rem; margin-bottom:10px;'>MODEL DETAILS</div>
          <table style='width:100%; font-size:0.82rem; border-collapse:collapse;'>
            <tr><td style='color:#64748B; padding:4px 0;'>Model Type</td><td style='color:#E2E8F0;'>Rule-Based + Weighted Scoring</td></tr>
            <tr><td style='color:#64748B; padding:4px 0;'>Input Features</td><td style='color:#E2E8F0;'>Age, KM, Accident, Months, Class</td></tr>
            <tr><td style='color:#64748B; padding:4px 0;'>Output</td><td style='color:#E2E8F0;'>Risk % (0–99.5)</td></tr>
            <tr><td style='color:#64748B; padding:4px 0;'>Intervention Threshold</td><td style='color:#F87171;'>75%</td></tr>
            <tr><td style='color:#64748B; padding:4px 0;'>Data Source</td><td style='color:#E2E8F0;'>HGS + Inspection Registry</td></tr>
            <tr><td style='color:#64748B; padding:4px 0;'>Training Bias Check</td><td style='color:#FBBF24;'>Pending External Audit</td></tr>
            <tr><td style='color:#64748B; padding:4px 0;'>Human Override</td><td style='color:#34D399;'>Yes — all interventions</td></tr>
          </table>
        </div>
        """, unsafe_allow_html=True)
    with mc2:
        st.markdown("""
        <div class='section-card'>
          <div style='color:#F87171; font-family:Space Mono,monospace; font-size:0.7rem; margin-bottom:10px;'>KNOWN LIMITATIONS & RISKS</div>
          <ul style='color:#94A3B8; font-size:0.82rem; padding-left:18px; line-height:1.9;'>
            <li>KM estimates derived from HGS frequency — may underestimate for rural vehicles</li>
            <li>AI scores not causally validated against actual failure rates</li>
            <li>Accident data may be incomplete (pre-2010 records not digitised)</li>
            <li>EV isolation model trained on limited sample (n < 250)</li>
            <li>No fairness audit conducted across vehicle age cohorts</li>
            <li>Score drift possible as fleet composition changes</li>
            <li>No adversarial robustness testing performed</li>
          </ul>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div style='background:#0A1628; border:1px solid #1E3A5F; border-radius:10px; padding:14px; margin-top:12px;
                font-family:Space Mono,monospace; font-size:0.72rem; color:#475569;'>
      <span style='color:#A78BFA;'>AI USE DISCLOSURE</span> — This system uses rule-based and statistical AI models to assist human
      decision-making in vehicle safety management. All automated decisions (SMS dispatch, HGS gantry locks) require
      confirmation by an authorised operator. No fully autonomous enforcement actions are taken without human oversight.
      Model logic is fully auditable. Developed in compliance with KVKK Law No. 6698 and EU AI Act risk classification
      (High-Risk System — Annex III, safety components).
    </div>
    """, unsafe_allow_html=True)

# ====================================================================
# FOOTER
# ====================================================================
st.divider()
st.markdown("""
<div style='text-align:center; color:#1E3A5F; font-family:Space Mono,monospace; font-size:0.65rem; padding:8px 0;'>
  NCPTT v2.1 · National Cyber-Physical Transportation Twin · 
  Developed for MobilityTech Digital Inspection Research · 
  Data simulated for academic purposes only · KVKK / GDPR compliant architecture
</div>
""", unsafe_allow_html=True)