# LLD — kontrakty API i artefaktów

**Data:** 21 października 2026. **Status:** projekt v0.1 do uzgodnienia, nie wygenerowana specyfikacja OpenAPI.

[Założenia](README.md) · [Model danych](model_danych.md) · [Cykl wykonania](cykl_wykonania.md)

## 1. Konwencje

- Publiczne API: `/api/v1`; wewnętrzne: `/internal/v1`. `contract_version` identyfikuje wersję dokumentu transportowego.
- JSON odrzuca nieznane pola komend. Liczebności są nieujemnymi liczbami całkowitymi, bez cichej konwersji `"200"` na `200` i `true` na `1`.
- Nazwy SQL zachowują schemat, wielkość liter i cytowanie w modelu strukturalnym. Nie identyfikujemy obiektu przez dowolny uproszczony tekst nazwy.
- Identyfikatory, hashe i profile są walidowane na granicy. Każde odwołanie ma sprawdzoną własność.
- Wiadomości i pliki mają limity rozmiaru; konkretne wartości będą konfiguracją po próbie.
- Wszystkie UUID i hashe w przykładach są ilustracyjne; nie odnoszą się do istniejących zasobów.

### Błędy

Proponowany wspólny kształt, nie deklaracja zgodności z dodatkowym standardem:

```json
{
  "error": {
    "code": "EXECUTOR_BUSY",
    "message": "Inna operacja zajmuje lokalnego wykonawcę.",
    "request_id": "00000000-0000-4000-8000-000000000013",
    "automatic_retry_allowed": false,
    "details": {}
  }
}
```

`404` dla zasobu nieistniejącego albo niedostępnego dla danego właściciela; `409` dla konfliktu rewizji, zajętości lub ponownie użytego klucza z inną treścią; `422` dla niepoprawnej komendy; `502/503/504` dla odpowiednio sklasyfikowanych awarii usług. Te kody nie uruchamiają automatycznej próby LLM.

Niepoprawny SQL/CSV otrzymany od modelu nie jest błędem HTTP wywołania dostawcy. To normalnie zwrócony kandydat z naruszeniami.

## 2. Zatwierdzenie i start

### Zatwierdzenie

`POST /api/v1/orders/{order_id}/approve`

```json
{
  "order_revision_id": "00000000-0000-4000-8000-000000000002",
  "requirements_sha256": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
}
```

Backend sprawdza uprawnienie, aktualność proponowanej rewizji, brak wykrytej blokady i kompletność wymaganych decyzji. Nie zatwierdza najnowszej wersji zamiast wskazanej. Odpowiedź `200` identyfikuje zatwierdzoną rewizję.

### Nowe wykonanie

`POST /api/v1/orders/{order_id}/runs`

Nagłówek `Idempotency-Key`: unikalny identyfikator akcji startu wygenerowany przez UI.

```json
{
  "order_revision_id": "00000000-0000-4000-8000-000000000002",
  "expected_requirements_sha256": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
}
```

Wariant realizacji pochodzi z zaufanej konfiguracji badania i jest utrwalany przez backend. Nie wymagamy panelu wyboru modeli i nie przyjmujemy dowolnych adresów providerów z tego body.

Pierwsza odpowiedź `202`:

```json
{
  "run_id": "00000000-0000-4000-8000-000000000003",
  "lifecycle": "ADMITTED",
  "phase": null,
  "version": 1
}
```

Ponowne dostarczenie tej samej komendy z identyczną treścią zwraca identyfikator już utworzonego wykonania, bez nowej pracy. Inna treść z tym samym kluczem daje `409 IDEMPOTENCY_CONFLICT`. Po utracie odpowiedzi UI może odczytać wynik komendy, nie wysyła automatycznie startu.

Proponowany odczyt: `GET /api/v1/commands/{idempotency_key}?scope_id={order_id}&kind=START_RUN`, z kontekstem właściciela po stronie serwera.

Ręczne ponowienie: `POST /api/v1/runs/{run_id}/new-run`, z nowym `Idempotency-Key`. Backend kopiuje dawne wymagania i przypina aktualny wariant; nie używa aktualnego DDL projektu zamiast historycznego.

## 3. Odczyt, anulowanie i przygotowanie

`GET /api/v1/runs/{run_id}` zwraca:

```json
{
  "run_id": "00000000-0000-4000-8000-000000000003",
  "lifecycle": "RUNNING",
  "phase": "VALIDATING",
  "version": 7,
  "cancel_requested_at": null,
  "corrections_started": 0,
  "correction_limit": 3,
  "outcome": null,
  "selected_candidate_id": null,
  "termination_code": null,
  "download_available": false
}
```

`POST /api/v1/runs/{run_id}/cancel`:

- `202` oznacza trwałe przyjęcie żądania, nie natychmiastowe zatrzymanie dostawcy.
- Ponowne anulowanie nie tworzy nowej operacji generowania.
- Dla już terminalnego wykonania zwracamy jego bieżący status i `cancellation_applied=false`.
- Odpowiedź nie stwierdza dostępności plików po przerwaniu; to nadal OD-08.

Interpretacja wymagań przed startem ma osobną `preparation_operation_id`. Proponujemy `GET /api/v1/preparation-operations/{id}` dla statusu i `POST /api/v1/preparation-operations/{id}/cancel` dla zatrzymania. Ślad wiążemy z projektem i rewizją zlecenia, nie nieistniejącym jeszcze wykonaniem. Wynik jest propozycją, którą trzeba zatwierdzić.

## 4. Kontrakt zlecenia generatora

`POST /internal/v1/generate`, a poprawka analogicznie `/correct`.

```json
{
  "contract_version": "1.0",
  "project_id": "00000000-0000-4000-8000-000000000001",
  "run_id": "00000000-0000-4000-8000-000000000003",
  "operation_id": "00000000-0000-4000-8000-000000000005",
  "execution_epoch": 1,
  "expected_service_instance_id": "00000000-0000-4000-8000-000000000015",
  "round_no": 0,
  "deadline_at": "2026-10-21T16:30:00Z",
  "snapshot": {
    "artifact_id": "00000000-0000-4000-8000-000000000007",
    "sha256": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
  },
  "context_package_id": "00000000-0000-4000-8000-000000000006",
  "variant_snapshot_id": "00000000-0000-4000-8000-000000000004",
  "output_profile_id": "insert-postgresql-proposed-v1",
  "mode": "GENERATE"
}
```

`/correct` ma `mode=CORRECT`, numer przyznanej rundy, odniesienie do poprzedniego kandydata i raportu naruszeń. Sam generator nie zwiększa numeru rundy. Wszelkie dane wskazane referencjami muszą być dostępne w uprawnieniu tej operacji.

`GET /internal/v1/health/ready` zwraca także losowy `service_instance_id` nadany przy starcie procesu. Po restarcie nie pasuje do starego zlecenia. Serwis odrzuca takie zlecenie `409 SERVICE_INSTANCE_CHANGED`, nie wywołuje modelu ponownie.

Usługa ma rejestr operacji swojego procesu. Duplikat identycznego `operation_id` nie wykonuje ponownie kroku; zwraca status albo zapamiętany rezultat. Inny hash żądania jest konfliktem. Rejestr nie jest przenoszony przez restart, dlatego potrzebna jest też kontrola instancji i zakaz ponownego wysyłania starego kroku.

Długie żądanie jest wykonywane tylko raz przez runner. `POST /internal/v1/operations/{id}/cancel` i odczyt aktywnych operacji działają równolegle. Stan instancji nie jest źródłem historii użytkownika.

## 5. Kandydat i odpowiedź generatora

Odpowiedź poprawnie wykonanej operacji wskazuje manifest:

```json
{
  "contract_version": "1.0",
  "operation_id": "00000000-0000-4000-8000-000000000005",
  "execution_epoch": 1,
  "candidate": {
    "candidate_id": "00000000-0000-4000-8000-000000000008",
    "round_no": 0,
    "format": "INSERT_SQL",
    "extraction_status": "COMPLETE",
    "files": [
      {
        "artifact_id": "00000000-0000-4000-8000-000000000009",
        "sha256": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
        "logical_name": "data.sql",
        "table_refs": ["public.customers", "public.orders"],
        "import_order": 1
      }
    ],
    "raw_response_artifact_id": "00000000-0000-4000-8000-000000000010",
    "extraction_issues": []
  }
}
```

Generator nadaje `candidate_id`; backend sprawdza, że nie istnieje konflikt, i publikuje go dopiero po weryfikacji manifestu i artefaktów. `table_refs` w przykładzie są nazwami prezentacyjnymi; właściwy kontrakt wiąże je z identyfikatorami obiektów w interpretacji schematu.

`COMPLETE` oznacza tylko wyodrębnienie deklarowanych plików, nie kompletność planu ani importowalność. Przy błędnej treści modelu `extraction_status=INVALID`, `files` może być puste, a `extraction_issues` wyjaśnia naruszenia. Surowa odpowiedź nadal jest artefaktem, jeśli udało się ją odebrać i utrwalić.

Podział kilku wywołań i plików pozostaje częścią wersjonowanej strategii i OD-10. W bazowym projekcie jedna runda publikuje jeden kandydat; nie zakładamy, że oznacza to jedno wywołanie modelu.

## 6. Walidacja

`POST /internal/v1/validate` zawiera tę samą kopertę operacji i dodatkowo: `candidate_id`, `manifest_artifact_id`, `manifest_sha256`, `snapshot` oraz `validation_profile_id`. Profil określa wymagany zestaw sprawdzeń, nie tylko listę tych, które walidator akurat wykonał.

Potwierdzona kolejność: format → wstępna zgodność schematu i typów → rzeczywisty import oraz kompletność → dodatkowe reguły biznesowe. Proponowane wartości `stage`: `FORMAT`, `SCHEMA_PRECHECK`, `TRIAL_IMPORT`, `COMPLETENESS`, `BUSINESS`; kompletność jest częścią etapu po imporcie, nie dodatkową alternatywą dla niego. Szczegóły i statusy decyzji opisuje [projekt walidacji](walidacja.md).

Przykładowa część odpowiedzi:

```json
{
  "candidate_id": "00000000-0000-4000-8000-000000000008",
  "complete": true,
  "importable": true,
  "business_conformant": false,
  "checks": [
    {
      "check_id": "business.delivery_after_purchase",
      "stage": "BUSINESS",
      "required_for": "BUSINESS_CONFORMANCE",
      "status": "VIOLATION",
      "scope": {"table": "public.orders", "checked_count": 200},
      "violation_count": 7,
      "unit": "ROW",
      "examples": [{"primary_key": {"id": 12}}],
      "reason_code": "DELIVERY_BEFORE_PURCHASE"
    }
  ]
}
```

To fragment, nie pełny raport: kompletny kontrakt ma również tożsamość operacji, hashe, profil, wersję walidatora, raport artefaktowy oraz wszystkie wymagane sprawdzenia formatu, schematu i liczebności.

Status sprawdzenia: `PASS`, `VIOLATION`, `NOT_RUN`, `UNSUPPORTED`, `UNDETERMINED`. Niewykonane sprawdzenie ma przyczynę; liczbę naruszeń nieznaną zapisujemy jako NULL. Dla obowiązkowych dowodów brak kompletnego zestawu wyników uniemożliwia `complete=true` lub `importable=true`.

Awaria infrastruktury ma kontrakt błędu, a nie raport z zerem naruszeń. Częściowe dowody mogą pozostać w historii, ale nie potwierdzają sukcesu.

## 7. Ślad wywołań

`POST /internal/v1/operations/{operation_id}/trace-events`

Każde zdarzenie ma `event_id`, `event_kind`, `call_id`, `payload_sha256`, odniesienia do payloadów i bezpieczne metadane. Backend sprawdza token, zakres, powiązanie oraz hash; tożsamość właściciela wynika z zapisanej operacji.

Proponowane rodzaje zdarzeń:

1. `CALL_PREPARED` — zapis żądania i próby przed wysłaniem, nie dowód doręczenia.
2. `PROVIDER_REQUEST_RECORDED` — rzeczywiste wiadomości/treść żądania po mapowaniu dostawcy, bez sekretów.
3. `CALL_RESPONSE_RECORDED` — odpowiedź, przyczyna zakończenia, dostępne metryki i identyfikatory.
4. `CALL_FAILED` — sklasyfikowany błąd z dostępnymi informacjami.

Przed rozpoczęciem kolejnego wywołania generator wymaga trwałego przyjęcia niezbędnego śladu i sprawdzenia aktualnego uprawnienia. Błąd zapisu kończy pracę bez ponownego wywołania dostawcy.

Potwierdzenie śladu i wysłanie żądania do dostawcy nie są jedną transakcją. Anulowanie może ścigać się z fizycznym wysłaniem; gwarantujemy blokadę dalszych skutków procesu, nie atomowe cofnięcie żądania na innym serwerze.

Zdarzenie o znanym ID i identycznym hashu daje ten sam rezultat bez nowego wpisu pomiaru. Zmiana treści daje `409 TRACE_EVENT_CONFLICT`. Po unieważnieniu operacji zaufana usługa może dosłać dostępne dowody jako `late=true`, ale nie otrzymuje zgody na nową generację. Przyjęcie późnego dowodu nadal wymaga uwierzytelnienia usługi i uprawnienia do tej operacji; nie wskrzesza wygasłego tokenu. Okno ważności dla domknięcia historii wymaga ustalenia w OD-07.

Dokładne wiadomości nie oznaczają ukrytego rozumowania modelu. Pomiary brakujące są NULL, koszty szacowane oznaczone, a informacja o przygotowaniu nie jest naliczana ponownie przy każdym ręcznym powtórzeniu wymagań.

## 8. Transfer i integralność plików

Proponowane wewnętrzne operacje:

1. `POST /internal/v1/operations/{id}/artifacts` — rezerwacja `artifact_id`, typu, limitu i opcjonalnego oczekiwanego hasha.
2. `PUT /internal/v1/artifacts/{id}/content` — strumień bajtów; tylko dla uprawnionej, zarezerwowanej operacji.
3. `GET /internal/v1/artifacts/{id}/content` — odczyt konkretnego zasobu przyznanego operacji.

Sekwencja zapisu w backendzie:

- Wiersz `WRITING` → ograniczony plik tymczasowy → hash i rozmiar → zamknięcie/synchronizacja → publikacja pod nowym kluczem → commit `READY`.
- Docelowy klucz wyznacza backend, nie `logical_name`. Nie pozwalamy na `../`, ścieżki absolutne i nadpisanie istniejącego gotowego pliku.
- Brak transakcji między systemem plików i bazą jest jawny. Po awarii uzgadniamy niegotowe metadane; nie publikujemy pliku jako kandydata samym znalezieniem go na dysku.
- Nie włączamy automatycznego ponawiania uploadu. Odczyt stanu rozstrzyga niepewną odpowiedź; ewentualna deduplikacja transferu nie uruchamia modelu.
- Po zakończeniu/anulowaniu nie publikujemy nowych plików danych jako skutecznego wyniku. Dopuszczalny zapis dowodów diagnostycznych ma osobny zakres i nie zmienia wybranego kandydata.

Usługi wywoływane przez backend uwierzytelniamy sekretem usługi z konfiguracji. Dostęp zwrotny do śladu i artefaktów dodatkowo ogranicza losowy token operacji, przesłany poza logowanym body. Adres backendu jest stałą konfiguracją, nie callbackiem od użytkownika. Token i nagłówki nie są kopiowane do historii.

## 9. Profile — konkretne propozycje do OD-04 i OD-10

### `insert-postgresql-proposed-v1`

Jeden plik UTF-8 z gotowymi `INSERT`, jawnymi listami kolumn i dozwolonymi wartościami/wyrażeniami z macierzy OD-01. Bez DDL, komend transakcyjnych, wyłączania ograniczeń i dowolnych zapytań. Dokładna lista dopuszczonych wyrażeń musi być zatwierdzona przed uruchomieniem walidacji.

### `csv-postgresql-proposed-v1`

Do oceny: UTF-8 bez BOM, przecinek, podwójny cudzysłów jako quote/escape, nagłówek z ustaloną kolejnością kolumn, oddzielny plik na tabelę i jawny znacznik NULL `\N`. Cytowany tekst `"\N"` jest wartością tekstową, nie NULL. Format wartości dat, czasu, liczb i typów dodatkowych wymaga macierzy.

Nie zmieniamy zakończeń linii ani cytowania w odebranym pliku. Parser struktury CSV i rzeczywisty import mają ten sam profil. Pusta komórka nie jest automatycznie traktowana jako NULL.

To kandydaci profili, nie wybór obsługi całego PostgreSQL.

## 10. Raport i eksport

`GET /api/v1/runs/{id}/report` zwraca wersjonowany dokument, a `/export` paczkę dostępną według zakończenia i polityki OD-08.

Proponowane minimum raportu: `report_version`, identyfikacja projektu/wykonania, hash migawki, wariant, status/powód, wybrany kandydat i manifest, walidacja/metoda, oczekiwane/rzeczywiste liczebności, reguły, rundy, czasy i pomiary z dostępnością.

Raport ma stabilny `candidate_id` i `validation_report_id`. Paczka nie wybiera „ostatniego pliku z katalogu”. Błąd pobierania po zakończeniu jest błędem dostarczenia artefaktu, nie powodem ponownej generacji.
