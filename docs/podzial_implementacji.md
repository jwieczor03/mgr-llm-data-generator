# Podział implementacji — własny rdzeń i gotowe komponenty

**Data:** 21 października 2026.

**Status:** propozycja architektoniczna do uzgodnienia, nie zatwierdzony wybór technologii.

**Podstawa:** [specyfikacja MVP](specyfikacja_mvp.md), [przepływy funkcjonalne](przeplywy_funkcjonalne.md) i rozmowa o wymienności modeli, walidatorów oraz przechowywania danych.

## 1. Cel i granice decyzji

Chcemy ograniczyć ilość własnego kodu technicznego i koszt jego weryfikacji, zachowując kontrolę nad znaczeniem wymagań oraz wyniku.

Proponowana zasada: **implementujemy zasady generatora, wykorzystujemy gotowe mechanizmy, a zależności zewnętrzne podłączamy przez niewielkie adaptery**.

Wymienność oznacza brak konieczności zmieniania pozostałych komponentów, jeżeli nowa implementacja zachowuje kontrakt i jego znaczenie. Nie oznacza braku testów, migracji istniejących danych ani automatycznej zgodności funkcjonalnej każdego zamiennika.

Nie wybieramy tutaj języka, frameworka, biblioteki modeli, magazynu aplikacji ani narzędzia orkiestracji. PostgreSQL pozostaje dialektem danych docelowych zgodnie ze specyfikacją, a nie nową decyzją o magazynie stanu roboczego. Historia wykonań jest poza MVP (REQ-072).

Podział na odpowiedzialności nie przesądza liczby mikroserwisów. Gotowy komponent może być biblioteką, procesem lokalnym albo usługą zewnętrzną. „Zewnętrzny” nie musi oznaczać płatnego SaaS ani wysyłania danych poza komputer.

MVP ma także uwzględniać późniejsze hostowanie i wielu użytkowników bez dodawania logowania do bieżącego zakresu (REQ-066). Proponowane granice kontekstu użytkownika, własności danych, dostępu, zadań i zależności wdrożeniowych opisuje [przygotowanie do hostowania](przygotowanie_do_hostowania.md).

Później uzgodniono lokalny interfejs webowy, gotowy SQL/CSV przygotowywany przez model, brak wznawiania oraz zatrzymanie po błędzie technicznym bez automatycznego retry (REQ-067–REQ-070). Naruszenia danych nadal uruchamiają ograniczone poprawki. Aktualny szkic usług i przepływu znajduje się w [architekturze ogólnej](architektura.md).

## 2. Własna logika produktu

„Własna” oznacza kod opisujący zachowanie generatora, także wtedy, gdy jego wykonanie korzysta z bibliotek.

| Obszar | Co implementujemy | Powiązanie ze specyfikacją |
| --- | --- | --- |
| Kontekst projektu | Wersje DDL, reguł i zatwierdzonych interpretacji; odróżnienie jawnych relacji od propozycji; jawne ograniczenia obsługi. | REQ-009–REQ-019 |
| Przygotowanie zlecenia | Przebieg doprecyzowań i zatwierdzania zakresu, liczebności wszystkich potrzebnych tabel, reguł i formatu. Model może proponować, ale nie zastępuje wymaganego zatwierdzenia. | REQ-020–REQ-026 |
| Migawka wymagań | Niezmienny zapis wymagań użytych w bieżącym wykonaniu; bez odtwarzania dawnych zleceń z archiwum. | REQ-026, REQ-059, REQ-072 |
| Sterowanie wykonaniem | Stany i przejścia procesu, uruchamianie etapów, globalny licznik rund poprawek, obsługa anulowania i błędów. Nie piszemy uniwersalnego silnika workflow. | REQ-032–REQ-042 |
| Interpretacja wyniku | Wykonanie zależy od kompletności, potwierdzonej importowalności i zgodności wszystkich obowiązujących relacji; dodatkowe naruszenia biznesowe i realizm są odrębne. Niewykonane sprawdzenie nie jest sukcesem. | REQ-012, REQ-027–REQ-031, REQ-048–REQ-051 |
| Kandydat i raport | Raport dotyczy konkretnej wersji; ochrona najnowszego użytecznego kandydata podczas poprawek, bez archiwum wszystkich wersji. Zwracamy wyłącznie najnowszego użytecznego kandydata, bez rankingu jakości. | REQ-038–REQ-040, REQ-047, REQ-072; OD-03 rozstrzygnięte, AC-36 |
| Raport badawczy | Powiązanie wymagań, rzeczywistego wariantu, kandydatów, sprawdzeń, rund i pomiarów; brak pomiaru odróżniony od zera. | REQ-047–REQ-065 |
| Granice przyszłej wieloużytkownikowości | Kontekst lokalnego właściciela, własność projektów i granica kontroli dostępu; bez rejestracji, sesji i obsługi wielu kont w MVP. | REQ-066 |
| Scenariusze testowe produktu | Oczekiwane zachowanie, przypadki brzegowe i testy zgodności wymiennych implementacji. Narzędzia do uruchamiania testów bierzemy gotowe. | AC-01–AC-32 |

Nie proponujemy zastąpienia tego rdzenia gotową platformą agentową. Platforma może wykonywać kroki, ale nie staje się źródłem prawdy o zatwierdzonym zadaniu i jego wykonaniu.

## 3. Gotowy mechanizm oraz nasz adapter

| Obszar | Co bierzemy gotowe | Co pozostaje nasze |
| --- | --- | --- |
| Odczyt DDL | Parser SQL świadomy dialektu i jego reprezentacja składniowa. | Mapowanie do potrzebnego opisu schematu, macierz obsługi i diagnostyka nieobsługiwanych konstrukcji. Nie piszemy parsera PostgreSQL od zera ani nie zastępujemy go wyrażeniami regularnymi. |
| Komunikacja z modelami | Klient dostawcy albo istniejąca warstwa integracyjna. | Kontrakt operacji modelu, mapowanie możliwości i błędów, identyfikacja ról, zapis faktycznych wiadomości oraz dostępnych metryk bez poświadczeń. |
| Modele lokalne | Istniejący silnik uruchamiania i udostępniania modeli. | Konfiguracja połączenia i adapter; nie implementujemy inferencji ani obsługi GPU. |
| Proces generowania | Opcjonalnie biblioteka do organizowania kroków lub agentów. | Prompty, podział odpowiedzialności, przekazywany kontekst i reakcja na naruszenia. Globalny limit poprawek i ostateczna ocena pozostają poza tym procesem. |
| Importowalność | Uzgodniony rzeczywisty próbny import do pustego, odizolowanego PostgreSQL, po wstępnej kontroli składni, schematu i typów. Szczegóły OD-02 nadal otwarte. | Przygotowanie środowiska, dozwolony zakres wejścia, uruchomienie importu, zebranie dowodów i diagnostyki oraz sprzątanie. |
| Kompletność | Gotowe odczyty danych, liczenie rekordów i operacje na zbiorach. | Porównanie z zatwierdzonym planem dla całej paczki, także wykrywanie brakujących tabel i nieuzgodnionego zakresu. |
| Reguły biznesowe | Gotowe operacje porównywania, agregacji lub wykonywania zapytań; ewentualnie biblioteka walidacyjna. | Zatwierdzona definicja sprawdzenia, jego przygotowanie w obsługiwanym zakresie, jednostka naruszenia i raport. Nie obiecujemy automatycznej obsługi dowolnego tekstowego wymagania. |
| Eksport | Biblioteki odczytu CSV do sprawdzeń, zapisu zawartości i archiwizacji. | Profil eksportu, wyodrębnienie gotowego SQL/CSV modelu, przypisanie plików do tabel, kolejność importu i powiązanie wyniku z kandydatem oraz raportem. Bez cichego poprawiania danych. |
| Zapis danych | Gotowy silnik przechowywania, sterownik i narzędzia migracji. | Zapisane projekty oraz bieżący czat, stan i artefakty wykonania. Po nowym czacie lub pełnym zamknięciu aplikacji nie wracamy do starej rozmowy i plików (REQ-074); fizyczne sprzątanie wymaga OD-09. Nie budujemy archiwum, własnej bazy ani uniwersalnego ORM. |
| Interfejs | Gotowe komponenty formularzy, list, przesyłania i pobierania plików. | Ekrany i interakcje przygotowania projektu, zatwierdzania zlecenia, śledzenia wykonania i odbioru wyniku. |
| Diagnostyka | Biblioteki logowania i pomiaru czasu. | Identyfikatory bieżącego wykonania, rundy i kandydata oraz dostępne pomiary raportu. Nie tworzymy historii badawczej ani archiwum pełnych wiadomości. |
| Komunikacja między usługami | Gotowy transport i biblioteki klientów, jeśli granica rzeczywiście jest sieciowa. | Kontrakty, wersjonowanie, korelacja operacji, deduplikacja skutków i reakcja na częściowe awarie. Nie wybieramy jeszcze brokera ani protokołu. |
| Logowanie — późniejsze rozszerzenie | Proponowana integracja gotowego rozwiązania tożsamości, dopiero po MVP. | Teraz granica źródła kontekstu i kontroli dostępu; później mapowanie tożsamości oraz autoryzacja dostępu do naszych zasobów. |

Gotowa biblioteka nie zwalnia nas z konfiguracji i testów. Nie zakładamy również, że każdy adapter będzie kilkoma liniami: parsowanie schematu i przygotowanie sprawdzalnych reguł wymagają istotnej logiki integracyjnej.

## 4. Walidacja — najważniejszy podział odpowiedzialności

### 4.1. Zgodność ze schematem i importowalność

21 października 2026 wybrano rzeczywisty próbny import zamiast samej analizy statycznej. Wstępna kontrola schematu i typów poprzedza import, ale nie odtwarza pełnej semantyki PostgreSQL. Gotowy silnik egzekwuje zadeklarowane ograniczenia, natomiast nasz adapter odpowiada za warunki próby i poprawność wniosku [S1].

Udany import nie dowodzi kompletności planu, zgodności relacji zatwierdzonych poza DDL, spełnienia wszystkich dodatkowych reguł ani realizmu. Uzgodnione 14 listopada 2026: relacje zatwierdzone poza DDL sprawdzamy osobno po imporcie; ich naruszenie blokuje sukces zadania, ale nie zmienia wyniku importu ani oryginalnego DDL (REQ-012, REQ-027, AC-34). Obsługa przez silnik nie rozszerza automatycznie zakresu generatora: nadal potrzebujemy macierzy OD-01.

Dla wybranej metody proponujemy następujące szczegóły realizacji:

- osobne środowisko walidacyjne, bez dostępu do danych aplikacji i baz użytkownika;
- ograniczone uprawnienia, czas i zasoby oraz jawna lista dozwolonych konstrukcji DDL, instrukcji i wyrażeń; nie uruchamiamy dowolnego SQL od użytkownika lub modelu;
- w szczególności brak niekontrolowanego dostępu do plików i uruchamiania programów przez SQL; mechanizmy uprawnień oraz `COPY` wymagają świadomej konfiguracji [S2, S3];
- import rzeczywistych artefaktów wybranego formatu według tego samego profilu, który otrzyma użytkownik;
- żadnego wyłączania ograniczeń ani pomijania błędnych rekordów w celu uzyskania sukcesu;
- uwzględnienie całej paczki i momentu sprawdzania ograniczeń, także przy kończeniu transakcji;
- zachowanie metody, wersji środowiska, zakresu i rezultatu sprawdzenia przy konkretnym kandydacie.

Nie zakładamy, że sam podział na mikroserwisy stanowi wystarczające zabezpieczenie uruchamiania SQL.

### 4.2. Kompletność

Tutaj potrzebujemy własnego porównania: „plan wymaga 200 zakupów, kandydat zawiera 150”. Silnik zapytań lub biblioteka może policzyć rekordy, ale to nasz kontrakt określa oczekiwany zakres i znaczenie wyniku.

### 4.3. Dodatkowe reguły biznesowe

To integracja, a nie wyłącznie zakup gotowego walidatora. Musimy powiązać:

1. tekst wymagania;
2. zatwierdzone znaczenie, w tym pola, zaokrąglenia, wartości puste i zakres, jeśli są istotne;
3. wykonywalne sprawdzenie w obsługiwanym zakresie;
4. wynik z liczbą, jednostką i przykładami naruszeń.

Nie każdą regułę między rekordami można zastąpić ograniczeniem `CHECK`; dokumentacja PostgreSQL wskazuje ograniczenia sprawdzeń odnoszących się do innych wierszy [S1].

Proponujemy rozpocząć od ograniczonego zestawu rodzajów sprawdzeń, a nie budować ogólny język reguł lub wykonywać dowolny kod napisany przez model. Model może proponować interpretację i sprawdzenie, ale sama jego opinia nie jest dowodem zgodności. Dokładny mechanizm i prezentacja pozostają do ustalenia w ramach OD-06.

## 5. Kontrakty umożliwiające wymianę

To robocze nazwy logiczne, nie gotowa definicja API ani lista osobnych usług.

| Kontrakt | Co powinien ukrywać | Co musi pozostać jawne |
| --- | --- | --- |
| Analiza schematu | Struktury parsera i sposób odczytu DDL. | Oryginalny DDL, rozpoznany zakres, elementy nieobsługiwane i wersja interpretacji. |
| Operacja modelu | Klasy SDK, transport i formaty błędów dostawcy. | Możliwości modelu, faktyczne ustawienia i wiadomości, identyfikator modelu, błędy i brakujące pomiary. |
| Generowanie i poprawianie | Wewnętrzny podział na kroki i agentów. | Niezmienione wymagania, wersja wariantu, identyfikacja rundy i powstałe artefakty. |
| Walidacja | Zastosowany silnik i organizacja sprawdzeń. | Kandydat i wymagania, metoda, profil możliwości, wyniki poszczególnych sprawdzeń oraz nierozstrzygnięcia. |
| Zapis i odczyt | Silnik, jego sterownik i fizyczny układ danych. | Semantyka operacji, spójność zapisów, tożsamość wersji i trwałość artefaktów. |
| Eksport i odbiór | Szczegóły bibliotek serializacji i archiwizacji. | Format, profil importu, dokładny kandydat i powiązany raport. |
| Kontekst operacji i dostęp | Lokalne źródło tożsamości, a w przyszłości szczegóły integracji logowania. | Zaufana wewnętrzna tożsamość, własność zasobu, dozwolona operacja i zakres dostępu do artefaktów. |

Nie zmuszamy modeli o różnych możliwościach do udawania identycznych. Gdy zamiennik nie obsługuje wymaganej funkcji, potrzebna jest jawna odmowa lub osobna zatwierdzona konfiguracja, nie cicha zmiana zadania.

Zmiana silnika magazynu aplikacji powinna dotyczyć adaptera i ewentualnej migracji. Zmiana docelowego dialektu danych wykracza poza obecny zakres i może wymagać zmian analizy schematu, generowania, walidacji oraz eksportu.

## 6. Co na razie odkładamy

- Własny parser SQL, silnik inferencji, silnik bazy danych i framework agentowy.
- Uniwersalny edytor workflow i ogólny język programowania walidatorów.
- Własny transport sieciowy, broker lub system migracji.
- Dedykowany mikroserwis dla każdej biblioteki, modelu, agenta lub pojedynczej reguły.
- Platformę eksperymentalną, automatyczne rankingi i obowiązkowego oceniającego LLM.
- Dodatkowy magazyn wektorowy, RAG i platformę obserwowalności bez konkretnej potrzeby wynikającej z MVP.
- Jednoczesne implementowanie wielu adapterów magazynu danych tylko po to, żeby zademonstrować wymienność. Na początek wystarczy wybrany adapter oraz implementacja testowa.

Nie wykluczamy bibliotek agentowych lub narzędzia workflow, jeśli ograniczą pracę. Proponujemy dopuścić je za kontraktem generowania, bez uzależniania od ich modelu danych całej aplikacji.

## 7. Kryteria przyjęcia gotowego komponentu

Przed wyborem konkretnego produktu trzeba sprawdzić:

1. Pokrycie naszego zakresu, także błędów i przypadków nieobsługiwanych.
2. Nakład integracji, konfiguracji, testów i późniejszej aktualizacji, a nie tylko rozmiar przykładowego wywołania.
3. Możliwość odizolowania jego typów i konfiguracji za adapterem.
4. Dostęp do odpowiedzi, błędów, identyfikatorów i pomiarów potrzebnych bieżącemu wykonaniu i raportowi, bez wymogu archiwizacji.
5. Możliwość wyłączenia technicznych retry i automatycznych fallbacków po błędzie zgodnie z REQ-070 oraz kontrolowania skracania kontekstu i innych zachowań zmieniających przebieg badania.
6. Licencję, utrzymanie, wersjonowanie, wymagania uruchomienia oraz przetwarzanie danych i poświadczeń.
7. Przejście tych samych testów kontraktowych co inne implementacje.

Nie zakładamy z góry, że agregator modeli jest prostszy od kilku oficjalnych klientów, a duży framework agentowy od niewielkiego procesu aplikacyjnego.

## 8. Proponowana kolejność prac

1. Uzgodnić podstawowe kontrakty i zakres sprawdzeń, szczególnie OD-01 i OD-02.
2. Przygotować testy rdzenia na kontrolowanym generatorze i walidatorze, bez kosztownych wywołań modeli.
3. Zbudować minimalny przepływ: zatwierdzone zlecenie → kandydat → rzeczywista walidacja → wynik i raport, bez historii.
4. Podłączyć jeden rzeczywisty wariant modelu i jeden adapter trwałego zapisu.
5. Dodać ograniczone poprawki i test zachowania wcześniejszego użytecznego kandydata.
6. Zweryfikować granicę modeli na kolejnym rzeczywiście potrzebnym adapterze; pozostałe implementacje sprawdzać przez wspólne testy kontraktowe.

Granice osobnych procesów i wdrożeń ustalimy osobno. Naturalnymi kandydatami są gotowy serwer modeli lokalnych oraz izolowane środowisko walidacji. Nie oznacza to jeszcze zatwierdzenia topologii.

## 9. Nierozstrzygnięte decyzje

Ten podział nie zamyka pozostałych szczegółów OD-01–OD-12 ze specyfikacji. Metodę próbnego importu już uzgodniono; otwarte pozostają szczegóły środowiska, wykonywanie reguł, profil eksportu, wartości timeoutów i raportowanie nieudanych operacji, dostępność częściowych lub niesprawdzonych artefaktów po przerwaniu, retencja oraz szczegóły organizacji wariantów. Uzgodniono brak automatycznego retry po błędzie technicznym oraz możliwość pobrania wcześniej zapisanego użytecznego kandydata z raportem po anulowaniu lub awarii, bez zmiany statusu wykonania (REQ-047, AC-35; częściowe rozstrzygnięcie OD-08). OD-03 jest zamknięte: zwracamy wyłącznie najnowszego użytecznego kandydata (REQ-039, AC-36). [Projekt walidacji](lld/walidacja.md) zawiera także niezatwierdzoną macierz PostgreSQL oraz potwierdzony 14 listopada 2026 zakres REQ-071: ograniczony rodzaj reguły sumującej dane między tabelami, ze szczegółami nadal do uzgodnienia.

Doprecyzowanie w specyfikacji v1.13: głównym widokiem jest czat z wyborem projektu i kolejnymi poleceniami (REQ-073). Przy zmianie danych LLM otrzymuje poprzednią paczkę i nowe polecenie; poprawiona paczka podlega walidacji (REQ-076). Każda nowa prośba ma własny limit napraw, domyślnie 3 rundy po pierwszym kandydacie (REQ-033–REQ-034). Po nieudanej zmianie zachowujemy poprzednią sprawdzoną wersję z jej raportem i komunikatem o niepowodzeniu; dodatkowe 3 rundy wymagają ręcznej akcji użytkownika i naprawiają ostatniego nieudanego kandydata z uwzględnieniem wykrytych błędów (REQ-078–REQ-079). Pobranie po przerwaniu dotyczy nadal dostępnej rozmowy; zdarzenia z REQ-074, także odświeżenie i zamknięcie strony, kończą dostęp do starego czatu i plików oraz uruchamiają anulowanie trwającego wykonania (REQ-077). Ostrzeżenie przed odświeżeniem lub zamknięciem podlega ograniczeniom przeglądarki; rezygnacja zachowuje dane i nie anuluje pracy (REQ-075).

Otwarte pozostają techniczne wykrycie wyjścia i przekazanie anulowania, moment potwierdzenia zatrzymania, mechanizm zakończenia dostępu, fizyczne sprzątanie oraz przypisanie prośby i dodatkowej serii do wykonania oraz liczników i kontrakt kontekstu. Nie są to decyzje do samodzielnego podjęcia podczas implementacji.

Uzgodniono, że model zwraca gotowy SQL/CSV. Nie budujemy przebiegu opartego na deterministycznym generowaniu tego formatu z pośrednich rekordów modelu. W ramach OD-10 pozostaje organizacja wariantów i dokładny kontrakt przekazania plików. Pozytywny raport i eksport muszą dotyczyć tych samych danych w rzeczywiście dostarczanym formacie.

## 10. Źródła potwierdzające dostępność mechanizmów

Sprawdzone 20 października 2026. Nie stanowią wyboru konkretnej biblioteki, wersji wdrożeniowej ani pełnej oceny kandydatów.

| ID | Dokumentacja pierwotna | Znaczenie |
| --- | --- | --- |
| S1 | PostgreSQL, Constraints: `https://www.postgresql.org/docs/18/ddl-constraints.html` | Egzekwowanie ograniczeń oraz ograniczenia stosowania `CHECK` do innych wierszy. |
| S2 | PostgreSQL, COPY: `https://www.postgresql.org/docs/18/sql-copy.html` | Gotowy import CSV, parametry profilu i operacje dostępu do plików lub programów wymagające ograniczenia. |
| S3 | PostgreSQL, Privileges: `https://www.postgresql.org/docs/18/ddl-priv.html` | Uprawnienia wykonywania operacji w pomocniczym środowisku. |
| S4 | SQLGlot, dokumentacja projektu: `https://github.com/tobymao/sqlglot` | Przykład gotowego parsera i generatora SQL; samo parsowanie nie potwierdza poprawności wykonania. Nie wybieramy tej biblioteki. |
| S5 | Ollama, Introduction: `https://docs.ollama.com/api/introduction` | Przykład gotowego serwera modeli dostępnego przez API, również lokalnie. Nie wybieramy środowiska modeli. |
