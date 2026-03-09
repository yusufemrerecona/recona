import streamlit as st
import pandas as pd
import time
import random
import re
from googlesearch import search
import requests
from bs4 import BeautifulSoup

# --- RECONA STRATEJİK YAPILANDIRMA ---
st.set_page_config(page_title="RECONA | İstihbarat Merkezi", page_icon="📡", layout="wide")

# Sade, Modern ve Profesyonel Arayüz Tasarımı
st.markdown("""
    <style>
    .stApp { background-color: #f8fafc; }
    .main-header { font-size: 2.8rem; font-weight: 900; color: #0f172a; letter-spacing: -1px; margin-bottom: 0px; }
    .status-tag { padding: 4px 12px; border-radius: 20px; font-size: 0.8rem; font-weight: 600; background: #e2e8f0; color: #475569; }
    .search-box { padding: 40px; border-radius: 24px; background: white; border: 1px solid #e2e8f0; box-shadow: 0 20px 25px -5px rgba(0,0,0,0.05); }
    .result-card { padding: 25px; border-radius: 16px; border-left: 8px solid #2563eb; background: #ffffff; margin-top: 25px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); }
    .stButton>button { width: 100%; border-radius: 12px; background: #2563eb; color: white; border: none; font-weight: 700; padding: 0.8rem; transition: 0.3s; }
    .stButton>button:hover { background: #1d4ed8; box-shadow: 0 10px 15px -3px rgba(37, 99, 235, 0.4); }
    </style>
    """, unsafe_allow_html=True)

# --- MERKEZİ VERİTABANI (CRM) ---
# Uygulama açık olduğu sürece verileri hafızada tutar.
if 'recona_db' not in st.session_state:
    st.session_state.recona_db = pd.DataFrame(columns=["Kayıt Tarihi", "Hedef İsim", "Web Adresi", "E-posta", "Telefon", "Tür", "İstihbarat Notu"])

# --- RECONA KEŞİF AJANI ---
def recona_scout(target):
    intel = {"Web": "Bulunamadı", "Email": "Bulunamadı", "Tel": "Bulunamadı"}
    try:
        # Google üzerinden dijital ayak izi takibi
        query = f"{target} resmi web sitesi iletişim"
        for url in search(query, num_results=1, lang="tr"):
            intel["Web"] = url
            break
        
        # İleride buraya web sitesinin içine girip e-posta/tel çeken fonksiyon eklenecek
    except:
        pass
    return intel

# --- ARAYÜZ ---
st.markdown('<div class="main-header">RECONA</div>', unsafe_allow_html=True)
st.markdown('<span class="status-tag">STRATEJİK KEŞİF VE ANALİZ SİSTEMİ</span>', unsafe_allow_html=True)
st.write("---")

tab_scout, tab_db = st.tabs(["🚀 Yeni Keşif", "📂 İstihbarat Arşivi"])

with tab_scout:
    st.markdown('<div class="search-box">', unsafe_allow_html=True)
    col_name, col_type = st.columns([3, 1])
    
    with col_name:
        target_input = st.text_input("Hedef Firma veya Rakip Adı", placeholder="Analiz edilecek unvanı girin...")
    with col_type:
        target_type = st.selectbox("Analiz Kategorisi", ["Potansiyel Müşteri", "Rakip İnceleme", "Stratejik Ortak"])

    if st.button("KEŞİF BAŞLAT"):
        if target_input:
            with st.spinner('RECONA ajanları dijital dünyada iz sürüyor...'):
                # Ajanı çalıştır
                found_data = recona_scout(target_input)
                
                # Veritabanına kaydet
                new_row = {
                    "Kayıt Tarihi": time.strftime("%d/%m/%Y"),
                    "Hedef İsim": target_input,
                    "Web Adresi": found_data["Web"],
                    "E-posta": found_data["Email"],
                    "Telefon": found_data["Tel"],
                    "Tür": target_type,
                    "İstihbarat Notu": f"{target_input} hakkında ilk keşif raporu oluşturuldu."
                }
                st.session_state.recona_db = pd.concat([st.session_state.recona_db, pd.DataFrame([new_row])], ignore_index=True)
                
                # Başarı mesajı ve rapor kartı
                st.markdown(f"""
                <div class="result-card">
                    <h3 style='margin-top:0;'>🔍 Keşif Tamamlandı</h3>
                    <p><b>Hedef:</b> {target_input}</p>
                    <p><b>Web Sitesi:</b> <a href="{found_data['Web']}" target="_blank">{found_data['Web']}</a></p>
                    <p style='color: #2563eb; font-weight:600;'>Bu hedef başarıyla İstihbarat Arşivi'ne eklendi.</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.warning("Lütfen araştırılacak bir isim girin.")
    st.markdown('</div>', unsafe_allow_html=True)

with tab_db:
    st.subheader("🗄️ Toplanan İstihbarat Verileri")
    if not st.session_state.recona_db.empty:
        # Arama ve filtreleme
        search_term = st.text_input("Arşivde Ara...", placeholder="Firma adı yazın...")
        df_filtered = st.session_state.recona_db
        if search_term:
            df_filtered = df_filtered[df_filtered["Hedef İsim"].str.contains(search_term, case=False)]
            
        st.dataframe(df_filtered, use_container_width=True, hide_index=True)
        
        # Excel/CSV olarak indir
        st.download_button("📂 Arşivi Dışa Aktar", 
                           df_filtered.to_csv(index=False).encode('utf-8-sig'), 
                           "recona_istihbarat_arsivi.csv", 
                           "text/csv")
    else:
        st.info("Henüz bir keşif yapılmadı. Arşiv boş.")

st.markdown("---")
st.caption("© 2026 RECONA | Ticari İstihbarat ve Stratejik Analiz Platformu")
