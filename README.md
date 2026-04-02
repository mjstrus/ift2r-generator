# Generator IFT-2R (wariant 12)

Aplikacja Streamlit do generowania pliku XML IFT-2R na podstawie paczki plików JPK_FA.

## Wymagania

```
pip install -r requirements.txt
```

## Uruchomienie

```
streamlit run app.py
```

## Pliki

| Plik | Opis |
|------|------|
| `app.py` | Główna aplikacja Streamlit |
| `jpk_parser.py` | Parser plików JPK_FA (4) |
| `ift2r_generator.py` | Generator XML IFT-2R wariant 12 |
| `gus_api.py` | Klient API GUS REGON (pobieranie danych firmy po NIP) |
| `requirements.txt` | Zależności Python |

## Przepływ pracy

1. **Sidebar** → wpisz NIP płatnika → kliknij "Pobierz z GUS" → dane płatnika wypełniają się automatycznie
2. **Sidebar** → wgraj pliki JPK_FA (4) → kliknij "Wczytaj i parsuj"
3. Zakładka **Zestawienie JPK_FA** → przejrzyj wykryte faktury od zagranicznych kontrahentów
4. Kliknij kontrahenta w sidebarze → dane podatnika wypełniają się automatycznie w Części B
5. Zakładka **Sekcje D–Q** → wybierz kategorię (K dla Google/Meta/LinkedIn), uzupełnij kwoty
6. Zakładka **Generuj XML** → pobierz gotowy plik XML

## Sekcje D formularza

| Symbol | Kategoria |
|--------|-----------|
| E | Opłaty żegluga morska |
| F | Przychody żegluga powietrzna |
| G | Dywidendy (art. 22) |
| H | Odsetki (art. 21 ust. 1 pkt 1) |
| I | Należności licencyjne |
| J | Działalność widowiskowa/sportowa |
| **K** | **Usługi niematerialne: reklama, doradztwo, przetwarzanie danych** ← Google, Meta, LinkedIn |
| L | Art. 21 – odsetki szczegółowo |
| M | Art. 21 – licencje szczegółowo |
| N | Art. 22 – dywidendy szczegółowo |
| O | Art. 21 – pozostałe |
| P | Zyski kapitałowe do rajów podatkowych |

## Ważne

- Właściwy urząd: **Lubelski Urząd Skarbowy w Lublinie** (kod 0671) – stały dla wszystkich IFT-2R
- Termin złożenia: **do końca marca** roku następnego
- Wysyłka wyłącznie elektronicznie przez **e-Deklaracje** z kwalifikowanym podpisem elektronicznym
- Dla Google/Meta/LinkedIn z certyfikatem rezydencji: kwota zwolniona = suma netto, podatek = 0

## Format JPK_FA

Aplikacja obsługuje pliki **JPK_FA (4)** zgodne ze schematem MF:
`http://jpk.mf.gov.pl/wzor/2022/02/17/02171/`
