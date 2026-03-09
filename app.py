import streamlit as st
import pandas as pd
import time
import requests
from bs4 import BeautifulSoup
import re
from googlesearch import search
import google.generativeai as genai

# --- RECONA 2.0 STRATEJİK YAPILANDIRMA ---
st.set_page_config(page_title="RECONA AI | Derin Analiz", page_icon="📡", layout="wide")

# --- AI AYARLARI (Buraya kendi API anahtarını yapıştırabilirsin veya yan menüden girebilirsin) ---
GEMINI_API_KEY = st.sidebar.text_input("Gemini API Anahtarınızı Girin", type="password")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# --- CSS TASARIM ---
st.markdown("""
    <style>
    .stApp { background-color: #f8fafc; }
    .result-card { padding: 25px; border-radius: 16px; background: white; border-left: 10px solid #2563eb; box-shadow: 0 4px 12px rgba(0,0,0,0.05); margin-bottom: 20px; }
    .ai-box { background-color: #f0f7ff; padding: 15px; border-radius: 10px; border: 1px dashed #2563eb; }
    </style>
    """, unsafe_allow_html=True)

# --- DERİN TARAYICI FONKSİYONU ---
def deep_scraping(url):
    data = {"Email": "Bulunamadı", "Tel": "Bulunamadı", "Icerik": ""}
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, timeout=10, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        text = soup.get_text()
        
        # Email ve Tel yakalama
        emails = re.findall(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', text)
        phones = re.findall(r'(\+?\d{10,15})', text)
        
        if emails: data["Email"] = emails[0]
        if phones: data["Tel"] = phones[0]
        data["Icerik"] = text[:2000] # AI analizi için ilk 2000 karakter
    except:
        pass
    return data

# --- AI ANALİZ FONKSİYONU ---
def ai_analiz(firma_adi, site_metni):
    if not GEMINI_API_KEY: return "AI Anahtarı girilmedi."
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"Şu firma hakkında web sitesinden alınan metni incele: {firma_adi}. \nMetin: {site_metni} \n\nLütfen şunları özetle: 1. Firmanın ana işi ne? 2. Hangi ürünleri satıyor? 3. Sence güvenilir bir iş ortağı mı? (Kısa ve öz olsun)"
        response = model.generate_content(prompt)
        return response.text
    except:
        return "AI analizi şu an yapılamıyor."

# --- ANA ARAYÜZ ---
if 'recona_db' not in st.session_state:
    st.session_state.recona_db = pd.DataFrame(columns=["Tarih", "Hedef", "Web", "Email", "Tel", "AI Analizi"])

st.title("📡 RECONA | Derin İstihbarat")
st.write("Firma ismini yazın, AI ve Derin Tarayıcı gerisini halletsin.")

target = st.text_input("Analiz Edilecek Firma")

if st.button("DERİN KEŞİF BAŞLAT"):
    if target:
        with st.spinner('Ajanlar web sitesine sızıyor ve AI rapor hazırlıyor...'):
            # 1. Web sitesini bul
            web_url = "Bulunamadı"
            for url in search(f"{target} resmi web sitesi", num_results=1, lang="tr"):
                web_url = url
                break
            
            # 2. Site içine gir ve veri topla
            scrape_data = {"Email": "N/A", "Tel": "N/A", "Icerik": ""}
            if web_url != "Bulunamadı":
                scrape_data = deep_scraping(web_url)
            
            # 3. AI ile analiz et
            analiz_notu = ai_analiz(target, scrape_data["Icerik"])
            
            # 4. Kaydet ve Göster
            new_row = {"Tarih": time.strftime("%d/%m/%Y"), "Hedef": target, "Web": web_url, "Email": scrape_data["Email"], "Tel": scrape_data["Tel"], "AI Analizi": analiz_notu}
            st.session_state.recona_db = pd.concat([st.session_state.recona_db, pd.DataFrame([new_row])], ignore_index=True)
            
            st.markdown(f"""
            <div class="result-card">
                <h3>🔍 {target} Raporu</h3>
                <p><b>🌐 Web:</b> {web_url}</p>
                <p><b>📧 E-posta:</b> {scrape_data['Email']} | <b>📞 Tel:</b> {scrape_data['Tel']}</p>
                <div class="ai-box">
                    <b>🤖 AI Strateji Notu:</b><br>{analiz_notu}
                </div>
            </div>
            """, unsafe_allow_html=True)

st.write("---")
st.subheader("📂 İstihbarat Arşivi")
st.dataframe(st.session_state.recona_db, use_container_width=True)
