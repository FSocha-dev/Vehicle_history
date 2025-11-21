import time
import requests
from requests.exceptions import RequestException
from calendar import monthrange
from datetime import datetime


class SessionExpired(Exception):
    pass

def prepare_session():
    session = requests.Session()
    default_headers = {"User-Agent": "Mozilla/5.0"}
    initial_url = "https://moj.gov.pl/nforms/engine/ng/index?xFormsAppName=HistoriaPojazdu#/search"

    session.get(initial_url, headers=default_headers)

    # Symulacja działania windowInfo.js
    wid_value = f"HistoriaPojazdu:{int(time.time() * 1000)}"
    session.post(initial_url.split("#")[0], data={"NF_WID": wid_value}, headers=default_headers)

    session.get("https://moj.gov.pl/nforms/api/init", headers=default_headers)

    xsrf_token = session.cookies.get("XSRF-TOKEN")

    if not xsrf_token:
        csrf_response = session.get("https://moj.gov.pl/nforms/api/csrf", headers=default_headers)
        try:
            xsrf_payload = csrf_response.json()
            xsrf_token = xsrf_payload.get("token")
            if xsrf_token:
                session.cookies.set("XSRF-TOKEN", xsrf_token, domain="moj.gov.pl", path="/")
        except ValueError:
            text_token = csrf_response.text.strip()
            if text_token:
                xsrf_token = text_token
                session.cookies.set("XSRF-TOKEN", xsrf_token, domain="moj.gov.pl", path="/")

    if not xsrf_token:
        raise RuntimeError("Nie udało się pobrać tokenu XSRF.")

    return session, xsrf_token, default_headers, wid_value

def fetch_vehicle(session, xsrf_token, base_headers, nf_wid_value, registration_number, vin, first_registration_date):
    payload = {
        "registrationNumber": registration_number,
        "VINNumber": vin,
        "firstRegistrationDate": first_registration_date,
    }

    headers = {
        **base_headers,
        "Content-Type": "application/json",
        "X-Xsrf-Token": xsrf_token,
        "Origin": "https://moj.gov.pl",
        "Referer": "https://moj.gov.pl/",
        "Nf_wid": nf_wid_value,
    }

    api_url = "https://moj.gov.pl/nforms/api/HistoriaPojazdu/1.0.18/data/vehicle-data"
    for attempt in range(3):
        try:
            response = session.post(api_url, json=payload, headers=headers, timeout=10)
        except RequestException as exc:
            time.sleep(0.1)
            continue

        if response.status_code == 429:
            raise SessionExpired("429 - reset sesji")

        if response.status_code == 401:
            raise SessionExpired("401 - sesja wygasła")

        break
    else:
        return None

    if response.status_code != 200:
        return None

    try:
        data = response.json()
    except ValueError:
        raise SessionExpired("Błąd JSON - reset sesji")

    if not data or "technicalData" not in data:
        return None

    return data

def generate_dates(year):
    for month in range(1, 13):
        days_in_month = monthrange(year, month)[1]
        for day in range(1, days_in_month + 1):
            dt = datetime(year, month, day)
            yield dt.strftime("%d.%m.%Y"), dt.strftime("%Y-%m-%d")

def main():
    plate = input("Podaj numer rejestracyjny pojazdu: ").strip()
    vin = input("Podaj numer VIN: ").strip()
    year_input = input("Podaj rok pierwszej rejestracji (RRRR): ").strip()

    if not plate or not vin or not year_input:
        print(" Wszystkie pola są wymagane.")
        return

    try:
        year = int(year_input)
        if year < 1960 or year > datetime.now().year:
            raise ValueError
    except ValueError:
        print("Nieprawidłowy rok. Podaj cztery cyfry.")
        return

    print("Przygotowywanie sesji z serwisem Historia Pojazdu GOV")
    try:
        session, xsrf_token, base_headers, nf_wid_value = prepare_session()
        time.sleep(1.5)
    except RuntimeError as err:
        print(err)
        return
    
    attempt_counter = 0
    found_entry = None

    for display_date, iso_date in generate_dates(year):
        attempt_counter += 1

        if attempt_counter >= 4:
            print("Automatyczny reset sesji co 3 daty, poniewaz połączenie jest blokowane.")
            session, xsrf_token, base_headers, nf_wid_value = prepare_session()
            time.sleep(1)
            attempt_counter = 1

        print(f"Testuję datę: {display_date}...")

        while True:
            try:
                result = fetch_vehicle(session, xsrf_token, base_headers, nf_wid_value, plate, vin, iso_date)
                time.sleep(2)
                break
            except SessionExpired as exc:
                print(f" {exc}. Odnawiam sesję...")
                session, xsrf_token, base_headers, nf_wid_value = prepare_session()
                time.sleep(1.5)
                continue

        if result:
            found_entry = (display_date, result)
            break

    if not found_entry:
        print(" Nie znaleziono pojazdu dla żadnej daty w podanym roku.")
        return

    display_date, vehicle_data = found_entry
    basic_data = vehicle_data.get("technicalData", {}).get("basicData", {})
    detailed_data = vehicle_data.get("technicalData", {}).get("detailedData", {})

    print(f"\n Znaleziono pojazd! Data pierwszej rejestracji: {display_date}")
    print("\n Dane pojazdu:")
    if basic_data:
        print(f" - Marka: {basic_data.get('make')}")
        print(f" - Model: {basic_data.get('model')}")
        print(f" - Status rejestracji: {basic_data.get('registrationStatus')}")
        print(f" - Status przeglądu: {basic_data.get('technicalInspectionStatus')}")
        print(f" - Rok produkcji: {basic_data.get('yearOfManufacture')}")
    if detailed_data:
        print(f" - Pojemność silnika: {detailed_data.get('engineCapacity')} cm3")
        print(f" - Moc netto: {detailed_data.get('maxNetEnginePower')} kW")
        print(f" - Poziom emisji: {detailed_data.get('euroEmissionLevel')}")

if __name__ == "__main__":
    main()