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
T1 ma pełny opis do przeglądu; T2–T9 pozostają szkicami z jawnymi
blokadami przed implementacją. Zadań nie opublikowano na GitHubie.

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

## Kontrole pull requestów

Po otwarciu PR i kolejnych commitach GitHub Actions uruchamia testy pytest
każdego backendu oraz sprawdzanie typów i build frontendu. Instalacja korzysta
z plików blokad. Ręczne uruchomienie jest dostępne w zakładce Actions.

Kontrole bezpieczeństwa obejmują zależności Python (`pip-audit`) i npm
(`npm audit`), sekrety w commitach PR (Gitleaks) oraz analizę kodu Python
i JavaScript/TypeScript (CodeQL). Każda znana podatność Python i podatności
npm o poziomie high lub critical powodują błąd kontroli. Gitleaks ukrywa
znalezione wartości w wynikach. CodeQL publikuje osobną kontrolę GitHub
„Code scanning results”; jej domyślne progi obejmują high, critical i error.
Szczegóły wyników znajdują się w Checks oraz w zakładce Security.

Do lokalnej kontroli backendów użyj poleceń pytest powyżej; zgodność blokad
można sprawdzić przez `uv sync --locked --project services/<nazwa-serwisu>`.
Dla frontendu wykonaj `npm ci --prefix apps/web`, `npm run build --prefix apps/web`
i `npm audit --prefix apps/web --audit-level=high`. Audyty wymagają dostępu
do publicznych baz podatności. Wykrycia należy przeanalizować; workflow
nie zmienia zależności automatycznie. Zestaw kontroli nie potwierdza jeszcze
pełnego przepływu aplikacji ani bezpieczeństwa wykonywania SQL.
