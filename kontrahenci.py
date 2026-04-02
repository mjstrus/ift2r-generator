"""
Słownik predefiniowanych kontrahentów zagranicznych (podatnicy IFT-2R).

Dane: nazwa, kraj, ID podatkowy, adres siedziby, domyślna sekcja D, domyślna stawka.
Źródło: oficjalne dane rejestrowe + certyfikaty rezydencji.
"""

# Klucz: identyfikator wewnętrzny (ID_podatkowy@kraj)
KONTRAHENCI: dict[str, dict] = {

    # ── GOOGLE ──────────────────────────────────────────────────────────────
    "6388047@IE": {
        "nazwa_skrot": "Google Ireland",
        "podatnik_nazwa": "GOOGLE IRELAND LIMITED",
        "podatnik_kraj": "IE",
        "podatnik_id": "6388047",
        "podatnik_rodzaj_id": 2,          # 2 = inny (nie NIP PL)
        "podatnik_ulica": "Gordon House, Barrow Street",
        "podatnik_nr_domu": "",
        "podatnik_miejscowosc": "Dublin 4",
        "podatnik_kod": "D04 E5W5",
        "domyslna_sekcja": "K",           # art. 21 ust. 1 pkt 2a – usługi reklamowe
        "domyslna_stawka": 20,
        "uwaga": "Certyfikat rezydencji IE → zwolnienie z UPO PL-IE. Wykaż jako zwolniony.",
        "logo": "🔍",
    },

    # ── META (Facebook) ─────────────────────────────────────────────────────
    "9692928F@IE": {
        "nazwa_skrot": "Meta (Facebook) Ireland",
        "podatnik_nazwa": "META PLATFORMS IRELAND LIMITED",
        "podatnik_kraj": "IE",
        "podatnik_id": "9692928F",
        "podatnik_rodzaj_id": 2,
        "podatnik_ulica": "4 Grand Canal Square, Grand Canal Harbour",
        "podatnik_nr_domu": "",
        "podatnik_miejscowosc": "Dublin 2",
        "podatnik_kod": "D02 X525",
        "domyslna_sekcja": "K",
        "domyslna_stawka": 20,
        "uwaga": "Certyfikat rezydencji IE → zwolnienie z UPO PL-IE. Wykaż jako zwolniony.",
        "logo": "📘",
    },

    # ── LINKEDIN ─────────────────────────────────────────────────────────────
    "IE9740425P@IE": {
        "nazwa_skrot": "LinkedIn Ireland",
        "podatnik_nazwa": "LINKEDIN IRELAND UNLIMITED COMPANY",
        "podatnik_kraj": "IE",
        "podatnik_id": "IE9740425P",
        "podatnik_rodzaj_id": 2,
        "podatnik_ulica": "Wilton Place",
        "podatnik_nr_domu": "70",
        "podatnik_miejscowosc": "Dublin 2",
        "podatnik_kod": "D02 R296",
        "domyslna_sekcja": "K",
        "domyslna_stawka": 20,
        "uwaga": "Certyfikat rezydencji IE → zwolnienie z UPO PL-IE. Wykaż jako zwolniony.",
        "logo": "💼",
    },

    # ── MICROSOFT ────────────────────────────────────────────────────────────
    "IE8256796U@IE": {
        "nazwa_skrot": "Microsoft Ireland",
        "podatnik_nazwa": "MICROSOFT IRELAND OPERATIONS LIMITED",
        "podatnik_kraj": "IE",
        "podatnik_id": "IE8256796U",
        "podatnik_rodzaj_id": 2,
        "podatnik_ulica": "One Microsoft Place, South County Business Park, Leopardstown",
        "podatnik_nr_domu": "",
        "podatnik_miejscowosc": "Dublin 18",
        "podatnik_kod": "D18 P521",
        "domyslna_sekcja": "K",
        "domyslna_stawka": 20,
        "uwaga": "Certyfikat rezydencji IE → zwolnienie z UPO PL-IE. Wykaż jako zwolniony.",
        "logo": "🪟",
    },

    # ── ADOBE ────────────────────────────────────────────────────────────────
    "IE4116127E@IE": {
        "nazwa_skrot": "Adobe Systems Ireland",
        "podatnik_nazwa": "ADOBE SYSTEMS SOFTWARE IRELAND LIMITED",
        "podatnik_kraj": "IE",
        "podatnik_id": "IE4116127E",
        "podatnik_rodzaj_id": 2,
        "podatnik_ulica": "4-6 Riverwalk, Citywest Business Campus",
        "podatnik_nr_domu": "",
        "podatnik_miejscowosc": "Dublin 24",
        "podatnik_kod": "D24 RX04",
        "domyslna_sekcja": "K",
        "domyslna_stawka": 20,
        "uwaga": "Certyfikat rezydencji IE → zwolnienie z UPO PL-IE.",
        "logo": "🅰️",
    },

    # ── AMAZON WEB SERVICES ─────────────────────────────────────────────────
    "IE9S99175L@IE": {
        "nazwa_skrot": "Amazon Web Services EMEA",
        "podatnik_nazwa": "AMAZON WEB SERVICES EMEA SARL",
        "podatnik_kraj": "LU",
        "podatnik_id": "LU26375245",
        "podatnik_rodzaj_id": 2,
        "podatnik_ulica": "38 Avenue John F. Kennedy",
        "podatnik_nr_domu": "",
        "podatnik_miejscowosc": "Luxembourg",
        "podatnik_kod": "L-1855",
        "domyslna_sekcja": "K",
        "domyslna_stawka": 20,
        "uwaga": "AWS fakturuje przez Luksemburg. Certyfikat rezydencji LU → UPO PL-LU.",
        "logo": "☁️",
    },

    # ── APPLE ────────────────────────────────────────────────────────────────
    "IE9700053D@IE": {
        "nazwa_skrot": "Apple Distribution International",
        "podatnik_nazwa": "APPLE DISTRIBUTION INTERNATIONAL LIMITED",
        "podatnik_kraj": "IE",
        "podatnik_id": "IE9700053D",
        "podatnik_rodzaj_id": 2,
        "podatnik_ulica": "Hollyhill Industrial Estate, Hollyhill",
        "podatnik_nr_domu": "",
        "podatnik_miejscowosc": "Cork",
        "podatnik_kod": "T23 YK84",
        "domyslna_sekcja": "K",
        "domyslna_stawka": 20,
        "uwaga": "Certyfikat rezydencji IE → zwolnienie z UPO PL-IE.",
        "logo": "🍎",
    },

    # ── CANVA ────────────────────────────────────────────────────────────────
    "46460965@AU": {
        "nazwa_skrot": "Canva Pty Ltd",
        "podatnik_nazwa": "CANVA PTY LTD",
        "podatnik_kraj": "AU",
        "podatnik_id": "46460965",
        "podatnik_rodzaj_id": 2,
        "podatnik_ulica": "110 Kippax Street",
        "podatnik_nr_domu": "",
        "podatnik_miejscowosc": "Surry Hills, NSW",
        "podatnik_kod": "2010",
        "domyslna_sekcja": "K",
        "domyslna_stawka": 20,
        "uwaga": "Australia – sprawdź UPO PL-AU lub zastosuj stawkę krajową 20%.",
        "logo": "🎨",
    },

    # ── DROPBOX ─────────────────────────────────────────────────────────────
    "IE9820477B@IE": {
        "nazwa_skrot": "Dropbox International",
        "podatnik_nazwa": "DROPBOX INTERNATIONAL UNLIMITED COMPANY",
        "podatnik_kraj": "IE",
        "podatnik_id": "IE9820477B",
        "podatnik_rodzaj_id": 2,
        "podatnik_ulica": "One Park Place, Hatch Street Upper",
        "podatnik_nr_domu": "",
        "podatnik_miejscowosc": "Dublin 2",
        "podatnik_kod": "D02 E651",
        "domyslna_sekcja": "K",
        "domyslna_stawka": 20,
        "uwaga": "Certyfikat rezydencji IE → zwolnienie z UPO PL-IE.",
        "logo": "📦",
    },

    # ── NETFLIX ──────────────────────────────────────────────────────────────
    "IE9397961L@IE": {
        "nazwa_skrot": "Netflix International",
        "podatnik_nazwa": "NETFLIX INTERNATIONAL B.V.",
        "podatnik_kraj": "NL",
        "podatnik_id": "NL856406553B01",
        "podatnik_rodzaj_id": 2,
        "podatnik_ulica": "Astronaut 1",
        "podatnik_nr_domu": "",
        "podatnik_miejscowosc": "Hoofddorp",
        "podatnik_kod": "2132 HG",
        "domyslna_sekcja": "I",           # należności licencyjne – dostęp do treści
        "domyslna_stawka": 20,
        "uwaga": "Netflix fakturuje przez NL. Certyfikat rezydencji NL → UPO PL-NL.",
        "logo": "🎬",
    },

    # ── SPOTIFY ──────────────────────────────────────────────────────────────
    "556703748001@SE": {
        "nazwa_skrot": "Spotify AB",
        "podatnik_nazwa": "SPOTIFY AB",
        "podatnik_kraj": "SE",
        "podatnik_id": "556703748001",
        "podatnik_rodzaj_id": 2,
        "podatnik_ulica": "Regeringsgatan 19",
        "podatnik_nr_domu": "",
        "podatnik_miejscowosc": "Stockholm",
        "podatnik_kod": "111 53",
        "domyslna_sekcja": "I",
        "domyslna_stawka": 20,
        "uwaga": "Szwecja → UPO PL-SE. Licencje na muzykę art. 21 ust. 1 pkt 1.",
        "logo": "🎵",
    },

    # ── NOTION ───────────────────────────────────────────────────────────────
    "US@NOTION": {
        "nazwa_skrot": "Notion Labs (USA)",
        "podatnik_nazwa": "NOTION LABS, INC.",
        "podatnik_kraj": "US",
        "podatnik_id": "88-3176691",
        "podatnik_rodzaj_id": 2,
        "podatnik_ulica": "2300 Harrison Street",
        "podatnik_nr_domu": "",
        "podatnik_miejscowosc": "San Francisco, CA",
        "podatnik_kod": "94110",
        "domyslna_sekcja": "K",
        "domyslna_stawka": 20,
        "uwaga": "USA → UPO PL-USA. Usługi SaaS przetwarzanie danych art. 21 ust. 1 pkt 2a.",
        "logo": "📝",
    },

    # ── SLACK / SALESFORCE ───────────────────────────────────────────────────
    "US@SLACK": {
        "nazwa_skrot": "Slack Technologies (USA)",
        "podatnik_nazwa": "SLACK TECHNOLOGIES, LLC",
        "podatnik_kraj": "US",
        "podatnik_id": "47-4759489",
        "podatnik_rodzaj_id": 2,
        "podatnik_ulica": "500 Howard Street",
        "podatnik_nr_domu": "",
        "podatnik_miejscowosc": "San Francisco, CA",
        "podatnik_kod": "94105",
        "domyslna_sekcja": "K",
        "domyslna_stawka": 20,
        "uwaga": "USA → UPO PL-USA. Przetwarzanie danych / usługi SaaS.",
        "logo": "💬",
    },

    # ── XERO ─────────────────────────────────────────────────────────────────
    "NZ@XERO": {
        "nazwa_skrot": "Xero Limited",
        "podatnik_nazwa": "XERO LIMITED",
        "podatnik_kraj": "NZ",
        "podatnik_id": "1780216",
        "podatnik_rodzaj_id": 2,
        "podatnik_ulica": "19 Bisley Drive",
        "podatnik_nr_domu": "",
        "podatnik_miejscowosc": "Wellington",
        "podatnik_kod": "6011",
        "domyslna_sekcja": "K",
        "domyslna_stawka": 20,
        "uwaga": "Nowa Zelandia – brak UPO z PL. Stawka krajowa 20%. Sprawdź certyfikat.",
        "logo": "📊",
    },
}


def szukaj_kontrahenta(fraza: str) -> list[tuple[str, dict]]:
    """Wyszukuje kontrahentów po frazie (nazwa, kraj, ID)."""
    fraza = fraza.lower().strip()
    if not fraza:
        return list(KONTRAHENCI.items())
    wyniki = []
    for klucz, dane in KONTRAHENCI.items():
        if (fraza in dane["podatnik_nazwa"].lower() or
                fraza in dane["nazwa_skrot"].lower() or
                fraza in dane["podatnik_kraj"].lower() or
                fraza in dane["podatnik_id"].lower()):
            wyniki.append((klucz, dane))
    return wyniki


def pobierz_kontrahenta(klucz: str) -> dict | None:
    return KONTRAHENCI.get(klucz)
