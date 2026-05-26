import streamlit as st
import pandas as pd
import numpy as np

# Ekranı genişletelim ki akış şeması gibi soldan sağa rahatça aksın
st.set_page_config(layout="wide", page_title="HGS Entegre Muayene İkizi")

def safe_rerun():
    if hasattr(st, "rerun"):
        st.rerun()
    else:
        st.experimental_rerun()

# 1. VERİ SİMÜLASYONU
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
        'Inspection_Result': ['Pass'] * n_samples
    })
    
    df.loc[(df['Vehicle_Type'] == 'ICE') & (df['Age'] > 10), 'NOx_Emissions'] += 200
    df.loc[(df['Vehicle_Type'] == 'ICE') & (df['NOx_Emissions'] > 100), 'Inspection_Result'] = 'Fail_Emission_Fraud'
    df.loc[(df['Vehicle_Type'] == 'EV') & (df['Age'] > 11), 'Insulation_Resistance_M_Ohm'] = 45
    df.loc[(df['Vehicle_Type'] == 'EV') & (df['Insulation_Resistance_M_Ohm'] < 100), 'Inspection_Result'] = 'Fail_EV_Safety'
    
    return df

df_vehicles = get_internal_data()

# Hafıza Durumları
if 'ice_q' not in st.session_state: st.session_state.ice_q = 2
if 'ev_q' not in st.session_state: st.session_state.ev_q = 5
if 'hybrid' not in st.session_state: st.session_state.hybrid = False
if 'last_action' not in st.session_state: st.session_state.last_action = "Sistem hazır. Otoyoldan araç bekleniyor."

# ==========================================
# ANA BAŞLIK VE SİBER-FİZİKSEL AKIŞ ŞEMASI
# ==========================================
st.markdown("<h2 style='text-align: center; color: #1E3A8A;'>🔄 HGS Otomasyonlu Araç Muayene Giriş-Çıkış Hattı</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #666;'>Otoyol Dedektörü ile Fiziksel İstasyon Kuyruklarının Gerçek Zamanlı Bağlantısı</p>", unsafe_allow_html=True)
st.divider()

# Giriş-Çıkış Mantığını Gösteren Sol-Sağ Akış Sütunları
step1, step2, step3 = st.columns([1.1, 1.2, 1.1], gap="medium")

# ------------------------------------------------------------------
# ADIM 1: OTOYOL HGS ANTENİ (VERİ TOPLAMA VE FİLTRELEME)
# ------------------------------------------------------------------
with step1:
    st.markdown("### 🗺️ 1. Otoyol Tarama Noktası")
    st.info("İstasyona 5 km mesafedeki HGS Anteni otoyoldan geçen araçların plakalarını havadan okur.")
    
    # Anlamlı Tuş Eylemi
    if st.button("📡 Otoyoldan Geçen Araçları Yakala", type="primary", use_container_width=True):
        sample = df_vehicles.sample(4)
        ice_added = 0
        ev_added = 0
        alerts = []
        
        for idx, row in sample.iterrows():
            if row['Appointment_Status'] == 'No_Appointment_Unlawful' and row['Tolerance_Days_Left'] < 0:
                alerts.append(f"🔴 {row['Vehicle_ID']}: Muayenesiz Kaçak! İstasyon kapısından içeri sokulmadı, otoyolda çevrilerek ceza yazıldı.")
            elif row['Appointment_Status'] == 'No_Show':
                alerts.append(f"🟡 {row['Vehicle_ID']}: Randevu İhlali! İstasyona kabul edilmedi, ceza puanı işlendi.")
            else:
                if row['Vehicle_Type'] == 'ICE': 
                    st.session_state.ice_q += 1
                    ice_added += 1
                else: 
                    st.session_state.ev_q += 1
                    ev_added += 1
        
        st.session_state.last_action = f"HGS Sinyali Gönderildi: Temiz olan +{ice_added} Klasik ve +{ev_added} Elektrikli araç istasyon bariyerinden içeri alındı!"
        if alerts:
            st.session_state.last_action += "\n\n" + "\n".join(alerts)
            
        safe_rerun()

    # HGS'den gelen anlık lojistik logları
    st.caption("**HGS ve İstasyon Haberleşme Günlüğü:**")
    st.code(st.session_state.last_action, language="markdown")

# ------------------------------------------------------------------
# ADIM 2: FİZİKSEL İSTASYON ALANI (KUYRUK VE DARBOĞAZ YÖNETİMİ)
# ------------------------------------------------------------------
with step2:
    st.markdown("### 🏢 2. İstasyon Bariyerleri ve Alanı")
    st.write("HGS'den gelen onay sinyaliyle içeri giren araçların oluşturduğu güncel fiziksel kuyruklar:")
    
    # Görsel Sayaç Panelleri
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("⛽ Peron 1 (Klasik)")
        st.markdown(f"<h2 style='color:#1E3A8A;'>{st.session_state.ice_q} Araç</h2>", unsafe_allow_html=True)
        st.caption("Benzinli / Dizel Sırası")
    with c2:
        st.subheader("⚡ Peron 2 (Elektrikli)")
        st.markdown(f"<h2 style='color:#0D9488;'>{st.session_state.ev_q} Araç</h2>", unsafe_allow_html=True)
        ev_wait = st.session_state.ev_q * 16 / (2 if st.session_state.hybrid else 1)
        st.caption(f"Bekleme Süresi: **{ev_wait:.0f} dakika**")

    st.write("---")
    
    # Dijital İkiz Karar Destek Mekanizması
    if st.session_state.ev_q >= 6 and not st.session_state.hybrid:
        st.error("⚠️ **Darboğaz Uyarısı:** Elektrikli araç sırası kritik sınırı aştı!")
        if st.button("🔀 Peron 1'i Hibrit Çalışmaya Geçir (Yükü Paylaş)", use_container_width=True):
            st.session_state.hybrid = True
            safe_rerun()
    elif st.session_state.hybrid:
        st.success("🔄 **Esnek Çalışma Aktif:** Peron 1 hem klasik hem elektrikli araç eritiyor.")
        if st.button("⚙️ Normal Çalışma Düzenine Geri Dön", use_container_width=True):
            st.session_state.hybrid = False
            safe_rerun()

    # Kuyruğu eriten fiziksel tuş
    if st.button("🚗 İstasyon Çıkış Bariyerini Aç (Araçları İlerlet)", use_container_width=True):
        if st.session_state.ice_q > 0: st.session_state.ice_q -= 1
        if st.session_state.ev_q > 0: st.session_state.ev_q -= (2 if st.session_state.hybrid else 1)
        st.session_state.last_action = "İstasyon çıkış bariyeri açıldı: Muayenesi biten araçlar tesisten uğurlandı."
        safe_rerun()

# ------------------------------------------------------------------
# ADIM 3: DİJİTAL MUAYENE VE SENSÖR TEST ODASI
# ------------------------------------------------------------------
with step3:
    st.markdown("### 🔬 3. Dijital Sensör Test Odası")
    st.write("Kuyruğun en önündeki aracı alarak sensör kalibrasyonlarını ve teknik muayenesini başlatın.")
    
    if st.button("🧪 Sıradaki Aracı Teste Al", type="secondary", use_container_width=True):
        # Eğer kuyrukta hiç araç yoksa simülasyondan rastgele çek, varsa mantığı koru
        car = df_vehicles.sample(1).iloc[0]
        
        st.markdown(f"**🔬 Test Edilen Araç:** `{car['Vehicle_ID']}` ({'Elektrikli' if car['Vehicle_Type']=='EV' else 'Konvansiyonel'})")
        
        if car['Vehicle_Type'] == 'ICE':
            st.markdown("**Egzoz Gaz Analizi Yapılıyor...**")
            st.metric(label="Ölçülen NOx Emisyonu", value=f"{car['NOx_Emissions']:.1f} ppm")
            if car['Inspection_Result'] == 'Fail_Emission_Fraud':
                st.error("🚨 **RED (Yazılım Hilesi):** Araç beynine emisyon gizleyici illegal yazılım (AdBlue İptali vb.) yüklendiği saptandı!")
            else:
                st.success("✅ **ONAYLANDI:** Çevre emisyon değerleri yasal sınırın altında.")
        else:
            st.markdown("**Yüksek Voltaj Direnç Testi Yapılıyor...**")
            st.metric(label="İzolasyon Direnci", value=f"{car['Insulation_Resistance_M_Ohm']:.1f} MΩ")
            if car['Inspection_Result'] == 'Fail_EV_Safety':
                st.error("🚨 **RED (Yangın Riski):** Batarya paketinde hücre içi sızıntı ve kritik termal risk bulundu!")
            else:
                st.success("✅ **ONAYLANDI:** Batarya hücre yalıtımı ve şasi güvenliği tam not aldı.")