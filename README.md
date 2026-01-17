# Historia Pojazdu

Skrypt do automatycznego pobierania danych pojazdu z serwisu Historia Pojazdu na portalu moj.gov.pl.

## Co robi skrypt?

Skrypt łączy się z API portalu moj.gov.pl i pobiera szczegółowe informacje o pojeździe na podstawie:
- Numeru rejestracyjnego
- Numeru VIN
- Roku pierwszej rejestracji

Skrypt automatycznie testuje wszystkie daty w podanym roku, aby znaleźć prawidłową datę pierwszej rejestracji pojazdu. Po znalezieniu odpowiedniej daty wyświetla następujące informacje:
- Marka i model pojazdu
- Status rejestracji
- Status przeglądu technicznego
- Rok produkcji
- Pojemność silnika
- Moc netto
- Poziom emisji Euro

## Wymagania

- Python 3
- Biblioteka `requests`

## Jak uruchomić?

### Metoda 1: Użycie skryptu setup_and_run.sh (rekomendowane)

```bash
chmod +x setup_and_run.sh
./setup_and_run.sh
```

Skrypt automatycznie:
1. Utworzy wirtualne środowisko Python
2. Zainstaluje wymagane zależności
3. Uruchomi program

### Metoda 2: Ręczna instalacja

```bash
# Utworzenie wirtualnego środowiska
python3 -m venv env

# Aktywacja wirtualnego środowiska
source env/bin/activate  # macOS/Linux
# lub
env\Scripts\activate  # Windows

# Instalacja zależności
pip install --upgrade pip
pip install requests

# Uruchomienie skryptu
python3 historia_pojazdu.py
```

## Użycie

Po uruchomieniu skryptu wprowadź:
1. **Numer rejestracyjny pojazdu** (np. ABC1234)
2. **Numer VIN** (17 znaków)
3. **Rok pierwszej rejestracji** (format: RRRR, np. 2020)

Skrypt automatycznie przetestuje wszystkie daty w podanym roku i wyświetli znalezione dane pojazdu.

## Uwagi

- Skrypt automatycznie resetuje sesję co 3 próby, aby uniknąć blokady połączenia
- W przypadku błędów autoryzacji (401) lub limitu zapytań (429) sesja jest automatycznie odnawiana
- Proces wyszukiwania może zająć kilka minut, w zależności od tego, która data w roku jest prawidłowa
