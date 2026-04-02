"""
IFT-2R Generator (wariant 12)
Aplikacja Streamlit do generowania pliku XML IFT-2R na podstawie JPK_FA.

Abacus Centrum Księgowe | Marcin
"""

import streamlit as st
import io
from decimal import Decimal
from datetime import date, datetime

from jpk_parser import parsuj_jpk_fa, grupuj_wg_kontrahenta, WynikParsowania
from ift2r_generator import generuj_xml, SEKCJE_D
from gus_api import pobierz_dane_nip
from kontrahenci import KONTRAHENCI, szukaj_kontrahenta

# ─── KONFIGURACJA STRONY ────────────────────────────────────────────────────
st.set_page_config(
    page_title="Generator IFT-2R",
    page_icon="🧾",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── STYL ───────────────────────────────────────────────────────────────────
st.markdown("""
<style>
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1a2744 0%, #0f1e3d 100%);
    color: #fff;
}
[data-testid="stSidebar"] .stMarkdown, [data-testid="stSidebar"] label {
    color: #d0d9f0 !important;
}
[data-testid="stSidebar"] .stTextInput > div > input {
    background: #253565;
    color: white;
    border: 1px solid #3a4f80;
}
.stTabs [data-baseweb="tab-list"] {
    gap: 4px;
}
.stTabs [data-baseweb="tab"] {
    background: #f5f7fa;
    border-radius: 6px 6px 0 0;
    padding: 8px 18px;
    font-size: 0.85rem;
}
.stTabs [aria-selected="true"] {
    background: #1a2744 !important;
    color: white !important;
}
.header-box {
    background: linear-gradient(90deg, #1a2744 0%, #2d4a8a 100%);
    padding: 1.2rem 1.5rem;
    border-radius: 10px;
    color: white;
    margin-bottom: 1.5rem;
}
.header-box h2 { margin: 0; font-size: 1.4rem; font-weight: 600; }
.header-box p  { margin: 0.3rem 0 0; font-size: 0.85rem; opacity: 0.8; }
.sekcja-card {
    background: #f8f9fb;
    border: 1px solid #e0e4ed;
    border-left: 4px solid #2d4a8a;
    border-radius: 6px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.8rem;
}
.kwota-total {
    font-size: 1.3rem;
    font-weight: 700;
    color: #1a2744;
}
.tag-zagr {
    display: inline-block;
    background: #e8f0fe;
    color: #1a56db;
    border-radius: 12px;
    padding: 2px 10px;
    font-size: 0.78rem;
    font-weight: 600;
}
</style>
""", unsafe_allow_html=True)

# ─── INICJALIZACJA STANU ────────────────────────────────────────────────────
def init_state():
    defaults = {
        # JPK
        "jpk_wyniki": [],           # lista WynikParsowania z wczytanych plików
        "grupy_kontrahentow": {},   # zagregowane dane wg kontrahenta
        # Dane formularza
        "cel_zlozenia": 1,
        "okres_od": f"{date.today().year - 1}-01-01",
        "okres_do": f"{date.today().year - 1}-12-31",
        # Płatnik
        "platnik_nip": "",
        "platnik_nazwa": "",
        "platnik_regon": "",
        "platnik_kraj": "PL",
        "platnik_wojewodztwo": "",
        "platnik_powiat": "",
        "platnik_gmina": "",
        "platnik_ulica": "",
        "platnik_nr_domu": "",
        "platnik_nr_lokalu": "",
        "platnik_miejscowosc": "",
        "platnik_kod": "",
        # Podatnik
        "podatnik_nazwa": "",
        "podatnik_kraj": "",
        "podatnik_id": "",
        "podatnik_rodzaj_id": 2,
        "podatnik_ulica": "",
        "podatnik_nr_domu": "",
        "podatnik_miejscowosc": "",
        "podatnik_kod": "",
        # Sekcje D
        "sekcje": [],               # lista słowników z wpisami sekcji D
        # Informacje
        "liczba_miesiecy": 12,
        "data_wniosku": "",
        "data_przekazania": "",
        "podpisujacy_imie": "",
        "podpisujacy_nazwisko": "",
        "email": "",
        "telefon": "",
        # Aktywny kontrahent
        "aktywny_klucz": None,
        # Klucz GUS
        "klucz_gus": "",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()


def _wczytaj_z_slownika(klucz: str):
    """Wczytuje dane kontrahenta ze słownika do session_state."""
    dane = KONTRAHENCI.get(klucz)
    if not dane:
        return
    st.session_state.podatnik_nazwa = dane["podatnik_nazwa"]
    st.session_state.podatnik_kraj = dane["podatnik_kraj"]
    st.session_state.podatnik_id = dane["podatnik_id"]
    st.session_state.podatnik_rodzaj_id = dane["podatnik_rodzaj_id"]
    st.session_state.podatnik_ulica = dane.get("podatnik_ulica", "")
    st.session_state.podatnik_nr_domu = dane.get("podatnik_nr_domu", "")
    st.session_state.podatnik_miejscowosc = dane.get("podatnik_miejscowosc", "")
    st.session_state.podatnik_kod = dane.get("podatnik_kod", "")
    st.session_state["_aktywny_slownik_klucz"] = klucz


# ═══════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("## 🧾 IFT-2R Generator")
    st.markdown("---")

    # ── GUS API klucz ──
    with st.expander("⚙️ Ustawienia API GUS", expanded=False):
        klucz_gus = st.text_input(
            "Klucz API GUS (BIR)",
            value=st.session_state.klucz_gus,
            type="password",
            help="Klucz do API REGON GUS. Testowy klucz działa bez rejestracji.",
            key="_klucz_gus_input",
        )
        st.session_state.klucz_gus = klucz_gus

    st.markdown("### 📋 NIP Płatnika")
    nip_input = st.text_input(
        "NIP płatnika (Twój klient)",
        value=st.session_state.platnik_nip,
        placeholder="0000000000",
        key="_nip_sidebar",
    )

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔍 Pobierz z GUS", use_container_width=True):
            nip_clean = nip_input.replace("-", "").replace(" ", "")
            klucz = st.session_state.klucz_gus or "abcde12345abcde12345"
            with st.spinner("Pobieranie danych..."):
                dane_gus = pobierz_dane_nip(nip_clean, klucz)
            if "blad" in dane_gus:
                st.error(dane_gus["blad"])
            else:
                st.session_state.platnik_nip = nip_clean
                st.session_state.platnik_nazwa = dane_gus.get("nazwa", "")
                st.session_state.platnik_regon = dane_gus.get("regon", "")
                st.session_state.platnik_wojewodztwo = dane_gus.get("wojewodztwo", "")
                st.session_state.platnik_powiat = dane_gus.get("powiat", "")
                st.session_state.platnik_gmina = dane_gus.get("gmina", "")
                st.session_state.platnik_ulica = dane_gus.get("ulica", "")
                st.session_state.platnik_nr_domu = dane_gus.get("nr_nieruchomosci", "")
                st.session_state.platnik_nr_lokalu = dane_gus.get("nr_lokalu", "")
                st.session_state.platnik_miejscowosc = dane_gus.get("miejscowosc", "")
                st.session_state.platnik_kod = dane_gus.get("kod_pocztowy", "")
                st.success(f"✅ {dane_gus.get('nazwa', '')}")
    with col2:
        if st.button("💾 Wpisz ręcznie", use_container_width=True):
            st.session_state.platnik_nip = nip_input

    st.markdown("---")
    st.markdown("### 📂 Wczytaj pliki JPK_FA")
    uploaded_files = st.file_uploader(
        "Wybierz pliki JPK_FA (XML)",
        type=["xml"],
        accept_multiple_files=True,
        key="_jpk_upload",
    )

    if uploaded_files:
        if st.button("📥 Wczytaj i parsuj", use_container_width=True, type="primary"):
            wszystkie_faktury = []
            bledy_suma = []
            for uf in uploaded_files:
                content = uf.read().decode("utf-8", errors="replace")
                wynik = parsuj_jpk_fa(content, uf.name)
                bledy_suma.extend(wynik.bledy)
                wszystkie_faktury.extend(wynik.faktury)
                if wynik.platnik_nip and not st.session_state.platnik_nip:
                    st.session_state.platnik_nip = wynik.platnik_nip
                    st.session_state.platnik_nazwa = wynik.platnik_nazwa

            # Zbiorczy wynik
            zbiorczy = WynikParsowania()
            zbiorczy.faktury = wszystkie_faktury
            zbiorczy.bledy = bledy_suma
            st.session_state.jpk_wyniki = [zbiorczy]
            st.session_state.grupy_kontrahentow = grupuj_wg_kontrahenta(zbiorczy)

            lf = len(wszystkie_faktury)
            lk = len(st.session_state.grupy_kontrahentow)
            st.success(f"✅ {lf} fakt. | {lk} kontr.")
            if bledy_suma:
                for b in bledy_suma:
                    st.warning(b)

    # ── Kontrahenci z JPK_FA ─────────────────────────────────────────────
    grupy = st.session_state.grupy_kontrahentow
    if grupy:
        st.markdown("---")
        st.markdown("### 👥 Z pliku JPK_FA")
        for klucz, g in grupy.items():
            n = g["liczba_faktur"]
            kw = g["suma_netto"]
            kraj = g["sprzedawca_kraj"]
            skrot = g["sprzedawca_nazwa"][:22] + "…" if len(g["sprzedawca_nazwa"]) > 22 else g["sprzedawca_nazwa"]
            lbl = f"{skrot} [{kraj}]\n{n} fakt | {kw:.2f} PLN"
            if st.button(lbl, key=f"sel_{klucz}", use_container_width=True):
                st.session_state.aktywny_klucz = klucz
                g2 = grupy[klucz]
                slownik_klucz = f"{g2['sprzedawca_id']}@{g2['sprzedawca_kraj']}"
                if slownik_klucz in KONTRAHENCI:
                    _wczytaj_z_slownika(slownik_klucz)
                else:
                    st.session_state.podatnik_nazwa = g2["sprzedawca_nazwa"]
                    st.session_state.podatnik_kraj = g2["sprzedawca_kraj"]
                    st.session_state.podatnik_id = g2["sprzedawca_id"]
                    st.session_state.podatnik_miejscowosc = ""

    # ── Słownik predefiniowanych kontrahentów ────────────────────────────
    st.markdown("---")
    st.markdown("### 📖 Słownik kontrahentów")
    szukaj = st.text_input("🔎 Szukaj", placeholder="np. Google, Meta, Microsoft…", key="_szukaj_kont")
    wyniki_slownika = szukaj_kontrahenta(szukaj)

    for s_klucz, s_dane in wyniki_slownika:
        logo = s_dane.get("logo", "🌍")
        skrot = s_dane["nazwa_skrot"]
        kraj = s_dane["podatnik_kraj"]
        lbl = f"{logo} {skrot} [{kraj}]"
        if st.button(lbl, key=f"dict_{s_klucz}", use_container_width=True):
            _wczytaj_z_slownika(s_klucz)
            st.session_state.aktywny_klucz = None


# ═══════════════════════════════════════════════════════════════════════════
# GŁÓWNA TREŚĆ
# ═══════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="header-box">
  <h2>🧾 Generator IFT-2R (wariant 12)</h2>
  <p>Informacja o przychodach podatnika CIT nierezydenta — obowiązuje od 01.01.2026 (dochody od 2025 r.)</p>
</div>
""", unsafe_allow_html=True)

tabs = st.tabs([
    "📋 Nagłówek",
    "🏢 Część A — Płatnik",
    "🌍 Część B — Podatnik",
    "📊 Zestawienie JPK_FA",
    "📂 Sekcje D–Q",
    "🔧 Informacje uzup.",
    "💾 Generuj XML",
])


# ─────────────────────────────────────────────────────────────────────────────
# TAB 1: NAGŁÓWEK
# ─────────────────────────────────────────────────────────────────────────────
with tabs[0]:
    st.subheader("Nagłówek deklaracji")

    col1, col2 = st.columns(2)
    with col1:
        cel = st.radio(
            "**Pole 7 — Cel złożenia**",
            options=[1, 2],
            format_func=lambda x: "1 — złożenie informacji" if x == 1 else "2 — korekta informacji",
            index=0 if st.session_state.cel_zlozenia == 1 else 1,
            horizontal=True,
        )
        st.session_state.cel_zlozenia = cel

    with col2:
        st.info("🏛️ **Urząd skarbowy (Pole 6)**\n\nLubelski Urząd Skarbowy w Lublinie\nKod: **0671** (stały dla wszystkich IFT-2R)")

    st.markdown("---")
    col3, col4 = st.columns(2)
    with col3:
        od = st.date_input(
            "**Pole 4 — Data początku roku podatkowego**",
            value=datetime.strptime(st.session_state.okres_od, "%Y-%m-%d").date(),
        )
        st.session_state.okres_od = od.strftime("%Y-%m-%d")
    with col4:
        do = st.date_input(
            "**Pole 5 — Data końca roku podatkowego**",
            value=datetime.strptime(st.session_state.okres_do, "%Y-%m-%d").date(),
        )
        st.session_state.okres_do = do.strftime("%Y-%m-%d")

    rok = od.year
    st.caption(f"ℹ️ Formularz za rok podatkowy: **{rok}**. Termin złożenia IFT-2R: do końca marca {rok + 1}.")


# ─────────────────────────────────────────────────────────────────────────────
# TAB 2: CZĘŚĆ A — PŁATNIK
# ─────────────────────────────────────────────────────────────────────────────
with tabs[1]:
    st.subheader("Część A — Dane płatnika / podmiotu wypłacającego")
    st.caption("Pola 8–18. Dane pobierane automatycznie z GUS po podaniu NIP w sidebarze.")

    col1, col2 = st.columns(2)
    with col1:
        st.session_state.platnik_nip = st.text_input(
            "**Pole 1 — NIP płatnika**",
            value=st.session_state.platnik_nip,
        )
        st.session_state.platnik_nazwa = st.text_input(
            "**Pole 9 — Pełna nazwa**",
            value=st.session_state.platnik_nazwa,
        )
        st.session_state.platnik_regon = st.text_input(
            "REGON (opcjonalnie)",
            value=st.session_state.platnik_regon,
        )
    with col2:
        st.session_state.platnik_ulica = st.text_input("Ulica", value=st.session_state.platnik_ulica)
        cola, colb = st.columns(2)
        with cola:
            st.session_state.platnik_nr_domu = st.text_input("Nr domu", value=st.session_state.platnik_nr_domu)
        with colb:
            st.session_state.platnik_nr_lokalu = st.text_input("Nr lokalu", value=st.session_state.platnik_nr_lokalu)
        st.session_state.platnik_miejscowosc = st.text_input("Miejscowość", value=st.session_state.platnik_miejscowosc)
        colc, cold = st.columns(2)
        with colc:
            st.session_state.platnik_kod = st.text_input("Kod pocztowy", value=st.session_state.platnik_kod)
        with cold:
            st.session_state.platnik_kraj = st.text_input("Kod kraju", value=st.session_state.platnik_kraj)

    with st.expander("Województwo / Powiat / Gmina"):
        col_w, col_p, col_g = st.columns(3)
        with col_w:
            st.session_state.platnik_wojewodztwo = st.text_input("Województwo", value=st.session_state.platnik_wojewodztwo)
        with col_p:
            st.session_state.platnik_powiat = st.text_input("Powiat", value=st.session_state.platnik_powiat)
        with col_g:
            st.session_state.platnik_gmina = st.text_input("Gmina", value=st.session_state.platnik_gmina)


# ─────────────────────────────────────────────────────────────────────────────
# TAB 3: CZĘŚĆ B — PODATNIK ZAGRANICZNY
# ─────────────────────────────────────────────────────────────────────────────
with tabs[2]:
    st.subheader("Część B — Dane podatnika zagranicznego (odbiorcy należności)")
    st.caption("Pola 19–32. Dane wczytywane automatycznie po wybraniu kontrahenta z JPK_FA w sidebarze.")

    # Jeśli wybrany kontrahent — pokaż info
    aktywny_słownik = st.session_state.get("_aktywny_slownik_klucz")
    aktywny_klucz = st.session_state.aktywny_klucz

    if aktywny_słownik and aktywny_słownik in KONTRAHENCI:
        sd = KONTRAHENCI[aktywny_słownik]
        st.success(
            f"{sd.get('logo','🌍')} Kontrahent ze słownika: **{sd['podatnik_nazwa']}** "
            f"[{sd['podatnik_kraj']}] | ID: `{sd['podatnik_id']}`"
        )
        if sd.get("uwaga"):
            st.info(f"💡 {sd['uwaga']}")
    elif aktywny_klucz and aktywny_klucz in st.session_state.grupy_kontrahentow:
        g = st.session_state.grupy_kontrahentow[aktywny_klucz]
        st.success(
            f"🌍 Kontrahent z JPK_FA: **{g['sprzedawca_nazwa']}** "
            f"[{g['sprzedawca_kraj']}] | ID: `{g['sprzedawca_id']}`"
        )

    col1, col2 = st.columns(2)
    with col1:
        st.session_state.podatnik_nazwa = st.text_input(
            "**Pole 20 — Pełna nazwa podatnika**",
            value=st.session_state.podatnik_nazwa,
        )
        st.session_state.podatnik_kraj = st.text_input(
            "**Pole 25 — Kraj siedziby (kod 2-znakowy)**",
            value=st.session_state.podatnik_kraj,
            help="np. IE = Irlandia, DE = Niemcy, US = USA",
        )
        rod_id = st.radio(
            "**Pole 23 — Rodzaj identyfikacji**",
            options=[1, 2],
            format_func=lambda x: "1 — podatkowy (VAT ID, NIP)" if x == 1 else "2 — inny",
            index=st.session_state.podatnik_rodzaj_id - 1,
            horizontal=True,
        )
        st.session_state.podatnik_rodzaj_id = rod_id
        st.session_state.podatnik_id = st.text_input(
            "**Pole 24 — Numer identyfikacyjny podatnika**",
            value=st.session_state.podatnik_id,
        )

    with col2:
        st.markdown("**Adres siedziby (Pola 27–32)**")
        st.session_state.podatnik_ulica = st.text_input("Ulica", value=st.session_state.podatnik_ulica, key="pod_ulica")
        st.session_state.podatnik_nr_domu = st.text_input("Nr domu", value=st.session_state.podatnik_nr_domu, key="pod_nr")
        st.session_state.podatnik_miejscowosc = st.text_input("Miejscowość", value=st.session_state.podatnik_miejscowosc, key="pod_msc")
        st.session_state.podatnik_kod = st.text_input("Kod pocztowy", value=st.session_state.podatnik_kod, key="pod_kod")


# ─────────────────────────────────────────────────────────────────────────────
# TAB 4: ZESTAWIENIE JPK_FA
# ─────────────────────────────────────────────────────────────────────────────
with tabs[3]:
    st.subheader("Zestawienie faktur z pliku JPK_FA")

    grupy = st.session_state.grupy_kontrahentow

    if not grupy:
        st.info("⬆️ Wczytaj pliki JPK_FA w sidebarze, a tutaj pojawi się zestawienie faktur.")
    else:
        # Wybór kontrahenta
        opcje = {k: f"{g['sprzedawca_nazwa']} [{g['sprzedawca_kraj']}]" for k, g in grupy.items()}
        wybrany = st.selectbox(
            "Wybierz kontrahenta:",
            options=list(opcje.keys()),
            format_func=lambda k: opcje[k],
            index=list(opcje.keys()).index(aktywny_klucz) if aktywny_klucz in opcje else 0,
        )

        if wybrany:
            st.session_state.aktywny_klucz = wybrany
            g = grupy[wybrany]

            col1, col2, col3 = st.columns(3)
            col1.metric("Liczba faktur", g["liczba_faktur"])
            col2.metric("Suma netto", f"{g['suma_netto']:.2f} {g['waluta']}")
            col3.metric("Suma brutto", f"{g['suma_brutto']:.2f} {g['waluta']}")

            st.markdown("---")
            st.markdown("**Szczegółowe faktury:**")

            import pandas as pd
            rows = []
            for f in g["faktury"]:
                rows.append({
                    "Numer faktury": f.numer,
                    "Data wystawienia": f.data_wystawienia,
                    "Data sprzedaży": f.data_sprzedazy,
                    "Sprzedawca": f.sprzedawca_nazwa,
                    "Kraj": f.sprzedawca_kraj,
                    "Waluta": f.waluta,
                    "Netto": float(f.netto),
                    "VAT": float(f.vat),
                    "Brutto": float(f.brutto),
                    "Plik JPK": f.zrodlo_plik,
                })

            df = pd.DataFrame(rows)
            st.dataframe(df, use_container_width=True, hide_index=True)

            # Suma
            st.markdown(f"**Suma netto:** `{g['suma_netto']:.2f}` {g['waluta']}  |  "
                        f"**Suma brutto:** `{g['suma_brutto']:.2f}` {g['waluta']}")

            st.markdown("---")
            st.info(
                "💡 Przejdź do zakładki **Sekcje D–Q**, aby przypisać te kwoty do odpowiedniej kategorii IFT-2R "
                "(np. sekcja K dla usług reklamowych Google, Meta, itp.)"
            )


# ─────────────────────────────────────────────────────────────────────────────
# TAB 5: SEKCJE D–Q
# ─────────────────────────────────────────────────────────────────────────────
with tabs[4]:
    st.subheader("Część D — Rodzaje przychodów i wysokość pobranego podatku")
    st.caption(
        "Dodaj wpisy dla każdej kategorii przychodu. "
        "Dla Google/Meta/LinkedIn to zazwyczaj **sekcja K** (usługi niematerialne, art. 21 ust. 1 pkt 2a)."
    )

    # Pomocnik szybkiego wpisania sumy z JPK
    grupy = st.session_state.grupy_kontrahentow
    aktywny_klucz = st.session_state.aktywny_klucz
    if grupy and aktywny_klucz and aktywny_klucz in grupy:
        g = grupy[aktywny_klucz]
        suma_netto = g["suma_netto"]
        st.markdown(
            f'<div class="sekcja-card">💡 Kontrahent: <b>{g["sprzedawca_nazwa"]}</b> '
            f'— suma netto z JPK_FA: <span class="kwota-total">{suma_netto:.2f} {g["waluta"]}</span></div>',
            unsafe_allow_html=True,
        )

    # Formularz nowego wpisu
    with st.expander("➕ Dodaj wpis do sekcji D", expanded=True):
        opcje_sek = {k: f"{k} — {v['opis']}" for k, v in SEKCJE_D.items()}

        # Domyślna sekcja ze słownika kontrahentów
        aktywny_słownik = st.session_state.get("_aktywny_slownik_klucz")
        domyslna_sek = "K"
        domyslna_stawka_sek = 20
        if aktywny_słownik and aktywny_słownik in KONTRAHENCI:
            domyslna_sek = KONTRAHENCI[aktywny_słownik].get("domyslna_sekcja", "K")
            domyslna_stawka_sek = KONTRAHENCI[aktywny_słownik].get("domyslna_stawka", 20)

        col1, col2 = st.columns([1, 3])
        with col1:
            sym = st.selectbox(
                "Symbol sekcji",
                options=list(opcje_sek.keys()),
                format_func=lambda k: opcje_sek[k],
                index=list(opcje_sek.keys()).index(domyslna_sek),
            )
        with col2:
            st.caption(SEKCJE_D[sym]["opis"])

        col3, col4, col5, col6 = st.columns(4)
        with col3:
            domysl_netto = float(suma_netto) if (grupy and aktywny_klucz and aktywny_klucz in grupy) else 0.0
            zwolniony = st.number_input(
                "Kwota zwolniona z opodatkowania (kol. c)",
                min_value=0.0,
                value=domysl_netto,
                step=0.01,
                format="%.2f",
                help="Kwota przychodu zwolnionego na podstawie UPO (certyfikat rezydencji). "
                     "Dla Google/Meta/LinkedIn zazwyczaj = suma netto wszystkich faktur.",
            )
        with col4:
            opodatkowany = st.number_input(
                "Kwota opodatkowana (kol. d)",
                min_value=0.0,
                value=0.0,
                step=0.01,
                format="%.2f",
                help="Kwota przychodu, od której pobrano podatek.",
            )
        with col5:
            max_stawka = SEKCJE_D[sym]["max_stawka"]
            # Domyślna stawka: ze słownika kontrahenta lub max dla sekcji
            domyslna_stk = min(float(domyslna_stawka_sek), float(max_stawka))
            stawka = st.number_input(
                f"Stawka podatku % (max {max_stawka}%)",
                min_value=0.0,
                max_value=float(max_stawka),
                value=domyslna_stk,
                step=1.0,
                format="%.0f",
            )
        with col6:
            podatek = st.number_input(
                "Kwota pobranego podatku (kol. e)",
                min_value=0.0,
                value=0.0,
                step=0.01,
                format="%.2f",
            )

        if st.button("➕ Dodaj do listy", type="primary"):
            st.session_state.sekcje.append({
                "symbol": sym,
                "opis": SEKCJE_D[sym]["opis"],
                "zwolniony": f"{zwolniony:.2f}",
                "opodatkowany": f"{opodatkowany:.2f}",
                "stawka": f"{stawka:.0f}",
                "podatek": f"{podatek:.2f}",
            })
            st.success(f"✅ Dodano wpis sekcja {sym}")

    # Lista wpisów
    sekcje = st.session_state.sekcje
    if sekcje:
        st.markdown("---")
        st.markdown("**Wpisane pozycje:**")
        for i, s in enumerate(sekcje):
            col_s, col_del = st.columns([9, 1])
            with col_s:
                st.markdown(
                    f'<div class="sekcja-card">'
                    f'<b>Sekcja {s["symbol"]}</b>: {s["opis"]}<br>'
                    f'Zwolniony: <b>{s["zwolniony"]}</b> | '
                    f'Opodatkowany: <b>{s["opodatkowany"]}</b> | '
                    f'Stawka: <b>{s["stawka"]}%</b> | '
                    f'Podatek: <b>{s["podatek"]}</b>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
            with col_del:
                if st.button("🗑️", key=f"del_sek_{i}", help="Usuń wpis"):
                    st.session_state.sekcje.pop(i)
                    st.rerun()

        # Sumy
        st.markdown("---")
        tot_zwol = sum(Decimal(s["zwolniony"]) for s in sekcje)
        tot_opod = sum(Decimal(s["opodatkowany"]) for s in sekcje)
        tot_pod = sum(Decimal(s["podatek"]) for s in sekcje)
        c1, c2, c3 = st.columns(3)
        c1.metric("Razem zwolniony", f"{tot_zwol:.2f}")
        c2.metric("Razem opodatkowany", f"{tot_opod:.2f}")
        c3.metric("Razem podatek", f"{tot_pod:.2f}")
    else:
        st.info("Brak wpisów. Dodaj co najmniej jeden wpis powyżej.")


# ─────────────────────────────────────────────────────────────────────────────
# TAB 6: INFORMACJE UZUPEŁNIAJĄCE
# ─────────────────────────────────────────────────────────────────────────────
with tabs[5]:
    st.subheader("Sekcja R, S, T, U — Informacje uzupełniające")

    col1, col2 = st.columns(2)
    with col1:
        lm = st.number_input(
            "**Pole 120 — Liczba miesięcy roku podatkowego**",
            min_value=1,
            max_value=24,
            value=st.session_state.liczba_miesiecy,
        )
        st.session_state.liczba_miesiecy = lm

        dw = st.text_input(
            "**Pole 121 — Data złożenia wniosku przez podatnika**",
            value=st.session_state.data_wniosku,
            placeholder="YYYY-MM-DD (jeśli dotyczy)",
        )
        st.session_state.data_wniosku = dw

        dp = st.text_input(
            "**Pole 122 — Data przekazania informacji podatnikowi**",
            value=st.session_state.data_przekazania,
            placeholder="YYYY-MM-DD",
        )
        st.session_state.data_przekazania = dp

    with col2:
        st.session_state.podpisujacy_imie = st.text_input(
            "**Pole 123 — Imię osoby podpisującej**",
            value=st.session_state.podpisujacy_imie,
        )
        st.session_state.podpisujacy_nazwisko = st.text_input(
            "**Pole 124 — Nazwisko osoby podpisującej**",
            value=st.session_state.podpisujacy_nazwisko,
        )
        st.session_state.telefon = st.text_input(
            "**Pole 128 — Telefon kontaktowy**",
            value=st.session_state.telefon,
        )
        st.session_state.email = st.text_input(
            "**Pole 129 — E-mail kontaktowy**",
            value=st.session_state.email,
        )


# ─────────────────────────────────────────────────────────────────────────────
# TAB 7: GENERUJ XML
# ─────────────────────────────────────────────────────────────────────────────
with tabs[6]:
    st.subheader("Generowanie pliku XML IFT-2R")

    # Walidacja
    bledy_walidacji = []
    if not st.session_state.platnik_nip:
        bledy_walidacji.append("❌ Brak NIP płatnika (Część A).")
    if not st.session_state.platnik_nazwa:
        bledy_walidacji.append("❌ Brak nazwy płatnika (Część A).")
    if not st.session_state.podatnik_nazwa:
        bledy_walidacji.append("❌ Brak nazwy podatnika zagranicznego (Część B).")
    if not st.session_state.podatnik_kraj:
        bledy_walidacji.append("❌ Brak kodu kraju podatnika (Część B).")
    if not st.session_state.podatnik_id:
        bledy_walidacji.append("❌ Brak numeru identyfikacyjnego podatnika (Część B).")
    if not st.session_state.sekcje:
        bledy_walidacji.append("❌ Brak wpisów w sekcjach D (Zakładka 'Sekcje D–Q').")

    if bledy_walidacji:
        for b in bledy_walidacji:
            st.error(b)
    else:
        st.success("✅ Wszystkie wymagane pola są wypełnione. Możesz wygenerować XML.")

    col_gen, col_blank = st.columns([1, 2])
    with col_gen:
        generuj = st.button("🔄 Generuj XML", type="primary", use_container_width=True, disabled=bool(bledy_walidacji))

    if generuj or "xml_wygenerowany" in st.session_state:
        if generuj:
            # Zbierz dane
            dane = {
                "cel_zlozenia": st.session_state.cel_zlozenia,
                "okres_od": st.session_state.okres_od,
                "okres_do": st.session_state.okres_do,
                "platnik_nip": st.session_state.platnik_nip,
                "platnik_nazwa": st.session_state.platnik_nazwa,
                "platnik_regon": st.session_state.platnik_regon,
                "platnik_kraj": st.session_state.platnik_kraj,
                "platnik_wojewodztwo": st.session_state.platnik_wojewodztwo,
                "platnik_powiat": st.session_state.platnik_powiat,
                "platnik_gmina": st.session_state.platnik_gmina,
                "platnik_ulica": st.session_state.platnik_ulica,
                "platnik_nr_domu": st.session_state.platnik_nr_domu,
                "platnik_nr_lokalu": st.session_state.platnik_nr_lokalu,
                "platnik_miejscowosc": st.session_state.platnik_miejscowosc,
                "platnik_kod": st.session_state.platnik_kod,
                "podatnik_nazwa": st.session_state.podatnik_nazwa,
                "podatnik_kraj": st.session_state.podatnik_kraj,
                "podatnik_id": st.session_state.podatnik_id,
                "podatnik_rodzaj_id": st.session_state.podatnik_rodzaj_id,
                "podatnik_ulica": st.session_state.podatnik_ulica,
                "podatnik_nr_domu": st.session_state.podatnik_nr_domu,
                "podatnik_miejscowosc": st.session_state.podatnik_miejscowosc,
                "podatnik_kod": st.session_state.podatnik_kod,
                "sekcje": st.session_state.sekcje,
                "liczba_miesiecy": st.session_state.liczba_miesiecy,
            }

            try:
                xml_output = generuj_xml(dane)
                st.session_state.xml_wygenerowany = xml_output
                st.session_state.xml_blad = None
            except Exception as e:
                st.session_state.xml_blad = str(e)
                st.session_state.xml_wygenerowany = None

        xml_out = st.session_state.get("xml_wygenerowany")
        xml_blad = st.session_state.get("xml_blad")

        if xml_blad:
            st.error(f"Błąd generowania XML: {xml_blad}")
        elif xml_out:
            # Nazwa pliku
            nip_p = st.session_state.platnik_nip
            rok = st.session_state.okres_od[:4]
            nazwa_pliku = f"IFT-2R_{nip_p}_{rok}.xml"

            st.download_button(
                label="⬇️ Pobierz XML IFT-2R",
                data=xml_out.encode("utf-8"),
                file_name=nazwa_pliku,
                mime="application/xml",
                type="primary",
                use_container_width=False,
            )

            st.markdown("---")
            st.markdown("**Podgląd XML:**")
            st.code(xml_out, language="xml")

            st.caption(
                "📌 Pamiętaj: po pobraniu XML otwórz go w aplikacji **e-Deklaracje** lub interaktywnym formularzu PDF "
                "z MF, zweryfikuj dane i wyślij z kwalifikowanym podpisem elektronicznym do Lubelskiego US."
            )
