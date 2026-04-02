"""Generator pliku XML IFT-2R (wariant 12) zgodnego ze schematem MF."""

from decimal import Decimal
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom
from datetime import date


IFT2R_NS = "http://crd.gov.pl/wzor/2025/10/27/13953/"

# Stałe wartości
KOD_URZEDU_LUBELSKI = "0671"


# ──────────────────────────────────────────────
# Sekcje D szczegółowe (kategorie przychodów)
# ──────────────────────────────────────────────
SEKCJE_D = {
    "E": {
        "opis": "Opłaty żegluga morska (art. 21 ust. 1 pkt 3)",
        "pola": {"zwolniony": "P_33", "opodatkowany": "P_34", "stawka": "P_35", "podatek": "P_36"},
        "max_stawka": 10,
    },
    "F": {
        "opis": "Przychody żegluga powietrzna",
        "pola": {"zwolniony": "P_37", "opodatkowany": "P_38", "stawka": "P_39", "podatek": "P_40"},
        "max_stawka": 10,
    },
    "G": {
        "opis": "Dywidendy i udziały w zyskach (art. 22)",
        "pola": {"zwolniony": "P_41", "opodatkowany": "P_42", "stawka": "P_43", "podatek": "P_44"},
        "max_stawka": 19,
    },
    "H": {
        "opis": "Odsetki (art. 21 ust. 1 pkt 1)",
        "pola": {"zwolniony": "P_45", "opodatkowany": "P_46", "stawka": "P_47", "podatek": "P_48"},
        "max_stawka": 20,
    },
    "I": {
        "opis": "Należności licencyjne (art. 21 ust. 1 pkt 1)",
        "pola": {"zwolniony": "P_49", "opodatkowany": "P_50", "stawka": "P_51", "podatek": "P_52"},
        "max_stawka": 20,
    },
    "J": {
        "opis": "Działalność widowiskowa, rozrywkowa lub sportowa (art. 21 ust. 1 pkt 1)",
        "pola": {"zwolniony": "P_53", "opodatkowany": "P_54", "stawka": "P_55", "podatek": "P_56"},
        "max_stawka": 20,
    },
    "K": {
        "opis": "Usługi niematerialne: doradcze, reklamowe, badania rynku, zarządzanie, przetwarzanie danych, rekrutacja, gwarancje itp. (art. 21 ust. 1 pkt 2a)",
        "pola": {"zwolniony": "P_57", "opodatkowany": "P_58", "stawka": "P_59", "podatek": "P_60"},
        "max_stawka": 20,
    },
    "L": {
        "opis": "Art. 21 CIT – odsetki (rozliczenie szczegółowe)",
        "pola": {"zwolniony": "P_61", "opodatkowany": "P_62", "stawka": "P_63", "podatek": "P_64"},
        "max_stawka": 20,
    },
    "M": {
        "opis": "Art. 21 CIT – należności licencyjne (rozliczenie szczegółowe)",
        "pola": {"zwolniony": "P_65", "opodatkowany": "P_66", "stawka": "P_67", "podatek": "P_68"},
        "max_stawka": 20,
    },
    "N": {
        "opis": "Art. 22 CIT – dywidendy (rozliczenie szczegółowe)",
        "pola": {"zwolniony": "P_69", "opodatkowany": "P_70", "stawka": "P_71", "podatek": "P_72"},
        "max_stawka": 19,
    },
    "O": {
        "opis": "Art. 21 CIT – pozostałe przychody (inne niż H, I, J, K)",
        "pola": {"zwolniony": "P_73", "opodatkowany": "P_74", "stawka": "P_75", "podatek": "P_76"},
        "max_stawka": 20,
    },
    "P": {
        "opis": "Zyski kapitałowe do rajów podatkowych (art. 7b ust. 1 pkt 3-6)",
        "pola": {"zwolniony": "P_77", "opodatkowany": "P_78", "stawka": "P_79", "podatek": "P_80"},
        "max_stawka": 20,
    },
}


def _fmt_dec(val) -> str:
    """Formatuje Decimal do stringa z 2 miejscami po przecinku."""
    try:
        d = Decimal(str(val))
        return str(d.quantize(Decimal("0.01")))
    except Exception:
        return "0.00"


def _fmt_date(d: str) -> str:
    """Zwraca datę w formacie YYYY-MM-DD."""
    return d


def generuj_xml(dane: dict) -> str:
    """
    Generuje XML IFT-2R wariant 12.

    dane = {
        # Nagłówek
        "cel_zlozenia": 1,           # 1=złożenie, 2=korekta
        "okres_od": "2025-01-01",
        "okres_do": "2025-12-31",

        # Podmiot1 - Płatnik
        "platnik_nip": "7162827437",
        "platnik_nazwa": "FJORDNETT Sp. z o.o.",
        "platnik_regon": "",         # opcjonalny
        "platnik_kraj": "PL",
        "platnik_wojewodztwo": "",
        "platnik_powiat": "",
        "platnik_gmina": "",
        "platnik_ulica": "",
        "platnik_nr_domu": "",
        "platnik_nr_lokalu": "",
        "platnik_miejscowosc": "",
        "platnik_kod": "",

        # Podmiot2 - Podatnik zagraniczny
        "podatnik_nazwa": "GOOGLE IRELAND LIMITED",
        "podatnik_kraj": "IE",
        "podatnik_id": "6388047",
        "podatnik_rodzaj_id": 2,     # 1=podatkowy, 2=inny
        "podatnik_data_rozpoczecia": "", # opcjonalna
        "podatnik_ulica": "",
        "podatnik_nr_domu": "",
        "podatnik_nr_lokalu": "",
        "podatnik_miejscowosc": "",
        "podatnik_kod": "",

        # Sekcje szczegółowe - lista wpisów
        "sekcje": [
            {
                "symbol": "K",       # E, F, G, H, I, J, K, L, M, N, O, P
                "zwolniony": "454.82",
                "opodatkowany": "0.00",
                "stawka": "20",
                "podatek": "0.00",
            }
        ],

        # Miesięczny podział (Q) - opcjonalny
        "miesiace": {               # klucz: "2025-01", wartość: kwota podatku
            # np. "2025-02": "0.00"
        },

        # Informacje uzupełniające
        "liczba_miesiecy": 12,
        "data_wniosku": "",          # pole 121 - opcjonalne
        "data_przekazania": "",      # pole 122 - opcjonalne

        # Osoba podpisująca (tylko do metadanych, XML podpisuje e-Deklaracje)
        "podpisujacy_imie": "",
        "podpisujacy_nazwisko": "",
        "data_sporzadzenia": "",
        "telefon": "",
        "email": "",
    }
    """
    root = Element("Deklaracja")
    root.set("xmlns", IFT2R_NS)

    # ── NAGŁÓWEK ──────────────────────────────────────────────────────────
    nagl = SubElement(root, "Naglowek")

    kod = SubElement(nagl, "KodFormularza")
    kod.set("kodSystemowy", "IFT-2R (12)")
    kod.set("kodPodatku", "CIT")
    kod.set("rodzajZobowiazania", "Z")
    kod.set("wersjaSchemy", "1-0E")
    kod.text = "IFT-2/IFT-2R"

    SubElement(nagl, "WariantFormularza").text = "12"

    cel = SubElement(nagl, "CelZlozenia")
    cel.set("poz", "P_7")
    cel.text = str(dane.get("cel_zlozenia", 1))

    od = SubElement(nagl, "OkresOd")
    od.set("poz", "P_4")
    od.text = dane.get("okres_od", "")

    do = SubElement(nagl, "OkresDo")
    do.set("poz", "P_5")
    do.text = dane.get("okres_do", "")

    SubElement(nagl, "KodUrzedu").text = KOD_URZEDU_LUBELSKI

    # ── PODMIOT1 – Płatnik ───────────────────────────────────────────────
    p1 = SubElement(root, "Podmiot1")
    p1.set("rola", "Płatnik/Podmiot (Wypłacający Należność)")

    # Identyfikator
    nip_el = SubElement(p1, "NIP")
    nip_el.text = dane.get("platnik_nip", "")

    nazwa_el = SubElement(p1, "PelnaNazwa")
    nazwa_el.text = dane.get("platnik_nazwa", "")

    regon = dane.get("platnik_regon", "")
    if regon:
        SubElement(p1, "REGON").text = regon

    # Adres
    adres_p1 = SubElement(p1, "AdresZamieszkaniaSiedziby")
    adres_p1.set("rodzajAdresu", "RAD")

    _dodaj_adres_pl(adres_p1, dane, prefix="platnik_")

    # ── PODMIOT2 – Podatnik zagraniczny ──────────────────────────────────
    p2 = SubElement(root, "Podmiot2")
    p2.set("rola", "Podatnik (Odbiorca Należności)")

    osoba = SubElement(p2, "OsobaNieFizZagr")
    nazwa_p2 = SubElement(osoba, "PelnaNazwa")
    nazwa_p2.text = dane.get("podatnik_nazwa", "")

    kraj_p2 = SubElement(osoba, "KrajSiedziby")
    kraj_p2.text = dane.get("podatnik_kraj", "")

    data_rozp = dane.get("podatnik_data_rozpoczecia", "")
    if data_rozp:
        dr_el = SubElement(osoba, "DataRozpoczeciaDzialalnosci")
        dr_el.set("poz", "P_23")
        dr_el.text = data_rozp

    rod_id = SubElement(osoba, "RodzajIdentyfikacji")
    rod_id.set("poz", "P_24")
    rod_id.text = str(dane.get("podatnik_rodzaj_id", 2))

    num_id = SubElement(osoba, "NumerIdentyfikacyjnyPodatnika")
    num_id.set("poz", "P_25")
    num_id.text = dane.get("podatnik_id", "")

    kraj_id = SubElement(osoba, "KodKrajuWydania")
    kraj_id.set("poz", "P_26")
    kraj_id.text = dane.get("podatnik_kraj", "")

    adres_p2 = SubElement(p2, "AdresSiedziby")
    adres_p2.set("rodzajAdresu", "RAD")
    _dodaj_adres_zagr(adres_p2, dane, prefix="podatnik_")

    # ── POZYCJE SZCZEGÓŁOWE ───────────────────────────────────────────────
    pozycje = SubElement(root, "PozycjeSzczegolowe")

    for sekcja in dane.get("sekcje", []):
        sym = sekcja.get("symbol", "")
        if sym not in SEKCJE_D:
            continue
        pola = SEKCJE_D[sym]["pola"]

        zwolniony = sekcja.get("zwolniony", "0.00")
        opodatkowany = sekcja.get("opodatkowany", "0.00")
        stawka = sekcja.get("stawka", "0")
        podatek = sekcja.get("podatek", "0.00")

        SubElement(pozycje, pola["zwolniony"]).text = _fmt_dec(zwolniony)
        SubElement(pozycje, pola["opodatkowany"]).text = _fmt_dec(opodatkowany)
        SubElement(pozycje, pola["stawka"]).text = str(stawka)
        SubElement(pozycje, pola["podatek"]).text = _fmt_dec(podatek)

    # Miesięczny podział Q (P_113, P_119 i inne)
    # P_72..P_119: 48 pól = 12 miesięcy × 4 pola (zwolniony, opodatkowany, stawka, podatek)
    # Numery: mies. 1 → P_81..P_84, ..., mies. 12 → P_117..P_120
    # UWAGA: Pola Q są wg kolejności od P_81 do P_120 (to jest robocze założenie)
    # W szablonie MF widnieją tylko P_113 i P_119 = 0
    # Na razie wypełniamy je jako 0 (wymagane pole)
    SubElement(pozycje, "P_113").text = "0"
    SubElement(pozycje, "P_119").text = "0"

    # ── POUCZENIE (wymagane) ──────────────────────────────────────────────
    pouczenie = SubElement(root, "Pouczenie")
    pouczenie.text = (
        "Za uchybienie obowiązkom płatnika/podmiotu grozi odpowiedzialność przewidziana "
        "w Kodeksie karnym skarbowym. [The infringement of tax remitter's / entity's duties "
        "shall be subject to the sanctions provided for the Fiscal Penal Code.]"
    )

    # ── FORMATOWANIE ──────────────────────────────────────────────────────
    xml_str = tostring(root, encoding="unicode")
    dom = minidom.parseString(f'<?xml version="1.0" encoding="UTF-8"?>{xml_str}')
    return dom.toprettyxml(indent="  ", encoding=None).replace(
        '<?xml version="1.0" ?>', '<?xml version="1.0" encoding="UTF-8"?>'
    )


def _dodaj_adres_pl(parent: Element, dane: dict, prefix: str):
    """Dodaje adres polski (płatnik)."""
    kraj = dane.get(f"{prefix}kraj", "PL")
    SubElement(parent, "KodKraju").text = kraj

    woj = dane.get(f"{prefix}wojewodztwo", "")
    if woj:
        SubElement(parent, "Wojewodztwo").text = woj

    powiat = dane.get(f"{prefix}powiat", "")
    if powiat:
        SubElement(parent, "Powiat").text = powiat

    gmina = dane.get(f"{prefix}gmina", "")
    if gmina:
        SubElement(parent, "Gmina").text = gmina

    ulica = dane.get(f"{prefix}ulica", "")
    if ulica:
        SubElement(parent, "Ulica").text = ulica

    nr_domu = dane.get(f"{prefix}nr_domu", "")
    if nr_domu:
        SubElement(parent, "NrDomu").text = nr_domu

    nr_lok = dane.get(f"{prefix}nr_lokalu", "")
    if nr_lok:
        SubElement(parent, "NrLokalu").text = nr_lok

    msc = dane.get(f"{prefix}miejscowosc", "")
    if msc:
        SubElement(parent, "Miejscowosc").text = msc

    kod = dane.get(f"{prefix}kod", "")
    if kod:
        SubElement(parent, "KodPocztowy").text = kod


def _dodaj_adres_zagr(parent: Element, dane: dict, prefix: str):
    """Dodaje adres zagraniczny (podatnik)."""
    SubElement(parent, "KodKraju").text = dane.get(f"{prefix}kraj", "")

    ulica = dane.get(f"{prefix}ulica", "")
    nr_domu = dane.get(f"{prefix}nr_domu", "")
    if ulica or nr_domu:
        SubElement(parent, "Ulica").text = f"{ulica} {nr_domu}".strip()

    msc = dane.get(f"{prefix}miejscowosc", "")
    if msc:
        SubElement(parent, "Miejscowosc").text = msc

    kod = dane.get(f"{prefix}kod", "")
    if kod:
        SubElement(parent, "KodPocztowy").text = kod
