# Plan realizacji MVP — story i stan planowania

**Stan implementacji S1-T1 — 15 listopada 2026:** utworzono szkielety
frontendowe i backendowe. Testy endpointów, build oraz lokalne sprawdzenie
proxy i odpowiedzi 404 przeszły; ekran i proxy sprawdzono w przeglądarce.
Zmiana oczekuje na ręczny odbiór użytkownika. Szczegóły uruchomienia
zawiera [README](../README.md#szkielet-deweloperski-s1-t1). Zapisy poniżej
o braku kodu i planowanych testach opisują punkt wyjścia.


Dokument zawiera uzgodniony podział aplikacji na obszary pracy oraz punkt
kontynuacji planowania. Obecnie jest jedynym miejscem zapisu backlogu:
planu story, przyszłych zadań i podzadań. Publikację na GitHubie odłożono.
Wymagania produktu nadal określa [specyfikacja MVP](specyfikacja_mvp.md).

Po osobnym zleceniu przeniesiemy uzgodnione opisy do GitHub Issues i Projects,
zachowując identyfikatory i hierarchię. Wtedy ustalimy przełączenie miejsca
prowadzenia planu; nie będziemy utrzymywać dwóch niezależnych backlogów.

**Aktualizacja:** 14 listopada 2026.

## 1. Uzgodniony stan

- Użytkownik zaakceptował obraz całego MVP i mapę story S1–S9.
- Story oznacza nadrzędny obszar pracy, nie mikroserwis ani pojedynczy ekran.
- Uzgodniono podział S1 na zadania S1-T1–S1-T9. Przygotowano opis T1
  do przeglądu oraz szkice T2–T9 z jawnymi blokadami. Nowe opisy wymagają
  akceptacji; nie są informacją o rozpoczęciu implementacji.
- Uzgodniono podział S3 na zadania S3-T1–S3-T5. W sesji dotyczącej S3
  przygotowano szkice wszystkich pięciu opisów z jawnymi blokadami.
  Szczegółowe instrukcje i ewentualne podzadania nie są jeszcze
  zaakceptowane ani gotowe do implementacji.
- Użytkownik wybrał S1 i zlecił przygotowanie opisów jego zadań.
  Zatwierdzono stos, trzy serwisy backendowe, Docker Compose i komunikację
  HTTP + JSON + OpenAPI. Użytkownik zaakceptował podział na S1-T1–S1-T9,
  bez zatwierdzania otwartych rozwiązań szczegółowych.
- Następnie użytkownik zlecił przygotowanie opisów zadań S2.
  Zaakceptował podział S2-T1–S2-T6. W rozmowie dotyczącej S2
  przygotowano szkice wszystkich sześciu opisów, z krokami, granicami,
  zależnościami, kryteriami i planowanymi sprawdzeniami.
  Brakujące kontrakty i decyzje są blokadami przed implementacją,
  nie uzgodnionymi rozwiązaniami ani poleceniem ich wyboru przez juniora.
  Akceptacja podziału nie rozstrzyga otwartych decyzji S1 ani S2.
- Akceptacja mapy nie zatwierdza propozycji technologicznych i otwartych decyzji.
- Najnowsze polecenie użytkownika: na razie zapisujemy plan lokalnie,
  a publikację całej uzgodnionej partii na GitHubie wykonamy później.
  Zastępuje to wcześniejsze zlecenie natychmiastowej publikacji S1–S9.
- Zachowany cel późniejszej publikacji: GitHub Project
  „Generator danych — MVP” na koncie `jwieczor03`, issues w repozytorium
  `jwieczor03/mgr-llm-data-generator`. Przed zapisem trzeba ponownie
  sprawdzić aktualny stan i dostęp.
- Repozytorium jest publiczne; poinformowano o tym użytkownika przed zgodą
  na publikację.
- Nie zlecono zamykania ani zmieniania wcześniejszych issues #1–#6.

## 2. Mapa zaakceptowanych obszarów

Wszystkie poniższe story mają status **uzgodnione na poziomie obszaru**.
Dla S1 zaakceptowano podział na zadania S1-T1–S1-T9,
dla S2 — S2-T1–S2-T6, a dla S3 — S3-T1–S3-T5.
Ich szczegółowe instrukcje i podzadania nie zostały jeszcze zaakceptowane.
Numeracja nie ustala priorytetów ani kolejności realizacji.

| ID | Story | Status publikacji |
| --- | --- | --- |
| S1 | Fundament aplikacji i lokalne uruchomienie | Nieopublikowane |
| S2 | Zapisane projekty i rozpoznawanie schematu | Nieopublikowane |
| S3 | Reguły biznesowe i ich zatwierdzanie | Nieopublikowane |
| S4 | Czat i przygotowanie zatwierdzonego zlecenia | Nieopublikowane |
| S5 | Integracja modeli i przygotowywanie paczek danych | Nieopublikowane |
| S6 | Sterowanie wykonaniem, naprawy i przerwania | Nieopublikowane |
| S7 | Walidacja paczki i rzeczywisty próbny import | Nieopublikowane |
| S8 | Wynik, raport i pobieranie plików | Nieopublikowane |
| S9 | Cykl życia czatu i danych roboczych | Nieopublikowane |

Hierarchia planu: `S1 → S1-T1 → S1-T1-P1`. Uzgodniono dzieci S1-T1–S1-T9;
nie utworzono podzadań ani relacji na GitHubie. Do pierwszej szczegółowej analizy użytkownik
wybrał S1; kolejności pozostałych story nie ustalono.

### S1 — Fundament aplikacji i lokalne uruchomienie

**Cel i rezultat:** aplikację można uruchomić lokalnie, a jej części mają
uzgodnione granice odpowiedzialności.

**Zakres:** struktura rozwiązania, konfiguracja, podłączenie magazynów,
granice integracji i kontekst lokalnego właściciela. Wspólne narzędzia
testowania oraz ochrona sekretów. Przygotowanie granic przyszłego
hostowania bez wdrażania tej funkcji.

**Poza zakresem:** logowanie, publiczny hosting, wielu użytkowników
i infrastruktura do skalowania.

**Źródła:** REQ-001–REQ-002, REQ-057, REQ-066–REQ-067; sekcja 13
specyfikacji i rejestr ustaleń architektonicznych.

**Powiązania:** wspólne przygotowanie środowiska dla pozostałych story
wykonujemy tutaj, bez jego powielania w każdym obszarze. Testy zachowania
konkretnej funkcji należą do jej zadania.

**Uzgodnione:** Python/FastAPI na backendzie i React/TypeScript
na frontendzie jako stos do implementacji MVP. Trzy osobno uruchamiane
serwisy backendowe: zarządzanie, generowanie i walidacja. Docker Compose
jako podstawowy sposób lokalnego uruchamiania backendów i potrzebnych baz.
Komunikacja między serwisami przez HTTP z danymi JSON i opisem API w OpenAPI.
Frontend: React + TypeScript + Vite, z npm do zarządzania pakietami
i uruchamiania poleceń.
Zależności i środowiska backendów Python: uv, z osobnym projektem,
deklaracjami zależności, plikiem blokady wersji i środowiskiem wirtualnym
dla każdego z trzech backendów, bez wspólnego workspace.
Bazowa linia Pythona dla wszystkich backendów: 3.14. Dokładne wydanie
poprawkowe wymaga przeglądu i próby zgodności zależności.
Serwer uruchamiający każdą z trzech aplikacji FastAPI: Uvicorn.
Narzędzie testów automatycznych wszystkich trzech backendów: pytest;
wersja, dodatkowe biblioteki i wtyczki pozostają otwarte.
Bazowa linia środowiska narzędziowego frontendu: Node.js 26 LTS;
dokładne wersje Node.js, npm i bibliotek pozostają do przypięcia
i sprawdzenia zgodności.
Podczas zwykłego lokalnego korzystania `application-api` udostępnia
zbudowany frontend i API pod jednym adresem. Osobny serwer Vite jest
przeznaczony wyłącznie do pracy deweloperskiej.

**Do wyjaśnienia:** szczegóły lokalnego uruchomienia i kontraktów usług,
pozostałe biblioteki oraz wersje. Szczegółowe propozycje architektury nie są
automatycznie instrukcjami implementacji.

#### Uzgodniony podział S1 na zadania

**Status:** użytkownik zaakceptował podział 14 listopada 2026.
Następnie zatwierdził wydzielenie niezależnego monitora i panelu jako
S1-T9. Identyfikatory S1-T1–S1-T8 pozostają bez zmian.
Poniższa lista określa uzgodnione zadania, ale nie stanowi jeszcze instrukcji
implementacji ani akceptacji wskazanych otwartych rozwiązań szczegółowych.
Nie utworzono podzadań. Poniżej tabeli zapisano opisy do przeglądu:
T1 ma pełny opis uzgodnionego szkieletu, T2–T9 pozostają szkicami
z blokadami. Każdy opis obejmuje sprawdzenie własnej zmiany; wspólna
konfiguracja narzędzi powstanie tylko raz. Kroki nie są osobnymi issues.

| ID | Uzgodnione zadanie | Oczekiwany rezultat i granice |
| --- | --- | --- |
| S1-T1 | Utworzyć szkielety frontendu i trzech serwisów backendowych | Podstawa React/TypeScript z Vite i npm na Node.js 26 LTS oraz osobne aplikacje FastAPI na Pythonie 3.14, uruchamiane przez Uvicorn. Każdy backend ma osobny projekt uv. Bez ekranów funkcjonalnych, integracji LLM i walidacji danych. Uzgodniono jeden wspólny układ repozytorium z frontendem w `apps/web/` i backendami w `services/application-api/`, `services/generation-service/`, `services/validation-service/`; katalogi są do utworzenia. Zatwierdzono minimalną strukturę backendów, kontrakt `/health/live`, ekran techniczny, adresy deweloperskie, proxy Vite i minimalny routing. Dokładne wersje dobierze deweloper po przeglądzie i próbie zgodności, bez zmiany uzgodnionego stosu. Pełny opis poniżej przygotowano do przeglądu i akceptacji. |
| S1-T2 | Przygotować konfigurację i ochronę sekretów | Oddzielenie adresów, poświadczeń i parametrów środowiska od logiki. Każdy backend ma własny lokalny `.env` poza Git i wersjonowany `.env.example` z opisem wymaganych zmiennych, bez prawdziwych sekretów. Odczyt i walidacja przez zatwierdzone Pydantic Settings przy starcie; zmiana konfiguracji wymaga restartu serwisu. Zmienne środowiskowe procesu lub kontenera mają pierwszeństwo przed `.env`. Braki konfiguracji zgłasza tryb diagnostyczny, blokując zależne operacje. Katalog parametrów i raport konfiguracji uzgodniono dla S1-T2; próby zależności należą do T9. |
| S1-T3 | Przygotować lokalne uruchomienie backendów i baz w Docker Compose | Dostarczono obrazy trzech backendów, frontend podawany przez API, Compose z bazą, lokalną konfiguracją, dwiema sieciami i trwałym wolumenem. Testy dostarczonego zakresu przeszły. Integracje T4/T5/T9 i odbiór w przeglądarce pozostają otwarte; szczegóły w opisie T3. Bez publicznego hostingu i rozstrzygania OD-02. |
| S1-T4 | Podłączyć bazę aplikacji i przygotować mechanizm migracji | Techniczna podstawa połączenia i kontrolowanej aktualizacji struktury PostgreSQL aplikacji w `application-api`, przez zatwierdzone SQLAlchemy i Psycopg oraz migracje Alembic, uruchamiane automatycznie wyłącznie w fazie startu tego serwisu. Błąd migracji pozostawia tryb diagnostyczny z przyczyną i blokadą funkcji wymagających bazy; ponowienie wymaga restartu. Bez tabel projektów, schematów i wykonań z dalszych story; bez nadawania generatorowi i walidatorowi dostępu do tej bazy. Migracje nie należą do health checków. Dokładne wersje i zgodność wymagają sprawdzenia; ochrona przed równoczesnym wykonaniem, tryb połączeń i transakcji pozostają do uzgodnienia. |
| S1-T5 | Przygotować granicę magazynu plików i lokalny adapter | Oddzielenie logiki od fizycznego katalogu plików. Zaimplementowano lokalny adapter i diagnostykę zgodnie z decyzją architekta w procesie #20; review i odbiór ręczny pozostają osobnymi etapami. Bez eksportu, API pobierania, metadanych kandydatów oraz cyklu życia i sprzątania czatu z S8–S9. |
| S1-T6 | Przygotować lokalny kontekst właściciela i granicę kontroli dostępu | Zaimplementowano wymienne źródło kontekstu i politykę własności bez logowania, zgodnie z decyzją architekta w procesie #21; review i odbiór pozostają osobnymi etapami. Podłączenie rzeczywistych zasobów należy do ich story. Bez kont, tokenów logowania i obsługi wielu użytkowników. |
| S1-T7 | Skonfigurować wspólne narzędzia kontroli jakości i testów | Zaimplementowano powtarzalne kontrole i testy zgodnie z decyzją architekta dla #22; review i odbiór ręczny pozostają osobnymi etapami. |
| S1-T8 | Sprawdzić uruchomienie całości w przeglądarce i opisać obsługę środowiska | Sprawdzony start, minimalne połączenie frontendu z API i instrukcja uruchomienia, zatrzymania oraz diagnostyki. Bez czatu i przepływu generowania. Zatwierdzono podawanie gotowego frontendu przez `application-api`, z osobnym Vite wyłącznie do developmentu. Kontrakt kontroli i szczegóły uruchomienia opisano w zadaniu oraz rejestrze decyzji. |
| S1-T9 | Przygotować niezależny monitor serwisów i panel diagnostyczny | Osobny proces monitora i panel w przeglądarce, niezależne od działania `application-api`. Kontrole przy uruchomieniu i co 30 minut oraz bezpłatna, niedestrukcyjna akcja „Sprawdź teraz”, bez wpływu na harmonogram. Raporty pokazują uzgodnione stany, przyczyny i ograniczenia bez sekretów. Zakres zaakceptowany; kontrakty, technologia, zabezpieczenia i obsługa jednoczesnych kontroli wymagają doprecyzowania. |

**Proponowana kolejność:** S1-T1 → S1-T7 → S1-T2, następnie
S1-T4 i uzgodnione części S1-T5–S1-T6, potem S1-T3 i S1-T8.
Konfiguracja Compose i adaptery będą wymagały wspólnego sprawdzenia
połączeń; ten porządek nie oznacza zakazu korzystania z bazy testowej
przed ukończeniem całego S1-T3.
Po dodaniu S1-T9 proponujemy jego integrację z uruchomieniem przed
końcowym sprawdzeniem środowiska w S1-T8. To uzupełnienie proponowanej
kolejności, nie osobna zaakceptowana decyzja o realizacji.

**Pokrycie:** REQ-001–REQ-002 i REQ-067 obejmują szkielety, uruchomienie
i sprawdzenie w przeglądarce (T1, T3, T8). REQ-057 obejmuje podstawę
ochrony sekretów (T2); funkcje dalszych story muszą zachować tę ochronę.
REQ-066 obejmuje granice komponentów, konfiguracji, magazynów i dostępu
(T1–T6). Stan i wykonawca zadań pozostają w S6, a ich cykl życia w S9.
AC-28 wymaga późniejszego przeglądu także tych obszarów; sam S1 nie
potwierdza zgodności całej aplikacji. T7 dostarcza wspólne narzędzia.
AC-29 sprawdzamy w T8, a AC-23 uzupełniamy testami rzeczywistych raportów,
diagnostyki i wyników w zadaniach odpowiednich story.
Sekcję 13.5 specyfikacji w zakresie niezależnego monitorowania i panelu
obejmuje S1-T9. S1-T8 sprawdza uruchomienie i instrukcję całego środowiska,
ale nie powiela implementacji monitora ani jego testów funkcjonalnych.

#### S1 — Pakiet zadań do przekazania deweloperowi

Pakiet zbiera dziewięć opisów w jednym miejscu. Linki prowadzą
do właściwych zadań poniżej, nie do drugiego backlogu.
Przygotowanie opisu nie oznacza zlecenia implementacji ani publikacji.
T1 jest opisany do przeglądu; T2–T9 mają jawne decyzje blokujące
przekazanie pełnego zakresu do implementacji.

| Opis zadania | Zależności wykonawcze | Co pozostaje przed implementacją |
| --- | --- | --- |
| [S1-T1 — Szkielety aplikacji](#s1-t1--utworzyć-szkielety-frontendu-i-trzech-serwisów-backendowych) | Brak wcześniejszych zadań | Przegląd opisu; dobór dokładnych wersji i próba zgodności są częścią zadania, w uzgodnionych granicach. |
| [S1-T2 — Konfiguracja i sekrety](#s1-t2--przygotować-konfigurację-i-ochronę-sekretów) | T1 | Katalog parametrów, walidacja, bezpieczne błędy i wspólny z T9 kontrakt diagnostyki. |
| [S1-T3 — Lokalne uruchomienie](#s1-t3--przygotować-lokalne-uruchomienie-backendów-i-baz-w-docker-compose) | T1/T2 wykorzystane; dalsze integracje T4/T5/T9 | Podstawowy zakres zaimplementowany i sprawdzony przez HTTP. Otwarte: integracje T4/T5/T9 i ręczny odbiór w przeglądarce. |
| [S1-T4 — Baza i migracje](#s1-t4--podłączyć-bazę-aplikacji-i-przygotować-mechanizm-migracji) | T1, T2; kontrakt diagnostyki i środowisko PostgreSQL do testów | Ochrona równoczesnych migracji, połączenia, transakcje, uprawnienia i testy mechanizmu. |
| [S1-T5 — Granica magazynu plików](#s1-t5--przygotować-granicę-magazynu-plików-i-lokalny-adapter) | T1, T2 | Adapter, konfigurację i diagnostykę zaimplementowano; review i odbiór ręczny pozostają do wykonania. |
| [S1-T6 — Kontekst właściciela i dostęp](#s1-t6--przygotować-lokalny-kontekst-właściciela-i-granicę-kontroli-dostępu) | T1 | Kontrakt i adapter zaimplementowano; review i odbiór ręczny pozostają do wykonania. |
| [S1-T7 — Narzędzia jakości i testów](#s1-t7--skonfigurować-wspólne-narzędzia-kontroli-jakości-i-testów) | T1 | Implementacja przygotowana; review i odbiór pozostają osobne. |
| [S1-T8 — Sprawdzenie całości i instrukcja](#s1-t8--sprawdzić-uruchomienie-całości-w-przeglądarce-i-opisać-obsługę-środowiska) | Dostarczone zakresy T1–T7 oraz T9 | Domknięcie zależności i minimalny kontrakt sprawdzenia połączenia frontend–API. |
| [S1-T9 — Monitor i panel diagnostyczny](#s1-t9--przygotować-niezależny-monitor-serwisów-i-panel-diagnostyczny) | T1, T2; kontrakt diagnostyki i integracja startu z T3 | Technologia, kontrakty, konkretne próby, zabezpieczenia, limity czasu, świeżość i jednoczesne kontrole. |

**Jak korzystać z pakietu:**
- Każdy opis zawiera cel, źródło, punkt startowy, zakres, wyłączenia,
  zależności, kryteria lub warunki do doprecyzowania oraz plan sprawdzeń.
- Przed rozpoczęciem danego zadania odczytać jego sekcję „Do wyjaśnienia”.
  Wskazane braki rozstrzygać z użytkownikiem, nie pozostawiać juniorowi
  wyboru architektury.
- Uzgodnienie kontraktu diagnostyki jest decyzją potrzebną przed
  implementacją zależnych części T2/T4/T9, nie wymaga wcześniejszego
  ukończenia kodu monitora. Analogicznie integracja T3/T9 nie oznacza,
  że całe oba zadania muszą być ukończone przed rozpoczęciem któregokolwiek.
- Testy każdej zmiany realizować w jej zadaniu. T7 przygotowuje narzędzia,
  a T8 sprawdza integrację i instrukcję; nie zastępują testów T1–T6 i T9.
- Po realizacji deweloper podaje zmienione pliki, rzeczywiste wyniki testów,
  ograniczenia i kroki ręcznego odbioru. Nie oznaczać zadania jako
  wykonanego na podstawie samej dokumentacji.

**Stan przekazania:**
- [x] Zebrano dziewięć opisów pod stabilnymi identyfikatorami.
- [x] Wskazano źródła, zależności, planowane sprawdzenia i otwarte decyzje.
- [ ] Zaakceptowano szczegółowe opisy.
- [ ] Rozstrzygnięto blokady zadań przeznaczonych do implementacji.
- [ ] Zlecono implementację wybranej partii.
- [ ] Osobno zlecono publikację uzgodnionej partii na GitHubie.

**Następny krok:** przegląd i akceptacja poniższych opisów. Nie trzeba
wstrzymywać ich przygotowania do rozstrzygnięcia wszystkich szczegółów.
Przed implementacją zależnych części trzeba jednak rozstrzygnąć wskazane
blokady, pojedynczo. Akceptacja szkicu nie zatwierdza otwartych rozwiązań.

**Wspólne zasady czytania opisów S1:** każde zadanie należy do
S1 — Fundament aplikacji i lokalne uruchomienie. Repozytorium zawiera
dokumentację, bez kodu aplikacji i konfiguracji jej startu. Wskazane
nowe moduły są do utworzenia, a nie istniejącym wzorcem. Wszystkie
poniższe testy i kroki odbioru są planowane, nie wykonane. Nie podajemy
niezweryfikowanych komend jako działających. Deweloper zapisze rzeczywiste
komendy i wyniki wraz z realizacją danej zmiany. Ręczny odbiór należy
do użytkownika. Szczegółowe propozycje LLD nie stają się wymaganiami
przez samo odwołanie do dokumentu.

#### S1-T1 — Utworzyć szkielety frontendu i trzech serwisów backendowych

**Status:** opis do przeglądu i akceptacji, oparty na zatwierdzonych
decyzjach. Bez podzadań i publikacji.

**Cel:** deweloper może osobno uruchomić frontend i każdy backend
bez infrastruktury danych i dostawców LLM.

**Źródło:** REQ-002, REQ-066–REQ-067 i AC-29
[specyfikacji](specyfikacja_mvp.md), decyzje S1 w
[rejestrze ustaleń](ustalenia_architektoniczne.md), sekcja 3
[LLD](lld/README.md) i zatwierdzona część sekcji 1
[kontraktów API](lld/kontrakty_api.md).

**Punkt startowy:** brak `apps/` i `services/`. Utworzyć `apps/web/`
oraz poniższe minimalne pliki backendów:

| Serwis | Utworzenie FastAPI i `/health/live` — do utworzenia | Test pytest — do utworzenia |
| --- | --- | --- |
| application-api | `services/application-api/src/application_api/bootstrap.py` | `services/application-api/tests/test_health.py` |
| generation-service | `services/generation-service/src/generation_service/bootstrap.py` | `services/generation-service/tests/test_health.py` |
| validation-service | `services/validation-service/src/validation_service/bootstrap.py` | `services/validation-service/tests/test_health.py` |

**Zależności:** brak wcześniejszych zadań implementacyjnych. Wybór
dokładnych wersji i próba zgodności są pierwszym krokiem tego zadania.

**Co należy zrobić:**
1. Dobrać i przypiąć dokładne wersje zaakceptowanych narzędzi oraz
   wymaganych zależności po sprawdzeniu dokumentacji i próbie zgodności.
   Zachować Python 3.14 i Node.js 26 LTS. W razie niezgodności wrócić
   do użytkownika, zamiast zmieniać stos lub dodawać opcjonalne narzędzia.
2. Utworzyć trzy niezależne projekty uv, każdy z własną deklaracją
   zależności, plikiem blokady wersji i `.venv`. Nie tworzyć uv workspace
   ani pustych warstw domeny i adapterów.
3. W każdym backendzie utworzyć aplikację FastAPI uruchamianą przez
   Uvicorn. `GET /health/live` zwraca HTTP 200 i dokładny JSON
   `{"status":"ok"}`. Nie sprawdza bazy, plików ani API dostawcy.
4. W `apps/web/` utworzyć React + TypeScript + Vite z npm.
   Ekran techniczny pokazuje nazwę aplikacji i „Szkielet aplikacji”.
   Nie dodawać czatu, formularzy ani udawanych funkcji biznesowych.
5. Przygotować bezpośrednie uruchomienie deweloperskie na `127.0.0.1`:
   `application-api:8000`, `generation-service:8001`,
   `validation-service:8002`, Vite `5173`.
   Te adresy nie ustalają sieci ani portów kontenerów.
6. Zachować rozdział adresów `application-api`: frontend `/`,
   biznesowe API `/api/v1`, techniczny `/health/live`.
   Nieznane `/api/v1/...` zwracają HTTP 404 z JSON-em, nie HTML.
   Nieznane strony i brakujące pliki zwracają 404, bez zastępowania
   ich stroną startową. Nie tworzyć nowych operacji biznesowych.
7. Używać adresów względnych po stronie frontendu. Proxy Vite przekazuje
   `/api/v1` i `/health/live` do `http://127.0.0.1:8000`, bez zmiany ścieżek.
   Nie przekazuje wewnętrznego API i nie łączy przeglądarki bezpośrednio
   z generatorem ani walidatorem.
8. Dodać test kontraktu health checku w każdym wskazanym pliku pytest.
   Zapisać rzeczywiste polecenia uruchomienia i testów oraz dobrane wersje.

**Poza zakresem:** Compose, bazy, migracje, szczegółowa diagnostyka,
LLM, modele danych, biblioteki UI i dodatkowe narzędzia jakości.
Zwykłe uruchomienie ma podawać zbudowany frontend przez `application-api`;
konfiguracja tego połączenia i odbiór całości należą do T3/T8.

**Kryteria ukończenia:**
- Każdy backend daje się uruchomić osobno bez baz, magazynu plików,
  Ollamy i kluczy API; odpowiada zgodnie z kontraktem `/health/live`.
- Frontend działa przez Vite na uzgodnionym adresie i pokazuje tylko
  uzgodniony ekran. Proxy zachowuje ścieżki i podział odpowiedzialności.
- Nieznane API nie zwraca HTML, a brak strony lub pliku nie jest
  maskowany stroną startową. Dostarczono trzy testy kontraktu.
- Zależności są rozdzielone i przypięte; instrukcja odtwarza rzeczywiste
  uruchomienie. Gotowość procesu nie jest opisana jako gotowość biznesowa.

**Jak sprawdzić:** uruchomić każdy backend bez zależności zewnętrznych;
sprawdzić status i treść `/health/live` oraz testy pytest. Otworzyć Vite,
sprawdzić ekran i żądanie `/health/live` przez proxy. Wywołać nieistniejący
adres `/api/v1/...`, stronę i plik; oczekiwać 404, dla API JSON-u.
Sprawdzić konfigurację proxy i adresy żądań w przeglądarce.

**Do wyjaśnienia:** brak dodatkowej decyzji blokującej sam szkielet.
Dokładne wersje i zgodność weryfikuje deweloper w kroku 1.
Ścieżka artefaktu frontendu i sposób podawania go przy zwykłym starcie
pozostają blokadą integracji T3/T8, nie powodem tworzenia ich na zapas w T1.

#### S1-T2 — Przygotować konfigurację i ochronę sekretów

**Status:** implementacja S1-T2 w toku. Katalog konfiguracji i raport HTTP uzgodniono w rozmowie.

**Cel:** każdy backend używa jawnie opisanej konfiguracji, a braki
nie wyłączają diagnostyki ani nie ujawniają sekretów.

**Źródło i punkt startowy:** REQ-057, AC-23 i sekcja 13.5
[specyfikacji](specyfikacja_mvp.md), zatwierdzone decyzje konfiguracji
w [rejestrze](ustalenia_architektoniczne.md). Punktem implementacji
będą szkielety T1. Istniejący `.gitignore` ignoruje `.env`.
W każdym z trzech uzgodnionych katalogów backendów `.env`
i `.env.example` są do utworzenia; pierwszy pozostaje lokalny.

**Zależności:** T1; katalog zmiennych i raport konfiguracji uzgodniono w zakresie S1-T2. Szersza diagnostyka pozostaje w T9.

**Uzgodnione kroki:**
1. Opisać uzgodnione wymagane parametry w `.env.example`, bez prawdziwych
   sekretów. Nie wymagać kluczy nieużywanych dostawców.
2. Odczytywać i walidować konfigurację przez Pydantic Settings
   we wszystkich trzech backendach przy starcie. Zmienne procesu
   lub kontenera mają pierwszeństwo przed `.env`.
3. Zmiany stosować dopiero po restarcie. Diagnostyka opisuje konfigurację
   używaną przez proces, nie nową treść pliku, której nie wczytano.
4. Przy braku lub błędzie konfiguracji utrzymać tryb diagnostyczny
   i zablokować zależne operacje. Nie zastępować sekretów fikcyjnymi
   wartościami. Nie ujawniać ich w błędach, logach i odpowiedziach.

**Poza zakresem:** konfiguracja monitora i frontendu bez osobnych ustaleń,
logowanie użytkowników oraz gwarancja startu HTTP np. przy zajętym porcie.

**Kryteria i planowane sprawdzenia:** dla jednego parametru ustawić
różne wartości w `.env` i środowisku procesu — wygra środowisko.
Zmiana `.env` nie wpływa na działający proces; po restarcie jest odczytana.
Usunięcie wymaganego parametru lub użycie błędnej wartości daje
bezpieczną przyczynę w diagnostyce i blokadę zależnej operacji.
Brak klucza nieużywanego dostawcy nie blokuje używanego zakresu.
Przejrzeć pliki wersjonowane, logi i odpowiedzi pod kątem wycieku sekretów.

**Ustalenie implementacyjne:** `application-api` wymaga pól `APP_DB_HOST`,
`APP_DB_PORT`, `APP_DB_NAME`, `APP_DB_USER`, `APP_DB_PASSWORD`,
`GENERATION_SERVICE_URL` i `VALIDATION_SERVICE_URL`; generator i walidator
nie mają na tym etapie wymaganych pól. Raport `GET /health/config` przedstawia
status walidacji konfiguracji, problemy i blokowane obszary bez jej wartości.
Nie potwierdza dostępności zależności. Szczegółowe sprawdzanie zależności,
agregacja i niezależny monitor należą do T9. Konfigurację LLM, magazynu
i środowiska importu ustalimy przy właściwych integracjach.

#### S1-T3 — Przygotować lokalne uruchomienie backendów i baz w Docker Compose

**Status — 16 listopada 2026:** dostarczono podstawowy zakres T3:
obrazy trzech backendów, frontend podawany przez API, Compose z bazą,
konfiguracją, sieciami i wolumenem. Testy opisano poniżej.
Pełne kryteria integracyjne z T4, magazynami i T9 pozostają otwarte;
T3 nie jest oznaczone jako w całości zakończone. Kontrola w przeglądarce
jest zablokowana brakiem dostępnego narzędzia i uprawnień Computer Use.

**Cel:** uruchomić lokalnie trzy backendy i potrzebne bazy
we wspólnie skonfigurowanym środowisku, bez obowiązkowego AWS.

**Źródło i punkt startowy:** REQ-002, REQ-066–REQ-067
[specyfikacji](specyfikacja_mvp.md) i decyzja Docker Compose
w [rejestrze](ustalenia_architektoniczne.md). Konfiguracja kontenerów
znajduje się w `compose.yaml` w katalogu głównym repozytorium
(decyzja użytkownika z 15 listopada 2026).

**Zależności:** T1, konfiguracja T2, połączenie T4; kontrakty
wykorzystywanych magazynów i integracja monitora T9 po ich uzgodnieniu.

**Uzgodnione kroki:**
1. Przygotować wspólny start backendów i potrzebnych baz przez Compose,
   z połączeniami odpowiadającymi granicom serwisów.
2. Podłączyć konfigurację bez zapisywania prawdziwych sekretów w repo.
   Compose wczytuje konfigurację każdego backendu z jego osobnego,
   lokalnego `.env` w katalogu serwisu (decyzja użytkownika
   z 15 listopada 2026). Pliki nie trafiają do obrazów; parametry
   i walidacja wynikają z T2. Zachować uzgodnione pierwszeństwo
   zmiennych przekazanych przy uruchomieniu kontenera.
   Dla parametrów samego Compose i bazy aplikacji użyć osobnego,
   lokalnego `.env` w katalogu głównym repozytorium, poza Git,
   oraz wersjonowanego `.env.example` bez prawdziwych sekretów
   (kolejna decyzja użytkownika z 15 listopada 2026). Pliki backendów
   pozostają osobne. T2 dostarcza katalog `APP_DB_*` i adresów backendów.
   Główny `.env.example` opisuje `POSTGRES_DB`, `POSTGRES_USER`
   i `POSTGRES_PASSWORD` do inicjalizacji bazy; nie ustala roli aplikacji z T4.
   Nie dawać generatorowi ani walidatorowi dostępu do bazy aplikacji.
3. Uwzględnić zwykłe lokalne użycie frontendu podawanego przez
   `application-api`. Zgodnie z decyzją z 15 listopada 2026 użyć
   wieloetapowego Dockerfile: Node.js buduje frontend, a gotowe pliki
   trafiają do końcowego obrazu backendu i są podawane przez FastAPI.
   Vite pozostaje serwerem wyłącznie w developmencie; w obrazie służy
   do budowania zasobów, nie do ich udostępniania.
4. Uruchamiać monitor z panelem jako osobną usługę w tym samym Docker
   Compose, bez uzależniania panelu od działania `application-api`
   (decyzja użytkownika z 15 listopada 2026). Uwzględnić go w instrukcji.
   Health checki nie mogą uruchamiać migracji.
5. Publikować na hoście wyłącznie port aplikacji (`application-api`
   z frontendem) i port panelu monitora, oba na `127.0.0.1`
   (decyzja użytkownika z 15 listopada 2026). Generator, walidator
   i baza pozostają bez publikowanych portów, dostępne wewnątrz
   uzgodnionych sieci Compose. Nie oznacza to dostępu każdego serwisu
   do wszystkich pozostałych.
   Domyślny adres aplikacji w Compose to `http://127.0.0.1:8000`
   (decyzja użytkownika z 15 listopada 2026). Domyślny adres panelu
   monitora to `http://127.0.0.1:8080` (kolejna decyzja z tej samej daty).
6. Przechowywać dane PostgreSQL aplikacji w nazwanym wolumenie Docker
   (decyzja użytkownika z 15 listopada 2026). Zwykłe zatrzymanie
   i odtworzenie kontenerów zachowuje ten wolumen i dane. Decyzja
   nie dotyczy magazynu plików ani środowiska próbnego importu.
7. Deweloper dobiera i przypina dokładne wersje obrazów po sprawdzeniu
   oficjalnej dokumentacji i próbie zgodności (decyzja użytkownika
   z 15 listopada 2026). Zachowuje Python 3.14 i Node.js 26.
   Upoważnienie obejmuje wersję PostgreSQL bazy aplikacji, ale nie
   środowisko próbnego importu. Konflikt wymagający zmiany ustaleń
   wraca do użytkownika przed zmianą. Wybrane wersje i wyniki sprawdzeń
   zapisano poniżej.
8. Wydzielić sieć bazy aplikacji, do której należą wyłącznie
   `application-api` i PostgreSQL aplikacji (decyzja użytkownika
   z 15 listopada 2026). Generator, walidator i monitor nie są do niej
   podłączone. Monitor odczytuje stan zależności bazy przez diagnostykę
   `application-api`, bez bezpośredniego połączenia z bazą.
9. Utworzyć drugą, wspólną sieć komunikacji HTTP dla `application-api`,
   `generation-service`, `validation-service` i monitora (decyzja
   użytkownika z 15 listopada 2026). Baza aplikacji nie należy do tej
   sieci. Monitor odpytuje każdy backend bez pośrednictwa głównego API.

**Szczegóły pozostawione deweloperowi — decyzja z 15 listopada 2026:**
nazwy sieci i wolumenu, porty wewnętrzne oraz ścieżkę zasobów frontendu
w obrazie dobiera deweloper, zachowując wszystkie zaakceptowane ustalenia.
Dobór wersji obrazów podlega warunkom z punktu 7. Delegacja nie obejmuje
zmiany granic dostępu, kontraktów diagnostyki ani rozstrzygania OD-02.

**Kolejność i stan implementacji:** poniższe etapy opisują realizację
T3, nie są nowymi zadaniami backlogu. Każdy etap kończy się sprawdzeniem
wyniku; wykryte problemy należy rozwiązać przed etapem zależnym.

1. **Obrazy i powtarzalne budowanie — wykonane.** Sprawdzić dokumentację i zgodność
   wersji; przygotować Dockerfile'e backendów i wykluczenia kontekstu
   budowania. Korzystać z istniejących plików blokad zależności.
   Rezultat: obrazy trzech backendów, bez lokalnych `.env` i sekretów.
   Zależność: szkielet T1. Sprawdzenie: build obrazów, testy pytest
   szkieletów i uruchomienie `/health/live` w każdym kontenerze.
2. **Frontend w obrazie głównego API — wykonane, sprawdzone przez HTTP.** Dodać etap budowania frontendu
   i podawanie gotowych zasobów przez FastAPI. Rezultat: frontend i API
   pod wspólnym adresem, bez serwera Vite. Zależność: etap 1.
   Sprawdzenie: build bez lokalnego `dist`, testy integracyjne `/`,
   zasobów, `/health/live` oraz uzgodnionych odpowiedzi 404.
3. **Podstawowa konfiguracja Compose — wykonana infrastruktura.** Złożyć backendy i bazę aplikacji,
   podłączyć dwa uzgodnione rodzaje sieci, publikację portów, wolumen
   i lokalną konfigurację. Rezultat dostarczony w T3: odtwarzalny start,
   dostęp sieciowy API do portu bazy, odczyt konfiguracji, izolacja sieci
   i trwałość danych testowych. Zależności: etapy 1–2 i dostarczony T2.
   Sprawdzono rzeczywisty PostgreSQL przez `psql`; połączenie SQL
   z kodu aplikacji i jego diagnostyka pozostają do integracji po T4.
4. **Start i gotowość — częściowo, dalsza integracja po T4/T9.** Wpiąć mechanizmy diagnostyki i migracji
   dostarczone w T2/T4, bez ich ponownej implementacji w T3.
   Rezultat: niedostępna zależność lub błąd migracji nie wyłącza
   diagnostyki backendu. Zależności: etap 3 i uzgodnione kontrakty
   T2/T4/T9. Sprawdzenie: start z brakującą konfiguracją i niedostępną
   bazą, błąd migracji oraz potwierdzenie, że diagnostyka jej nie ponawia.
5. **Integracja monitora i magazynów — oczekuje na T9/T5.** Włączyć dostarczony monitor
   z panelem do tego samego Compose i podłączyć uzgodnione magazyny.
   Rezultat: panel niezależny od głównego API i rzeczywiste zależności
   zamiast atrap. Zależności: etap 4, T9 oraz wykorzystywany zakres T5.
   Sprawdzenie: panel na porcie 8080 po zatrzymaniu głównego API
   i dalsze odpytywanie generatora oraz walidatora. Funkcjonalne testy
   harmonogramu i diagnostyki należą do T9.
6. **Sprawdzenie środowiska i instrukcja — wykonane dla dostarczonego zakresu.** Uruchomić adekwatną regresję
   pytest, build frontendu i test całego środowiska przez rzeczywiste
   HTTP, z izolowanymi danymi. Nie dodawać narzędzi E2E bez uzgodnienia
   w T7. Rezultat: sprawdzone polecenia w README oraz kroki ręcznego
   odbioru: start, otwarcie aplikacji i panelu, zatrzymanie głównego API,
   ponowny start i zachowanie danych bazy. Zależność: etapy 1–5.
   Końcowe odtworzenie instrukcji i sprawdzenie w przeglądarce pozostaje
   w T8. Przy przekazaniu rozdzielić testy wykonane od niewykonanych.

**Poza zakresem:** publiczny hosting, wdrożenie AWS, wybór modelu LLM
i rozstrzygnięcie izolacji próbnego importu z S7/OD-02.

**Kryteria i planowane sprawdzenia:** odtworzyć start z przygotowanej
konfiguracji i sprawdzić dostępność trzech procesów oraz ich zależności.
Otworzyć frontend pod wspólnym adresem z API bez serwera Vite.
Sprawdzić, że zatrzymanie głównego API nie uniemożliwia odczytu panelu
monitora. Udokumentować faktyczne polecenia startu i zatrzymania.
Samo HTTP 200 z `/health/live` nie zalicza sprawdzenia gotowości.
Sprawdzić również, że tylko aplikacja i panel mają publikowane porty,
oba związane z `127.0.0.1`; generator, walidator i baza nie mają
mapowań portów na hosta.
Zbudować obraz `application-api` bez wcześniejszego lokalnego builda
frontendu i sprawdzić, że zawiera oraz udostępnia gotowe zasoby.
Sprawdzić zachowanie uzgodnionych tras i odpowiedzi 404.
Na izolowanej bazie testowej zapisać dane, zatrzymać i odtworzyć
kontenery bez usuwania wolumenu, a następnie potwierdzić ich zachowanie.
Sprawdzić skład sieci bazy i połączenie `application-api` z PostgreSQL;
generator, walidator i monitor nie mogą łączyć się bezpośrednio z bazą.
Sprawdzić połączenia HTTP we wspólnej sieci oraz możliwość odpytania
generatora i walidatora przez monitor po zatrzymaniu `application-api`.
Sprawdzić odczyt osobnych plików konfiguracji, pierwszeństwo ustawień
przekazanych przy uruchomieniu oraz brak plików `.env` w obrazach.
Nie ujawniać wartości sekretów w wynikach sprawdzeń.

**Otwarte zależności pełnej integracji:** role, połączenie SQL aplikacji
i migracje (T4), diagnostyka gotowości (T4/T9), kontrakty pozostałych
magazynów (T5) oraz obraz, konfiguracja i kontrakty monitora (T9).
Nie rozstrzygać tych kwestii
przez wpisanie domyślnych wartości do Compose. Nazwy sieci i wolumenu,
porty wewnętrzne oraz ścieżka zasobów nie wymagają osobnych decyzji
użytkownika w ramach powyższej delegacji. Nie przenosić portów
deweloperskich T1 do Compose jako domniemanej decyzji.

**Dostarczone artefakty:** `compose.yaml`, `.env.example`, `.dockerignore`,
Dockerfile każdego backendu, podawanie frontendu w `application-api`,
testy `test_frontend.py` i `tests/integration/test_compose.py` oraz
instrukcja i kroki ręcznego odbioru w README. Nie zmieniono UI.

**Przyjęte szczegóły wykonawcze:** sieć `services` łączy trzy backendy;
wewnętrzna sieć `database` łączy tylko API i bazę. Backendy słuchają
w kontenerach na porcie 8000, PostgreSQL na 5432. Na hoście publikowany
jest tylko `127.0.0.1:8000`. Wolumen `app-db-data` jest zamontowany
pod `/var/lib/postgresql`, zgodnie z układem obrazu PostgreSQL 18.
Frontend trafia do `/app/src/application_api/web` w obrazie API.
Monitor i port 8080 zostaną dodane po T9, bez atrapy w obecnym Compose.
Brak `.env` backendu nie blokuje startu. Kontenery backendów nie czekają
na gotowość zależności; ich health check potwierdza wyłącznie liveness.

**Wersje i źródła:** sprawdzono oficjalne materiały
[Python](https://github.com/docker-library/python/blob/master/versions.json),
[Node.js](https://github.com/nodejs/docker-node/blob/main/26/bookworm-slim/Dockerfile),
[PostgreSQL](https://github.com/docker-library/docs/blob/master/postgres/README.md)
i [uv](https://docs.astral.sh/uv/guides/integration/docker/).
Obrazy bazowe: Python 3.14.10 slim-bookworm, Node.js 26.13.1 bookworm-slim,
uv 0.11.1 i PostgreSQL 18.7 bookworm. Nie zmieniano blokad bibliotek.

**Rzeczywiste sprawdzenia:** zbudowano trzy obrazy i frontend w Dockerze;
pytest: API 17/17, generator 2/2, walidator 2/2. Testy Compose na osobnym
projekcie i tymczasowym wolumenie: 6/6. Obejmują działający frontend
i zasoby, HTTP między backendami, izolację bazy, zachowanie danych po
odtworzeniu jej kontenera, działanie API przy niedostępnej bazie i bez
pliku `.env`, pierwszeństwo jawnych ustawień kontenera oraz brak `.env`
w obrazach. Pierwszy test HTTP na hoście zablokował sandbox; pełny zestaw
API przeszedł po uruchomieniu z dostępem do lokalnych portów.
Testy zgłaszają zastane ostrzeżenie o wycofywaniu integracji TestClient
z httpx. Nie zmieniano zależności poza zakresem T3.

**Niesprawdzone:** renderowanie i interakcja w przeglądarce (brak dostępnej
przeglądarki automatyzacji i uprawnień Computer Use), integracje T4/T5/T9,
pełny odbiór T8. Rzeczywiste HTTP nie zastępuje kontroli wyglądu w przeglądarce.
Komendy testów i kroki ręcznej weryfikacji są w README.

#### S1-T4 — Podłączyć bazę aplikacji i przygotować mechanizm migracji

**Status:** realizacja zadania [#19](https://github.com/jwieczor03/mgr-llm-data-generator/issues/19)
w procesie koordynatora; decyzje techniczne podjęte przez architekta
16 listopada 2026. Implementację i testy wykonano; niezależne review
i ręczny odbiór użytkownika pozostają do wykonania.

**Cel:** `application-api` ma fundament połączenia z PostgreSQL
i wersjonowania struktury, zanim powstaną tabele funkcji biznesowych.

**Źródło i punkt startowy:** sekcje 13.5–13.6
[specyfikacji](specyfikacja_mvp.md) i decyzje SQLAlchemy, Psycopg
oraz Alembic w [rejestrze](ustalenia_architektoniczne.md).
Kod powstanie w `services/application-api/` z T1. Szczegóły połączeń, transakcji, uprawnień, blokady i raportu
`/health/database` określa decyzja architekta z 16 listopada 2026
w rejestrze ustaleń. Wykonawca dobierze nazwy plików w tym zakresie.

**Zależności:** T1, konfiguracja T2 i kontrakt diagnostyki.
Do testów potrzebne uzgodnione środowisko PostgreSQL; nie wymaga
to ukończenia całej konfiguracji Compose.

**Uzgodnione kroki:**
1. Przygotować obsługę połączenia przez SQLAlchemy i Psycopg oraz
   mechanizm migracji Alembic wyłącznie dla bazy aplikacji.
2. Automatycznie uruchamiać przygotowane migracje tylko w fazie startu
   procesu `application-api`, również po restarcie.
   Nie projektować zmian tabel automatycznie.
3. Po błędzie migracji utrzymać tryb diagnostyczny z bezpieczną przyczyną
   i zablokować funkcje wymagające bazy.
4. Po naprawie przyczyny ponowić migrację dopiero przy restarcie.
   Nie uruchamiać jej przez health check, kontrolę okresową,
   „Sprawdź teraz” ani samoczynnie w działającym procesie.

**Poza zakresem:** tabele projektów, schematów i wykonań, DDL użytkownika,
próbny import i dostęp innych backendów do bazy aplikacji.
Migracje tabel domenowych należą do ich story.

**Kryteria i planowane sprawdzenia:** w uzgodnionym środowisku testowym
przygotowana migracja jest stosowana przy starcie bez ręcznej komendy.
Wymuszony błąd pozostawia diagnostykę i blokadę funkcji bazy.
Usunięcie przyczyny bez restartu nie ponawia migracji; restart umożliwia
kolejną próbę. Wywołania diagnostyki nie wykonują migracji.
Nie tworzyć tabel testowych w docelowej bazie „na zapas”.

**Ustalenia techniczne do wykonania:** synchroniczne SQLAlchemy/Psycopg,
krótkie sesje operacji, migracje w jednej transakcji z blokadą PostgreSQL
przed inicjalizacją Alembic, osobne konto bez uprawnień administratora
w schemacie `app` oraz pusta rewizja początkowa. Inicjalizacja konta
nie należy do migracji. Obraz serwisu zawiera pliki migracji.
`/health/database` sprawdza połączenie i wersję przez odczyt, bez migracji;
strażnik capability blokuje zależne operacje. Awaria po udanym starcie
może ustąpić bez restartu; nieudany start migracji wymaga restartu.
Pełny kontrakt, limity i uzasadnienia znajdują się w rejestrze.

**Dodatkowe sprawdzenia mechanizmu:** równoległe starty, timeout blokady,
wycofanie nieudanej rewizji, utrata i odzyskanie bazy, strażnik 503,
bezpieczny raport, konto bez uprawnień administratora oraz migracje
w rzeczywistym obrazie. PostgreSQL 18.7 działa w jednorazowym,
izolowanym środowisku testowym, bez lokalnych danych użytkownika.

**Wynik implementacji 16 listopada 2026:** dodano migracje i adapter
w `application-api`, diagnostykę oraz provisioning konta i schematu.
Przypięto SQLAlchemy 2.0.48, Psycopg 3.3.3 i Alembic 1.18.4;
weryfikację wykonano na Pythonie 3.14.6 i PostgreSQL 18.7. Testy
`RUN_DATABASE_TESTS=1 uv run --locked --project services/application-api pytest services/application-api/tests -q`
dały 26 passed (jedno zastane ostrzeżenie Starlette/httpx), a
`RUN_COMPOSE_TESTS=1 uv run --locked --project services/application-api pytest tests/integration/test_compose.py -q -x`
dały 6 passed. Sprawdzono m.in. migracje na osobnych procesach, timeout
blokady, rollback, brak retry, odzyskanie połączenia, uprawnienia,
provisioning i obecność migracji w obrazie. Kontrolowane tabele i rewizje
powstały wyłącznie w izolowanej bazie i kopii migracji. Po review poprawiono
izolację testów frontendu i procesu HTTP: nie korzystają z lokalnej konfiguracji
bazy ani nie uruchamiają migracji. Ponowny pełny zestaw API z izolowanym
PostgreSQL dał 27 passed, jedno istniejące ostrzeżenie; domyślny zestaw
z testowymi wartościami `APP_DB_*` w środowisku dał 18 passed i 9 pominiętych
testów PostgreSQL, które uruchamia się osobno. Instrukcję dla istniejącego
wolumenu i ręcznego odbioru podaje README. Niezależne review
i ręczny odbiór nie są zastąpione testami automatycznymi.

#### S1-T5 — Przygotować granicę magazynu plików i lokalny adapter

**Status:** decyzje techniczne ustalone 16 listopada 2026 przez rolę
senior-software-architect w zleconym procesie realizacji
[issue #20](https://github.com/jwieczor03/mgr-llm-data-generator/issues/20).
Implementacja i testy wykonane w podanym zakresie; niezależne review i ręczny
odbiór użytkownika pozostają do wykonania.

**Cel:** logika aplikacji korzysta z logicznych referencji zamiast
fizycznych ścieżek, aby później można było wymienić magazyn.

**Źródło:** REQ-066 i AC-28 [specyfikacji](specyfikacja_mvp.md),
[przygotowanie do hostowania](przygotowanie_do_hostowania.md) oraz
[pełna decyzja architekta](ustalenia_architektoniczne.md#decyzje-architekta-z-16-listopada-2026--realizacja-s1-t5).
Zależności T1 i T2 dostarczają szkielet i konfigurację. T4 nie nadaje
magazynowi dostępu do bazy; S1-T5 nie dodaje tabel ani metadanych plików.

**Zakres:** moduł `application_api.artifact_store` z kontraktem
`ArtifactStore`, `ArtifactRef` i lokalnym adapterem. Operacje
`put(namespace, content: bytes) -> ArtifactRef`, `get(ref) -> bytes`
i `delete(ref) -> bool`, bez nadpisania, listowania i usuwania zbiorczego.
Dwie przestrzenie `project` i `working` mają odrębne katalogi i wolumeny.
Referencja zawiera tylko przestrzeń oraz UUID v4 wygenerowany przez adapter.
Oryginalne bajty pozostają niezmienione. Wywołujący kod w przyszłych
funkcjach odpowiada za kontrolę własności i przypisanie referencji do danych.

**Konfiguracja i integracja:** wymagane `ARTIFACT_PROJECT_ROOT`
i `ARTIFACT_WORKING_ROOT` w API; bezwzględne, rozłączne korzenie,
przygotowane przed startem. Braki blokują `artifacts`, zachowując diagnostykę
HTTP. Dostarczyć bezpieczny `/health/artifacts` oraz strażnik capability
według pełnego kontraktu w rejestrze. Compose montuje dwa nazwane wolumeny
tylko do API; obraz przygotowuje katalogi dla UID/GID 10001. Nie zmieniać
sposobu konfiguracji generatora i walidatora.

**Kryteria ukończenia i planowane sprawdzenia:**

1. Ten sam kontrakt pozwala podstawić adapter testowy bez fizycznych
   ścieżek w kodzie wywołującym. Zapis/odczyt zachowują bajty, także binarne;
   usuwanie działa tylko dla wskazanego obiektu i jest idempotentne.
2. Przerwany/błędny zapis przed atomową publikacją nie udostępnia
   częściowego obiektu ani nie narusza już zapisanych plików. Błąd
   usuwania jest jawny. Plik pomocniczy pozostały po awarii nie jest
   dostępny przez referencję. Atomowość nie obejmuje paczki DDL i bazy.
3. Błędne referencje, `..`, ścieżki absolutne, obce przestrzenie,
   symlinki i obiekty inne niż zwykłe pliki są odrzucane; żaden test
   nie odczytuje ani nie usuwa pliku poza wskazanym magazynem.
4. Brak konfiguracji/korzenia, odmowa dostępu i błąd I/O dają bezpieczne
   kody z rejestru. Raport nie ujawnia ścieżek ani treści i nie blokuje
   `/health/live`; capability odrzuca zależną operację przez 503.
   Po przywróceniu katalogu/dostępu kolejny probe może potwierdzić gotowość.
5. Test kontenerowy potwierdza probe jako UID 10001, zachowanie plików
   obu przestrzeni po odtworzeniu API i brak montowań w pozostałych
   backendach. Testy korzystają wyłącznie z własnych katalogów/wolumenów.
6. README wyjaśnia przygotowanie katalogów na hoście, konfigurację
   Compose, rzeczywiste komendy testów oraz ręczny odbiór diagnostyki
   przy brakującym i poprawnym zasobie. Wykonawca zapisuje rzeczywiste
   wyniki oraz ograniczenia; review i odbiór pozostają osobnymi etapami.

**Wyniki wykonawcy (16 listopada 2026):** testy API: 30 zaliczonych,
9 pominiętych wymagających osobnej bazy; osobna regresja PostgreSQL: 9 zaliczonych;
izolowany test Compose: 7 zaliczonych,
w tym UID 10001 i trwałość obu wolumenów po odtworzeniu API; regresja generatora
i walidatora: po 2 zaliczone testy. Odmowę uprawnień sprawdzono przez
kontrolowany błąd systemowy, nie zmianą praw dostępu na hoście. Review oraz
ręczny odbiór nie zostały wykonane.

**Poza zakresem:** workflow uploadu i wersji DDL z S2, eksport i API
pobierania z S8, metadane kandydatów, uprawnienia biznesowe T6 oraz
cykl życia i sprzątanie czatu z S9. Nie wybrano terminu kasowania plików
roboczych i nie zamknięto OD-09. Pierwszy kontrakt odczytuje cały plik
do pamięci; nie ustanawia limitu rozmiaru uploadu ani retencji.

#### S1-T6 — Przygotować lokalny kontekst właściciela i granicę kontroli dostępu

**Status:** implementacja przygotowana do niezależnego review; ręczny odbiór pozostaje osobnym krokiem.

**Cel i źródło:** wymienne źródło kontekstu i podstawa kontroli własności
bez logowania, na podstawie REQ-001, REQ-066 i AC-28
[specyfikacji](specyfikacja_mvp.md), zadania [#21](https://github.com/jwieczor03/mgr-llm-data-generator/issues/21)
oraz [przygotowania do hostowania](przygotowanie_do_hostowania.md).

**Zależność:** T1. Kontrakt i uzasadnienie zapisano w
[rejestrze](ustalenia_architektoniczne.md#kontekst-właściciela-i-polityka-dostępu--s1-t6).
Zaimplementowano lokalne źródło, politykę oraz zależności API. Testy
sprawdzają walidację, odmowę, wymianę zależności i brak kontekstu przez
trasę istniejącą wyłącznie w testach.

**Granice:** podłączenie projektów, wykonań i plików należy do ich story.
Nie ma kont, logowania ani izolacji rzeczywistych zasobów. Ten fundament
nie realizuje całego AC-28 ani nie zabezpiecza hostingu. Review i ręczny
odbiór nie są potwierdzone samą implementacją.

#### S1-T7 — Skonfigurować wspólne narzędzia kontroli jakości i testów

**Status:** implementacja w zadaniu [#22](https://github.com/jwieczor03/mgr-llm-data-generator/issues/22); niezależne review i ręczny odbiór są osobnymi etapami.

**Cel i zakres:** powtarzalna kontrola trzech niezależnych projektów uv,
frontendu i istniejących testów integracyjnych. Szczegóły decyzji technicznych
znajdują się w [rejestrze](ustalenia_architektoniczne.md), a komendy w
[README](../README.md#kontrola-jakości-i-testy-s1-t7).

**Plan realizacji:** przypiąć narzędzia i skonfigurować kolekcję pytest;
wyizolować konfigurację i dane testowe; przygotować osobne komendy kontroli
szybkiej i integracyjnej; sprawdzić sukces oraz kontrolowane błędy testów,
Ruff i TypeScript. Testy konkretnych funkcji pozostają w ich zadaniach.
Nie dodajemy CI, dodatkowych formaterów ani testów przeglądarkowych.

#### S1-T8 — Sprawdzić uruchomienie całości w przeglądarce i opisać obsługę środowiska

**Status:** implementacja w toku, [issue #23](https://github.com/jwieczor03/mgr-llm-data-generator/issues/23). Niezależne review i ręczny odbiór użytkownika pozostają osobnymi krokami.

**Cel:** użytkownik uruchamia fundament lokalnie według sprawdzonej
instrukcji i potrafi znaleźć przyczynę ograniczonej gotowości.

**Źródło i punkt startowy:** REQ-002, REQ-067, AC-29 i sekcja 13.5
[specyfikacji](specyfikacja_mvp.md). Istniejący `README.md`
jest punktem wejścia i opisuje uruchomienie dostarczonego fundamentu.
Instrukcja nie przedstawia fundamentu jako gotowej aplikacji biznesowej.

**Zależności:** dostarczone i sprawdzone zakresy T1–T7 oraz T9;
przed integracją rozstrzygnięcie podawania frontendu i sposobu
prezentacji sprawdzenia połączenia z API.

**Uzgodnione kroki:**
1. Odtworzyć zwykły lokalny start z Compose i potrzebną konfiguracją.
   Otworzyć frontend podawany przez `application-api` pod wspólnym
   adresem z API, bez uruchamiania serwera Vite.
2. Sprawdzić połączenie frontendu z API według uzgodnionego minimalnego
   kontraktu. Oddzielnie sprawdzić development z proxy Vite.
3. Zweryfikować start i odczyt niezależnego panelu. Nie powielać
   implementacji i pełnych testów monitora z T9.
4. Opisać wymagania środowiska, konfigurację bez sekretów, start,
   zatrzymanie, restart i odczyt diagnostyki. Wyjaśnić różnicę między
   działaniem procesu a gotowością oraz migracje tylko przy starcie.
5. Przekazać wyniki rzeczywistych sprawdzeń, ograniczenia i odtwarzalne
   kroki ręcznego odbioru użytkownikowi.

**Poza zakresem:** czat, generowanie, walidacja danych użytkownika
i potwierdzenie gotowości całej aplikacji biznesowej.

**Kryteria i planowane sprawdzenia:** instrukcja pozwala uruchomić
fundament lokalnie; frontend i API korzystają ze wspólnego adresu
bez Vite. Osobny tryb deweloperski działa przez proxy. Panel można
otworzyć także po zatrzymaniu `application-api`. Brak wymaganej
konfiguracji jest widoczny jako problem, nie jako pełna gotowość.
Instrukcja nie zawiera sekretów ani niezweryfikowanych poleceń.

**Ustalone:** szczegóły kontroli procesu i tekstów ekranu zapisano w
[rejestrze decyzji](ustalenia_architektoniczne.md#s1-t8--połączenie-ekranu-technicznego-z-api-17-listopada-2026)
oraz [systemie UI](ui/design-system.md#ekran-techniczny-s1-t8--decyzje-designera-17-listopada-2026).

**Wykonane sprawdzenia:** `scripts/check.py` przeszedł (w tym 7 testów
nowego widoku; testy bazy pominięte w szybkim przebiegu). Osobna kontrola
`integration` uruchomiła rzeczywisty PostgreSQL i Compose na izolowanych
danych: 9 testów bazy i 8 testów Compose przeszło. W osobnym projekcie
odbiorowym zwykły pierwszy start przed restartem zwrócił `ready` i migrację
`applied`. Wyścig z bazą nadal jest możliwy; instrukcja opisuje restart.
W przeglądarce sprawdzono połączenie pod wspólnym adresem API i przez
proxy Vite, ponowienie myszą i klawiaturą, jasny i ciemny motyw oraz
szerokości 390 i 1280 px bez poziomego przewijania. Po zatrzymaniu API
otwarta strona Vite pokazała błąd, a niezależny monitor działał i wskazał
niedostępność API. Po przywróceniu API oba widoki pokazały powrót działania;
ręczne kontrole monitora nie zmieniły czasu kolejnej kontroli automatycznej.
To wynik kontroli wykonawcy; ręczny odbiór użytkownika pozostaje osobny.

#### S1-T9 — Przygotować niezależny monitor serwisów i panel diagnostyczny

**Status:** implementacja w toku, [issue #24](https://github.com/jwieczor03/mgr-llm-data-generator/issues/24). Decyzje techniczne i wizualne
podjęto 17 listopada 2026 w delegowanym procesie realizacji. Niezależne
review i ręczny odbiór użytkownika pozostają osobnymi krokami.

**Story nadrzędne:** S1 — Fundament aplikacji i lokalne uruchomienie.

**Cel:** użytkownik może sprawdzić stan serwisów i przyczyny ograniczeń
bez debugowania, także gdy główna aplikacja jest niedostępna.

**Źródło i punkt startowy:** sekcja 13.5
[specyfikacji](specyfikacja_mvp.md), decyzje o diagnostyce
w [rejestrze ustaleń](ustalenia_architektoniczne.md) oraz sekcja
„Szczegółowa diagnostyka i monitoring” w
[kontraktach API](lld/kontrakty_api.md).
Monitor i panel implementowane są w `services/monitor-service` i
`apps/web`; szczegóły kontraktu zapisano w powyższym LLD.

**Uzgodniony zakres:**
1. Osobny proces regularnie odpytuje health checki serwisów,
   w tym `application-api`. Nie polega wyłącznie na jego raporcie
   zbiorczym. Każdy backend nadal sprawdza własne bezpośrednie zależności.
   `application-api` agreguje wyniki; nie tworzyć rekurencyjnego
   schematu, w którym każdy backend sprawdza wszystkie pozostałe.
2. Kontrole odbywają się przy uruchamianiu i co 30 minut.
3. Osobny panel w przeglądarce udostępnia wyniki także przy niedostępnym
   `application-api`. Podaje zdolność do działania, częściową zdolność
   lub brak zdolności, wraz z przyczynami i ograniczeniami.
4. „Sprawdź teraz” wykonuje nową, bezpłatną i niedestrukcyjną diagnostykę.
   Nie przesuwa kontroli automatycznych ani nie zeruje odstępu 30 minut.
5. Kontrole automatyczne są wyłącznie bezpłatne i niedestrukcyjne.
   Przycisk „Sprawdź teraz” nie uruchamia płatnych prób LLM.
   Wartości sekretów nie trafiają do wyników.
6. Szczegółowa diagnostyka backendu obejmuje inicjalizację, kompletność
   i poprawność używanej konfiguracji oraz sekretów, połączenia
   z wykorzystywanymi zewnętrznymi API, istnienie wymaganych zasobów
   wewnętrznych i dostęp do nich. Bezpłatna próba nie może być opisana
   jako potwierdzenie aspektu, którego nie sprawdza.
   Brak konfiguracji lub zależności nie wyłącza diagnostyki;
   blokowane są zależne operacje.

**Granice:** nie zmieniać kontraktu `/health/live` ani nie uznawać
działającego procesu za dowód gotowości do generowania. Monitor nie
ponawia generowania lub walidacji. Osobny proces nie gwarantuje
odporności na awarię hosta ani wykrycia własnego zatrzymania.
Płatne sprawdzenia wymagają odrębnej ręcznej akcji i zgody użytkownika;
ich obsługa pozostaje poza zakresem S1-T9.

**Zależności i blokady:** szkielety serwisów S1-T1, konfiguracja
i ochrona sekretów S1-T2 oraz uzgodniony kontrakt szczegółowej
diagnostyki backendów. Uzgodniono 15 listopada 2026 uruchamianie monitora
z panelem jako osobnej usługi w tym samym Docker Compose (integracja
w S1-T3), niezależnej od działania `application-api`. Wybrano FastAPI,
React/Vite i harmonogram oparty na asyncio; szczegóły i ograniczenia
opisują [kontrakty API](lld/kontrakty_api.md).

**Kryteria weryfikacji:**
- Po zatrzymaniu `application-api` panel nadal można otworzyć i odczytać
  wynik monitorowania tego serwisu, zamiast polegać na jego ostatnim
  raporcie zbiorczym.
- Zmiana stanu lub dostępności zależności jest widoczna po nowej kontroli,
  wraz z przyczyną i ograniczeniami udostępnionymi przez diagnostykę.
- Kontrola startowa i okresowe kontrole co 30 minut nie wykonują płatnych
  operacji ani nie ujawniają wartości sekretów.
- Ręczne sprawdzenie uruchomione między kontrolami nie zmienia terminu
  następnej kontroli automatycznej.
- Brak wymaganego sekretu, niedostępne API, brak zasobu i brak dostępu
  do zasobu dają odpowiadające im przyczyny i ograniczenia.
  Sprawdzić trzy uzgodnione poziomy zdolności na przypadkach
  wynikających z katalogu prób w [kontrakcie](lld/kontrakty_api.md).
- Health check i kontrole monitora nie uruchamiają migracji,
  także po usunięciu przyczyny wcześniejszego błędu migracji.

**Wyniki sprawdzeń:** testy izolowanego Compose potwierdziły dostępność
panelu i niezależne wyniki serwisów po zatrzymaniu API. Pozostałe wyniki
i ograniczenia sprawdzeń należy ocenić według dowodów w PR. Wygląd,
klawiatura i działanie panelu w rzeczywistej przeglądarce nie zostały
jeszcze sprawdzone; ręczny odbiór należy do użytkownika.

**Ograniczenia obecnego zakresu:** raport dotyczy fundamentu. Generator
i walidator są szkieletami; nie sprawdzono dostawcy ani modelu LLM.
Monitor nie wykrywa własnego zatrzymania ani awarii hosta.

### S2 — Zapisane projekty i rozpoznawanie schematu

**Cel i rezultat:** użytkownik zapisuje projekt z DDL, czyli definicją
struktury bazy, i wielokrotnie korzysta z rozpoznanego schematu.

**Zakres:** utworzenie i wybór projektu, wgranie pełnego DDL PostgreSQL,
rozpoznanie tabel i ograniczeń, wersje schematu oraz diagnostyka
nieobsługiwanych konstrukcji. Rozróżnienie relacji z DDL od propozycji,
które wymagają zatwierdzenia. Zakres obejmuje proste hierarchie
w jednej tabeli zgodnie z REQ-005, nie dowolne cykle.

**Poza zakresem:** edytor pojedynczych tabel i kolumn, połączenie
z istniejącą bazą użytkownika i obsługa całego PostgreSQL.
Obsługa kolumn `json`/`jsonb` pozostaje poza MVP.

**Źródła:** REQ-003–REQ-007, REQ-009–REQ-014;
AC-01–AC-05 i AC-37.

**Powiązania:** S1; dostarcza strukturę dla interpretacji zleceń,
generowania i walidacji. Zmiana wersji schematu nie zmienia wymagań
już rozpoczętego wykonania.

**Do wyjaśnienia:** macierz obsługiwanych konstrukcji i wybór parsera
(OD-01). Usuwanie projektów pozostaje w OD-09 i nie jest uzgodnioną
funkcją tego story.

#### Uzgodniony podział S2 na zadania

**Status:** podział zaakceptowany przez użytkownika 14 listopada 2026.
Poniższe pozycje określają rezultaty
i granice pracy, nie są jeszcze szczegółowymi instrukcjami implementacji.
Akceptacja podziału nie zatwierdza otwartych kontraktów ani reszty OD-01.
Wszystkie zadania mają rodzica S2.

| ID | Zadanie | Oczekiwany rezultat | Zależności |
| --- | --- | --- | --- |
| S2-T1 | Dodać zapis i odczyt projektów w backendzie | Projekt pozostaje dostępny do ponownego wyboru po zakończeniu czatu i ponownym uruchomieniu aplikacji. | Fundament magazynu i API z S1. |
| S2-T2 | Dodać wgrywanie i przechowywanie pełnych wersji DDL | Oryginalny DDL jest zachowany; pojedynczy plik lub wspólnie wysłana paczka plików tworzy jedną pełną wersję bez nadpisywania wcześniejszej. Błąd analizy jednego pliku blokuje użycie całej nowej wersji. Odczyt wskazanej wersji umożliwia zachowanie wymagań trwającego wykonania. | S2-T1. |
| S2-T3 | Dodać rozpoznawanie struktury i ograniczeń DDL | Analiza dostarcza tabele, kolumny, typy i obsługiwane ograniczenia, w tym klucze wielokolumnowe i automatyczne ID. Nie zależy od dziedziny ani stałych nazw obiektów. | S2-T2; uzgodniony parser i kontrakt modelu schematu. |
| S2-T4 | Dodać diagnostykę nieobsługiwanych konstrukcji i zależności | Analiza jawnie wskazuje ograniczenia obsługi oraz dostarcza informację blokującą generowanie zależne od nieobsługiwanego przypadku. Diagnostyka wskazuje oryginalny plik i wiersz, gdy lokalizację można ustalić; dla problemu całej paczki nie tworzy sztucznej lokalizacji. Nie odrzuca prostych hierarchii tylko z powodu relacji do tej samej tabeli. | S2-T3; doprecyzowany pozostały zakres OD-01. |
| S2-T5 | Dodać rozróżnianie i zatwierdzanie relacji spoza DDL | Relacje z DDL są obowiązujące; propozycje spoza DDL stają się obowiązujące dopiero po zatwierdzeniu, bez zmiany oryginału. Uzupełnienie jest powiązane z właściwą wersją schematu. | S2-T3; uzgodniony kontrakt relacji i źródło propozycji, w razie wykorzystania LLM integracja z S5. |
| S2-T6 | Dodać interfejs projektów, wgrywania DDL i podglądu analizy | Użytkownik tworzy i wybiera projekt, wgrywa pełny DDL lub nową wersję, przegląda strukturę i diagnostykę oraz zatwierdza propozycje relacji. | Odpowiednie operacje S2-T1–S2-T5 i fundament frontendu z S1. |

**Granice:** S2-T1–S2-T5 obejmują zapis, analizę i operacje backendu,
a S2-T6 ich interfejs. Interakcje S2-T6 można rozwijać wraz z gotowością
odpowiednich operacji, nie trzeba czekać na ukończenie całego backendu.
S2-T5 nie implementuje własnej integracji z dostawcą LLM.
Generowanie jawnych ID należy do S5, a ich rzeczywisty import do S7.
S6 odpowiada za przypięcie wymagań wykonania do konkretnej wersji;
S2 nie implementuje maszyny stanów wykonania ani historii czatów.
Nie obejmujemy usuwania projektów, edytora pojedynczych tabel ani
łączenia z bazą użytkownika.

**Pokrycie:** S2-T1–S2-T2 i S2-T6 realizują część projektową REQ-003,
REQ-009, REQ-014, AC-01 i AC-05; S2-T3–S2-T4 oraz podgląd S2-T6
obejmują rozpoznanie i diagnostykę REQ-004–REQ-005, REQ-010–REQ-011,
REQ-013, AC-02 i AC-04. S2-T5–S2-T6 obejmują zatwierdzanie z REQ-012
i AC-03; sprawdzanie danych względem tych relacji pozostaje w S7.
S2 dostarcza informacje o schemacie potrzebne dla REQ-006–REQ-007,
nie realizuje generowania ani nie ustala sztywnego limitu rekordów.
AC-37 wymaga współpracy S2, S5–S7, nie samego rozpoznania schematu.

**Sprawdzenie:** testy zachowania należy opisać przy każdym zadaniu,
uwzględniając schematy z różnych dziedzin i przypadki nieobsługiwane.
Nie utworzono osobnego zadania „testy na końcu”. Nie wykonano testów
aplikacji; repozytorium nadal nie zawiera jej implementacji.
Poniżej opisano wszystkie sześć zadań jako częściowo uzgodnione szkice.
Pola projektu i zachowanie po nieudanej analizie już uzgodniono.
Otwarte kontrakty, wybór parsera i pozostałe postacie DDL są wskazane
jako blokady przed implementacją, a nie powód do odkładania całego
opisu zadania. Nie pozostawiamy tych wyborów juniorowi.

#### S2-T1 — Dodać zapis i odczyt projektów w backendzie

**Status:** implementacja S2-T1 przygotowana; niezależne review i ręczny odbiór pozostają osobnymi krokami. Źródłem szczegółów jest [issue #25](https://github.com/jwieczor03/mgr-llm-data-generator/issues/25).

**Story nadrzędne:** S2 — Zapisane projekty i rozpoznawanie schematu.
**Cel:** użytkownik tworzy zapisany projekt i później odczytuje go bez
ponownego przygotowywania jego nazwy i opisu.
**Źródło:** REQ-009, projektowa część AC-01 i AC-40, sekcja 5.1
specyfikacji oraz uzgodniony zakres projektów w kontraktach API.

**Punkt startowy:** fundament S1 dostarcza bazę, migracje i kontekst właściciela. Model projektu i kontrakt API opisano w LLD.
**Zależności:** szkielet S1-T1, konfiguracja S1-T2, baza i mechanizm
migracji S1-T4, uzgodniony kontekst dostępu S1-T6 oraz narzędzia testów
z S1-T7. Wspólnej infrastruktury nie tworzymy ponownie w tym zadaniu.

**Zakres zadania:**
1. Dodać trwały zapis projektów w bazie aplikacji i potrzebną migrację.
   Utworzenie projektu nie wymaga DDL ani nie oznacza gotowości do generowania.
2. Dodać `POST /api/v1/projects` z wymaganą nazwą i opcjonalnym opisem.
   Przyjmować wyłącznie tekstową nazwę i opis tekstowy, `null` lub pominięty.
   Nie konwertować innych typów na tekst i odrzucać dodatkowe pola,
   również `id` i `created_at` nadawane przez backend.
   Usunąć brzegowe białe znaki przed sprawdzeniem długości i zapisem.
   Wymagać nazwy 1–100 znaków i opisu najwyżej 2000 znaków.
   Pusty opis traktować jako brak, nie obcinać przekroczonych wartości.
3. Zapewnić unikalność nazw bez rozróżniania wielkości liter.
   Konflikt nie może nadpisać projektu ani utworzyć duplikatu,
   również przy równoczesnym dostarczeniu żądań.
4. Zwracać `201` i obiekt `id`, `name`, `description`, `created_at`.
   Backend nadaje UUID i czas utworzenia. W API czas ma format
   ISO 8601 w UTC z końcówką `Z`, a brak opisu jest `null`.
5. Dodać `GET /api/v1/projects/{project_id}` z tym samym obiektem
   i odpowiedzią `200` oraz `GET /api/v1/projects` z `{"items": [...]}`.
   Zwracać wszystkie projekty bez podziału na strony, sortując po
   `created_at` malejąco, a przy remisie po `id` rosnąco.
6. Zwracać `422 VALIDATION_ERROR` dla niepoprawnych pól,
   `409 PROJECT_NAME_CONFLICT` dla zajętej nazwy i `404 PROJECT_NOT_FOUND`
   dla nieistniejącego projektu. Stosować uzgodnioną strukturę `error`
   z `code`, `message`, `request_id`, `automatic_retry_allowed=false`
   i `details.fields`. Każdy problem pola ma `field` i `message`;
   konflikt wskazuje `name`, a nieistniejący projekt daje pustą listę.

**Poza zakresem:** frontend (S2-T6), upload i analiza DDL (S2-T2–T4),
reguły i relacje, usuwanie lub edycja projektu, konta oraz historia czatów.

**Kryteria ukończenia i planowane sprawdzenia:**
- Utworzenie projektu bez DDL daje `201`, a odczyt po jego `id` zwraca
  te same zapisane dane; projekt pozostaje dostępny po restarcie backendu.
- Po zapisaniu `Bank` próby zapisania `bank` i ` Bank ` dają `409`
  bez zmiany wcześniejszego projektu. Sprawdzić również równoczesne próby.
- Nazwa z samych białych znaków i nazwa o długości 101 znaków dają `422`;
  poprawne nazwy długości 1 i 100 znaków są przyjmowane.
- Opis o długości 2000 znaków jest przyjmowany, a 2001 daje `422`.
  Pusty opis po usunięciu brzegowych białych znaków wraca jako `null`.
- Pusta lista daje `200` i `{"items": []}`. Kilka projektów jest zwracanych
  w uzgodnionej kolejności, także przy identycznym czasie utworzenia.
- Nieistniejący, poprawnie zapisany identyfikator projektu daje `404`.
- Brak `name`, `name=null`, liczba lub wartość logiczna zamiast tekstu,
  dodatkowe pole i niepoprawny UUID w ścieżce dają `422 VALIDATION_ERROR`
  ze wskazaniem pola. Nie powstaje projekt z automatycznie przekonwertowaną
  wartością. Dla niepoprawnego UUID wskazane pole to `project_id`.
- Pominięty `description`, `description=null` i pusty opis po usunięciu
  brzegowych białych znaków skutkują `description=null` w odpowiedzi.
- Błędy mają uzgodnione kody tekstowe i strukturę; konflikt nazwy wskazuje
  `details.fields` z polem `name`, a `404` ma pustą listę pól.
  Odpowiedź nie ujawnia szczegółów bazy ani zapytań SQL.
- Przykłady projektów obejmują różne dziedziny, bez listy dozwolonych branż.
  Testy automatyczne należą do tego zadania.

**Ręczna weryfikacja:** utworzyć projekt, odczytać go i listę, sprawdzić konflikt nazwy, zrestartować backend i ponowić odczyt. Przykładowe polecenia znajdują się w README. Odbiór w przeglądarce będzie możliwy po S2-T6.

#### S2-T2 — Dodać wgrywanie i przechowywanie pełnych wersji DDL

**Stan implementacji — 19 listopada 2026:** zapis paczki, rezerwacja,
potwierdzenie, wersje, odzyskiwanie i izolowany worker są dostarczane w
[S2-T2, issue #26](https://github.com/jwieczor03/mgr-llm-data-generator/issues/26).
Parser i ocena obsługiwalności pozostają w S2-T3/T4: do ich integracji analiza
kończy się błędem technicznym, bez wyboru nowej wersji domyślnej. Ręczny
odbiór należy do użytkownika; kroki API znajdują się w README. Poniższy opis
zachowano historycznie; aktualny zakres techniczny określa issue #26.
**Story nadrzędne:** S2 — Zapisane projekty i rozpoznawanie schematu.
**Cel:** zachować oryginalne pliki i kolejność każdej pełnej wersji
schematu bez nadpisywania poprzednich wersji.
**Źródło:** REQ-003, REQ-009–REQ-014, sekcje 5.1 i 13.3 specyfikacji
oraz uzgodnienia S2-T2 zapisane w stanie sesji.
**Punkt startowy:** docelowy backend `services/application-api/`,
tworzony w S1; projekt z S2-T1. Model danych LLD zawiera propozycje
`schema_versions` i `schema_interpretations`, nie zatwierdzony
kompletny model przechowywania paczki.
**Zależności:** S2-T1, magazyn i migracje S1-T4, dostęp S1-T6,
narzędzia testów S1-T7; do integracji wyniku analizy kontrakty S2-T3–T4.

**Co należy zrobić po wyjaśnieniu braków:**
1. Dodać przyjęcie pojedynczego pliku lub wspólnie wysyłanych plików SQL
   jako jednej pełnej wersji istniejącego projektu. Zachować oryginalne
   pliki i kolejność ustawioną przez użytkownika. Nie scalać ich
   z fragmentami poprzedniej wersji.
2. Wymagać UTF-8, dopuszczając BOM na początku każdego pliku.
   BOM pomijać wyłącznie przy analizie; nie zmieniać oryginalnych plików.
   Nie zgadywać kodowania ani automatycznie konwertować błędnych plików.
   Błąd kodowania choćby jednego pliku odrzuca całą paczkę przed
   utworzeniem wersji i uruchomieniem analizy DDL. W MVP ponownie
   wysyłana jest pełna poprawiona paczka, bez podmiany pojedynczego pliku.
   Pusty plik lub plik zawierający wyłącznie białe znaki również odrzuca
   całą paczkę przed utworzeniem wersji, zamiast być automatycznie pomijany.
   Tak samo traktować plik zawierający wyłącznie komentarze SQL
   i ewentualne białe znaki, bez instrukcji SQL.
   Wymagać unikalnych nazw plików w paczce bez rozróżniania wielkości
   liter. Konflikt odrzuca całą paczkę przed utworzeniem wersji.
   Dla kompletnie odebranej paczki zebrać wykryte błędy kodowania,
   pustych plików i konfliktów nazw, zamiast kończyć sprawdzanie
   na pierwszym błędzie. Nie wymagać analizy treści pliku, którego
   nie można poprawnie odczytać. Nie jest to zobowiązanie do zebrania
   wszystkich błędów późniejszej analizy DDL.
3. Przy przerwanym transferze lub nieudanym zapisie nie tworzyć nowej
   wersji. Dotychczasowy schemat pozostawić bez zmian; ponowne wysłanie
   ma obejmować całą paczkę. Nie utożsamiać utraty odpowiedzi
   z potwierdzonym nieudanym zapisem. Po utracie odpowiedzi najpierw
   sprawdzić wynik wysłania, zamiast od razu proponować ponowienie.
   Wykorzystać unikalny identyfikator próby utworzony przez frontend
   przed wysłaniem plików. Odczyt wyniku tej samej próby w backendzie
   nie wymaga ponownego przesyłania paczki.
   Jeśli wynik nadal jest nieznany, blokować ponowne wysłanie tej paczki
   do ustalenia wyniku. Udostępnić w S2-T6 przycisk „Sprawdź ponownie”
   odczytujący wynik tej samej próby, bez przesyłania plików.
   Odświeżenie lub zamknięcie strony/aplikacji podczas transferu
   ma anulować przesyłanie. Samo ostrzeżenie i rezygnacja z wyjścia
   nie anulują transferu. Po wykonanym wyjściu przed odebraniem
   potwierdzenia przez przeglądarkę nie zachowywać nowej wersji również
   wtedy, gdy backend zapisał już całą paczkę. Usunąć pliki anulowanej
   próby bez zmiany wcześniejszych wersji. Mechanizm rozpoznania,
   anulowania i sprzątania jest otwarty.
4. Potwierdzić odebranie i zapis plików bez oczekiwania na zakończenie
   analizy. Najpierw zapisać paczkę roboczo i wysłać komunikat o zapisie.
   Uruchomić analizę dopiero po otrzymaniu dodatkowego automatycznego
   potwierdzenia z przeglądarki, że odebrała ten komunikat, bez wymagania
   dodatkowego kliknięcia. Sam zapis ani wysłanie odpowiedzi nie
   uruchamiają analizy. Udostępnić paczkę do analizy w tle w ustalonej kolejności
   i przyjąć jej wynik według przyszłego kontraktu S2-T3–T4.
   Udostępnić stan analizy dla interfejsu S2-T6. Błąd analizy jednego
   pliku zachowuje całą nieudaną wersję z diagnostyką, ale blokuje jej użycie.
   Po otrzymaniu dodatkowego potwierdzenia analiza jest niezależna od
   otwartej strony. Odświeżenie lub zamknięcie strony nie anuluje już
   rozpoczętej analizy przyjętej paczki. Osobne ręczne przerwanie
   nadal obowiązuje; zatrzymanie backendu podlega obsłudze awarii.
   Egzekwować limit jednej aktywnej analizy DDL w całej aplikacji MVP,
   także między różnymi projektami. Podczas analizy blokować wgrywanie
   DDL we wszystkich projektach, bez przyjmowania paczek do kolejki.
   Blokada obowiązuje już od rozpoczęcia wysyłania jednej paczki,
   również w innych kartach przeglądarki i we wszystkich projektach.
   Nie dopuszczać równoczesnego wysyłania kolejnej paczki przed analizą.
   Mechanizm egzekwowania pozostaje otwarty.
   Próbę wysłania kolejnej paczki przy aktywnej blokadzie odrzucać
   odpowiedzią HTTP `409` z kodem `DDL_PROCESSING_IN_PROGRESS`.
   Pozostałe pola błędu i ścieżka uploadu pozostają otwarte.
   Zachować blokadę również podczas oczekiwania na automatyczne
   ponowienie analizy po awarii; przerwa pomiędzy próbami nie pozwala
   przyjąć kolejnej paczki.
   Po awarii przerywającej analizę automatycznie uruchomić analizę
   zapisanej paczki ponownie, gdy jest to możliwe, bez ponownego wgrywania
   i bez ręcznej akcji, maksymalnie trzy razy poza pierwszym uruchomieniem.
   Po wyczerpaniu ponowień zatrzymać analizę z czytelnym błędem,
   bez kolejnego automatycznego ponowienia. Nie oznacza to automatycznego
   naprawiania DDL ani ponawiania generowania danych.
   Nie udostępniać ręcznego ponowienia analizy zapisanej paczki po
   wyczerpaniu trzech automatycznych ponowień. Dalsza próba wymaga
   ponownego wgrania całej paczki, bez wznawiania zakończonej analizy.
   Przy ponowieniu kontynuować od zachowanego postępu, jeżeli jest to
   technicznie możliwe i zapewnia poprawny, kompletny wynik. W przeciwnym
   razie automatycznie analizować zapisaną paczkę od początku, w ramach
   tego samego limitu trzech ponowień, bez ponownego wgrywania.
   Wykonalność i zapis postępu wymagają rozstrzygnięcia przed implementacją.
   Dodać możliwość przerwania analizy przez użytkownika. Wgranie kolejnej
   wersji w tym samym projekcie dopuścić dopiero po zatrzymaniu bieżącej
   analizy; nie analizować obu wersji równolegle. Świadome przerwanie
   nie może uruchamiać automatycznego ponowienia starej analizy.
   Interfejs S2-T6 wymaga przed przerwaniem potwierdzenia z ostrzeżeniem
   o usunięciu plików i częściowego wyniku. Rezygnacja z potwierdzenia
   nie wywołuje zatrzymania ani usuwania danych.
   Po potwierdzonym ręcznym zatrzymaniu usunąć pliki wgrane dla tej
   analizy i jej częściowy wynik. Nie zachowywać ich jako wersji
   „przerwana”; nie zmieniać wcześniejszych wersji schematu.
5. Wersję po poprawnej analizie bez blokad użycia wybrać automatycznie
   jako domyślną dla nowych zleceń. Nie zmieniać wymagań rozpoczętych
   wykonań. Domyślność nie omija ponownego przeglądu reguł i relacji.
6. Dodać odczyt wskazanej wersji. Wewnętrzny podział odpowiedzialności
   za blokadę przeglądu uzgodnić z S2-T5, S3 i S6, bez dublowania wdrożenia.

**Poza zakresem:** parser i diagnostyka S2-T3–T4, interfejs S2-T6,
interpretacja reguł S3, generowanie LLM, import do bazy użytkownika,
obsługa ZIP bez osobnego uzgodnienia, podmiana pojedynczego pliku
w zapisanej paczce (kierunek rozwoju po MVP).

**Kryteria ukończenia i plan sprawdzeń:**
- Ponowny odczyt wersji zwraca te same oryginalne pliki w tej samej
  kolejności, także gdy różni się ona od kolejności alfabetycznej.
- Kolejna pełna paczka tworzy nową wersję, nie zmienia poprzedniej.
- Wymuszony błąd transferu lub zapisu nie pozostawia nowej wersji
  schematu ani nie zmienia dotychczasowej wersji domyślnej.
- Utrata odpowiedzi po udanym zapisie powoduje sprawdzenie wyniku
  wysłania, bez ponownego wysyłania plików i tworzenia drugiej wersji.
  Odczyt korzysta z identyfikatora utworzonego przed wysłaniem,
  nie z nowego identyfikatora po utracie odpowiedzi.
- Przy niedostępnym odczycie wyniku próby ponowne wysłanie paczki jest
  zablokowane. „Sprawdź ponownie” odpytuje o tę samą próbę bez uploadu;
  brak odpowiedzi nie jest przedstawiany jako potwierdzony błąd zapisu.
  Po przywróceniu odczytu można ustalić faktyczny wynik.
- Podczas kontrolowanego, niezakończonego transferu osobno spróbować
  odświeżyć i zamknąć stronę: wymagane ostrzeżenie o anulowaniu,
  zgodnie z ograniczeniami sekcji 11.1 specyfikacji. Pozostanie na stronie
  nie anuluje przesyłania; wykonane wyjście ma anulować transfer,
  bez utworzenia wersji z niekompletnej paczki. To plan, nie wynik testu.
- Zasymulować zapis kompletnej paczki i opóźnić dostarczenie potwierdzenia.
  Wykonać wyjście przed jego odebraniem przez przeglądarkę. Oczekiwane:
  nowa wersja nie jest zachowywana, pliki tej próby są usuwane,
  wcześniejsze wersje pozostają bez zmian. Mechanizm i sposób
  potwierdzenia skutku muszą zostać uzgodnione przed implementacją.
- Zatrzymać dodatkowe potwierdzenie z przeglądarki po roboczym zapisie
  paczki: analiza nie startuje. Dostarczyć potwierdzenie: dopiero wtedy
  można uruchomić analizę w tle. Nie wymagać nowego kliknięcia użytkownika.
- Po przyjęciu dodatkowego potwierdzenia i rozpoczęciu analizy osobno
  odświeżyć i zamknąć stronę, pozostawiając backend uruchomiony.
  Analiza trwa w tle i może zapisać wynik; dane tej wersji nie są
  usuwane z powodu opuszczenia strony. Nie mylić z anulowaniem transferu.
- Sprawdzić dwa różne projekty: ich analizy DDL nigdy nie działają
  jednocześnie. Podczas analizy w pierwszym projekcie wgrywanie DDL
  w drugim jest zablokowane; paczka nie trafia do kolejki. Techniczny
  kontrakt odmowy obejmuje HTTP `409` i `DDL_PROCESSING_IN_PROGRESS`;
  pozostałe pola pozostają do uzgodnienia.
- Rozpocząć wysyłanie paczki i opóźnić transfer, zanim ruszy analiza.
  Z drugiej karty spróbować wysłać kolejną paczkę, także do innego
  projektu. Drugie wysłanie jest blokowane już podczas pierwszego
  transferu, a nie dopiero po rozpoczęciu analizy.
- Wymusić awarię analizy i zatrzymać jej automatyczne ponowienie
  w stanie oczekiwania. Próba wgrania kolejnej paczki, także w innym
  projekcie lub karcie, nadal jest blokowana pomiędzy uruchomieniami.
- Przy kontrolowanym opóźnieniu analizy wgranie jest już potwierdzone,
  a stan analizy jest dostępny do odczytu. Samo potwierdzenie zapisu
  nie dopuszcza nieprzeanalizowanej wersji do generowania.
- Po wymuszonej awarii w trakcie analizy i przywróceniu możliwości pracy
  aplikacja automatycznie uruchamia analizę zapisanej paczki, bez
  ponownego wgrywania i ręcznej akcji.
- Wymuszać awarię pierwszego uruchomienia i każdego z trzech ponowień.
  Oczekiwane: po pierwszym uruchomieniu następują najwyżej trzy automatyczne
  ponowienia; po ich niepowodzeniu analiza zatrzymuje się z czytelnym
  błędem, bez czwartego automatycznego ponowienia.
- Po wyczerpaniu trzech automatycznych ponowień nie można ręcznie
  ponowić analizy zapisanych plików. Interfejs informuje o konieczności
  ponownego wgrania całej paczki; nie pokazuje akcji wznawiającej
  zakończoną analizę. Nowe wgranie nie podmienia pojedynczego pliku.
- Przy braku możliwości kontynuacji analiza automatycznie zaczyna od
  początku zapisanej paczki, bez ponownego wgrywania. Przejście z kontynuacji
  na analizę od początku nie przyznaje dodatkowych ponowień.
- Podczas analizy użytkownik ją przerywa. Nowy DDL można wgrać po jej
  zatrzymaniu, bez równoległej analizy obu wersji i bez automatycznego
  ponowienia świadomie przerwanej analizy.
- Po potwierdzonym ręcznym zatrzymaniu pliki tej analizy i częściowy
  wynik są usuwane. Wcześniejsze wersje i ich pliki pozostają bez zmian.
  Osobno sprawdzić, że awaria nie uruchamia tego sprzątania zamiast
  uzgodnionego automatycznego ponowienia.
- W interfejsie S2-T6 wybranie przerwania najpierw pokazuje ostrzeżenie
  o usunięciu plików i częściowego wyniku. Rezygnacja pozostawia analizę
  i dane bez zmian; potwierdzenie uruchamia zatrzymanie, a po nim sprzątanie.
- Nieudana analiza kompletnej paczki zachowuje jedną wersję z diagnostyką,
  bez częściowego przyjęcia poprawnych plików.
- Poprawna analiza pozwala wybrać nową wersję domyślną; wymagania
  rozpoczętego wcześniej wykonania pozostają bez zmian.
- Sprawdzić pliki UTF-8 z polskimi znakami, z BOM i bez niego,
  oraz niepoprawną sekwencję bajtów. Nie wolno cicho zastępować znaków.
- Paczka z poprawnym plikiem i plikiem o błędnym kodowaniu daje czytelny
  błąd bez utworzenia wersji schematu i bez uruchomienia analizy DDL.
  Ponowne przesłanie poprawionego pełnego zestawu przechodzi sprawdzenie
  kodowania. Nie ma operacji podmiany jednego pliku w zapisanej paczce.
- Pojedynczy pusty plik i plik zawierający wyłącznie białe znaki nie
  tworzą wersji. Paczka zawierająca taki plik i poprawny plik jest
  odrzucana w całości, bez automatycznego pominięcia pustego pliku.
- Pliki o identycznych nazwach lub nazwach różniących się tylko wielkością
  liter, np. `schema.sql` i `SCHEMA.sql`, powodują odrzucenie całej paczki
  przed utworzeniem wersji. Różne nazwy nie powodują tego konfliktu.
- Wysłać kompletną paczkę zawierającą jednocześnie plik o błędnym
  kodowaniu, inny pusty plik oraz parę nazw różniących się tylko
  wielkością liter. Oczekiwane: wspólna lista wykrytych problemów,
  bez zakończenia na pierwszym, bez utworzenia wersji i analizy DDL.
- Plik zawierający wyłącznie komentarze SQL, także z białymi znakami,
  jest traktowany jak pusty i powoduje odrzucenie całej paczki przed
  utworzeniem wersji. Rozpoznawanie komentarzy nie może usuwać tekstu
  będącego częścią wartości SQL; sposób rozpoznania wymaga projektu.
- Plan sprawdzeń musi objąć uzgodnioną skalę kilkuset tabel; konkretny
  zestaw i oczekiwane czasy pozostają do ustalenia.

**Do wyjaśnienia:** kontrakt API przesyłania i odczytu, dokładne stany
oraz mechanizm analizy w tle, zapis licznika i odstępy automatycznych
ponowień po awarii, wykonalność i zapis postępu
kontynuowanej analizy, potwierdzenie zatrzymania analizy, techniczny zapis
i usuwanie roboczej wersji, obsługa błędu sprzątania, zapis paczki
i jego spójność, uprawnienia, limity liczby plików
i bajtów, techniczny sposób porównania nazw, pozostała walidacja nazw
i techniczny sposób rozpoznania pustej treści SQL,
format i przechowywanie identyfikatora próby oraz odczyt jej wyniku,
zachowanie identyfikatora i blokady po odświeżeniu strony, sprzątanie plików, kontrakt
przekazania analizy oraz blokady ponownego przeglądu.
Sposób ręcznego sprawdzenia przez API i komendy testów wymagają gotowych
kontraktów i konfiguracji S1. Powyższe testy są planowane, nie wykonane.

#### S2-T3 — Dodać rozpoznawanie struktury i ograniczeń DDL

**Stan implementacji:** parser `pglast==8.9` tworzy model pośredni
i checkpoint workera dla profilu `postgres-mvp-v1`. Ocena obsługiwalności
pozostaje w S2-T4, dlatego wynik pośredni nie jest publikowany jako końcowa
analiza; worker kończy technicznie po istniejących ponowieniach. Aktualne
ustalenia i ograniczenia opisuje [rejestr](ustalenia_architektoniczne.md).
Poniższy szkic zachowuje historyczny punkt startowy zadania.


**Status opisu:** szkic oparty na uzgodnionym zakresie,
**do wyjaśnienia przed implementacją**.
**Story nadrzędne:** S2 — Zapisane projekty i rozpoznawanie schematu.
**Cel:** otrzymać opis struktury przesłanego schematu, wspólny dla
podglądu, przygotowania zlecenia, generowania i walidacji.
**Źródło:** REQ-004–REQ-005, REQ-010–REQ-011; sekcja 5.1 specyfikacji,
uzgodniona część macierzy PostgreSQL w `lld/walidacja.md`;
AC-02 i część schematowa AC-37.
**Punkt startowy:** docelowy `services/application-api/` tworzony w S1.
Nie ma jeszcze modułu parsera. `schema_interpretations` w modelu LLD
jest propozycją zapisu, nie zatwierdzonym formatem wyniku.
**Zależności:** zapis paczki i przekazanie jej do analizy z S2-T2;
wybrany parser i model schematu; narzędzia testów z S1.

**Co należy zrobić po zamknięciu blokad technicznych:**
1. Przyjąć komplet plików jednej wersji z S2-T2. Czytać je w kolejności
   ustawionej przez użytkownika, bez przestawiania instrukcji, zmieniania
   oryginałów lub dołączania plików starszej wersji.
2. Rozpoznać tabele, kolumny, typy oraz obsługiwane ograniczenia.
   Uwzględnić `smallint`, `integer`, `bigint`, `numeric`/`decimal`
   z precyzją i skalą, `text`, `varchar` z długością, `boolean`, `uuid`,
   `date`, `timestamp` i `timestamptz`.
3. Rozpoznać wymaganie wartości `NOT NULL`, klucze główne, obce
   i ograniczenia unikalności. Dla kluczy wielokolumnowych zachować
   kompletną listę i przyporządkowanie kolumn; nie zastępować jednego
   klucza złożonego kilkoma niezależnymi relacjami.
4. Rozpoznać uzgodnione `CHECK`: porównania, `BETWEEN`, `IN`,
   `AND`, `OR`, `NOT` w jednym rekordzie, bez funkcji.
   Dla `DEFAULT` obsłużyć zgodne typowo stałe, `CURRENT_DATE`
   i `CURRENT_TIMESTAMP`, bez dopuszczania dowolnych wyrażeń.
5. Rozpoznać `serial`, `bigserial` i oba warianty `IDENTITY`.
   Przekazać tę informację odbiorcom modelu; nie generować tutaj
   wartości ID i nie implementować importu ani obsługi sekwencji.
6. Relacje zadeklarowane w DDL przekazać jako jawne, obowiązujące.
   Nie odgadywać relacji z nazw takich jak `buyer_id`. Nie zaszywać
   nazw tabel, pól ani statusów właściwych bankowi lub sklepowi.
7. Zachować informacje potrzebne diagnostyce S2-T4, w tym powiązanie
   z oryginalnym plikiem i wierszem, gdy pozycję można ustalić.
   Wynik przekazać S2-T2 według uzgodnionego kontraktu, bez częściowego
   uznania błędnej paczki za nowy poprawny schemat.

**Poza zakresem:** wybór wersji domyślnej i sterowanie ponowieniami
z S2-T2, samodzielne rozszerzanie dialektu, propozycje relacji spoza DDL,
wywołania LLM, generowanie danych, próbny import oraz interfejs.

**Kryteria ukończenia i plan sprawdzeń:**
- Schemat bankowy i sklepowy z różnymi nazwami daje wierny opis tabel,
  kolumn i obsługiwanych ograniczeń, bez reguł wpisanych pod przykład.
- Przypadki obejmują każdy uzgodniony typ oraz precyzję, skalę i długość.
- Złożone PK, FK i `UNIQUE` zachowują wszystkie kolumny i powiązania.
- Uzgodnione warianty `CHECK`, `DEFAULT` i automatycznych ID są
  rozpoznane; nieobsługiwane wyrażenie nie znika z diagnostyki.
- Relacja do tej samej tabeli pozostaje w modelu; sam ten fakt
  nie oznacza odrzucenia prostej hierarchii.
- Paczka wieloplikowa zachowuje kolejność i oryginalne dane.
  Zestaw o skali kilkuset tabel wymaga osobnego uzgodnionego pomiaru;
  szkic nie deklaruje wyniku ani gwarantowanego czasu.

**Do wyjaśnienia:** wybór parsera (SQLGlot jest tylko kandydatem),
format modelu schematu i jego odczytu, obsługa nazw i schematów SQL,
pozostałe warianty DDL z OD-01 oraz kontrakt źródłowych pozycji.
Komendy testów zostaną podane po konfiguracji S1; testów nie wykonano.

#### S2-T4 — Dodać diagnostykę nieobsługiwanych konstrukcji i zależności

**Status opisu:** częściowo uzgodniony szkic,
**do wyjaśnienia przed implementacją**.
**Story nadrzędne:** S2 — Zapisane projekty i rozpoznawanie schematu.
**Cel:** użytkownik rozumie ograniczenia analizy, a aplikacja nie
uruchamia generowania zależnego od nieobsługiwanego przypadku.
**Źródło:** REQ-005, REQ-013, sekcje 4.2 i 5.1 specyfikacji;
AC-04 i AC-37; uzgodniona część OD-01 w `lld/walidacja.md`.
**Punkt startowy:** model schematu i informacje o pozycjach z S2-T3;
docelowy `services/application-api/`. Moduł diagnostyki jest do utworzenia.
**Zależności:** S2-T3; dla zapisu wyniku i stanu integracja z S2-T2;
dla blokady wykonania kontrakt przekazania informacji do S6.

**Co należy zrobić po doprecyzowaniu kontraktów:**
1. Na podstawie analizy wskazać błędne lub nieobsługiwane konstrukcje
   zamiast je pomijać i przedstawiać schemat jako w pełni obsługiwany.
   Rozróżnić problem treści DDL od awarii technicznej procesu analizy.
2. Diagnozować znane ograniczenia MVP: kolumny `json`/`jsonb`,
   nieobsługiwane wyrażenia `CHECK` i `DEFAULT`, poprawność zależną
   od wyzwalaczy, procedur lub własnych funkcji oraz nieobsługiwane
   obowiązkowe zależności kołowe. Nie rozstrzygać samodzielnie reszty OD-01.
3. Dla możliwego do zlokalizowania problemu podać oryginalny plik
   i numer wiersza w tym pliku. Nie podawać wyłącznie numeru z połączonego
   skryptu. Problem całej paczki opisać bez sztucznej lokalizacji.
4. Nie klasyfikować każdej relacji do własnej tabeli jako zakazanego
   cyklu. Prosta hierarchia z dopuszczalnym brakiem rodzica dla korzenia
   pozostaje w MVP; analiza samego DDL nie jest dowodem, że przyszłe
   rekordy nie będą zawierały zapętleń.
5. Dostarczyć informację blokującą użycie nieobsługiwanego przypadku.
   Współpracować z S2-T2 przy zachowaniu nieudanej wersji z diagnostyką
   i z S6 przy blokowaniu zależnego zlecenia. Nie implementować ponownie
   magazynu wersji ani maszyny wykonania.
6. Nie usuwać ograniczeń i nie przepisywać DDL, żeby uzyskać pozytywny
   wynik. Zbiorcza kontrola kodowania, pustych plików i nazw w S2-T2
   nie oznacza obowiązku zebrania wszystkich błędów analizy DDL.

**Poza zakresem:** automatyczna naprawa DDL, obsługa dowolnych cykli,
walidowanie wygenerowanych rekordów, wykonywanie kodu LLM,
próbny import S7 i prezentacja interfejsu S2-T6.

**Kryteria ukończenia i plan sprawdzeń:**
- Schemat wymagający nieobsługiwanej obowiązkowej zależności kołowej
  daje jawną diagnozę przed generowaniem zależnego zlecenia (AC-04).
- Prosta hierarchia jednej tabeli nie jest odrzucana wyłącznie za FK
  wskazujący tę samą tabelę; testy danych i importu należą do S5–S7.
- Nieobsługiwany `CHECK` z funkcją, `DEFAULT` spoza katalogu
  i kolumna `jsonb` są jawnie wskazane, nie pominięte.
- Błąd w drugim pliku wskazuje jego oryginalny wiersz, także przy BOM
  i komentarzach. Błąd ogólny nie otrzymuje zmyślonej lokalizacji.
- Nieudana analiza nie zastępuje wcześniejszej wersji domyślnej;
  ten scenariusz integracyjny wykorzystuje zapis z S2-T2.

**Do wyjaśnienia:** reszta macierzy OD-01, rozpoznawanie obowiązkowych
cykli i jego granice, kontrakt diagnostyki oraz blokad dla S6,
mapowanie pozycji parsera na pliki, statusy błędów analizy.
Nie wybrano komend sprawdzeń i nie wykonano testów.

#### S2-T5 — Dodać rozróżnianie i zatwierdzanie relacji spoza DDL

**Status opisu:** częściowo uzgodniony szkic,
**do wyjaśnienia przed implementacją**.
**Story nadrzędne:** S2 — Zapisane projekty i rozpoznawanie schematu.
**Cel:** używać dodatkowej relacji dopiero po świadomym zatwierdzeniu
i zachować różnicę między nią a relacją zadeklarowaną w DDL.
**Źródło:** REQ-011–REQ-014, sekcja 5.1 specyfikacji; AC-02–AC-03,
AC-05 i granica sprawdzania z AC-34.
**Punkt startowy:** wynik S2-T3 i wersja schematu S2-T2;
docelowy `services/application-api/`. Model relacji i operacje
zatwierdzania są do zaprojektowania; nie ma gotowego modułu.
**Zależności:** S2-T2–T3; uzgodnione źródło propozycji i kontrakt relacji;
w razie użycia LLM adapter S5, bez własnej integracji z dostawcą.

**Co należy zrobić po doprecyzowaniu kontraktów:**
1. Rozróżnić relacje z DDL, propozycje spoza DDL i zatwierdzone relacje
   dodatkowe. To wymagane znaczenia, nie przyjęte nazwy enumów lub pól.
2. Nie wymagać zatwierdzania jawnego FK jako domysłu i nie zastępować
   go relacją wynikającą z podobieństwa nazw. Samo pole `buyer_id`
   nie upoważnia do dodania obowiązującej relacji.
3. Przyjąć propozycję zgodnie z uzgodnionym później źródłem i powiązać
   ją z konkretną wersją schematu. Udostępnić S2-T6 czytelne znaczenie
   propozycji do decyzji użytkownika oraz operację jej zatwierdzenia.
4. Dopiero po zatwierdzeniu przekazywać relację dodatkową jako
   obowiązującą dla nowych zleceń. Nie dopisywać jej do oryginalnego DDL.
   Udostępnić ją przygotowaniu zlecenia i walidacji przez uzgodnione
   kontrakty, bez implementowania tych obszarów w tym zadaniu.
5. Po zmianie wersji wcześniejsze dodatkowe relacje pokazać jako
   propozycje do ponownego przeglądu, nie jako automatycznie zatwierdzone.
   Każdą trzeba zweryfikować i zatwierdzić albo świadomie odrzucić
   dla nowej wersji. Nie zmieniać wymagań rozpoczętych wykonań.
6. Przekazać stan rozpatrzenia propozycji do wspólnej blokady przeglądu
   z S2-T2/S3/S6. Nie tworzyć osobnego, konkurencyjnego mechanizmu
   gotowości projektu ani drugiej implementacji reguł biznesowych.

**Poza zakresem:** automatyczne uznawanie domysłów za obowiązujące,
zmienianie oryginalnego DDL, interpretacja reguł biznesowych S3,
własny klient LLM, sprawdzanie relacji na danych po imporcie (S7),
generowanie danych i interfejs S2-T6.

**Kryteria ukończenia i plan sprawdzeń:**
- Jawny FK od początku jest obowiązujący, bez akcji akceptacji domysłu.
- Propozycja dla `buyer_id` nie obowiązuje przed zatwierdzeniem (AC-03);
  po zatwierdzeniu jest odróżnialna od relacji pochodzącej z DDL.
- Oryginalne pliki są identyczne przed zatwierdzeniem i po nim.
- Zatwierdzona relacja jest dostępna dla S7 do osobnego sprawdzenia,
  także jeśli przyszły próbny import sam w sobie zakończy się powodzeniem.
  Rzeczywisty test danych z AC-34 pozostaje w S7.
- Nowa wersja DDL nie dziedziczy zatwierdzenia. Nierozpatrzona propozycja
  blokuje start zgodnie ze wspólną regułą przeglądu; po rozpatrzeniu
  wszystkich znikają tylko blokady tego przeglądu, nie inne przeszkody.
- Zmiana schematu i decyzji dla nowej wersji nie zmienia wcześniejszego
  przypięcia wymagań rozpoczętego wykonania.

**Do wyjaśnienia:** źródło i moment powstawania propozycji, format relacji
i operacje API, sprawdzenie istnienia i zgodności wskazanych kolumn,
semantyka NULL i kluczy złożonych dla relacji spoza DDL, zapis decyzji
oraz wspólny kontrakt przeglądu i przekazania do S6/S7.
Komendy zależą od S1; testów nie wykonano.

#### S2-T6 — Dodać interfejs projektów, wgrywania DDL i podglądu analizy

**Status opisu:** częściowo uzgodniony szkic, **do wyjaśnienia**.
**Story nadrzędne:** S2 — Zapisane projekty i rozpoznawanie schematu.
**Cel:** użytkownik tworzy i wybiera projekt, wgrywa schemat i rozumie
wynik jego analizy, bez mylenia zapisu plików z gotowością do generowania.
**Źródło:** sekcja 5.1 specyfikacji, REQ-003, REQ-009–REQ-014,
AC-01–AC-05 oraz uzgodnienia S2 dotyczące paczek i analizy w tle.
**Punkt startowy:** docelowy katalog `apps/web/`, do utworzenia w S1.
Przy sporządzaniu tego szkicu katalog aplikacji nadal nie istnieje.
Nie wybrano w tym opisie układu ekranów ani nazw komponentów.
**Zależności:** fundament frontendu i konfiguracja S1; odpowiednie
kontrakty operacji S2-T1–T5. Backendowej walidacji nie zastępować
wyłącznie sprawdzeniem w przeglądarce.

**Co należy zrobić po doprecyzowaniu kontraktów i interfejsu:**
1. Udostępnić tworzenie i wybór zapisanych projektów zgodnie z S2-T1:
   nazwa i opcjonalny opis, bez zamkniętej listy branż. Projekt bez DDL
   pozostaje dostępny, ale nie jest gotowy do generowania.
2. Dodać wspólne wysłanie jednego lub wielu plików SQL i możliwość
   ustawienia ich kolejności przed wysłaniem. W MVP poprawka wymaga
   ponownego wysłania pełnej paczki, bez podmiany pojedynczego pliku.
   Przed wysłaniem utworzyć unikalny identyfikator próby; po utracie
   odpowiedzi sprawdzić po nim wynik w backendzie bez ponownego uploadu.
   Przy nadal nieznanym wyniku zablokować ponowne wysłanie tej paczki
   do ustalenia wyniku i pokazać „Sprawdź ponownie”; akcja tylko
   sprawdza wynik tej samej próby.
   Po odebraniu komunikatu o roboczym zapisie automatycznie potwierdzić
   jego odbiór backendowi; dopiero to pozwala uruchomić analizę.
   Nie dodawać osobnego przycisku zatwierdzenia zapisu.
   Już od rozpoczęcia wysyłania paczki oraz podczas analizy zablokować
   wgrywanie DDL we wszystkich projektach i innych kartach przeglądarki;
   nie przedstawiać kolejnego wysłania jako oczekującego w kolejce.
   Dla HTTP `409` z kodem `DDL_PROCESSING_IN_PROGRESS` pokazać
   „Trwa przesyłanie lub analiza DDL. Poczekaj na zakończenie”.
   Zachować blokadę wgrywania także podczas oczekiwania na automatyczne
   ponowienie analizy po awarii.
   Podczas przesyłania ostrzec przed odświeżeniem lub zamknięciem
   strony/aplikacji o anulowaniu transferu, z uwzględnieniem ograniczeń
   z sekcji 11.1 specyfikacji. Pozostanie na stronie nie anuluje transferu.
3. Rozróżnić potwierdzenie zapisu plików, stan analizy w tle
   i odrzucenie paczki podczas wstępnego sprawdzenia. W tym ostatnim
   przypadku pokazać razem wykryte błędy kodowania, pustych plików
   i konfliktów nazw. Rozróżnić też stan analizy
   i gotowość schematu do generowania. Pokazać diagnostykę z oryginalnym
   plikiem i wierszem, gdy można wskazać lokalizację; nie wymyślać jej
   dla problemów dotyczących całej paczki.
   Po wyczerpaniu trzech automatycznych ponowień po awarii wskazać
   konieczność ponownego wgrania całej paczki, bez przycisku ręcznego
   ponowienia analizy zapisanych plików.
   Nie wiązać anulowania rozpoczętej analizy przyjętej paczki
   z samym odświeżeniem lub zamknięciem strony.
4. Dodać ręczne przerwanie analizy poprzedzone potwierdzeniem
   z ostrzeżeniem o usunięciu jej plików i częściowego wyniku.
   Rezygnacja nie przerywa pracy. Kolejny DDL w tym samym projekcie
   można wysłać po zatrzymaniu poprzedniej analizy.
5. Udostępnić podgląd rozpoznanych tabel, ograniczeń i relacji,
   rozróżniając relacje z DDL od propozycji wymagających zatwierdzenia.
   Po zmianie schematu wcześniejsze reguły i relacje pokazać do ponownego
   przeglądu. Bez ich rozpatrzenia nie przedstawiać projektu jako gotowego
   do generowania. Nie implementować w tym zadaniu interpretacji reguł S3.

**Poza zakresem:** parser, magazyn plików, uruchamianie analizy
i sprzątanie danych po stronie backendu, właściwa interpretacja reguł,
generowanie danych, historia czatów i podmiana jednego pliku po MVP.

**Kryteria i plan ręcznej weryfikacji po implementacji:**
- Utworzyć projekt bankowy i sklepowy bez DDL; oba można ponownie wybrać.
- Wybrać wiele plików, zmienić kolejność, wysłać i porównać ją
  z kolejnością zapisaną przez backend.
- Opóźnić analizę: interfejs odróżnia zapis paczki od jej przeanalizowania.
- Wywołać błąd w drugim pliku: diagnostyka odnosi się do tego pliku.
- Wysłać paczkę z kilkoma różnymi problemami wstępnego sprawdzenia:
  interfejs pokazuje razem wykryte błędy, nie tylko pierwszy.
- Po utracie odpowiedzi i przy niedostępnym odczycie wyniku sprawdzić
  blokadę ponownego wysłania i akcję „Sprawdź ponownie”. Akcja nie
  przesyła plików ani nie tworzy nowej próby.
- Wybrać przerwanie i zrezygnować: analiza trwa, dane nie są usuwane.
  Powtórzyć z potwierdzeniem: po zatrzymaniu pliki i częściowy wynik
  są usuwane, wcześniejszy schemat pozostaje bez zmian.
- Po zmianie schematu sprawdzić blokadę gotowości przy nierozpatrzonych
  propozycjach reguł i relacji. Sprawdzić podgląd schematu kilkuset tabel.
To plan sprawdzeń, nie wykonane testy ani zatwierdzony projekt wizualny.

**Do wyjaśnienia:** układ i nawigacja ekranów, dokładna prezentacja
stanów i błędów, kontrakty S2-T2–T5, dane podglądu, wygodna obsługa
kilkuset tabel, techniczne rozpoznawanie wyniku wysłania po utracie
odpowiedzi, narzędzia i komendy testów interfejsu z S1.

### S3 — Reguły biznesowe i ich zatwierdzanie

**Cel i rezultat:** wymagania tekstowe mają jawne znaczenie i wiadomo,
co aplikacja potrafi automatycznie sprawdzić.

**Zakres:** wprowadzanie reguł i wskazówek jakościowych, propozycja
interpretacji, doprecyzowania, wykryte konflikty i zatwierdzanie znaczenia
sprawdzenia. Obejmuje definicję ograniczonej reguły sumującej dane między
tabelami z REQ-071.

**Poza zakresem:** wykonywanie dowolnego kodu modelu, automatyczna ocena
realizmu i obsługa każdej możliwej reguły tekstowej.

**Źródła:** REQ-015–REQ-019, REQ-071; AC-06–AC-08 i AC-33.

**Powiązania:** S2 oraz operacje interpretacji z S5. Tutaj definiujemy
i zatwierdzamy znaczenie reguły; jej sprawdzenie na danych należy do S7.

**Do wyjaśnienia:** katalog, reprezentacja i organizacja reguł projektu
oraz zlecenia (OD-06). Dla reguły sumującej obowiązuje zaokrąglenie
wartości każdej pozycji przed sumowaniem; pozostałe szczegóły obliczeń
nie są domyślnie rozstrzygnięte.

### S4 — Czat i przygotowanie zatwierdzonego zlecenia

**Cel i rezultat:** polecenie użytkownika prowadzi do jednoznacznego,
zatwierdzonego planu danych przed rozpoczęciem generowania.

**Zakres:** główny widok czatu, wybór projektu, kolejne polecenia,
pytania doprecyzowujące, propozycja potrzebnych tabel i liczebności,
wybór SQL `INSERT` albo CSV oraz zatwierdzenie wymagań. Przygotowanie
prośby o zmianę otrzymanej paczki bez zmiany wymagań wcześniejszego wyniku.

**Poza zakresem:** historia rozmów i rozpoczynanie generowania
bez wymaganych zatwierdzeń.

**Źródła:** REQ-020–REQ-026, REQ-043, REQ-073, REQ-076;
AC-09–AC-10, AC-39 i AC-42.

**Powiązania:** S2, S3 i interpretacja z S5. Cykl dostępności czatu
należy do S9, a sterowanie zatwierdzonym wykonaniem do S6.

**Do wyjaśnienia:** szczegóły interakcji, zmiana projektu podczas
rozmowy oraz powiązanie prośby ze zleceniem i wykonaniem (OD-10, OD-12).

### S5 — Integracja modeli i przygotowywanie paczek danych

**Cel i rezultat:** wymienny wariant dużego modelu językowego (LLM)
interpretuje wymagania, przygotowuje i modyfikuje gotowy SQL/CSV.

**Zakres:** granica komunikacji z modelami, przygotowanie kontekstu,
prompty, wyodrębnienie plików, generowanie, poprawianie naruszeń
i zmiana istniejącej paczki na polecenie użytkownika. Dostarczanie
rzeczywistych informacji o wariancie i dostępnych pomiarach.

**Poza zakresem:** wybór zwycięskiego modelu, platforma eksperymentów,
obowiązkowe wyszukiwanie kontekstu za pomocą embeddingów i zastępowanie
wyniku modelu własnym SQL/CSV generowanym z pośrednich rekordów.

**Źródła:** REQ-035–REQ-036, REQ-060–REQ-065, REQ-068, REQ-076.

**Powiązania:** kontrakty S2–S4. Generator dostarcza kandydata i pomiary;
nie ustala limitu napraw ani sukcesu zadania. Te decyzje należą do S6.
Przy zmianie danych punktem wyjścia jest otrzymana paczka, nie niezależny
nowy zestaw.

**Do wyjaśnienia:** profile plików, przekazanie paczki i ograniczenia
kontekstu (OD-04, OD-10). Wybrane zależności wymagają weryfikacji przed
przyjęciem; kierunek LiteLLM nie jest zatwierdzeniem konkretnej wersji.

### S6 — Sterowanie wykonaniem, naprawy i przerwania

**Cel i rezultat:** proces ma kontrolowany przebieg i kończy się zgodnie
z rzeczywistym wynikiem.

**Zakres:** niezmienne wymagania wykonania, etapy i statusy, limit rund
dla każdej prośby, ochrona najnowszego użytecznego kandydata, anulowanie,
błędy techniczne i ręczne nowe wykonanie. Jednorazowa dodatkowa seria
napraw po nieudanej zmianie paczki.

Domyślnie pierwszemu kandydatowi mogą towarzyszyć najwyżej 3 automatyczne
rundy naprawcze. Dodatkową serię do 3 rund użytkownik zleca najwyżej raz
dla danej nieudanej prośby o zmianę istniejących danych. Jej wejściem jest
ostatni nieudany kandydat i jego błędy, nie poprzednia sprawdzona paczka.
Po nieudanym pierwszym generowaniu bez użytecznej paczki akcja dodatkowej
serii nie jest dostępna. Niepowodzenie modyfikacji nie usuwa poprzedniej
sprawdzonej paczki ani jej raportu i nie zalicza nowej prośby.

**Poza zakresem:** automatyczne techniczne ponowienia, przełączanie
modelu po awarii, wznawianie procesu i ranking jakości kandydatów.

**Źródła:** REQ-026–REQ-042, REQ-059, REQ-069–REQ-070,
REQ-078–REQ-079; sekcje 8–9 specyfikacji.

**Powiązania:** kontrakty S5 i S7; raport i odbiór wyniku w S8.
S9 przekazuje informację o opuszczeniu czatu, a S6 obsługuje anulowanie
wykonania. Użyteczny kandydat to paczka spełniająca kompletność,
importowalność i wszystkie obowiązujące relacje, niekoniecznie wszystkie
dodatkowe reguły biznesowe.

**Do wyjaśnienia:** timeouty, potwierdzenie anulowania i powiązanie
dodatkowej serii z wykonaniem oraz licznikami (OD-07–OD-10).

### S7 — Walidacja paczki i rzeczywisty próbny import

**Cel i rezultat:** ocena danych wynika z wykonanych sprawdzeń,
a nie deklaracji modelu.

**Zakres:** cztery etapy walidacji: składnia i format; wstępna zgodność
ze schematem i typami; rzeczywisty próbny import do odizolowanego
PostgreSQL wraz ze sprawdzeniem relacji i kompletności; dodatkowe reguły.
Wyniki i przykłady naruszeń są przypisane do konkretnego kandydata.

Relacje zatwierdzone poza DDL są osobnym obowiązkowym sprawdzeniem:
ich naruszenie blokuje sukces mimo udanego importu, ale nie zmienia
wyniku tego importu ani oryginalnego DDL.

**Poza zakresem:** ciche poprawianie danych, zmiana DDL dla uzyskania
sukcesu i uznawanie niewykonanego sprawdzenia za pozytywne.

**Źródła:** REQ-012, REQ-027–REQ-031, REQ-048–REQ-051,
REQ-071; AC-11–AC-15, AC-33–AC-34 i AC-37.

**Powiązania:** S2, zatwierdzone definicje S3 i wspólny profil plików
z S5 oraz S8. Walidator dostarcza wyniki sprawdzeń; S6 decyduje
o dalszej pracy lub zakończeniu.

**Do wyjaśnienia:** macierz PostgreSQL, izolacja próbnego importu,
profile plików i dokładne wykonywanie reguł (OD-01, OD-02, OD-04, OD-06).

### S8 — Wynik, raport i pobieranie plików

**Cel i rezultat:** użytkownik otrzymuje właściwą paczkę wraz z raportem
dotyczącym dokładnie tych danych.

**Zakres:** prezentacja wyniku, raport możliwy do automatycznego odczytu,
dostępne pomiary oraz pobieranie SQL lub paczki CSV z informacją
o przypisaniu plików do tabel i kolejności importu. Pobieranie zachowanego
wyniku po przerwaniu oraz oznaczenie poprzedniej wersji po nieudanej zmianie.

**Poza zakresem:** archiwum wyników, panel badawczy, zbiorcza punktacja
jakości i ponowna generacja podczas pobierania.

**Źródła:** REQ-008, REQ-039–REQ-040, REQ-043–REQ-051,
REQ-062–REQ-065, REQ-078.

**Powiązania:** S5–S7. Pliki i raport dotyczą tego samego kandydata;
pakowanie nie zmienia sprawdzonych danych. Brak dostępnego pomiaru
nie jest zerem. Pobranie paczki po anulowaniu lub awarii nie zmienia
statusu całego wykonania i jest możliwe tylko w nadal dostępnym czacie.

**Do wyjaśnienia:** dokładny profil eksportu i minimum raportu
(OD-04–OD-05), a także dostępność częściowych lub niesprawdzonych
artefaktów (OD-08).

### S9 — Cykl życia czatu i danych roboczych

**Cel i rezultat:** zakończenie rozmowy kończy dostęp do jej danych
i uruchamia anulowanie pracy nad porzuconym wynikiem.

**Zakres:** „Nowy czat”, odświeżenie, zamknięcie strony i aplikacji,
ostrzeżenie przed wyjściem, zakończenie dostępu do plików, przekazanie
anulowania oraz sprzątanie danych roboczych. Ochrona nowego czatu
przed spóźnioną odpowiedzią starego.

Rezygnacja z opuszczenia strony zachowuje rozmowę i nie anuluje
wykonania. Po rzeczywistym wyjściu nie przywracamy czatu ani jego plików.
Zapisane projekty pozostają. Ostrzeżenie podlega ograniczeniom
przeglądarki z sekcji 11.1 specyfikacji; nie obiecujemy jego działania
przy każdym wymuszonym zakończeniu procesu ani natychmiastowego
zatrzymania żądania obsługiwanego przez dostawcę LLM.

**Poza zakresem:** przywracanie rozmów i usuwanie plików wcześniej
pobranych na dysk użytkownika.

**Źródła:** REQ-072, REQ-074–REQ-075, REQ-077;
AC-38 i AC-40–AC-43.

**Powiązania:** S4, S6 i S8. S9 odpowiada za cykl rozmowy i przekazanie
anulowania; sterowanie wykonaniem pozostaje w S6.

**Do wyjaśnienia:** wykrywanie wyjścia, zakończenie dostępu, fizyczne
sprzątanie i potwierdzenie zatrzymania (OD-08–OD-09).

## 3. Zasady dalszego rozpisywania dla juniora

Użytkownik wymaga opisów zrozumiałych dla junior developera. Nie wystarczą
hasła „dodaj walidację”, „obsłuż błędy” lub „napisz testy”.

Każde zadanie i sensowne podzadanie ma wskazywać:

1. **Rodzica, cel i źródło:** stabilny identyfikator, mały rezultat,
   powód zmiany i konkretne wymagania.
2. **Punkt startowy:** sprawdzone istniejące moduły i pliki albo miejsce
   do utworzenia zgodne z uzgodnioną strukturą. Repozytorium nie ma jeszcze
   kodu aplikacji, więc nie przedstawiamy projektowanych ścieżek jako istniejących.
3. **Zakres pracy:** konkretne czynności w kolejności wykonania,
   oczekiwane zachowanie i istotne przypadki błędne lub brzegowe.
4. **Granice:** czego nie zmieniać i jakie inne zadania odpowiadają
   za sąsiedni zakres.
5. **Zależności i decyzje:** co musi być gotowe; brakujący kontrakt
   lub reguła oznacza „do wyjaśnienia”, nie wybór pozostawiony juniorowi.
6. **Kryteria ukończenia:** obserwowalne wyniki, także dla istotnego
   przypadku niepoprawnego. Samo istnienie pliku nie potwierdza poprawności.
7. **Sprawdzenie:** konkretne testy z oczekiwanym wynikiem, sprawdzone
   komendy bieżącego projektu i kroki ręcznego odbioru przez użytkownika,
   odpowiednio do zakresu. Planowanych testów nie opisujemy jako wykonanych.

Szczegóły opisujemy na podstawie
[standardu zadań dla juniora](../.agents/skills/github-work-planner/references/junior-task-writing.md).
Ten standard nie uzupełnia brakujących wymagań ani nie wybiera technologii.

Najpierw uzgadniamy listę zadań jednego story, dopiero potem rozwijamy
zaakceptowane zadania na podzadania. Drobne czynności bez osobnego
sprawdzalnego rezultatu pozostają krokami, nie osobnymi elementami backlogu.
Rodzic grupuje pracę dzieci, zamiast ponownie zlecać tę samą implementację.
Testy konkretnej funkcji i potrzebny jej interfejs należą do jej zakresu,
nie do osobnego końcowego etapu.

Przy rozpisywaniu danego obszaru sprawdzamy pokrycie jego REQ i AC,
brak dublowania pracy oraz wykonalną kolejność. Powtórzenie identyfikatora
w kilku story oznacza współpracę, nie wielokrotną implementację tej samej
funkcji. Wymagania i kryteria jawnie odłożone poza MVP nie stają się zadaniami.
Badania pozostają osobnym rezultatem.

## 4. Weryfikacja przed późniejszą publikacją

Sprawdzono listy Projects kont `jwieczor03` i `jakwiecz` oraz projekty
powiązane z repozytorium: brak istniejących tablic.

Przeczytano treść wszystkich sześciu istniejących issues:

- #1: przestrzeń na luźne pomysły;
- #2: kryteria wyboru modeli do badań;
- #3: instalacja Ollamy i próba modelu lokalnego;
- #4: przygotowanie środowiska Python;
- #5: PoC generowania JSON;
- #6: PoC walidacji odpowiedzi przez Pydantic.

Nie są odpowiednikami nadrzędnych story S1–S9. Część tematów może być
powiązana z przyszłymi zadaniami, ale nie przesądza to ich ponownego użycia,
zgodności z obecnym MVP ani statusu wykonania. Nie zmieniono tych issues.

## 5. Punkt kontynuacji i dostęp

**Bieżący etap:** etap 3 — szczegółowa analiza S2 i wyjaśnienie decyzji
przed zaproponowaniem zadań. Użytkownik zlecił przygotowanie opisów zadań
tego obszaru. Publikacja na GitHubie jest odłożona na później.

GitHub CLI jest uwierzytelnione jako `jakwiecz`. To konto ma uprawnienie
`WRITE` do repozytorium, ale uzgodniony właściciel nowego Project to inne
konto osobiste: `jwieczor03`.

Użytkownik zatwierdził dodanie `read:project`; odczyt Projects działa.
Nie uzyskano jeszcze zakresu zapisu `project` ani nie uzgodniono
autoryzacji konta właściciela lub zmiany właściciela tablicy.

**Zakończono wcześniej:** analizę całej specyfikacji, uzgodnienie mapy
S1–S9, porównanie wcześniejszych issues oraz zapis pełnych opisów story
i standardu dalszych zadań. Nie rozpisano technicznych zadań i podzadań.

**Kontynuacja 14 listopada 2026 — S1:** sprawdzono stan repozytorium
(nadal brak kodu aplikacji i konfiguracji uruchomienia lub testów),
wymagania S1 z sekcji 4, 11 i 13 specyfikacji, rejestr ustaleń,
podział implementacji, opis serwisów oraz przygotowanie do hostowania.
Przejrzano także propozycje struktury, portów, konfiguracji i lokalnego
dostępu w ogólnym LLD. Nie wykonywano pełnego przeglądu szczegółowych
kontraktów API, modelu danych ani cyklu wykonania.

**Decyzja użytkownika w rozmowie o S1:** zatwierdzono Python/FastAPI
+ React/TypeScript do implementacji MVP. Zakres tej akceptacji zapisano
w rejestrze ustaleń i doprecyzowano w opisie serwisów.

**Kolejna decyzja użytkownika w rozmowie o S1:** zatwierdzono trzy
osobno uruchamiane serwisy backendowe: zarządzanie (`application-api`),
generowanie (`generation-service`) i walidację (`validation-service`).
Nie oznacza to akceptacji szczegółowych kontraktów ani sposobu uruchomienia.

**Kolejna decyzja użytkownika w rozmowie o S1:** zatwierdzono Docker
Compose jako podstawowy sposób lokalnego uruchamiania trzech serwisów
backendowych i potrzebnych baz. Wersje obrazów i organizacja izolowanego
środowiska próbnego importu (OD-02) pozostają otwarte; decyzja nie obejmuje
sposobu uruchamiania frontendu ani lokalnego modelu.

**Kolejna decyzja użytkownika w rozmowie o S1:** zatwierdzono HTTP
+ JSON oraz opis API w OpenAPI dla komunikacji między serwisami,
bez akceptacji endpointów, pól, timeoutów, bibliotek i zabezpieczeń.

**Do wyjaśnienia:** szczegóły kontraktów i konfiguracji, biblioteki
pomocnicze, narzędzia jakości oraz wersje pozostają propozycjami. Nie należy
wpisywać ich do zadań jako zaakceptowanych decyzji.

**Decyzja użytkownika:** zaakceptowano podział S1-T1–S1-T8
zapisany w sekcji S1, z rezultatami, granicami i jawnymi brakami.
Akceptacja podziału nie zatwierdza otwartych rozwiązań.

**Bieżący element w rozmowie o S1:** przygotowano opis S1-T1
do przeglądu oraz szkice S1-T2–S1-T9 z jawnymi blokadami w sekcji S1.
Nie są jeszcze zaakceptowanymi instrukcjami całego obszaru.
Zatwierdzono osobne
`.env` poza Git i wersjonowane `.env.example` dla trzech backendów.
Zatwierdzono pierwszeństwo zmiennych środowiskowych procesu lub kontenera
przed wartościami z `.env` oraz Pydantic Settings do odczytu i walidacji
konfiguracji we wszystkich trzech backendach. Zastosowanie zmian
konfiguracji wymaga restartu danego serwisu; bez automatycznego
przeładowania `.env`. W S1-T4 zatwierdzono SQLAlchemy i Psycopg do bazy
aplikacji w `application-api` oraz Alembic do jej migracji.
Zatwierdzono automatyczne uruchamianie migracji przy starcie
`application-api`, poza health checkami. Błąd migracji pozostawia serwis
w trybie diagnostycznym z przyczyną i blokadą funkcji wymagających bazy.
Zatwierdzono wykonywanie migracji wyłącznie w fazie startu serwisu;
ponowienie po błędzie wymaga restartu. Pozostałe decyzje S1-T4 obejmują
ochronę przed równoczesnym wykonaniem oraz tryb połączeń i transakcji.
Nie rozpoczęto implementacji ani tworzenia plików aplikacji.

**Decyzja użytkownika dotycząca S1-T1:** zatwierdzono jeden wspólny układ
obecnego repozytorium z frontendem w `apps/web/` i backendami
w `services/application-api/`, `services/generation-service/`
oraz `services/validation-service/`. Decyzję zapisano w rejestrze ustaleń
i przy strukturze ogólnego LLD. Nie zatwierdza ona wewnętrznego drzewa
modułów ani sposobu zarządzania zależnościami.

**Kolejna decyzja użytkownika dotycząca S1-T1:** po wyjaśnieniu ról
narzędzi zatwierdzono React + TypeScript + Vite, z npm do zarządzania
pakietami i uruchamiania poleceń. React nie jest zastępowany przez Vite,
a npm nie zastępuje żadnego z tych narzędzi. Decyzję zapisano w rejestrze
ustaleń i opisie serwisów. Nie obejmuje Mantine, TanStack Query, wersji
Node.js i pakietów ani sposobu podawania zbudowanego frontendu.

**Kolejna decyzja użytkownika dotycząca S1-T1:** zatwierdzono uv
do zarządzania zależnościami i środowiskami backendów Python. Nie oznacza
to akceptacji wspólnego workspace, osobnych plików blokad ani konkretnych
wersji. Decyzję zapisano w rejestrze ustaleń i opisie serwisów.

**Kolejna decyzja użytkownika dotycząca S1-T1:** zatwierdzono osobny
projekt uv dla każdego z trzech backendów, z własnymi deklaracjami
zależności, plikiem blokady wersji i środowiskiem wirtualnym, zamiast
wspólnego workspace. Decyzję zapisano także w rejestrze ustaleń
i opisie serwisów.

**Kolejna decyzja użytkownika dotycząca S1-T1:** zatwierdzono Python 3.14
jako bazową linię dla wszystkich trzech backendów. Dokładne wydanie
poprawkowe przypniemy po przeglądzie i próbie zgodności wybranych
zależności. Decyzję zapisano w rejestrze ustaleń i opisie serwisów.
Nie wykonano próby zgodności całego zestawu bibliotek.

**Kolejna decyzja użytkownika dotycząca S1-T1:** zatwierdzono Node.js 26
LTS jako bazową linię środowiska narzędziowego frontendu. Decyzję zapisano
w rejestrze ustaleń i opisie serwisów. Dokładne wersje Node.js, npm
i bibliotek pozostają do przypięcia oraz sprawdzenia zgodności;
nie wykonano instalacji ani próby uruchomienia.

**Kolejna decyzja użytkownika dotycząca S1:** zatwierdzono udostępnianie
zbudowanego frontendu przez `application-api` pod jednym lokalnym
adresem z API. Osobny serwer Vite służy tylko do developmentu;
podstawowe korzystanie z aplikacji nie wymaga osobnego serwera frontendu.
Decyzję zapisano w rejestrze ustaleń, opisie serwisów i ogólnym LLD.
Wpływa na S1-T1, S1-T3 i S1-T8; nie zatwierdza konkretnych tras i portów
ani szczegółowej konfiguracji dostępu.

**Kolejna decyzja użytkownika dotycząca S1-T1:** zatwierdzono Uvicorn
jako serwer uruchamiający każdą z trzech aplikacji FastAPI. Decyzję
zapisano w rejestrze ustaleń i opisie serwisów. Konkretna wersja,
wariant instalacji oraz parametry wymagają doprecyzowania i sprawdzenia
zgodności; nie zainstalowano ani nie uruchomiono serwera.

**Kolejna decyzja użytkownika dotycząca S1-T1:** zatwierdzono
`GET /health/live` w każdym backendzie: HTTP 200 i JSON `{"status":"ok"}`,
bez wywołań LLM, sprawdzania baz i magazynów oraz ujawniania konfiguracji.
Odpowiedź potwierdza obsłużenie żądania przez proces, nie gotowość
do generowania lub walidacji. Nie zastępuje proponowanego
`GET /internal/v1/health/ready` z sekcji 4 kontraktów API ani nie zatwierdza
mechanizmu identyfikacji instancji, zabezpieczeń i ekspozycji usług w sieci.
Decyzję zapisano w rejestrze ustaleń, opisie serwisów i kontraktach API.
Nie zaimplementowano ani nie przetestowano endpointu.

**Kolejna decyzja użytkownika dotycząca S1:** zatwierdzono pytest
jako narzędzie testów automatycznych wszystkich trzech backendów.
Dotyczy testów szkieletów w S1-T1 i wspólnych zasad konfiguracji w S1-T7.
Konkretna wersja, dodatkowe biblioteki i wtyczki pozostają otwarte.
Decyzję zapisano w rejestrze ustaleń i opisie serwisów.
Nie zainstalowano narzędzia ani nie wykonano testów aplikacji.

**Kolejna decyzja użytkownika dotycząca S1-T1:** zatwierdzono prosty
ekran techniczny frontendu z nazwą aplikacji i informacją
„Szkielet aplikacji”, bez czatu, formularzy i logiki biznesowej.
Sprawdzenie połączenia z API pozostaje w S1-T8. Nie jest to projekt
docelowego interfejsu ani rozstrzygnięcie OD-12. Decyzję zapisano
w rejestrze ustaleń i opisie serwisów; nie wykonano implementacji.

**Kolejna decyzja użytkownika dotycząca S1-T1:** zatwierdzono minimalną
wewnętrzną strukturę każdego backendu: kod w `src/<pakiet>/`,
utworzenie aplikacji FastAPI i obsługę health w `bootstrap.py`,
test kontraktu w lokalnym `tests/test_health.py`, bez pustych warstw
domeny i adapterów. Nazwy pakietów: `application_api`,
`generation_service` i `validation_service`.
Decyzję zapisano w rejestrze ustaleń i strukturze LLD.
Nie zatwierdzono całego drzewa LLD ani nie utworzono plików aplikacji.

**Kolejna decyzja użytkownika dotycząca S1-T1:** zatwierdzono dla
bezpośredniego uruchomienia deweloperskiego poza Compose domyślne porty: `application-api`
8000, `generation-service` 8001, `validation-service` 8002 i Vite 5173,
wszystkie na `127.0.0.1`. To ustalenie lokalnego sposobu weryfikacji
szkieletów, nie decyzja o publikacji portów kontenerów, sieci Compose
ani konfiguracji przekazywania żądań przez Vite. Decyzję zapisano
w rejestrze ustaleń i opisie serwisów. Nie sprawdzono uruchomienia
ani dostępności portów.

**Kolejna decyzja użytkownika dotycząca S1-T1:** szkielety mają
uruchamiać się i udostępniać health bez działających baz, magazynu
plików, Ollamy i kluczy dostawców LLM. To granica odbioru
fundamentu, nie tryb pozorujący gotowość funkcji biznesowych.
Integracje i wymagania ich konfiguracji pozostają w odpowiednich
zadaniach; decyzja nie wprowadza atrap odpowiedzi biznesowych.
Decyzję zapisano w rejestrze ustaleń i opisie serwisów.
Nie wykonano implementacji ani sprawdzenia uruchomienia.

**Kolejna decyzja użytkownika dotycząca S1-T1:** dobór i przypięcie dokładnych
wersji zaakceptowanych narzędzi oraz ich wymaganych zależności
powierzono deweloperowi w pierwszym kroku S1-T1, po przeglądzie
oficjalnej dokumentacji i próbie zgodności przez instalację i testy.
Uzgodnione granice:
bez zmiany stosu, Python 3.14 i Node.js 26 LTS pozostają obowiązujące,
a konflikt wymagający ich zmiany wraca do użytkownika przed zmianą.
Nie oznacza to zgody na dobieranie nowych opcjonalnych narzędzi.
Decyzję zapisano w rejestrze ustaleń i opisie serwisów.
W tej konsultacji nie wybrano wersji ani nie rozpoczęto implementacji.

**Kolejna decyzja użytkownika dotycząca S1:** zatwierdzono rozdział adresów
w `application-api`: frontend od `/`, publiczne operacje biznesowe
pod `/api/v1`, a uzgodniony `/health/live` jako osobną trasę techniczną.
To akceptacja rozdziału tras, nie wszystkich operacji i pól z kontraktów ani rozwiązania
obsługi brakujących zasobów, tras interfejsu i proxy Vite.
Decyzję zapisano w rejestrze ustaleń, opisie serwisów i kontraktach API.
Nie zaimplementowano ani nie przetestowano tras.

**Kolejna decyzja użytkownika dotycząca S1:** nieznany adres pod `/api/v1`
ma zwracać HTTP 404 z odpowiedzią JSON, nigdy stronę HTML frontendu.
Chroni to granicę API przed przejęciem błędnych adresów przez mechanizm
podawania interfejsu. Nie ustala wspólnego formatu błędów ani obsługi
brakujących plików i pozostałych tras. Decyzję zapisano w rejestrze
ustaleń, opisie serwisów i kontraktach API. Nie wykonano implementacji
ani testu tego zachowania.

**Kolejna decyzja użytkownika dotycząca S1:** w development Vite ma
przekazywać żądania `/api/v1` i `/health/live` do `application-api`
na `http://127.0.0.1:8000`, bez zmiany ścieżek, a frontend korzystać
z adresów względnych. To uzgodniony sposób adresowania
backendu z interfejsu podczas developmentu i zwykłego użycia.
Przeglądarka nie wywołuje bezpośrednio generatora ani walidatora.
Proxy nie udostępnia wewnętrznego API. Obsługę `server.proxy` potwierdzono
w oficjalnej dokumentacji Vite 14 listopada 2026:
`https://vite.dev/config/server-options.html#server-proxy`.
Decyzję zapisano w rejestrze ustaleń i opisie serwisów.
Nie wykonano konfiguracji ani testu połączenia.

**Kolejna decyzja użytkownika dotycząca S1-T1:** w początkowym szkielecie
ekran startowy jest dostępny pod `/`, a nieznane adresy stron
i brakujące pliki mają zwracać HTTP 404 zamiast strony startowej.
To minimalny zakres routingu S1-T1, bez dodawania obsługi wielu ekranów
na zapas. Nie rozstrzyga docelowej nawigacji MVP.
Decyzję zapisano w rejestrze ustaleń, opisie serwisów i kontraktach API.
Nie wykonano implementacji ani testów.

**Wcześniejsza decyzja użytkownika dotycząca S1-T2 — zastąpiona
poniższą decyzją o trybie diagnostycznym:** brak lub błędna wartość
wymaganej konfiguracji blokuje start danego serwisu z czytelnym
komunikatem bez ujawniania wartości sekretów. Dotyczy konfiguracji
wymaganej dla uruchamianego zakresu, nie klucza niewykorzystywanego
dostawcy. Decyzję zapisano w rejestrze ustaleń i opisie serwisów.

**Dodatkowe wymaganie użytkownika:** przy uruchamianiu mają być
przeprowadzane sprawdzenia serwisów i połączeń, aby wiadomo było,
które części działają. Podział odpowiedzialności zatwierdzono poniżej.
Do wyjaśnienia: szczegółowa lista połączeń, kontrakt gotowości,
prezentacja wyników, limity czasu i reakcja na błąd
dostępności. Trzeba także uzgodnić wpływ na wcześniejszy niezależny
start szkieletów S1-T1. Nie zmieniono kontraktu `/health/live`
ani nie przyjęto domyślnie płatnych wywołań LLM.
Nie wykonano implementacji ani testów.

**Kolejna decyzja użytkownika dotycząca diagnostyki startu:** zatwierdzono
podział, w którym każdy backend sprawdza własne bezpośrednie zależności,
a `application-api` zbiera ich statusy i własne wyniki w obraz całości,
zamiast sprawdzania wszystkich przez wszystkich.
Nie wprowadzamy rekurencyjnego pobierania zbiorczego statusu.
Szczegółowy mechanizm i kontrakt pozostają otwarte.
Decyzję zapisano w rejestrze ustaleń i opisie serwisów.
Nie wykonano implementacji ani sprawdzeń połączeń.

**Kolejna decyzja użytkownika — reakcja na niedostępność:**
przy poprawnej wymaganej konfiguracji proces ma pozostać uruchomiony,
gdy zależność nie odpowiada, udostępniać diagnostykę braku gotowości
i nie dopuszczać operacji wymagających tej zależności, zamiast kończyć
proces. Nie wprowadza to ponawiania generowania ani walidacji.
Późniejsza decyzja o trybie diagnostycznym opisana poniżej obejmuje
również brakującą lub błędną wymaganą konfigurację.
Podstawa rozróżnienia działania procesu i gotowości: oficjalna
dokumentacja Kubernetes o sondach liveness i readiness, sprawdzona
14 listopada 2026. To odniesienie do zasady, nie wybór Kubernetes:
`https://kubernetes.io/docs/concepts/workloads/pods/probes/`.

**Rozszerzenie wymagania przez użytkownika — diagnostyka operacyjna:**
- Health check każdego serwisu sprawdza poprawność jego uruchomienia,
  wymagane zmienne środowiskowe i sekrety, poprawność połączeń do
  wykorzystywanych zewnętrznych API oraz istnienie i dostęp do wymaganych
  zasobów wewnętrznych.
- Raport rozróżnia zdolność do działania, częściową zdolność i całkowity
  brak zdolności; wyjaśnia przyczyny i ograniczenia bez ujawniania sekretów.
- Jeden wspólny mechanizm ma regularnie wywoływać health checki serwisów
  i zbierać wyniki także po uruchomieniu. Zachowano wcześniejszy podział:
  własne zależności w serwisie, agregacja w `application-api`.
- Do uzgodnienia pozostają katalog konkretnych prób, kontrakt i ochrona
  raportu, limity czasu, świeżość wyników oraz obsługa
  awarii samego monitora. Niezależność monitora zatwierdzono poniżej.
  Nie zatwierdzono płatnych prób LLM.
- Zakres zapisano w rejestrze ustaleń, opisie serwisów i kontraktach API.
  Nie wykonano implementacji ani testów.

**Zatwierdzona zmiana w S1-T2 — tryb diagnostyczny:**
brakujące zmienne lub sekrety oraz błędna wymagana konfiguracja nie
zatrzymują samej diagnostyki. Serwis udostępnia health check z przyczynami
braku lub ograniczenia gotowości i blokuje operacje biznesowe wymagające
tej konfiguracji. Użytkownik chce od razu otrzymywać informację o problemie,
bez debugowania. Decyzja zastępuje wcześniejszą zasadę kończenia procesu
przy takich brakach. Raport nadal nie ujawnia wartości sekretów.
Nie obiecujemy działania endpointu, jeśli nie można uruchomić samego
serwera diagnostyki. Obsługa takiej awarii i szczegóły etapowania
diagnostyki względem szkieletu S1-T1 pozostają otwarte.
Uzupełniono również sekcję 13.5 specyfikacji. Nie wykonano implementacji
ani testów.

**Zatwierdzona decyzja w S1 — niezależny proces monitora:**
wspólny monitor działa poza trzema backendami jako osobny proces.
Sprawdza także `application-api`, aby wykrywać jego zatrzymanie,
i nie polega wyłącznie na zbiorczym raporcie tego API.
Własne sprawdzenia zależności w backendach i uzgodniona agregacja
w `application-api` pozostają bez zmian. Zgoda dotyczy osobnego procesu,
nie wyboru narzędzia, technologii ani sposobu uruchomienia.
Nie oznacza odporności na awarię całego hosta ani wykrywania własnego
zatrzymania przez monitor. Nie wykonano implementacji ani testów.

**Zatwierdzona decyzja w S1 — osobny panel monitora:**
wyniki monitorowania są dostępne w osobnym panelu w przeglądarce,
działającym również przy niedostępnej głównej aplikacji.
Udostępnianie panelu i odczyt wyników nie mogą zależeć od działania
`application-api`. Nie wybrano technologii, wyglądu, adresu ani
zabezpieczeń panelu. Nie wykonano implementacji ani testów.
Warunek do późniejszej weryfikacji: po zatrzymaniu `application-api`
można nadal otworzyć panel i odczytać wynik monitorowania tego serwisu.

**Zatwierdzona decyzja w S1 — bezpłatna i niedestrukcyjna automatyczna
diagnostyka:** automatyczne health checki wykonują wyłącznie bezpłatne
i niedestrukcyjne próby. Sprawdzenia wymagające płatnego wywołania LLM
pozostają do ręcznego uruchomienia za zgodą użytkownika na daną próbę.
Nie ustalono konkretnych prób, mechanizmu ręcznego uruchomienia
ani potwierdzania kosztu. Nie wykonano implementacji, testów ani
płatnych wywołań.
Warunek do późniejszej weryfikacji: start serwisów i kolejne cykle
monitorowania nie uruchamiają płatnej operacji LLM; bez ręcznej akcji
i zgody użytkownika taka próba nie jest wykonywana.

**Zatwierdzona decyzja w S1 — harmonogram monitorowania:**
sprawdzenia odbywają się przy uruchamianiu, a następnie co 30 minut.
To częstotliwość kontroli, nie gwarantowany maksymalny czas wykrycia
awarii. Problem między kontrolami może pozostać niewykryty niemal
30 minut, powiększone o czas oczekiwania na odpowiedź.
Limity tego oczekiwania pozostają do uzgodnienia.
Warunek do późniejszej weryfikacji: kontrola startowa i kolejne kontrole
w odstępach 30 minut bez płatnych wywołań LLM. Test harmonogramu nie
wymaga rzeczywistego oczekiwania 30 minut; szczegóły testu dobierze
deweloper. Nie wykonano implementacji ani testów.

**Pozostałe kwestie diagnostyki S1:** katalog prób, kontrakt raportu,
limity czasu i świeżość wyników, zabezpieczenia panelu, technologia
monitora oraz obsługa awarii samego monitorowania pozostają otwarte.

**Zatwierdzona decyzja w S1 — przycisk „Sprawdź teraz”:**
panel monitora umożliwia uruchomienie nowej, bezpłatnej i niedestrukcyjnej
diagnostyki bez czekania na kolejną kontrolę okresową.
Nie jest to samo odświeżenie poprzedniego wyniku i nie uruchamia
płatnych prób LLM. Zatwierdzono brak wpływu ręcznej kontroli na
harmonogram automatyczny: nie przesuwa kolejnej kontroli i nie zeruje
odstępu 30 minut. Obsługa jednoczesnych kontroli pozostaje do uzgodnienia.
Warunek do późniejszej weryfikacji: po zmianie dostępności zależności
wybranie „Sprawdź teraz” wykonuje nowe sprawdzenie i udostępnia jego
wynik bez oczekiwania na kontrolę okresową, bez płatnego wywołania LLM.
Nie wykonano implementacji ani testów.

**Zatwierdzona decyzja w S1-T2 — lokalne pliki konfiguracji:**
każdy z trzech backendów ma własny `.env`, nieprzechowywany w Git,
oraz wersjonowany `.env.example` z opisem wymaganych zmiennych,
bez prawdziwych sekretów. Pliki są do utworzenia w uzgodnionych katalogach
serwisów. To ustalenie nie obejmuje konfiguracji frontendu ani monitora.
Warunek do późniejszej weryfikacji: dla każdego backendu można
przygotować lokalny `.env` według jego `.env.example`; rzeczywisty
`.env` nie trafia do Git, a plik przykładowy nie zawiera sekretów.
Zatwierdzono pierwszeństwo zmiennych środowiskowych przekazanych przy
uruchomieniu procesu lub kontenera przed wartościami z `.env`.
Warunek do późniejszej weryfikacji: gdy ta sama zmienna ma inną wartość
w `.env` i w środowisku uruchomionego procesu, używana jest wartość
ze środowiska procesu. Zestaw i nazwy zmiennych pozostają otwarte.
Nie utworzono plików ani nie wykonano testów.

**Zatwierdzona decyzja w S1-T2 — Pydantic Settings:**
wszystkie trzy backendy korzystają z Pydantic Settings do odczytu
i walidacji konfiguracji. Dokładnej wersji i zgodności zależności jeszcze
nie sprawdzono. Integracja musi zachować wcześniej uzgodniony tryb
diagnostyczny przy brakujących lub błędnych ustawieniach, z blokadą
zależnych operacji i bez wartości sekretów w raporcie.
Warunek do późniejszej weryfikacji: błędna wartość ustawienia jest
wykrywana i zgłaszana przez diagnostykę, zamiast nieobsłużonego błędu
kończącego proces. Nie zastępujemy brakujących sekretów fikcyjnymi
wartościami. Nie zainstalowano biblioteki ani nie wykonano testów.

**Zatwierdzona decyzja w S1-T4 — narzędzia bazy aplikacji:**
SQLAlchemy i Psycopg obsługują PostgreSQL aplikacji w `application-api`,
a Alembic wersjonuje zmiany struktury tej bazy. Zakres nie obejmuje
DDL użytkownika, akceptacji proponowanych tabel ani dostępu pozostałych
backendów do bazy aplikacji. Fundament migracji powstaje w S1-T4;
migracje rzeczywistych tabel domenowych należą do odpowiednich story.
Zatwierdzono automatyczne uruchamianie przygotowanych migracji przy
starcie `application-api`, bez osobnej ręcznej komendy przy zwykłym
uruchomieniu. Nie jest to automatyczne projektowanie zmian struktury
ani część health checków, kontroli co 30 minut lub „Sprawdź teraz”.
Warunek do późniejszej weryfikacji: po dodaniu przygotowanej migracji
start `application-api` uruchamia jej zastosowanie bez ręcznej komendy;
wywołanie health checku nie uruchamia migracji.
Zatwierdzono reakcję na błąd migracji: serwis pozostaje w trybie
diagnostycznym, podaje przyczynę bez wartości sekretów i blokuje
funkcje wymagające bazy.
Warunek do późniejszej weryfikacji: wymuszony błąd migracji nie wyłącza
endpointu diagnostycznego; wynik wskazuje problem, a operacje wymagające
bazy nie są dopuszczane.
Zatwierdzono wykonywanie migracji wyłącznie w fazie uruchamiania
`application-api`, także po restarcie. Po błędzie kolejna próba wymaga
restartu; migracje nie są ponawiane podczas działania procesu.
Warunek do późniejszej weryfikacji: po błędzie i naprawieniu przyczyny
kontrole diagnostyczne nie ponawiają migracji; kolejna próba następuje
dopiero podczas startu po restarcie.
Nie ustalono ochrony przed równoczesnym wykonaniem ani trybu połączeń
i transakcji.
Dokładne wersje i zgodność z Pythonem 3.14 wymagają sprawdzenia.
Nie wykonano instalacji, migracji ani testów.

**Dalszy krok dla S1:** przejrzeć przygotowany
[pakiet dziewięciu zadań](#s1--pakiet-zadań-do-przekazania-deweloperowi)
i zaakceptować szczegółowe opisy. Pakiet zawiera indeks zależności
i stan przekazania; nie oznacza publikacji ani zlecenia implementacji.
Pełny opis szkieletu zastępuje wcześniejszą listę wytycznych:
[S1-T1](#s1-t1--utworzyć-szkielety-frontendu-i-trzech-serwisów-backendowych).
Szkice T2–T9 zawierają uzgodnione zachowania, planowane sprawdzenia
i jawne braki; zależne części wymagają decyzji przed implementacją.
Nie wracać do pytań o już zatwierdzone ustalenia. Szczególnie zachować
migracje wyłącznie przy starcie i ponowienie po błędzie dopiero po restarcie,
nie przez diagnostykę. Dokładne wersje dobiera deweloper
w uzgodnionych granicach po próbie zgodności.
Nie utworzono podzadań S1 ani nie opublikowano zadań.

**Kontynuacja 14 listopada 2026 — S2:** użytkownik wskazał ten obszar
do przygotowania opisów zadań. Odczytano jego zapisany zakres, standard
zadań dla juniora, wymagania sekcji 4–5 specyfikacji i OD-01,
rejestr ustaleń oraz propozycję macierzy PostgreSQL w sekcji 5
projektu walidacji. Przejrzano propozycje modułów projektów, wersjonowania,
modelu danych i API; nie przeprowadzono pełnego przeglądu wszystkich
szczegółowych kontraktów. Repozytorium nadal nie zawiera kodu aplikacji
ani konfiguracji uruchomienia i testów.

**Uzgodnione dla S2 — 14 listopada 2026:** użytkownik zatwierdził listę
typów kolumn: `smallint`, `integer`, `bigint`, `numeric`/`decimal`
z precyzją i skalą, `text`, `varchar` z długością, `boolean`, `uuid`,
`date`, `timestamp` i `timestamptz`. Decyzję zapisano w sekcji 5.1
specyfikacji, rejestrze ustaleń i przy macierzy projektu walidacji.
Nie zatwierdzono przez to pozostałej części OD-01.

**Kolejne uzgodnienie S2 — 14 listopada 2026:** użytkownik zatwierdził
obsługę wielokolumnowych `PRIMARY KEY`, `FOREIGN KEY` i `UNIQUE`.
Zaktualizowano te same źródła. Decyzja nie obejmuje pozostałych
wariantów ograniczeń ani relacji zatwierdzanych poza DDL.

**Kolejne uzgodnienie S2 — 14 listopada 2026:** użytkownik zatwierdził
`CHECK` obejmujące porównania, zakresy (`BETWEEN`), zbiory wartości (`IN`)
i operatory `AND`, `OR`, `NOT` w obrębie rekordu, bez wywołań funkcji.
Podkreślił, że projekty mogą dotyczyć różnych dziedzin, np. bankowości,
sklepu lub e-commerce. W opisach zadań uwzględniamy rozpoznawanie
dostarczonego DDL bez stałych nazw tabel, kolumn i wartości oraz
przyszłe sprawdzenia na przykładach z różnych dziedzin. Nie oznacza
to obsługi dowolnych konstrukcji PostgreSQL ani wszystkich reguł biznesowych.
Decyzję zapisano w specyfikacji, rejestrze ustaleń i projekcie walidacji.

**Do wyjaśnienia dla S2:** pozostały zakres konstrukcji DDL
(OD-01), parser, kontrakt zapisu i analizy wersji oraz szczegóły obsługi
projektów i zatwierdzania relacji. Proponowane tabele i interfejsy LLD
nie są zatwierdzoną instrukcją implementacji. Zależności od fundamentu
S1 należy wskazać, nie rozstrzygać ich w ramach S2.

**Kolejne uzgodnienie S2 — 14 listopada 2026:** użytkownik zatwierdził
`DEFAULT` obejmujące stałe zgodne z obsługiwanymi typami oraz
`CURRENT_DATE` i `CURRENT_TIMESTAMP`, bez innych wywołań funkcji
i dowolnych wyrażeń. Decyzję zapisano w sekcji 5.1 specyfikacji,
rejestrze ustaleń i macierzy projektu walidacji. Nie obejmuje
automatycznych identyfikatorów.

**Kolejne uzgodnienie S2 — 14 listopada 2026:** użytkownik zatwierdził
obsługę `serial`, `bigserial`, `GENERATED BY DEFAULT AS IDENTITY`
i `GENERATED ALWAYS AS IDENTITY` w dostarczanym DDL. Zaktualizowano
specyfikację, rejestr ustaleń i macierz projektu walidacji. Sposób
nadawania ID w paczce i szczegóły importu SQL/CSV pozostają otwarte.

**Kolejne uzgodnienie S2 — 14 listopada 2026:** użytkownik zatwierdził
jawne wartości ID przygotowywane przez model w paczce również dla
kolumn z automatycznym ID, wraz z powiązaniami rekordów. Zapisano
to w specyfikacji, rejestrze ustaleń i projekcie walidacji. Szczegóły
importu SQL/CSV oraz obsługa sekwencji pozostają otwarte.

**Akceptacja podziału S2 — 14 listopada 2026:** użytkownik zaakceptował
S2-T1–S2-T6 wraz z przedstawionymi rezultatami i granicami. Zapisano
zależności i pokrycie wymagań. Akceptacja podziału nie oznacza gotowości
szczegółowych instrukcji do implementacji ani zatwierdzenia otwartych
kontraktów.

**Bieżący element S2:** S2-T1 — zapis i odczyt projektów w backendzie.
Sprawdzono propozycję encji `projects` w sekcji 3 modelu danych LLD
oraz operacje projektów w opisie serwisów.

**Uzgodnienie S2-T1 — 14 listopada 2026:** użytkownik zatwierdził
wymaganą nazwę i opcjonalny krótki opis kontekstu przy tworzeniu projektu,
bez wyboru dziedziny z zamkniętej listy. Opis nie zastępuje DDL ani
zatwierdzonych reguł. Uzupełniono specyfikację, rejestr ustaleń i model
danych LLD; pozostałe szczegóły tego modelu nie zostały przez to
zatwierdzone. Limity i walidację pól doprecyzowano poniżej.

**Kolejne uzgodnienie S2-T1 — 14 listopada 2026:** użytkownik zatwierdził
zapis projektu z nazwą i opcjonalnym opisem przed wgraniem DDL.
Schemat można dodać później. Projekt bez schematu pozostaje zapisany,
ale nie jest gotowy do generowania. Uzupełniono specyfikację, rejestr
ustaleń i model danych LLD. Nie rozstrzygnięto zachowania po nieudanej
analizie wgranego DDL.

**Kolejne uzgodnienie S2-T1 — 14 listopada 2026:** zatwierdzono
walidację pól projektu: nazwa 1–100 znaków, opis opcjonalny do 2000 znaków,
długości liczone po usunięciu białych znaków z początku i końca obu pól,
nazwa z samych białych znaków odrzucana, pusty opis traktowany jako brak
opisu, przekroczenie limitu odrzucane czytelnym błędem bez obcinania treści.
Uzupełniono specyfikację, rejestr ustaleń i model danych LLD.

**Kolejne uzgodnienie S2-T1 — 14 listopada 2026:** użytkownik zatwierdził
unikalność nazw w danej instalacji bez rozróżniania wielkości liter.
Wcześniej uzgodnione usuwanie brzegowych białych znaków nadal obowiązuje.
Duplikat jest odrzucany czytelnym błędem bez nadpisania projektu.
Zapisano decyzję w specyfikacji, rejestrze ustaleń i modelu danych.
Techniczna realizacja porównania i ograniczenia w bazie pozostaje otwarta.

**Kolejne uzgodnienie S2-T1 — 14 listopada 2026:** zatwierdzono
podstawowy zakres API projektów: `POST /api/v1/projects` tworzy projekt
z `name` i opcjonalnym `description` i zwraca `201`; `GET /api/v1/projects`
zwraca listę (`200`); `GET /api/v1/projects/{project_id}` zwraca wybrany
projekt (`200`). Zatwierdzono błędy: `422` dla niepoprawnych pól,
`409` dla zajętej nazwy, `404` dla nieistniejącego projektu.
Zaktualizowano kontrakty API, opis serwisów i rejestr ustaleń.
Akceptacja nie ustala jeszcze kompletu pól odpowiedzi, organizacji
listy, szczegółowego formatu błędów ani realizacji unikalności w bazie.

**Kolejne uzgodnienie S2-T1 — 14 listopada 2026:** użytkownik zatwierdził
obiekt projektu zwracany przez API z polami `id`, `name`, `description`
(opis albo `null`) oraz `created_at`, z identyfikatorem i czasem
utworzenia nadawanymi przez backend. Ten sam zestaw pól obowiązuje
dla utworzenia, odczytu i elementu listy. Typ identyfikatora,
format czasu i organizacja listy pozostają do doprecyzowania.
Zaktualizowano kontrakty API i rejestr ustaleń.

**Kolejne uzgodnienie S2-T1 — 14 listopada 2026:** użytkownik zatwierdził
`id` jako tekstowy UUID i `created_at` jako datę i czas ISO 8601 w UTC
z końcówką `Z`. Obie wartości nadaje backend, nie klient. Uzupełniono
kontrakty API i rejestr ustaleń. Nie wybrano konkretnej wersji UUID
ani biblioteki.

**Kolejne uzgodnienie S2-T1 — 14 listopada 2026:** zatwierdzono listę
`{"items": [...]}` ze wszystkimi projektami bez podziału na strony w MVP,
od najnowszych (`created_at` malejąco, przy remisie `id` rosnąco).
Brak projektów daje `200` i `{"items": []}`. Zaktualizowano kontrakty
API i rejestr ustaleń. W sekcji S2 zapisano szkic szczegółowego opisu
S2-T1, kryteria, planowane sprawdzenia i jawne braki. Szkic nie jest
jeszcze gotowy do przekazania do implementacji.

**Kolejne uzgodnienie S2-T1 — 14 listopada 2026:** zatwierdzono
dla błędów projektów `422`, `409` i `404` wspólną strukturę `error`
z polami `code`, `message`, `request_id`, `automatic_retry_allowed`
i `details`, z `automatic_retry_allowed=false`. Kody tekstowe i dokładny
format `details` pozostają do doprecyzowania. Zaktualizowano kontrakty
API, rejestr ustaleń i listę braków szkicu S2-T1.

**Kolejne uzgodnienie S2-T1 — 14 listopada 2026:** zatwierdzono
kody `VALIDATION_ERROR` (`422`), `PROJECT_NAME_CONFLICT` (`409`)
i `PROJECT_NOT_FOUND` (`404`) oraz `details` jako `{"fields": [...]}`
z pozycjami `field` i `message`. Konflikt wskazuje pole `name`,
a nieistniejący projekt pustą listę. Zaktualizowano kontrakty API,
rejestr ustaleń i szkic opisu S2-T1.

**Kolejne uzgodnienie S2-T1 — 14 listopada 2026:** zatwierdzono
ścisłą walidację wejścia: wymagany tekst `name`, opcjonalny tekst lub
`null` w `description`, brak automatycznej konwersji innych typów
na tekst i odrzucanie dodatkowych pól. Brak lub `null` dla nazwy,
niepoprawne typy, dodatkowe pola i niepoprawny UUID w ścieżce dają
`422 VALIDATION_ERROR`. `description` pominięte, `null` lub puste
po usunięciu brzegowych białych znaków oznacza brak opisu.
Zaktualizowano kontrakty API, rejestr ustaleń, instrukcje i planowane
sprawdzenia S2-T1. Opis nadal ma status **do wyjaśnienia** ze względu
na wymienione przy nim szczegóły techniczne i zależności S1.

**Bieżące niezależne doprecyzowanie S2:** S2-T2 — wgrywanie i przechowywanie
pełnych wersji DDL. Tworzenie projektu bez DDL jest uzgodnione.
REQ-014 wymaga zachowania wymagań rozpoczętego wykonania, ale nie określa
zapisu wersji po nieudanej analizie. Przejrzano opis `schema_versions`
i `schema_interpretations` w modelu danych; niezatwierdzona propozycja
modelu nie rozstrzyga tej reakcji.

**Uzgodnienie S2-T2 — 14 listopada 2026:** użytkownik zatwierdził, że wgrany
plik DDL po nieudanej analizie zachowujemy jako osobną wersję
z diagnostyką, bez dopuszczenia jej do generowania i bez zastępowania
dotychczasowej używanej wersji schematu. Poprawiony pełny DDL stanowi
kolejną wersję. Zaktualizowano specyfikację, rejestr ustaleń i model
danych LLD. Nie ustalono pól statusu, kontraktu uploadu ani obsługi
błędów transferu i zapisu.

**Kolejne uzgodnienie S2-T2 — 14 listopada 2026:** nowa wersja DDL
po poprawnej analizie, bez blokad uniemożliwiających jej użycie,
automatycznie staje się domyślną dla nowych zleceń. Rozpoczęte
wykonania zachowują wcześniej przypięte wymagania (REQ-014).
Zaktualizowano specyfikację, rejestr ustaleń i model danych LLD.
Obsługę reguł i zatwierdzonych relacji spoza DDL doprecyzowano poniżej.

**Kolejne uzgodnienie S2-T2 — ponowne zatwierdzenie, 14 listopada 2026:**
reguły biznesowe i zatwierdzone relacje spoza DDL z poprzedniej wersji
wymagają ponownej weryfikacji i zatwierdzenia przed użyciem z nową wersją
schematu. Nie przenosimy automatycznie ich zatwierdzenia.
Rozpoczęte wykonania pozostają bez zmian. Zaktualizowano specyfikację,
rejestr ustaleń i model danych LLD. Techniczne powiązanie z wersją
pozostaje otwarte; zadanie nadal ma status **do wyjaśnienia**.

**Kolejne uzgodnienie S2-T2 — propozycje do przeglądu, 14 listopada 2026:**
po zmianie DDL dotychczasowe reguły biznesowe i relacje spoza DDL pokazujemy
jako propozycje do przeglądu, bez konieczności wpisywania ich od początku.
Nie obowiązują z nową wersją przed ponowną weryfikacją i zatwierdzeniem.
Zaktualizowano specyfikację, rejestr ustaleń i model danych LLD.
Blokadę generowania przed zakończeniem przeglądu uzgodniono poniżej.

**Kolejne uzgodnienie S2-T2 — blokada do zakończenia przeglądu,
14 listopada 2026:** start generowania na nowym schemacie jest zablokowany
do rozpatrzenia każdej przeniesionej propozycji reguły lub relacji:
zatwierdzenia po weryfikacji albo świadomego odrzucenia dla nowej wersji.
Wersja domyślna nie oznacza gotowości do generowania. Zakończenie przeglądu
nie omija innych blokad. Rozpoczęte wykonania pozostają bez zmian.
Zaktualizowano specyfikację, rejestr ustaleń i model danych LLD.

**Przypadki do sprawdzenia po implementacji — granica S2/S3/S6:**
- Nowy poprawny DDL staje się domyślny, ale jedna nierozpatrzona
  propozycja nadal blokuje start generowania na nowym schemacie.
- Zatwierdzenie części propozycji nie usuwa blokady pozostałych.
- Po rozpatrzeniu wszystkich propozycji znika blokada przeglądu,
  lecz pozostałe przeszkody nadal blokują start.
- Wykonanie rozpoczęte przed zmianą DDL zachowuje wcześniejsze wymagania.
To plan testów, nie wynik wykonanych sprawdzeń. Podział implementacji
tej blokady między zadania wymaga doprecyzowania kontraktów.

**Kolejne uzgodnienie S2-T2 — wiele plików, 14 listopada 2026:**
użytkownik odrzucił ograniczenie do pojedynczego pliku SQL. MVP dopuszcza
również paczki wielu plików DDL. Zaktualizowano specyfikację, rejestr
ustaleń i model danych LLD. Sposób przekazania paczki uzgodniono poniżej.
Kolejność plików i reakcję na błąd analizy części paczki uzgodniono
poniżej; limity są otwarte.
Opisy S2-T2, analizy S2-T3–T4 i interfejsu S2-T6 muszą uwzględniać
wejście wieloplikowe; szczegóły pozostają **do wyjaśnienia**.

**Kolejne uzgodnienie S2-T2 — wspólne wysłanie plików, 14 listopada 2026:**
użytkownik zaznacza wiele plików SQL i wysyła je razem w formularzu,
bez konieczności tworzenia archiwum. Nie uzgodniono obsługi ZIP ani
technicznego kontraktu przesyłania. Zaktualizowano specyfikację, rejestr
ustaleń i model danych LLD.

**Kolejne uzgodnienie S2-T2 — paczka jako jedna wersja, 14 listopada 2026:**
wszystkie pliki wysłane razem tworzą jedną pełną wersję schematu,
dopuszczaną do użycia wyłącznie w całości. Błąd analizy jednego pliku
blokuje użycie całej nowej wersji, bez częściowego zastępowania
dotychczasowego schematu. Nieudaną wersję zachowujemy z diagnostyką.
Zaktualizowano rezultat S2-T2, specyfikację, rejestr ustaleń i model danych.
Nie rozstrzygnięto awarii transferu lub zapisu.

**Przypadek do sprawdzenia po implementacji S2-T2–T4:** przesłać paczkę
z poprawnym i błędnym plikiem. Oczekiwane: jedna nieudana wersja
z diagnostyką, brak użycia poprawnej części jako nowego schematu
i brak zmiany dotychczasowej wersji domyślnej. To plan testu,
nie wykonane sprawdzenie.

**Kolejne uzgodnienie S2-T2 — kolejność plików, 14 listopada 2026:**
użytkownik może ustawić kolejność plików przed wysłaniem. Aplikacja traktuje
je w tej kolejności jako jeden skrypt DDL, bez samodzielnego przestawiania.
Zapis wersji musi zachować wybraną kolejność. Zaktualizowano specyfikację,
rejestr ustaleń i model danych LLD. Nie rozstrzygnięto technicznego sposobu
łączenia treści ani mapowania diagnostyki na pliki.

**Przypadek do sprawdzenia po implementacji S2-T2/S2-T6:** wybrać pliki
o nazwach, których kolejność alfabetyczna różni się od ustawionej ręcznie.
Po wysłaniu i ponownym odczycie wersji oczekiwana jest kolejność wybrana
przez użytkownika, również na wejściu analizy. To plan testu,
nie wykonane sprawdzenie.

**Kolejne uzgodnienie S2-T2 — UTF-8, 14 listopada 2026:**
pliki DDL przyjmujemy wyłącznie w kodowaniu UTF-8. Niepoprawne kodowanie
zgłaszamy jako czytelny błąd, bez automatycznego zgadywania i konwersji.
Zaktualizowano specyfikację, rejestr ustaleń i model danych LLD.
Obsługę BOM uzgodniono poniżej. Etap odrzucenia błędnego pliku
i jego zapis jako nieudanej wersji pozostają do wyjaśnienia.

**Przypadki do sprawdzenia po implementacji S2-T2:** poprawny plik UTF-8
z polskimi znakami zachowuje treść; plik z niepoprawną sekwencją bajtów
UTF-8 daje czytelny błąd, bez zastępowania znaków lub konwersji.
To plan sprawdzeń, nie wykonane testy.

**Kolejne uzgodnienie S2-T2 — BOM, 14 listopada 2026:** dopuszczamy UTF-8
także z BOM, czyli opcjonalnym znacznikiem na początku każdego pliku.
Zachowujemy oryginalny plik bez zmian; znacznik pomijamy wyłącznie
na potrzeby analizy. Zaktualizowano specyfikację, rejestr ustaleń
i model danych LLD.

**Przypadek do sprawdzenia po implementacji S2-T2–T3:** paczka zawiera
pliki UTF-8 z BOM i bez BOM. Oczekiwane: BOM na początku każdego pliku
nie zakłóca analizy, a zapisane oryginały zachowują swoje bajty.
To plan sprawdzenia, nie wykonany test.

**Do wyjaśnienia S2-T2 — skala wejścia, 14 listopada 2026:** użytkownik
zakwestionował propozycję limitu 10 MiB jako potencjalnie zbyt małą
dla złożonych baz, podając Allegro jako przykład oczekiwanej złożoności.
Limit 10 MiB nie został zaakceptowany i nie jest wymaganiem.
Nie ustalono też większego limitu ani obsługi rzeczywistego schematu
Allegro. Docelową skalę schematu w MVP doprecyzowano poniżej.
Limit wejściowych plików DDL dotyczy definicji struktury, nie rozmiaru
danych w bazie; nie oznacza możliwości przekazania całości do LLM
w jednym wywołaniu. Wykonalność przetwarzania dużych schematów pozostaje
do weryfikacji, bez zmiany uzgodnionego zakresu dialektu PostgreSQL.

**Kolejne uzgodnienie S2 — kilkaset tabel, 14 listopada 2026:**
użytkownik wskazał docelowo nawet kilkaset tabel w jednym projekcie MVP.
To uzgodniona skala schematu, nie dokładny limit tabel ani potwierdzona
wydajność. Nie zmienia zakresu obsługiwanych konstrukcji PostgreSQL
ani skali liczby rekordów z REQ-007. Zaktualizowano sekcję 13.3
specyfikacji i rejestr ustaleń. S2-T2–T4 i S2-T6 muszą uwzględnić tę
skalę w planowanych sprawdzeniach wgrywania, odczytu, analizy, diagnostyki
i prezentacji. Nie uzgodniono jeszcze konkretnego zestawu testowego,
progów czasowych ani limitów pamięci. Nie wykonano testów.

**Kolejne uzgodnienie — granica S2/S4/S6, 14 listopada 2026:**
jedno zlecenie może obejmować generowanie danych do wszystkich kilkuset
tabel projektu. Nie oznacza to jednego wywołania LLM ani równoległego
przetwarzania wszystkich tabel. Nie wybrano sposobu podziału pracy
i nie zmieniono skali łącznej liczby rekordów z REQ-007.
Zaktualizowano sekcję 13.3 specyfikacji i rejestr ustaleń.
Ujednolicono też REQ-003 z zaakceptowaną wcześniej obsługą paczek plików.
Ta skala wymaga uwzględnienia w przyszłych opisach zadań S4/S6/S7,
ale nie stanowi zgody na ich implementację ani zmiany wariantów badawczych.
Nie wykonano testów wydajności ani wywołań modeli.

**Kolejne uzgodnienie S2-T2 — awaria wgrywania, 14 listopada 2026:**
przy przerwanym transferze lub nieudanym zapisie paczki nie tworzymy nowej
wersji schematu i nie zmieniamy dotychczasowego schematu. Użytkownik musi
ponownie wysłać całą paczkę. To nie dotyczy nieudanej analizy kompletnej,
zapisanej paczki, którą zachowujemy jako wersję z diagnostyką.
Zaktualizowano specyfikację, rejestr ustaleń i model danych LLD.
Dodano częściowo uzgodniony opis S2-T2 w sekcji obszaru wraz z planem
sprawdzeń i jawnymi blokadami. Nie wykonano implementacji ani testów.

**Kolejne uzgodnienie S2-T2 — utrata odpowiedzi, 14 listopada 2026:**
po utracie odpowiedzi serwera aplikacja najpierw sprawdza wynik wysłania
paczki, zamiast od razu proponować ponowne wysłanie. Ma to uniknąć
duplikatu, gdy zapis się udał, ale odpowiedź nie dotarła. Zaktualizowano
specyfikację, rejestr ustaleń, model danych LLD oraz kroki i plan testów
w opisie S2-T2. Mechanizm identyfikacji wysłania, kontrakt odczytu wyniku
i zachowanie przy nadal nieznanym wyniku są otwarte.

**Kolejne uzgodnienie S2-T2 — analiza w tle, 14 listopada 2026:**
po odebraniu i zapisaniu plików potwierdzamy wgranie, a analizę DDL
wykonujemy w tle. Interfejs pokazuje stan analizy. Żądanie wgrywania
nie czeka na jej zakończenie, a potwierdzenie zapisu nie oznacza poprawnej
analizy ani gotowości do generowania. Zaktualizowano specyfikację,
rejestr ustaleń, model danych LLD oraz kroki i plan testów S2-T2.
Mechanizm uruchamiania, dokładne stany i obsługa przerwania pozostają
otwarte; nie uzgodniono procentowego postępu ani automatycznego wznowienia.

**Kolejne uzgodnienie — lokalizacja diagnostyki S2, 14 listopada 2026:**
błąd analizy wskazuje nazwę oryginalnego pliku i numer wiersza w nim,
jeżeli lokalizację można ustalić. Sama pozycja w połączonym skrypcie
nie wystarcza. Problem całej paczki otrzymuje opis bez sztucznej
lokalizacji. Zaktualizowano specyfikację, rejestr ustaleń, model danych
LLD i rezultat S2-T4. Kontrakt diagnostyki i mapowanie pozycji są otwarte.

**Przypadki do sprawdzenia po implementacji S2-T3–T4/S2-T6:**
- Błąd w drugim pliku paczki wskazuje ten plik i wiersz w jego oryginalnej
  treści, także przy BOM i kolejności plików innej niż alfabetyczna.
- Problem dotyczący całej paczki nie otrzymuje wymyślonego pliku
  ani numeru wiersza.
To plan sprawdzeń, nie wykonane testy.

**Kolejne uzgodnienie S2-T2 — automatyczne uruchomienie po awarii,
14 listopada 2026:** użytkownik odrzucił propozycję wymagania ręcznej
akcji. Po awarii przerywającej analizę aplikacja automatycznie uruchamia
analizę zapisanej paczki ponownie, gdy jest to możliwe, bez ponownego
wgrywania plików. Nie rozstrzygnięto jeszcze rozpoczęcia od nowa lub
kontynuacji częściowej pracy, limitu ani odstępów ponowień.
To ustalenie dotyczy analizy DDL, nie naprawiania błędnego schematu
ani wznowienia generowania danych. Zaktualizowano specyfikację, rejestr
ustaleń, model danych oraz kroki i plan testów S2-T2.
Nie wykonano implementacji ani testów.

**Kolejne uzgodnienie S2-T2 — limit ponowień analizy, 14 listopada 2026:**
maksymalnie trzy automatyczne ponowienia analizy po awarii, poza pierwszym
uruchomieniem. Po wyczerpaniu analiza zatrzymuje się z czytelnym błędem,
bez kolejnego automatycznego ponowienia. To limit odrębny od rund
naprawczych generowania. Zaktualizowano specyfikację, rejestr ustaleń,
model danych LLD oraz kroki i plan testów S2-T2. Nie wykonano testów.
Zapis licznika, odstępy ponowień i dalsza ręczna obsługa są otwarte.

**Kolejne uzgodnienie S2-T2 — kontynuacja, jeżeli możliwa, 14 listopada
2026:** użytkownik nie przyjął bezwarunkowej analizy całej paczki od początku.
Przy ponowieniu kontynuujemy od zachowanego postępu, jeżeli jest to
technicznie możliwe i zapewnia poprawny, kompletny wynik. Nie zweryfikowano
wykonalności ani nie wybrano sposobu zapisu postępu. Limit trzech
automatycznych ponowień nadal obowiązuje. Zaktualizowano specyfikację,
rejestr ustaleń, model danych LLD i opis S2-T2. Nie wykonano implementacji
ani testów. Zachowanie przy braku możliwości kontynuacji pozostaje otwarte.

**Kolejne uzgodnienie S2-T2 — brak możliwości kontynuacji, 14 listopada
2026:** gdy kontynuacja od zachowanego postępu jest niemożliwa,
automatycznie analizujemy zapisaną paczkę od początku, bez ponownego
wgrywania. Obowiązuje ten sam limit trzech automatycznych ponowień;
zmiana sposobu ponowienia nie przyznaje dodatkowego limitu.
Zaktualizowano specyfikację, rejestr ustaleń, model danych LLD oraz kroki
i plan testów S2-T2. Nie wykonano implementacji ani testów.

**Kolejne uzgodnienie S2-T2 — przerwanie przed nowym DDL, 14 listopada
2026:** użytkownik najpierw przerywa bieżącą analizę. Po jej zatrzymaniu
może wgrać nowy DDL jako kolejną wersję tego samego projektu.
Nie analizujemy obu wersji równolegle. Świadome przerwanie nie jest awarią
i nie uruchamia automatycznych ponowień starej analizy.
Zaktualizowano specyfikację, rejestr ustaleń, model danych LLD oraz kroki
i plan sprawdzeń S2-T2. Mechanizm potwierdzenia zatrzymania i sposób
zachowania przerwanej wersji pozostają do uzgodnienia. Nie wykonano testów.

**Kolejne uzgodnienie S2-T2 — odrzucone zachowanie przerwanej wersji,
14 listopada 2026:** użytkownik odrzucił propozycję zachowania plików
ręcznie przerwanej analizy jako wersji schematu oznaczonej „przerwana”.
Nie zmienia to ponawiania po awarii ani zachowania wersji po błędzie
analizy. Zaktualizowano specyfikację, rejestr ustaleń i model danych LLD.
Sposób rozliczenia roboczych plików, częściowego wyniku i zapisu wersji
pozostaje otwarty. Nie usunięto żadnych plików ani danych.

**Kolejne uzgodnienie S2-T2 — sprzątanie po ręcznym przerwaniu,
14 listopada 2026:** po potwierdzonym ręcznym zatrzymaniu usuwamy pliki
wgrane dla tej analizy i jej częściowy wynik. Wcześniejsze wersje schematu
pozostają bez zmian. Nie zmienia to zachowania po awarii ani po błędzie
analizy kompletnej paczki. Zaktualizowano specyfikację, rejestr ustaleń,
model danych LLD oraz kroki i plan testów S2-T2. To ustalenie docelowego
zachowania aplikacji: nie usunięto żadnych danych ani plików w repozytorium.
Techniczny sposób sprzątania i obsługa jego błędu pozostają otwarte.

**Kolejne uzgodnienie S2-T6 — potwierdzenie przerwania, 14 listopada
2026:** przed ręcznym przerwaniem interfejs wymaga potwierdzenia
z ostrzeżeniem o usunięciu wgranych dla tej analizy plików i częściowego
wyniku. Rezygnacja z potwierdzenia nie przerywa analizy ani nie usuwa
danych. Zaktualizowano specyfikację, rejestr ustaleń, model danych
oraz powiązania i plan sprawdzeń w opisie S2-T2.
Nie wykonano implementacji, testów ani operacji usuwania.

**Kolejne uzgodnienie S2-T2 — odrzucenie kodowania w MVP, 14 listopada
2026:** błędne kodowanie choćby jednego pliku odrzuca całą paczkę przed
utworzeniem wersji schematu i uruchomieniem analizy DDL. Użytkownik
otrzymuje czytelny błąd i ponownie wysyła pełną poprawioną paczkę.
Użytkownik wskazał podmianę pojedynczego pliku jako kierunek po MVP;
nie dodajemy jej do obecnych zadań ani nie implementujemy na zapas.
Zaktualizowano specyfikację (w tym kierunki rozszerzeń), rejestr ustaleń,
model danych LLD oraz kroki, wyłączenia i plan testów S2-T2.
Nie wykonano implementacji ani testów.

**Kolejne uzgodnienie S2-T2 — puste pliki, 14 listopada 2026:**
pusty plik lub plik zawierający wyłącznie białe znaki odrzuca całą paczkę
przed utworzeniem wersji. Nie pomijamy go automatycznie; zasada dotyczy
również pojedynczego pliku. Zaktualizowano specyfikację, rejestr ustaleń,
model danych LLD oraz kroki i plan sprawdzeń S2-T2.
Nie wykonano implementacji ani testów.

**Kolejne uzgodnienie S2-T2 — same komentarze, 14 listopada 2026:**
plik zawierający wyłącznie komentarze SQL i ewentualne białe znaki,
bez instrukcji SQL, traktujemy jak pusty: odrzucamy całą paczkę przed
utworzeniem wersji. Zaktualizowano specyfikację, rejestr ustaleń,
model danych LLD oraz kroki i plan testów S2-T2.
Zebrano też ustalone zachowania w częściowym opisie S2-T6,
bez wybierania układu interfejsu i brakujących kontraktów.
Opisy nadal nie są gotowe do implementacji. Nie wykonano testów.

**Kolejne uzgodnienie S2-T2 — unikalne nazwy plików, 14 listopada 2026:**
nazwy w jednej paczce są unikalne bez rozróżniania wielkości liter.
Konflikt, np. `schema.sql` i `SCHEMA.sql`, odrzuca całą paczkę przed
utworzeniem wersji. Zaktualizowano specyfikację, rejestr ustaleń,
model danych LLD oraz kroki i plan sprawdzeń S2-T2.
Techniczny sposób porównania nazw pozostaje do doprecyzowania.
Nie wykonano implementacji ani testów.

**Kolejne uzgodnienie S2-T2 — zbiorcze błędy, 14 listopada 2026:**
dla kompletnie odebranej paczki pokazujemy razem wykryte błędy
wstępnego sprawdzenia plików (kodowanie, puste pliki, konflikty nazw),
zamiast kończyć sprawdzenie po pierwszym błędzie. Nie obiecujemy zebrania
wszystkich błędów późniejszej analizy DDL ani sprawdzania treści pliku
o niepoprawnym kodowaniu. Zaktualizowano specyfikację, rejestr ustaleń,
model danych LLD oraz kroki i plan sprawdzeń S2-T2 i S2-T6.
Nie wykonano implementacji ani testów.

**Kolejne uzgodnienie S2-T2 — identyfikator próby, 14 listopada 2026:**
każda próba wysłania otrzymuje unikalny identyfikator utworzony przez
frontend przed przesłaniem plików. Po utracie odpowiedzi aplikacja
sprawdza po nim wynik tej samej próby w backendzie, bez ponownego
wysyłania paczki. Format i przechowywanie identyfikatora, powiązanie
z wersją i kontrakt odczytu są otwarte. Zaktualizowano specyfikację,
rejestr ustaleń, model danych oraz opisy S2-T2 i S2-T6.
Nie wykonano implementacji ani testów.

**Kolejne uzgodnienie S2-T2 — nadal nieznany wynik, 14 listopada 2026:**
do ustalenia wyniku próby blokujemy ponowne wysłanie tej paczki
i pokazujemy „Sprawdź ponownie”. Akcja odczytuje wynik tej samej próby
bez przesyłania plików. Niedostępny odczyt nie oznacza nieudanego zapisu;
użytkownik może musieć poczekać na przywrócenie odczytu z backendu.
Zaktualizowano specyfikację, rejestr ustaleń, model danych oraz opisy
i plan sprawdzeń S2-T2 i S2-T6. Nie wykonano implementacji ani testów.

**Kolejne uzgodnienie S2-T2/S2-T6 — wyjście podczas przesyłania,
14 listopada 2026:** użytkownik wskazał zamiast przywracania próby:
podczas przesyłania ma pojawić się ostrzeżenie, że odświeżenie lub
zamknięcie strony/aplikacji anuluje przesyłanie. Pozostanie na stronie
nie anuluje transferu. Nie uznano tego za zgodę na przywracanie próby
po powrocie ani na usuwanie paczki już zapisanej przez backend.
Uwzględniono ograniczenia ostrzeżenia z sekcji 11.1 specyfikacji.
Zaktualizowano specyfikację, rejestr ustaleń, model danych i opisy
S2-T2/S2-T6. Nie wykonano implementacji ani testów.

**Kolejne uzgodnienie S2-T2/S2-T6 — zapis bez odebranego potwierdzenia,
14 listopada 2026:** użytkownik odrzucił zachowanie nowej wersji po
wyjściu przed odebraniem potwierdzenia przez przeglądarkę, nawet jeśli
backend zapisał już całą paczkę. Usuwamy pliki anulowanej próby bez
zmiany wcześniejszych wersji. To doprecyzowanie poprzedniego uzgodnienia,
nie operacja na rzeczywistych plikach. Zaktualizowano specyfikację,
rejestr ustaleń, model danych i opis oraz plan sprawdzeń S2-T2.
Mechanizm pozostaje otwarty; nie wykonano implementacji ani testów.

**Kolejne uzgodnienie S2-T2/S2-T6 — dodatkowe potwierdzenie odbioru,
14 listopada 2026:** serwer zapisuje paczkę roboczo. Analizę uruchamia
dopiero po otrzymaniu dodatkowego potwierdzenia z przeglądarki, że odebrała
komunikat o zapisie. Potwierdzenie jest automatyczne, bez dodatkowego
kliknięcia użytkownika. Sam zapis i wysłanie odpowiedzi nie wystarczają.
Zaktualizowano specyfikację, rejestr ustaleń, model danych oraz opisy
S2-T2/S2-T6 i plan sprawdzeń. Kontrakt, utrata potwierdzenia, wykrycie
porzuconego zapisu, okna awarii i sprzątanie pozostają otwarte.
Nie wykonano implementacji ani testów.

**Kolejne uzgodnienie S2-T2/S2-T6 — analiza asynchroniczna,
14 listopada 2026:** po przyjęciu dodatkowego potwierdzenia rozpoczęta
analiza może działać niezależnie od otwartej strony. Odświeżenie lub
zamknięcie strony jej nie anuluje. Nie zmieniono zasad anulowania
transferu, osobnego ręcznego przerwania analizy ani obsługi awarii
backendu. Zaktualizowano specyfikację, rejestr ustaleń, model danych
oraz opisy S2-T2/S2-T6 i plan sprawdzeń. Nie wykonano testów ani kodu.

**Kolejne uzgodnienie S2-T2/S2-T6 — brak ręcznego ponowienia,
14 listopada 2026:** po doprecyzowaniu wypowiedzi użytkownik potwierdził,
że po wyczerpaniu trzech automatycznych ponowień musi ponownie wgrać
całą paczkę plików. Nie udostępniamy ręcznego ponowienia analizy
zapisanej paczki. To rozstrzyga wcześniejszą otwartą kwestię dalszej
ręcznej obsługi; nie ma osobnego licznika dla nieprzyjętej akcji.
Zaktualizowano specyfikację, rejestr ustaleń, model danych i opisy
S2-T2/S2-T6 oraz plan sprawdzeń. Nie wykonano implementacji ani testów.

**Kolejne uzgodnienie S2-T2 — jedna analiza w całym MVP,
14 listopada 2026:** użytkownik odrzucił równoległe analizy różnych
projektów. Jednocześnie działa tylko jedna analiza DDL w całej aplikacji,
bez ograniczania liczby zapisanych projektów. Nie przyjęto jeszcze
kolejki ani blokady wgrywania w innych projektach. Zaktualizowano
specyfikację, rejestr ustaleń, model danych i opis oraz plan sprawdzeń
S2-T2. Nie wykonano implementacji ani testów.

**Kolejne uzgodnienie S2-T2/S2-T6 — blokada wgrywania podczas analizy,
14 listopada 2026:** podczas analizy jednego projektu blokujemy
wgrywanie DDL również w pozostałych. Nie przyjmujemy kolejnych paczek
do kolejki. To rozstrzyga wcześniejszą propozycję blokady lub oczekiwania.
Zaktualizowano specyfikację, rejestr ustaleń, model danych oraz opisy
S2-T2/S2-T6 i plan sprawdzeń. Nie wykonano implementacji ani testów.

**Kolejne uzgodnienie S2-T2/S2-T6 — blokada od początku wysyłania,
14 listopada 2026:** użytkownik potwierdził, że blokada obowiązuje
już od rozpoczęcia wysyłania jednej paczki, także w innych kartach
przeglądarki i we wszystkich projektach. Nie dopuszczamy równoczesnego
wysyłania kolejnej paczki przed analizą. Zaktualizowano specyfikację,
rejestr ustaleń, model danych oraz opisy S2-T2/S2-T6 i plan sprawdzeń.
Techniczny mechanizm pozostaje otwarty. Nie wykonano kodu ani testów.

**Kolejne uzgodnienie S2-T2/S2-T6 — blokada pomiędzy próbami,
14 listopada 2026:** blokada wgrywania pozostaje aktywna również
podczas oczekiwania na automatyczne ponowienie analizy po awarii.
Przerwa pomiędzy uruchomieniami nie pozwala wgrać kolejnej paczki.
Zaktualizowano specyfikację, rejestr ustaleń, model danych oraz opisy
S2-T2/S2-T6 i plan sprawdzeń. Nie wykonano implementacji ani testów.

**Kolejne uzgodnienie S2-T2/S2-T6 — odmowa API,
14 listopada 2026:** przy aktywnej blokadzie backend odrzuca wysłanie
kolejnej paczki odpowiedzią HTTP `409` z kodem
`DDL_PROCESSING_IN_PROGRESS`. Interfejs pokazuje „Trwa przesyłanie lub
analiza DDL. Poczekaj na zakończenie”. Uzupełniono specyfikację,
rejestr ustaleń, kontrakty API i opisy S2-T2/S2-T6.
Nie zatwierdzono przez to ścieżki uploadu ani pozostałych pól błędu.

**Sposób dalszego planowania — 14 listopada 2026:** użytkownik zwrócił
uwagę na nadmierną liczbę drobnych pytań przed otrzymaniem opisów.
Zamiast uzależniać sporządzenie całej treści od zamknięcia każdego
kontraktu, uzupełniono w tym samym planie szkice S2-T3, S2-T4 i S2-T5.
S2-T1–S2-T6 mają teraz opisy zakresu, kroków, wyłączeń, zależności,
kryteriów i planowanych sprawdzeń. Nie jest to akceptacja nowych opisów
przez użytkownika ani gotowość całego S2 do implementacji.

**Zebrane blokady przed implementacją — bez nowego backlogu:**

| Grupa | Co trzeba doprecyzować | Dotyczy |
| --- | --- | --- |
| Parser i model schematu | Wybrać parser, określić format wyniku, pozostałe konstrukcje OD-01 i mapowanie błędów na pliki. | T3–T4, odbiorcy w T2/T5/T6. |
| Wgrywanie i praca w tle | Doprecyzować roboczy zapis i potwierdzenie, globalną blokadę, anulowanie i sprzątanie, utratę potwierdzenia, zapis postępu i licznika ponowień. | T2, obsługa stanów w T6. |
| Kontrakty i relacje | Uzupełnić operacje wgrywania, odczytu, stanu, przerwania i zatwierdzania; określić źródło propozycji relacji, ich semantykę oraz wspólny przegląd po zmianie DDL. | T2–T6 i granice z S3/S6/S7. |
| Limity, interfejs i fundament S1 | Uzgodnić limity wejścia i pomiary dla kilkuset tabel, układ podglądu oraz brakujące zależności magazynu, dostępu i testów. Nie przyjęto limitu 10 MiB ani gwarancji wydajności. | T1–T6, zależności od S1. |

To grupy braków technicznych, nie cztery gotowe pytania ani nowe
zadania do samodzielnego rozstrzygnięcia przez juniora. Nie wymagamy
zamknięcia wszystkich grup, żeby użytkownik mógł przeczytać i ocenić
przygotowane opisy. Przed uruchomieniem konkretnego zadania należy
zamknąć jego zależne blokady; nie wolno dopisywać rozwiązań jako faktów.

**Następny krok dla S2:** przegląd przygotowanych opisów S2-T1–S2-T6,
a następnie dopracowanie blokad wybranego zadania przed implementacją.
Nie rozpoczynać kolejnej serii drobnych pytań tylko po to, by opóźniać
przekazanie szkiców. Nie utworzono nowych podzadań ani issue,
nie wykonano kodu ani testów aplikacji.

Przy powrocie do publikacji najpierw uzgodnić aktualny zakres zapisu
i właściwy dostęp do konta oraz Projects. Następnie ponownie sprawdzić
duplikaty, utworzyć lub wykorzystać tablicę i opublikować tylko uzgodnioną
partię. Mapowanie zapisywać po każdym utworzeniu, a wynik potwierdzić
odczytem opisów, relacji i faktycznego członkostwa w Project.

Nie utworzono Project, nowych issues, pól, etykiet ani milestone'ów.
Nie wykonano implementacji, commitów ani pushowania.

### Stan sesji dotyczącej S3 — 14 listopada 2026

**Zlecony zakres:** przygotowanie opisów zadań S3 — reguły biznesowe
i ich zatwierdzanie. Etap 4: przygotowano szkice opisów S3-T1–S3-T5
po zaakceptowaniu listy zadań i zleceniu kontynuacji ze wskazaniem blokad.
Ten zapis dotyczy S3 i nie zastępuje otwartych ustaleń S1 ani S2.
Publikacja pozostaje odłożona.

**Sprawdzone źródła:** opis S3 w tym planie, standard zadań dla juniora,
sekcja 5.2 specyfikacji (REQ-015–REQ-019, REQ-071), AC-06–AC-08 i AC-33,
OD-06, rejestr ustaleń i sekcja 6 projektu walidacji. Przejrzano dotyczące
reguł fragmenty ogólnego LLD, modelu danych, kontraktów API i opisu
serwisów. Nie jest to pełny przegląd tych dokumentów ani implementacji.
Repozytorium nie zawiera jeszcze kodu aplikacji i konfiguracji testów.

**Ustalone:** użytkownik zatwierdza interpretację i znaczenie sprawdzenia
przed generowaniem. Wykryte konflikty wymagają wyjaśnienia. Wskazówki
jakościowe nie są automatycznie zaliczanymi testami. Ograniczona reguła
sumująca należy do MVP; wartości pozycji zaokrąglamy przed sumowaniem.
S3 definiuje znaczenie reguł, a S7 wykonuje sprawdzenia na danych.
Integracja dostawców modeli pozostaje w S5.

**Decyzja użytkownika — 14 listopada 2026:** zatwierdzono rozszerzenie
katalogu MVP o porównanie kolumn, porównanie wartości z progiem, zakresem
lub zbiorem oraz regułę warunkową. Razem z ograniczoną regułą sumującą
to cztery rodzaje reguł objęte MVP. Decyzję zapisano w sekcji 5.2
specyfikacji i OD-06 oraz powiązanej dokumentacji. Nie zatwierdzono przez
to operatorów, typów, znaczenia NULL ani kontraktów wykonawczych.

**Kolejna decyzja użytkownika — 14 listopada 2026:** zatwierdzono dwa
zakresy obowiązywania. Zatwierdzone reguły projektu obowiązują we
wszystkich jego nowych zleceniach. Reguła dodana do pojedynczego zlecenia
dotyczy tylko jego i nie zapisuje się automatycznie w projekcie. Wykryty
konflikt wymaga wyjaśnienia; nie ma cichego nadpisania reguły projektu.
Nie zatwierdzono przez to modelu przechowywania ani szczegółów interfejsu.

**Decyzja o nieobsługiwanej regule — 14 listopada 2026:** użytkownik
wybrał blokadę startu oraz informację z wyborem kontynuowania bez tej
reguły albo jej poprawienia. Bez świadomego wyboru generowanie nie rusza.
Przy poprawie wymagane są obsługiwana interpretacja i jej zatwierdzenie.
Pominięcie nie jest pozytywnym wynikiem sprawdzenia ani automatyczną
zamianą we wskazówkę jakościową. Zaktualizowano REQ-017 i AC-06.

**Decyzja o zakresie pominięcia — 14 listopada 2026:** użytkownik
zatwierdził pominięcie nieobsługiwanej reguły projektu wyłącznie
w bieżącym zleceniu, bez zmiany lub usunięcia zapisanej reguły.
W kolejnych nowych zleceniach reguła nadal obowiązuje; jej ponowne
pominięcie wymaga świadomej decyzji użytkownika.

**Decyzja o mechanizmie — 14 listopada 2026:** użytkownik zatwierdził
propozycję rodzaju reguły i parametrów od LLM, kontrolę obsługiwalności
przez aplikację, zatwierdzenie czytelnego opisu przez użytkownika oraz
sprawdzanie danych gotowym mechanizmem, bez wykonywania kodu modelu.
Zaktualizowano REQ-016, OD-06 i projekt walidacji.

**Do wyjaśnienia przed instrukcjami implementacji — stan po analizie:**
format definicji reguł, kontrakty API, zapis oraz szczegóły interpretacji,
prezentacji, zatwierdzania i obsługi konfliktów. W sumowaniu pozostają
zakres parametru precyzji, NULL w kluczu relacji oraz jednostka
i raportowanie naruszeń. Uzgodnionych niżej operatorów, typów i zasad
prostych porównań oraz reguł warunkowych nie otwieramy ponownie.
Propozycje tabel, API i modułów w LLD nie są zatwierdzonymi instrukcjami.

#### Uzgodniony podział S3 na zadania

**Decyzja użytkownika — 14 listopada 2026:** zaakceptowano podział
S3-T1–S3-T5, ich rezultaty, granice i proponowaną kolejność.
**Status wszystkich pozycji: uzgodnione na poziomie podziału, szczegółowe
opisy do dopracowania.** Akceptacja nie rozstrzyga otwartych szczegółów
OD-06 ani kontraktów. Identyfikatory zachowujemy przy dalszym dopracowaniu.
Nie utworzono podzadań ani issues.

| ID | Zadanie | Oczekiwany rezultat | Zależności |
| --- | --- | --- | --- |
| S3-T1 | Dodać model definicji reguł i kontrolę ich obsługiwalności | Aplikacja rozpoznaje definicje czterech uzgodnionych rodzajów reguł, sprawdza kompletność parametrów i zgodność odwołań ze schematem. Odróżnia je od wskazówek jakościowych i nie przyjmuje dowolnego kodu do wykonania. Dotyczy również parametrów reguły sumującej, nie jej wykonania na danych. | Model schematu S2; uzgodnienie szczegółowego kontraktu i znaczenia reguł w OD-06. |
| S3-T2 | Dodać zapis i odczyt reguł projektu oraz zlecenia | Reguły i wskazówki zachowują treść, interpretację i właściwy zakres. Zatwierdzone reguły projektu trafiają do jego nowych zleceń; reguły zlecenia nie zapisują się automatycznie w projekcie. Pominięcie nieobsługiwanej reguły nie zmienia jej zapisu w projekcie. | S3-T1; projekty S2; fundament magazynu z S1; uzgodniony kontrakt zlecenia z S4. |
| S3-T3 | Podłączyć interpretację tekstu reguły przez LLM | Powstaje propozycja rodzaju reguły, parametrów i czytelnego znaczenia. Wynik podlega kontroli S3-T1, pozostaje niezatwierdzony i pozwala doprecyzować niejasności. Wskazówki jakościowe pozostają odrębne; wykryte konflikty są przekazywane do rozstrzygnięcia. | S3-T1–S3-T2; operacja interpretacji i integracja modeli z S5. |
| S3-T4 | Dodać zatwierdzanie reguł i rozstrzyganie blokad zlecenia | Backend udostępnia zatwierdzoną interpretację i informację o blokadach przygotowania zlecenia. Wykryty konflikt wymaga wyjaśnienia. Dla nieobsługiwanej reguły użytkownik wybiera poprawę lub pominięcie tylko w bieżącym zleceniu; brak decyzji zachowuje blokadę. | S3-T1–S3-T3; uzgodniony kontrakt przygotowania zlecenia z S4. |
| S3-T5 | Dodać interfejs wprowadzania, wyjaśniania i zatwierdzania reguł | Użytkownik podaje regułę dla projektu lub zlecenia, widzi proponowane znaczenie i status, doprecyzowuje ją i zatwierdza. Przy nieobsługiwanej regule widzi informację oraz wybór kontynuowania bez niej albo poprawy; pominięcie nie jest prezentowane jako spełnienie. | Odpowiednie operacje S3-T2–S3-T4; fundament frontendu S1 i uzgodnione miejsce interakcji z S4. |

**Uzgodniona kolejność:** S3-T1 → S3-T2 → S3-T3 → S3-T4.
S3-T5 można rozwijać po udostępnieniu odpowiednich operacji backendu.
Testy zachowania należą do każdego zadania, nie do osobnego etapu.

**Granice:** S3-T1 sprawdza definicję reguły, a nie wygenerowaną paczkę.
S7 wykonuje obliczenia i sprawdzenia na danych oraz zwraca naruszenia.
S3-T3 nie tworzy drugiej integracji z dostawcami modeli poza S5.
S3-T4 dostarcza stan zatwierdzenia i blokad; S4 składa całe zlecenie,
a S6 steruje wykonaniem. S3-T5 nie implementuje całego czatu ani jego
cyklu życia. S3-T2 zapewnia operacje zapisu i odczytu; decyzje i zmiany
stanu zatwierdzenia wykonuje S3-T4, bez powielania logiki zapisu.

**Pokrycie źródeł:** REQ-015 → S3-T2 i S3-T5;
REQ-016 → S3-T1, S3-T3–S3-T5; REQ-017 → S3-T1 i S3-T3–S3-T5;
REQ-018 → S3-T1–S3-T3 i S3-T5; REQ-019 → S3-T3–S3-T5;
REQ-071 → definicja w S3-T1, interpretacja i zatwierdzenie w S3-T3–S3-T5,
wykonanie sprawdzenia w S7. AC-06 i AC-08 obejmują S3-T3–S3-T5;
AC-07 wymaga także przekazania wskazówek do S5 i poprawnego raportu S8;
AC-33 wymaga definicji S3 i sprawdzenia na danych S7.

**Bieżący element:** przegląd szkiców wszystkich pięciu zadań poniżej.
Historia decyzji dotyczących S3-T1 pozostaje podstawą ich zakresu.
Nie wracamy do analizy każdej reguły od początku.

**Decyzja dotycząca S3-T1 — 14 listopada 2026:** użytkownik zatwierdził
ograniczenie rodzaju „porównanie kolumn” do dwóch kolumn tego samego
rekordu w jednej tabeli. Porównania kolumn różnych rekordów lub tabel
nie należą do tego rodzaju. Osobna reguła sumująca pozostaje w MVP.
Zaktualizowano sekcję 5.2 specyfikacji, OD-06 i powiązane opisy.

**Decyzja o operacjach porównania — 14 listopada 2026:** użytkownik
zatwierdził sześć operacji: równe, różne, mniejsze, mniejsze lub równe,
większe i większe lub równe. Nie rozstrzyga to obsługiwanych par typów,
dopuszczalnych dla nich operacji, znaczenia NULL ani zapisu operatorów
w definicji. Zaktualizowano sekcję 5.2 specyfikacji i OD-06.

**Decyzja o macierzy typów — 14 listopada 2026:** użytkownik
zaakceptował poniższe pary typów i dostępne operacje porównania kolumn.
Zapisano je w sekcji 5.2 specyfikacji i częściowo rozstrzygnięto OD-06.

| Para typów — uzgodnione | Operacje |
| --- | --- |
| Dowolna para spośród `smallint`, `integer`, `bigint`, `numeric`/`decimal` | Wszystkie sześć. |
| `date` z `date` | Wszystkie sześć. |
| `timestamp` z `timestamp` | Wszystkie sześć. |
| `timestamptz` z `timestamptz` | Wszystkie sześć. |
| Dowolna para spośród `text` i `varchar` | Równe, różne. |
| `boolean` z `boolean` | Równe, różne. |
| `uuid` z `uuid` | Równe, różne. |

Decyzja wyklucza pozostałe pary oraz automatyczne konwersje poza
porównaniami wewnątrz wymienionych grup. Nie dopuszcza np. porównywania
liczby z tekstem ani `date` z `timestamp`. Nie rozstrzyga znaczenia NULL,
szczegółów porównań tekstowych ani formatu definicji. To zakres produktu,
nie twierdzenie o pełnych możliwościach PostgreSQL.

**Decyzja o NULL w porównaniu kolumn — 14 listopada 2026:** użytkownik
zatwierdził, że NULL w którejkolwiek z porównywanych kolumn oznacza
naruszenie, także gdy obie wartości są NULL. Rekordu nie pomijamy ani
nie uznajemy porównania za spełnione. Nie zmieniamy oryginalnego DDL
ani nie rozszerzamy tej zasady na pozostałe rodzaje reguł. Zaktualizowano
sekcję 5.2 specyfikacji, OD-06 i powiązane opisy.

**Decyzja o tekście w porównaniu kolumn — 14 listopada 2026:**
użytkownik zatwierdził dokładne porównywanie treści, z uwzględnieniem
wielkości liter i wszystkich spacji, bez automatycznego przekształcania.
„ABC” i „abc” są różne, podobnie „ABC” i „ABC ”. Decyzja nie wybiera
biblioteki ani mechanizmu wykonania. Zaktualizowano sekcję 5.2
specyfikacji, OD-06 i powiązane opisy.

**Decyzja o zakresie i jednostce naruszenia — 14 listopada 2026:**
użytkownik zatwierdził sprawdzanie wszystkich rekordów wskazanej tabeli
w zaimportowanej paczce oraz liczenie jednego niezgodnego rekordu jako
jednego naruszenia tej reguły. Dotyczy to również rekordu z NULL w obu
porównywanych kolumnach. Wynik pokazuje liczbę naruszeń wobec liczby
sprawdzonych rekordów, np. 7 wśród 100. Nie rozszerzono tej decyzji
na pozostałe rodzaje reguł. Zaktualizowano sekcję 5.2 specyfikacji i OD-06.

**Decyzja o zakresie porównania ze stałą — 14 listopada 2026:**
użytkownik zatwierdził pojedynczą kolumnę rekordu porównywaną ze stałą
wartością, stałymi granicami zakresu albo jawnym zbiorem stałych wartości,
bez obliczeń i odwołań do innych rekordów lub tabel. Reguła sumująca
pozostaje osobnym rodzajem. Nie rozstrzygnięto operatorów, granic zakresu,
typów stałych, NULL ani jednostki naruszenia. Zaktualizowano sekcję 5.2
specyfikacji, OD-06 i powiązane opisy.

**Decyzja o domknięciu zakresu — 14 listopada 2026:** użytkownik
zatwierdził, że wariant „wartość w zakresie” obejmuje obie granice,
np. dla 18–65 dopuszcza również 18 i 65. W tym wariancie MVP nie ma
wyboru granic otwartych. Nie rozstrzygnięto poprawności równych lub
odwróconych granic, obsługiwanych typów, NULL ani pozostałych operacji.
Zaktualizowano sekcję 5.2 specyfikacji, OD-06 i powiązane opisy.

**Decyzja o poprawności granic — 14 listopada 2026:** użytkownik
zatwierdził zasadę: dolna granica musi być mniejsza lub równa górnej.
Zakres 18–18 jest poprawny i dopuszcza tylko 18. Zakres 65–18 jest
błędną definicją: aplikacja wyświetla zrozumiały błąd i nie zamienia
granic automatycznie. Zaktualizowano sekcję 5.2 specyfikacji, OD-06
i powiązane opisy. Typy i znaczenie NULL nadal pozostają otwarte.

**Decyzja o operacjach porównania z pojedynczą stałą — 14 listopada 2026:**
Dla porównania kolumny z pojedynczą stałą uzgodniono sześć operacji: równe, różne, mniejsze, mniejsze lub równe, większe oraz większe lub równe. To katalog operacji, nie dopuszczenie każdej z nich dla każdego typu. Macierz typów, znaczenie NULL i zapis operatorów pozostają otwarte. Zaktualizowano sekcję 5.2 specyfikacji, OD-06 i powiązane opisy.

**Decyzja o macierzy porównania z pojedynczą stałą — 14 listopada 2026:**
użytkownik zatwierdził wszystkie sześć operacji dla kolumn `smallint`,
`integer`, `bigint`, `numeric`/`decimal`, `date`, `timestamp` i `timestamptz`;
tylko równe i różne dla `text`, `varchar`, `boolean` i `uuid`.
Zgodność typu stałej z kolumną, konwersje, porównywanie tekstu, NULL i zapis
definicji pozostają otwarte. Nie rozszerzono macierzy na zakresy ani zbiory.
Zaktualizowano sekcję 5.2 specyfikacji, OD-06 i powiązane opisy.

**Decyzja o zgodności typów w porównaniu z pojedynczą stałą — 14 listopada 2026:**
W porównaniu z pojedynczą stałą wymagamy zgodności typów: liczby porównujemy w grupie smallint/integer/bigint/numeric/decimal, tekst w grupie text/varchar, a date, timestamp, timestamptz, boolean i uuid każde wyłącznie ze stałą swojego typu. Pozostałe pary są nieobsługiwane, bez automatycznych konwersji między grupami, np. liczba–tekst i date–timestamp. Dotyczy to typów w definicji reguły, nie sposobu rozpoznawania polecenia przez LLM. Format stałych, znaczenie NULL, szczegóły porównywania tekstu i zapis operatorów pozostają otwarte.
Decyzji nie rozszerzono na zakresy ani zbiory. Zaktualizowano sekcję 5.2
specyfikacji, OD-06 i powiązane opisy.

**Decyzja o NULL w kolumnie porównywanej ze stałą — 14 listopada 2026:**
W porównaniu kolumny z pojedynczą stałą inną niż NULL brak wartości (NULL) w kolumnie zawsze oznacza naruszenie, także przy operacji „różne”. Rekordu nie pomijamy ani nie uznajemy za zgodny. Na przykład brak statusu narusza regułę „status różny od anulowany”. Nie zmieniamy oryginalnego DDL. Decyzja nie rozstrzyga użycia NULL jako stałej ani zasad dla zakresów i zbiorów.
Zaktualizowano sekcję 5.2 specyfikacji, OD-06 i powiązane opisy.

**Decyzja o tekście w porównaniu z pojedynczą stałą — 14 listopada 2026:**
Równość i różność tekstu w porównaniu kolumny z pojedynczą stałą dotyczą dokładnej treści, z uwzględnieniem wielkości liter i wszystkich spacji, bez automatycznego przekształcania. „ABC” jest różne od „abc” i od „ABC ” (ze spacją na końcu). Decyzji nie rozszerzono na zakresy ani zbiory.
Zaktualizowano sekcję 5.2 specyfikacji, OD-06 i powiązane opisy.

**Decyzja o zakresie i jednostce naruszenia porównania ze stałą — 14 listopada 2026:**
Porównanie z pojedynczą stałą obejmuje wszystkie rekordy wskazanej tabeli w zaimportowanej paczce. Każdy niezgodny rekord, także z NULL, oznacza jedno naruszenie tej reguły. Przykładowo 7 niezgodnych rekordów spośród 100 daje 7 naruszeń wśród 100 sprawdzonych. Decyzja nie ustala zakresu sprawdzania ani jednostki naruszenia dla zakresów i zbiorów.
Zaktualizowano sekcję 5.2 specyfikacji, OD-06 i powiązane opisy.

**Decyzja o NULL po stronie stałej — 14 listopada 2026:**
W wariancie porównania z pojedynczą stałą NULL nie może występować po stronie stałej. Definicje „równe NULL” i „różne od NULL” są nieobsługiwane w tym wariancie; aplikacja podaje czytelną przyczynę zamiast wykonywać zwykłe porównanie. Ewentualne osobne sprawdzanie obecności lub braku wartości pozostaje do ustalenia. Nie usuwa to uzgodnionego wymagania obsługi reguły warunkowej z wymaganą datą dostawy przy określonym statusie.
Zaktualizowano sekcję 5.2 specyfikacji, OD-06 i powiązane opisy.

**Decyzja o typach kolumn dla zakresu — 14 listopada 2026:**
Wariant „wartość w zakresie” obsługuje wyłącznie kolumny smallint, integer, bigint, numeric/decimal, date, timestamp i timestamptz. Zakresy dla text, varchar, boolean i uuid są nieobsługiwane. Zgodność i zapis typów granic, znaczenie NULL, zakres sprawdzania i jednostka naruszenia nadal wymagają ustaleń.
Zaktualizowano sekcję 5.2 specyfikacji, OD-06 i powiązane opisy.

**Decyzja o zgodności typów granic zakresu — 14 listopada 2026:**
Dla kolumny liczbowej obie granice zakresu są liczbami ze wspólnej grupy smallint/integer/bigint/numeric/decimal. Dla date, timestamp i timestamptz obie granice mają dokładnie ten sam typ co kolumna. Pozostałe połączenia są nieobsługiwane, bez automatycznych konwersji między tymi grupami, np. tekst–liczba i date–timestamp. Dotyczy to typów w definicji reguły, nie rozpoznawania polecenia przez LLM.
Format granic i znaczenie NULL nadal pozostają otwarte. Zaktualizowano
sekcję 5.2 specyfikacji, OD-06 i powiązane opisy.

**Decyzja o NULL w kolumnie sprawdzanej regułą zakresu — 14 listopada 2026:**
W wariancie „wartość w zakresie” NULL w sprawdzanej kolumnie zawsze oznacza naruszenie reguły. Rekordu nie pomijamy i nie zmieniamy oryginalnego DDL. Na przykład brak wieku narusza regułę „wiek w zakresie 18–65”. Decyzja nie rozstrzyga dopuszczalności NULL lub braku granicy w definicji ani zakresu sprawdzania i jednostki naruszenia.
Zaktualizowano sekcję 5.2 specyfikacji, OD-06 i powiązane opisy.

**Decyzja o wymaganiu obu granic innych niż NULL — 14 listopada 2026:**
Wariant „wartość w zakresie” wymaga obu granic innych niż NULL. Brak którejkolwiek granicy lub NULL zamiast niej oznacza błędną definicję z czytelnym komunikatem. Nie traktujemy brakującej granicy jako nieskończoności. Warunki jednostronne, np. „wiek co najmniej 18”, można opisać porównaniem z pojedynczą stałą.
Zaktualizowano sekcję 5.2 specyfikacji, OD-06 i powiązane opisy.

**Korekta sposobu analizy — 14 listopada 2026:** użytkownik zwrócił uwagę
na powtarzające się pytania o ten sam sposób liczenia naruszeń dla różnych
wariantów porównań. Dalej grupujemy wspólne zasady w jedną propozycję,
a osobno pytamy o rzeczywiste różnice. Nadal obowiązuje jedno pytanie
naraz. Uwaga użytkownika i polecenie kontynuacji nie oznaczają akceptacji
otwartej zasady dla zakresu ani zbioru.

**Pozostały zakres przygotowania opisów S3 — aktualny stan:**
- Rozstrzygnąć trzy otwarte szczegóły sumowania wymienione pod koniec
  historii decyzji. Wspólne zasady prostych porównań, zbioru i reguł
  warunkowych są już uzgodnione; nie zadawać ponownie tych samych pytań.
- Uzgodnić format definicji i potrzebne kontrakty, zapis reguł projektu
  i zlecenia oraz powiązania z S2, S4, S5 i S7. Nie powielać ich implementacji.
- Doprecyzować interpretację, poprawianie, zatwierdzanie i konflikty,
  w tym stany i błędy, których dotychczasowe ustalenia nie rozstrzygają.
- Doprecyzować potrzebne widoki i działania użytkownika, a następnie
  uzupełnić i uzgodnić przygotowane niżej szkice S3-T1–S3-T5.
  Lista pięciu zadań jest zaakceptowana; szkice mają kryteria ukończenia
  i planowane przypadki sprawdzające, ale blokady uniemożliwiają
  traktowanie ich jako gotowych instrukcji. Podzadania wydzielimy
  tylko tam, gdzie powstanie odrębny, sprawdzalny rezultat.
To mapa pozostałej pracy, nie nowy backlog ani zgoda na rozwiązania.

**Decyzja o wspólnej zasadzie prostych porównań — 14 listopada 2026:**
Dla prostych porównań (kolumna–kolumna, pojedyncza stała, zakres i zbiór) obowiązuje wspólna zasada: sprawdzamy wszystkie rekordy wskazanej tabeli w zaimportowanej paczce; każdy niezgodny rekord oznacza jedno naruszenie danej reguły. Wynik podaje liczbę naruszeń wobec liczby sprawdzonych rekordów, np. 7 wśród 100. Nie rozstrzyga to znaczenia NULL dla zbioru ani zasad reguł warunkowych i sumujących.
Zaktualizowano sekcję 5.2 specyfikacji, OD-06 i powiązane opisy.
Nie pytamy ponownie o tę zasadę dla poszczególnych wariantów.

**Decyzja o operacjach porównania ze zbiorem — 14 listopada 2026:**
Porównanie ze zbiorem obsługuje dwie operacje: „należy do zbioru” oraz „nie należy do zbioru”. Przykładowo status ma należeć do listy {nowy, opłacony, wysłany} albo nie należeć do listy {anulowany, odrzucony}. Typy elementów, NULL, pusty zbiór i szczegóły porównywania tekstu nadal wymagają ustaleń.
Zaktualizowano sekcję 5.2 specyfikacji, OD-06 i powiązane opisy.

**Decyzja o poprawności zawartości zbioru — 14 listopada 2026:**
W obu operacjach porównania ze zbiorem definicja musi zawierać niepustą listę stałych innych niż NULL. Pusta lista lub NULL jako element oznacza błędną definicję z czytelną informacją o przyczynie, zamiast wykonania reguły. Dotyczy to listy w definicji, nie braku wartości w sprawdzanym rekordzie.
Zaktualizowano sekcję 5.2 specyfikacji, OD-06 i powiązane opisy.

**Decyzja o znaczeniu operacji zbioru — 14 listopada 2026:**
Obie operacje zbioru korzystają z uzgodnionych zasad porównania z pojedynczą stałą: „należy” wymaga spełnienia porównania „równe” z co najmniej jednym elementem, a „nie należy” spełnienia porównania „różne” ze wszystkimi elementami. Każdy element musi być zgodny typowo z kolumną: liczby w grupie smallint/integer/bigint/numeric/decimal, tekst w grupie text/varchar, a date, timestamp, timestamptz, boolean i uuid każde ze swoim typem. Nie stosujemy konwersji między tymi grupami i nie pomijamy niezgodnych elementów definicji. Tekst porównujemy dokładnie, z uwzględnieniem wielkości liter i wszystkich spacji. NULL w sprawdzanej kolumnie oznacza naruszenie w obu operacjach.
Zaktualizowano sekcję 5.2 specyfikacji, OD-06 i powiązane opisy.
Format zapisu definicji nadal wymaga uzgodnienia.

**Decyzja o postaci reguły warunkowej — 14 listopada 2026:**
Reguła warunkowa w MVP ma postać „jeśli jeden warunek, to jedno wymaganie” i dotyczy tego samego rekordu jednej tabeli. Nie ma gałęzi „w przeciwnym razie” ani zagnieżdżonych reguł. Przykład: jeśli status jest równy „wysłany”, data dostawy musi być podana. Osobna reguła sumująca między tabelami pozostaje w MVP.
Katalog warunków i wymagań, znaczenie NULL, wynik dla niespełnionego warunku oraz zakres sprawdzania i jednostka naruszenia reguły warunkowej nadal wymagają ustaleń.
Zaktualizowano sekcję 5.2 specyfikacji, OD-06 i powiązane opisy.

**Decyzja o katalogu składników reguły warunkowej — 14 listopada 2026:**
Warunek i wymaganie korzystają z tego samego katalogu pojedynczych sprawdzeń: porównanie dwóch kolumn, porównanie z pojedynczą stałą, zakres, zbiór, „wartość jest NULL” oraz „wartość nie jest NULL”. Każdy człon jest jednym sprawdzeniem, bez łączenia przez „i”/„lub”; wszystkie odwołania dotyczą tego samego rekordu. „Wartość nie jest NULL” oznacza obecność wartości, nie sprawdzanie niepustości tekstu.
Ocena całej reguły warunkowej, w tym NULL w warunku i wynik dla niespełnionego warunku, oraz zakres sprawdzania i jednostka naruszenia nadal wymagają ustaleń.
Zaktualizowano sekcję 5.2 specyfikacji, OD-06 i powiązane opisy.

**Decyzja o modelu oceny reguły warunkowej — 14 listopada 2026:**
Gdy warunek jest spełniony, oceniamy wymaganie: jego spełnienie oznacza zgodność, a niespełnienie naruszenie. Gdy warunek jest niespełniony przy dostępnych danych, wynik to „nie dotyczy”: wymagania nie oceniamy i nie zgłaszamy naruszenia. NULL w wartości potrzebnej do zwykłego porównania w warunku oznacza naruszenie całej reguły, a nie „nie dotyczy”. Jawne sprawdzenia „jest NULL” i „nie jest NULL” normalnie rozstrzygają warunek. Na przykład dla „jeśli status = wysłany, data dostawy nie jest NULL” status nowy daje „nie dotyczy”, status wysłany bez daty naruszenie, a status NULL również naruszenie.
Zakres sprawdzania, jednostka naruszenia i liczniki raportu reguły warunkowej nadal wymagają ustaleń.
Zaktualizowano sekcję 5.2 specyfikacji, OD-06 i powiązane opisy.

**Decyzja o raportowaniu reguły warunkowej — 14 listopada 2026:**
Reguła warunkowa obejmuje wszystkie rekordy wskazanej tabeli w zaimportowanej paczce. Raport rozlicza je w trzech rozłącznych grupach: zgodne, naruszenia i „nie dotyczy”. Każdy rekord trafia do jednej grupy i daje najwyżej jedno naruszenie danej reguły, również przy NULL w warunku. Rekordów „nie dotyczy” nie przedstawiamy jako spełniających wymaganie. Przykładowo 100 ocenionych rekordów to 35 zgodnych, 5 naruszeń i 60 „nie dotyczy”.
Zaktualizowano sekcję 5.2 specyfikacji, OD-06 i powiązane opisy.
Format pól raportu i kontrakt API nadal pozostają otwarte.

**Decyzja o powiązaniu i zakresie sumowania — 14 listopada 2026:**
Reguła sumująca obejmuje wszystkie pozycje danego rekordu nadrzędnego w paczce, powiązane jedną jawnie wskazaną obowiązującą relacją. Nie obejmuje dodatkowego filtrowania pozycji ani przechodzenia przez kolejne tabele. Relacja pochodzi z DDL albo jest zatwierdzona poza nim zgodnie z REQ-012; aplikacja nie wybiera jej domyślnie. Przykład: wartość zamówienia równa sumie ilość × cena wszystkich jego pozycji, a nie tylko pozycji wybranego statusu.
Zaktualizowano sekcję 5.2 specyfikacji, OD-06 i powiązane opisy.

**Decyzja o precyzji jako parametrze reguły sumującej — 14 listopada 2026:**
Liczba miejsc po przecinku, do której zaokrąglamy iloczyn każdej pozycji, jest jawnym parametrem konkretnej reguły sumującej, widocznym w interpretacji do zatwierdzenia. Reguły mogą wskazywać różną precyzję, np. 2 albo 3 miejsca. Nie narzucamy dwóch miejsc wszystkim regułom ani nie wyprowadzamy precyzji po cichu ze schematu.
Dozwolony zakres parametru precyzji i tryb zaokrąglania pozostają otwarte.
Zaktualizowano sekcję 5.2 specyfikacji, OD-06 i powiązane opisy.

**Decyzja o trybie zaokrąglania — 14 listopada 2026:**
W MVP stosujemy jeden tryb zaokrąglania iloczynu pozycji: do najbliższej wartości o zadanej liczbie miejsc, a przy dokładnej połowie — od zera. Dla 2 miejsc: 1,234 daje 1,23; 1,235 daje 1,24; −1,235 daje −1,24. Tryb jest stałą zasadą aplikacji, widoczną w interpretacji reguły, bez wyboru innego trybu.
Dozwolony zakres parametru precyzji pozostaje otwarty.
Zaktualizowano sekcję 5.2 specyfikacji, OD-06 i powiązane opisy.

**Decyzja o NULL w polach obliczenia reguły sumującej — 14 listopada 2026:**
NULL w wartości rekordu nadrzędnego albo w którymkolwiek z dwóch mnożonych pól którejkolwiek powiązanej pozycji oznacza naruszenie reguły sumującej dla rekordu nadrzędnego. Nie zastępujemy NULL zerem i nie pomijamy niekompletnych pozycji. Na przykład zamówienie z pozycją bez ceny narusza regułę, zamiast być sprawdzane wyłącznie na podstawie sumy pozostałych pozycji.
Zaktualizowano sekcję 5.2 specyfikacji, OD-06 i powiązane opisy.
Brak pozycji, NULL w kluczu relacji i jednostka naruszenia pozostają otwarte.

**Decyzja o sumie przy braku pozycji — 14 listopada 2026:**
Przy braku powiązanych pozycji suma wynosi 0. Rekord nadrzędny bez pozycji spełnia regułę sumującą wyłącznie wtedy, gdy jego wartość wynosi 0; inna wartość daje naruszenie, a NULL pozostaje naruszeniem zgodnie z zasadą brakujących wartości. Brak pozycji sam w sobie nie narusza tej reguły. Nie zmienia to wymagań DDL ani innych reguł, które mogą wymagać istnienia pozycji.
Zaktualizowano sekcję 5.2 specyfikacji, OD-06 i powiązane opisy.

**Decyzja o dokładnym porównaniu wyniku sumowania — 14 listopada 2026:**
Wartość nadrzędną porównujemy dokładnie z sumą już zaokrąglonych pozycji, bez tolerancji różnicy i bez dodatkowego zaokrąglania wartości nadrzędnej lub sumy. Porównujemy wartość liczbową, nie liczbę zer w zapisie. Dla sumy 19,99 wartość nadrzędna 19,990 daje zgodność, a 19,991 naruszenie.
Zaktualizowano sekcję 5.2 specyfikacji, OD-06 i powiązane opisy.
Typy pól i techniczna reprezentacja obliczeń nadal wymagają ustaleń.

**Decyzja o dziedzinie i dokładności sumowania — 14 listopada 2026:**
Reguła sumująca operuje wyłącznie na typach smallint, integer, bigint i numeric/decimal we wszystkich trzech polach: wartości nadrzędnej oraz obu mnożonych polach pozycji. Obliczenia zachowują dokładność dziesiętną, bez przybliżania przez binarne liczby zmiennoprzecinkowe i bez automatycznej zamiany tekstu na liczby. Nie wybiera to biblioteki ani reprezentacji API.
Zaktualizowano sekcję 5.2 specyfikacji, OD-06 i powiązane opisy.

**Stan po pytaniu użytkownika o pozostałą analizę:** dziedzina sumowania
jest zaakceptowana. Do wyjaśnienia w tym rodzaju reguły pozostają trzy
zagadnienia: dozwolony zakres parametru precyzji, obsługa NULL w kluczu
relacji oraz jednostka i raportowanie naruszeń. Osobno nadal otwarte są
kontrakty definicji i API oraz szczegóły zapisu, interpretacji,
zatwierdzania, konfliktów i interfejsu S3-T2–S3-T5. To lista zagadnień,
nie deklaracja dokładnej liczby przyszłych pytań.

**Zlecenie i rezultat kontynuacji:** użytkownik odpowiedział „dawaj”
na propozycję przygotowania szkiców bez kolejnej serii drobnych pytań.
Zapisano poniżej opisy S3-T1–S3-T5 na podstawie uzgodnionego zakresu,
z jawnymi blokadami „do wyjaśnienia”. Zlecenie przygotowania szkiców
nie jest akceptacją ich szczegółów ani brakujących rozwiązań.

**Najbliższa nierozstrzygnięta decyzja sumowania:** dozwolony zakres
liczby miejsc po przecinku. Nie zaproponowano ani nie przyjęto limitu.
Nie wracać do rozstrzygniętych zasad prostych porównań, reguł warunkowych
i obliczeń sumowania. Nie wykonano implementacji, testów aplikacji
ani publikacji.

#### S3 — pakiet do późniejszego przeniesienia na GitHub

**Zlecenie użytkownika — 14 listopada 2026:** zachować opisy S3
w repozytorium tak, aby można było łatwo dodać je do GitHub Project
po odzyskaniu dostępu. Ten dokument pozostaje jedynym źródłem opisów;
nie tworzymy drugiego, niezależnie edytowanego backlogu.

**Stan pakietu:** pięć szkiców pokrywa cały uzgodniony zakres S3.
Nie oznacza to gotowości do implementacji ani akceptacji otwartych
kontraktów. Każdy opis zawiera blokady, zależności i plan sprawdzeń.
Żaden z poniższych elementów nie został w ramach tego zlecenia
utworzony ani dodany do projektu na GitHubie.

**Zapisany cel późniejszej publikacji:** repozytorium
`jwieczor03/mgr-llm-data-generator`, GitHub Project
„Generator danych — MVP” na koncie `jwieczor03`.
Dostęp, istnienie projektu i wcześniejszych issues trzeba sprawdzić
ponownie przed publikacją; historyczna kontrola nie potwierdza
dzisiejszego stanu.

**Indeks opisów i miejsce zapisu wyników publikacji:**

| ID | Tytuł przyszłego issue / opis do skopiowania | Rodzic | Issue URL | Dodano do Project |
| --- | --- | --- | --- | --- |
| S3 | [S3 — Reguły biznesowe i ich zatwierdzanie](#s3--reguły-biznesowe-i-ich-zatwierdzanie) | Obszar nadrzędny | Nie opublikowano | Nie |
| S3-T1 | [S3-T1 — Dodać model definicji reguł i kontrolę ich obsługiwalności](#s3-t1--dodać-model-definicji-reguł-i-kontrolę-ich-obsługiwalności) | S3 | Nie opublikowano | Nie |
| S3-T2 | [S3-T2 — Dodać zapis i odczyt reguł projektu oraz zlecenia](#s3-t2--dodać-zapis-i-odczyt-reguł-projektu-oraz-zlecenia) | S3 | Nie opublikowano | Nie |
| S3-T3 | [S3-T3 — Podłączyć interpretację tekstu reguły przez LLM](#s3-t3--podłączyć-interpretację-tekstu-reguły-przez-llm) | S3 | Nie opublikowano | Nie |
| S3-T4 | [S3-T4 — Dodać zatwierdzanie reguł i rozstrzyganie blokad zlecenia](#s3-t4--dodać-zatwierdzanie-reguł-i-rozstrzyganie-blokad-zlecenia) | S3 | Nie opublikowano | Nie |
| S3-T5 | [S3-T5 — Dodać interfejs wprowadzania, wyjaśniania i zatwierdzania reguł](#s3-t5--dodać-interfejs-wprowadzania-wyjaśniania-i-zatwierdzania-reguł) | S3 | Nie opublikowano | Nie |

**Jak przenieść pakiet po uzyskaniu dostępu:**

1. Sprawdzić istniejące issues i elementy właściwego Project, aby nie
   tworzyć duplikatów. Użyć istniejącego rodzica S3, jeśli już powstał.
   Brak projektu wymaga osobnego uzgodnienia jego utworzenia.
2. Przed publikacją uzgodnić partię i status: obecne opisy są szkicami
   do dopracowania. Publikacja szkicu nie może oznaczać, że zadanie
   jest gotowe do implementacji; sekcje „Do wyjaśnienia” pozostają.
3. Tytuł issue wziąć z indeksu, zachowując ID. Do treści przenieść
   cały opis danego zadania od nagłówka do następnego zadania,
   wraz z kryteriami, planem sprawdzeń i blokadami. Dołączyć wspólne
   zastrzeżenia o stanie repozytorium i testach z początku sekcji
   szkiców albo jawne odwołanie do tej części planu.
4. Przy kopiowaniu zmienić względne odnośniki do dokumentacji na
   odnośniki działające z issue w docelowym repozytorium.
   Nie usuwać zależności od S1, S2, S4 i S5.
5. Połączyć T1–T5 z S3 jako zadania podrzędne. Zwykła wzmianka
   „rodzic S3” w opisie nie zastępuje relacji. Jeśli używane narzędzie
   nie pozwala zachować hierarchii, uzgodnić sposób jej odwzorowania.
6. Dodać issues do właściwego Project — samo utworzenie issue tego
   nie potwierdza. Pola, etykiety i statusy ustawiać tylko zgodnie
   z uzgodnionym sposobem prowadzenia projektu.
7. Po każdej udanej operacji uzupełnić powyżej URL i stan dodania.
   Oddzielnie sprawdzić opisy, hierarchię i obecność na tablicy.
   Przy częściowym powodzeniu kontynuować brakujący etap, bez
   ponownego tworzenia już zapisanych issues.

**Granice pakietu:** S3 definiuje, interpretuje, zapisuje i zatwierdza
reguły oraz pokazuje te działania użytkownikowi. Integracja dostawców
LLM pozostaje w S5, przygotowanie/start całego zlecenia w S4/S6,
wykonanie sprawdzeń na danych w S7, a raport w S8. Nie brakuje z tego
powodu szóstego zadania S3. Dalsze podzadania mogą jedynie rozbić
większe opisy na mniejsze rezultaty, bez automatycznego poszerzania zakresu.

#### Szkice szczegółowych opisów S3-T1–S3-T5

**Status: szkice do przeglądu, nie gotowe zadania implementacyjne.**
Poniższe kroki opisują uzgodnione zachowania. Części zależne od otwartych
decyzji pozostają wstrzymane; deweloper nie dobiera sam brakującego
kontraktu, semantyki ani rozwiązania architektonicznego.

**Wspólny punkt startowy:** repozytorium zawiera dokumentację, bez kodu
aplikacji i konfiguracji testów. Zatwierdzone miejsca przyszłego kodu
to backend `services/application-api/`, usługa modelowa
`services/generation-service/` oraz frontend `apps/web/`.
Moduły funkcji reguł są **do utworzenia, lokalizacja do ustalenia**.
Drzewo domeny, repozytoriów i operacji w
[LLD](lld/README.md), tabele w [modelu danych](lld/model_danych.md)
i operacje w [kontraktach API](lld/kontrakty_api.md) są materiałem
projektowym, nie automatycznie przyjętym kontraktem S3.

**Sprawdzanie:** każdy task obejmuje własne testy. Wymienione poniżej
przypadki są planem, nie wynikami wykonanych testów. Nie ma obecnie
sprawdzonej komendy uruchomienia aplikacji ani tych testów; trzeba ją
uzupełnić po dostarczeniu fundamentu S1 i uzgodnieniu narzędzi.
Ręczne kroki to przyszły odbiór użytkownika, nie osobne zadanie QA.

##### S3-T1 — Dodać model definicji reguł i kontrolę ich obsługiwalności

**Story nadrzędne:** S3 — Reguły biznesowe i ich zatwierdzanie.  
**Cel:** ustalić, czy proponowana definicja mieści się w możliwościach MVP,
zanim użytkownik ją zatwierdzi i zanim S7 sprawdzi dane.  
**Źródło:** [specyfikacja](specyfikacja_mvp.md), sekcja 5.2,
REQ-016–REQ-018, REQ-071, OD-06;
[walidacja](lld/walidacja.md), sekcja 6.  
**Punkt startowy:** wspólny punkt startowy powyżej; model schematu S2
oraz uzgodniony katalog i macierz typów w sekcji 5.2 specyfikacji.  
**Zależności:** fundament backendu S1; kontrakt tabel, kolumn, typów
i obowiązujących relacji z S2; rozstrzygnięcie formatu definicji.

**Co należy zrobić:**
1. Po uzgodnieniu formatu opisać cztery rodzaje definicji: porównanie
   kolumn, porównanie ze stałą/zakresem/zbiorem, warunkową i sumującą.
   Oddzielić definicję sprawdzalną od wskazówki jakościowej.
2. Kontrolować istnienie wskazanych obiektów w wybranym schemacie,
   kompletność parametrów oraz zgodność typów i operacji z macierzą.
   Porównanie kolumn ograniczyć do jednego rekordu jednej tabeli.
   Nie dodawać konwersji między grupami typów.
3. Dla zakresu wymagać obu granic innych niż NULL i dolnej nie większej
   od górnej. Dla zbioru wymagać niepustej listy stałych innych niż NULL,
   z poprawnym typem każdego elementu. Zwykłe porównanie ze stałą
   nie może używać NULL jako stałej.
4. W regule warunkowej dopuścić jeden warunek i jedno wymaganie
   z uzgodnionego katalogu, w tym jawne sprawdzenia NULL.
   Nie dopuścić else, zagnieżdżeń, AND/OR ani odwołań do innych rekordów.
5. W sumowaniu wymagać wartości nadrzędnej, dwóch pól pozycji,
   jednej jawnie wskazanej obowiązującej relacji oraz jawnej precyzji.
   Wszystkie trzy pola muszą należeć do grupy liczbowej
   smallint/integer/bigint/numeric/decimal. Nie dopuścić filtrów
   ani przechodzenia przez kolejne tabele. Kontrolę zakresu precyzji
   dopisać dopiero po jego uzgodnieniu.
6. Przekazywać czytelną przyczynę błędnej lub nieobsługiwanej definicji
   do interpretacji i zatwierdzania. Nie wykonywać kodu ani zapytań
   zaproponowanych przez model jako sposobu sprawdzenia.
7. Zapewnić, że przyjęta definicja jednoznacznie przekazuje do S7
   uzgodnione znaczenie NULL, tekstu, zakresu, liczników i obliczeń;
   nie implementować tutaj oceny rekordów.

**Poza zakresem:** wywołania LLM, zapis, decyzje użytkownika oraz
wykonywanie reguł na paczce i budowa raportu S7/S8.

**Kryteria ukończenia:**
- Obsługiwane definicje każdego rodzaju przechodzą kontrolę;
  brak pola, nieistniejąca kolumna i nieobsługiwana para typów
  dają rozpoznawalną przyczynę zamiast pozornej obsługi.
- Zakres 18–18 jest poprawny, 65–18 błędny, bez zamiany granic.
- Definicja nie może rozszerzyć katalogu przez dostarczenie kodu LLM.
- Kontrola definicji nie zwraca wyniku „dane spełniają regułę”.

**Jak sprawdzić — plan automatyczny:**
- Tabela przypadków dla całej macierzy typów i operacji: m.in.
  integer–numeric akceptowane; date–timestamp odrzucane;
  text–varchar tylko równe/różne.
- Zakres bez granicy, granica NULL, pusty zbiór, element NULL
  i niezgodny typ elementu — odrzucenie z przyczyną.
- Warunkowa „status równy wysłany → data nie jest NULL” przyjmowana;
  else, drugi warunek i odwołanie do innej tabeli odrzucane.
- Sumowanie z jawną relacją z DDL lub zatwierdzoną poza DDL
  dopuszczone w uzgodnionym zakresie; relacja tylko zaproponowana,
  brak precyzji i tekstowe pole ceny nie przechodzą kontroli.

**Odbiór ręczny:** po podłączeniu S3-T5 wprowadzić regułę obsługiwaną
i nieobsługiwaną; sprawdzić wyjaśnienie różnicy, bez uruchamiania
walidacji danych. Przed integracją przedstawić wyniki testów definicji.

**Do wyjaśnienia — blokady:** zapis operatorów, typowanych stałych,
dat i czasów oraz odwołań do obiektów schematu; format wyników kontroli
i przekazania definicji do S7. Dla sumowania: zakres precyzji,
NULL w kluczu relacji, jednostka i raportowanie naruszeń.
Nie wybieramy jeszcze biblioteki obliczeń ani sposobu transportu
dokładnych liczb dziesiętnych.

##### S3-T2 — Dodać zapis i odczyt reguł projektu oraz zlecenia

**Story nadrzędne:** S3 — Reguły biznesowe i ich zatwierdzanie.  
**Cel:** zachować treść i interpretację we właściwym zakresie,
bez przenoszenia reguł jednego zlecenia do całego projektu.  
**Źródło:** specyfikacja, sekcje 5.1–5.2, REQ-014–REQ-018;
[model danych](lld/model_danych.md), sekcja 3 — propozycja do dopracowania.  
**Punkt startowy:** przyszły backend `services/application-api/`;
operacje projektów S2 oraz model definicji S3-T1. Brak repozytorium
reguł i wykonanych migracji.  
**Zależności:** S3-T1; projekty i wersje schematu S2; magazyn S1;
kontrakt przygotowywanego zlecenia S4.

**Co należy zrobić:**
1. Po uzgodnieniu modelu danych przygotować zapis i odczyt tekstu,
   interpretacji, definicji, powiązania ze schematem i projektu/zlecenia.
   Wskazówki jakościowe zachować oddzielnie od sprawdzalnych reguł.
2. Dla nowego zlecenia udostępnić obowiązujące zatwierdzone reguły
   projektu. Dodatkową regułę zlecenia przypisać wyłącznie do niego.
3. Zapisać decyzję pominięcia z S3-T4 w zakresie bieżącego zlecenia,
   bez zmiany treści i zatwierdzenia reguły projektu.
4. Umożliwić zapis i odczyt wyników interpretacji oraz decyzji S3-T4.
   Nie podejmować decyzji o zatwierdzeniu w warstwie przechowywania.
5. Uwzględnić ustalenie S2: po zmianie DDL dotychczasowe reguły są
   propozycjami do ponownej weryfikacji i zatwierdzenia. Nie kopiować
   automatycznie zatwierdzenia na nowy schemat; nie zmieniać wymagań
   już rozpoczętego wykonania.
6. Dodać migrację i testy zapisu dopiero według uzgodnionego modelu.
   Nie tworzyć przy okazji archiwum rozmów ani wykonań.

**Poza zakresem:** interpretowanie tekstu, wykrywanie konfliktów,
zatwierdzanie znaczenia, polityka sprzątania czatu S9.

**Kryteria ukończenia:**
- Odczyt zachowuje treść, znaczenie, rodzaj i zakres zapisanej reguły.
- Nowe zlecenie uwzględnia obowiązujące reguły właściwego projektu,
  bez reguł innych projektów i wcześniejszych zleceń.
- Pominięcie w jednym zleceniu nie usuwa reguły z następnego.
- Nowa wersja DDL nie dziedziczy samego zatwierdzenia.

**Jak sprawdzić — plan automatyczny:**
- Zapis i odczyt reguły projektu, reguły zlecenia i wskazówki
  jakościowej — zachowanie treści i rozróżnienia.
- Projekt A z regułą P; zlecenie A1 z dodatkową Z i pominiętą P;
  nowe A2 uwzględnia P, nie dostaje Z ani pominięcia z A1.
  Projekt B nie otrzymuje żadnej z tych reguł.
- Po zmianie DDL odczyt pokazuje regułę do przeglądu, nie jako już
  zatwierdzoną dla nowej wersji; rozpoczęte wykonanie zachowuje wymagania.

**Odbiór ręczny:** przez docelowy interfejs utworzyć regułę projektu,
odczytać ją w nowym zleceniu, pominąć tylko w nim i sprawdzić kolejne
zlecenie. Dla reguły lokalnej potwierdzić brak automatycznego zapisu
w projekcie. Odbiór po podłączeniu S3-T4–S3-T5.

**Do wyjaśnienia — blokady:** tabele, pola, migracje, kontrakty zapisu
i odczytu, powiązanie interpretacji i zatwierdzenia ze schematem;
zasady edycji zapisanej reguły i wpływ zmian projektu na już przygotowywane
zlecenia. Model stanu bieżącego zlecenia musi być uzgodniony z S4/S9,
bez domyślnego trwałego archiwum.

##### S3-T3 — Podłączyć interpretację tekstu reguły przez LLM

**Story nadrzędne:** S3 — Reguły biznesowe i ich zatwierdzanie.  
**Cel:** zamienić tekst na propozycję znaczenia, którą aplikacja
potrafi skontrolować, a użytkownik świadomie zatwierdzić.  
**Źródło:** specyfikacja, sekcja 5.2, REQ-016–REQ-019, REQ-071;
AC-06–AC-08; [opis serwisów](serwisy_i_technologie.md),
odpowiedzialności interpretacji w `generation-service`.  
**Punkt startowy:** przyszłe operacje interpretacji S5,
kontrola definicji S3-T1 i zapis S3-T2; propozycja przygotowania
w [LLD](lld/README.md), sekcja 6.  
**Zależności:** S3-T1–S3-T2, model schematu S2 i kontrakt interpretacji S5.

**Co należy zrobić:**
1. Przekazać tekst, wybrany schemat, właściwe reguły i uzyskane
   doprecyzowania do operacji interpretacji z S5. Nie budować drugiego
   klienta dostawców ani konfiguracji modeli w backendzie zarządzającym.
2. Odebrać propozycję rodzaju, parametrów i czytelnego znaczenia.
   Każdą proponowaną definicję sprawdzić przez S3-T1; deklaracja modelu
   „obsługiwana” nie zastępuje kontroli aplikacji.
3. Przy niejasności przekazać potrzebę doprecyzowania, przy braku obsługi
   czytelną przyczynę, a wykryty konflikt skierować do S3-T4.
   Nie uzupełniać brakującego parametru niewidoczną wartością domyślną.
4. W opisie znaczenia pokazać właściwe operacje, pola, zakres i NULL.
   Dla warunkowej wyjaśnić „nie dotyczy”; dla sumowania — relację,
   precyzję i stałą kolejność: zaokrąglenie każdej pozycji, potem suma.
5. Zachować rozdzielenie wskazówek jakościowych i reguł sprawdzalnych;
   „realistyczne dane” nie otrzymuje fikcyjnej definicji testu.
6. Zapisać propozycję i udostępnić ją do przeglądu. Wynik LLM sam
   nie zatwierdza reguły, nie pomija blokady ani nie uruchamia generowania.

**Poza zakresem:** adaptery dostawców i pomiary S5, walidacja danych S7,
pełny czat S4, samodzielne rozstrzyganie konfliktów przez model.

**Kryteria ukończenia:**
- Poprawna odpowiedź modelu staje się propozycją, nie zatwierdzeniem.
- Nieobsługiwany operator, nieznana kolumna i brak parametru pozostają
  widocznymi problemami; nie są cicho poprawiane na inne wymaganie.
- Czytelne znaczenie odpowiada skontrolowanej definicji i ujawnia
  istotne zasady; wskazówka jakościowa nie udaje testu.

**Jak sprawdzić — plan automatyczny:**
- Z kontrolowaną odpowiedzią zastępczą S5: poprawne porównanie,
  reguła warunkowa i sumowanie tworzą niezatwierdzone propozycje.
- Odpowiedź zawierająca nieznaną kolumnę, niedozwolony operator
  lub kod zamiast definicji nie omija S3-T1.
- „Wartość ma być odpowiednia” bez ustalonego znaczenia pozostaje
  do wyjaśnienia; „dane realistyczne” pozostaje wskazówką jakościową.
- Zgłoszony konflikt nie nadpisuje reguły projektu i trafia do S3-T4.
- Dla sumowania opis ujawnia precyzję i tryb połówek od zera,
  bez cichego przyjęcia dwóch miejsc po przecinku.

**Odbiór ręczny:** podać regułę, przeczytać znaczenie przed akceptacją,
następnie doprecyzować niejasny tekst i sprawdzić nową propozycję.
Potwierdzić, że sama odpowiedź LLM nie rozpoczyna generowania.

**Do wyjaśnienia — blokady:** kontrakt wejścia i wyjścia interpretacji,
kompletność kontekstu, format pytań i odpowiedzi doprecyzowujących,
minimalny zakres wykrywania konfliktów oraz obsługa błędu operacji
interpretacji. Sposób odczytu trwającej operacji pozostaje do uzgodnienia
z S5; nie przyjmujemy proponowanych tras LLD bez decyzji.

##### S3-T4 — Dodać zatwierdzanie reguł i rozstrzyganie blokad zlecenia

**Story nadrzędne:** S3 — Reguły biznesowe i ich zatwierdzanie.  
**Cel:** backend jednoznacznie wskazuje, które znaczenie zatwierdzono
i co nadal blokuje przygotowanie zlecenia.  
**Źródło:** specyfikacja, sekcje 5.1–5.2, REQ-015–REQ-019,
AC-06 i AC-08; zasady ponownego zatwierdzenia po zmianie DDL w S2.  
**Punkt startowy:** przyszły backend `services/application-api/`,
propozycje S3-T3, kontrola S3-T1, zapis S3-T2;
projekt zatwierdzania w [kontraktach API](lld/kontrakty_api.md),
sekcja 2 — niezatwierdzony kontrakt szczegółowy.  
**Zależności:** S3-T1–S3-T3; kontrakt przygotowania zlecenia S4;
powiązanie zatwierdzenia ze schematem S2.

**Co należy zrobić:**
1. Po uzgodnieniu kontraktu powiązać decyzję użytkownika z pokazanym
   znaczeniem i definicją. Nie zatwierdzać innej interpretacji niż
   przedstawiona do akceptacji.
2. Udostępnić do S4 stan zatwierdzenia i listę nierozstrzygniętych
   blokad S3. Brak decyzji dla nieobsługiwanej reguły zachowuje blokadę.
3. Obsłużyć „Popraw regułę”: przekazać poprawę do ponownej interpretacji
   i kontroli; samo wybranie działania nie odblokowuje zlecenia.
4. Obsłużyć „Kontynuuj bez tej reguły”: świadomie pominąć wskazaną
   nieobsługiwaną regułę tylko w bieżącym zleceniu. Nie zmieniać
   reguły projektu ani nie przedstawiać pominięcia jako spełnienia
   lub zamiany na wskazówkę jakościową.
5. Zachować wykryty konflikt jako blokadę do wyjaśnienia, bez cichego
   nadpisania lub ignorowania jednej strony. Szczegółowe działania
   rozstrzygające dopisać dopiero po uzgodnieniu.
6. Po zmianie DDL wymagać przeglądu każdej wcześniejszej reguły:
   ponownej weryfikacji i zatwierdzenia albo świadomego odrzucenia
   dla nowej wersji, zgodnie z S2. Odrzucenie w tym przeglądzie nie jest
   tym samym co pominięcie nieobsługiwanej reguły w jednym zleceniu.
7. Przekazać S4 rozstrzygnięty zakres reguł, wskazówki i nadal otwarte
   blokady. Usunięcie blokad S3 nie oznacza gotowości całego zlecenia.

**Poza zakresem:** składanie i start całego zlecenia S4/S6, automatyczne
naprawy danych i przyznawanie ogólnego prawa pomijania dowolnego konfliktu.

**Kryteria ukończenia:**
- Niezatwierdzona interpretacja nie staje się obowiązującą regułą
  do generowania bez decyzji użytkownika.
- Żądanie bezpośrednie do backendu nie omija blokady przez pominięcie UI.
- Poprawa usuwa daną blokadę dopiero po uzyskaniu obsługiwanej,
  zatwierdzonej interpretacji; inne blokady pozostają widoczne.
- Pominięcie dotyczy tylko wskazanej reguły i zlecenia.
- Nowy schemat wymaga rozpatrzenia propozycji ze starej wersji.

**Jak sprawdzić — plan automatyczny:**
- Nieobsługiwana reguła bez decyzji → blokada; wybranie poprawy
  bez poprawnej interpretacji → nadal blokada.
- Poprawiona, skontrolowana i zatwierdzona interpretacja → usunięcie
  jej blokady, bez usuwania niezależnego konfliktu.
- Pominięcie reguły projektu w A1 → wyłączona z wymagań A1;
  zapis projektu bez zmian; A2 ponownie wymaga jej rozpatrzenia.
- Konflikt reguły z DDL lub regułą projektu → blokada bez nadpisania.
- Po zmianie DDL brak decyzji o jednej wcześniejszej propozycji
  nadal blokuje; rozpatrzenie wszystkich nie omija innych blokad.

**Odbiór ręczny:** odtworzyć dwie ścieżki dla nieobsługiwanej reguły:
poprawa i ponowne zatwierdzenie oraz pominięcie w bieżącym zleceniu.
Sprawdzić stan następnego zlecenia i blokadę po zmianie DDL.

**Do wyjaśnienia — blokady:** kontrakty decyzji i odczytu blokad,
identyfikacja zatwierdzanej interpretacji, zmiana treści po zatwierdzeniu,
nieaktualne i powtórzone żądania; konkretna procedura rozstrzygania
konfliktów i zapis odrzucenia propozycji po zmianie schematu.
Nazwy technicznych stanów i kody błędów nie są jeszcze zatwierdzone.

##### S3-T5 — Dodać interfejs wprowadzania, wyjaśniania i zatwierdzania reguł

**Story nadrzędne:** S3 — Reguły biznesowe i ich zatwierdzanie.  
**Cel:** użytkownik widzi zakres reguły, rozumie proponowane sprawdzenie
i może świadomie zatwierdzić, poprawić albo rozstrzygnąć blokadę.  
**Źródło:** specyfikacja, sekcje 5.1–5.2, REQ-015–REQ-019,
REQ-071, AC-06–AC-08; [opis serwisów](serwisy_i_technologie.md)
— frontend i granica odpowiedzialności backendu.  
**Punkt startowy:** frontend `apps/web/` do utworzenia w S1;
zatwierdzony kierunek React/TypeScript i Mantine. Komponenty reguł
nie istnieją; ich lokalizacja i widoki wymagają uzgodnienia z S4.  
**Zależności:** fundament frontendu S1; właściwe operacje S3-T2–S3-T4;
wybór projektu i schematu S2 oraz miejsce interakcji w czacie S4.

**Co należy zrobić:**
1. W uzgodnionym miejscu umożliwić podanie tekstu reguły dla projektu
   albo bieżącego zlecenia. Pokazać zakres i odróżnić wskazówki jakościowe.
2. Wyświetlić propozycję znaczenia przed zatwierdzeniem, potrzebę
   doprecyzowania i przyczyny braku obsługi z backendu.
   Pokazać istotne parametry bez wymagania czytania technicznego JSON.
3. Umożliwić przesłanie doprecyzowania i świadome zatwierdzenie
   znaczenia. Nie traktować zakończenia odpowiedzi LLM jako akceptacji.
4. Przy nieobsługiwanej regule pokazać blokadę i działania
   „Kontynuuj bez tej reguły” oraz „Popraw regułę”.
   Wyjaśnić, że pominięcie reguły projektu dotyczy tylko tego zlecenia.
5. Pokazać nierozstrzygnięty konflikt bez sugerowania, że jedna reguła
   została automatycznie zastąpiona. Działania rozstrzygające oprzeć
   na uzgodnionym kontrakcie S3-T4.
6. Po zmianie DDL pokazać wcześniejsze reguły jako propozycje do
   przeglądu i pozwolić je rozpatrzyć zgodnie z S3-T4, bez wpisywania
   treści od początku. Nie oznaczać ich jako już obowiązujących.
7. Prezentować stan operacji i błędy zgodnie z ustalonym API;
   nie wyliczać w przeglądarce niezależnej polityki obsługiwalności
   ani zatwierdzania.

**Poza zakresem:** cały czat, wybór modeli, wykonanie walidacji,
pełny raport S8, mechanizm kończenia czatu S9 i generalny redesign aplikacji.

**Kryteria ukończenia:**
- Użytkownik rozpoznaje regułę projektu, regułę zlecenia, wskazówkę,
  propozycję do zatwierdzenia oraz blokadę.
- Przed zatwierdzeniem widzi to znaczenie, którego dotyczy decyzja.
- Pominięta reguła nie ma oznaczenia „spełniona”; poprawa nie usuwa
  wizualnej blokady przed potwierdzeniem właściwego stanu przez backend.
- Interfejs nie ogłasza gotowości całego zlecenia na podstawie
  samego usunięcia problemów reguł S3.

**Jak sprawdzić — plan automatyczny:**
- Testy komponentów z kontrolowanymi odpowiedziami backendu:
  propozycja, doprecyzowanie, nieobsługiwana reguła, konflikt i zatwierdzenie.
- Akcje „Popraw” i „Kontynuuj bez” wysyłają właściwą decyzję
  dla wskazanej reguły i nie pokazują pozornego sukcesu.
- Reguła warunkowa ujawnia „nie dotyczy”; sumowanie pokazuje relację,
  precyzję, kolejność i tryb zaokrąglania; wskazówka jakościowa
  nie pokazuje automatycznej oceny realizmu.
- Błąd zapisu/zatwierdzenia jest widoczny i nie zmienia propozycji
  w zatwierdzoną regułę.

**Odbiór ręczny:** wybrać projekt, dodać regułę projektu i regułę
zlecenia; przeczytać i zatwierdzić znaczenie; doprecyzować niejasność;
przejść obie ścieżki obsługi nieobsługiwanej reguły. W następnym
zleceniu sprawdzić ponowną obecność pominiętej reguły projektu.
Po zmianie DDL sprawdzić przegląd wcześniejszych propozycji.

**Do wyjaśnienia — blokady:** rozmieszczenie interakcji w czacie,
sposób wyboru zakresu, wygląd listy reguł i przeglądu po zmianie DDL,
szczegóły potwierdzeń i komunikatów oraz kontrakty stanów i błędów
S3-T2–S3-T4. Nie zatwierdzono przez ten szkic nowych ekranów ani nawigacji.

#### Kontrola pokrycia i dalsza praca po przygotowaniu szkiców

- Zachowano pięć zaakceptowanych identyfikatorów i granice zadań.
  Kroki wewnątrz opisów nie są osobno zaakceptowanymi podzadaniami.
- REQ-015: zapis i zakres w T2, prezentacja w T5.
  REQ-016–REQ-017: kontrola T1, interpretacja T3, decyzje T4 i UI T5.
  REQ-018: odrębność T1–T3/T5; przekazanie do generowania i raport
  wymagają także S5 i S8.
- REQ-019: wykryte konflikty T3, blokady T4 i prezentacja T5.
  AC-06 i AC-08 wymagają wspólnego sprawdzenia T3–T5.
  AC-07 nie jest spełnione przez sam ekran reguł.
- REQ-071 i AC-33: definicja T1, znaczenie T3 i zatwierdzenie T4–T5;
  rzeczywiste obliczenia i wyniki na danych pozostają w S7/S8.
  Do sprawdzenia przez S7 należą m.in. NULL w danych, liczniki prostych
  porównań i warunkowych oraz różnica między sumą zaokrąglonych pozycji
  a zaokrągleniem sumy. Nie są to testy wykonawcze S3-T1.
- Uwzględniono aktualne ustalenie S2 o ponownym przeglądzie po zmianie
  DDL, bez modyfikacji źródeł S1/S2 ani wymagań produktu.
- Nie wykonano implementacji, migracji ani testów aplikacji.
  Nie utworzono issues, commitów ani publikacji.

**Następny krok:** przegląd szkiców z użytkownikiem, następnie
uzupełnienie blokujących kontraktów i trzech szczegółów sumowania.
Nie zaczynać ponownie serii pytań o zaakceptowane zasady.
Szczegółowe opisy pozostają do akceptacji; gotowość do implementacji
wymaga usunięcia blokad konkretnego zadania.

## 6. Źródła do kontynuacji

- [Specyfikacja MVP](specyfikacja_mvp.md) — wersja 1.15 przeczytana wcześniej
  w całości; w sesji S3 uzupełniona do 1.62 o katalog, zakresy obowiązywania,
  obsługę i pominięcie nieobsługiwanej reguły, mechanizm interpretacji,
  zasady porównania kolumn, zakres porównania ze stałą, zakresem lub zbiorem
  oraz domknięcie i poprawność granic zakresu oraz katalog i macierz operacji
  porównania z pojedynczą stałą, zgodność typów, znaczenie NULL w kolumnie
  i dokładne porównywanie tekstu oraz zakres sprawdzania i jednostkę
  naruszenia w tym porównaniu, wykluczenie NULL po stronie stałej oraz
  zestaw typów kolumn, zgodność typów granic i znaczenie NULL w kolumnie
  oraz wymaganie obu granic innych niż NULL dla wariantu „wartość w zakresie”.
  Uzgodniono wspólną zasadę sprawdzania wszystkich rekordów i jednego
  naruszenia za niezgodny rekord dla kolumn, stałej, zakresu i zbioru.
  Uzgodniono operacje „należy do zbioru” i „nie należy do zbioru”
  oraz wymaganie niepustej listy stałych innych niż NULL.
  Uzgodniono znaczenie operacji zbioru oparte na porównaniach ze stałymi,
  wraz ze zgodnością typów, dokładnym porównaniem tekstu i znaczeniem NULL.
  Uzgodniono postać reguły warunkowej: jeden warunek i jedno wymaganie
  w jednym rekordzie, bez gałęzi alternatywnej i zagnieżdżeń.
  Uzgodniono wspólny katalog pojedynczych sprawdzeń dla obu członów,
  obejmujący proste porównania i sprawdzanie NULL, bez łączenia „i”/„lub”.
  Uzgodniono model oceny reguły warunkowej: zgodność lub naruszenie przy
  spełnionym warunku, „nie dotyczy” przy niespełnionym i naruszenie przy
  NULL uniemożliwiającym zwykłe porównanie w warunku.
  Uzgodniono raportowanie wszystkich rekordów reguły warunkowej w trzech
  rozłącznych grupach: zgodne, naruszenia i „nie dotyczy”, z najwyżej
  jednym naruszeniem danej reguły na rekord.
  Uzgodniono sumowanie wszystkich pozycji przez jedną wskazaną relację,
  bez dodatkowych filtrów i przechodzenia przez kolejne tabele.
  Uzgodniono liczbę miejsc po przecinku jako jawny parametr reguły sumującej,
  widoczny w interpretacji do zatwierdzenia.
  Uzgodniono stały tryb zaokrąglania: do najbliższej wartości, przy
  dokładnej połowie od zera, bez wyboru innego trybu w MVP.
  Uzgodniono NULL w wartości nadrzędnej lub mnożonych polach pozycji jako
  naruszenie, bez zastępowania zerem i pomijania niekompletnych pozycji.
  Uzgodniono sumę równą 0 przy braku pozycji, bez naruszenia tej reguły
  wyłącznie z powodu braku pozycji.
  Uzgodniono dokładne porównanie wartości nadrzędnej z sumą zaokrąglonych
  pozycji, bez tolerancji i dodatkowego zaokrąglania.
  Uzgodniono dokładne typy liczbowe we wszystkich polach sumowania
  i obliczenia zachowujące dokładność dziesiętną.
- [Rejestr ustaleń](ustalenia_architektoniczne.md).
- [Przepływy funkcjonalne](przeplywy_funkcjonalne.md).
- [Podział implementacji](podzial_implementacji.md).
- [Architektura ogólna](architektura.md).
- [Serwisy i technologie](serwisy_i_technologie.md).
- [Przygotowanie do hostowania](przygotowanie_do_hostowania.md).
- [Ogólny projekt LLD](lld/README.md) i [walidacja](lld/walidacja.md).
- [Plan badań](plan_badan.md) — osobny rezultat, nie dodatkowy backlog MVP.

Szczegółowe dokumenty modelu danych, kontraktów API i cyklu wykonania
wymagają ponownego odczytu dla wybranego story. Nie przeprowadzono ich
pełnego przeglądu implementacyjnego ani aktualnej weryfikacji bibliotek.
Archiwum koncepcji nie było podstawą mapy story.
