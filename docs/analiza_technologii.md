# Wstępna analiza technologii i narzędzi

**Data:** 21 października 2026.

**Status:** rekomendacja robocza, nie zatwierdzony stos ani lista zależności do instalacji.

**Podstawa:** [specyfikacja MVP](specyfikacja_mvp.md), [architektura ogólna](architektura.md), [podział implementacji](podzial_implementacji.md) i [przygotowanie do hostowania](przygotowanie_do_hostowania.md).

**Dalszy zapis ustaleń:** kierunki adaptera LLM i magazynu kontekstu utrwalono w [rejestrze architektonicznym](ustalenia_architektoniczne.md). Na bazie wariantu A przygotowano [szczegółowy opis serwisów i technologii](serwisy_i_technologie.md). Nie jest to potwierdzenie zgodności wersji ani zamknięcie wszystkich decyzji implementacyjnych.

## 1. Wniosek i poziom pewności

Wstępny faworyt to **Python + FastAPI po stronie backendu, generowania i walidacji oraz TypeScript + React po stronie interfejsu**. Proponowany zestaw zaplecza to PostgreSQL, SQLAlchemy, Alembic i Psycopg, a lokalnego uruchomienia — Compose. Przy modelach lokalnych rozpatrujemy Ollamę jako podłączane środowisko, nie obowiązkowy element wszystkich prób.

Najsilniejszą alternatywą jest **TypeScript + NestJS + React**. Nie należy jej odrzucać na podstawie założenia, że integracje LLM lub parser PostgreSQL istnieją wyłącznie dla Pythona: dokumentacja Ollamy opisuje klientów dla obu języków, a parser PostgreSQL jest dostępny także dla Node.js [S4, S12].

Trzeci wariant to **Python + Django + szablony HTML i HTMX**. Jest istotnym kandydatem, jeśli najważniejsze okaże się ograniczenie własnego kodu interfejsu i liczby osobno składanych mechanizmów aplikacji.

**Pewność: umiarkowana.** Sprawdzono dokumentację źródłową, ale nie wykonano instalacji, prototypu, benchmarków, audytu zależności ani pomiaru zużycia pamięci. Nie znamy jeszcze doświadczenia autora w samodzielnej weryfikacji kodu poszczególnych języków. Ta informacja może zmienić ranking.

Nie podajemy pozornie precyzyjnych punktów, prognoz godzin lub kosztów utrzymania bez danych. „Najlepszy” oznacza tutaj najlepiej dopasowany do wymagań i kosztu weryfikacji, nie najszybszy w ogólnym benchmarku.

## 2. Kryteria i warunki niepodlegające negocjacji

Priorytety oceny:

1. Łatwość zrozumienia, przetestowania i samodzielnego zrecenzowania kodu.
2. Wymienne integracje, bez uzależnienia całej aplikacji od wybranego dostawcy.
3. Kontrola rzeczywistych wiadomości, wywołań, timeoutów i braku technicznego retry.
4. Wiarygodna walidacja PostgreSQL bez cichej poprawy wygenerowanych danych.
5. Niewielki koszt lokalnego uruchomienia i późniejszej obsługi.
6. Droga do hostowania, tożsamości użytkowników i współbieżnych zadań.

Każdy wariant musi zachować gotowy SQL/CSV przygotowywany przez model, domyślny globalny limit 3 rund poprawek, zatrzymanie po błędzie technicznym, brak wznawiania, historię i rozdzielenie własności danych.

Wybór narzędzi nie zatwierdza automatycznie proponowanego podziału procesów, metody potwierdzania importowalności ani obsługi całego dialektu PostgreSQL.

## 3. Porównanie kompletnych wariantów

| Obszar | A: FastAPI + React | B: NestJS + React | C: Django + HTMX |
| --- | --- | --- | --- |
| Główne języki własnego kodu | Python i TypeScript | TypeScript | Głównie Python, HTML i niewielkie zachowania w przeglądarce |
| Podejście do backendu | API i osobne kontrakty; dobieramy zapis, migracje i pozostałe mechanizmy | Moduły, kontrolery, wstrzykiwanie zależności i kontrakty w ekosystemie Node | Więcej mechanizmów aplikacyjnych w jednym frameworku |
| Interfejs | Osobna aplikacja React, z gotową biblioteką komponentów | Taki sam wariant interfejsu jak A | HTML renderowany na serwerze i fragmenty aktualizowane przez HTMX |
| Własny kod integracyjny | Łączenie backendu i UI przez API; klient może wynikać z OpenAPI | Jeden język nie usuwa potrzeby kontraktów i walidacji w czasie wykonania | Mniej granic JSON w UI, ale API usług nadal wymaga kontraktów |
| Eksperymenty modelowe | Korzystne, jeśli autor chce pracować z narzędziami i analizą w Pythonie | Pełnoprawny wybór, jeśli autor lepiej zna TypeScript | Ten sam język eksperymentów co A; główne API nie musi być FastAPI |
| Przygotowanie do kont | Podłączenie wybranego rozwiązania później | Podłączenie wybranego rozwiązania później | Framework ma gotowe mechanizmy tożsamości; nie musimy ich udostępniać w MVP |
| Główne ryzyko w naszym projekcie | Dwa języki i więcej składanych zależności | Dodatkowe struktury i konfiguracja; wygoda zależy od znajomości NestJS | Silniejsze związanie interfejsu z backendem oraz dyscyplina wydzielenia przypadków użycia |
| Kiedy wybrać | API i wymienne procesy są ważniejsze niż maksymalnie gotowy szkielet całej aplikacji | Najważniejsza jest dobra znajomość jednego języka i narzędzi Node | Priorytetem jest prosty interfejs formularzowy i duży zakres gotowego zaplecza |

### A. Python + FastAPI

FastAPI opiera kontrakty na typach Pythona i Pydantic oraz generuje opis OpenAPI. Dokumentacja wskazuje możliwość generowania klientów na jego podstawie [S1]. To pasuje do naszych granic usług i interfejsu.

Moja rekomendacja dla tego projektu: ten sam język w zarządzaniu, generowaniu i walidacji, a dostawcy modeli za niewielkimi adapterami. Nie jest to teza, że Python automatycznie daje lepsze dane lub że jego serwer HTTP przyspieszy odpowiedź modelu.

Kosztem jest konieczność dobrania i utrzymywania dodatkowych elementów. Sam FastAPI nie rozwiązuje historii, migracji, autoryzacji do projektów ani cyklu zadań.

### B. TypeScript + NestJS

NestJS dokumentuje moduły, kontrolery, dostawców zależności, walidację oraz integrację OpenAPI [S2]. Proponowany wariant używałby jednego języka w backendzie i React. Szczegółowy wybór warstwy zapisu i walidacji kontraktów wymagałby osobnej próby, zamiast automatycznego dokładania kilku konkurencyjnych bibliotek.

To może być lepszy wybór od A, jeżeli autor samodzielnie i pewnie recenzuje TypeScript, a Python byłby nowym językiem. Nie ma obecnie wymagania, które wyklucza ten wariant.

Nie proponujemy mieszaniny NestJS do zarządzania i Pythona do wszystkich operacji LLM tylko na podstawie skojarzenia „AI = Python”. Dodatkowy język powinien wynikać z konkretnej potrzebnej biblioteki lub eksperymentu.

### C. Python + Django + HTMX

Django dostarcza ORM, migracje, szablony i panel administracyjny; ma też gotowy system uwierzytelniania [S3]. HTMX pozwala aktualizować fragmenty strony odpowiedziami HTML i wspiera odpytywanie o stan [S5].

Dla formularzy projektu, zatwierdzania zlecenia, historii i pobierania wyników ten wariant zasługuje na porównanie. Nie wymaga osobnej aplikacji React. Hosting i wielu użytkowników nie są argumentem samym w sobie przeciw temu podejściu.

Oddzielne generowanie i walidacja nadal pozostają możliwe; nie należy umieszczać całego procesu w widoku HTTP. Koszt pojawi się przy potrzebie znacznie bardziej rozbudowanego interfejsu klienckiego lub gdy szczególnie ważne będzie niezależne rozwijanie UI.

## 4. Proponowane komponenty wariantu A

| Warstwa | Proponowany kandydat | Uzasadnienie i warunek |
| --- | --- | --- |
| API zarządzające | FastAPI + Pydantic | Kontrakty i OpenAPI; logika przypadków użycia poza funkcjami obsługi HTTP. |
| Generowanie i walidacja | Python; FastAPI na granicach HTTP, jeśli potwierdzimy osobne usługi | Wspólny język, ale oddzielne odpowiedzialności i adaptery. |
| Interfejs | React + TypeScript + Vite | Osobna aplikacja interfejsu. Vite zapewnia uruchomienie deweloperskie i budowę zasobów statycznych [S6]. |
| Gotowe UI | Mantine | Kandydat do ograniczenia własnych komponentów; dokumentuje integrację z Vite i TypeScript [S7]. |
| Stan zapytań UI | TanStack Query, jeśli korzyść uzasadni zależność | Odczyt statusu i danych; kontrola retry oraz brak automatycznego ponawiania komend uruchomienia. |
| API między częściami | HTTP + OpenAPI | Proponujemy tę granicę zamiast wprowadzania od razu gRPC lub brokera. |
| Trwałe dane aplikacji | PostgreSQL | Projekty, migawki, wykonania i indeks artefaktów. Rekomendacja do zatwierdzenia, nie skutek samego dialektu wyników. |
| Zapis i migracje | SQLAlchemy + Alembic | Gotowa warstwa dostępu i migracje dla schematu aplikacji [S8]. |
| Kontakt walidatora z PostgreSQL | Psycopg | Sterownik i operacje importu, bez dynamicznego tworzenia modeli ORM dla każdego DDL [S9]. |
| Parser DDL i SQL | SQLGlot albo pglast za portem parsera | Wybór warunkowy po próbie zgodności i sprawdzeniu licencji; nie zatwierdzamy jeszcze jednego z nich. |
| Modele lokalne | Ollama uruchamiana osobno | Kandydat na środowisko udostępniające model; nie wybór modelu ani gwarancja jego jakości. |
| Płatne modele | Klienci wybranych dostawców za naszymi adapterami | Zapis wiadomości i metryk, jawne możliwości oraz brak technicznego retry i fallbacku. |
| Biblioteka wielu dostawców | LiteLLM Python SDK — preferowany kandydat do próby | Doprecyzowana rekomendacja w sekcji 8.1; warunkiem są testy śladu wywołań, braku ponowień i przegląd konkretnej wersji. |
| Agentowy wariant badawczy | LangGraph — opcjonalnie | Za kontraktem generowania, nie jako źródło prawdy o wykonaniu i jego sukcesie. |
| Artefakty | Lokalny adapter plików i metadane w bazie | Referencje logiczne; nie dokładamy magazynu obiektowego wyłącznie na zapas. |
| Lokalne uruchomienie | Compose | Powtarzalny opis uruchomienia usług i baz; nie jest decyzją o przyszłym klastrze [S16]. |
| Narzędzia pracy | uv; Ruff i mypy; pytest; Playwright | Zarządzanie Pythonem i zależnościami, kontrola kodu, testy backendu i pełnego przebiegu w przeglądarce [S20]. |

Biblioteki aplikacji nie powinny przenikać do kontraktów domenowych. SQLAlchemy i Alembic dotyczą **naszych tabel aplikacyjnych**, nie generowania schematów użytkownika ani poprawiania wyniku modelu.

### Co rzeczywiście będzie wymienne

To wymaganie architektoniczne, a nie gotowa właściwość FastAPI lub mikroserwisów. Proponujemy porty modelu, walidacji i magazynu danych oraz testy kontraktowe dla każdej ich implementacji:

- **Adapter modelu** przyjmuje jawne wiadomości i ustawienia, a zwraca gotowy artefakt, dostępne metryki albo sklasyfikowany błąd. Nie zakładamy, że wszyscy dostawcy obsługują te same opcje; różnice możliwości muszą być jawne.
- **Adapter walidacji** przyjmuje artefakt, migawkę schematu i zatwierdzone reguły, a zwraca ujednolicony raport z wykonanymi i pominiętymi sprawdzeniami. Nie eksportuje do innych części własnych obiektów parsera.
- **Adapter magazynu aplikacji** realizuje operacje na projektach, wykonaniach i historii bez ujawniania modeli ORM. Wymiana silnika nadal wymaga migracji istniejących danych i sprawdzenia semantyki transakcji.

Cel to ograniczenie zmian do odpowiedniego adaptera i konfiguracji, **nie obietnica braku testów integracyjnych całej aplikacji**. Zmiana znaczenia raportu, zakresu obsługiwanych typów czy możliwości modelu może wymagać świadomej zmiany kontraktu.

Wymiana bazy przechowującej historię aplikacji to także inna decyzja niż dodanie nowego docelowego dialektu danych. Przejście z generowania dla PostgreSQL na inny silnik dotknie co najmniej obsługi DDL, walidacji i profilu eksportu — nie tylko repozytorium.

## 5. Frontend: React czy coś prostszego

Proponuję React, jeżeli chcemy oddzielny frontend z gotowymi komponentami i traktujemy API jako stałą granicę produktu. Nie wynika z tego, że React jest niezbędny do późniejszego hostowania.

Vite jest narzędziem budowania, nie kompletnym frameworkiem aplikacji. Dokumentacja React ostrzega, że start od samego narzędzia budowania wymaga dobrania m.in. routingu i pobierania danych [S6]. W analizowanym wariancie nie pozostawiamy tych problemów własnemu „mini-frameworkowi”: dobieramy gotowe rozwiązania i sprawdzamy ich liczbę względem prostszego Django + HTMX.

Nie rekomenduję obecnie Next.js jako dodatkowej warstwy domyślnej: nie ustaliliśmy wymagań korzystających z jego mechanizmów serwerowych. Nie oznacza to, że Next.js wymaga Vercela lub zawsze osobnego serwera; dokumentuje także eksport statyczny i samodzielny hosting [S21].

Proponowany odczyt statusu to proste odpytywanie, bez obowiązkowego WebSocket. Awaria odczytu statusu w UI nie dowodzi awarii zadania i nie może powodować jego ponownego uruchomienia.

## 6. Walidacja: ważniejsza próba niż ranking frameworków

Rekomendowany do sprawdzenia układ:

1. Parser SQL lub odczyt CSV sprawdza format i zakres dozwolonych konstrukcji.
2. Próbny import gotowych artefaktów do izolowanego PostgreSQL potwierdza typy i obsługiwane ograniczenia. Osobne sprawdzenia porównują rzeczywiste tabele i liczebności z planem.
3. Zatwierdzone dodatkowe reguły są sprawdzane przez kontrolowane operacje, np. zapytania zwracające naruszenia, jeśli taka postać reguł zostanie przyjęta.

PostgreSQL egzekwuje zadeklarowane ograniczenia, natomiast `COPY` ma parametry formatu CSV, wartości pustych i obsługi błędów [S10]. Nie wolno uzyskać sukcesu przez pomijanie błędnych wierszy. Sam udany import nie dowodzi kompletności planu ani spełnienia dodatkowych reguł.

Potrzebne są **odrębne środowiska danych aplikacji i walidacji**, bez wspólnych uprawnień do historii. Rekomendujemy ograniczone role i konstrukcje SQL, limity czasu i zasobów oraz brak dostępu do danych hosta i innych zleceń. Nie dajemy aplikacji ogólnego dostępu do gniazda administracyjnego kontenerów. Sam kontener nie jest pełnym dowodem bezpieczeństwa.

Model zwraca gotowy wynik. W tym układzie nie używamy parsera do przepisywania go ani Pydantic do cichego konwertowania danych kandydata. Pydantic może domyślnie konwertować typy i udostępnia tryb ścisły [S15]; to narzędzie kontraktów aplikacji, nie zamiennik semantyki PostgreSQL.

Próbny import pozostaje rekomendacją do rozstrzygnięcia w OD-02. Kolejność etapów jest już ustalona, ale nie wybiera automatycznie konkretnego parsera, silnika lub sposobu reprezentacji reguł biznesowych.

## 7. Parser: istotne ryzyko licencyjne i zgodności

| Kandydat | Co wynika ze źródła | Wniosek dla projektu |
| --- | --- | --- |
| SQLGlot | Parser i narzędzia analizy wielu dialektów, kod w Pythonie; repozytorium wskazuje MIT [S11]. | Pierwszy kandydat do próby zadeklarowanego podzbioru DDL. Akceptacja przez parser nie jest dowodem poprawności na rzeczywistym PostgreSQL. |
| pglast | Udostępnia drzewo parsera PostgreSQL przez libpg_query. Dokumentacja deklaruje GPL v3 lub późniejszą i powiązania wersji parsera z wydaniami PostgreSQL [S13]. | Technicznie interesujący, ale nie zatwierdzamy go przed przeglądem warunków użycia i zgodności konkretnej wersji. |
| pgsql-parser dla Node.js | Repozytorium opisuje parser AST PostgreSQL i wskazuje MIT [S12]. | Rzeczywista alternatywa dla wariantu TypeScript; sam parser nie wymusza wyboru Pythona. |

To identyfikacja deklaracji licencji, nie opinia prawna o dystrybucji aplikacji. Wydzielenie biblioteki do osobnej usługi nie zastępuje przeglądu licencyjnego. Każdy kandydat wymaga dopasowania obsługiwanego dialektu i testów na naszych schematach.

## 8. Modele i frameworki agentowe

Ollama udostępnia API i klientów Pythona oraz JavaScript [S4]. Proponujemy ją jako pierwszy kandydat do modeli lokalnych, a nie jako warstwę ukrywającą wszystkich płatnych dostawców.

Na macOS rekomendujemy rozpatrzenie natywnego uruchomienia Ollamy obok kontenerów aplikacji. Dokumentacja Ollamy wskazuje brak akceleracji GPU w Docker Desktop na macOS [S14]. Trzeba też potwierdzić pamięć i możliwości faktycznego sprzętu badawczego; wcześniejsze notatki nie są benchmarkiem.

LiteLLM dokumentuje retry i fallbacki [S17]. Nie jest przez to wykluczone, ale ich wyłączenie i wierność zapisywanych wiadomości są warunkami dopuszczenia. Bezpośrednie SDK dostawców za naszymi adapterami pozostają punktem odniesienia i rozwiązaniem zastępczym, jeśli wspólna biblioteka nie spełni kontraktu.

LangGraph dokumentuje checkpointy, wznowienia i polityki retry [S18]. Nie potrzebujemy tych mechanizmów jako infrastruktury całej aplikacji. Możemy użyć biblioteki do badanego grafu ról, jeśli zachowa nasz limit poprawek i zasady błędów. Nie jest prawdą, że korzystanie z niej automatycznie wymusza wznowienia — liczy się wybrana konfiguracja.

Nie wybieramy jeszcze konkretnych modeli. Kontekst i długość odpowiedzi wymagają osobnego sprawdzenia: gotowy SQL/CSV dla wielu tabel nie musi zmieścić się w pojedynczej odpowiedzi. Podział generowania na wywołania pozostaje częścią jawnego wariantu, a nie zwiększeniem limitu rund czy przyzwoleniem na ciche skracanie wyniku.

### 8.1. Doprecyzowanie rekomendacji adaptera LLM

Po dodatkowym przeglądzie dokumentacji rekomendujemy **własny port `LlmClient` i implementację `LiteLlmAdapter`, korzystającą z LiteLLM Python SDK wewnątrz usługi generowania**. To preferowany kandydat do próby, nie zatwierdzona zależność. Nie uruchamiamy osobnego LiteLLM Proxy/Gateway na potrzeby MVP. SDK jest biblioteką w procesie i udostępnia wspólne wywołania, odpowiedzi oraz mapowanie błędów; obsługuje też Ollamę, w tym ścieżkę `ollama_chat` [S25, S26].

Własna warstwa ma obejmować kontrakt żądania i wyniku, jawne możliwości modelu, konfigurację połączenia, mapowanie błędów i rejestr prób. Nie implementujemy ponownie komunikacji HTTP ani specyfiki każdego API. Klasy LiteLLM nie wychodzą poza adapter. Jeśli potrzebna funkcja dostawcy lub wierność historii nie przejdzie testów, podłączymy bezpośredni adapter danego SDK pod ten sam port, bez zmiany logiki generowania.

Warunki przyjęcia:

- Brak technicznych retry we wszystkich warstwach. Dokumentacja rozróżnia `num_retries` LiteLLM i `max_retries` klienta dostawcy; konfigurację bezpośrednich wywołań SDK musimy sprawdzić dla przypiętej wersji, a liczbę faktycznych żądań potwierdzić testem. Nie włączamy fallbacków, cache odpowiedzi ani automatycznego skracania kontekstu [S17, S27].
- Rejestrujemy rzeczywiste treści żądań po mapowaniu do dostawcy i odpowiedzi oraz ustawienia, identyfikatory i dostępne pomiary. Same dane przed wywołaniem wspólnej biblioteki nie dowodzą wierności śladu. LiteLLM dokumentuje callbacki i mechanizm raw request/response; ich kompletność dla wybranych dostawców jest przedmiotem próby. Zapisujemy tylko dozwolone pola, bez nagłówków uwierzytelniania i kluczy; nie uruchamiamy zewnętrznego eksportu logów [S28].
- Nie włączamy cichego odrzucania nieobsługiwanych parametrów (`drop_params`). Różnice możliwości dostawców są jawne. Brak metryki nie jest zerem, a szacowany koszt nie jest rozliczeniem dostawcy [S29].
- Ucięta odpowiedź nie staje się sukcesem przez sam fakt odpowiedzi HTTP. Zachowujemy informację o zakończeniu i przekazujemy artefakt do ustalonych etapów walidacji. Adapter nie poprawia SQL/CSV i nie steruje rundami poprawek [S30].
- Timeout i anulowanie są testowane wraz ze spóźnioną odpowiedzią. Konfiguracja i dane jednego wykonania nie mogą wyciekać do następnego. Dokumentacja SDK ostrzega o globalnych ustawieniach procesu i braku bezpieczeństwa wątkowego; nie zmieniamy globalnych kluczy ani callbacków per wykonanie [S25].

**Istotne ryzyko zależności:** według komunikatu zespołu LiteLLM z 24 marca 2026, aktualizowanego w kolejnych dniach, pakiety PyPI `1.82.7` i `1.82.8` zostały skompromitowane w incydencie łańcucha dostaw. Nie instalujemy tych wersji. Przed przyjęciem wybierzemy konkretną wersję po sprawdzeniu aktualnych ostrzeżeń, pochodzenia i zależności, z plikiem blokad i hashami. Komunikat historyczny nie stanowi gwarancji bezpieczeństwa późniejszych wydań; sam tryb SDK nie usuwa ryzyka instalacyjnego [S31].

Próba nie wymaga płatnego wywołania: najpierw sprawdzamy kontrolowany endpoint testowy i odpowiedzi błędów. Wykorzystanie rzeczywistego modelu pozostaje oddzielnym krokiem.

## 9. Długie zadania: bez dużej platformy, ale nie bez kontroli

Nie rekomendujemy zakładania od razu Celery z dodatkowym brokerem ani platformy trwałych workflow. Z drugiej strony nie traktujemy `BackgroundTasks` jako kompletnego rozwiązania zadań: dokumentacja FastAPI opisuje wykonanie w procesie i rozróżnia je od narzędzi pracy w innych procesach [S19].

Do próby są dwie realizacje przyjętego kontraktu:

- jawny pojedynczy wykonawca z kontrolą anulowania i trwałym stanem w aplikacji, jeśli taka realizacja okaże się mała i wystarczająca;
- gotowy wykonawca zadań, jeżeli ograniczy własny kod i przejdzie testy braku retry, wznowienia oraz obsługi anulowania.

Kandydatem do drugiej próby jest **Procrastinate**, działający w oparciu o PostgreSQL. Dokumentuje strategie retry, anulowanie i osobny mechanizm ponawiania zadań pozostawionych po utracie workera [S22]. Nie zatwierdzamy go bez prototypu. Nie używamy ręcznego retry biblioteki do kontynuowania starego wykonania: nasz przycisk tworzy nowe.

Wybór takiego narzędzia dodaje zależność infrastruktury pracy od PostgreSQL. Nie wolno udawać, że zmiana magazynu aplikacji automatycznie usunie także tę zależność. Jeżeli zadania używają technicznego schematu kolejki, dostęp workerów do niego nie oznacza dostępu do wewnętrznych tabel projektów i historii.

W każdym wariancie restart nie odtwarza wykonywania starego zadania. Pozostawiony status jest uzgadniany z faktem utraty procesu, a historia pozostaje do odczytu.

## 10. Przechowywanie i lokalne uruchomienie

Dla danych aplikacji proponujemy PostgreSQL zamiast dodawania SQLite wyłącznie dlatego, że MVP jest lokalne. Jest to ocena projektu: i tak rozpatrujemy PostgreSQL do walidacji, a zależy nam na podobnym zachowaniu zapisu lokalnie i później na serwerze.

SQLite nie jest z definicji niezdolne do obsługi witryn lub wielu użytkowników. Jego dokumentacja opisuje zastosowania lokalne i webowe oraz ograniczenia współbieżnego zapisu [S23]. Może być rozsądną alternatywą, jeśli priorytetem będzie minimalna instalacja. Koszt późniejszej migracji i dwóch zestawów testów trzeba wtedy przyjąć jawnie.

Rekomendacja PostgreSQL oznacza osobny magazyn aplikacji i osobne, izolowane środowisko prób importu, nawet jeśli korzystają z tej samej rodziny silnika. Nie proponujemy jednego konta administracyjnego dla obu.

Compose opisuje konfigurację wielokontenerowej aplikacji i wspiera lokalne uruchomienie oraz wdrożenia na pojedynczym hoście [S16]. Nie oznacza automatycznego skalowania ani bezpiecznego publicznego wdrożenia. Wersje obrazów i zależności należy przypiąć po próbie zgodności, zamiast używać ruchomego `latest`.

### 10.1. Schematy i kontekst: baza relacyjna oraz opcjonalne wyszukiwanie wektorowe

Rekomendujemy **PostgreSQL jako trwałe źródło schematów, a pgvector jako opcjonalną warstwę wyszukiwania**, nie zamianę dokładnych definicji na same embeddingi. pgvector jest rozszerzeniem PostgreSQL: można przechowywać wektory obok pozostałych danych bez osobnego serwera bazy wektorowej [S32]. Nie zatwierdzamy teraz rozszerzenia, modelu embeddingowego ani RAG jako obowiązkowego elementu MVP.

Proponowany zapis obejmuje:

- oryginalny plik DDL jako niezmienny artefakt oraz jego identyfikator lub hash;
- wersję schematu powiązaną z projektem i migawką wykonania;
- wynik analizy obsługiwanego DDL: tabele, kolumny, typy, ograniczenia i zatwierdzone relacje — jako model strukturalny, np. w `jsonb` lub tabelach aplikacji;
- opcjonalnie fragmenty opisów tabel i reguł, ich embeddingi oraz odniesienia do dokładnej wersji źródła.

PostgreSQL obsługuje dokumenty `jsonb` i ich indeksowanie. Taki dokument nie jest kopią oryginalnego tekstu zachowującą całe formatowanie, dlatego nie zastępuje przechowania oryginalnego DDL [S33].

Przygotowanie kontekstu proponujemy ukryć za portem `ContextProvider`. Pierwsza implementacja pobiera całą potrzebną definicję, jeśli mieści się w budżecie modelu, albo wybiera obiekty na podstawie zatwierdzonego zakresu i jawnych zależności. Dla dużych schematów można porównać ją z wariantem hybrydowym: wyszukiwanie po identyfikatorach i nazwach, podobieństwo semantyczne opisów, następnie uzupełnienie obowiązkowych zależności i reguł z modelu strukturalnego. Dokumentacja LlamaIndex pokazuje rozróżnienie całego kontekstu schematu i wyszukiwania tabel przy zbyt dużym schemacie w zastosowaniu Text-to-SQL; to przykład mechanizmu, nie dowód jego skuteczności dla naszego generatora [S34].

Nie zakładamy, że najbliższe semantycznie fragmenty stanowią kompletny schemat. Nawet dokładne wyszukiwanie sąsiadów nie jest sprawdzeniem kompletności zależności, a przybliżone indeksy pgvector dodatkowo wymieniają część recall na szybkość [S32]. Przykładowo tabela potrzebna jako cel klucza obcego może nie wejść do pierwszych trafień. Dlatego identyfikację wymaganych zależności opieramy na DDL i zatwierdzonych uzupełnieniach, nie wyłącznie na rankingu embeddingów. Nowa potrzeba rozszerzenia generowanego zakresu wraca do zatwierdzenia, zamiast zmieniać zakres już uruchomionego wykonania.

Jeśli wprowadzimy embeddingi:

- użyjemy oddzielnego portu `EmbeddingClient`; model generujący SQL/CSV i model embeddingowy pełnią inne role;
- zwiążemy indeks z wersją źródła, identyfikatorem modelu embeddingowego i sposobem podziału tekstu; zmiana tych elementów może wymagać przebudowy indeksu;
- zapytania ograniczymy do uprawnionego projektu i właściwej wersji, z przygotowaniem do przyszłego rozdzielenia właścicieli;
- nie wyślemy schematów do zewnętrznego dostawcy embeddingów bez świadomej zgody na taki transfer;
- zachowamy fragmenty rzeczywiście użyte w kontekście i ustawienia selekcji przy wykonaniu.

Embeddings wymagają ich wytworzenia przez odpowiedni model, nie powstają automatycznie przez zapis w pgvector. Przykładowo Ollama udostępnia operację embed i zaleca ten sam model przy indeksowaniu i wyszukiwaniu [S35]. Ostateczna treść potrzebnych fragmentów nadal musi trafić do kontekstu wywołania; wektor nie zastępuje definicji tabel w promptach.

Decyzję o dodaniu wyszukiwania wektorowego poprzedzimy pomiarem rozmiaru rzeczywistych schematów, budżetu kontekstu i kompletności wybranych informacji. Nie wyznaczamy progu wyłącznie liczbą tabel ani liczbą generowanych rekordów. Na razie preferujemy prostą implementację `ContextProvider`, zachowując możliwość jej wymiany.

## 11. Koszt weryfikacji, utrzymanie i bezpieczeństwo

| Rodzaj kosztu | A: FastAPI + React | B: NestJS + React | C: Django + HTMX |
| --- | --- | --- | --- |
| Nauka i code review | Korzystne przy znajomości Pythona i TypeScript; nieznajomość jednego z nich zwiększa koszt | Korzystne przy dobrej znajomości TypeScript | Korzystne przy znajomości Pythona i modelu serwerowych formularzy |
| Składanie mechanizmów | Więcej decyzji o warstwie zapisu, interfejsie i integracjach | Więcej wspólnej struktury Nest, ale nadal dobór zapisu i bibliotek UI | Więcej funkcji we frameworku; mniej osobnej infrastruktury interfejsu |
| Utrzymanie kontraktów | Python–TypeScript przez OpenAPI i testy | Wspólny język pomaga, lecz kontrakty sieciowe nadal podlegają wersjonowaniu | Mniej kontraktów UI JSON, ale kontrakty usług i formularzy pozostają |
| Uruchomienie i modele | Wspólne koszty zależne głównie od przyjętej topologii i badań | Te same kategorie kosztów | Te same koszty walidacji i modeli; możliwie prostsze dostarczanie UI |

Nie wyliczamy 5-letniego TCO w pieniądzu bez planu użytkowania i hostingu. Trzeba uwzględnić pobranie i pamięć modeli, wywołania API, przestrzeń na historię, testy, aktualizacje, migracje i obsługę narzędzi uruchomieniowych.

Nie wykonano audytu CVE ani pełnego audytu licencji. Po wybraniu wersji potrzebne są pliki blokad zależności, sprawdzenie podatności i licencji oraz regularne aktualizacje. Brak konkretnej znalezionej podatności w tej analizie nie jest potwierdzeniem bezpieczeństwa.

Wymagamy testu kontrolującego retry nie tylko w SDK modeli: TanStack Query dokumentuje domyślne ponawianie zapytań i możliwość jego wyłączenia [S24]. Żadne zachowanie UI, klienta HTTP czy biblioteki agentowej nie może powtórnie uruchomić zadania lub ukryć błędu technicznego.

## 12. Próby przed zatwierdzeniem stosu

Nie tworzymy jeszcze pełnej aplikacji. Proponujemy niewielkie, ograniczone próby:

1. **Parser i DDL:** kilka reprezentatywnych schematów, jawne ograniczenia, nieobsługiwane konstrukcje, zgodność wersji i przegląd licencji.
2. **Rzeczywista walidacja:** gotowy SQL i CSV; osobno błąd składni, typu, klucza obcego, liczebności i reguły biznesowej. Sprawdzamy dokładną dostarczaną zawartość bez jej naprawiania.
3. **Wywołania modeli:** lokalny i wybrany płatny adapter; faktyczne wiadomości, brakujące metryki, timeout i dowód braku drugiego wywołania po błędzie.
4. **Cykl wykonania:** start, odczyt statusu, anulowanie, spóźniona odpowiedź, utrata procesu i ręczne nowe wykonanie. Sprawdzamy zachowanie wcześniejszego użytecznego kandydata.
5. **Minimalny UI:** wgranie pliku, zatwierdzenie planu i start/stop/status. Ocena ilości własnego kodu i zrozumiałości w porównaniu z prostszym interfejsem.
6. **Lokalne uruchomienie:** czas i zasoby mierzone na rzeczywistym komputerze, połączenie aplikacji z modelem natywnym, brak niepotrzebnej ekspozycji portów.

Nie wykonujemy płatnych wywołań, pobrań modeli ani instalacji w ramach samej analizy.

## 13. Kolejna decyzja

Przed zatwierdzeniem rekomendacji trzeba ustalić, w których językach i frameworkach autor potrafi samodzielnie recenzować kod. Wybieramy potem jeden wariant główny i wykonujemy próby o najwyższym ryzyku, zamiast rozwijać równolegle trzy aplikacje.

Wstępne uporządkowanie:

- **A — faworyt do dalszej weryfikacji**, jeżeli Python jest akceptowalnym językiem backendu.
- **B — równorzędny kandydat przy wyraźnej przewadze znajomości TypeScript.**
- **C — kandydat do ograniczenia kodu aplikacyjnego i frontendowego**, jeśli prosty model interakcji wystarczy.

Rekomendacja nie zamyka OD-01, OD-02, OD-03 ani sposobu wykonywania reguł. Nie zmienia też zatwierdzonego zachowania aplikacji.

Do dalszego szczegółowego projektowania rozpisano wariant A. Aktualny status kierunków, warunków i otwartych punktów znajduje się w [rejestrze ustaleń](ustalenia_architektoniczne.md), a zakres poszczególnych komponentów w [serwisach i technologiach](serwisy_i_technologie.md). Samo przygotowanie tego projektu nie zastępuje prób technicznych.

## 14. Źródła pierwotne

Sprawdzone 21 października 2026. Dokumentacje niektórych projektów pokazują różne wersje na różnych podstronach. Nie utożsamiamy ich nagłówków z zatwierdzoną kombinacją zależności ani nie twierdzimy, że wskazane strony opisują zawsze najnowsze wydanie.

| ID | Dokumentacja |
| --- | --- |
| S1 | FastAPI Features: `https://fastapi.tiangolo.com/features/` |
| S2 | NestJS: `https://docs.nestjs.com/`; walidacja: `https://docs.nestjs.com/application/validation`; OpenAPI: `https://docs.nestjs.com/openapi/introduction` |
| S3 | Django Overview: `https://docs.djangoproject.com/en/6.0/intro/overview/`; Authentication: `https://docs.djangoproject.com/en/6.0/topics/auth/default/` |
| S4 | Ollama API: `https://docs.ollama.com/api/introduction` |
| S5 | HTMX: `https://htmx.org/docs/` |
| S6 | Vite: `https://vite.dev/guide/`; React: `https://react.dev/learn/build-a-react-app-from-scratch` |
| S7 | Mantine: `https://mantine.dev/getting-started/` |
| S8 | SQLAlchemy: `https://docs.sqlalchemy.org/en/20/intro.html`; Alembic: `https://alembic.sqlalchemy.org/en/latest/` |
| S9 | Psycopg: `https://www.psycopg.org/psycopg3/docs/` |
| S10 | PostgreSQL Constraints: `https://www.postgresql.org/docs/18/ddl-constraints.html`; COPY: `https://www.postgresql.org/docs/18/sql-copy.html`; limity zapytań: `https://www.postgresql.org/docs/18/runtime-config-client.html` |
| S11 | SQLGlot: `https://github.com/tobymao/sqlglot` |
| S12 | pgsql-parser: `https://github.com/constructive-io/pgsql-parser` |
| S13 | pglast: `https://pglast.readthedocs.io/en/latest/`; projekt: `https://github.com/lelit/pglast` |
| S14 | Ollama FAQ: `https://docs.ollama.com/faq` |
| S15 | Pydantic Strict Mode: `https://docs.pydantic.dev/latest/concepts/strict_mode/` |
| S16 | Docker Compose: `https://docs.docker.com/compose/intro/features-uses/` |
| S17 | LiteLLM Retry/Fallback: `https://docs.litellm.ai/docs/completion/reliable_completions` |
| S18 | LangGraph Persistence: `https://docs.langchain.com/oss/python/langgraph/persistence`; retry: `https://reference.langchain.com/python/langgraph/types/RetryPolicy` |
| S19 | FastAPI Background Tasks: `https://fastapi.tiangolo.com/tutorial/background-tasks/` |
| S20 | uv: `https://docs.astral.sh/uv/`; Ruff: `https://docs.astral.sh/ruff/`; mypy: `https://mypy.readthedocs.io/en/stable/`; pytest: `https://docs.pytest.org/en/stable/`; Playwright: `https://playwright.dev/docs/intro` |
| S21 | Next.js Deploying: `https://nextjs.org/docs/app/getting-started/deploying` |
| S22 | Procrastinate: retry `https://procrastinate.readthedocs.io/en/stable/howto/advanced/retry.html`; anulowanie `https://procrastinate.readthedocs.io/en/stable/howto/advanced/cancellation.html`; utrata workera `https://procrastinate.readthedocs.io/en/stable/howto/production/retry_stalled_jobs.html` |
| S23 | SQLite Appropriate Uses: `https://www.sqlite.org/whentouse.html` |
| S24 | TanStack Query Retries: `https://tanstack.com/query/latest/docs/framework/react/guides/query-retries` |
| S25 | LiteLLM Python SDK, tryb biblioteczny, async i ustawienia globalne: `https://docs.litellm.ai/docs/python_sdk` |
| S26 | LiteLLM Ollama i ścieżka chat: `https://docs.litellm.ai/docs/providers/ollama` |
| S27 | LiteLLM Router, rozróżnienie retry biblioteki i SDK dostawcy: `https://docs.litellm.ai/docs/routing` |
| S28 | LiteLLM Custom Callbacks: `https://docs.litellm.ai/docs/observability/custom_callback`; Raw Request/Response Logging: `https://docs.litellm.ai/docs/observability/raw_request_response` |
| S29 | LiteLLM Input Params, zachowanie dla nieobsługiwanych parametrów: `https://docs.litellm.ai/docs/completion/input` |
| S30 | LiteLLM Output, treść, usage i finish reason: `https://docs.litellm.ai/docs/completion/output` |
| S31 | LiteLLM Security Update, incydent z 24 marca 2026 i późniejsze aktualizacje: `https://docs.litellm.ai/blog/security-update-march-2026`; podsumowanie zespołu: `https://docs.litellm.ai/blog/security-townhall-updates` |
| S32 | pgvector, przechowywanie, wyszukiwanie dokładne i przybliżone oraz filtrowanie: `https://github.com/pgvector/pgvector` |
| S33 | PostgreSQL JSON Types, `jsonb` i różnice względem dokładnego tekstu: `https://www.postgresql.org/docs/18/datatype-json.html` |
| S34 | LlamaIndex Text-to-SQL Guide, dobór schematów do kontekstu: `https://developers.llamaindex.ai/python/examples/index_structs/struct_indices/sqlindexdemo/` |
| S35 | Ollama Embeddings, wytwarzanie wektorów i spójność modelu: `https://docs.ollama.com/capabilities/embeddings` |
