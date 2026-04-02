"""Pobieranie danych firmy z API GUS REGON (BIR) po numerze NIP."""

import requests
import xml.etree.ElementTree as ET
from typing import Optional


# Klucz API – użytkownik powinien wpisać swój w UI lub env
KLUCZ_API_TESTOWY = "abcde12345abcde12345"  # testowy klucz GUS

WSDL_URL = "https://wyszukiwarkaregon.stat.gov.pl/wsBIR/UslugaBIRzewnPubl.svc"


def _soap(action: str, body: str, sid: str = "") -> str:
    headers = {
        "Content-Type": "application/soap+xml; charset=utf-8",
        "SOAPAction": f"http://CIS/BIR/PUBL/2014/07/IUslugaBIRzewnPubl/{action}",
    }
    if sid:
        headers["sid"] = sid

    envelope = f"""<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope"
               xmlns:ns="http://CIS/BIR/PUBL/2014/07">
  <soap:Header>
    <ns:guid>{sid}</ns:guid>
  </soap:Header>
  <soap:Body>
    {body}
  </soap:Body>
</soap:Envelope>"""

    resp = requests.post(WSDL_URL, data=envelope.encode("utf-8"), headers=headers, timeout=15)
    resp.raise_for_status()
    return resp.text


def _zaloguj(klucz: str) -> str:
    body = f"""<ns:Zaloguj xmlns:ns="http://CIS/BIR/PUBL/2014/07">
      <ns:pKluczUzytkownika>{klucz}</ns:pKluczUzytkownika>
    </ns:Zaloguj>"""
    resp = _soap("Zaloguj", body)
    root = ET.fromstring(resp)
    el = root.find(".//{http://CIS/BIR/PUBL/2014/07}ZalogujResult")
    return el.text.strip() if el is not None and el.text else ""


def _wyloguj(sid: str):
    body = f"""<ns:Wyloguj xmlns:ns="http://CIS/BIR/PUBL/2014/07">
      <ns:pIdentyfikatorSesji>{sid}</ns:pIdentyfikatorSesji>
    </ns:Wyloguj>"""
    try:
        _soap("Wyloguj", body, sid)
    except Exception:
        pass


def _szukaj_nip(nip: str, sid: str) -> str:
    body = f"""<ns:DaneSzukajPodmioty xmlns:ns="http://CIS/BIR/PUBL/2014/07">
      <ns:pParametryWyszukiwania>
        <dat:NIP xmlns:dat="http://CIS/BIR/PUBL/2014/07/DataContract">{nip}</dat:NIP>
      </ns:pParametryWyszukiwania>
    </ns:DaneSzukajPodmioty>"""
    resp = _soap("DaneSzukajPodmioty", body, sid)
    root = ET.fromstring(resp)
    el = root.find(".//{http://CIS/BIR/PUBL/2014/07}DaneSzukajPodmiotyResult")
    return el.text.strip() if el is not None and el.text else ""


def _parse_podmiot(xml_str: str) -> dict:
    """Parsuje XML z danymi podmiotu i zwraca słownik."""
    if not xml_str:
        return {}
    try:
        root = ET.fromstring(xml_str)
    except ET.ParseError:
        return {}

    def t(tag: str) -> str:
        el = root.find(f".//{tag}")
        return el.text.strip() if el is not None and el.text else ""

    return {
        "regon": t("Regon"),
        "nip": t("Nip"),
        "nazwa": t("Nazwa"),
        "wojewodztwo": t("Wojewodztwo"),
        "powiat": t("Powiat"),
        "gmina": t("Gmina"),
        "miejscowosc": t("MiejscowoscNazwa"),
        "kod_pocztowy": t("KodPocztowy"),
        "ulica": t("UlicaNazwa"),
        "nr_nieruchomosci": t("NrNieruchomosci"),
        "nr_lokalu": t("NrLokalu"),
        "typ": t("Typ"),  # P=prawna, F=fizyczna
    }


def pobierz_dane_nip(nip: str, klucz: str = KLUCZ_API_TESTOWY) -> dict:
    """
    Pobiera dane firmy z GUS REGON API.

    Zwraca słownik z kluczami: nazwa, regon, nip, adres...
    Przy błędzie zwraca {"blad": "..."}
    """
    nip_clean = nip.replace("-", "").replace(" ", "").strip()
    if len(nip_clean) != 10:
        return {"blad": "Nieprawidłowy NIP – powinien mieć 10 cyfr."}

    try:
        sid = _zaloguj(klucz)
        if not sid:
            return {"blad": "Nie można zalogować do API GUS. Sprawdź klucz API."}

        xml_wynik = _szukaj_nip(nip_clean, sid)
        _wyloguj(sid)

        if not xml_wynik:
            return {"blad": f"Nie znaleziono podmiotu o NIP {nip_clean}."}

        return _parse_podmiot(xml_wynik)

    except requests.exceptions.Timeout:
        return {"blad": "Timeout – API GUS nie odpowiada."}
    except requests.exceptions.ConnectionError:
        return {"blad": "Brak połączenia z API GUS."}
    except Exception as e:
        return {"blad": f"Błąd API GUS: {e}"}
