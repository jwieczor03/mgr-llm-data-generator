# Architektura niskopoziomowa — LLD v0.1

**Data:** 21 października 2026.

**Status:** konkretny projekt do przeglądu, nie implementacja ani zatwierdzenie otwartych wymagań.

**Podstawa:** [specyfikacja MVP](../specyfikacja_mvp.md), [ustalenia](../ustalenia_architektoniczne.md) i [serwisy](../serwisy_i_technologie.md).

**Uzupełnienie uzgodnione 21 października 2026:** [cztery etapy walidacji i rzeczywisty próbny import](walidacja.md). Pozostałe szczegóły LLD zachowują status propozycji.

## 1. Zakres i kolejność czytania

| Dokument | Co ustala na poziomie projektu |
| --- | --- |
| Ten dokument | Moduły, kierunek zależności, klasy, porty, przygotowanie kontekstu i punkty rozszerzeń. |
| [Model danych](model_danych.md) | Tabele, pola, niezmienność, klucze, indeksy i granice transakcji. |
| [Kontrakty API](kontrakty_api.md) | Komendy, odpowiedzi, błędy, kontrakty usług, historia i transfer plików. |
| [Cykl wykonania](cykl_wykonania.md) | Maszyna stanów, algorytm, wyścigi, anulowanie, timeouty, restart i testy. |
| [Walidacja](walidacja.md) | Zatwierdzona kolejność i próbny import oraz odrębne propozycje zakresu PostgreSQL, środowiska i reguł biznesowych. |

Projekt wykorzystuje trzy proponowane serwisy backendowe oraz React. Nie zmienia go w monolit, ale też nie wprowadza mikroserwisu dla każdej klasy. Nie budujemy event sourcingu, uniwersalnego workflow ani własnego frameworka DI.

## 2. Zasady obowiązujące każdą implementację

1. Zatwierdzony plan i migawka wykonania są niezmienne.
2. Model przygotowuje gotowy SQL/CSV; aplikacja nie generuje go z rekordów pośrednich.
3. Kandydat jest niezmiennym manifestem dokładnych plików; poprawka tworzy nowego kandydata.
4. Walidacja dotyczy konkretnego kandydata, migawki i profilu walidatora.
5. Backend jest jedynym właścicielem trwałej historii i decyzji o kolejnych etapach.
6. Naruszenia danych i błędy techniczne mają różne kontrakty; wyjątek transportu nie staje się prośbą o poprawkę.
7. Nie ma automatycznego retry, fallbacku, wznowienia i odtwarzania pracy po restarcie.
8. Brak pomiaru nie jest zerem. Stan procesu nie jest oceną realizmu.
9. Obowiązują uprawnienia do projektu, operacji i artefaktu, a nie zaufanie do identyfikatora otrzymanego od modelu.
10. Zmiana adaptera wymaga zgodności kontraktu i testów. Zmiana dialektu danych nie jest samą wymianą repozytorium.

## 3. Proponowana struktura kodu

Poniższe ścieżki opisują przyszłą strukturę, a nie utworzone pliki:

```text
apps/web/src/
  features/projects/
  features/orders/
  features/runs/
  api/                     # klient i DTO z kontraktu, bez własnego modelu procesu

services/application-api/src/application_api/
  domain/
    projects.py            # identyfikacja projektu i własność
    requirements.py        # zatwierdzony plan i wersje wymagań
    runs.py                # Run, przejścia i globalny limit rund
    candidates.py          # Candidate, Eligibility, CandidateSelectionPolicy
  application/
    projects/              # upload i analiza DDL
    preparation/           # interpretacja, doprecyzowanie i zatwierdzenie
    context/               # DependencyContextProvider
    executions/            # StartRun, RunCoordinator, CancelRun, StartupReconciler
    reporting/             # raport, historia, opakowanie eksportu
    ports/                 # repozytoria, UoW, klient generatora/walidatora, magazyn
  adapters/
    http/public/           # API przeglądarki
    http/internal/         # ślad i artefakty w zakresie operacji
    postgres/              # modele ORM i repozytoria
    artifacts/             # LocalArtifactStore
    services/              # HttpGenerationClient, HttpValidationClient
    runner/                # LocalExecutionRunner
    identity/              # LocalActorContextProvider
    schema/                # adapter parsera DDL
  bootstrap.py             # składanie zależności i cykl życia

services/generation-service/src/generation_service/
  application/             # InterpretRequirements, GenerateCandidate, CorrectCandidate
  domain/                  # kontrakt strategii i własne typy wyniku
  ports/                   # LlmClient, TraceSink, ArtifactWriter
  adapters/                # FastAPI, LiteLLM, HTTP do backendu, rejestr operacji
  strategies/              # pierwszy prosty wariant; inne dopiero do badań
  bootstrap.py

services/validation-service/src/validation_service/
  application/             # ValidateCandidate, CancelValidation
  domain/                  # CheckResult, ValidationProfile, CandidateEligibility
  ports/                   # SqlParser, ValidationEnvironment, BusinessRuleEvaluator
  adapters/                # FastAPI, parser, CSV, Psycopg, HTTP do artefaktów
  checks/                  # format, precheck, próbny import/kompletność, reguły
  bootstrap.py

contracts/                 # wersjonowane opisy transportu i przykłady zgodności
tests/                     # testy domeny, adapterów, kontraktów i ścieżki E2E
deploy/                    # przyszła konfiguracja lokalna
```

Wewnątrz serwisu zależności wskazują do środka: adapter → przypadek użycia → domena. Domena nie importuje FastAPI, Pydantic, SQLAlchemy ani LiteLLM. DTO Pydantic powstają na granicach i są mapowane na własne typy.

Nie kopiujemy całego modelu domeny do wspólnej biblioteki trzech serwisów. Wspólne są kontrakty komunikacji, nie repozytoria, sesje bazy ani klasy parsera. Nie tworzymy osobnej klasy i interfejsu dla każdej prostej funkcji.

## 4. Główne obiekty i odpowiedzialności

| Obiekt | Odpowiedzialność | Czego nie robi |
| --- | --- | --- |
| `ApprovedRequirements` | Schemat i interpretacja, reguły, tabele/liczebności, polecenie i profil wyniku. | Nie zawiera kluczy API ani zmiennego „aktualnego projektu”. |
| `Run` | Legalne przejścia, `version`, blokada po anulowaniu i licznik rund. | Nie wykonuje HTTP ani SQL. |
| `RunCoordinator` | Zleca kroki, zapisuje ich skutki i kończy proces. | Nie generuje rekordów i nie ocenia realizmu. |
| `Candidate` | Tożsamość manifestu, pochodzenie i odwołania do plików. | Nie nadpisuje poprzednika. |
| `CandidateEligibility` | Odrębne potwierdzenie kompletności i importowalności. | Nie jest zbiorczą oceną biznesową. |
| `ContextPackage` | Dokładne fragmenty i ślad selekcji dla konkretnej operacji. | Nie zastępuje pełnych wymagań i walidacji. |
| `Operation` | Jedno zlecenie usługi, uprawnienie, termin i fencing. | Nie jest trwałym workflow z retry. |
| `ModelCall` | Jedno faktyczne wywołanie dostawcy i dostępne dowody jego przebiegu. | Nie jest synonimem rundy. |
| `ValidationReport` | Wyniki sprawdzeń i profil metody dla konkretnej wersji danych. | Nie ogłasza sukcesu całego procesu. |
| `ExportBuilder` | Opakowuje wybrany manifest i raport bez zmiany plików. | Nie odtwarza CSV/SQL z tabel walidacyjnych. |

## 5. Porty — proponowane sygnatury

Pseudokod kontraktów, nie kod do skopiowania bez definicji typów:

```python
class UnitOfWork:
    async def __aenter__(self) -> "UnitOfWork": ...
    async def commit(self) -> None: ...
    async def __aexit__(self, exc_type, exc, tb) -> None: ...

class RunRepository:
    async def lock(self, run_id: RunId, project_id: ProjectId) -> Run: ...
    async def save(self, run: Run, expected_version: int) -> None: ...

class GenerationClient:
    async def generate(self, request: GenerationRequest) -> GenerationResult: ...
    async def correct(self, request: CorrectionRequest) -> GenerationResult: ...
    async def cancel(self, operation_id: OperationId) -> StopAcknowledgement: ...

class ValidationClient:
    async def validate(self, request: ValidationRequest) -> ValidationResult: ...
    async def cancel(self, operation_id: OperationId) -> StopAcknowledgement: ...

class LlmClient:
    async def complete(self, request: ModelRequest,
                       control: OperationControl) -> ModelResult: ...

class ContextProvider:
    async def build(self, requirements: ApprovedRequirements,
                    budget: ContextBudget) -> ContextPackage: ...

class ArtifactStore:
    async def write(self, upload: AuthorizedUpload) -> StoredArtifact: ...
    async def open(self, reference: AuthorizedArtifactRef) -> ByteStream: ...

class CandidateSelectionPolicy:
    def select(self, eligible: list[EvaluatedCandidate]) -> Selection: ...
```

UoW wycofuje niezatwierdzoną transakcję przy wyjściu. `OperationControl` zawiera termin, sygnał anulowania i tożsamość operacji, nie token użytkownika. Błędy techniczne są osobnymi typami, a nie `GenerationResult` udającym puste dane.

Interfejsy domenowe nie zwracają `Response`, `AsyncSession`, obiektu LiteLLM ani AST parsera. Adapter SQLAlchemy używa osobnej sesji dla każdej transakcji/zadania; dokumentacja ostrzega przed współdzieleniem `AsyncSession` przez współbieżne zadania [N1].

## 6. Przygotowanie wymagań i kontekstu

### 6.1. Rewizje, nie zmiana historii

1. Wgranie DDL tworzy nową `SchemaVersion`; bajty oryginału nie są nadpisywane.
2. Analiza tworzy `SchemaInterpretation`, wiążącą wersję DDL, profil parsera i jawne uzupełnienia interpretacji.
3. Propozycja relacji nieobecnej w DDL ma `source=USER_APPROVED`, identyfikator i zapis zatwierdzenia. Nie jest dopisywana po cichu do DDL.
4. Interpretacja reguły i plan danych są rewizjami. Nowa propozycja nie zmienia dawnej zatwierdzonej rewizji.
5. Zatwierdzamy identyfikator i hash konkretnej rewizji. Start nie korzysta z ruchomego „latest”.

### 6.2. `DependencyContextProvider`

Przed zatwierdzeniem model może proponować zakres na podstawie katalogu schematu i jego potrzebnych fragmentów. Po zatwierdzeniu kontekst jest związany z ustalonym planem.

Algorytm bazowy:

1. Pobierz dokładnie przypiętą interpretację, plan i reguły.
2. Ustal obiekty wskazane planem oraz wymagane definicje zależności.
3. Jeśli brakuje danych wymaganych przez relację, zwróć blokadę. Przed startem można zaproponować rozszerzenie do zatwierdzenia; w trakcie wykonania nie zwiększamy samowolnie liczebności.
4. Wybierz oryginalne fragmenty DDL i zatwierdzone uzupełnienia. Struktura parsera pomaga wybierać, nie przepisuje ograniczeń.
5. Dołącz zasady profilu wyjściowego, reguły i wskazówki jakościowe.
6. Sprawdź budżet całego wywołania: instrukcje, schemat, rozmowa, raport poprawki i rezerwa odpowiedzi. Sposób oszacowania zapisz; brak wiarygodnej oceny oznacza jawną niepewność, nie gwarancję.
7. Zapisz pakiet kontekstu, hash i wersję selekcji przed użyciem.

Za duży kontekst daje `CONTEXT_BUDGET_EXCEEDED` albo prowadzi do jawnie zdefiniowanego wielowywołaniowego wariantu. Nie skracamy wymagań ani odpowiedzi w ukryciu. Globalny budżet rund pozostaje jeden.

pgvector pozostaje opcjonalną implementacją selekcji. Ani embedding, ani wynik `top-k` nie zastępują uzupełnienia zależności. Walidator otrzymuje pełne wymagania, nie tylko fragmenty wybrane dla LLM.

## 7. Generator i walidator wewnątrz

### Generator

`GenerateCandidateHandler → GenerationStrategy → LlmClient`

- `TracedLlmClient`/rekorder adaptera utrwala próbę i rzeczywiste wiadomości w sposób opisany w kontraktach. Sam zapis logicznego promptu przed mapowaniem dostawcy nie wystarcza.
- `ArtifactExtractor` wyodrębnia zadeklarowane treści bez poprawiania ich zawartości.
- Jeśli model zwróci niepoprawny format, powstaje kandydat diagnostyczny z `extraction_issues`; surowa odpowiedź pozostaje w historii. To naruszenie danych, nie awaria transportu.
- `OperationRegistry` zna aktywne zadania lokalnego procesu. Restart nie odtwarza ich z bazy.

### Walidator

`ValidateCandidateHandler → FormatChecks → SchemaPrechecks → TrialImportAndCompleteness → BusinessRuleChecks`

- Każdy etap tworzy listę `CheckResult`, bez domyślnego pozytywnego wyniku.
- Parser SQL sprawdza dozwolone instrukcje i wyrażenia. Nie dzielimy SQL prostym `split(";")`.
- Parser CSV sprawdza strukturę i profil. Do importu trafiają oryginalne bajty, nie ponownie zapisane rekordy.
- Wstępne sprawdzenia schematu i typów poprzedzają rzeczywisty import; nie zastępują jego wyniku ani semantyki typów PostgreSQL. Po imporcie osobno porównujemy rzeczywiste liczebności z planem.
- `ValidationEnvironment` przygotowuje obszar próby i sprząta go także po przerwaniu.
- `BusinessRuleEvaluator` ma rejestr jawnie obsługiwanych rodzajów sprawdzeń. Model proponuje ich parametry, nie dowolny kod do wykonania.

**Propozycja OD-06:** pierwszym typem może być `column_comparison.v1` z tabelą, dwiema kolumnami, operatorem, znaczeniem NULL i jednostką naruszenia. Agregacje wymagają osobnej zatwierdzonej definicji. Nie obiecujemy w tej wersji obsługi dowolnej reguły tekstowej.

**Uzgodniono metodę OD-02:** rzeczywisty próbny import do pustego, odizolowanego PostgreSQL. **Proponowana organizacja:** odrębna baza tymczasowa dla operacji w osobnej instancji walidacyjnej pozwala zachować kwalifikowane nazwy z DDL bez przepisywania kandydata. Adapter provisioningu ma uprawnienia tylko w tej instancji i generuje nazwy zasobów sam. Role prób nie mają dostępu do innych baz, hosta ani `app-db`. Wymaga to przeglądu uprawnień, listy dozwolonych konstrukcji i testów; nie stanowi gotowej piaskownicy bezpieczeństwa.

### 7.1. Granice wykonania walidacji

1. Przed próbą w silniku parser sprawdza zarówno DDL, jak i SQL kandydata, włącznie z funkcjami i wyrażeniami. Sama zgodność składni nie daje uprawnienia do wykonania.
2. Profil dopuszcza konkretne konstrukcje; nie dopuszcza wyzwalaczy, własnych procedur, rozszerzeń, dostępu do plików hosta ani `COPY PROGRAM`. Walidator nie otrzymuje gniazda Docker ani poświadczeń `app-db`.
3. Próba importuje całą paczkę w ustalonej kolejności i sprawdza także ograniczenia odroczone. Nie pomija błędnych wierszy i nie wyłącza ograniczeń dla uzyskania pozytywnego raportu.
4. Dopiero na poprawnie załadowanych danych potwierdza liczebności i wykonuje dodatkowe reguły. Jeśli wcześniejsza warstwa to uniemożliwia, dalsze sprawdzenia mają `NOT_RUN` z przyczyną; nie są domyślnie zaliczone.
5. Adapter klasyfikuje rozpoznane błędy danych jako naruszenia, a utratę połączenia, timeout lub awarię silnika jako błąd techniczny. Nieznany wyjątek nie jest automatycznie błędem danych przeznaczonym do poprawienia przez model.
6. Generator ani walidator nie przyjmują od modelu adresów usług, poświadczeń i poleceń administracyjnych. Uprawnienia provisioningu pozostają odrębne od ograniczonej roli importującej dane.

Szczegółowy zakres dopuszczonych instrukcji, wartości i ograniczeń wymaga macierzy OD-01. Próbny import wybrano w rozmowie; nie oznacza to zatwierdzenia całej proponowanej topologii, ról ani profili.

## 8. Konfiguracja i składanie

- `bootstrap` składa konkretne adaptery i rejestr strategii. Endpointy nie wybierają implementacji na podstawie dowolnej nazwy klasy od użytkownika.
- Wersja wariantu obejmuje strategię, prompty, sposób kontekstu, modele i ustawienia niebędące sekretami. Przypięty profil walidacji też jest częścią porównywalnego wykonania.
- Sekrety i adresy pochodzą z konfiguracji instalacji; w historii zapisujemy bezpieczne identyfikatory konfiguracji.
- `Clock` i generator identyfikatorów mogą być podstawiane w testach; nie potrzebujemy osobnego serwisu czasu.
- W bazowym MVP jeden proces backendu prowadzi runner. Generator i walidator również mają po jednej instancji procesu z lokalnym rejestrem operacji. Konfiguracja wielu workerów/replik jest niedopuszczona, dopóki nie powstanie wspólna polityka przydziału i identyfikacji instancji.

### 8.1. Interfejs przeglądarkowy

- `features/projects` ma zapytania projektu i wersji schematu, `features/orders` — edycję propozycji i zatwierdzenie rewizji, `features/runs` — status, historię i pobrania.
- Proponowane klucze zapytań: `["project", projectId]`, `["order", orderId, revisionId]`, `["run", runId]` i `["run-history", runId, cursor]`. Późniejsza zmiana kontekstu właściciela czyści/oddziela cache.
- `useStartRun` jest mutacją wywołaną akcją użytkownika, nie skutkiem renderowania lub odświeżenia strony. Zachowuje klucz komendy do rozstrzygnięcia niepewnej odpowiedzi.
- `useRunStatus` odpytuje o stan, ale nie ponawia komend. Zatrzymuje polling po stanie terminalnym; błąd samego odczytu pokazuje osobno, bez dopisywania awarii wykonania.
- `useCancelRun` pokazuje przyjęte żądanie jako oczekiwanie na rozstrzygnięcie, nie natychmiastowy sukces zatrzymania.
- Formularz przechowuje lokalny draft, a zatwierdzony dokument i hash pochodzą z backendu. Odpowiedź ze starej rewizji nie podmienia nowszego widoku.
- Podgląd DDL i odpowiedzi modelu jest tekstem, nie wykonywanym HTML. Nazwa pliku i opis reguły nie są zaufanym markupem.

### 8.2. Dostęp do lokalnego API

- Publiczny port aplikacji wiążemy z interfejsem loopback; portów wewnętrznych usług i baz nie wystawiamy do sieci lokalnej ani Internetu.
- Proponujemy wspólny origin UI i publicznego API; podczas developmentu Vite przekazuje `/api` do backendu. Nie włączamy CORS `*`.
- Backend sprawdza dozwolony `Host` oraz `Origin` dla komend przeglądarkowych; komendy JSON wymagają właściwego `Content-Type`. Zapis nie jest dostępny przez `GET`.
- Lokalny kontekst właściciela nie oznacza uwierzytelnienia przeglądarki. Ochronę przed żądaniami obcej witryny trzeba sprawdzić testem; brak logowania nie jest zgodą na dowolne zewnętrzne żądania.
- API wewnętrzne nie korzysta z przeglądarkowej ścieżki zaufania: wymaga uwierzytelnienia usługi i ograniczonego tokenu operacji. Publiczne proxy nie udostępnia `/internal`.

To propozycja zabezpieczenia lokalnego MVP, nie wdrożenie logowania ani deklaracja gotowości do publicznego hostowania.

## 9. Propozycje do zatwierdzenia, nie ukryte ustalenia

| ID | Propozycja LLD | Zależność |
| --- | --- | --- |
| LP-01 | UUID generowane w aplikacji, krótkie transakcje i warunkowe zapisy wersji. | Próba adaptera bazy. |
| LP-02 | Jedno miejsce pracy dla wykonania lub przygotowania LLM; odrzucenie zajętego startu bez kolejki. | Próba runnera. |
| LP-03 | Anulowanie natychmiast blokuje kolejne kroki i podnosi `execution_epoch`; zwolnienie miejsca po lokalnym zatrzymaniu. | Szczegóły OD-07 i OD-08. |
| LP-04 | Długie HTTP tylko między runnerem a usługą; osobne API anulowania, śladu i plików. | Próba transportu i timeoutów. |
| LP-05 | Jawne, wersjonowane profile SQL/CSV oraz wykonywalnych reguł. | OD-01, OD-04, OD-06 i OD-10. |
| LP-06 | `CandidateSelectionPolicy`; do rozważenia najnowszy kompletny/importowalny kandydat, bez punktacji. | OD-03; nie przyjmujemy tego automatycznie. |
| LP-07 | Eksport oparty na niezmiennym manifeście i raporcie. | OD-04, OD-05 i dostępność OD-08. |

Nie ma jeszcze migracji ani kompletnego OpenAPI. Przykłady w dokumentach służą uzgodnieniu kontraktu. Specyfikacja v1.4 doprecyzowuje REQ-030 i częściowo rozstrzyga OD-02 po potwierdzeniu użytkownika; pozostałe propozycje nie zmieniają samodzielnie wymagań.

## 10. Źródła technicznych ograniczeń

Sprawdzone 21 października 2026; strony nie oznaczają wyboru wersji runtime:

| ID | Źródło |
| --- | --- |
| N1 | SQLAlchemy AsyncSession i współbieżne zadania: `https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html` |
| N2 | PostgreSQL blokady wierszy i długość transakcji: `https://www.postgresql.org/docs/18/explicit-locking.html` |
| N3 | PostgreSQL częściowe indeksy unikalne: `https://www.postgresql.org/docs/18/indexes-partial.html` |
| N4 | HTTPX, osobne timeouty connect/read/write/pool: `https://www.python-httpx.org/advanced/timeouts/` |
| N5 | Python asyncio, zadania, timeout i anulowanie: `https://docs.python.org/3/library/asyncio-task.html` |
