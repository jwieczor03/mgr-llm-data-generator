# mgr-llm-data-generator

Aplikacja do generowania syntetycznych danych testowych dla wielu powiązanych tabel PostgreSQL na podstawie schematu DDL, reguł biznesowych i polecenia w języku naturalnym.

Wynikiem są polecenia `INSERT` albo paczka CSV. Aplikacja ma sprawdzać kompletność i importowalność danych, wykonywać ograniczoną liczbę poprawek oraz udostępniać wynik z prostym raportem. MVP nie przechowuje historii wykonań; jest ona wyłącznie potencjalnym kierunkiem rozwoju.

## Status

Projekt jest na etapie specyfikacji i projektu architektury. Repozytorium zawiera dokumentację i początkowe szkielety, nie gotową aplikację. Zapisano kierunki technologiczne i szczegółową propozycję serwisów; konkretne wersje, część mechanizmów i fizyczny podział nadal wymagają potwierdzenia. Instrukcję uruchomienia szkieletu opisano poniżej.

MVP jest jednoosobowe i uruchamiane lokalnie. Jego zakres nie obejmuje obowiązkowego wdrożenia AWS, obsługi kolumn `json`/`jsonb` w schematach użytkownika, generowania samodzielnych dokumentów JSON ani automatycznej platformy eksperymentalnej. Obsługa tych kolumn jest potencjalnym kierunkiem rozwoju, nie zaplanowaną funkcją.

Interfejs działa w lokalnej przeglądarce. Model przygotowuje gotowy SQL albo treść CSV; aplikacja zapisuje, sprawdza i udostępnia wynik. Przerwanego wykonania nie wznawia się — ręczne ponowienie tworzy nową próbę od początku.

Głównym widokiem jest czat: użytkownik wybiera projekt, wpisuje polecenie, otrzymuje odpowiedź i dostępny wynik, a następnie może kontynuować rozmowę kolejnymi poleceniami. „Nowy czat”, odświeżenie i zamknięcie strony kończą dostęp do rozmowy i jej plików. Po powrocie, także po pełnym zamknięciu aplikacji, widzimy nowy czat. Przed odświeżeniem lub zamknięciem strony wymagamy ostrzeżenia o utracie danych; rezygnacja z wyjścia zachowuje rozmowę. Okno i możliwość jego wyświetlenia podlegają ograniczeniom przeglądarki opisanym w sekcji 11.1 specyfikacji. Zapisane projekty pozostają.

Opuszczenie czatu ma także anulować trwające generowanie (REQ-077). Samo otwarcie ostrzeżenia lub pozostanie na stronie go nie anuluje. Po przyjęciu anulowania aplikacja nie rozpoczyna dalszych etapów; nie obiecujemy natychmiastowego zatrzymania żądania już przyjętego przez dostawcę LLM. Mechanizm wykrycia wyjścia i przekazania anulowania pozostaje do doprojektowania.

W nadal dostępnym czacie po anulowaniu lub awarii można pobrać wcześniej zapisaną paczkę spełniającą obowiązkowe warunki wraz z jej raportem. Nie zmienia to statusu całego wykonania na wykonane.

W obrębie jednego wykonania zwracamy wyłącznie najnowszą paczkę spełniającą obowiązkowe warunki, bez rankingu dodatkowych naruszeń biznesowych. Stan roboczy chroni ją przed utratą przy nieudanej poprawce; nie jest archiwum dawnych wykonań. Historia czatów i plików jest wyłącznie kandydatem na dalszy rozwój aplikacji poza MVP.

Przy kolejnym poleceniu zmiany danych LLM otrzymuje dotychczasową paczkę jako kontekst i prośbę użytkownika. Poprawia wskazane dane, zamiast generować niezależny zestaw od zera. Poprawiona paczka przechodzi walidację i otrzymuje raport dotyczący tej wersji. Każda nowa prośba o zmianę ma własny limit, domyślnie 3 automatyczne rundy naprawcze po pierwszej zmienionej paczce, niezależny od wcześniejszych próśb.

Jeśli mimo tych rund nie uzyskano użytecznej poprawionej paczki, aplikacja informuje o niepowodzeniu i udostępnia poprzednią sprawdzoną wersję z jej raportem, bez przedstawiania jej jako realizacji nowej prośby. Użytkownik może ręcznie wybrać **„Podejmij kolejne 3 próby”**: tylko raz dla danej prośby, zlecając do 3 dodatkowych rund (REQ-078–REQ-079). Jeśli ta seria również nie da użytecznej poprawionej paczki, kończymy naprawy, informujemy o niepowodzeniu i nie pokazujemy ponownie przycisku. Poprzednia sprawdzona paczka z jej raportem pozostaje dostępna. Dodatkowe próby naprawiają ostatnią nieudaną wersję z uwzględnieniem wykrytych w niej błędów, nie zaczynają od poprzedniej sprawdzonej paczki. Po nieudanym pierwszym generowaniu bez użytecznej paczki przycisk dodatkowych 3 prób nie jest dostępny (AC-47). Nie jest to techniczne ponowienie po awarii. Przypisanie prośby i serii do wykonania, przekazanie kontekstu i sprzątanie pozostają do doprecyzowania.

Naruszenia danych uruchamiają automatyczne poprawki, domyślnie do 3 rund dla danej prośby, łącznie dla wszystkich jej tabel i wywołań modeli. Automatyczna poprawka nie odnawia limitu. Błąd techniczny kończy wykonanie bez automatycznego retry lub zmiany wariantu; użytkownik może uruchomić nową próbę.

Uzgodniona walidacja: składnia/format → wstępna zgodność ze schematem i typami → rzeczywisty próbny import do odizolowanego PostgreSQL, obowiązujące relacje i kompletność → dodatkowe reguły biznesowe. Relacje zatwierdzone poza DDL są sprawdzane osobno i obowiązkowe mimo udanego importu. Katalog reguł MVP obejmuje porównanie kolumn, porównanie wartości z progiem, zakresem lub zbiorem, regułę warunkową i ograniczoną regułę sumującą dane między tabelami. Szczegóły ich wykonania i dokładna macierz typów nadal wymagają uzgodnienia.

Architektura ma uwzględniać późniejsze hostowanie, logowanie, wielu użytkowników i skalowanie wykonania. W MVP przygotowujemy granice tych rozszerzeń, ale nie wdrażamy kont ani publicznego hostingu (REQ-066).

Zapisane kierunki to PostgreSQL jako źródło danych i wersji schematów, opcjonalny pgvector zamiast obowiązkowej osobnej bazy wektorowej oraz własny kontrakt LLM z LiteLLM SDK jako preferowaną implementacją po testach. Szczegółowy projekt korzysta z bazowego wariantu Python/FastAPI + React/TypeScript i proponuje trzy własne serwisy backendowe: zarządzanie, generowanie i walidację.

## Dokumentacja

**Design system v0.1 — zaakceptowany fundament wizualny:**
[zasady dla dewelopera](docs/ui/design-system.md),
[galeria komponentów](docs/ui/design-system.html) i [katalog ekranów](docs/ui/index.html).
Akceptacja z 14 listopada 2026 obejmuje kierunek wizualny oraz istniejące tokeny
i komponenty light/dark. Demonstracyjny czat jest wzorcem wyglądu, nie implementacją
aplikacji ani akceptacją wszystkich przepływów produktu.

| Dokument | Rola i status |
| --- | --- |
| [Plan realizacji MVP](docs/plan_realizacji_mvp.md) | Lokalny plan zaakceptowanych story S1–S9, standard opisów dla juniora i punkt kontynuacji. Zadania i podzadania dopracowujemy kolejno; publikacja na GitHubie odłożona na później. |
| [Specyfikacja MVP](docs/specyfikacja_mvp.md) | Obowiązujące wymagania, kryteria wykonania i akceptacji oraz jawne otwarte decyzje. Punkt wyjścia do pracy nad aplikacją. |
| [Rejestr ustaleń architektonicznych](docs/ustalenia_architektoniczne.md) | Zapis wymagań, kierunków LLM i bazy danych oraz statusów propozycji i otwartych decyzji. |
| [Serwisy i technologie](docs/serwisy_i_technologie.md) | Szczegółowa propozycja funkcji, narzędzi, kontraktów, własności danych, API, testów i lokalnego uruchomienia każdego komponentu. |
| [Architektura niskopoziomowa — LLD](docs/lld/README.md) | Projekt v0.1: moduły i interfejsy, model danych, kontrakty żądań/odpowiedzi, transakcje, maszyna stanów, anulowanie i okna awarii. |
| [Walidacja — ustalenia i propozycje](docs/lld/walidacja.md) | Potwierdzone cztery etapy, próbny import i objęcie MVP ograniczonym rodzajem reguły sumującej dane między tabelami. Szczegóły tej reguły, macierz PostgreSQL, środowisko i reprezentacja reguł pozostają otwarte. |
| [Architektura ogólna](docs/architektura.md) | Aktualny roboczy szkic odpowiedzialności, własności danych i przepływu, z uzgodnionym rozróżnieniem błędów technicznych i naruszeń danych. Podział procesów pozostaje propozycją. |
| [Analiza technologii](docs/analiza_technologii.md) | Wstępne porównanie FastAPI, NestJS i Django oraz narzędzi interfejsu, modeli, walidacji i uruchomienia. Rekomendacja do weryfikacji, nie zatwierdzony stos. |
| [Przepływy funkcjonalne](docs/przeplywy_funkcjonalne.md) | Objaśnienie zachowania opisanego w specyfikacji, bez narzucania architektury i technologii. |
| [Podział implementacji](docs/podzial_implementacji.md) | Robocza propozycja: własna logika produktu, gotowe mechanizmy i wymienne adaptery. Nie zatwierdza technologii ani liczby mikroserwisów. |
| [Przygotowanie do hostowania](docs/przygotowanie_do_hostowania.md) | Uzgodniony kierunek rozwoju i proponowane granice przyszłego logowania, izolacji danych i skalowania; bez wdrażania tych funkcji w MVP. |
| [Plan badań](docs/plan_badan.md) | Uzgodniony cel, główne pytanie, ramy porównania modeli i procesów oraz rekomendacje oparte na poprawności, czasie i koszcie. Pytania szczegółowe są robocze, protokół odłożono do czasu uzyskania aplikacji. Nie rozszerza MVP. |
| [Stan badań i literatura](badania/stan-badan.md) | Osobny obszar badawczy: ocena koncepcji pracy magisterskiej, podobne publikacje i otwarte decyzje. Nie zastępuje planu ani nie zatwierdza protokołu. |
| [Archiwum koncepcji](docs/archiwum/README.md) | Historyczne materiały zachowane do wglądu. Nie stanowią aktualnych wymagań ani wyborów technologicznych. |

W razie rozbieżności obowiązuje specyfikacja MVP. Dokumenty uzupełniające nie rozszerzają jej zakresu samodzielnie.

### Zadania S1 — fundament aplikacji

[Pakiet dziewięciu zadań S1](docs/plan_realizacji_mvp.md#s1--pakiet-zadań-do-przekazania-deweloperowi)
zawiera opisy, zależności, kryteria i planowane sprawdzenia:
szkielety aplikacji, konfigurację, lokalny start, bazę i migracje,
magazyn plików, dostęp, narzędzia testów, sprawdzenie całości
oraz niezależny monitor z panelem diagnostycznym.
T1–T3 dostarczają szkielety, konfigurację i lokalne uruchomienie.
T4 ma implementację i testy oraz oczekuje niezależnego review i odbioru;
pozostałe zadania są opisane w planie wraz ze swoim statusem.

### Zadania S3 do późniejszego przeniesienia na GitHub

[Pakiet S3 w planie realizacji](docs/plan_realizacji_mvp.md#s3--pakiet-do-późniejszego-przeniesienia-na-github)
zawiera indeks pięciu opisów zadań, zależności, kryteria ukończenia,
planowane sprawdzenia i checklistę późniejszego dodania do Issues oraz
GitHub Project. Opisy pozostają szkicami z jawnymi blokadami,
nie gotowymi instrukcjami implementacji. Nie zostały jeszcze opublikowane.

## Wykorzystanie w badaniach

W aktualnie doprecyzowywanym planie porównujemy również generowanie z aplikacją
z bezpośrednim użyciem LLM bez aplikacji. Wariant odniesienia otrzymuje
ten sam pełny DDL, oryginalne polecenie i reguły, bez dodatkowego kontekstu
aplikacji. Wykonuje jedno wywołanie bez poprawek, a wynik jest później
oceniany walidatorem bez przekazywania błędów modelowi. Pozostałe ustalenia zawiera
[plan badań](docs/plan_badan.md).

Ten sam model porównujemy bez aplikacji i w jej procesie bez podziału na
agentów. Badamy też podział na planistę, wykonawcę i reviewera tego samego
modelu. Reviewer ocenia, a wykonawca poprawia dane w ograniczonej pętli.

Autor będzie ręcznie zmieniał modele dostępne przez API lub uruchamiane lokalnie, prompty oraz organizację procesu, a następnie wykonywał te same zlecenia. Modele o otwartych wagach mogą być badane przez API albo lokalnie. Organizacja badań i gromadzenie ich materiałów pozostają poza aplikacją. Generator udostępnia bieżący wynik i prosty raport, bez historii wykonań i archiwum wiadomości.

Główna ocena badawcza obejmuje poprawność, błędy, czas i koszt. Realizm
danych i rozumienie zadania mogą być opisane jako obserwacje poboczne;
nie planujemy obowiązkowej osobnej ewaluacji realizmu. Docelowo aplikacja
będzie korzystać z wariantu wybranego na podstawie badań.
Wynikiem pracy mają być rekomendacje przy różnych priorytetach i opis
kompromisów między poprawnością, czasem i kosztem, nie jeden zbiorczy ranking.
Prompty są częścią przygotowania wariantów, bez osobnego badania technik
promptowania w głównym zakresie.

## Jak czytać wymagania

- **Wykonanie zadania:** uzyskano kompletny, importowalny wynik zgodny ze wszystkimi obowiązującymi relacjami, także zatwierdzonymi poza DDL.
- **Zgodność biznesowa:** raport opisuje spełnienie poszczególnych dodatkowych reguł; ich naruszenia mogą pozostać w wykonanym zadaniu.
- **Realizm:** ocena zewnętrzna, nie automatyczna gwarancja generatora.

Lista nierozstrzygniętych szczegółów znajduje się w sekcji 16 specyfikacji. Nie należy zastępować tych decyzji założeniami zaczerpniętymi z archiwum.

## Lokalne uruchomienie przez Docker Compose — S1-T3

Ten zakres uruchamia trzy backendy i PostgreSQL aplikacji. Gotowy frontend
udostępnia `application-api` pod `http://127.0.0.1:8000`, bez serwera Vite.
To nadal fundament aplikacji: S1-T4 dodaje połączenie `application-api`
z bazą i migracje; monitor z panelem na porcie 8080 należy do T9.

Potrzebny jest działający Docker z Compose co najmniej 2.24.4. Nie trzeba
instalować Pythona ani Node.js na hoście. Z katalogu głównego repozytorium
przygotuj lokalne pliki konfiguracji; `cp -n` zachowuje istniejące pliki:

```sh
cp -n .env.example .env
cp -n services/application-api/.env.example services/application-api/.env
cp -n services/generation-service/.env.example services/generation-service/.env
cp -n services/validation-service/.env.example services/validation-service/.env
```

W głównym `.env` wpisz własne `POSTGRES_PASSWORD`. `POSTGRES_DB` i
`POSTGRES_USER` określają inicjalizowaną bazę i konto administracyjne.
`APP_DB_USER` oraz `APP_DB_PASSWORD` określają osobne konto aplikacji.
Wpisz te same wartości w `services/application-api/.env`. Te parametry działają
przy inicjalizacji pustego wolumenu, nie zmieniają hasła istniejącego konta.

Każdy backend otrzymuje wyłącznie swój plik `.env`. Brak pliku lub wymaganych
ustawień backendu nie blokuje startu jego diagnostyki. Dla `application-api`
można ustawić adresy infrastruktury Compose:

```dotenv
APP_DB_HOST=app-db
APP_DB_PORT=5432
GENERATION_SERVICE_URL=http://generation-service:8000
VALIDATION_SERVICE_URL=http://validation-service:8000
```

Pozostałe wymagane pola opisuje sekcja konfiguracji backendów. Główny `.env`
nie uzupełnia automatycznie `APP_DB_*`. Bez pełnej konfiguracji raport
`/health/config` ma status `invalid`; frontend i `/health/live` nadal działają.
Status `valid` nie potwierdza połączenia z bazą; sprawdza je
`/health/database`. Generator, walidator i baza nie mają portów publikowanych
na hoście. Baza jest w osobnej sieci dostępnej tylko dla `application-api`.

Po uzupełnieniu hasła bazy uruchom:

```sh
docker compose config --quiet
docker compose up -d --build --wait
docker compose ps
curl --fail http://127.0.0.1:8000/health/live
curl --fail http://127.0.0.1:8000/health/config
```

Otwórz `http://127.0.0.1:8000`. Oczekiwanie `--wait` sprawdza działanie
procesów backendów i gotowość PostgreSQL, nie gotowość funkcji biznesowych.
Backendy nie czekają na gotowość bazy, aby móc udostępnić diagnostykę
również przy jej awarii. Brak hasła uniemożliwia start nowej bazy;
przyczynę sprawdzisz przez `docker compose logs --tail 50 app-db`.

Zmiana pliku `.env` w tym trybie wymaga odtworzenia danego kontenera,
ponieważ Compose przekazuje ustawienia do środowiska przy jego tworzeniu:

```sh
docker compose up -d --force-recreate application-api
```

Zwykłe zatrzymanie, ponowny start i usunięcie kontenerów bez kasowania danych:

```sh
docker compose stop
docker compose up -d --wait
docker compose down
```

Nazwany wolumen `app-db-data` zachowuje dane po tych operacjach. Usunięcie
wolumenu usuwa dane bazy i nie jest częścią zwykłego zatrzymania.
Pliki `.env`, zależności hosta i dane nie trafiają do kontekstu budowania.
Obrazy korzystają z Python 3.14.10, Node.js 26.13.1 tylko podczas budowania
frontendu, uv 0.11.1 i PostgreSQL 18.7. Biblioteki są instalowane z blokad.

### Sprawdzenie i ręczny odbiór S1-T3

1. Uruchom środowisko powyższymi poleceniami i otwórz stronę startową.
2. Sprawdź `/health/live`, `/health/config` i `/api/v1/nieznany`.
   Ostatni adres ma zwrócić JSON 404. Nieznana strona i brakujący plik
   również zwracają 404 zamiast strony startowej.
3. Wykonaj `docker compose stop app-db`. Frontend i oba endpointy
   diagnostyczne powinny nadal odpowiadać. Raport konfiguracji nie służy
   do wykrywania tej awarii. Przywróć bazę przez `docker compose up -d app-db`.
4. Zmień parametr backendu, odtwórz jego kontener i sprawdź nowy raport.
5. Zatrzymaj i uruchom środowisko ponownie. Port 8080 pozostaje niedostępny
   do czasu dostarczenia T9. Odbiór połączenia i migracji opisano poniżej.

Automatyczne testy rzeczywistych kontenerów uruchom osobno:

```sh
RUN_COMPOSE_TESTS=1 uv run --project services/application-api pytest tests/integration/test_compose.py -v
```

Testy budują obrazy, używają własnej konfiguracji i losowo nazwanego projektu,
tymczasowego portu oraz osobnego wolumenu. Sprawdzają frontend, komunikację
backendów, izolację bazy, trwałość danych po odtworzeniu kontenera, start
bez `.env` backendu, pierwszeństwo jawnie przekazanych ustawień kontenera
i brak `.env` w obrazach. Po wykonaniu usuwają wyłącznie swoje kontenery
i testowy wolumen. Nie wymagają wypełniania lokalnych plików `.env`.
Bez `RUN_COMPOSE_TESTS=1` ten zestaw jest pomijany.

## Baza i migracje — S1-T4

W głównym `.env` ustaw `APP_DB_USER` i `APP_DB_PASSWORD` inne niż konto
administracyjne `POSTGRES_USER`. Te same dane wpisz w konfiguracji
`services/application-api/.env`, wraz z nazwą bazy `APP_DB_NAME` zgodną
z `POSTGRES_DB`. Na nowym wolumenie obraz PostgreSQL tworzy konto bez
uprawnień administratora i schemat `app`. Brak obu parametrów konta nie
blokuje bazy, ale nie tworzy konta aplikacji. Ustawienie tylko jednego lub
wybór konta administratora powoduje błąd inicjalizacji.

Przy istniejącym wolumenie, po uzupełnieniu obu plików, utwórz brakujące
konto i schemat bez usuwania danych:

```sh
docker compose up -d --build app-db
docker compose exec app-db /docker-entrypoint-initdb.d/10-app-role.sh
docker compose up -d --build --force-recreate application-api
```

Skrypt nie zmienia hasła istniejącej roli ani właściciela istniejącego
schematu. Jeśli konto lub schemat istnieją z innymi ustawieniami, administrator
musi je uzgodnić przed startem; nie należy kasować wolumenu. Zmiana pliku
`.env` wymaga odtworzenia kontenera, aby nowe wartości trafiły do środowiska.

Backend wykonuje przygotowane migracje raz podczas startu, pod transakcyjną
blokadą PostgreSQL (klucz `1395733556`, limit oczekiwania 5 s). Pierwsza
rewizja tworzy wyłącznie `app.alembic_version`. Błąd migracji zachowuje
tryb diagnostyczny; po naprawie wymagany jest restart backendu. Jeśli przy
pierwszym starcie baza nie zdąży się uruchomić, po jej gotowości uruchom
`docker compose restart application-api`. `/health/database` sprawdza
połączenie i wersję schematu bez migracji. Po udanym starcie sam wykryje
utratę i powrót bazy; nie gwarantuje sukcesu następnego zapytania.

Ręczny odbiór: uruchom Compose, sprawdź `curl http://127.0.0.1:8000/health/database`
i oczekuj `ready` oraz `applied`. Wykonaj `docker compose restart application-api`
i sprawdź ponownie ten raport. Następnie zatrzymaj `app-db`, sprawdź raport
`unavailable`, przywróć bazę i ponów kontrolę: po udanym starcie backendu
powinien wrócić `ready`. Po błędzie migracji usuń jego przyczynę i zrestartuj
backend. Endpointy `/health/live` i `/health/config` pozostają dostępne.

Test izolowanej bazy (wymaga Docker):

```sh
RUN_DATABASE_TESTS=1 uv run --locked --project services/application-api pytest services/application-api/tests/test_database.py -q
```

Test tworzy własne kontenery PostgreSQL i usuwa je po zakończeniu. Rewizje
wymuszające błąd lub tworzące tabelę istnieją tylko w kopii testowej.

## Szkielet deweloperski S1-T1

Repozytorium zawiera początkowe szkielety trzech serwisów i frontendu. Nie są one jeszcze gotową aplikacją. Do uruchomienia potrzebne są Python 3.14, uv oraz Node.js 26 i npm. Sprawdzono Python 3.14.6, uv 0.11.1, Node.js 26.13.0 i npm 11.20.0. Wersje bibliotek znajdują się w deklaracjach i plikach blokad poszczególnych projektów.

Z katalogu głównego repozytorium zainstaluj zależności i wykonaj testy każdego backendu:

```sh
uv sync --project services/application-api --python 3.14
uv sync --project services/generation-service --python 3.14
uv sync --project services/validation-service --python 3.14
uv run --project services/application-api pytest services/application-api/tests
uv run --project services/generation-service pytest services/generation-service/tests
uv run --project services/validation-service pytest services/validation-service/tests
```

Uruchom każdy serwis w osobnym terminalu:

```sh
uv run --project services/application-api uvicorn application_api.bootstrap:app --app-dir services/application-api/src --host 127.0.0.1 --port 8000
uv run --project services/generation-service uvicorn generation_service.bootstrap:app --app-dir services/generation-service/src --host 127.0.0.1 --port 8001
uv run --project services/validation-service uvicorn validation_service.bootstrap:app --app-dir services/validation-service/src --host 127.0.0.1 --port 8002
```

W kolejnym terminalu uruchom frontend:

```sh
npm ci --prefix apps/web
npm run build --prefix apps/web
npm run dev --prefix apps/web
```

Otwórz `http://127.0.0.1:5173/`. Każdy backend pod `/health/live` zwraca `{"status":"ok"}`; ten adres na porcie 5173 przechodzi przez proxy do `application-api`. Nieistniejący `/api/v1/nieznany` zwraca 404 jako JSON, a nieistniejąca strona i plik — 404. Procesy zatrzymuje się przez Ctrl+C. Endpoint potwierdza działanie procesu, a nie gotowość funkcji biznesowych.

## Konfiguracja backendów

Każdy backend ma własny plik `.env` w `services/<nazwa-serwisu>`. Skopiuj
znajdujący się tam `.env.example` do `.env` i wypełnij wymagane pola. Pliki
`.env` nie są wersjonowane. Nie umieszczaj prawdziwych sekretów w przykładach.

`application-api` wymaga `APP_DB_HOST`, `APP_DB_PORT`, `APP_DB_NAME`,
`APP_DB_USER`, `APP_DB_PASSWORD`, `GENERATION_SERVICE_URL`,
`VALIDATION_SERVICE_URL`, `ARTIFACT_PROJECT_ROOT` i `ARTIFACT_WORKING_ROOT`.
Port bazy to liczba od 1 do 65535. Adresy usług są
bazowymi adresami HTTP lub HTTPS, bez poświadczeń i dodatkowej ścieżki.
Generator i walidator nie wymagają jeszcze parametrów konfiguracji.

Zmienne przekazane procesowi mają pierwszeństwo przed `.env`, również gdy są
puste. Zmiana konfiguracji wymaga restartu danego backendu. `GET /health/config`
pokazuje wynik sprawdzenia konfiguracji i blokowane obszary, bez jej wartości.
Status `valid` nie potwierdza dostępności bazy ani usług. `GET /health/live`
potwierdza jedynie działanie procesu.

Aby ręcznie sprawdzić diagnostykę, uruchom serwisy poleceniami z sekcji
„Szkielet deweloperski S1-T1” i otwórz `http://127.0.0.1:8000/health/config`.
Przy pustym `.env` raport wskaże brakujące pola. Uzupełnij `.env` i uruchom
`application-api` ponownie: przy poprawnych wartościach status zmieni się na
`valid`. Zmień pole w pliku podczas działania procesu i odczytaj raport przed
restartem oraz po nim, aby sprawdzić, kiedy zmiana jest stosowana.

### Lokalny magazyn artefaktów S1-T5

API przechowuje bajty w dwóch oddzielnych katalogach: `project` dla oryginałów
DDL i `working` dla plików roboczych. Referencja zawiera nazwę przestrzeni
i UUID, a nie ścieżkę. Aktualny kontrakt wczytuje cały plik do pamięci.
Nie definiuje limitu uploadu ani czasu przechowywania plików roboczych.

Compose ustawia ścieżki i montuje dwa osobne nazwane wolumeny tylko w API.
Zwykłe odtworzenie kontenera zachowuje ich zawartość; `docker compose down --volumes` usuwa także dane wolumenów. Na hoście przygotuj dwa rozłączne
katalogi, do których użytkownik uruchamiający API może czytać i pisać:

```sh
mkdir -p "$PWD/.local-artifacts/project" "$PWD/.local-artifacts/working"
```

Ustaw ich bezwzględne ścieżki w `services/application-api/.env` jako
`ARTIFACT_PROJECT_ROOT` i `ARTIFACT_WORKING_ROOT`. Katalogi muszą istnieć,
nie mogą być dowiązaniami symbolicznymi ani zawierać się wzajemnie. Zmiana
konfiguracji wymaga restartu API. Compose nadpisuje te wartości swoimi
ścieżkami wewnątrz kontenera.

Odbiór diagnostyki: przy uruchomionym API wywołaj
`curl --fail http://127.0.0.1:8000/health/artifacts`. Poprawne katalogi
dają `ready` dla obu przestrzeni. Na hoście zatrzymaj API, zmień nazwę
jednego pustego katalogu i uruchom API ponownie: raport wskaże `missing_root`,
a `/health/live` nadal zadziała. Przywróć katalog; następne wywołanie
diagnostyki powinno zwrócić `ready` bez restartu. Nie wykonuj tej próby na
katalogach zawierających potrzebne dane.

Testy adaptera i API oraz izolowanego Compose uruchom poleceniami:

```sh
uv run --locked --project services/application-api pytest services/application-api/tests -q
RUN_COMPOSE_TESTS=1 uv run --locked --project services/application-api pytest tests/integration/test_compose.py -q
```

Test Compose tworzy i usuwa własny projekt i wolumeny.
