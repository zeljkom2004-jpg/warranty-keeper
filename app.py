import streamlit as st
import pandas as pd
import sqlite3
import datetime
from PIL import Image
import os

# --- KONFIGURACIJA STRANICE ---
st.set_page_config(page_title="Moj Garant", page_icon="📄", layout="centered")

st.title("📄 Moj Garant - Praćenje Garancija")

# --- BAZA PODATAKA (SQLite) ---
DB_FILE = "garancije.db"
IMG_FOLDER = "slike_racuna"

if not os.path.exists(IMG_FOLDER):
    os.makedirs(IMG_FOLDER)

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS garancije
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  naziv TEXT, 
                  datum_kupovine TEXT, 
                  trajanje_meseci INTEGER, 
                  datum_isteka TEXT, 
                  putanja_slike TEXT)''')
    conn.commit()
    conn.close()

init_db()

# --- FUNKCIJE ---
def dodaj_garanciju(naziv, datum_kup, trajanje, slika):
    datum_kup_obj = datetime.datetime.strptime(datum_kup, "%Y-%m-%d").date()
    datum_isteka_obj = datum_kup_obj + datetime.timedelta(days=trajanje*30)
    datum_isteka = datum_isteka_obj.strftime("%Y-%m-%d")

    ime_slike = f"{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}_{slika.name}"
    putanja_slike = os.path.join(IMG_FOLDER, ime_slike)
    with open(putanja_slike, "wb") as f:
        f.write(slika.getbuffer())

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO garancije (naziv, datum_kupovine, trajanje_meseci, datum_isteka, putanja_slike) VALUES (?, ?, ?, ?, ?)",
              (naziv, datum_kup, trajanje, datum_isteka, putanja_slike))
    conn.commit()
    conn.close()

def preuzmi_sve_garancije():
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query("SELECT * FROM garancije", conn)
    conn.close()
    return df

# --- INTERFEJS ---
tab1, tab2 = st.tabs(["📋 Lista Garancija", "➕ Dodaj Novu"])

with tab2:
    st.subheader("Unesi podatke o novom računu")
    form_naziv = st.text_input("Naziv uređaja/predmeta")
    form_datum_kup = st.date_input("Datum kupovine", datetime.date.today())
    form_trajanje = st.number_input("Trajanje garancije (u mesecima)", min_value=1, value=24)
    form_slika = st.file_uploader("Uslikaj ili otpremi račun", type=['jpg', 'jpeg', 'png'])

    if st.button("Sačuvaj u bazu"):
        if form_naziv and form_slika:
            dodaj_garanciju(form_naziv, str(form_datum_kup), form_trajanje, form_slika)
            st.success(f"Garancija za '{form_naziv}' je uspešno sačuvana!")
            st.balloons()
        else:
            st.error("Molimo unesite naziv i otpremite sliku računa.")

with tab1:
    st.subheader("Tvoje aktivne i istekle garancije")
    df = preuzmi_sve_garancije()

    if not df.empty:
        df['datum_isteka'] = pd.to_datetime(df['datum_isteka']).dt.date
        danas = datetime.date.today()
        
        aktivne = df[df['datum_isteka'] >= danas].sort_values(by='datum_isteka')
        istekle = df[df['datum_isteka'] < danas].sort_values(by='datum_isteka', ascending=False)

        col1, col2 = st.columns(2)
        col1.metric("Aktivne", len(aktivne))
        col2.metric("Istekle", len(istekle))

        st.write("---")

        if not aktivne.empty:
            st.write("### ✅ Aktivne Garancije")
            for index, row in aktivne.iterrows():
                preostalo_dana = (row['datum_isteka'] - danas).days
                status_boja = "⚠️ Uskoro ističe" if preostalo_dana < 30 else "✅ Aktivno"
                expander_boja = "⚠️" if preostalo_dana < 30 else "✅"

                with st.expander(f"{expander_boja} {row['naziv']} (ističe: {row['datum_isteka']})"):
                    col_img, col_txt = st.columns([1, 2])
                    with col_img:
                        if os.path.exists(row['putanja_slike']):
                            st.image(Image.open(row['putanja_slike']), use_column_width=True)
                    with col_txt:
                        st.write(f"**Datum kupovine:** {row['datum_kupovine']}")
                        st.write(f"**Trajanje:** {row['trajanje_meseci']} meseci")
                        st.write(f"**Status:** {status_boja}")
                        st.write(f"**Preostalo:** {preostalo_dana} dana")
        
        if not istekle.empty:
            st.write("### ❌ Istekle Garancije")
            for index, row in istekle.iterrows():
                with st.expander(f"❌ {row['naziv']} (isteklo: {row['datum_isteka']})", expanded=False):
                    col_img, col_txt = st.columns([1, 2])
                    with col_img:
                        if os.path.exists(row['putanja_slike']):
                            st.image(Image.open(row['putanja_slike']), use_column_width=True)
                    with col_txt:
                        st.write(f"**Datum kupovine:** {row['datum_kupovine']}")
                        st.write(f"**Trajanje:** {row['trajanje_meseci']} meseci")
                        st.write(f"**Status:** ❌ Isteklo")
    else:
        st.info("Nema sačuvanih garancija. Idi na tab 'Dodaj Novu' da uneseš prvu.")