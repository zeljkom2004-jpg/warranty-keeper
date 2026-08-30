import streamlit as st
import pandas as pd
import sqlite3
import datetime
from PIL import Image
import os

# --- KONFIGURACIJA STRANICE ---
st.set_page_config(
    page_title="Warranty Vault Pro", 
    page_icon="🛡️", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- MODERNIZOVANI PRILAGOĐENI CSS ---
st.markdown('''
    <style>
    /* Google Fonts Import */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Pozadina i glavne margine */
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }

    /* Stilizovanje glavnog naslova i hedera */
    .hero-container {
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
        padding: 24px 32px;
        border-radius: 16px;
        color: white;
        box-shadow: 0 10px 20px rgba(0,0,0,0.12);
        margin-bottom: 25px;
    }
    
    .hero-title {
        font-size: 32px;
        font-weight: 700;
        margin: 0;
        letter-spacing: -0.5px;
    }
    
    .hero-subtitle {
        font-size: 15px;
        color: #e0e6ed;
        margin-top: 6px;
    }

    /* Kartice za garancije */
    div[data-testid="stExpander"] {
        background-color: #ffffff !important;
        border-radius: 12px !important;
        border: 1px solid #e1e8ed !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05) !important;
        margin-bottom: 12px !important;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }

    div[data-testid="stExpander"]:hover {
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1) !important;
    }

    /* Metric kartice */
    div[data-testid="stMetric"] {
        background: white;
        padding: 16px;
        border-radius: 12px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.04);
        border-left: 5px solid #2a5298;
    }

    /* Dugmići sa gradijentom i hover efektom */
    .stButton > button {
        background: linear-gradient(90deg, #11998e 0%, #38ef7d 100%);
        color: white !important;
        font-weight: 600 !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 12px 24px !important;
        width: 100%;
        box-shadow: 0 4px 12px rgba(56, 239, 125, 0.3);
        transition: all 0.3s ease !important;
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 18px rgba(56, 239, 125, 0.45);
    }

    /* Custom Badges za status */
    .badge-ok {
        background-color: #d4edda;
        color: #155724;
        padding: 4px 10px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 13px;
    }
    
    .badge-warn {
        background-color: #fff3cd;
        color: #856404;
        padding: 4px 10px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 13px;
    }

    .badge-exp {
        background-color: #f8d7da;
        color: #721c24;
        padding: 4px 10px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 13px;
    }
    </style>
''', unsafe_allow_html=True)

# --- REČNIK ZA JEZIKE (SRB / ENG) ---
TEXTS = {
    "SR": {
        "title": "🛡️ Warranty Vault Pro",
        "subtitle": "Pametni digitalni sef za upravljanje garancijama, računima i vrednošću",
        "tab_list": "📋 Pregled Garancija",
        "tab_add": "➕ Dodaj Novu Garanciju",
        "form_title": "📝 Unesite podatke o računu",
        "label_name": "Naziv uređaja / artikla",
        "label_category": "Kategorija",
        "label_price": "Cena / Vrednost (RSD ili EUR)",
        "label_date": "Datum kupovine",
        "label_duration": "Trajanje garancije (u mesecima)",
        "label_upload": "Fotografija ili fajl računa",
        "btn_save": "Sačuvaj u Sef",
        "success": "Garancija je uspešno sačuvana u sefu!",
        "error": "Molimo vas unesite naziv i priložite sliku računa.",
        "active_header": "✅ Aktivne Garancije",
        "expired_header": "❌ Istekle Garancije",
        "stat_active": "Aktivne Garancije",
        "stat_expired": "Istekle Garancije",
        "stat_val": "Ukupna Vrednost",
        "purchased": "Datum kupovine",
        "duration": "Trajanje garancije",
        "status": "Status garancije",
        "remaining": "Preostalo vreme",
        "days": "dana",
        "months": "meseci",
        "search_ph": "🔍 Pretraži po nazivu uređaja...",
        "cat_all": "Sve Kategorije",
        "confirm_del": "Obriši",
        "del_success": "Garancija je uspešno obrisana!"
    },
    "EN": {
        "title": "🛡️ Warranty Vault Pro",
        "subtitle": "Smart digital vault for managing warranties, receipts, and asset values",
        "tab_list": "📋 Warranty Overview",
        "tab_add": "➕ Add New Warranty",
        "form_title": "📝 Enter Receipt Details",
        "label_name": "Item Name",
        "label_category": "Category",
        "label_price": "Price / Value",
        "label_date": "Purchase Date",
        "label_duration": "Warranty Duration (Months)",
        "label_upload": "Receipt Image / Document",
        "btn_save": "Save to Vault",
        "success": "Warranty successfully saved to vault!",
        "error": "Please enter an item name and upload a receipt image.",
        "active_header": "✅ Active Warranties",
        "expired_header": "❌ Expired Warranties",
        "stat_active": "Active Warranties",
        "stat_expired": "Expired Warranties",
        "stat_val": "Total Tracked Value",
        "purchased": "Purchase Date",
        "duration": "Warranty Duration",
        "status": "Warranty Status",
        "remaining": "Remaining Time",
        "days": "days",
        "months": "months",
        "search_ph": "🔍 Search by item name...",
        "cat_all": "All Categories",
        "confirm_del": "Delete",
        "del_success": "Warranty successfully deleted!"
    }
}

CATEGORIES = {
    "SR": ["📱 Elektronika", "🚗 Auto / Vozila", "👕 Odeća & Obuća", "🏠 Bela tehnika & Dom", "🛠️ Alat & Oprema", "📑 Ostalo"],
    "EN": ["📱 Electronics", "🚗 Vehicles", "👕 Fashion & Apparel", "🏠 Home & Appliances", "🛠️ Tools & Gear", "📑 Other"]
}

# --- SIDEBAR (JEZIK & INFO) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/929/929422.png", width=90)
    st.title("Podešavanja / Settings")
    lang_choice = st.selectbox("🌐 Izaberite Jezik / Language", ["Srpski", "English"])
    lang = "SR" if lang_choice == "Srpski" else "EN"
    t = TEXTS[lang]
    st.markdown("---")
    st.info("💡 **Pro Tip:** Fotografišite račun u uslovima dobrog osvetljenja.")

# --- HERDER SEKCIJA ---
st.markdown(f'''
    <div class="hero-container">
        <div class="hero-title">{t["title"]}</div>
        <div class="hero-subtitle">{t["subtitle"]}</div>
    </div>
''', unsafe_allow_html=True)

# --- BAZA PODATAKA (SQLite) ---
DB_FILE = "garancije_v2.db"
IMG_FOLDER = "slike_racuna"

if not os.path.exists(IMG_FOLDER):
    os.makedirs(IMG_FOLDER)

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS garancije
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  naziv TEXT, 
                  kategorija TEXT,
                  cena REAL,
                  datum_kupovine TEXT, 
                  trajanje_meseci INTEGER, 
                  datum_isteka TEXT, 
                  putanja_slike TEXT)''')
    conn.commit()
    conn.close()

init_db()

def dodaj_garanciju(naziv, kategorija, cena, datum_kup, trajanje, slika):
    datum_kup_obj = datetime.datetime.strptime(datum_kup, "%Y-%m-%d").date()
    datum_isteka_obj = datum_kup_obj + datetime.timedelta(days=trajanje*30)
    datum_isteka = datum_isteka_obj.strftime("%Y-%m-%d")

    ime_slike = f"{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}_{slika.name}"
    putanja_slike = os.path.join(IMG_FOLDER, ime_slike)
    with open(putanja_slike, "wb") as f:
        f.write(slika.getbuffer())

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO garancije (naziv, kategorija, cena, datum_kupovine, trajanje_meseci, datum_isteka, putanja_slike) VALUES (?, ?, ?, ?, ?, ?, ?)",
              (naziv, kategorija, cena, datum_kup, trajanje, datum_isteka, putanja_slike))
    conn.commit()
    conn.close()

def preuzmi_sve_garancije():
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query("SELECT * FROM garancije", conn)
    conn.close()
    return df

def obrisi_garanciju(id_garancije):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("DELETE FROM garancije WHERE id = ?", (id_garancije,))
    conn.commit()
    conn.close()

# --- GLAVNI TABOVI ---
tab1, tab2 = st.tabs([t["tab_list"], t["tab_add"]])

# --- TAB 2: DODAVANJE GARANCIJE ---
with tab2:
    st.subheader(t["form_title"])
    
    col_a, col_b = st.columns(2)
    with col_a:
        form_naziv = st.text_input(t["label_name"])
        form_kategorija = st.selectbox(t["label_category"], CATEGORIES[lang])
        form_cena = st.number_input(t["label_price"], min_value=0.0, value=0.0, step=500.0)
    with col_b:
        form_datum_kup = st.date_input(t["label_date"], datetime.date.today())
        form_trajanje = st.number_input(t["label_duration"], min_value=1, value=24)
        form_slika = st.file_uploader(t["label_upload"], type=['jpg', 'jpeg', 'png'])

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button(t["btn_save"]):
        if form_naziv and form_slika:
            dodaj_garanciju(form_naziv, form_kategorija, form_cena, str(form_datum_kup), form_trajanje, form_slika)
            st.success(t["success"])
            st.balloons()
            st.rerun()
        else:
            st.error(t["error"])

# --- TAB 1: PREGLED GARANCIJA ---
with tab1:
    df = preuzmi_sve_garancije()

    if not df.empty:
        df['datum_isteka_dt'] = pd.to_datetime(df['datum_isteka']).dt.date
        danas = datetime.date.today()
        
        aktivne = df[df['datum_isteka_dt'] >= danas].sort_values(by='datum_isteka_dt')
        istekle = df[df['datum_isteka_dt'] < danas].sort_values(by='datum_isteka_dt', ascending=False)
        
        # STATISTIČKE KARTICE
        col_m1, col_m2, col_m3 = st.columns(3)
        col_m1.metric(t["stat_active"], len(aktivne))
        col_m2.metric(t["stat_expired"], len(istekle))
        col_m3.metric(t["stat_val"], f"{df['cena'].sum():,.2f}")

        st.markdown("<hr>", unsafe_allow_html=True)

        # PRETRAGA I FILTRIRANJE
        col_s1, col_s2 = st.columns([2, 1])
        with col_s1:
            pretraga = st.text_input("", placeholder=t["search_ph"])
        with col_s2:
            filter_kat = st.selectbox("", [t["cat_all"]] + CATEGORIES[lang])

        # Primena filtera
        if pretraga:
            df = df[df['naziv'].str.contains(pretraga, case=False, na=False)]
        if filter_kat != t["cat_all"]:
            df = df[df['kategorija'] == filter_kat]

        aktivne = df[df['datum_isteka_dt'] >= danas].sort_values(by='datum_isteka_dt')
        istekle = df[df['datum_isteka_dt'] < danas].sort_values(by='datum_isteka_dt', ascending=False)

        # AKTIVNE GARANCIJE
        if not aktivne.empty:
            st.markdown(f"### {t['active_header']}")
            for index, row in aktivne.iterrows():
                preostalo_dana = (row['datum_isteka_dt'] - danas).days
                
                if preostalo_dana < 30:
                    badge_html = f'<span class="badge-warn">⚠️ {preostalo_dana} {t["days"]}</span>'
                    icon = "⚠️"
                else:
                    badge_html = f'<span class="badge-ok">✅ {preostalo_dana} {t["days"]}</span>'
                    icon = "🛡️"

                header_text = f"{icon} **{row['naziv']}** ({row['kategorija']}) — Ističe: {row['datum_isteka']}"
                
                with st.expander(header_text):
                    col_img, col_txt = st.columns([1, 2])
                    with col_img:
                        if os.path.exists(row['putanja_slike']):
                            st.image(Image.open(row['putanja_slike']), use_container_width=True)
                    with col_txt:
                        st.markdown(f"**{t['purchased']}:** {row['datum_kupovine']}")
                        st.markdown(f"**{t['duration']}:** {row['trajanje_meseci']} {t['months']}")
                        st.markdown(f"**{t['remaining']}:** {badge_html}", unsafe_allow_html=True)
                        if row['cena'] > 0:
                            st.markdown(f"**Vrednost:** {row['cena']:,.2f}")
                        
                        st.markdown("<br>", unsafe_allow_html=True)
                        if st.button(f"{t['confirm_del']} #{row['id']}", key=f"del_{row['id']}"):
                            obrisi_garanciju(row['id'])
                            st.success(t["del_success"])
                            st.rerun()

        # ISTEKLE GARANCIJE
        if not istekle.empty:
            st.markdown(f"### {t['expired_header']}")
            for index, row in istekle.iterrows():
                badge_html = f'<span class="badge-exp">❌ {t["months"]}</span>'
                header_text = f"❌ **{row['naziv']}** ({row['kategorija']}) — Isteklo: {row['datum_isteka']}"
                
                with st.expander(header_text, expanded=False):
                    col_img, col_txt = st.columns([1, 2])
                    with col_img:
                        if os.path.exists(row['putanja_slike']):
                            st.image(Image.open(row['putanja_slike']), use_container_width=True)
                    with col_txt:
                        st.markdown(f"**{t['purchased']}:** {row['datum_kupovine']}")
                        st.markdown(f"**{t['duration']}:** {row['trajanje_meseci']} {t['months']}")
                        if row['cena'] > 0:
                            st.markdown(f"**Vrednost:** {row['cena']:,.2f}")
                        
                        st.markdown("<br>", unsafe_allow_html=True)
                        if st.button(f"{t['confirm_del']} #{row['id']}", key=f"del_{row['id']}"):
                            obrisi_garanciju(row['id'])
                            st.success(t["del_success"])
                            st.rerun()
    else:
        st.info("Nema sačuvanih garancija. Dodajte novu u drugom tabu! / No saved warranties.")