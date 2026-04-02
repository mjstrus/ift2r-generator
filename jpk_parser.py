"""Parser plików JPK_FA (4) - ekstrakcja danych o fakturach od zagranicznych kontrahentów."""

import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from typing import Optional
from decimal import Decimal, ROUND_HALF_UP


JPK_NS = "http://jpk.mf.gov.pl/wzor/2022/02/17/02171/"
NS2 = "http://crd.gov.pl/xml/schematy/dziedzinowe/mf/2018/08/24/eD/DefinicjeTypy/"

NS_MAP = {
    "jpk": JPK_NS,
    "ns2": NS2,
}


@dataclass
class Faktura:
    numer: str
    data_wystawienia: str
    data_sprzedazy: str
    sprzedawca_nazwa: str
    sprzedawca_kraj: str
    sprzedawca_id: str
    nabywca_nip: str
    nabywca_nazwa: str
    waluta: str
    netto: Decimal
    vat: Decimal
    brutto: Decimal
    zrodlo_plik: str = ""


@dataclass
class WynikParsowania:
    faktury: list[Faktura] = field(default_factory=list)
    platnik_nip: str = ""
    platnik_nazwa: str = ""
    data_od: str = ""
    data_do: str = ""
    bledy: list[str] = field(default_factory=list)
    ostrzezenia: list[str] = field(default_factory=list)


def _txt(element, tag: str, ns: str = JPK_NS, default: str = "") -> str:
    """Bezpieczne odczytanie tekstu z elementu XML."""
    found = element.find(f"{{{ns}}}{tag}")
    if found is not None and found.text:
        return found.text.strip()
    return default


def _dec(element, tag: str, ns: str = JPK_NS) -> Decimal:
    """Odczyt wartości dziesiętnej z elementu XML."""
    val = _txt(element, tag, ns)
    if val:
        try:
            return Decimal(val)
        except Exception:
            pass
    return Decimal("0")


def parsuj_jpk_fa(xml_content: str, nazwa_pliku: str = "") -> WynikParsowania:
    """Parsuje plik JPK_FA (4) i zwraca listę faktur od zagranicznych kontrahentów."""
    wynik = WynikParsowania()

    try:
        root = ET.fromstring(xml_content)
    except ET.ParseError as e:
        wynik.bledy.append(f"Błąd parsowania XML: {e}")
        return wynik

    # Nagłówek
    naglowek = root.find(f"{{{JPK_NS}}}Naglowek")
    if naglowek is not None:
        wynik.data_od = _txt(naglowek, "DataOd")
        wynik.data_do = _txt(naglowek, "DataDo")

    # Podmiot1 (płatnik)
    podmiot1 = root.find(f"{{{JPK_NS}}}Podmiot1")
    if podmiot1 is not None:
        ident = podmiot1.find(f"{{{JPK_NS}}}IdentyfikatorPodmiotu")
        if ident is not None:
            wynik.platnik_nip = _txt(ident, "NIP")
            wynik.platnik_nazwa = _txt(ident, "PelnaNazwa")

    # Faktury
    for faktura_el in root.findall(f"{{{JPK_NS}}}Faktura"):
        try:
            sprzedawca_kraj = _txt(faktura_el, "P_4A")
            sprzedawca_id = _txt(faktura_el, "P_4B")
            sprzedawca_nazwa = _txt(faktura_el, "P_3C")

            # Pomijamy faktury od polskich kontrahentów
            if not sprzedawca_kraj or sprzedawca_kraj.upper() == "PL":
                wynik.ostrzezenia.append(
                    f"Faktura {_txt(faktura_el, 'P_2A')} od polskiego kontrahenta - pomijam."
                )
                continue

            netto = _dec(faktura_el, "P_13_1")
            # Suma wszystkich stawek netto jeśli jest więcej
            for i in range(2, 6):
                n = _dec(faktura_el, f"P_13_{i}")
                netto += n

            vat = _dec(faktura_el, "P_14_1")
            for i in range(2, 6):
                v = _dec(faktura_el, f"P_14_{i}")
                vat += v

            brutto = _dec(faktura_el, "P_15")
            if brutto == 0:
                brutto = netto + vat

            f = Faktura(
                numer=_txt(faktura_el, "P_2A"),
                data_wystawienia=_txt(faktura_el, "P_1"),
                data_sprzedazy=_txt(faktura_el, "P_6") or _txt(faktura_el, "P_1"),
                sprzedawca_nazwa=sprzedawca_nazwa,
                sprzedawca_kraj=sprzedawca_kraj,
                sprzedawca_id=sprzedawca_id,
                nabywca_nip=_txt(faktura_el, "P_5B"),
                nabywca_nazwa=_txt(faktura_el, "P_3A"),
                waluta=_txt(faktura_el, "KodWaluty") or "PLN",
                netto=netto,
                vat=vat,
                brutto=brutto,
                zrodlo_plik=nazwa_pliku,
            )
            wynik.faktury.append(f)

        except Exception as e:
            wynik.bledy.append(f"Błąd w fakturze: {e}")

    return wynik


def grupuj_wg_kontrahenta(wynik: WynikParsowania) -> dict:
    """Grupuje faktury wg kontrahenta (sprzedawca_id + kraj) i sumuje wartości."""
    grupy: dict[str, dict] = {}

    for f in wynik.faktury:
        klucz = f"{f.sprzedawca_id}@{f.sprzedawca_kraj}"
        if klucz not in grupy:
            grupy[klucz] = {
                "sprzedawca_nazwa": f.sprzedawca_nazwa,
                "sprzedawca_kraj": f.sprzedawca_kraj,
                "sprzedawca_id": f.sprzedawca_id,
                "waluta": f.waluta,
                "suma_netto": Decimal("0"),
                "suma_vat": Decimal("0"),
                "suma_brutto": Decimal("0"),
                "liczba_faktur": 0,
                "faktury": [],
            }
        g = grupy[klucz]
        g["suma_netto"] += f.netto
        g["suma_vat"] += f.vat
        g["suma_brutto"] += f.brutto
        g["liczba_faktur"] += 1
        g["faktury"].append(f)

    return grupy
