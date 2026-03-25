import streamlit as st
import pandas as pd
import os

# =========================
# WCZYTANIE DANYCH
# =========================
df = pd.read_csv("baza_fotelikow.csv", encoding="cp1250", sep=";")
df.columns = df.columns.str.strip().str.lower()

# konwersje
df["cena"] = pd.to_numeric(df["cena"], errors="coerce")
df["wzrost_min"] = pd.to_numeric(df["wzrost_min"], errors="coerce")
df["wzrost_max"] = pd.to_numeric(df["wzrost_max"], errors="coerce")

# tylko foteliki i podstawki
df = df[
    df["kategoria"].str.contains("fotelik|podstawki", case=False, na=False)
]

# usuwamy akcesoria
df = df[~df["nazwa produktu"].str.contains("mata|lusterko", case=False, na=False)]

# =========================
# UI
# =========================
st.title("Doradca fotelików")

wzrost = st.number_input("Podaj wzrost dziecka (cm):", 40, 150, 75)

# =========================
# FUNKCJA MODEL
# =========================
def get_model(nazwa):
    try:
        return nazwa.lower().split()[1]
    except:
        return nazwa.lower()

# =========================
# LOGIKA
# =========================
dopasowane = df[
    (df["wzrost_min"] <= wzrost) &
    (df["wzrost_max"] >= wzrost)
]

if dopasowane.empty:
    df["roznica"] = abs(df["wzrost_min"] - wzrost)
    dopasowane = df.sort_values("roznica")

dopasowane = dopasowane.sort_values(
    ["wzrost_max", "cena"],
    ascending=[False, True]
)

# wybór unikalnych modeli
unikalne = []
modele = set()

for _, row in dopasowane.iterrows():
    model = get_model(row["nazwa produktu"])

    if model not in modele:
        unikalne.append(row)
        modele.add(model)

    if len(unikalne) == 3:
        break

wyniki = pd.DataFrame(unikalne)

# =========================
# KOMUNIKAT
# =========================
st.markdown(f"### 🔎 Dopasowane do dziecka o wzroście **{wzrost} cm**")

# =========================
# KAFELKI
# =========================
cols = st.columns(3)

for i, (_, row) in enumerate(wyniki.iterrows()):

    with cols[i]:

        # badge
        if i == 0:
            st.markdown("⭐ Najlepszy wybór")
        else:
            st.markdown("⭐")

        # zdjęcie
        nazwa_pliku = str(row["zdjecie"]).strip().lower()
        znalezione = False

        for plik in os.listdir("zdjecia"):
            if plik.lower() == nazwa_pliku:
                st.image(f"zdjecia/{plik}", width=220)
                znalezione = True
                break

        if not znalezione:
            st.write(" ")

        # nazwa
        st.markdown(f"**{row['nazwa produktu']}**")

        # cena
        st.markdown(f"### {int(row['cena'])} zł")

        # =========================
        # 🔥 NOWOŚĆ – DLACZEGO POLECAMY
        # =========================
        powody = []

        # dopasowanie
        powody.append("✔ Idealnie dopasowany do wzrostu dziecka")

        # norma
        if "isize" in str(row["norma"]).lower():
            powody.append("✔ Spełnia normę bezpieczeństwa i-Size")

        # obrotowy
        if str(row["obrotowy"]).lower() == "tak":
            powody.append("✔ Obrotowa baza ułatwia wkładanie dziecka")

        # cena
        if row["cena"] < 600:
            powody.append("✔ Bardzo dobry stosunek ceny do jakości")

        st.markdown("**Dlaczego polecamy:**")
        for p in powody:
            st.write(p)

        # =========================
        # CECHY TECHNICZNE
        # =========================
        if "isofix" in str(row["system_montażu"]).lower():
            st.write("✔ ISOFIX")

        if str(row["obrotowy"]).lower() == "tak":
            st.write("✔ Obrotowy")

        st.write(f"✔ {int(row['wzrost_min'])}-{int(row['wzrost_max'])} cm")

        # wyrównanie
        st.write(" ")
        st.write(" ")

        # przycisk
        if pd.notna(row["link"]):
            st.link_button("Zobacz produkt", row["link"])

        st.write("---")