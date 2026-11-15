# LLD — kontrakty API i artefaktów

**Data:** 21 października 2026. **Status:** projekt v0.1 do uzgodnienia, nie wygenerowana specyfikacja OpenAPI.

[Założenia](README.md) · [Model danych](model_danych.md) · [Cykl wykonania](cykl_wykonania.md)

**Aktualizacja 14 listopada 2026 — specyfikacja v1.8:** kontrakty są propozycją obsługi projektów i bieżącej pracy, bez archiwum rozmów. Wymagają uzupełnienia o kolejne polecenia i granicę dostępu do plików (REQ-073–REQ-075, OD-10 i OD-12). Po zdarzeniach z REQ-074, także odświeżeniu lub zamknięciu strony, zachowany `run_id` lub adres pobrania nie daje dostępu do starego czatu. Rezygnacja z wyjścia w ostrzeżeniu nie może unieważniać plików. Mechanizm identyfikacji czatu, zakończenia dostępu i fizyczne sprzątanie wymagają OD-09; nie zakładamy niezawodnego żądania API przy zamykaniu strony.

## 1. Konwencje

**Uzupełnienie do specyfikacji v1.13:** kontrakt prośby o zmianę danych musi umożliwić przekazanie do LLM poprzedniej paczki i nowego polecenia oraz zwrot nowego kandydata do walidacji (REQ-076). Każda nowa prośba ma własny limit napraw zgodnie z REQ-033–REQ-034. Trzeba odróżnić niepowodzenie tej prośby od dostępności poprzedniej sprawdzonej paczki z jej własnym raportem (REQ-078). Osobna ręczna akcja „Podejmij kolejne 3 próby” zleca jedną dodatkową serię napraw na prośbę (REQ-079), nie automatyczne retry komendy po błędzie. Ponowne użycie akcji nie może przyznać drugiej dodatkowej serii tej samej prośbie; sposób egzekwowania tego warunku wymaga projektu kontraktu. Pierwsza dodatkowa runda otrzymuje ostatniego nieudanego kandydata i listę wykrytych w nim błędów, nie poprzednią sprawdzoną paczkę. Poniższe API nie opisuje jeszcze tych przypadków. Automatyczna poprawka przy tych samych wymaganiach nie zastępuje nowej prośby użytkownika. Endpointy, pola żądań, przekazanie kandydata i jego błędów oraz przypisanie do wykonania i liczników pozostają w OD-10.

- Zatwierdzony 14 listopada 2026 podział adresów w `application-api`: frontend od `/`, publiczne operacje biznesowe pod `/api/v1`, osobna trasa techniczna `/health/live`. Nie zatwierdza to wszystkich operacji i pól poniżej. Minimalny routing szkieletu opisano osobno poniżej.
- Wewnętrzny prefiks `/internal/v1` i pole `contract_version` identyfikujące wersję dokumentu transportowego pozostają propozycją.
- JSON odrzuca nieznane pola komend. Liczebności są nieujemnymi liczbami całkowitymi, bez cichej konwersji `"200"` na `200` i `true` na `1`.
- Nazwy SQL zachowują schemat, wielkość liter i cytowanie w modelu strukturalnym. Nie identyfikujemy obiektu przez dowolny uproszczony tekst nazwy.
- Identyfikatory, hashe i profile są walidowane na granicy. Każde odwołanie ma sprawdzoną własność.
- Wiadomości i pliki mają limity rozmiaru; konkretne wartości będą konfiguracją po próbie.
- Wszystkie UUID i hashe w przykładach są ilustracyjne; nie odnoszą się do istniejących zasobów.

**Zatwierdzony zakres routingu początkowego szkieletu:** ekran startowy
pod `/`; nieznane adresy stron i brakujące pliki zwracają HTTP 404,
nie ekran startowy. Nie ustala to docelowej nawigacji MVP ani formatu
odpowiedzi dla brakującej strony lub pliku. Nie wykonano implementacji.

### Sprawdzenie działania procesu — uzgodnione dla S1

**Decyzja z 14 listopada 2026:** każdy z trzech backendów udostępnia
`GET /health/live`. Odpowiedź to HTTP 200 i JSON `{"status":"ok"}`.
Operacja nie wywołuje LLM, nie sprawdza baz ani magazynów i nie ujawnia
konfiguracji. To sprawdzenie działania procesu, nie gotowości do wykonania
operacji biznesowych. Kontrakt jest zatwierdzony, ale niezaimplementowany.

Nie zastępuje propozycji `GET /internal/v1/health/ready` z sekcji 4
i nie zatwierdza jej pól ani mechanizmu rozpoznawania instancji.
Adres `/health/live` jest odrębną trasą techniczną, poza proponowanymi
prefiksami operacji biznesowych. Zabezpieczenia i ekspozycja sieciowa
wymagają osobnego doprecyzowania; nie jest to zgoda na publiczne
udostępnienie generatora lub walidatora.

### Diagnostyka konfiguracji S1-T2

Każdy backend udostępnia `GET /health/config` (HTTP 200) z polami `service`,
`status` (`valid` lub `invalid`), `issues` (`field`, `code`, `message`)
i `blocked_capabilities`. Pole `field` może być puste przy błędzie pliku.
Obszary `application-api` to `database`, `generation` i `validation`.
Odpowiedź nie zawiera wartości konfiguracji. Nie sprawdza ona połączeń;
T9 obejmuje szerszą diagnostykę i monitor. Zależne operacje zwracają 503
z kodem `configuration_unavailable` i listą zablokowanych obszarów.

### Szczegółowa diagnostyka i monitoring — zakres uzgodniony, kontrakt otwarty

Każdy serwis ma sprawdzać poprawność uruchomienia, wymagane zmienne
środowiskowe i sekrety, połączenia do wykorzystywanych zewnętrznych API
oraz istnienie i dostęp do wymaganych zasobów wewnętrznych.
Wynik rozróżnia zdolność do działania, częściową zdolność i całkowity
brak zdolności; podaje przyczyny i ograniczenia bez wartości sekretów.
Każdy backend sprawdza własne bezpośrednie zależności, a `application-api`
zbiera statusy. Wspólny mechanizm odpytuje serwisy przy uruchamianiu,
a następnie co 30 minut. Zatwierdzono jego działanie
jako osobnego procesu monitora, niezależnego od trzech backendów.
Monitor sprawdza również `application-api` i nie polega wyłącznie
na jego zbiorczym raporcie, aby wykrywać zatrzymanie tego API.
Zatwierdzono osobny panel wyników w przeglądarce. Udostępnianie panelu
i odczyt wyników mają działać również przy niedostępnej głównej
aplikacji, bez zależności od działania `application-api`.
Nie ustalono technologii, sposobu uruchomienia monitora ani wyglądu,
adresu i zabezpieczeń panelu.

Zatwierdzono przycisk „Sprawdź teraz” w panelu: uruchamia nową,
bezpłatną i niedestrukcyjną diagnostykę bez oczekiwania na kontrolę
okresową. Nie ogranicza się do odczytu poprzedniego wyniku i nie
uruchamia płatnych prób LLM. Ścieżka, metoda i odpowiedź tej akcji
oraz obsługa jednoczesnych kontroli pozostają do uzgodnienia.
Ręczne sprawdzenie nie zmienia harmonogramu automatycznego:
nie przesuwa następnej kontroli i nie zeruje odstępu 30 minut.

Automatyczne health checki wykonują wyłącznie bezpłatne, niedestrukcyjne
próby. Sprawdzenie wymagające płatnego wywołania LLM wymaga ręcznego
uruchomienia i zgody użytkownika na daną próbę. Nie ustalono kontraktu
takiej akcji ani mechanizmu potwierdzania kosztu. Nie wykonano płatnych
prób.

Dla szerszej diagnostyki T9 nie wybrano jeszcze ścieżki, formatu pól,
kodów HTTP, zabezpieczeń ani limitów czasu. Raport konfiguracji T2 opisano powyżej. Nie zatwierdza to
automatycznie proponowanego `/internal/v1/health/ready` i jego pól.
Zatwierdzono tryb diagnostyczny mimo brakujących zmiennych lub sekretów
oraz błędnej konfiguracji: health check podaje przyczyny i ograniczenia,
a operacje wymagające tej konfiguracji są zablokowane. Zastępuje to
wcześniejszą zasadę blokowania startu procesu przy takich brakach.
Nie jest to gwarancja działania endpointu przy błędzie uniemożliwiającym
uruchomienie samego serwera diagnostyki; sposób zgłoszenia takiej awarii
pozostaje otwarty.
Nie zmieniono kontraktu `/health/live`; diagnostyka gotowości nie jest
potwierdzeniem poprawności każdego przyszłego wykonania biznesowego.
Nie wykonano implementacji ani testów.

### Błędy

**Zatwierdzone 14 listopada 2026 dla `application-api`:** nieznany
adres pod `/api/v1` zwraca HTTP 404 z odpowiedzią JSON, nigdy stronę HTML
frontendu. Nie zatwierdza to poniższego wspólnego formatu błędów
ani docelowej nawigacji; zachowanie szkieletu dla brakujących plików i stron określono powyżej. Nie wykonano
implementacji ani testu tego zachowania.

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

### Blokada wgrywania DDL — uzgodniony fragment S2-T2

**Uzgodnione 14 listopada 2026:** próbę wysłania kolejnej paczki przy
aktywnej globalnej blokadzie backend odrzuca odpowiedzią HTTP `409`
i kodem `DDL_PROCESSING_IN_PROGRESS`. Blokada obowiązuje od rozpoczęcia
wysyłania, podczas analizy oraz oczekiwania na automatyczne ponowienie,
również między projektami i kartami przeglądarki.
Interfejs pokazuje: „Trwa przesyłanie lub analiza DDL. Poczekaj na
zakończenie”.

Nie zatwierdza to jeszcze ścieżki uploadu, pól żądania, pełnej odpowiedzi
błędu ani kontraktu zwalniania blokady. Wspólny format uzgodniony dla
projektów poniżej nie zostaje przez to automatycznie rozszerzony na
wszystkie operacje DDL.

### Projekty — uzgodniony zakres S2-T1

**Uzgodnione 14 listopada 2026:** poniższe operacje i kody odpowiedzi
zatwierdzono podczas planowania S2-T1. Nie jest to akceptacja całego LLD.

| Metoda i ścieżka | Znaczenie | Odpowiedź po sukcesie |
| --- | --- | --- |
| `POST /api/v1/projects` | Utworzenie projektu z `name` i opcjonalnym `description`. DDL nie jest wymagany przy tworzeniu. | `201` |
| `GET /api/v1/projects` | Pobranie listy zapisanych projektów. | `200` |
| `GET /api/v1/projects/{project_id}` | Pobranie wybranego projektu. | `200` |

Uzgodnione błędy: `422` dla niepoprawnych pól, `409` dla zajętej nazwy
i `404` dla nieistniejącego projektu. Walidację pól i unikalność nazw
określa sekcja 5.1 specyfikacji. Błąd nie nadpisuje istniejącego projektu.
Wgrywanie DDL należy do S2-T2, a nie do komendy tworzenia projektu.

**Uzgodnione 14 listopada 2026 — obiekt projektu:** `id` jako identyfikator
nadany przez backend, `name` jako zapisana nazwa, `description` jako
zapisany opis albo `null`, `created_at` jako czas utworzenia nadany
przez backend. Ten sam zestaw pól obowiązuje w odpowiedzi utworzenia,
odczycie pojedynczego projektu i dla każdego elementu listy.
Format identyfikatora i czasu oraz postać i kolejność listy
doprecyzowano poniżej.

**Do wyjaśnienia:** techniczna realizacja unikalności nazw i powiązanie
operacji z uzgodnionym kontekstem dostępu z S1-T6.
Wspólny kształt błędu powyżej zatwierdzono dla opisanych niżej
błędów projektów, nie dla wszystkich pozostałych operacji aplikacji.

**Uzgodnione 14 listopada 2026 — format pól technicznych:** `id` jako tekstowy
UUID, `created_at` jako tekst daty i czasu w formacie ISO 8601 w UTC,
z końcówką `Z`. Obie wartości nadaje backend; klient nie wybiera ich
przy tworzeniu projektu. Nie wybrano przez to konkretnej wersji UUID
ani biblioteki generującej identyfikatory.

**Uzgodnione 14 listopada 2026 — lista projektów:** `GET /api/v1/projects`
zwraca `{"items": [...]}` ze wszystkimi zapisanymi projektami, bez
podziału na strony w MVP. Każdy element ma zatwierdzone pola obiektu
projektu. Sortowanie: `created_at` malejąco, a przy identycznym czasie
`id` rosnąco. Brak projektów daje `200` i `{"items": []}`, nie błąd.
Jest to zatwierdzony kontrakt listy dla S2-T1.

**Uzgodnione 14 listopada 2026 — błędy projektów:** wykorzystujemy wspólną
strukturę `error` z polami `code`, `message`, `request_id`,
`automatic_retry_allowed` i `details`. `code` identyfikuje rodzaj błędu
dla interfejsu, `message` jest czytelnym komunikatem, `request_id`
umożliwia powiązanie błędu z obsługiwanym żądaniem, a `details` przenosi
szczegóły, np. wskazanie błędnego pola. Dla opisanych błędów `422`,
`409` i `404` obowiązuje `automatic_retry_allowed=false`.
Kody tekstowe i format `details` doprecyzowano poniżej.

**Uzgodnione 14 listopada 2026 — kody i szczegóły błędów projektów:**

| HTTP | `error.code` | Znaczenie |
| --- | --- | --- |
| `422` | `VALIDATION_ERROR` | Niepoprawne dane żądania. |
| `409` | `PROJECT_NAME_CONFLICT` | Nazwa projektu jest już zajęta. |
| `404` | `PROJECT_NOT_FOUND` | Projekt nie istnieje. |

`details` ma postać `{"fields": [...]}`. Każda pozycja
zawiera `field` (nazwę pola) i `message` (czytelny opis problemu).
Dla konfliktu nazwy pozycja wskazuje `name`; dla nieistniejącego projektu
lista jest pusta. Format nie zakłada zwracania odrzuconej wartości pola,
treści zapytań SQL ani szczegółów bazy.

**Uzgodnione 14 listopada 2026 — walidacja wejścia projektów:** body komendy
utworzenia jest obiektem JSON. `name` jest wymaganym tekstem, a `description`
tekstem, `null` albo pominiętym polem. `null`, pominięcie i pusty opis
po usunięciu brzegowych białych znaków oznaczają brak opisu.
Nie konwertujemy liczb, wartości logicznych, tablic ani obiektów na tekst.
Brak `name`, `name=null`, błędny typ, dodatkowe pola (także `id`
i `created_at`) oraz niepoprawny UUID w ścieżce dają `422 VALIDATION_ERROR`.
Niepoprawny UUID wskazujemy przez `field=project_id`; dodatkowe pole
przez jego nazwę.

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

Kolejną próbę uruchamia się jako nowe wykonanie przygotowanego zlecenia, z nowym `Idempotency-Key`. Dawny kontrakt `POST /api/v1/runs/{run_id}/new-run`, kopiujący wymagania z historii, jest poza MVP.

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
- Samo przyjęcie anulowania nie potwierdza dostępności plików. Odczyt statusu i eksport uwzględniają REQ-047: wcześniej zapisany użyteczny kandydat z raportem jest dostępny także po anulowaniu lub błędzie. Pobranie nie zmienia `lifecycle` ani nie nadaje `FULFILLED`.

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
    "extraction_issues": []
  }
}
```

Generator nadaje `candidate_id`; backend sprawdza, że nie istnieje konflikt, i publikuje go dopiero po weryfikacji manifestu i artefaktów. `table_refs` w przykładzie są nazwami prezentacyjnymi; właściwy kontrakt wiąże je z identyfikatorami obiektów w interpretacji schematu.

`COMPLETE` oznacza tylko wyodrębnienie deklarowanych plików, nie kompletność planu ani importowalność. Przy błędnej treści modelu `extraction_status=INVALID`, `files` może być puste, a `extraction_issues` wyjaśnia naruszenia. Surowa odpowiedź może być potrzebna bieżącej poprawce, lecz nie archiwizujemy jej jako historii; jej przekazanie nie jest obowiązkowym polem manifestu danych.

Podział kilku wywołań i plików pozostaje częścią wersjonowanej strategii i OD-10. W bazowym projekcie jedna runda publikuje jeden kandydat; nie zakładamy, że oznacza to jedno wywołanie modelu.

## 6. Walidacja

`POST /internal/v1/validate` zawiera tę samą kopertę operacji i dodatkowo: `candidate_id`, `manifest_artifact_id`, `manifest_sha256`, `snapshot` oraz `validation_profile_id`. Profil określa wymagany zestaw sprawdzeń, nie tylko listę tych, które walidator akurat wykonał.

Potwierdzona kolejność: format → wstępna zgodność schematu i typów → rzeczywisty import, obowiązujące relacje i kompletność → dodatkowe reguły biznesowe. Proponowane wartości `stage`: `FORMAT`, `SCHEMA_PRECHECK`, `TRIAL_IMPORT`, `COMPLETENESS`, `BUSINESS`; kompletność jest częścią etapu po imporcie, nie dodatkową alternatywą dla niego. W tym etapie osobno sprawdzamy relacje zatwierdzone poza DDL. Muszą być oznaczone jako obowiązkowe dla wykonania zadania, a nie jedynie dla `BUSINESS_CONFORMANCE`. Dokładne oznaczenie etapu i podsumowania tych sprawdzeń w kontrakcie pozostaje do doprecyzowania. Szczegóły i statusy decyzji opisuje [projekt walidacji](walidacja.md).

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

To fragment, nie pełny raport: kompletny kontrakt ma również tożsamość operacji, hashe, profil, wersję walidatora, raport artefaktowy oraz wszystkie wymagane sprawdzenia formatu, schematu, obowiązujących relacji i liczebności. Samo `complete=true` i `importable=true` nie wystarcza do kwalifikacji kandydata bez dowodów zgodności relacji zatwierdzonych poza DDL.

Status sprawdzenia: `PASS`, `VIOLATION`, `NOT_RUN`, `UNSUPPORTED`, `UNDETERMINED`. Niewykonane sprawdzenie ma przyczynę; liczbę naruszeń nieznaną zapisujemy jako NULL. Brak dowodów kompletności lub importowalności uniemożliwia odpowiednio `complete=true` lub `importable=true`. Brak dowodu relacji zatwierdzonej poza DDL blokuje sukces zadania bez zmiany wyniku samego importu.

Awaria infrastruktury ma kontrakt błędu, a nie raport z zerem naruszeń. Dostępne częściowe dowody mogą trafić do bieżącego raportu, ale nie potwierdzają sukcesu.

## 7. Pomiary bieżącego wykonania, bez archiwum wiadomości

Dawny kontrakt `trace-events`, obejmujący pełne żądania, odpowiedzi i kursor historii, jest poza MVP. Nie wdrażamy go jako warunku rozpoczęcia każdego wywołania.

Generator nadal przekazuje dostępne pomiary i błędy potrzebne raportowi, bez sekretów i bez podwójnego naliczania tych samych wywołań. Brak pomiaru jest oznaczany jako brak, nie zero. Dokładny uproszczony kontrakt wymaga OD-05 i OD-07; jego transport nie został wybrany przez rezygnację z historii.

Przed kolejnym wywołaniem nadal obowiązują kontrola anulowania, termin i uprawnienie operacji. Awaria wymaganego mechanizmu kończy pracę bez ponowienia modelu. Spóźniona odpowiedź nie może uruchomić kolejnego etapu. Nie obiecujemy atomowego cofnięcia żądania już wysłanego do dostawcy.

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
- Po zakończeniu/anulowaniu nie przyjmujemy spóźnionej odpowiedzi jako nowego skutecznego kandydata. Nie blokuje to udostępnienia i opakowania wcześniej zapisanych, sprawdzonych artefaktów z ich raportem zgodnie z REQ-047. Dopuszczalny zapis dowodów diagnostycznych ma osobny zakres i nie zmienia wybranego kandydata.

Usługi wywoływane przez backend uwierzytelniamy sekretem usługi z konfiguracji. Dostęp zwrotny do pomiarów i artefaktów dodatkowo ogranicza losowy token operacji, przesłany poza logowanym body. Adres backendu jest stałą konfiguracją, nie callbackiem od użytkownika. Token i nagłówki nie są kopiowane do raportów ani diagnostyki.

## 9. Profile — konkretne propozycje do OD-04 i OD-10

### `insert-postgresql-proposed-v1`

Jeden plik UTF-8 z gotowymi `INSERT`, jawnymi listami kolumn i dozwolonymi wartościami/wyrażeniami z macierzy OD-01. Bez DDL, komend transakcyjnych, wyłączania ograniczeń i dowolnych zapytań. Dokładna lista dopuszczonych wyrażeń musi być zatwierdzona przed uruchomieniem walidacji.

### `csv-postgresql-proposed-v1`

Do oceny: UTF-8 bez BOM, przecinek, podwójny cudzysłów jako quote/escape, nagłówek z ustaloną kolejnością kolumn, oddzielny plik na tabelę i jawny znacznik NULL `\N`. Cytowany tekst `"\N"` jest wartością tekstową, nie NULL. Format wartości dat, czasu, liczb i typów dodatkowych wymaga macierzy.

Nie zmieniamy zakończeń linii ani cytowania w odebranym pliku. Parser struktury CSV i rzeczywisty import mają ten sam profil. Pusta komórka nie jest automatycznie traktowana jako NULL.

To kandydaci profili, nie wybór obsługi całego PostgreSQL.

## 10. Raport i eksport

`GET /api/v1/runs/{id}/report` zwraca wersjonowany dokument, a `/export` paczkę dostępną zgodnie z REQ-047. Wcześniej zapisany użyteczny kandydat z raportem może być pobrany także dla `CANCELLED` i `FAILED_TECHNICALLY`; raport zachowuje stan i przyczynę przerwania oraz wyniki sprawdzeń konkretnego kandydata. Nie wznawiamy modelu ani walidacji na potrzeby pobrania. Dostępność częściowych lub niesprawdzonych artefaktów pozostaje w OD-08. Zgodnie z REQ-039 i rozstrzygniętym OD-03 zwracamy wyłącznie najnowszego użytecznego kandydata z jego raportem, bez rankingu jakości.

Proponowane minimum raportu: `report_version`, identyfikacja projektu/wykonania, hash migawki, wariant, status/powód, wybrany kandydat i manifest, walidacja/metoda, oczekiwane/rzeczywiste liczebności, reguły, rundy, czasy i pomiary z dostępnością.

Raport ma stabilny `candidate_id` i `validation_report_id`. Paczka nie wybiera „ostatniego pliku z katalogu”. Błąd pobierania po zakończeniu jest błędem dostarczenia artefaktu, nie powodem ponownej generacji.
