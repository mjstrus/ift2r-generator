"""
IFT-2R Generator (wariant 12)
Aplikacja Streamlit — Abacus Centrum Księgowe
"""

import streamlit as st
from decimal import Decimal
from datetime import date, datetime

from jpk_parser import parsuj_jpk_fa, grupuj_wg_kontrahenta, WynikParsowania
from ift2r_generator import generuj_xml, SEKCJE_D
from gus_api import pobierz_dane_nip
from kontrahenci import KONTRAHENCI, szukaj_kontrahenta

# ─── KONFIGURACJA ───────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Generator IFT-2R | Abacus",
    page_icon="🧾",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── STYL — identyczny jak Informacja Dodatkowa ─────────────────────────────
st.markdown("""
<style>
/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background-color: #f0f2f6;
    border-right: 1px solid #d0d5e0;
}
[data-testid="stSidebar"] .stMarkdown p,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] .stRadio label {
    color: #1a2744 !important;
    font-size: 0.88rem;
}
[data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
    color: #1a2744 !important;
}

/* ── Główny nagłówek ── */
.abacus-header {
    background: linear-gradient(135deg, #1a2744 0%, #2d4a8a 60%, #1a3a6b 100%);
    padding: 1.4rem 2rem;
    border-radius: 12px;
    margin-bottom: 1.8rem;
    color: white;
}
.abacus-header h1 {
    margin: 0 0 0.3rem 0;
    font-size: 1.6rem;
    font-weight: 700;
    letter-spacing: -0.02em;
    color: white !important;
}
.abacus-header p {
    margin: 0;
    font-size: 0.88rem;
    opacity: 0.82;
    color: white !important;
}
.abacus-header .badge {
    display: inline-block;
    background: rgba(255,255,255,0.18);
    border: 1px solid rgba(255,255,255,0.35);
    border-radius: 20px;
    padding: 2px 12px;
    font-size: 0.78rem;
    margin-top: 0.6rem;
    color: white;
}

/* ── Zakładki ── */
.stTabs [data-baseweb="tab-list"] {
    gap: 2px;
    background: #f0f2f6;
    border-radius: 8px;
    padding: 4px;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 6px;
    padding: 6px 16px;
    font-size: 0.83rem;
    font-weight: 500;
    color: #4a5568;
    background: transparent;
}
.stTabs [aria-selected="true"] {
    background: #1a2744 !important;
    color: white !important;
}

/* ── Karty sekcji ── */
.sekcja-card {
    background: #f8f9fb;
    border: 1px solid #e2e6ef;
    border-left: 4px solid #2d4a8a;
    border-radius: 6px;
    padding: 0.75rem 1rem;
    margin-bottom: 0.6rem;
    font-size: 0.87rem;
    color: #1a2744;
}
.info-box {
    background: #eef3fd;
    border: 1px solid #c3d3f5;
    border-radius: 8px;
    padding: 0.8rem 1rem;
    font-size: 0.84rem;
    color: #1a2744;
    margin-bottom: 1rem;
}
.warn-box {
    background: #fff8e6;
    border: 1px solid #f5d87a;
    border-radius: 8px;
    padding: 0.8rem 1rem;
    font-size: 0.84rem;
    color: #7a5200;
    margin-bottom: 1rem;
}
.kontrahent-card {
    background: #eef3fd;
    border: 1px solid #c3d3f5;
    border-radius: 8px;
    padding: 0.7rem 1rem;
    margin-bottom: 0.8rem;
    font-size: 0.85rem;
}
.kwota-big {
    font-size: 1.4rem;
    font-weight: 700;
    color: #1a2744;
}

/* ── Sidebar search ── */
[data-testid="stSidebar"] input {
    background: white !important;
    border: 1px solid #c8d0e0 !important;
    border-radius: 6px !important;
    font-size: 0.85rem !important;
}
</style>
""", unsafe_allow_html=True)

# ─── STAN APLIKACJI ─────────────────────────────────────────────────────────
def _init():
    defaults = {
        "jpk_wyniki": [],
        "grupy_kontrahentow": {},
        "cel_zlozenia": 1,
        "okres_od": f"{date.today().year - 1}-01-01",
        "okres_do": f"{date.today().year - 1}-12-31",
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
        "podatnik_nazwa": "",
        "podatnik_kraj": "",
        "podatnik_id": "",
        "podatnik_rodzaj_id": 2,
        "podatnik_ulica": "",
        "podatnik_nr_domu": "",
        "podatnik_miejscowosc": "",
        "podatnik_kod": "",
        "sekcje": [],
        "liczba_miesiecy": 12,
        "data_wniosku": "",
        "data_przekazania": "",
        "podpisujacy_imie": "",
        "podpisujacy_nazwisko": "",
        "email": "",
        "telefon": "",
        "aktywny_klucz": None,
        "_aktywny_slownik_klucz": None,
        "xml_wygenerowany": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

_init()


def _wczytaj_z_slownika(klucz: str):
    d = KONTRAHENCI.get(klucz)
    if not d:
        return
    st.session_state.podatnik_nazwa = d["podatnik_nazwa"]
    st.session_state.podatnik_kraj = d["podatnik_kraj"]
    st.session_state.podatnik_id = d["podatnik_id"]
    st.session_state.podatnik_rodzaj_id = d["podatnik_rodzaj_id"]
    st.session_state.podatnik_ulica = d.get("podatnik_ulica", "")
    st.session_state.podatnik_nr_domu = d.get("podatnik_nr_domu", "")
    st.session_state.podatnik_miejscowosc = d.get("podatnik_miejscowosc", "")
    st.session_state.podatnik_kod = d.get("podatnik_kod", "")
    st.session_state["_aktywny_slownik_klucz"] = klucz


# ═══════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("### 🏢 NIP Płatnika")

    nip_input = st.text_input(
        "NIP płatnika",
        value=st.session_state.platnik_nip,
        placeholder="0000000000",
        label_visibility="collapsed",
    )

    if st.button("🔍 Pobierz dane z MF API", use_container_width=True, type="primary"):
        nip_clean = nip_input.replace("-", "").replace(" ", "")
        with st.spinner("Pobieranie danych..."):
            wynik_mf = pobierz_dane_nip(nip_clean)
        if "blad" in wynik_mf:
            st.error(wynik_mf["blad"])
        else:
            st.session_state.platnik_nip = nip_clean
            st.session_state.platnik_nazwa = wynik_mf.get("nazwa", "")
            st.session_state.platnik_regon = wynik_mf.get("regon", "")
            st.session_state.platnik_ulica = wynik_mf.get("ulica", "")
            st.session_state.platnik_nr_domu = wynik_mf.get("nr_nieruchomosci", "")
            st.session_state.platnik_nr_lokalu = wynik_mf.get("nr_lokalu", "")
            st.session_state.platnik_miejscowosc = wynik_mf.get("miejscowosc", "")
            st.session_state.platnik_kod = wynik_mf.get("kod_pocztowy", "")
            st.success(f"✅ {wynik_mf.get('nazwa', '')}")

    if nip_input and nip_input != st.session_state.platnik_nip:
        if st.button("Zapisz NIP ręcznie", use_container_width=True):
            st.session_state.platnik_nip = nip_input.replace("-", "").replace(" ", "")

    # ── JPK_FA ──────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("### 📂 Pliki JPK_FA")

    uploaded = st.file_uploader(
        "Wybierz pliki XML",
        type=["xml"],
        accept_multiple_files=True,
        label_visibility="collapsed",
    )

    if uploaded:
        if st.button("📥 Wczytaj i parsuj", use_container_width=True, type="primary"):
            wszystkie_faktury, bledy_sum = [], []
            for uf in uploaded:
                content = uf.read().decode("utf-8", errors="replace")
                w = parsuj_jpk_fa(content, uf.name)
                bledy_sum.extend(w.bledy)
                wszystkie_faktury.extend(w.faktury)
                if w.platnik_nip and not st.session_state.platnik_nip:
                    st.session_state.platnik_nip = w.platnik_nip
                    st.session_state.platnik_nazwa = w.platnik_nazwa

            zb = WynikParsowania()
            zb.faktury = wszystkie_faktury
            zb.bledy = bledy_sum
            st.session_state.jpk_wyniki = [zb]
            st.session_state.grupy_kontrahentow = grupuj_wg_kontrahenta(zb)
            lf = len(wszystkie_faktury)
            lk = len(st.session_state.grupy_kontrahentow)
            st.success(f"✅ {lf} faktur | {lk} kontrahentów")
            for b in bledy_sum:
                st.warning(b)

    # ── Kontrahenci z JPK ────────────────────────────────────────────────
    grupy = st.session_state.grupy_kontrahentow
    if grupy:
        st.markdown("---")
        st.markdown("### 👥 Z pliku JPK_FA")
        for klucz, g in grupy.items():
            kw = g["suma_netto"]
            skrot = g["sprzedawca_nazwa"][:24] + "…" if len(g["sprzedawca_nazwa"]) > 24 else g["sprzedawca_nazwa"]
            lbl = f"{skrot}\n[{g['sprzedawca_kraj']}] {g['liczba_faktur']} fakt. · {kw:.2f} PLN"
            if st.button(lbl, key=f"jpk_{klucz}", use_container_width=True):
                st.session_state.aktywny_klucz = klucz
                sl_k = f"{g['sprzedawca_id']}@{g['sprzedawca_kraj']}"
                if sl_k in KONTRAHENCI:
                    _wczytaj_z_slownika(sl_k)
                else:
                    st.session_state.podatnik_nazwa = g["sprzedawca_nazwa"]
                    st.session_state.podatnik_kraj = g["sprzedawca_kraj"]
                    st.session_state.podatnik_id = g["sprzedawca_id"]
                    st.session_state["_aktywny_slownik_klucz"] = None

    # ── Słownik kontrahentów ─────────────────────────────────────────────
    st.markdown("---")
    st.markdown("### 📖 Słownik kontrahentów")
    szukaj = st.text_input(
        "Szukaj kontrahenta",
        placeholder="Google, Meta, LinkedIn…",
        label_visibility="collapsed",
        key="_szukaj",
    )
    for s_k, s_d in szukaj_kontrahenta(szukaj):
        lbl = f"{s_d.get('logo','🌍')} {s_d['nazwa_skrot']} [{s_d['podatnik_kraj']}]"
        if st.button(lbl, key=f"sl_{s_k}", use_container_width=True):
            _wczytaj_z_slownika(s_k)
            st.session_state.aktywny_klucz = None


# ═══════════════════════════════════════════════════════════════════════════
# NAGŁÓWEK
# ═══════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="abacus-header">
  <h1>🧾 Generator IFT-2R</h1>
  <p>Informacja o przychodach podatnika CIT niemającego siedziby w Polsce (wariant 12)</p>
  <span class="badge">Obowiązuje od 01.01.2026 · dochody od 2025 r.</span>
</div>
""", unsafe_allow_html=True)

# Aktywny kontrahent — pasek informacyjny
sk = st.session_state.get("_aktywny_slownik_klucz")
if sk and sk in KONTRAHENCI:
    sd = KONTRAHENCI[sk]
    uwaga = sd.get("uwaga", "")
    st.markdown(
        f'<div class="kontrahent-card">'
        f'{sd.get("logo","🌍")} <b>{sd["podatnik_nazwa"]}</b> [{sd["podatnik_kraj"]}] · '
        f'ID: <code>{sd["podatnik_id"]}</code> · domyślna sekcja: <b>{sd["domyslna_sekcja"]}</b>'
        + (f'<br><span style="color:#555">💡 {uwaga}</span>' if uwaga else "")
        + "</div>",
        unsafe_allow_html=True,
    )

# ═══════════════════════════════════════════════════════════════════════════
# ZAKŁADKI
# ═══════════════════════════════════════════════════════════════════════════
tabs = st.tabs([
    "📋 Nagłówek",
    "🏢 Część A — Płatnik",
    "🌍 Część B — Podatnik",
    "📊 Zestawienie JPK",
    "📂 Sekcje D–Q",
    "🔧 Uzupełnienia",
    "💾 Generuj XML",
])


# ── TAB 1: NAGŁÓWEK ─────────────────────────────────────────────────────────
with tabs[0]:
    st.subheader("Nagłówek deklaracji")

    col1, col2 = st.columns([1, 1])
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
        st.markdown(
            '<div class="info-box">🏛️ <b>Urząd skarbowy (Pole 6)</b><br>'
            'Lubelski Urząd Skarbowy w Lublinie<br>'
            '<b>Kod 0671</b> — stały dla wszystkich IFT-2R w Polsce</div>',
            unsafe_allow_html=True,
        )

    st.markdown("---")
    col3, col4 = st.columns(2)
    with col3:
        od = st.date_input(
            "**Pole 4 — Początek roku podatkowego**",
            value=datetime.strptime(st.session_state.okres_od, "%Y-%m-%d").date(),
        )
        st.session_state.okres_od = od.strftime("%Y-%m-%d")
    with col4:
        do_d = st.date_input(
            "**Pole 5 — Koniec roku podatkowego**",
            value=datetime.strptime(st.session_state.okres_do, "%Y-%m-%d").date(),
        )
        st.session_state.okres_do = do_d.strftime("%Y-%m-%d")

    st.caption(
        f"📅 Rok podatkowy: **{od.year}** · "
        f"Termin złożenia IFT-2R: **31 marca {od.year + 1}**"
    )


# ── TAB 2: CZĘŚĆ A — PŁATNIK ─────────────────────────────────────────────────
with tabs[1]:
    st.subheader("Część A — Dane płatnika")
    st.caption("Pola 1, 8–18. Kliknij 'Pobierz dane z MF API' w panelu bocznym aby wypełnić automatycznie.")

    col1, col2 = st.columns(2)
    with col1:
        st.session_state.platnik_nip = st.text_input(
            "**NIP płatnika (Pole 1)**",
            value=st.session_state.platnik_nip,
        )
        st.session_state.platnik_nazwa = st.text_input(
            "**Pełna nazwa (Pole 9)**",
            value=st.session_state.platnik_nazwa,
        )
        st.session_state.platnik_regon = st.text_input(
            "REGON (opcjonalnie)",
            value=st.session_state.platnik_regon,
        )
    with col2:
        st.session_state.platnik_ulica = st.text_input("Ulica", value=st.session_state.platnik_ulica)
        ca, cb = st.columns(2)
        with ca:
            st.session_state.platnik_nr_domu = st.text_input("Nr domu", value=st.session_state.platnik_nr_domu)
        with cb:
            st.session_state.platnik_nr_lokalu = st.text_input("Nr lokalu", value=st.session_state.platnik_nr_lokalu)
        st.session_state.platnik_miejscowosc = st.text_input("Miejscowość", value=st.session_state.platnik_miejscowosc)
        cc, cd = st.columns(2)
        with cc:
            st.session_state.platnik_kod = st.text_input("Kod pocztowy", value=st.session_state.platnik_kod)
        with cd:
            st.session_state.platnik_kraj = st.text_input("Kraj", value=st.session_state.platnik_kraj)

    with st.expander("Województwo / Powiat / Gmina"):
        cw, cp, cg = st.columns(3)
        with cw:
            st.session_state.platnik_wojewodztwo = st.text_input("Województwo", value=st.session_state.platnik_wojewodztwo)
        with cp:
            st.session_state.platnik_powiat = st.text_input("Powiat", value=st.session_state.platnik_powiat)
        with cg:
            st.session_state.platnik_gmina = st.text_input("Gmina", value=st.session_state.platnik_gmina)


# ── TAB 3: CZĘŚĆ B — PODATNIK ────────────────────────────────────────────────
with tabs[2]:
    st.subheader("Część B — Dane podatnika zagranicznego")
    st.caption("Pola 19–32. Wybierz kontrahenta ze słownika lub z JPK_FA w panelu bocznym.")

    sk2 = st.session_state.get("_aktywny_slownik_klucz")
    ak2 = st.session_state.aktywny_klucz
    grupy2 = st.session_state.grupy_kontrahentow

    if sk2 and sk2 in KONTRAHENCI:
        sd2 = KONTRAHENCI[sk2]
        st.success(f"{sd2.get('logo','🌍')} Ze słownika: **{sd2['podatnik_nazwa']}** [{sd2['podatnik_kraj']}]")
        if sd2.get("uwaga"):
            st.markdown(f'<div class="info-box">💡 {sd2["uwaga"]}</div>', unsafe_allow_html=True)
    elif ak2 and ak2 in grupy2:
        g2 = grupy2[ak2]
        st.success(f"📄 Z JPK_FA: **{g2['sprzedawca_nazwa']}** [{g2['sprzedawca_kraj']}]")

    col1, col2 = st.columns(2)
    with col1:
        st.session_state.podatnik_nazwa = st.text_input(
            "**Pełna nazwa (Pole 20)**",
            value=st.session_state.podatnik_nazwa,
        )
        st.session_state.podatnik_kraj = st.text_input(
            "**Kraj siedziby — kod 2-znakowy (Pole 25)**",
            value=st.session_state.podatnik_kraj,
            help="IE = Irlandia, DE = Niemcy, US = USA, NL = Holandia, LU = Luksemburg",
        )
        rod = st.radio(
            "**Rodzaj identyfikacji (Pole 23)**",
            options=[1, 2],
            format_func=lambda x: "1 — podatkowy (VAT ID)" if x == 1 else "2 — inny",
            index=st.session_state.podatnik_rodzaj_id - 1,
            horizontal=True,
        )
        st.session_state.podatnik_rodzaj_id = rod
        st.session_state.podatnik_id = st.text_input(
            "**Numer identyfikacyjny (Pole 24)**",
            value=st.session_state.podatnik_id,
        )
    with col2:
        st.markdown("**Adres siedziby (Pola 27–32)**")
        st.session_state.podatnik_ulica = st.text_input(
            "Ulica", value=st.session_state.podatnik_ulica, key="pod_ul")
        st.session_state.podatnik_nr_domu = st.text_input(
            "Nr domu", value=st.session_state.podatnik_nr_domu, key="pod_nr")
        st.session_state.podatnik_miejscowosc = st.text_input(
            "Miejscowość", value=st.session_state.podatnik_miejscowosc, key="pod_msc")
        st.session_state.podatnik_kod = st.text_input(
            "Kod pocztowy", value=st.session_state.podatnik_kod, key="pod_kod")


# ── TAB 4: ZESTAWIENIE JPK ───────────────────────────────────────────────────
with tabs[3]:
    st.subheader("Zestawienie faktur z pliku JPK_FA")

    grupy3 = st.session_state.grupy_kontrahentow
    if not grupy3:
        st.markdown(
            '<div class="info-box">⬆️ Wczytaj pliki JPK_FA w panelu bocznym, '
            'a tutaj pojawi się zestawienie faktur od zagranicznych kontrahentów.</div>',
            unsafe_allow_html=True,
        )
    else:
        opcje = {k: f"{g['sprzedawca_nazwa']} [{g['sprzedawca_kraj']}]" for k, g in grupy3.items()}
        ak3 = st.session_state.aktywny_klucz
        idx = list(opcje.keys()).index(ak3) if ak3 in opcje else 0
        wybrany = st.selectbox(
            "Kontrahent:",
            options=list(opcje.keys()),
            format_func=lambda k: opcje[k],
            index=idx,
        )
        if wybrany:
            st.session_state.aktywny_klucz = wybrany
            g3 = grupy3[wybrany]

            c1, c2, c3 = st.columns(3)
            c1.metric("Faktur", g3["liczba_faktur"])
            c2.metric("Suma netto", f"{g3['suma_netto']:.2f} {g3['waluta']}")
            c3.metric("Suma brutto", f"{g3['suma_brutto']:.2f} {g3['waluta']}")

            st.markdown("---")
            import pandas as pd
            rows = [{
                "Nr faktury": f.numer,
                "Data wystawienia": f.data_wystawienia,
                "Sprzedawca": f.sprzedawca_nazwa,
                "Kraj": f.sprzedawca_kraj,
                "ID sprzedawcy": f.sprzedawca_id,
                "Waluta": f.waluta,
                "Netto": float(f.netto),
                "VAT": float(f.vat),
                "Brutto": float(f.brutto),
                "Plik": f.zrodlo_plik,
            } for f in g3["faktury"]]
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

            st.markdown(
                '<div class="info-box">💡 Przejdź do zakładki <b>Sekcje D–Q</b>, '
                'aby przypisać sumę netto do właściwej kategorii IFT-2R.<br>'
                'Dla usług Google/Meta/LinkedIn → <b>sekcja K</b> (art. 21 ust. 1 pkt 2a).</div>',
                unsafe_allow_html=True,
            )


# ── TAB 5: SEKCJE D–Q ────────────────────────────────────────────────────────
with tabs[4]:
    st.subheader("Część D — Rodzaje przychodów i wysokość pobranego podatku")

    grupy4 = st.session_state.grupy_kontrahentow
    ak4 = st.session_state.aktywny_klucz
    suma_netto = Decimal("0")
    if grupy4 and ak4 and ak4 in grupy4:
        suma_netto = grupy4[ak4]["suma_netto"]
        g4 = grupy4[ak4]
        st.markdown(
            f'<div class="sekcja-card">'
            f'📄 <b>{g4["sprzedawca_nazwa"]}</b> [{g4["sprzedawca_kraj"]}] — '
            f'suma netto z JPK_FA: <span class="kwota-big">{suma_netto:.2f} {g4["waluta"]}</span>'
            f'</div>',
            unsafe_allow_html=True,
        )

    # Domyślna sekcja ze słownika
    sk5 = st.session_state.get("_aktywny_slownik_klucz")
    dom_sek = "K"
    dom_stk = 20
    if sk5 and sk5 in KONTRAHENCI:
        dom_sek = KONTRAHENCI[sk5].get("domyslna_sekcja", "K")
        dom_stk = KONTRAHENCI[sk5].get("domyslna_stawka", 20)

    with st.expander("➕ Dodaj wpis", expanded=True):
        opcje_sek = {k: f"{k} — {v['opis']}" for k, v in SEKCJE_D.items()}
        col1, col2 = st.columns([1, 3])
        with col1:
            sym = st.selectbox(
                "Sekcja",
                options=list(opcje_sek.keys()),
                format_func=lambda k: opcje_sek[k],
                index=list(opcje_sek.keys()).index(dom_sek),
            )
        with col2:
            st.caption(f"📌 {SEKCJE_D[sym]['opis']}")

        c3, c4, c5, c6 = st.columns(4)
        with c3:
            zwolniony = st.number_input(
                "Kwota zwolniona (kol. c)",
                min_value=0.0,
                value=float(suma_netto),
                step=0.01,
                format="%.2f",
                help="Kwota przychodu zwolnionego z opodatkowania (UPO / certyfikat rezydencji).",
            )
        with c4:
            opodatkowany = st.number_input(
                "Kwota opodatkowana (kol. d)",
                min_value=0.0,
                value=0.0,
                step=0.01,
                format="%.2f",
            )
        with c5:
            max_stk = float(SEKCJE_D[sym]["max_stawka"])
            dom_stk_val = min(float(dom_stk), max_stk)
            stawka = st.number_input(
                f"Stawka % (max {int(max_stk)})",
                min_value=0.0,
                max_value=max_stk,
                value=dom_stk_val,
                step=1.0,
                format="%.0f",
            )
        with c6:
            podatek = st.number_input(
                "Pobrany podatek (kol. e)",
                min_value=0.0,
                value=0.0,
                step=0.01,
                format="%.2f",
            )

        if st.button("➕ Dodaj pozycję", type="primary"):
            st.session_state.sekcje.append({
                "symbol": sym,
                "opis": SEKCJE_D[sym]["opis"],
                "zwolniony": f"{zwolniony:.2f}",
                "opodatkowany": f"{opodatkowany:.2f}",
                "stawka": f"{stawka:.0f}",
                "podatek": f"{podatek:.2f}",
            })
            st.success(f"✅ Dodano — sekcja {sym}")

    if st.session_state.sekcje:
        st.markdown("---")
        st.markdown("**Dodane pozycje:**")
        for i, s in enumerate(st.session_state.sekcje):
            cs, cd = st.columns([11, 1])
            with cs:
                st.markdown(
                    f'<div class="sekcja-card">'
                    f'<b>Sekcja {s["symbol"]}</b> &nbsp;·&nbsp; {s["opis"]}<br>'
                    f'Zwolniony: <b>{s["zwolniony"]}</b> &nbsp;|&nbsp; '
                    f'Opodatkowany: <b>{s["opodatkowany"]}</b> &nbsp;|&nbsp; '
                    f'Stawka: <b>{s["stawka"]}%</b> &nbsp;|&nbsp; '
                    f'Podatek: <b>{s["podatek"]}</b>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
            with cd:
                if st.button("🗑", key=f"del_{i}"):
                    st.session_state.sekcje.pop(i)
                    st.rerun()

        st.markdown("---")
        t_zw = sum(Decimal(s["zwolniony"]) for s in st.session_state.sekcje)
        t_op = sum(Decimal(s["opodatkowany"]) for s in st.session_state.sekcje)
        t_po = sum(Decimal(s["podatek"]) for s in st.session_state.sekcje)
        tc1, tc2, tc3 = st.columns(3)
        tc1.metric("Razem zwolniony", f"{t_zw:.2f}")
        tc2.metric("Razem opodatkowany", f"{t_op:.2f}")
        tc3.metric("Razem podatek", f"{t_po:.2f}")


# ── TAB 6: UZUPEŁNIENIA ──────────────────────────────────────────────────────
with tabs[5]:
    st.subheader("Informacje uzupełniające (R, S, T, U)")

    col1, col2 = st.columns(2)
    with col1:
        lm = st.number_input("**Pole 120 — Liczba miesięcy roku podatkowego**",
                             min_value=1, max_value=24, value=st.session_state.liczba_miesiecy)
        st.session_state.liczba_miesiecy = lm
        st.session_state.data_wniosku = st.text_input(
            "**Pole 121 — Data wniosku podatnika** (opcjonalne)",
            value=st.session_state.data_wniosku, placeholder="YYYY-MM-DD")
        st.session_state.data_przekazania = st.text_input(
            "**Pole 122 — Data przekazania informacji podatnikowi**",
            value=st.session_state.data_przekazania, placeholder="YYYY-MM-DD")
    with col2:
        st.session_state.podpisujacy_imie = st.text_input(
            "**Pole 123 — Imię osoby podpisującej**",
            value=st.session_state.podpisujacy_imie)
        st.session_state.podpisujacy_nazwisko = st.text_input(
            "**Pole 124 — Nazwisko**",
            value=st.session_state.podpisujacy_nazwisko)
        st.session_state.telefon = st.text_input(
            "**Pole 128 — Telefon**", value=st.session_state.telefon)
        st.session_state.email = st.text_input(
            "**Pole 129 — E-mail**", value=st.session_state.email)


# ── TAB 7: GENERUJ XML ───────────────────────────────────────────────────────
with tabs[6]:
    st.subheader("Generowanie pliku XML IFT-2R")

    bledy = []
    if not st.session_state.platnik_nip:
        bledy.append("Brak NIP płatnika — wypełnij Część A.")
    if not st.session_state.platnik_nazwa:
        bledy.append("Brak nazwy płatnika — wypełnij Część A.")
    if not st.session_state.podatnik_nazwa:
        bledy.append("Brak nazwy podatnika zagranicznego — wypełnij Część B.")
    if not st.session_state.podatnik_kraj:
        bledy.append("Brak kodu kraju podatnika — wypełnij Część B.")
    if not st.session_state.podatnik_id:
        bledy.append("Brak numeru identyfikacyjnego podatnika — wypełnij Część B.")
    if not st.session_state.sekcje:
        bledy.append("Brak pozycji w sekcji D — dodaj przynajmniej jedną pozycję.")

    if bledy:
        for b in bledy:
            st.error(f"❌ {b}")
    else:
        st.markdown(
            '<div class="info-box">✅ Wszystkie wymagane pola wypełnione. Możesz wygenerować plik XML.</div>',
            unsafe_allow_html=True,
        )

    if st.button("🔄 Generuj XML", type="primary", disabled=bool(bledy)):
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
            xml_out = generuj_xml(dane)
            st.session_state.xml_wygenerowany = xml_out
        except Exception as e:
            st.error(f"Błąd generowania: {e}")

    if st.session_state.xml_wygenerowany:
        nip_p = st.session_state.platnik_nip
        rok = st.session_state.okres_od[:4]
        nazwa_pliku = f"IFT-2R_{nip_p}_{rok}.xml"

        st.download_button(
            label="⬇️ Pobierz plik XML",
            data=st.session_state.xml_wygenerowany.encode("utf-8"),
            file_name=nazwa_pliku,
            mime="application/xml",
            type="primary",
        )
        st.markdown("---")
        st.code(st.session_state.xml_wygenerowany, language="xml")
        st.markdown(
            '<div class="warn-box">'
            '📌 <b>Pamiętaj:</b> wygenerowany plik XML wyślij przez system <b>e-Deklaracje</b> '
            'do <b>Lubelskiego Urzędu Skarbowego w Lublinie</b> z <b>kwalifikowanym podpisem elektronicznym</b>. '
            'Termin: do końca marca roku następującego po roku podatkowym.'
            '</div>',
            unsafe_allow_html=True,
        )
