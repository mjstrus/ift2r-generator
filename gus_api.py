"""
Pobieranie danych firmy po NIP z API Ministerstwa Finansów (Biała Lista VAT).

Nie wymaga żadnego klucza API — działa bez rejestracji.
Endpoint: https://wl-api.mf.gov.pl/api/search/nip/{NIP}?date={YYYY-MM-DD}
"""

import re
import requests
from datetime import date


MF_API_URL = "https://wl-api.mf.gov.pl/api/search/nip/{nip}?date={data}"


def _parse_adres(adres_str: str) -> dict:
    """Rozkłada adres 'ul. Przykładowa 1, 00-000 Miasto' na składowe."""
    result = {"ulica": "", "nr_domu": "", "nr_lokalu": "", "kod": "", "miejscowosc": ""}
    if not adres_str:
        return result

    m = re.search(r"(\d{2}-\d{3})\s+(.+)$", adres_str)
    if m:
        result["kod"] = m.group(1)
        result["miejscowosc"] = m.group(2).strip()
        adres_str = adres_str[:m.start()].strip().rstrip(",").strip()

    adres_str = re.sub(r"^(ul\.|al\.|pl\.|os\.|rondo\s)\s*", "", adres_str, flags=re.IGNORECASE)

    m2 = re.search(r"\s+([\d]+[a-zA-Z]?(?:/[\d]+[a-zA-Z]?)?)$", adres_str)
    if m2:
        numer = m2.group(1)
        if "/" in numer:
            czesci = numer.split("/", 1)
            result["nr_domu"] = czesci[0]
            result["nr_lokalu"] = czesci[1]
        else:
            result["nr_domu"] = numer
        result["ulica"] = adres_str[:m2.start()].strip()
    else:
        result["ulica"] = adres_str

    return result


def pobierz_dane_nip(nip: str, _klucz: str = "") -> dict:
    """
    Pobiera dane firmy z API MF (Biała Lista VAT) po numerze NIP.
    Nie wymaga klucza API.
    Zwraca dict z kluczami: nazwa, regon, nip, ulica, nr_nieruchomosci,
    nr_lokalu, kod_pocztowy, miejscowosc; lub {"blad": "..."} przy błędzie.
    """
    nip_clean = nip.replace("-", "").replace(" ", "").strip()
    if len(nip_clean) != 10 or not nip_clean.isdigit():
        return {"blad": "Nieprawidłowy NIP — powinien mieć dokładnie 10 cyfr."}

    dzis = date.today().strftime("%Y-%m-%d")
    url = MF_API_URL.format(nip=nip_clean, data=dzis)

    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code == 404:
            return {"blad": f"Nie znaleziono podmiotu o NIP {nip_clean} w bazie MF."}
        resp.raise_for_status()
        data = resp.json()
    except requests.exceptions.Timeout:
        return {"blad": "Timeout — API MF nie odpowiada. Spróbuj ponownie."}
    except requests.exceptions.ConnectionError:
        return {"blad": "Brak połączenia z API MF (wl-api.mf.gov.pl)."}
    except Exception as e:
        return {"blad": f"Błąd: {e}"}

    subject = data.get("result", {}).get("subject")
    if not subject:
        return {"blad": f"Brak danych dla NIP {nip_clean}."}

    adres_str = subject.get("workingAddress") or subject.get("residenceAddress") or ""
    adres = _parse_adres(adres_str)

    return {
        "nip": nip_clean,
        "nazwa": subject.get("name", ""),
        "regon": subject.get("regon", ""),
        "ulica": adres.get("ulica", ""),
        "nr_nieruchomosci": adres.get("nr_domu", ""),
        "nr_lokalu": adres.get("nr_lokalu", ""),
        "kod_pocztowy": adres.get("kod", ""),
        "miejscowosc": adres.get("miejscowosc", ""),
        "wojewodztwo": "",
        "powiat": "",
        "gmina": "",
    }
