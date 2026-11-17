# Specyfikacja funkcjonalna MVP — generator relacyjnych danych testowych

**Wersja:** 1.65

**Data:** 14 listopada 2026

**Podstawa:** wywiad dotyczący wymagań i potwierdzenie zakresu w pytaniu Q42 oraz późniejsze uzgodnienia rozwoju do wielu użytkowników, lokalnego interfejsu webowego, gotowego wyniku modelu, etapów walidacji i braku wznawiania. Uzupełnienie 21 października 2026: potwierdzona kolejność walidacji z wstępną kontrolą typów i rzeczywistym próbnym importem przed regułami biznesowymi. Uzupełnienie 14 listopada 2026: potwierdzona obsługa ograniczonego rodzaju reguły sumującej dane między tabelami oraz obowiązkowe sprawdzanie zatwierdzonych relacji niewystępujących w DDL; szczegółowe znaczenie obliczeń pozostaje otwarte.

**Status:** zatwierdzony zakres MVP; szczegóły wymienione w sekcji 16 wymagają dalszych decyzji.

## 1. Rola dokumentu

Dokument określa, **co ma robić aplikacja**, jakie wyniki ma dostarczać i kiedy można uznać jej zachowanie za prawidłowe. Nie określa sposobu implementacji.

W szczególności nie wybiera języka, frameworka, bibliotek, architektury wdrożeniowej, sposobu przechowywania danych ani narzędzi do obsługi modeli. Określa uzgodnioną metodę potwierdzania importowalności, ale nie wybiera bibliotek i szczegółowej realizacji walidatora.

Wymagania oznaczone identyfikatorami `REQ-…` należą do uzgodnionego zakresu, chyba że jawnie oznaczono je jako **poza MVP**. Takie identyfikatory zachowujemy dla ciągłości odwołań, nie jako zadania do realizacji. Przykłady ilustrują zachowanie, ale nie narzucają nazw tabel, domeny biznesowej ani konkretnych liczebności. Punkty `OD-…` wskazują nierozstrzygnięte szczegóły; przy częściowym rozstrzygnięciu zapisujemy, co już przyjęto, a co nadal jest otwarte.

### 1.1. Relacja do wcześniejszych materiałów

Dotychczasowe dokumenty zostały zachowane bez zmian treści jako historyczne materiały w [archiwum koncepcji](archiwum/README.md):

- [Pierwotna specyfikacja funkcjonalna](archiwum/2026-10-20/dev/specyfikacja_funkcjonalna.md).
- [Pierwotna architektura](archiwum/2026-10-20/dev/architektura.md).
- [Pierwotne przepływy sekwencyjne](archiwum/2026-10-20/dev/przeplywy_sekwencyjne.md).
- [Pierwotna strategia modeli AI](archiwum/2026-10-20/koncepcje/strategia_modeli_ai.md).
- [Pierwotny wybór LLM](archiwum/2026-10-20/koncepcje/wybor_llm.md).
- [Pierwotne założenia środowiska](archiwum/2026-10-20/koncepcje/zalozenia.md).
- [Pierwotne pomysły i notatki](archiwum/2026-10-20/koncepcje/pomysly_notatki.md).

Aktualnym uzupełnieniem są [przepływy funkcjonalne](przeplywy_funkcjonalne.md) oraz [roboczy plan badań](plan_badan.md). Przepływy objaśniają wymagania, a plan zachowuje pytania i hipotezy do rozpatrzenia; żaden z tych dokumentów nie rozszerza samodzielnie zakresu MVP.

W przypadku rozbieżności **niniejszy dokument opisuje uzgodniony zakres MVP**. Wcześniejsze wybory technologiczne, propozycje AWS, RAG, mikroserwisów lub konkretnych modeli nie stają się przez to wymaganiami.

## 2. Cel i sposób wykorzystania

### 2.1. Cel aplikacji

Aplikacja ma generować syntetyczne dane testowe dla wielu powiązanych tabel PostgreSQL na podstawie:

1. schematu bazy dostarczonego przez użytkownika;
2. zapisanych reguł biznesowych i wskazówek jakościowych;
3. zlecenia wyrażonego językiem naturalnym;
4. zatwierdzonego zakresu danych i liczebności rekordów.

Wynik ma nadawać się do załadowania do pustej pod względem danych bazy zgodnej z dostarczonym schematem. Użytkownik wybiera wynik w postaci poleceń `INSERT` albo CSV.

### 2.2. Cel badań

Autor projektu używa aplikacji jak zwykły użytkownik, a pomiędzy próbami ręcznie zmienia modele, prompty wewnętrzne oraz organizację procesu generowania. Badania obejmują modele lokalne i płatne modele dostępne przez API, w tym warianty procesu jedno- i wieloagentowego.

**Przedmiotem oceny jest wynik całego procesu**, z uwzględnieniem walidacji, poprawek, czasu i dostępnych informacji o zużyciu zasobów. Pierwsza odpowiedź modelu nie stanowi osobnego głównego kryterium porównania. Badania i gromadzenie materiałów do analizy są odpowiedzialnością autora poza generatorem.

Aplikacja nie ma automatycznie prowadzić eksperymentów ani wybierać zwycięzcy. Po badaniach do docelowej aplikacji zostaje podłączone rozwiązanie wybrane przez autora.

**Rozstrzygnięcie 14 listopada 2026, zastępujące wcześniejsze ustalenia o historii:** MVP nie przechowuje archiwum wykonań ani wiadomości modeli. Użytkownik pracuje w bieżącym czacie i może prowadzić w nim rozmowę, także po otrzymaniu wyniku. „Nowy czat”, odświeżenie strony oraz jej zamknięcie kończą dostęp do starej konwersacji i związanych z nią plików. Po ponownym otwarciu całkowicie zamkniętej aplikacji również widzimy nową rozmowę. Przed odświeżeniem lub zamknięciem strony wymagane jest ostrzeżenie o utracie danych, z uwzględnieniem ograniczeń przeglądarki opisanych w sekcji 11.1. Pozostają zapisane projekty. Historia czatów i plików jest wyłącznie kandydatem na dalszy rozwój poza MVP. Magazyn i fizyczne sprzątanie pozostają w OD-09.

### 2.3. Role

| Rola | Odpowiedzialność |
| --- | --- |
| Użytkownik generatora | Dostarcza schemat i reguły, zleca generowanie, odpowiada na pytania, zatwierdza wymagania i odbiera dane. |
| Autor prowadzący badania | Ręcznie zmienia badany wariant, ponawia te same zadania, porównuje wyniki i wybiera rozwiązanie docelowe. |
| Osoba oceniająca realizm | Ocenia dane poza generatorem, ewentualnie z pomocą zewnętrznego LLM lub osobnej aplikacji. |

W MVP role te może pełnić ta sama osoba. Nie oznaczają one kont ani poziomów uprawnień.

## 3. Pojęcia

| Pojęcie | Znaczenie |
| --- | --- |
| Projekt | Zapisany kontekst pracy obejmujący schemat, reguły i zatwierdzone uzupełnienia jego interpretacji. |
| Czat | Bieżąca rozmowa użytkownika z aplikacją: wybór projektu, polecenia, odpowiedzi i związane z rozmową wyniki. Nie jest archiwum dawnych rozmów ani synonimem pojedynczego wykonania. |
| Schemat | Dostarczony DDL PostgreSQL opisujący tabele i ich obsługiwane ograniczenia. |
| Reguła biznesowa | Dodatkowe wymaganie użytkownika, którego zatwierdzoną interpretację aplikacja potrafi automatycznie sprawdzić. |
| Wskazówka jakościowa | Wymaganie przekazywane do generowania, ale nieoceniane automatycznie, np. ogólne oczekiwanie realizmu. |
| Zlecenie | Polecenie użytkownika wraz z zatwierdzonymi wymaganiami dotyczącymi potrzebnych danych. |
| Plan danych | Jawny zakres zlecenia: potrzebne tabele, liczebności, relacje i warunki istotne dla wykonania. Nie jest planem implementacyjnym. |
| Wykonanie | Jedna próba realizacji zatwierdzonego zlecenia przez konkretny wariant generowania, obejmująca ewentualne poprawki. |
| Wariant generowania | Faktycznie zastosowane modele, ich ustawienia, prompty wewnętrzne i organizacja procesu. |
| Kandydat wyniku | Konkretna wersja wygenerowanej paczki danych poddawana walidacji. |
| Runda poprawek | Reakcja procesu na zgłoszone naruszenia i przygotowanie kolejnego kandydata do oceny. Nie jest synonimem pojedynczego wywołania modelu. |
| Kompletność | Zgodność rzeczywistych liczebności i zakresu danych z zatwierdzonym zleceniem. |
| Importowalność | Potwierdzona możliwość poprawnego załadowania danych zgodnie z obsługiwanym schematem i uzgodnionymi warunkami importu. |
| Obowiązujące relacje | Relacje zadeklarowane w DDL oraz relacje nieobecne w DDL, które użytkownik zatwierdził jako część wymagań danego wykonania. |
| Wykonane zadanie | Zlecenie, dla którego istnieje wynik kompletny, importowalny i ze sprawdzoną zgodnością ze wszystkimi obowiązującymi relacjami. |
| Użyteczny kandydat | Kandydat spełniający obowiązkowe warunki wykonania zadania. Może nadal naruszać dodatkowe reguły biznesowe. |

## 4. Zakres MVP

### 4.1. W zakresie

| ID | Wymaganie |
| --- | --- |
| REQ-001 | Aplikacja jest przeznaczona dla jednego użytkownika w danej instalacji. |
| REQ-002 | MVP można uruchomić lokalnie; wdrożenie samej aplikacji na AWS nie jest warunkiem ukończenia. |
| REQ-003 | Wejściowym opisem struktury jest pojedynczy plik SQL DDL dla PostgreSQL lub wspólnie wysłana paczka takich plików, tworząca jedną pełną wersję schematu. |
| REQ-004 | Podstawowy zakres obejmuje tabele, typy kolumn, klucze główne i obce, `NOT NULL`, `UNIQUE`, `CHECK` oraz wartości domyślne w jawnie określonym obsługiwanym zakresie. |
| REQ-005 | Aplikacja obsługuje generowanie danych dla wielu powiązanych tabel, w tym tabel łączących, oraz proste hierarchie rekordów w obrębie jednej tabeli, np. pracowników i ich przełożonych. |
| REQ-006 | Dane są generowane jako samodzielna paczka dla bazy bez istniejących danych; nie zakłada się dostępności klientów, produktów ani innych rekordów poza paczką. |
| REQ-007 | Docelowa skala MVP obejmuje setki do kilku tysięcy rekordów łącznie we wszystkich uzupełnianych tabelach. Jest to zakres oczekiwanego użycia, a nie zatwierdzony sztywny limit liczbowy. |
| REQ-008 | Użytkownik wybiera wynik w postaci poleceń `INSERT` albo CSV. Generowanie obu formatów jednocześnie nie jest wymagane. |
| REQ-067 | MVP jest aplikacją webową uruchamianą lokalnie i obsługiwaną przez przeglądarkę. Nie wybiera to frameworka interfejsu ani backendu. |
| REQ-073 | Głównym widokiem pracy jest czat. Użytkownik wybiera w nim projekt, wpisuje polecenie i otrzymuje odpowiedź oraz dostępny wynik. Może wysyłać kolejne polecenia i kontynuować tę samą rozmowę po otrzymaniu wyniku. |

**Proste hierarchie w jednej tabeli — uzgodnione 14 listopada 2026:** rekord może wskazywać rekord nadrzędny z tej samej tabeli. Przykładowo Anna nie ma przełożonego, Jan wskazuje Annę, a Ola wskazuje Jana. Rekord na szczycie hierarchii nie ma rodzica; schemat musi dopuszczać taki brak, np. przez `NULL`. Wszyscy wskazani rodzice należą do generowanej paczki. Zakres obejmuje hierarchie bez zapętleń, nie dowolne cykle ani odwołanie rekordu do samego siebie. Nie zmieniamy DDL, aby umożliwić utworzenie korzenia hierarchii.

### 4.2. Poza zakresem MVP

- Obsługa kolumn typu `json` i `jsonb` w schematach, dla których generujemy dane.
- Generowanie samodzielnych zagnieżdżonych dokumentów JSON jako osobnej rodziny zadań.
- XML oraz import schematów z OpenAPI, Swaggera lub przykładowych dokumentów JSON.
- Obsługa innych dialektów SQL.
- Dopisywanie danych do już wypełnionej bazy, uzgadnianie istniejących identyfikatorów i wykrywanie konfliktów z jej zawartością.
- Obowiązkowe bezpośrednie połączenie z bazą użytkownika.
- Poprawność zależna od wyzwalaczy, procedur i własnych funkcji bazodanowych.
- Obowiązkowe zależności kołowe, w których rekordy wzajemnie wymagają swojego wcześniejszego istnienia.
- Celowe generowanie naruszeń do testów negatywnych.
- Edytor tabel i kolumn oraz aktualizowanie schematu przez edycję jego pojedynczych fragmentów w aplikacji.
- Konta, logowanie, współdzielenie projektów i uprawnienia zespołowe.
- Wizualny edytor workflow, panel do budowania zespołów agentów i obowiązkowy wybór wariantu badawczego w interfejsie.
- Automatyczne serie eksperymentów, rankingi modeli i automatyczny wybór najlepszego rozwiązania.
- Wbudowana ręczna punktacja realizmu, moduł notatek badawczych i obowiązkowy LLM oceniający realizm.
- Obsługa setek tysięcy lub milionów rekordów jako gwarantowana zdolność MVP.
- Obowiązkowe wdrożenie produkcyjne w chmurze.
- Przechowywanie i przeglądanie historii wykonań, archiwum wiadomości modeli oraz ponawianie zlecenia z historycznego zapisu.

Rozszerzenia można rozpatrywać po uzyskaniu działającego MVP i w zależności od dostępnego czasu. Odłożenie kolumn `json`/`jsonb` dotyczy danych generowanych dla użytkownika, nie wewnętrznego przechowywania danych aplikacji ani formatu komunikacji. Techniczny raport wykonania nie jest „generowaniem dokumentów JSON” w znaczeniu odłożonej rodziny zadań; jego format pozostaje do ustalenia.

## 5. Projekty i przygotowanie kontekstu

### 5.1. Wgranie i rozpoznanie schematu

| ID | Wymaganie |
| --- | --- |
| REQ-009 | Użytkownik może zapisać projekt i wielokrotnie korzystać z jego schematu oraz reguł bez ponownego przygotowywania całego kontekstu. |
| REQ-010 | Po wgraniu DDL aplikacja rozpoznaje tabele, kolumny i obsługiwane ograniczenia, w tym jawne relacje. |
| REQ-011 | Relacje jawnie zadeklarowane w DDL są obowiązujące i nie wymagają odgadywania na podstawie nazw pól. |
| REQ-012 | Aplikacja może zaproponować relacje brakujące w DDL, ale nie może używać domyślonej relacji jako obowiązującej bez zatwierdzenia przez użytkownika. Po zatwierdzeniu zgodność z taką relacją jest obowiązkowym warunkiem wykonania zadania, także gdy sam próbny import zakończy się powodzeniem. Aplikacja sprawdza ją osobno, bez dopisywania ograniczenia do oryginalnego DDL. |
| REQ-013 | Wykryte elementy nieobsługiwane i obowiązkowe zależności kołowe są jawnie zgłaszane. Generowanie zależne od takiego przypadku nie rozpoczyna się jako rzekomo obsługiwane. |
| REQ-014 | Aktualizacja schematu odbywa się przez wgranie nowej wersji całego DDL. Nie zmienia to wymagań rozpoczętego wcześniej, nadal obsługiwanego wykonania. |

Wgranie schematu nie oznacza zgody na jego automatyczne modyfikowanie. Aplikacja nie może usuwać ograniczeń ani zmieniać struktury wyłącznie po to, aby wygenerowany wynik uzyskał pozytywną ocenę.

**Dane projektu — uzgodnione 14 listopada 2026 podczas planowania S2-T1:**
przy tworzeniu projektu użytkownik podaje wymaganą nazwę i opcjonalny
krótki opis kontekstu. Nie wybiera dziedziny z zamkniętej listy.
Opis nie zastępuje DDL ani zatwierdzonych reguł biznesowych.
Nazwa ma od 1 do 100 znaków, a opcjonalny opis najwyżej 2000 znaków.
Przed sprawdzeniem długości i zapisem usuwamy białe znaki z początku
i końca obu pól. Nazwa pusta po tej operacji jest błędem; pusty opis
oznacza brak opisu. Przekroczenie limitu powoduje czytelny błąd,
bez obcinania treści. Nazwy projektów są unikalne w danej instalacji
bez rozróżniania wielkości liter. Po zapisaniu „Bank” próba utworzenia
„bank” lub „ Bank ” kończy się czytelnym błędem, bez nadpisania
istniejącego projektu. Techniczny sposób porównywania nazw i wymuszenia
unikalności w bazie pozostaje do doprecyzowania.
Użytkownik może zapisać projekt przed wgraniem DDL, a schemat dodać
w kolejnym kroku. Projekt bez schematu pozostaje zapisany, ale nie jest
gotowy do generowania.

**Wiele plików DDL — uzgodnione 14 listopada 2026 podczas planowania
S2-T2:** MVP dopuszcza również paczki wielu plików DDL. Nie ograniczamy
wejścia do pojedynczego pliku SQL. Użytkownik zaznacza wiele plików SQL
i wysyła je razem w formularzu, bez konieczności tworzenia archiwum.
Nie uzgodniono obsługi ZIP. Wszystkie pliki wysłane razem tworzą jedną
pełną wersję schematu, dopuszczaną do użycia wyłącznie w całości.
Błąd analizy w jednym pliku blokuje użycie całej nowej wersji,
bez częściowego zastępowania dotychczasowego schematu. Zachowujemy
nieudaną wersję z diagnostyką zgodnie z zasadą poniżej.
Użytkownik może ustawić kolejność plików przed wysłaniem. Aplikacja
traktuje je w tej kolejności jako jeden skrypt DDL, bez samodzielnego
przestawiania. Pliki DDL przyjmujemy wyłącznie w kodowaniu UTF-8.
Niepoprawne kodowanie zgłaszamy jako czytelny błąd, bez automatycznego
zgadywania kodowania i konwersji. Dopuszczamy UTF-8 także z BOM,
czyli opcjonalnym znacznikiem na początku każdego pliku. Oryginalny plik
zachowujemy bez zmian; znacznik pomijamy wyłącznie na potrzeby analizy.
Limity pozostają do uzgodnienia.

**Błędne kodowanie i poprawienie paczki — uzgodnione 14 listopada 2026
podczas planowania S2-T2:** w MVP niepoprawne kodowanie choćby jednego
pliku odrzuca całą paczkę przed utworzeniem wersji schematu i uruchomieniem
analizy DDL. Użytkownik otrzymuje czytelny błąd i ponownie wysyła pełną
poprawioną paczkę; nie podmienia pojedynczego pliku w zapisanej paczce.
Podmiana tylko jednego pliku jest kierunkiem rozszerzenia po MVP
(sekcja 15), nie częścią obecnych zadań.

**Puste pliki — uzgodnione 14 listopada 2026 podczas planowania S2-T2:**
pusty plik lub plik zawierający wyłącznie białe znaki odrzuca całą paczkę
przed utworzeniem wersji schematu. Nie pomijamy go automatycznie.
Zasada obowiązuje także dla pojedynczego pliku. Plik zawierający
wyłącznie komentarze SQL i ewentualne białe znaki, bez instrukcji SQL,
traktujemy tak samo: odrzucamy całą paczkę przed utworzeniem wersji.

**Nazwy plików w paczce — uzgodnione 14 listopada 2026 podczas planowania
S2-T2:** nazwy są unikalne w obrębie jednej paczki bez rozróżniania
wielkości liter. Konflikt, np. `schema.sql` i `SCHEMA.sql`, odrzuca całą
paczkę przed utworzeniem wersji. Techniczny sposób porównania nazw
pozostaje do doprecyzowania.

**Zbiorcze błędy wstępnego sprawdzenia — uzgodnione 14 listopada 2026
podczas planowania S2-T2:** dla kompletnie odebranej paczki pokazujemy
razem wykryte problemy kodowania, pustych plików i konfliktów nazw,
zamiast kończyć sprawdzanie po pierwszym błędzie. Paczka z takimi błędami
jest odrzucana przed utworzeniem wersji i uruchomieniem analizy DDL.
Nie oznacza to obietnicy zebrania wszystkich błędów późniejszej analizy
DDL ani analizy treści pliku, którego nie można poprawnie odczytać.

**Przerwany transfer lub nieudany zapis paczki — uzgodnione 14 listopada
2026 podczas planowania S2-T2:** nie tworzymy nowej wersji schematu.
Dotychczasowy schemat pozostaje bez zmian; użytkownik musi ponownie
wysłać całą paczkę. Nie jest to przypadek nieudanej analizy kompletnie
odebranej i zapisanej paczki, którą zachowujemy jako wersję z diagnostyką.
Sam brak odpowiedzi serwera nie potwierdza nieudanego zapisu.
Po utracie odpowiedzi aplikacja najpierw sprawdza wynik wysłania paczki,
zamiast od razu proponować ponowne wysłanie. Ma to zapobiec utworzeniu
duplikatu, gdy zapis się udał, ale odpowiedź nie dotarła.
**Identyfikacja próby — uzgodniona 14 listopada 2026 w S2-T2:**
każda próba wysłania otrzymuje unikalny identyfikator utworzony przez
frontend przed przesłaniem plików. Po utracie odpowiedzi aplikacja
używa tego identyfikatora do sprawdzenia w backendzie wyniku tej samej
próby, bez ponownego przesyłania paczki. Format i przechowywanie
identyfikatora oraz kontrakt odczytu wyniku pozostają do uzgodnienia.

**Nadal nieznany wynik — uzgodnione 14 listopada 2026 w S2-T2:**
jeśli sprawdzenie nie rozstrzyga wyniku próby, aplikacja blokuje ponowne
wysłanie tej paczki i udostępnia przycisk „Sprawdź ponownie”.
Blokada trwa do ustalenia wyniku; sama niedostępność odczytu nie oznacza
nieudanego zapisu. Może to wymagać oczekiwania na przywrócenie odczytu
z backendu. Przycisk sprawdza wynik tej samej próby, nie wysyła plików.

**Opuszczenie strony podczas wysyłania — uzgodnione 14 listopada 2026
w S2-T2/S2-T6:** podczas trwającego przesyłania DDL aplikacja ma ostrzec,
że odświeżenie strony lub zamknięcie strony/aplikacji anuluje przesyłanie.
Rezygnacja z wyjścia pozostawia przesyłanie aktywne; wykonane wyjście
ma je anulować. Ostrzeżenie podlega ograniczeniom z sekcji 11.1,
bez gwarancji własnego tekstu standardowego okna i jego wyświetlenia
przy wymuszonym zamknięciu.
**Doprecyzowanie 14 listopada 2026:** jeśli użytkownik wykona wyjście,
zanim przeglądarka otrzyma potwierdzenie zapisu, nie zachowujemy nowej
wersji także wtedy, gdy backend zdążył już zapisać całą paczkę.
Pliki tej anulowanej próby podlegają usunięciu; wcześniejsze wersje
pozostają bez zmian. Nie wystarczy samo przerwanie transferu po stronie
przeglądarki. Mechanizm rozpoznania tego przypadku, anulowania,
sprzątania i potwierdzenia skutku wymaga projektu.
Nie zaakceptowano propozycji przywracania nierozstrzygniętej próby po
ponownym otwarciu aplikacji.

**Potwierdzenie z przeglądarki — uzgodnione 14 listopada 2026
w S2-T2/S2-T6:** serwer najpierw zapisuje paczkę roboczo i wysyła
komunikat o zapisie. Przeglądarka automatycznie potwierdza odebranie
tego komunikatu; nie wymaga to dodatkowego kliknięcia użytkownika.
Analizę DDL wolno uruchomić dopiero po otrzymaniu tego potwierdzenia
przez backend. Sam roboczy zapis ani samo wysłanie odpowiedzi przez
serwer nie uruchamiają analizy. Kontrakt potwierdzenia, obsługa jego
utraty, rozpoznawanie porzuconego zapisu i sprzątanie pozostają otwarte.

**Analiza DDL w tle — uzgodnione 14 listopada 2026 podczas planowania
S2-T2:** po odebraniu i zapisaniu plików aplikacja potwierdza wgranie,
a DDL analizuje w tle. Interfejs pokazuje stan analizy; żądanie wgrywania
nie czeka na jej zakończenie. Potwierdzenie wgrania nie oznacza poprawnej
analizy ani gotowości schematu do generowania.
**Niezależność od otwartej strony — uzgodniona 14 listopada 2026
w S2-T2/S2-T6:** po przyjęciu dodatkowego potwierdzenia z przeglądarki
analiza może działać asynchronicznie, niezależnie od otwartej strony.
Odświeżenie lub zamknięcie strony nie anuluje już rozpoczętej analizy
przyjętej paczki. Nie zmienia to anulowania podczas wysyłania ani
możliwości świadomego przerwania analizy osobną akcją.
Zamknięcie procesu backendu jest przypadkiem awarii, nie gwarancją
działania analizy bez uruchomionej aplikacji.
Po awarii przerywającej analizę aplikacja automatycznie rozpoczyna
analizę zapisanej paczki ponownie, gdy możliwe jest jej uruchomienie.
Nie wymaga to ponownego wgrywania plików ani ręcznego uruchomienia
przez użytkownika. Dotyczy przerwanej analizy, nie poprawiania błędnego
DDL ani ponawiania generowania danych. Dopuszczamy maksymalnie trzy
automatyczne ponowienia po awarii, poza pierwszym uruchomieniem analizy.
Po ich wyczerpaniu analiza zatrzymuje się z czytelnym błędem, bez kolejnego
automatycznego ponowienia. To limit odrębny od rund naprawczych
generowania danych. Przy ponowieniu kontynuujemy analizę od zachowanego
postępu, jeżeli jest to technicznie możliwe i pozwala uzyskać poprawny,
kompletny wynik. Nie przyjęto bezwarunkowego analizowania całej paczki
od początku. Wykonalność i sposób zachowania postępu wymagają weryfikacji.
Gdy kontynuacja nie jest możliwa, automatycznie analizujemy zapisaną
paczkę od początku, bez ponownego wgrywania i w ramach tego samego
limitu trzech ponowień. Zmiana sposobu ponowienia nie daje dodatkowego
limitu.
**Po wyczerpaniu ponowień — uzgodnione 14 listopada 2026 w S2-T2/S2-T6:**
nie udostępniamy ręcznego ponowienia analizy zapisanej paczki.
Użytkownik musi ponownie wgrać całą paczkę plików; nie podmienia
pojedynczego pliku ani nie wznawia zakończonej analizy.
Mechanizm uruchamiania, dokładne stany i odstępy ponowień
pozostają do uzgodnienia.
Nie ustalono procentowego postępu.

**Jedna analiza w MVP — uzgodnione 14 listopada 2026 w S2-T2:**
w całej aplikacji może jednocześnie działać tylko jedna analiza DDL,
także gdy paczki należą do różnych projektów. Limit nie dotyczy
liczby zapisanych projektów.
**Blokada wgrywania — uzgodniona 14 listopada 2026 w S2-T2/S2-T6:**
podczas trwającej analizy blokujemy wgrywanie DDL we wszystkich
projektach. Nie przyjmujemy kolejnych paczek do kolejki oczekujących
analiz.
**Początek blokady — uzgodniony 14 listopada 2026 w S2-T2/S2-T6:**
blokada obowiązuje już od rozpoczęcia wysyłania jednej paczki,
we wszystkich projektach i także w innych kartach przeglądarki.
Nie dopuszczamy równoczesnego wysyłania kolejnej paczki przed analizą.
**Oczekiwanie na ponowienie — uzgodnione 14 listopada 2026
w S2-T2/S2-T6:** blokada pozostaje aktywna także pomiędzy próbami,
gdy po awarii aplikacja czeka na automatyczne ponowienie analizy.
Nie zwalniamy jej tylko dlatego, że analiza chwilowo nie pracuje.
Techniczny mechanizm egzekwowania blokady pozostaje do doprecyzowania.
**Odmowa podczas blokady — uzgodniona 14 listopada 2026 w S2-T2/S2-T6:**
backend odrzuca próbę wysłania kolejnej paczki odpowiedzią HTTP `409`
z kodem `DDL_PROCESSING_IN_PROGRESS`. Interfejs pokazuje komunikat:
„Trwa przesyłanie lub analiza DDL. Poczekaj na zakończenie”.
Szczegóły kontraktu pozostają w dokumencie kontraktów API.

**Nowy DDL podczas analizy — uzgodnione 14 listopada 2026 podczas
planowania S2-T2:** jeżeli w projekcie trwa analiza, użytkownik najpierw
ją przerywa. Dopiero po jej zatrzymaniu może wgrać nowy DDL jako kolejną
wersję. Nie analizujemy w tym samym projekcie obu wersji równolegle.
Świadome przerwanie przez użytkownika nie jest awarią i nie uruchamia
automatycznych ponowień. Nie zachowujemy plików ręcznie przerwanej analizy
jako wersji schematu oznaczonej „przerwana”. Po potwierdzonym ręcznym
zatrzymaniu usuwamy wgrane dla tej analizy pliki i jej częściowy wynik,
pozostawiając wcześniejsze wersje schematu bez zmian.
Przed ręcznym przerwaniem interfejs wymaga potwierdzenia i ostrzega
o usunięciu wgranych dla tej analizy plików oraz częściowego wyniku.
Rezygnacja z potwierdzenia nie przerywa analizy ani nie usuwa jej danych.
Techniczne potwierdzenie zatrzymania, sposób sprzątania oraz obsługa
błędu usuwania pozostają do uzgodnienia. Decyzja nie zmienia zachowania
po awarii ani po błędzie analizy kompletnej paczki.

**Nieudana analiza nowej wersji DDL — uzgodnione 14 listopada 2026
podczas planowania S2-T2:** zachowujemy przesłany DDL jako osobną wersję
z diagnostyką. Nie dopuszczamy tej wersji do generowania ani nie zastępujemy
nią dotychczasowej używanej wersji schematu. Użytkownik może wgrać
poprawiony pełny DDL jako kolejną wersję. Jeżeli projekt nie miał jeszcze
wersji dopuszczonej do użycia, sama nieudana analiza takiej wersji nie tworzy.
Błędy transferu i zapisu opisano osobno powyżej.

**Lokalizacja błędów analizy — uzgodnione 14 listopada 2026 podczas
planowania S2:** diagnostyka wskazuje nazwę oryginalnego pliku i numer
wiersza w tym pliku, jeżeli miejsce błędu można ustalić. Nie zastępujemy
tej lokalizacji samym numerem wiersza w połączonym skrypcie. Dla problemu
dotyczącego całej paczki pokazujemy opis bez sztucznego przypisywania
do konkretnego pliku lub wiersza. Kontrakt diagnostyki i sposób mapowania
pozycji pozostają do uzgodnienia.

**Wybór wersji po udanej analizie — uzgodnione 14 listopada 2026
podczas planowania S2-T2:** nowa wersja DDL po poprawnej analizie,
bez blokad uniemożliwiających jej użycie, automatycznie staje się
domyślną wersją dla nowych zleceń. Rozpoczęte wykonania zachowują
wcześniej przypięte wymagania zgodnie z REQ-014. Nie oznacza to
automatycznego przeniesienia zatwierdzenia reguł biznesowych ani
relacji spoza DDL.

**Reguły i relacje po zmianie DDL — uzgodnione 14 listopada 2026
podczas planowania S2-T2:** reguły biznesowe i zatwierdzone relacje
spoza DDL z poprzedniej wersji wymagają ponownej weryfikacji
i zatwierdzenia przed użyciem z nową wersją schematu. Wcześniejsze
zatwierdzenie nie wystarcza, nawet jeżeli ustalenie wydaje się pasować
do nowego schematu. Dotychczasowe reguły i relacje pokazujemy jako
propozycje do przeglądu, bez konieczności wpisywania ich od początku.
Nie obowiązują z nową wersją do czasu ponownej weryfikacji i zatwierdzenia.
Start generowania na nowym schemacie jest zablokowany, dopóki użytkownik
nie rozpatrzy każdej propozycji: zatwierdzi ją po weryfikacji albo
świadomie odrzuci dla nowej wersji. Sam wybór nowej wersji jako domyślnej
nie oznacza gotowości do generowania. Zakończenie przeglądu nie omija
innych blokad. Rozpoczęte wykonania pozostają bez zmian.

**Obsługiwane typy kolumn — uzgodnione 14 listopada 2026 podczas planowania S2:**
`smallint`, `integer`, `bigint`, `numeric`/`decimal` z precyzją i skalą,
`text`, `varchar` z ograniczeniem długości, `boolean`, `uuid`, `date`,
`timestamp` i `timestamptz`. Zatwierdzenie tej listy nie rozstrzyga
mechanizmu automatycznych identyfikatorów, postaci ograniczeń i wyrażeń,
parsera ani wersji silnika. Pozostałe szczegóły OD-01 nadal są otwarte.

**Klucze wielokolumnowe — uzgodnione 14 listopada 2026 podczas planowania S2:**
obsługa `PRIMARY KEY`, `FOREIGN KEY` i `UNIQUE` obejmuje również
ograniczenia złożone z kilku kolumn. Nie rozstrzyga to pozostałych
wariantów ograniczeń, np. ich odraczania, ani szczegółów relacji
zatwierdzanych poza DDL.

**Zakres `CHECK` — uzgodniony 14 listopada 2026 podczas planowania S2:**
porównania, zakresy (`BETWEEN`), zbiory wartości (`IN`) i łączenie
warunków przez `AND`, `OR` i `NOT` w obrębie jednego rekordu.
Wywołania funkcji wewnątrz `CHECK` są poza tym zakresem i podlegają
jawnej diagnostyce zgodnie z REQ-013.

**Zakres `DEFAULT` — uzgodniony 14 listopada 2026 podczas planowania S2:**
obsługujemy stałe zgodne z obsługiwanymi typami kolumn oraz
`CURRENT_DATE` i `CURRENT_TIMESTAMP`. Inne wywołania funkcji i dowolne
wyrażenia pozostają poza tym zakresem i podlegają diagnostyce zgodnie
z REQ-013. Mechanizmy automatycznych identyfikatorów opisano osobno
poniżej; nie rozszerzają ogólnej listy dopuszczonych wyrażeń `DEFAULT`.

**Automatyczne identyfikatory — uzgodnione 14 listopada 2026 podczas planowania S2:**
obsługiwane definicje kolumn obejmują `serial`, `bigserial`,
`GENERATED BY DEFAULT AS IDENTITY` i `GENERATED ALWAYS AS IDENTITY`.
Następnie zatwierdzono jawne wartości identyfikatorów w paczce również
dla tych kolumn: model przygotowuje je wraz z powiązaniami między rekordami,
bez odgadywania wartości nadanych dopiero podczas importu. Szczegółowy
profil importu SQL/CSV i obsługa sekwencji pozostają otwarte.
Nie zmieniamy DDL użytkownika, aby ominąć wymagania tych mechanizmów.

**Niezależność od dziedziny projektu — potwierdzona 14 listopada 2026:**
projekty mogą opisywać różne dziedziny, np. bankowość, sklep lub e-commerce.
Rozpoznawanie struktury i ograniczeń wynika z dostarczonego DDL,
nie ze stałej listy nazw tabel, kolumn czy statusów. Przykłady w dokumentacji
nie są zamkniętym katalogiem obsługiwanych projektów. Nadal obowiązuje
uzgodniony zakres konstrukcji PostgreSQL; różnorodność dziedzin nie oznacza
obsługi dowolnego DDL ani wszystkich reguł biznesowych.

### 5.2. Reguły biznesowe i wskazówki jakościowe

| ID | Wymaganie |
| --- | --- |
| REQ-015 | Użytkownik może podawać reguły biznesowe w języku naturalnym w kontekście projektu lub przygotowywanego zlecenia. Zatwierdzone reguły projektu obowiązują we wszystkich jego nowych zleceniach. Reguła dodana do pojedynczego zlecenia obowiązuje tylko w nim i nie zapisuje się automatycznie w projekcie. Wykryty konflikt wymaga wyjaśnienia zgodnie z REQ-019; reguła zlecenia nie nadpisuje po cichu reguły projektu. Szczegóły organizacji tych informacji w interfejsie pozostają do ustalenia. |
| REQ-016 | Przed generowaniem użytkownik zatwierdza interpretację reguły i znaczenie jej sprawdzenia. LLM proponuje rodzaj reguły z uzgodnionego katalogu i jej parametry, aplikacja sprawdza obsługiwalność tej definicji, a użytkownik zatwierdza czytelny opis znaczenia sprawdzenia. Walidator sprawdza dane gotowym mechanizmem danego rodzaju, zamiast wykonywać kod napisany przez model. Aplikacja nie ocenia konfiguracji według nieujawnionej interpretacji wymagania. Szczegółowy format definicji pozostaje do uzgodnienia w OD-06. |
| REQ-017 | Reguła niejednoznaczna lub nieweryfikowalna automatycznie jest jawnie oznaczana; aplikacja nie przypisuje jej fikcyjnego wyniku „spełniona”. Gdy aplikacja nie potrafi automatycznie sprawdzić reguły, blokuje rozpoczęcie generowania, informuje użytkownika o problemie i pozwala wybrać kontynuowanie bez tej reguły albo jej poprawienie. Bez świadomego wyboru użytkownika generowanie nie rozpoczyna się. Wybranie poprawy nie usuwa blokady samo w sobie: poprawiona reguła wymaga ustalenia obsługiwanej interpretacji i jej zatwierdzenia zgodnie z REQ-016. Kontynuowanie bez reguły nie oznacza jej spełnienia ani automatycznej zamiany we wskazówkę jakościową. Wybranie „Kontynuuj bez tej reguły” dla reguły zapisanej w projekcie pomija ją wyłącznie w bieżącym zleceniu, bez usuwania lub zmiany reguły projektu. W kolejnych nowych zleceniach reguła nadal obowiązuje, chyba że użytkownik ponownie świadomie wybierze jej pominięcie zgodnie z tym wymaganiem. |
| REQ-018 | Wskazówki jakościowe pozostają częścią wymagań przekazywanych do generowania, ale ich spełnienie podlega ocenie poza automatycznym raportem zgodności. |
| REQ-019 | Wykryty konflikt między wymaganiami wymaga wyjaśnienia przed rozpoczęciem generowania. Aplikacja nie zmienia ani nie ignoruje po cichu jednej ze stron konfliktu. |
| REQ-071 | MVP automatycznie sprawdza ograniczony, jawnie zdefiniowany rodzaj reguły między tabelami: wartość rekordu nadrzędnego ma odpowiadać sumie iloczynów dwóch pól jego rekordów podrzędnych, np. wartość zamówienia równa sumie `ilość × cena` jego pozycji. Nie oznacza to obsługi dowolnych obliczeń ani dowolnego kodu modelu. Szczegóły definicji i obliczeń wymagają rozstrzygnięcia w OD-06 przed implementacją tego sprawdzenia. |

**Katalog MVP — uzgodniony 14 listopada 2026 podczas planowania S3:** poza ograniczoną regułą sumującą z REQ-071 automatyczne sprawdzanie obejmuje porównanie kolumn, porównanie wartości z progiem, zakresem lub zbiorem oraz regułę warunkową. Przykładami są data dostawy późniejsza niż data zakupu oraz wymagana data dostawy przy określonym statusie. Zatwierdzenie tych rodzajów nie rozstrzyga jeszcze obsługiwanych operatorów i typów, znaczenia NULL, zakresu sprawdzenia, jednostki naruszenia ani wykonywalnej reprezentacji. Te szczegóły nadal wymagają OD-06; nie obiecujemy obsługi dowolnego warunku tekstowego ani dowolnego kodu modelu.

**Porównanie kolumn — uzgodnione 14 listopada 2026 podczas doprecyzowania S3-T1:** ten rodzaj reguły obejmuje dwie kolumny tego samego rekordu w jednej tabeli, np. porównanie daty dostawy z datą zakupu. Nie obejmuje porównań kolumn różnych rekordów ani różnych tabel. Nie ogranicza osobnego, uzgodnionego rodzaju reguły sumującej między tabelami. Uzgodniono sześć operacji: równe, różne, mniejsze, mniejsze lub równe, większe i większe lub równe. Jest to katalog operacji, nie zgoda na użycie każdej z nich dla dowolnej pary typów. Pary typów i dostępne operacje określa poniższa macierz. Dla tego rodzaju reguły NULL w którejkolwiek z porównywanych kolumn oznacza naruszenie, także gdy obie wartości są NULL. Rekord nie jest pomijany ani uznawany za zgodny. Nie zmienia to dopuszczalności NULL w oryginalnym DDL ani nie ustala zasad NULL dla pozostałych rodzajów reguł. Dla tekstu równość i różność dotyczą dokładnej treści, z uwzględnieniem wielkości liter i wszystkich spacji, bez automatycznego przekształcania wartości. Przykładowo „ABC” i „abc” są różne, podobnie „ABC” i „ABC ”. Zapis operatorów w definicji nadal wymaga OD-06.

**Zakres i jednostka naruszenia porównania kolumn — uzgodnione 14 listopada 2026 podczas doprecyzowania S3-T1:** sprawdzamy wszystkie rekordy wskazanej tabeli w zaimportowanej paczce. Jeden niezgodny rekord oznacza jedno naruszenie tej reguły, także gdy obie porównywane wartości są NULL. Przykładowo 7 niezgodnych rekordów spośród 100 daje 7 naruszeń wśród 100 sprawdzonych. Nie rozszerza to tej jednostki na pozostałe rodzaje reguł.

**Macierz porównania kolumn — uzgodniona 14 listopada 2026 podczas doprecyzowania S3-T1:**

| Porównywane typy | Dostępne operacje |
| --- | --- |
| Dowolna para spośród `smallint`, `integer`, `bigint`, `numeric`/`decimal` | Wszystkie sześć. |
| `date` z `date` | Wszystkie sześć. |
| `timestamp` z `timestamp` | Wszystkie sześć. |
| `timestamptz` z `timestamptz` | Wszystkie sześć. |
| Dowolna para spośród `text` i `varchar` | Równe, różne. |
| `boolean` z `boolean` | Równe, różne. |
| `uuid` z `uuid` | Równe, różne. |

Pozostałe pary są nieobsługiwane, bez automatycznego dopasowywania typów poza porównaniami wewnątrz wymienionych grup. Nie dopuszczamy np. porównania liczby z tekstem ani `date` z `timestamp`. To zakres tego rodzaju reguły w aplikacji, nie deklaracja pełnych możliwości PostgreSQL. Nie rozszerza automatycznie zakresu pozostałych rodzajów reguł.

**Porównanie kolumny ze stałą, zakresem lub zbiorem — uzgodniony zakres 14 listopada 2026 podczas doprecyzowania S3-T1:** ten rodzaj reguły dotyczy pojedynczej kolumny rekordu porównywanej ze stałą wartością, stałymi granicami zakresu albo jawnym zbiorem stałych wartości. Nie obejmuje obliczeń ani odwołań do innych rekordów lub tabel. Wariant „wartość w zakresie” obejmuje obie granice (przedział domknięty z obu stron), np. dla 18–65 dopuszcza również 18 i 65. W tym wariancie MVP nie ma wyboru granic otwartych. Wariant „wartość w zakresie” obsługuje wyłącznie kolumny smallint, integer, bigint, numeric/decimal, date, timestamp i timestamptz. Zakresy dla text, varchar, boolean i uuid są nieobsługiwane. Dla kolumny liczbowej obie granice zakresu są liczbami ze wspólnej grupy smallint/integer/bigint/numeric/decimal. Dla date, timestamp i timestamptz obie granice mają dokładnie ten sam typ co kolumna. Pozostałe połączenia są nieobsługiwane, bez automatycznych konwersji między tymi grupami, np. tekst–liczba i date–timestamp. Dotyczy to typów w definicji reguły, nie rozpoznawania polecenia przez LLM. W wariancie „wartość w zakresie” NULL w sprawdzanej kolumnie zawsze oznacza naruszenie reguły. Rekordu nie pomijamy i nie zmieniamy oryginalnego DDL. Na przykład brak wieku narusza regułę „wiek w zakresie 18–65”. Zakres sprawdzania i jednostkę naruszenia określa wspólna zasada prostych porównań poniżej. Wariant „wartość w zakresie” wymaga obu granic innych niż NULL. Brak którejkolwiek granicy lub NULL zamiast niej oznacza błędną definicję z czytelnym komunikatem. Nie traktujemy brakującej granicy jako nieskończoności. Warunki jednostronne, np. „wiek co najmniej 18”, można opisać porównaniem z pojedynczą stałą. Dla prostych porównań (kolumna–kolumna, pojedyncza stała, zakres i zbiór) obowiązuje wspólna zasada: sprawdzamy wszystkie rekordy wskazanej tabeli w zaimportowanej paczce; każdy niezgodny rekord oznacza jedno naruszenie danej reguły. Wynik podaje liczbę naruszeń wobec liczby sprawdzonych rekordów, np. 7 wśród 100. Nie ustala to zasad reguł warunkowych i sumujących. Format granic nadal wymaga ustalenia. Dolna granica musi być mniejsza lub równa górnej. Zakres 18–18 jest poprawny i dopuszcza tylko 18. Zakres 65–18 jest błędną definicją: aplikacja wyświetla zrozumiały błąd i nie zamienia granic automatycznie. Dla porównania kolumny z pojedynczą stałą uzgodniono sześć operacji: równe, różne, mniejsze, mniejsze lub równe, większe oraz większe lub równe. To katalog operacji, nie dopuszczenie każdej z nich dla każdego typu. Dla kolumn smallint, integer, bigint, numeric/decimal, date, timestamp i timestamptz dostępne są wszystkie sześć operacji. Dla text, varchar, boolean i uuid dostępne są tylko równe i różne. W porównaniu z pojedynczą stałą wymagamy zgodności typów: liczby porównujemy w grupie smallint/integer/bigint/numeric/decimal, tekst w grupie text/varchar, a date, timestamp, timestamptz, boolean i uuid każde wyłącznie ze stałą swojego typu. Pozostałe pary są nieobsługiwane, bez automatycznych konwersji między grupami, np. liczba–tekst i date–timestamp. Dotyczy to typów w definicji reguły, nie sposobu rozpoznawania polecenia przez LLM. W porównaniu kolumny z pojedynczą stałą inną niż NULL brak wartości (NULL) w kolumnie zawsze oznacza naruszenie, także przy operacji „różne”. Rekordu nie pomijamy ani nie uznajemy za zgodny. Na przykład brak statusu narusza regułę „status różny od anulowany”. Nie zmieniamy oryginalnego DDL. NULL w sprawdzanej kolumnie narusza obie operacje zbioru. Równość i różność tekstu w porównaniu kolumny z pojedynczą stałą dotyczą dokładnej treści, z uwzględnieniem wielkości liter i wszystkich spacji, bez automatycznego przekształcania. „ABC” jest różne od „abc” i od „ABC ” (ze spacją na końcu). Decyzji nie rozszerzono na zakresy ani zbiory. Porównanie z pojedynczą stałą obejmuje wszystkie rekordy wskazanej tabeli w zaimportowanej paczce. Każdy niezgodny rekord, także z NULL, oznacza jedno naruszenie tej reguły. Przykładowo 7 niezgodnych rekordów spośród 100 daje 7 naruszeń wśród 100 sprawdzonych. Wspólna zasada poniżej obejmuje również zakresy i zbiory. W wariancie porównania z pojedynczą stałą NULL nie może występować po stronie stałej. Definicje „równe NULL” i „różne od NULL” są nieobsługiwane w tym wariancie; aplikacja podaje czytelną przyczynę zamiast wykonywać zwykłe porównanie. Ewentualne osobne sprawdzanie obecności lub braku wartości pozostaje do ustalenia. Nie usuwa to uzgodnionego wymagania obsługi reguły warunkowej z wymaganą datą dostawy przy określonym statusie. Format stałych i zapis operatorów pozostają otwarte. Porównanie ze zbiorem obsługuje dwie operacje: „należy do zbioru” oraz „nie należy do zbioru”. Przykładowo status ma należeć do listy {nowy, opłacony, wysłany} albo nie należeć do listy {anulowany, odrzucony}. W obu operacjach porównania ze zbiorem definicja musi zawierać niepustą listę stałych innych niż NULL. Pusta lista lub NULL jako element oznacza błędną definicję z czytelną informacją o przyczynie, zamiast wykonania reguły. Dotyczy to listy w definicji, nie braku wartości w sprawdzanym rekordzie. Obie operacje zbioru korzystają z uzgodnionych zasad porównania z pojedynczą stałą: „należy” wymaga spełnienia porównania „równe” z co najmniej jednym elementem, a „nie należy” spełnienia porównania „różne” ze wszystkimi elementami. Każdy element musi być zgodny typowo z kolumną: liczby w grupie smallint/integer/bigint/numeric/decimal, tekst w grupie text/varchar, a date, timestamp, timestamptz, boolean i uuid każde ze swoim typem. Nie stosujemy konwersji między tymi grupami i nie pomijamy niezgodnych elementów definicji. Tekst porównujemy dokładnie, z uwzględnieniem wielkości liter i wszystkich spacji. NULL w sprawdzanej kolumnie oznacza naruszenie w obu operacjach. Format zapisu stałych nadal wymaga OD-06. Nie zmienia to osobnej reguły sumującej między tabelami.

**Postać reguły warunkowej — uzgodniona 14 listopada 2026 podczas doprecyzowania S3-T1:** Reguła warunkowa w MVP ma postać „jeśli jeden warunek, to jedno wymaganie” i dotyczy tego samego rekordu jednej tabeli. Nie ma gałęzi „w przeciwnym razie” ani zagnieżdżonych reguł. Przykład: jeśli status jest równy „wysłany”, data dostawy musi być podana. Osobna reguła sumująca między tabelami pozostaje w MVP. Warunek i wymaganie korzystają z tego samego katalogu pojedynczych sprawdzeń: porównanie dwóch kolumn, porównanie z pojedynczą stałą, zakres, zbiór, „wartość jest NULL” oraz „wartość nie jest NULL”. Każdy człon jest jednym sprawdzeniem, bez łączenia przez „i”/„lub”; wszystkie odwołania dotyczą tego samego rekordu. „Wartość nie jest NULL” oznacza obecność wartości, nie sprawdzanie niepustości tekstu. Gdy warunek jest spełniony, oceniamy wymaganie: jego spełnienie oznacza zgodność, a niespełnienie naruszenie. Gdy warunek jest niespełniony przy dostępnych danych, wynik to „nie dotyczy”: wymagania nie oceniamy i nie zgłaszamy naruszenia. NULL w wartości potrzebnej do zwykłego porównania w warunku oznacza naruszenie całej reguły, a nie „nie dotyczy”. Jawne sprawdzenia „jest NULL” i „nie jest NULL” normalnie rozstrzygają warunek. Na przykład dla „jeśli status = wysłany, data dostawy nie jest NULL” status nowy daje „nie dotyczy”, status wysłany bez daty naruszenie, a status NULL również naruszenie. Reguła warunkowa obejmuje wszystkie rekordy wskazanej tabeli w zaimportowanej paczce. Raport rozlicza je w trzech rozłącznych grupach: zgodne, naruszenia i „nie dotyczy”. Każdy rekord trafia do jednej grupy i daje najwyżej jedno naruszenie danej reguły, również przy NULL w warunku. Rekordów „nie dotyczy” nie przedstawiamy jako spełniających wymaganie. Przykładowo 100 ocenionych rekordów to 35 zgodnych, 5 naruszeń i 60 „nie dotyczy”.

**Powiązanie i zakres sumowania — uzgodnione 14 listopada 2026 podczas doprecyzowania S3-T1:** Reguła sumująca obejmuje wszystkie pozycje danego rekordu nadrzędnego w paczce, powiązane jedną jawnie wskazaną obowiązującą relacją. Nie obejmuje dodatkowego filtrowania pozycji ani przechodzenia przez kolejne tabele. Relacja pochodzi z DDL albo jest zatwierdzona poza nim zgodnie z REQ-012; aplikacja nie wybiera jej domyślnie. Przykład: wartość zamówienia równa sumie ilość × cena wszystkich jego pozycji, a nie tylko pozycji wybranego statusu.

**Brak wartości w sumowaniu — uzgodnione 14 listopada 2026 podczas doprecyzowania S3-T1:** NULL w wartości rekordu nadrzędnego albo w którymkolwiek z dwóch mnożonych pól którejkolwiek powiązanej pozycji oznacza naruszenie reguły sumującej dla rekordu nadrzędnego. Nie zastępujemy NULL zerem i nie pomijamy niekompletnych pozycji. Na przykład zamówienie z pozycją bez ceny narusza regułę, zamiast być sprawdzane wyłącznie na podstawie sumy pozostałych pozycji.

**Brak pozycji — uzgodnione 14 listopada 2026 podczas doprecyzowania S3-T1:** Przy braku powiązanych pozycji suma wynosi 0. Rekord nadrzędny bez pozycji spełnia regułę sumującą wyłącznie wtedy, gdy jego wartość wynosi 0; inna wartość daje naruszenie, a NULL pozostaje naruszeniem zgodnie z zasadą brakujących wartości. Brak pozycji sam w sobie nie narusza tej reguły. Nie zmienia to wymagań DDL ani innych reguł, które mogą wymagać istnienia pozycji.

**Porównanie wyniku sumowania — uzgodnione 14 listopada 2026 podczas doprecyzowania S3-T1:** Wartość nadrzędną porównujemy dokładnie z sumą już zaokrąglonych pozycji, bez tolerancji różnicy i bez dodatkowego zaokrąglania wartości nadrzędnej lub sumy. Porównujemy wartość liczbową, nie liczbę zer w zapisie. Dla sumy 19,99 wartość nadrzędna 19,990 daje zgodność, a 19,991 naruszenie.

**Dziedzina i dokładność sumowania — uzgodnione 14 listopada 2026 podczas doprecyzowania S3-T1:** Reguła sumująca operuje wyłącznie na typach smallint, integer, bigint i numeric/decimal we wszystkich trzech polach: wartości nadrzędnej oraz obu mnożonych polach pozycji. Obliczenia zachowują dokładność dziesiętną, bez przybliżania przez binarne liczby zmiennoprzecinkowe i bez automatycznej zamiany tekstu na liczby. Nie wybiera to biblioteki ani reprezentacji API.

Dla REQ-071 uzgodniono stałą kolejność obliczeń: najpierw obliczamy i zaokrąglamy wartość każdej pozycji, a następnie sumujemy te wartości. Aplikacja nie pyta użytkownika o wybór tej kolejności. Liczba miejsc po przecinku, do której zaokrąglamy iloczyn każdej pozycji, jest jawnym parametrem konkretnej reguły sumującej, widocznym w interpretacji do zatwierdzenia. Reguły mogą wskazywać różną precyzję, np. 2 albo 3 miejsca. Nie narzucamy dwóch miejsc wszystkim regułom ani nie wyprowadzamy precyzji po cichu ze schematu. W MVP stosujemy jeden tryb zaokrąglania iloczynu pozycji: do najbliższej wartości o zadanej liczbie miejsc, a przy dokładnej połowie — od zera. Dla 2 miejsc: 1,234 daje 1,23; 1,235 daje 1,24; −1,235 daje −1,24. Tryb jest stałą zasadą aplikacji, widoczną w interpretacji reguły, bez wyboru innego trybu. Dozwolony zakres parametru precyzji pozostaje otwarty.

Przykładowy podział:

| Wymaganie | Traktowanie |
| --- | --- |
| Kolumna wymagana w DDL nie może być pusta | Warunek zgodności ze schematem, wpływający na importowalność. |
| Dokładnie 200 rekordów zakupów | Warunek kompletności, wpływający na wykonanie zadania. |
| Zatwierdzone powiązanie zakupu z klientem, bez klucza obcego w DDL | Obowiązująca relacja; jej naruszenie blokuje wykonanie zadania mimo udanego importu. |
| Data dostawy ma być późniejsza niż data zakupu, bez takiego ograniczenia w DDL | Dodatkowa reguła biznesowa, o ile zatwierdzono sposób jej sprawdzania. |
| Łączna wartość zakupu ma odpowiadać sumie `ilość × cena` jego pozycji | Rodzaj reguły objęty MVP (REQ-071); wymaga jednoznacznego ustalenia uwzględnianych pól i obliczeń. |
| Zakupy mają wyglądać realistycznie | Wskazówka jakościowa, oceniana przez użytkownika lub jego zewnętrzne narzędzie. |

**Istotne rozróżnienie:** jeśli reguła biznesowa jest również ograniczeniem zapisanym w DDL i jej naruszenie uniemożliwia import, stanowi także warunek importowalności. Nie można wtedy uznać wyniku za wykonany, powołując się na zasadę łagodniejszego traktowania dodatkowych reguł.

Zatwierdzona relacja nieobecna w DDL także nie jest łagodniej traktowaną dodatkową regułą biznesową. Jej zgodność trzeba potwierdzić niezależnie od wyniku importu (REQ-012).

Aplikacja nie gwarantuje wykrycia każdej możliwej sprzeczności przed generowaniem. Wymaganie dotyczy właściwej reakcji na konflikty, które rzeczywiście rozpozna.

## 6. Przygotowanie zlecenia

### 6.1. Interpretacja intencji

| ID | Wymaganie |
| --- | --- |
| REQ-020 | Użytkownik zleca generowanie w języku naturalnym, bez konieczności samodzielnego wypisywania wszystkich potrzebnych tabel. |
| REQ-021 | Aplikacja ustala potrzebny zakres danych na podstawie polecenia, schematu, zatwierdzonych relacji i reguł. |
| REQ-022 | Istotne niejasności dotyczące znaczenia lub zakresu zlecenia są wyjaśniane przez pytania do użytkownika przed generowaniem. |
| REQ-023 | Wartości i szczegóły, których użytkownik nie ograniczył i które nie wymagają rozstrzygnięcia dla poprawności zadania, mogą zostać dobrane w procesie generowania bez osobnego pytania o każdy rekord. |

Przykład istotnej niejasności: „200 zakupów klientów VIP”, gdy projekt nie definiuje znaczenia VIP. Aplikacja nie powinna arbitralnie ustalać, że VIP oznacza określony poziom wydatków.

### 6.2. Zatwierdzony plan danych

| ID | Wymaganie |
| --- | --- |
| REQ-024 | Przed generowaniem zostają ustalone liczebności dla wszystkich tabel objętych zleceniem, nie tylko dla encji wymienionej w poleceniu. |
| REQ-025 | Aplikacja może zaproponować liczebności danych powiązanych; użytkownik zatwierdza je przed wykonaniem. Nie musi przygotowywać ich ręcznie od początku. |
| REQ-026 | Zatwierdzony zakres, liczebności, reguły, schemat i wybrany format wyniku stanowią ustalone wymagania wykonania. Proces nie może ich samowolnie upraszczać, aby uzyskać sukces. |

Przykładowy plan dla polecenia „200 zakupów”:

| Tabela | Oczekiwana liczba rekordów |
| --- | --- |
| Kupujący | 50 |
| Produkty | 30 |
| Zakupy | 200 |
| Pozycje zakupów | 600 |

Liczby są przykładowe. Nie stanowią domyślnych proporcji dla każdego projektu. Zlecenie nie wymaga uzupełnienia każdej tabeli całego schematu, tylko uzgodnionego zakresu potrzebnego do jego realizacji.

## 7. Warunki wykonania i ocena jakości

### 7.1. Dwa niezależne wymiary wyniku

| Wymiar | Pytanie | Znaczenie |
| --- | --- | --- |
| Wykonanie | Czy wynik jest kompletny, importowalny i zgodny ze wszystkimi obowiązującymi relacjami? | Rozstrzyga wykonanie zadania. |
| Zgodność biznesowa | Które sprawdzalne dodatkowe reguły są spełnione? | Opisuje jakość i uruchamia poprawki, ale samo naruszenie nie musi oznaczać niewykonania. |
| Realizm i użyteczność | Czy dane są wiarygodne i przydatne do zamierzonego testu? | Ocena użytkownika poza generatorem, ewentualnie ze wsparciem LLM. |

| ID | Wymaganie |
| --- | --- |
| REQ-027 | Zadanie jest wykonane wyłącznie wtedy, gdy wybrany wynik jest kompletny, importowalny i ma potwierdzoną zgodność ze wszystkimi obowiązującymi relacjami, także zatwierdzonymi poza DDL. |
| REQ-028 | Brak wymaganej liczby rekordów oznacza niewykonanie zadania, nawet jeśli dostępna część nadaje się do importu. |
| REQ-029 | Naruszenia dodatkowych reguł biznesowych obniżają zgodność jakościową, ale nie odbierają statusu wykonania wynikowi spełniającemu obowiązkowe warunki REQ-027. Zasada ta nie dotyczy obowiązujących relacji, także zatwierdzonych poza DDL. |
| REQ-030 | Importowalność jest potwierdzana rzeczywistym próbnym importem kandydata do pustego, odizolowanego środowiska PostgreSQL z zatwierdzonym schematem. Dla SQL sprawdzane są gotowe polecenia `INSERT`, a dla CSV rzeczywisty import plików. Zakres potwierdzenia musi być jawny; sama analiza statyczna lub deklaracja modelu nie jest dowodem udanego importu. |
| REQ-031 | Niewykonane, nieobsługiwane lub nierozstrzygnięte sprawdzenie nie może zostać przedstawione jako pozytywna weryfikacja. Jeśli dotyczy obowiązkowego warunku wykonania, aplikacja nie może potwierdzić sukcesu. |

Uzgodniono cztery kolejne etapy walidacji:

1. **Składnia i format** — sprawdzenie budowy SQL/CSV i dozwolonego zakresu konstrukcji, bez wykonania danych.
2. **Wstępna zgodność ze schematem i typami** — istnienie tabel i kolumn, zgodność liczby pól oraz możliwe do wiarygodnego wykrycia błędy wartości. Nie budujemy odrębnego pełnego systemu typów PostgreSQL i nie zmieniamy danych przez ciche konwersje.
3. **Próbny import, relacje i kompletność** — rzeczywiste wykonanie gotowych `INSERT` lub import CSV potwierdza typy i obsługiwane ograniczenia schematu, w tym relacje zadeklarowane w DDL. Na załadowanych danych osobno sprawdzamy zatwierdzone relacje nieobecne w DDL oraz rzeczywisty zakres i liczebności wobec planu. Dla CSV projekt zakłada `COPY FROM STDIN`, bez tworzenia zastępczych `INSERT`.
4. **Dodatkowe reguły biznesowe** — sprawdzenie zatwierdzonych kryteriów na załadowanych danych. Nie zastępują ograniczeń zapisanych w DDL.

Wstępne sprawdzenie typów nie jest ostatecznym potwierdzeniem importowalności. Jeżeli wcześniejszy etap uniemożliwia dalsze sprawdzenia, są one oznaczane jako niewykonane, a nie pozytywne. Naruszenia danych uruchamiają poprawki w dostępnym limicie; awarie techniczne zatrzymują wykonanie bez retry.

Udany import i zgodność relacji zatwierdzonych poza DDL to odrębne wyniki. Naruszenie lub brak potwierdzenia takiej relacji blokuje sukces, ale nie zmienia udanego importu w nieudany ani nie oznacza automatycznej zmiany schematu.

Szczegółowy zapis uzgodnienia i odrębnych propozycji znajduje się w [projekcie walidacji](lld/walidacja.md). Zatwierdzenie kolejności i próbnego importu nie zatwierdza całej proponowanej macierzy typów, profilu plików ani katalogu reguł biznesowych.

### 7.2. Zakres sprawdzeń

Raport powinien rozróżniać:

1. poprawność wybranego formatu wyjściowego;
2. zgodność z obsługiwanymi typami i ograniczeniami schematu;
3. integralność relacji w całej paczce, nie wyłącznie poprawność pojedynczych plików;
4. zgodność zakresu i liczebności z zatwierdzonym planem;
5. zgodność ze sprawdzalnymi dodatkowymi regułami;
6. wskazówki jakościowe pozostawione do oceny zewnętrznej.

Przykłady interpretacji:

| Wynik | Ocena wykonania |
| --- | --- |
| 200 zakupów, wymagana reszta paczki, importowalność i zgodność obowiązujących relacji potwierdzone, brak naruszeń dodatkowych reguł | Wykonane; brak wykrytych naruszeń sprawdzalnych reguł. |
| Taka sama kompletna paczka, ale 7 zakupów narusza dodatkową regułę dat dostawy | Wykonane z naruszeniami biznesowymi; naruszenia są raportowane i mogą uruchomić poprawki. |
| 150 zamiast wymaganych 200 zakupów | Niewykonane z powodu niekompletności. |
| 200 zakupów, ale odwołanie do nieistniejącego klienta narusza klucz obcy z DDL | Niewykonane z powodu braku potwierdzonej importowalności. |
| Import 200 zakupów udał się, ale odwołanie do nieistniejącego klienta narusza relację zatwierdzoną poza DDL | Niewykonane z powodu naruszenia obowiązującej relacji; raport zachowuje informację o udanym imporcie. |
| Prawidłowe pliki, ale obowiązkowego sprawdzenia nie udało się przeprowadzić | Wykonanie niepotwierdzone, a nie sukces. |
| Poprawny i kompletny wynik zawiera mało realistyczne, powtarzalne opisy, których nie ograniczała żadna sprawdzalna reguła | Może być wykonane; realizm pozostaje do oceny zewnętrznej. |

„Brak wykrytych naruszeń” nie oznacza gwarancji realizmu ani sprawdzenia wymagań oznaczonych jako jakościowe.

## 8. Generowanie, poprawki i zakończenie

### 8.1. Główny przebieg

1. Użytkownik w głównym oknie czatu wybiera zapisany projekt i wprowadza zlecenie.
2. Aplikacja ustala znaczenie i zakres polecenia.
3. Użytkownik rozstrzyga wykryte niejasności, brakujące relacje i interpretacje reguł.
4. Powstaje zatwierdzony plan danych z liczebnościami i formatem wyniku.
5. Aplikacja rozpoczyna wykonanie, przypisując do niego wymagania i faktycznie używany wariant generowania.
6. Proces przygotowuje pierwszy kandydat wyniku.
7. Aplikacja sprawdza kompletność, importowalność, obowiązujące relacje i dodatkowe reguły.
8. Naruszenia uruchamiają poprawki, jeśli pozostał dopuszczalny limit.
9. Nowi kandydaci są sprawdzani i odróżniani od poprzednich w obrębie bieżącego wykonania. Nie powstaje archiwum przebiegu dostępne jako historia.
10. Proces kończy się po uzyskaniu wymaganego wyniku bez dalszych wykrytych naruszeń sprawdzalnych reguł, wyczerpaniu limitu, anulowaniu lub wystąpieniu błędu uniemożliwiającego kontynuację.
11. Użytkownik otrzymuje status, dostępny wynik i prosty raport.
12. Może kontynuować rozmowę w tym samym czacie. Przy prośbie o zmianę otrzymanych danych LLM dostaje dotychczasową paczkę jako kontekst wraz z nowym poleceniem, poprawia wskazane dane i zwraca poprawioną paczkę do walidacji (REQ-076). Nowa prośba ma własny limit automatycznych poprawek zgodnie z REQ-033–REQ-034. Nie jest automatyczną kolejną rundą wcześniejszej prośby ani wznowieniem zakończonego procesu. Przypisanie jej do zlecenia lub wykonania pozostaje w OD-10.

| ID | Wymaganie |
| --- | --- |
| REQ-068 | Model przygotowuje gotowy wynik w wybranym formacie: polecenia `INSERT` albo treść plików CSV. Aplikacja może wyodrębniać, zapisywać, sprawdzać i pakować tę zawartość, ale nie zastępuje jej deterministycznym generowaniem SQL/CSV z pośrednich rekordów ani nie poprawia po cichu danych. Zmieniona wersja danych jest osobnym kandydatem. |
| REQ-076 | Gdy użytkownik w bieżącym czacie prosi o zmianę otrzymanych danych, aplikacja przekazuje dotychczasową paczkę jako kontekst do LLM wraz z nowym poleceniem. Paczka jest podstawą modyfikacji, nie tylko przykładem do wygenerowania niezależnego zestawu. Model ma poprawić dane zgodnie z prośbą użytkownika, bez samowolnej zmiany pozostałych danych. Poprawiona paczka stanowi nowego kandydata i przed udostępnieniem jako użyteczny wynik przechodzi obowiązującą walidację. Jej raport dotyczy poprawionej wersji, nie poprzednika. |

Przykład: po otrzymaniu 100 klientów użytkownik prosi o zmianę ich adresów na polskie. Model dostaje tę paczkę i polecenie zmiany; zadaniem jest zmiana adresów w istniejących danych, a nie utworzenie innych 100 klientów. Konflikt nowej prośby ze schematem lub obowiązującymi regułami wymaga wyjaśnienia zgodnie z REQ-019. Nie zmieniamy wstecz wymagań i raportu wcześniejszego wyniku.

### 8.2. Zasady poprawek

| ID | Wymaganie |
| --- | --- |
| REQ-032 | Błędy kompletności, importowalności, obowiązujących relacji oraz sprawdzalnych reguł biznesowych uruchamiają automatyczne poprawki w granicach ustalonego limitu. |
| REQ-033 | Domyślny limit wynosi 3 automatyczne rundy naprawcze po przygotowaniu pierwszego kandydata dla danej prośby użytkownika. Dotyczy to zarówno początkowego generowania, jak i każdej nowej prośby o zmianę otrzymanej paczki zgodnie z REQ-076. |
| REQ-034 | Każda nowa prośba użytkownika o zmianę danych ma własny, niezależny limit poprawek; zużycie limitu przy wcześniejszej prośbie go nie pomniejsza. Limit jest wspólny dla wszystkich tabel i wywołań modeli obsługujących daną prośbę, nie dla całego czatu. Automatyczna poprawka, kolejna tabela ani wywołanie modelu nie odnawiają go. Zachowana zostaje możliwość zmiany limitu podczas badań i zapisania użytego ustawienia przy wykonaniu. |
| REQ-035 | Liczba rund poprawek i liczba wywołań modeli są rejestrowane jako odrębne informacje. Wariant wieloagentowy może wykonywać wiele wywołań w ramach jednego etapu. |
| REQ-036 | Poprawki muszą odnosić się do wykrytych problemów, bez samowolnej zmiany zatwierdzonych wymagań. Sposób i szczegółowość naprawy pozostają częścią badanego wariantu. |
| REQ-037 | Po wyczerpaniu limitu wykonanie kończy się z rzeczywistym wynikiem weryfikacji. Nie powstaje kolejna niejawna seria prób. Ręczne zlecenie dodatkowej serii po nieudanej zmianie danych określa REQ-079; nie jest ono automatycznym odnowieniem limitu. |
| REQ-079 | Po nieudanej zmianie danych opisanej w REQ-078 użytkownik może w nadal dostępnym czacie wybrać „Podejmij kolejne 3 próby”. Akcja nie jest dostępna po nieudanym pierwszym generowaniu, gdy nie uzyskano jeszcze użytecznej paczki. Przy domyślnym limicie akcja zleca maksymalnie 3 dodatkowe rundy naprawcze dla tej samej prośby, bez dodatkowego pierwszego kandydata poza tym limitem i bez zmiany zatwierdzonych wymagań. Pierwsza dodatkowa runda otrzymuje ostatniego nieudanego kandydata i listę błędów wykrytych w tej wersji. Model ma naprawiać tę wersję, zamiast ponownie zaczynać modyfikację od poprzedniej sprawdzonej paczki. Poprzednia sprawdzona paczka i jej raport pozostają chronione zgodnie z REQ-078. Dla jednej prośby o zmianę można uruchomić najwyżej jedną taką dodatkową serię. Seria rozpoczyna się wyłącznie po świadomej akcji użytkownika, nie automatycznie. Jeśli ona również nie da poprawionej paczki spełniającej REQ-027 dla tej prośby, kończymy naprawy i pokazujemy niepowodzenie, pozostawiając poprzednią sprawdzoną paczkę z jej raportem. Nie pokazujemy ponownie przycisku dla tej samej prośby. Może zakończyć się wcześniej zgodnie z zasadami zakończenia, anulowania i błędów technicznych. Nie oznacza wznawiania anulowanego, zakończonego błędem lub utraconego procesu. |

Limit 3 rund oznacza pierwszy kandydat i maksymalnie 3 kolejne rundy naprawcze, a nie łącznie 3 wywołania modelu. Wykryte naruszenie danych jest wynikiem walidacji i uruchamia poprawki w granicach tego limitu. Błąd techniczny nie jest rundą naprawczą: kończy wykonanie bez automatycznego ponowienia.

Przykład: po wykorzystaniu 3 rund dla wcześniejszej prośby użytkownik zleca zmianę adresów klientów. Pierwsza zmieniona paczka nie zużywa rundy naprawczej tej nowej prośby. Jeżeli walidacja wykryje naruszenia danych, dostępne są dla niej ponownie maksymalnie 3 automatyczne rundy naprawcze przy domyślnym ustawieniu. Nie odnawiamy limitu automatycznie. Dodatkowa seria dla tej samej nieudanej prośby wymaga ręcznej akcji z REQ-079. Techniczne przypisanie prośby i dodatkowej serii do wykonania nadal wymaga OD-10.

### 8.3. Zachowanie wcześniejszego wyniku

| ID | Wymaganie |
| --- | --- |
| REQ-038 | Użyteczny kandydat spełniający REQ-027 nie może zostać utracony tylko dlatego, że proces próbuje poprawić jego zgodność biznesową. |
| REQ-039 | Jako wynik zwracamy wyłącznie najnowszego użytecznego kandydata spełniającego REQ-027, według kolejności tworzenia kandydatów danego wykonania. Jeśli późniejsze poprawki nie spełniają tych warunków, zwracamy najnowszego wcześniejszego użytecznego kandydata. Raport wskazuje wybraną wersję i jej pozostałe naruszenia. |
| REQ-040 | Raport i eksportowane dane muszą dotyczyć tego samego kandydata. Nie wolno łączyć danych z jednej próby z pozytywnym raportem innej. |
| REQ-078 | Jeżeli przy zmianie danych zgodnie z REQ-076 po wyczerpaniu limitu napraw nie uzyskano poprawionej paczki spełniającej obowiązkowe warunki REQ-027 dla nowej prośby, użytkownik otrzymuje jasny komunikat o niepowodzeniu i liczbie wykorzystanych rund, domyślnie 3. W nadal dostępnym czacie pozostaje do pobrania poprzednia sprawdzona paczka wraz z raportem dotyczącym tej wersji. Jest oznaczona jako poprzednia wersja, nie wynik spełniający nową prośbę. Nie zmieniamy wstecz jej wymagań ani raportu i nie przedstawiamy nieudanej zmiany jako wykonanej. |

Wybór nie zależy od liczby ani wag dodatkowych naruszeń biznesowych. Nowszy użyteczny kandydat jest zwracany także wtedy, gdy ma ich więcej niż wcześniejszy. Zasada obowiązuje również przy pobieraniu paczki po anulowaniu lub błędzie zgodnie z REQ-047, w granicach bieżącego czatu (REQ-074). Nie wprowadzamy rankingu jakości. Stan roboczy musi zachować najnowszego użytecznego kandydata i jego raport na wypadek uszkodzenia danych przez późniejszą poprawkę; nie wymaga to archiwum wszystkich kandydatów ani historii zakończonych wykonań. Wybór kandydata dotyczy jednego wykonania. Zachowanie poprzedniej paczki po nieudanej kolejnej prośbie określa REQ-078; jej wcześniejsza walidacja nie potwierdza wykonania nowej prośby.

Przykładowy komunikat przy domyślnym limicie: „Nie udało się wprowadzić zmian mimo 3 rund naprawczych. Możesz pobrać poprzednią sprawdzoną wersję danych.” Obok dostępna jest akcja **„Podejmij kolejne 3 próby”** zgodnie z REQ-079. Oznacza ona do 3 dodatkowych rund, a nie nowego pierwszego kandydata i jeszcze 3 rundy. Uzgodnione 14 listopada 2026: dodatkowa seria zaczyna od ostatniego nieudanego kandydata i jego wykrytych błędów. Jeśli adresy zostały już zmienione zgodnie z prośbą, ale uszkodzono powiązania z zamówieniami, naprawiamy tę wersję zamiast zaczynać zmianę adresów od starej paczki. Stan roboczy musi zachować ostatniego nieudanego kandydata i wynik jego walidacji, oddzielnie od chronionej sprawdzonej paczki. Nie tworzy to archiwum wszystkich prób. Techniczne przypisanie serii do wykonania i liczników pozostaje w OD-10.

### 8.4. Anulowanie

| ID | Wymaganie |
| --- | --- |
| REQ-041 | Użytkownik może zlecić przerwanie trwającego wykonania. |
| REQ-042 | Status i raport bieżącego wykonania odróżniają anulowanie przez użytkownika od niepowodzenia modelu i zawierają dostępne pomiary. Nie wymaga to przechowywania historii wykonań. |
| REQ-077 | Opuszczenie bieżącego czatu przez „Nowy czat”, wykonane odświeżenie lub zamknięcie strony, także przy zamykaniu aplikacji, uruchamia anulowanie trwającego wykonania tej rozmowy. Aplikacja ma zatrzymać dalszą pracę, a nie kontynuować generowanie wyniku niedostępnego dla użytkownika. Po przyjęciu anulowania nie rozpoczyna kolejnych etapów ani wywołań LLM; aktywną operację zatrzymuje w zakresie swojej kontroli. Spóźniona odpowiedź nie wznawia procesu ani nie trafia do nowego czatu. Samo wyświetlenie ostrzeżenia i rezygnacja z wyjścia nie uruchamiają anulowania. |

Jeżeli przed anulowaniem zapisano użytecznego kandydata wraz z potwierdzającym go raportem, użytkownik może pobrać tę paczkę zgodnie z REQ-047. Nie zmienia to statusu anulowanego wykonania.

Nie zakłada się, że anulowanie zawsze natychmiast przerwie już obsługiwane zewnętrzne żądanie. Dotyczy to także opuszczenia czatu zgodnie z REQ-077. Sposób wykrycia opuszczenia strony i przekazania anulowania, dokładny moment potwierdzenia zatrzymania oraz dostępność częściowych lub niesprawdzonych artefaktów pozostają do doprecyzowania w OD-08 i OD-09. Nie opieramy gwarancji wyłącznie na żądaniu wysyłanym podczas zamykania strony; ograniczenia opisuje sekcja 11.1.

### 8.5. Brak wznawiania i błędy techniczne

| ID | Wymaganie |
| --- | --- |
| REQ-069 | MVP nie wznawia wykonania po anulowaniu, błędzie kończącym proces ani utracie procesu aplikacji. Użytkownik może uruchomić nowe wykonanie od początku na podstawie przygotowanego zlecenia. Nie wymaga to zachowania poprzedniej próby w historii. |
| REQ-070 | Błąd techniczny uniemożliwiający kontynuację, np. błąd połączenia z modelem lub awaria walidatora, kończy wykonanie jako przerwane błędem. MVP nie ponawia automatycznie nieudanej operacji, nie przełącza po takim błędzie wariantu i nie rozpoczyna rundy naprawczej. Użytkownik może ręcznie uruchomić nowe wykonanie od początku. |

Uzgodniono rozróżnienie błędu technicznego od naruszeń wykrytych w danych. REQ-032–REQ-037 o ograniczonych poprawkach pozostają obowiązujące. Otrzymany wynik z niepoprawną składnią, typem, relacją, liczebnością lub naruszeniem reguły biznesowej jest kandydatem z naruszeniami, a nie sam przez się awarią techniczną. Brak historii nie usuwa odczytu statusu bieżącego wykonania.

Zakaz technicznego retry obejmuje także konfigurację wykorzystywanych klientów i bibliotek. Timeout kończy nieudaną operację; nie zakłada się, że zewnętrzny dostawca natychmiast przerwał jej obsługę. Raport uwzględnia dostępne informacje o próbie, a spóźniona odpowiedź nie wznawia zakończonego procesu.

Brak wznawiania dotyczy procesu, nie zakazu wykorzystania danych jako wejścia do kolejnej prośby. Zmiana paczki zlecona przez użytkownika zgodnie z REQ-076 jest odrębna od technicznego ponowienia przerwanej operacji. Nie wymaga generowania niezależnego zestawu od zera. Ma własny limit poprawek zgodnie z REQ-033–REQ-034; techniczne przypisanie prośby do wykonania pozostaje w OD-10.

Ręczna akcja z REQ-079 jest osobną zgodą na ograniczoną serię dalszych napraw po wyczerpaniu limitu, nie technicznym retry po awarii. Wykorzystuje ostatniego nieudanego kandydata i jego błędy, ale nie przywraca starego procesu ani dostępu do porzuconego czatu. Liczniki i powiązanie serii z wykonaniem wymagają OD-10; nie zakładamy przez to przejścia z końcowego stanu wykonania z powrotem do pracy.

## 9. Statusy i prezentacja wyniku

Poniższe nazwy opisują znaczenie stanów, a nie narzucone nazwy pól, enumów lub elementów interfejsu.

| Stan | Znaczenie |
| --- | --- |
| Przygotowywanie / wymaga wyjaśnienia | Nie ma jeszcze zatwierdzonego, wystarczająco jednoznacznego zlecenia. |
| Gotowe do rozpoczęcia | Wymagania są zatwierdzone i nie ma wykrytej blokady rozpoczęcia. |
| W toku | Trwa generowanie, walidacja lub poprawianie danych. |
| Zakończone — wykonane | Wybrany wynik spełnia obowiązkowe warunki REQ-027; zgodność z dodatkowymi regułami biznesowymi opisuje osobny raport. |
| Zakończone — niewykonane | Nie uzyskano wyniku spełniającego warunki wykonania. Raport opisuje przyczynę i pozostałe błędy. |
| Przerwane błędem | Kontynuację uniemożliwił błąd operacyjny, np. niedostępność używanego modelu; nie jest to to samo co wygenerowanie błędnych danych. |
| Anulowane przez użytkownika | Proces został przerwany na żądanie użytkownika. |

Samo istnienie pliku nie jest dowodem wykonania zadania. Po anulowaniu lub błędzie można pobrać wcześniejszego użytecznego kandydata z jego raportem (REQ-047), ale wykonanie pozostaje anulowane lub przerwane błędem. Niesprawdzone albo częściowe artefakty nie mogą być przedstawiane jako gotowa paczka; ich dostępność do diagnostyki pozostaje do ustalenia.

## 10. Wyniki i eksport

### 10.1. Wybór formatu

| ID | Wymaganie |
| --- | --- |
| REQ-043 | Użytkownik wybiera CSV albo polecenia `INSERT`; wybrany format jest częścią zapisu zlecenia i wykonania. |
| REQ-044 | Wynik w postaci `INSERT` jest przeznaczony dla PostgreSQL i obejmuje dane potrzebne do realizacji zatwierdzonego planu. |
| REQ-045 | Wynik CSV zawiera osobny plik dla każdej uzupełnianej tabeli, pobierany wraz z pozostałymi jako jedna paczka. |
| REQ-046 | Paczka CSV zawiera prostą informację o przypisaniu plików do tabel i kolejności importu. |
| REQ-047 | Użytkownik może pobrać dane oraz prosty raport wykonania w postaci możliwej do automatycznego odczytania w przyszłym narzędziu oceniającym. Dotyczy to także wcześniejszego użytecznego kandydata, którego dane i raport potwierdzający wszystkie warunki REQ-027 zapisano przed anulowaniem lub przerwaniem błędem. Pobranie nie zmienia statusu całego wykonania ani nie wznawia generowania, walidacji lub poprawek. Raport wskazuje udostępnioną wersję, jej rzeczywiste wyniki sprawdzeń oraz status i przyczynę przerwania wykonania. |

Kontraktem wyjściowym są dane do importu, a nie tworzenie lub modyfikacja schematu. Sposób przygotowania bazy docelowej z posiadanego DDL nie jest funkcją wymaganą od generatora. Jeżeli wybrana metoda walidacji tworzy pomocnicze środowisko, jest to oddzielne od eksportowanego wyniku.

Szczegóły plików SQL, opakowania paczki i profilu CSV nie zostały jeszcze wybrane. Obejmują m.in. zapis wartości pustych, dat, znaków specjalnych oraz instrukcję odczytu. Nie należy uznawać dowolnego pliku z rozszerzeniem `.csv` za spełnienie kontraktu.

### 10.2. Prosty raport wykonania

Raport powinien umożliwiać powiązanie wyniku z konkretnym wykonaniem i obejmować:

- identyfikację wykonania i projektu;
- wymagania użyte w tym wykonaniu, w tym schemat, polecenie, zakres danych i liczebności;
- rozpoznawalny opis użytego wariantu generowania;
- końcowy status i przyczynę zakończenia;
- wskazanie zwróconego kandydata, jeśli istnieje;
- oczekiwane i rzeczywiste liczebności;
- wyniki sprawdzeń kompletności, importowalności i obowiązujących relacji wraz z informacją, jak je potwierdzono;
- wyniki poszczególnych dodatkowych reguł;
- liczbę wykorzystanych rund poprawek i ich limit;
- czas wykonania oraz dostępne dane o tokenach, wywołaniach i koszcie;
- identyfikację bieżącego wykonania i dokładnie tej wersji danych, której raport dotyczy; bez wymogu dołączania archiwum wiadomości i prób.

Nie oznacza to obowiązku stworzenia rozbudowanego formatu analitycznego, dashboardu ani osadzania każdej dużej odpowiedzi modelu w głównym pliku raportu. Dokładne minimum eksportu i sposób dołączenia szczegółów wymagają ustalenia.

### 10.3. Raportowanie reguł

| ID | Wymaganie |
| --- | --- |
| REQ-048 | Wynik każdej sprawdzalnej reguły jest raportowany oddzielnie, z liczbą naruszeń i przykładami pozwalającymi zrozumieć problem. |
| REQ-049 | Raport w miarę znaczenia danej reguły wskazuje zakres sprawdzenia, np. 7 naruszeń wśród 200 sprawdzonych zakupów. Nie sprowadza wszystkich reguł do pojedynczych pól. |
| REQ-050 | MVP nie wylicza jednej zbiorczej oceny punktowej jakości ani automatycznej oceny realizmu. |
| REQ-051 | Wskazówki jakościowe i niewykonane sprawdzenia są wyraźnie odróżnione od sprawdzeń zakończonych wynikiem pozytywnym. |

Wynik reguły musi odpowiadać jej zatwierdzonemu znaczeniu. Jednostką naruszenia może być rekord, para rekordów, relacja albo cały zbiór; nie wolno przyjmować jednej jednostki dla wszystkich wymagań bez określenia jej znaczenia.

## 11. Bieżący czat i historia poza MVP

**Uzgodnione 14 listopada 2026:** historii wykonań nie przechowujemy w MVP. Poniższe pozycje oznaczone jako poza MVP zachowują dawne identyfikatory wyłącznie dla ciągłości dokumentacji. Można wrócić do nich przy rozwoju, bez obietnicy realizacji.

| ID | Wymaganie |
| --- | --- |
| REQ-052 | **Poza MVP:** trwały rejestr zakończonych, nieudanych i anulowanych wykonań. |
| REQ-053 | **Poza MVP:** archiwizowanie wymagań dawnych wykonań do późniejszego odczytu. Niezmienność wymagań bieżącego wykonania nadal wynika z REQ-026. |
| REQ-054 | **Poza MVP:** archiwum kandydatów, błędów walidacji i przebiegu poprawek. Ochrona najnowszego użytecznego kandydata w bieżącym wykonaniu nadal wynika z REQ-038–REQ-040. |
| REQ-055 | **Poza MVP:** przechowywanie dokładnych wiadomości wysłanych do modeli i otrzymanych od modeli jako archiwum. Treść bieżącej rozmowy oraz wiadomości potrzebne do generowania i poprawek nie są takim archiwum. |
| REQ-056 | **Poza MVP:** przegląd modeli i ich ról w archiwum dawnych wykonań. Opis wariantu w bieżącym raporcie pozostaje wymagany. |
| REQ-057 | Klucze API i inne dane uwierzytelniające nie są częścią udostępnianych danych, raportu ani diagnostyki. |
| REQ-058 | **Poza MVP:** wybór historycznego zlecenia i ponowienie go na podstawie archiwalnego zapisu. |
| REQ-059 | Ręczne ponowienie po anulowaniu, błędzie kończącym proces albo utracie procesu tworzy nowe wykonanie od początku na podstawie przygotowanego zlecenia. Nie wznawia starego procesu ani nie uruchamia automatycznej serii prób. Nie utożsamiamy go z akcją „Podejmij kolejne 3 próby” po wyczerpaniu limitu napraw z REQ-079. |
| REQ-072 | MVP nie przechowuje archiwum wykonań i wiadomości modeli ani nie udostępnia przeglądu dawnych czatów. Obsługuje bieżącą rozmowę, stan wykonania, wynik i prosty raport. Granice dostępności rozmowy i plików określa REQ-074; sposób przechowywania pozostaje decyzją techniczną. |
| REQ-074 | Po wybraniu „Nowy czat” lub wykonaniu odświeżenia strony użytkownik widzi nową rozmowę bez dostępu do poprzedniej konwersacji i związanych z nią plików. Zamknięcie strony również kończy dostęp do czatu; po jej ponownym otwarciu widzimy nową rozmowę. Tak samo działa ponowne otwarcie całkowicie zamkniętej aplikacji. Nie przywracamy starego czatu ani jego plików. Zapisane projekty pozostają dostępne. |
| REQ-075 | Przed odświeżeniem lub zamknięciem strony z bieżącą rozmową lub danymi aplikacja uruchamia ostrzeżenie o ich utracie i umożliwia rezygnację z opuszczenia strony. Anulowanie tej czynności zachowuje czat i jego pliki; samo otwarcie ostrzeżenia nie usuwa danych. Wymaganie podlega ograniczeniom przeglądarki opisanym w sekcji 11.1; nie obiecuje własnego tekstu okna ani wyświetlenia go przy awarii lub wymuszonym zamknięciu procesu. |

Brak archiwum nie wyklucza wieloetapowej rozmowy w aktywnym czacie. Nie usuwa zapisanych projektów, możliwości odczytu statusu, limitu poprawek, walidacji ani pobrania dostępnego wyniku i raportu po przerwaniu zgodnie z REQ-047. Dostęp przez aplikację kończy się jednak po zdarzeniach z REQ-074; możliwość pobrania po anulowaniu lub błędzie nie oznacza możliwości powrotu do porzuconego czatu.

Nie ustalono przez to magazynu ani terminu fizycznego usuwania danych roboczych. Nie chodzi też o usuwanie plików wcześniej pobranych przez użytkownika na dysk. Techniczny mechanizm zakończenia dostępu i sprzątanie pozostają w OD-09. Opuszczenie czatu ma anulować trwające wykonanie zgodnie z REQ-077; nie utożsamiamy jednak utraty dostępu z potwierdzonym zatrzymaniem żądania u dostawcy LLM. Techniczne wykrycie opuszczenia strony i moment potwierdzenia zatrzymania nadal wymagają OD-08 i OD-09.

### 11.1. Ostrzeżenie przed utratą rozmowy

**Uzgodnione:** przed odświeżeniem lub zamknięciem strony chcemy ostrzec użytkownika, że utraci bieżącą rozmowę i związane z nią pliki, oraz pozwolić mu pozostać na stronie. Po rezygnacji z wyjścia niczego nie resetujemy. Dopiero wykonane odświeżenie lub zamknięcie kończy dostęp zgodnie z REQ-074. Zapisane projekty i pliki już pobrane na dysk nie są przedmiotem tej utraty.

**Ograniczenie przeglądarki, sprawdzone 14 listopada 2026:** standardowe okno potwierdzenia przy opuszczaniu strony jest kontrolowane przez przeglądarkę. Ma jej własny tekst i wymaga wcześniejszej interakcji użytkownika ze stroną. Zdarzenie `beforeunload`, które pozwala o nie poprosić, nie jest niezawodne, zwłaszcza przy wymuszonym zamykaniu lub na urządzeniach mobilnych. Nie można obiecać własnego okna z dokładnym zdaniem ani ostrzeżenia przy każdym zakończeniu procesu. Źródło: [MDN — Window: beforeunload event](https://developer.mozilla.org/en-US/docs/Web/API/Window/beforeunload_event).

To ograniczenie techniczne, nie decyzja o przywracaniu historii. Projekt mechanizmu dostępu i sprzątania musi je uwzględnić; samo wysłanie żądania usunięcia podczas zamykania strony nie stanowi jeszcze dowodu jego wykonania. Scenariusz ostrzeżenia trzeba sprawdzić w docelowej przeglądarce po implementacji.

## 12. Wymienność modeli i informacje o bieżącym wykonaniu

Poniższe funkcje należą do generatora, nie do modułu badawczego. Zastosowanie ich w badaniach odbywa się poza aplikacją.

| ID | Wymaganie |
| --- | --- |
| REQ-060 | Podczas badań można stosować modele lokalne i płatne modele udostępniane przez zewnętrzne API. |
| REQ-061 | Autor może ręcznie zmieniać modele, prompty i organizację procesu, w tym sprawdzać warianty wieloagentowe. Nie wymaga to edytora workflow ani panelu eksperymentów w aplikacji. |
| REQ-062 | Wykonanie zapisuje rzeczywiście zastosowany wariant i dostępne parametry modeli w zakresie potrzebnym do późniejszego rozróżnienia prób. |
| REQ-063 | Porównywane próby realizują ten sam zatwierdzony scenariusz. Zmiany jego wymagań muszą być widoczne, a nie ukryte pod tą samą etykietą zadania. |
| REQ-064 | Czas całego procesu obejmuje również przeprowadzone poprawki. Dostępne informacje o wywołaniach, tokenach i koszcie nie mogą pomijać prób naprawczych. |
| REQ-065 | Brak danych pomiarowych jest oznaczany jako brak dostępności, a nie jako wartość zero. Sam fakt działania modelu lokalnie nie stanowi podstawy do przypisania wyliczonego kosztu. |

### 12.1. Badania pozostają poza generatorem

Autor sam gromadzi materiały i organizuje powtórzenia według [planu badań](plan_badan.md). Generator nie odtwarza dawnych prób z historii, nie planuje eksperymentów i nie przechowuje archiwum badań. Liczba powtórzeń, dobór modeli, ocena realizmu i porównywanie wyników nie są funkcjami MVP.

## 13. Wymagania przekrojowe i granice obietnic

### 13.1. Przejrzystość

- Użytkownik musi odróżnić wynik wykonany, niewykonany, przerwany błędem i anulowany.
- Wykryte naruszenia nie mogą zostać ukryte przez samo zakończenie procesu generowania.
- Powinno być jasne, czy trwa generowanie, sprawdzanie czy poprawianie. Szczegółowy układ interfejsu nie jest ustalony.
- Status i raport muszą odzwierciedlać rzeczywisty przebieg bieżącego wykonania, a nie wyłącznie ostatnią pozytywną odpowiedź.

### 13.2. Bezpieczeństwo znaczeniowe i poufność

- Treść wygenerowanych danych nie może samodzielnie zmieniać wymagań ani kryteriów oceny.
- Wariant generowania nie może zatwierdzić własnej poprawności wyłącznie przez deklarację tekstową.
- Materiały przekazywane do zewnętrznych API muszą być materiałami, które wolno wysłać poza środowisko użytkownika.
- Zgoda na porównanie modeli przez API nie oznacza zgody na wysyłanie dowolnych poufnych schematów.
- Aplikacja nie może deklarować pełnej prywatności tylko dlatego, że jest uruchamiana lokalnie, jeśli używany wariant komunikuje się z zewnętrznym modelem.

Nie ustalono wymogu automatycznego wykrywania poufnych danych ani rozbudowanego systemu polityk firmowych. Nie są one domyślną funkcją MVP.

### 13.3. Skala i wydajność

- **Uzgodnione 14 listopada 2026 podczas planowania S2:** projekt ma
  obsługiwać schematy obejmujące nawet kilkaset tabel. Jest to docelowa
  skala schematu w MVP, nie potwierdzony wynik testów ani sztywny limit
  liczby tabel. Użytkownik może jednym zleceniem objąć generowanie danych
  do wszystkich tych kilkuset tabel. Nie wymaga to jednego wywołania LLM
  ani równoległego przetwarzania wszystkich tabel; sposób podziału pracy
  pozostaje do uzgodnienia. Nadal obowiązuje uzgodniony zakres obsługiwanych
  konstrukcji PostgreSQL i skala łącznej liczby rekordów z REQ-007.
- Limit 10 MiB dla wejściowego DDL nie został zaakceptowany.
  Limit rozmiaru paczki i liczby plików pozostaje do ustalenia.
- Oczekiwany zakres danych dotyczy sumy rekordów we wszystkich tabelach.
- Czas i dostępne zużycie zasobów są obserwowanymi wynikami, a nie z góry przyjętą przewagą danego modelu.
- Nie ustalono maksymalnego dopuszczalnego czasu generowania ani gwarancji wydajności.
- Możliwość anulowania i skończony limit poprawek nie zastępują jeszcze decyzji dotyczącej timeoutów i błędów komunikacji.

### 13.4. Przygotowanie do hostowania i wielu użytkowników

Uzupełnienie uzgodnione 20 października 2026: lokalny i jednoosobowy sposób uruchomienia jest zakresem MVP, a nie docelowym ograniczeniem całej aplikacji.

| ID | Wymaganie |
| --- | --- |
| REQ-066 | Architektura MVP uwzględnia późniejsze hostowanie, logowanie, izolację danych wielu użytkowników i skalowanie wykonania. Granice odpowiedzialności powinny umożliwiać dodanie tych funkcji bez zastępowania rdzenia przygotowania zleceń, generowania, walidacji i raportowania. Nie oznacza to wdrożenia tych funkcji w MVP ani gwarancji ich dodania bez zmian integracyjnych, migracji i testów. |

Przygotowanie obejmuje zaprojektowanie źródła kontekstu użytkownika, własności i zakresu dostępu do danych, granicy kontroli dostępu, trwałego stanu zadań oraz wymiennych zależności wdrożeniowych. Szczegóły stanowią propozycję w dokumencie [przygotowanie do hostowania](przygotowanie_do_hostowania.md), nie wybór technologii.

REQ-001 i REQ-002 pozostają bez zmian. Konta, logowanie, współdzielenie i publiczne wdrożenie nadal nie są funkcjami wymaganymi od MVP. Gotowość architektury do rozwoju nie jest potwierdzeniem bezpieczeństwa wdrożenia wieloużytkownikowego ani wydajności przy nieustalonym obciążeniu.

### 13.5. Diagnostyka i monitorowanie działania

**Uzgodnione 14 listopada 2026 podczas planowania S1:** każdy serwis
ma udostępniać diagnostykę warunków potrzebnych do jego poprawnego
działania. Sprawdzenia obejmują poprawność uruchomienia, kompletność
i poprawność wymaganych zmiennych środowiskowych oraz sekretów,
połączenia z wykorzystywanymi zewnętrznymi API, a także istnienie
i dostęp do wymaganych zasobów wewnętrznych.

- Wynik rozróżnia trzy stany: zdolny do działania, częściowo zdolny
  do działania oraz niezdolny do działania. Podaje przyczyny problemów
  i wynikające z nich ograniczenia, bez ujawniania wartości sekretów.
- Brak lub błędna wymagana konfiguracja, w tym brak zmiennych i sekretów,
  nie zatrzymuje samej diagnostyki. Serwis uruchamia tryb diagnostyczny
  i blokuje operacje biznesowe wymagające tej konfiguracji. Tak samo
  zgłasza niedostępność wymaganej zależności bez kończenia procesu.
  Wymagalność dotyczy używanego zakresu, nie kluczy niewykorzystywanych
  dostawców.
- Sprawdzenia odbywają się przy uruchamianiu, a następnie co 30 minut.
  Jeden wspólny mechanizm odpytuje serwisy i zbiera wyniki
  w obraz stanu całości. Monitor działa jako osobny proces niezależny
  od trzech backendów i sprawdza również `application-api`, aby wykrywać
  jego zatrzymanie. Nie polega wyłącznie na raporcie zbiorczym tego API.
  Nie oznacza to odporności na awarię całego hosta.
- Wyniki monitorowania są dostępne w osobnym panelu w przeglądarce.
  Panel i odczyt wyników działają również przy niedostępnej głównej
  aplikacji, bez wymagania działania `application-api`. Decyzje techniczne
  dla S1-T9 opisano w [kontraktach API](lld/kontrakty_api.md).
- Panel udostępnia przycisk „Sprawdź teraz”. Uruchamia on nową,
  bezpłatną i niedestrukcyjną diagnostykę bez czekania na kolejną
  kontrolę okresową, a nie tylko odczytuje poprzedni wynik.
  Nie uruchamia płatnych prób LLM.
  Ręczna kontrola nie zmienia harmonogramu automatycznego:
  nie przesuwa następnej kontroli ani nie zeruje odstępu 30 minut.
- Diagnostyka nie uruchamia ponownie generowania ani walidacji.
  Automatyczne health checki wykonują wyłącznie bezpłatne,
  niedestrukcyjne próby. Sprawdzenie wymagające płatnego wywołania
  LLM można wykonać wyłącznie po ręcznym uruchomieniu i zgodzie
  użytkownika na tę próbę. Zgoda na monitorowanie nie jest zgodą
  na automatyczne płatne wywołania.
- Potwierdzenie działania procesu nie oznacza gotowości do operacji
  biznesowych. Diagnostyka nie gwarantuje powodzenia każdego przyszłego
  wykonania ani uruchomienia endpointu przy awarii samego serwera.

**Do wyjaśnienia:** przyszłe próby i uprawnienia wykraczające poza
obecny fundament oraz wykrywanie awarii samego monitora poza jego procesem. Podział odpowiedzialności
serwisów opisuje [rejestr ustaleń architektonicznych](ustalenia_architektoniczne.md).
Wymagania opisują planowane zachowanie, nie wynik wykonanych testów.

### 13.6. Automatyczna aktualizacja struktury bazy aplikacji

**Uzgodnione 14 listopada 2026 podczas planowania S1:** przy starcie
backendu zarządzającego aplikacja automatycznie uruchamia przygotowane
migracje swojej bazy. Migracje to wersjonowane zmiany struktury,
np. dodanie tabeli lub kolumny. Zwykłe uruchomienie nie wymaga osobnej
ręcznej komendy aktualizującej strukturę.
Migracje wykonujemy wyłącznie w fazie uruchamiania tego backendu,
także po restarcie, nigdy podczas jego dalszego działania.

Nie dotyczy to DDL wgrywanego przez użytkownika ani automatycznego
projektowania zmian tabel. Migracje są osobnym etapem uruchomienia,
nie częścią diagnostyki: health checki, kontrole co 30 minut i przycisk
„Sprawdź teraz” nie uruchamiają migracji.

Po błędzie migracji backend pozostaje w trybie diagnostycznym,
udostępnia przyczynę bez wartości sekretów i blokuje funkcje wymagające
bazy, zamiast całkowicie się wyłączać.
Po usunięciu przyczyny błędu kolejna próba migracji następuje dopiero
po restarcie backendu. Nie ma samoczynnego ponawiania w działającym procesie.

**Do wyjaśnienia:** zabezpieczenie przed równoczesnym wykonaniem migracji.
Nie wykonano implementacji ani testów aplikacji.

## 14. Scenariusze i kryteria akceptacji

Poniższe kryteria opisują oczekiwane zachowanie. Nie narzucają narzędzi testowych ani sposobu implementacji testów. Kryterium jawnie oznaczone jako **poza MVP** nie jest warunkiem odbioru tej wersji.

| ID | Scenariusz i oczekiwany rezultat | Powiązane wymagania |
| --- | --- | --- |
| AC-01 | Użytkownik wgrywa obsługiwany DDL PostgreSQL, zapisuje projekt i może później zlecić generowanie bez ponownego wgrywania schematu. | REQ-003, REQ-009, REQ-010 |
| AC-02 | DDL jawnie definiuje klucz obcy. Relacja jest wykorzystywana jako część schematu bez zastępowania jej zgadywaniem na podstawie nazw. | REQ-011 |
| AC-03 | Aplikacja podejrzewa niezadeklarowane powiązanie `buyer_id`. Do czasu zatwierdzenia nie przedstawia go jako obowiązującej relacji. | REQ-012 |
| AC-04 | Zlecenie wymaga nieobsługiwanej obowiązkowej zależności kołowej. Użytkownik otrzymuje informację przed generowaniem, a aplikacja nie zużywa limitu na udawane próby obsługi. | REQ-013 |
| AC-05 | Użytkownik wgrywa nową wersję DDL. Nowe zlecenie może z niej korzystać, ale wymagania rozpoczętego wcześniej, nadal obsługiwanego wykonania nie zmieniają się. Nie wymaga to archiwum zakończonych prób. | REQ-014, REQ-026 |
| AC-06 | Reguła biznesowa jest niejednoznaczna. Użytkownik widzi potrzebę wyjaśnienia i zatwierdza znaczenie sprawdzenia przed generowaniem. Dla reguły, której aplikacja nie potrafi automatycznie sprawdzić, start jest zablokowany i użytkownik otrzymuje informację oraz wybór: kontynuowanie bez tej reguły albo jej poprawienie. Brak wyboru nie uruchamia generowania. Kontynuacja bez reguły nie przedstawia jej jako spełnionej ani nie zamienia jej automatycznie we wskazówkę jakościową. Wybranie poprawy zachowuje blokadę do uzyskania obsługiwanej i zatwierdzonej interpretacji. Po pominięciu reguły projektu bieżące zlecenie nie uwzględnia jej w wymaganiach, lecz reguła pozostaje niezmieniona w projekcie i ponownie obowiązuje w następnym nowym zleceniu; jej ponowne pominięcie wymaga nowej świadomej decyzji. | REQ-016, REQ-017 |
| AC-07 | Wskazówka „dane mają być realistyczne” jest przekazana do generowania, lecz raport nie przedstawia jej jako automatycznie zaliczonego testu. | REQ-018, REQ-051 |
| AC-08 | Wykryto sprzeczność polecenia z DDL. Generowanie nie startuje, dopóki użytkownik jej nie rozstrzygnie. | REQ-019 |
| AC-09 | Polecenie wymienia nieokreślonych klientów VIP. Aplikacja prosi o doprecyzowanie zamiast sama tworzyć definicję VIP. | REQ-020, REQ-022 |
| AC-10 | Użytkownik prosi o 200 zakupów. Przed wykonaniem zatwierdza także liczby klientów, produktów i pozycji, bez konieczności samodzielnego wskazywania wszystkich tabel od początku. | REQ-021, REQ-024, REQ-025 |
| AC-11 | Każdy wygenerowany zakup odwołuje się wyłącznie do właściwych rekordów zawartych w paczce. Wynik nie zakłada wcześniej istniejących danych. | REQ-005, REQ-006, REQ-027 |
| AC-12 | Wynik zawiera 150 zamiast 200 wymaganych zakupów, mimo że jest importowalny. Status nie wskazuje wykonania zadania. | REQ-028 |
| AC-13 | Wynik spełnia wszystkie warunki REQ-027, ale narusza dodatkową regułę biznesową. Uruchamia poprawki w granicach limitu; jeśli naruszenie pozostaje po zakończeniu, status wykonania może pozostać pozytywny z jawnym raportem naruszenia. | REQ-029, REQ-032, REQ-037 |
| AC-14 | Reguła jest również ograniczeniem DDL, a jej naruszenie uniemożliwia import. Wynik nie zostaje uznany za wykonany wyłącznie na podstawie łagodniejszej oceny biznesowej. | REQ-027, REQ-030 |
| AC-15 | Obowiązkowego sprawdzenia nie udało się wykonać. Raport oznacza brak rozstrzygnięcia, a aplikacja nie deklaruje spełnienia tego warunku ani wykonania zadania. Dotyczy to także relacji zatwierdzonej poza DDL po udanym imporcie; taki przypadek nie zmienia wyniku samego importu. | REQ-012, REQ-027, REQ-031 |
| AC-16 | Ustawiono domyślny limit. Po pierwszym kandydacie aplikacja wykonuje najwyżej 3 rundy poprawek dla całego zlecenia i nie odnawia limitu przy następnej tabeli. | REQ-033, REQ-034, REQ-037 |
| AC-17 | Wariant wieloagentowy wykonuje kilka wywołań modeli w jednej rundzie. Raport bieżącego wykonania nie utożsamia liczby rund z liczbą wywołań i uwzględnia dostępne pomiary wszystkich wywołań. | REQ-035, REQ-062, REQ-064 |
| AC-18 | Pierwszy kandydat spełnia wszystkie warunki REQ-027, ale ma dodatkowe naruszenia biznesowe. Wszystkie późniejsze poprawki go uszkadzają. Po zakończeniu dostępny jest wcześniejszy użyteczny wynik ze swoim rzeczywistym raportem. | REQ-038, REQ-039, REQ-040 |
| AC-19 | Użytkownik anuluje wykonanie. Bieżący status i dostępny raport odróżniają anulowanie od niepowodzenia modelu, bez wymogu wpisu w historii. | REQ-041, REQ-042, REQ-072 |
| AC-20 | Użytkownik wybiera `INSERT`. Wynikiem są dane w postaci przeznaczonej dla PostgreSQL; aplikacja nie wymaga jednoczesnego wygenerowania CSV. | REQ-008, REQ-043, REQ-044 |
| AC-21 | Użytkownik wybiera CSV dla wielu tabel. Otrzymuje jedną paczkę, osobny plik na tabelę i informację o przypisaniu oraz kolejności importu. | REQ-045, REQ-046 |
| AC-22 | Regułę narusza 7 z 200 zakupów. Raport pokazuje wynik tej reguły, zakres, liczbę i przykłady naruszeń, bez wyliczania ogólnej punktacji realizmu. | REQ-048, REQ-049, REQ-050 |
| AC-23 | Klucze API i inne dane uwierzytelniające nie występują w udostępnionych danych, raporcie ani diagnostyce. Nie wymaga to przechowywania pełnych wiadomości modeli. | REQ-057 |
| AC-24 | **Poza MVP:** ponowienie historycznego zlecenia na podstawie archiwum wymagań i użycie aktualnego wariantu. Nie jest warunkiem odbioru MVP. | REQ-053, REQ-058 |
| AC-25 | Dane wraz z prostym raportem można pobrać i jednoznacznie powiązać z bieżącym wykonaniem bez odwoływania się do historii aplikacji. | REQ-047, REQ-072 |
| AC-26 | Dostawca nie udostępnia liczby tokenów albo nie ustalono kosztu lokalnego. Raport oznacza brak danych, zamiast wpisywać zero. | REQ-064, REQ-065 |
| AC-27 | Autor ręcznie podłącza kolejny lokalny lub zewnętrzny wariant i ponawia zadanie. Nie musi budować workflow ani uruchamiać automatycznej serii eksperymentów w interfejsie. | REQ-060, REQ-061, REQ-063 |
| AC-28 | Przegląd architektury identyfikuje granice kontekstu użytkownika, własności danych, kontroli dostępu, trwałego stanu zadań i zależności wdrożeniowych oraz wskazuje drogę rozwoju bez zastępowania rdzenia generatora. Odbiór MVP nie wymaga działającego logowania, wielu kont ani testów obciążeniowych przyszłego wdrożenia. | REQ-001, REQ-002, REQ-066 |
| AC-29 | Użytkownik korzysta z lokalnie uruchomionej aplikacji przez przeglądarkę. Nie jest wymagane logowanie ani publiczny hosting. | REQ-001, REQ-002, REQ-067 |
| AC-30 | Model przygotowuje wynik w wybranym formacie. Raport odnosi się do wyodrębnionej zawartości konkretnego kandydata, a pakowanie lub pobieranie nie zmienia sprawdzonych danych. Błędy nie są ukrywane przez ciche poprawianie danych przez aplikację. | REQ-040, REQ-043, REQ-068 |
| AC-31 | Po anulowaniu lub przerwaniu błędem użytkownik uruchamia nowe wykonanie od początku na podstawie przygotowanego zlecenia. Aplikacja nie kontynuuje starej próby z checkpointu i nie wymaga jej historycznego zapisu. | REQ-059, REQ-069 |
| AC-32 | Błąd połączenia z modelem lub awaria walidatora kończy wykonanie bez automatycznego retry, zmiany wariantu i uruchamiania rundy naprawczej. Natomiast poprawnie odebrany SQL/CSV z wykrytym naruszeniem danych uruchamia poprawki w granicach limitu. | REQ-032, REQ-033, REQ-069, REQ-070 |
| AC-33 | Po uzgodnieniu szczegółów OD-06 i zatwierdzeniu przez użytkownika konkretnej reguły „wartość zamówienia = suma ilość × cena jego pozycji” aplikacja sprawdza ją na zaimportowanych danych. Najpierw zaokrągla wartość każdej pozycji, następnie sumuje te wartości, bez pytania użytkownika o tę kolejność. Sprawdzenie obejmuje przypadek, w którym zaokrąglenie dopiero sumy dałoby inny wynik. Dla danych zgodnych i naruszających znaczenie reguły zwraca odpowiednie wyniki, zakres, liczbę i przykłady naruszeń. Nie zastępuje obliczenia opinią modelu. | REQ-016, REQ-048, REQ-049, REQ-071 |
| AC-34 | Użytkownik zatwierdza relację `zakupy.klient_id` → `klienci.id`, której nie ma w DDL. Aplikacja osobno sprawdza ją na zaimportowanych danych: poprawne odwołania przechodzą sprawdzenie, a odwołanie do nieistniejącego klienta blokuje uznanie kandydata za użyteczny i uruchamia poprawkę w dostępnym limicie. Jeśli naruszenie pozostaje i nie ma innego użytecznego kandydata, zadanie jest niewykonane mimo udanego importu. Raport odróżnia wynik importu od wyniku relacji; oryginalny DDL nie zostaje zmieniony. | REQ-012, REQ-027, REQ-029, REQ-030, REQ-032 |
| AC-35 | W stanie roboczym bieżącego wykonania zachowano użytecznego kandydata i jego raport, a podczas późniejszej poprawki użytkownik anuluje proces albo występuje błąd techniczny. W obu przypadkach użytkownik może pobrać tę paczkę i raport dotyczący dokładnie tej wersji, z jej pozostałymi dodatkowymi naruszeniami biznesowymi. Status wykonania pozostaje odpowiednio anulowany albo przerwany błędem, a raport podaje przyczynę. Pobranie nie wywołuje modelu, ponownej walidacji ani poprawek. Sam plik bez potwierdzenia obowiązkowych warunków nie uprawnia do przedstawienia go jako użytecznej paczki. Nie ustanawia to archiwum dawnych wykonań ani gwarancji dostępności po restarcie. | REQ-027, REQ-040, REQ-042, REQ-047, REQ-069, REQ-070 |
| AC-36 | W jednym wykonaniu wcześniejszy użyteczny kandydat ma 2 dodatkowe naruszenia biznesowe, a nowszy 7. Aplikacja zwraca wyłącznie nowszego i jego rzeczywisty raport, bez rankingu jakości. Późniejszy kandydat niespełniający REQ-027 nie zastępuje najnowszego użytecznego wyniku. Ten sam wybór obowiązuje przy pobieraniu po anulowaniu lub błędzie z AC-35. Nie wymaga to przechowywania starszych wersji jako historii. | REQ-027, REQ-038, REQ-039, REQ-040, REQ-047, REQ-072 |
| AC-37 | Schemat zawiera tabelę pracowników z relacją do przełożonego w tej samej tabeli i dopuszcza brak przełożonego dla korzenia. Użytkownik zleca prostą hierarchię. Aplikacja nie odrzuca tego schematu wyłącznie z powodu relacji do tej samej tabeli. Zarówno dla wybranego `INSERT`, jak i w osobnym wykonaniu dla CSV, można uzyskać kompletną, rzeczywiście zaimportowaną paczkę z pracownikiem bez przełożonego i co najmniej dwoma kolejnymi poziomami. Każdy wskazany przełożony istnieje w paczce; dane nie zawierają zapętleń ani odwołań do samego siebie. Schemat i sprawdzane pliki pozostają niezmienione przez aplikację. | REQ-005, REQ-006, REQ-008, REQ-011, REQ-027, REQ-030, REQ-068 |
| AC-38 | MVP nie zapisuje archiwum dawnych wykonań i pełnych wiadomości modeli oraz nie oferuje ich przeglądu ani ponowienia z historii. Bieżąca rozmowa może zawierać kolejne polecenia i odpowiedzi. Bieżące wykonanie nadal ma status, walidację, poprawki, wynik i prosty raport; AC-35 i AC-36 obowiązują w granicach bieżącego czatu. Sposób fizycznego sprzątania danych roboczych sprawdza się dopiero po rozstrzygnięciu OD-09. | REQ-026, REQ-038, REQ-039, REQ-047, REQ-059, REQ-072, REQ-073, REQ-074 |
| AC-39 | Użytkownik w głównym widoku czatu wybiera zapisany projekt, wysyła polecenie i otrzymuje odpowiedź oraz dostępny wynik zgodnie z zasadami walidacji. Po odpowiedzi może wysłać następne polecenie i prowadzić rozmowę w tym samym czacie. Nie musi wybierać historycznego wykonania. | REQ-009, REQ-027, REQ-047, REQ-073 |
| AC-40 | Po rozmowie z dostępnymi plikami użytkownik wybiera „Nowy czat”: widzi nową rozmowę bez dostępu do starej i jej plików. To samo sprawdza osobno po wykonanym odświeżeniu strony, zamknięciu i ponownym otwarciu strony oraz po całkowitym zamknięciu i ponownym uruchomieniu aplikacji. W każdym przypadku zapisany projekt pozostaje dostępny do wyboru. Odrzucona próba opuszczenia strony nie uruchamia tego resetu (AC-41). | REQ-009, REQ-072, REQ-074, REQ-075 |
| AC-41 | W docelowej przeglądarce, po interakcji z aplikacją i utworzeniu rozmowy z plikami, użytkownik osobno próbuje odświeżyć i zamknąć stronę. W obu scenariuszach pojawia się standardowe ostrzeżenie przeglądarki o możliwości utraty danych. Rezygnacja z wyjścia zachowuje czat i pliki; potwierdzenie prowadzi do utraty dostępu zgodnie z AC-40. Nie wymagamy własnego tekstu okna ani ostrzeżenia przy wymuszonym zakończeniu procesu; ograniczenia opisuje sekcja 11.1. | REQ-074, REQ-075 |
| AC-42 | Użytkownik otrzymał paczkę 100 klientów, a następnie w tym samym czacie prosi o zmianę adresów na polskie. LLM otrzymuje poprzednią paczkę i nowe polecenie. Zwrócona poprawiona paczka dotyczy tych samych klientów, ze zmienionymi adresami, a nie niezależnego zestawu. Przed przedstawieniem jej jako użytecznego wyniku aplikacja sprawdza nowego kandydata zgodnie z wymaganiami i udostępnia raport tej wersji. Nie przenosi pozytywnej walidacji z poprzedniej paczki. | REQ-019, REQ-026, REQ-027, REQ-030, REQ-040, REQ-068, REQ-073, REQ-076 |
| AC-43 | Podczas trwającego generowania użytkownik osobno wybiera „Nowy czat”, potwierdza i wykonuje odświeżenie oraz potwierdza i wykonuje zamknięcie strony. W każdym przypadku aplikacja inicjuje anulowanie opuszczanego wykonania. Po przyjęciu anulowania nie rozpoczyna kolejnych etapów ani wywołań LLM; spóźniona odpowiedź nie kontynuuje pracy i nie pojawia się w nowym czacie. Osobny scenariusz potwierdza, że otwarcie ostrzeżenia i pozostanie na stronie nie anuluje wykonania ani nie usuwa rozmowy. Nie wymagamy dowodu natychmiastowego zatrzymania obliczeń u dostawcy. Sposób wykrycia wyjścia i moment potwierdzenia zatrzymania wymagają doprojektowania w OD-08 i OD-09. | REQ-041, REQ-069, REQ-074, REQ-075, REQ-077 |
| AC-44 | Przy domyślnym limicie wcześniejsza prośba wykorzystała wszystkie 3 rundy naprawcze. Użytkownik w tym samym czacie prosi o zmianę otrzymanej paczki. Po pierwszej zmienionej paczce, jeżeli walidacja wykrywa naruszenia danych, aplikacja może wykonać dla nowej prośby ponownie maksymalnie 3 automatyczne rundy naprawcze. Pierwsza zmieniona paczka nie jest jedną z tych rund. Kolejne tabele, wywołania modeli i automatyczne poprawki nie odnawiają limitu; po jego wyczerpaniu nie ma niejawnej czwartej rundy. Błąd techniczny nadal kończy proces bez automatycznego ponowienia. | REQ-032, REQ-033, REQ-034, REQ-035, REQ-037, REQ-070, REQ-073, REQ-076 |
| AC-45 | W bieżącym czacie dostępna jest sprawdzona paczka i jej raport. Użytkownik zleca zmianę adresów. Pierwszy zmieniony kandydat i wszystkie 3 rundy naprawcze nie dają paczki spełniającej obowiązkowe warunki dla tej prośby. Aplikacja informuje, że zmiana nie powiodła się mimo 3 rund naprawczych. Poprzednia paczka i jej niezmieniony raport nadal są dostępne do pobrania, jawnie oznaczone jako poprzednia wersja. Nie są przedstawiane jako realizacja nowej prośby. Bez akcji użytkownika nie rozpoczyna się dalsza naprawa. | REQ-027, REQ-037, REQ-040, REQ-074, REQ-076, REQ-078 |
| AC-46 | Po scenariuszu AC-45 użytkownik widzi „Podejmij kolejne 3 próby”. Samo wyświetlenie akcji nie uruchamia modelu. Jej ręczne wybranie zleca dla tej samej prośby najwyżej 3 dodatkowe rundy naprawcze, bez dodatkowego pierwszego kandydata poza limitem. Pierwsza dodatkowa runda otrzymuje ostatniego nieudanego kandydata z już zmienionymi adresami i listę błędów wykrytych w tej wersji, np. uszkodzonych powiązań z zamówieniami. Nie zaczyna od poprzedniej sprawdzonej paczki; ta i jej raport pozostają niezmienione i dostępne. Dla tej prośby można uruchomić tylko jedną dodatkową serię. Jeżeli wszystkie jej rundy nadal nie dają użytecznej poprawionej paczki, aplikacja kończy naprawy, informuje o niepowodzeniu i zachowuje poprzednią sprawdzoną paczkę z jej raportem. Nie pokazuje ponownie przycisku dla tej prośby i nie przyznaje drugiej dodatkowej serii. Poprawiony wynik podlega walidacji i ma własny raport, a wcześniejsze zakończenie, anulowanie i błędy techniczne zachowują dotychczasowe zasady. | REQ-032, REQ-035, REQ-036, REQ-037, REQ-040, REQ-041, REQ-069, REQ-070, REQ-076, REQ-078, REQ-079 |
| AC-47 | Podczas pierwszego generowania pierwszy kandydat i wszystkie 3 rundy naprawcze przy domyślnym limicie nie dają żadnej paczki spełniającej REQ-027. Aplikacja pokazuje niepowodzenie i rzeczywisty wynik weryfikacji. Nie pokazuje przycisku „Podejmij kolejne 3 próby” ani nie uruchamia dodatkowej serii napraw. Nie przedstawia niesprawdzonych lub błędnych danych jako gotowej paczki. | REQ-027, REQ-033, REQ-037, REQ-079 |

## 15. Kierunki rozszerzeń

Poniższa lista nie jest zatwierdzonym harmonogramem ani zobowiązaniem do realizacji:

1. Szersza obsługa PostgreSQL, w tym kolumn `json`/`jsonb` przechowujących obiekty JSON, trudniejszych zależności i większego zakresu typów.
2. Generowanie samodzielnych złożonych dokumentów JSON.
3. Inne formaty schematów i wyników, jeśli będą potrzebne.
4. Uzupełnianie istniejących zbiorów danych.
5. Testy negatywne z odróżnieniem zamierzonych i niezamierzonych naruszeń.
6. Większe wolumeny.
7. Wdrożenie chmurowe lub udostępnienie zespołowi.
8. Osobna prosta aplikacja do oceny realizmu i porównywania wyników.
9. Historia czatów, ich plików i wykonań, archiwum wiadomości i kandydatów oraz ponawianie zleceń z historycznego zapisu — kandydat na dalszy rozwój aplikacji, nie funkcja MVP ani zobowiązanie do wdrożenia.
10. Podmiana pojedynczego pliku w paczce DDL, bez ponownego wysyłania całego zestawu — kierunek wskazany 14 listopada 2026 podczas planowania S2, poza MVP. Szczegóły przechowywania i ponownej analizy wymagają osobnego uzgodnienia.

Żaden z tych punktów nie powinien blokować ukończenia uzgodnionego MVP.

## 16. Otwarte decyzje i rozstrzygnięcia

Zakres MVP jest potwierdzony, ale nie wszystkie szczegóły kontraktów są już ustalone. Ta sekcja zapobiega dopisywaniu ukrytych założeń podczas implementacji. Rozstrzygnięte punkty zachowujemy dla ciągłości odwołań; nie są już otwartymi decyzjami.

| ID | Temat decyzji | Status i ustalenia |
| --- | --- | --- |
| OD-01 | Dokładna macierz obsługiwanych elementów PostgreSQL: typy, postacie kluczy, wyrażenia `CHECK` i `DEFAULT`, ewentualne dodatkowe wymagania importu. | Częściowo rozstrzygnięte 14 listopada 2026: obsługa kolumn `json`/`jsonb` w schematach użytkownika pozostaje poza MVP, jako potencjalny kierunek rozwoju, nie zaplanowana funkcja. Proste hierarchie rekordów w jednej tabeli, bez zapętleń i z dopuszczalnym brakiem rodzica dla korzenia, należą do MVP (REQ-005, AC-37). Pozostały zakres nadal wymaga uzgodnienia; nie obiecano obsługi całego PostgreSQL. |
| OD-02 | Szczegółowy zakres i organizacja próbnego importu: wersja silnika, profil transakcji, provisioning i izolacja zasobów. | Częściowo rozstrzygnięte 21 października 2026: wybrano rzeczywisty próbny import do pustego, odizolowanego PostgreSQL. Kolejność: składnia/format → wstępna zgodność schematu i typów → import oraz kompletność → reguły biznesowe. Nie zatwierdzono jeszcze szczegółów środowiska. |
| OD-03 | Wybór między kilkoma użytecznymi kandydatami o różnej zgodności biznesowej. | Rozstrzygnięte 14 listopada 2026: zwracamy wyłącznie najnowszego kandydata spełniającego wszystkie warunki REQ-027, także po anulowaniu lub błędzie. Liczba i waga dodatkowych naruszeń nie zmieniają wyboru; brak rankingu jakości. Wybór dotyczy bieżącego wykonania, bez archiwum starszych wersji (REQ-039, AC-36). |
| OD-04 | Dokładny profil CSV i postać eksportu poleceń `INSERT`. | Użytkownik wybiera jeden format, a CSV dla wielu tabel jest paczką plików z kolejnością importu. |
| OD-05 | Minimalny format prostego raportu bieżącego wykonania. | Raport ma być maszynowo czytelny, prosty i powiązany z konkretnym wynikiem; nie budujemy modułu analitycznego ani archiwum wiadomości. |
| OD-06 | Szczegółowy zakres i wykonywalna postać reguł, ich prezentacja i zatwierdzanie oraz organizacja reguł projektu i zlecenia. Dla REQ-071 pozostają do ustalenia dozwolony zakres parametru precyzji, NULL w kluczu relacji, jednostka naruszenia oraz format wskazania pól i relacji. | Użytkownik zna kryterium sprawdzenia przed generowaniem; wskazówki jakościowe są odrębne. Częściowo rozstrzygnięte 14 listopada 2026: katalog MVP obejmuje porównanie kolumn, porównanie wartości z progiem/zakresem/zbiorem, regułę warunkową i ograniczoną regułę „wartość zamówienia = suma ilość × cena jego pozycji”. Nie obejmuje dowolnych obliczeń. Dla reguły sumującej obowiązuje kolejność: zaokrąglenie wartości każdej pozycji → suma; aplikacja nie pyta o wybór tej kolejności. Zatwierdzone reguły projektu obowiązują we wszystkich jego nowych zleceniach; reguły pojedynczego zlecenia dotyczą tylko jego i nie zapisują się automatycznie w projekcie. Wykryty konflikt wymaga wyjaśnienia, bez cichego nadpisania reguły projektu. Nieobsługiwana reguła blokuje start do świadomego wyboru kontynuowania bez niej albo jej poprawienia (REQ-017). Świadome pominięcie nieobsługiwanej reguły projektu dotyczy wyłącznie bieżącego zlecenia, bez zmiany lub usunięcia reguły w projekcie. Uzgodniono mechanizm: propozycja rodzaju i parametrów od LLM → kontrola obsługiwalności przez aplikację → zatwierdzenie czytelnego opisu przez użytkownika → sprawdzenie danych gotowym mechanizmem, bez wykonywania kodu modelu. Porównanie kolumn ograniczono do dwóch kolumn tego samego rekordu w jednej tabeli; osobna reguła sumująca między tabelami pozostaje w MVP. Dla porównania kolumn uzgodniono sześć operacji: równe, różne, mniejsze, mniejsze lub równe, większe i większe lub równe. Uzgodniono macierz par typów i dostępnych operacji porównania kolumn w sekcji 5.2; pozostałe pary nie są obsługiwane i nie stosujemy automatycznych konwersji poza wymienionymi grupami. Dla porównania kolumn NULL w którejkolwiek z nich jest naruszeniem, także gdy obie wartości są NULL, bez pomijania rekordu i bez zmiany DDL. Równość i różność tekstu w porównaniu kolumn dotyczą dokładnej treści, z uwzględnieniem wielkości liter i wszystkich spacji, bez automatycznego przekształcania wartości. Porównanie kolumn obejmuje wszystkie rekordy wskazanej tabeli w zaimportowanej paczce; jeden niezgodny rekord to jedno naruszenie tej reguły, także gdy obie wartości są NULL. Porównanie ze stałą, zakresem lub zbiorem ograniczono do pojedynczej kolumny rekordu oraz stałej wartości, stałych granic lub jawnego zbioru stałych, bez obliczeń i odwołań do innych rekordów lub tabel. Wariant „wartość w zakresie” obejmuje obie granice, bez wyboru granic otwartych w MVP. Wariant „wartość w zakresie” obsługuje wyłącznie kolumny smallint, integer, bigint, numeric/decimal, date, timestamp i timestamptz. Zakresy dla text, varchar, boolean i uuid są nieobsługiwane. Dla kolumny liczbowej obie granice zakresu są liczbami ze wspólnej grupy smallint/integer/bigint/numeric/decimal. Dla date, timestamp i timestamptz obie granice mają dokładnie ten sam typ co kolumna. Pozostałe połączenia są nieobsługiwane, bez automatycznych konwersji między tymi grupami, np. tekst–liczba i date–timestamp. Dotyczy to typów w definicji reguły, nie rozpoznawania polecenia przez LLM. W wariancie „wartość w zakresie” NULL w sprawdzanej kolumnie zawsze oznacza naruszenie reguły. Rekordu nie pomijamy i nie zmieniamy oryginalnego DDL. Na przykład brak wieku narusza regułę „wiek w zakresie 18–65”. Zakres sprawdzania i jednostkę naruszenia określa wspólna zasada prostych porównań poniżej. Wariant „wartość w zakresie” wymaga obu granic innych niż NULL. Brak którejkolwiek granicy lub NULL zamiast niej oznacza błędną definicję z czytelnym komunikatem. Nie traktujemy brakującej granicy jako nieskończoności. Warunki jednostronne, np. „wiek co najmniej 18”, można opisać porównaniem z pojedynczą stałą. Dla prostych porównań (kolumna–kolumna, pojedyncza stała, zakres i zbiór) obowiązuje wspólna zasada: sprawdzamy wszystkie rekordy wskazanej tabeli w zaimportowanej paczce; każdy niezgodny rekord oznacza jedno naruszenie danej reguły. Wynik podaje liczbę naruszeń wobec liczby sprawdzonych rekordów, np. 7 wśród 100. Nie ustala to zasad reguł warunkowych i sumujących. Format granic nadal wymaga ustalenia. Dolna granica musi być mniejsza lub równa górnej. Zakres 18–18 jest poprawny i dopuszcza tylko 18. Zakres 65–18 jest błędną definicją: aplikacja wyświetla zrozumiały błąd i nie zamienia granic automatycznie. Dla porównania kolumny z pojedynczą stałą uzgodniono sześć operacji: równe, różne, mniejsze, mniejsze lub równe, większe oraz większe lub równe. To katalog operacji, nie dopuszczenie każdej z nich dla każdego typu. Dla kolumn smallint, integer, bigint, numeric/decimal, date, timestamp i timestamptz dostępne są wszystkie sześć operacji. Dla text, varchar, boolean i uuid dostępne są tylko równe i różne. W porównaniu z pojedynczą stałą wymagamy zgodności typów: liczby porównujemy w grupie smallint/integer/bigint/numeric/decimal, tekst w grupie text/varchar, a date, timestamp, timestamptz, boolean i uuid każde wyłącznie ze stałą swojego typu. Pozostałe pary są nieobsługiwane, bez automatycznych konwersji między grupami, np. liczba–tekst i date–timestamp. Dotyczy to typów w definicji reguły, nie sposobu rozpoznawania polecenia przez LLM. W porównaniu kolumny z pojedynczą stałą inną niż NULL brak wartości (NULL) w kolumnie zawsze oznacza naruszenie, także przy operacji „różne”. Rekordu nie pomijamy ani nie uznajemy za zgodny. Na przykład brak statusu narusza regułę „status różny od anulowany”. Nie zmieniamy oryginalnego DDL. NULL w sprawdzanej kolumnie narusza obie operacje zbioru. Równość i różność tekstu w porównaniu kolumny z pojedynczą stałą dotyczą dokładnej treści, z uwzględnieniem wielkości liter i wszystkich spacji, bez automatycznego przekształcania. „ABC” jest różne od „abc” i od „ABC ” (ze spacją na końcu). Decyzji nie rozszerzono na zakresy ani zbiory. Porównanie z pojedynczą stałą obejmuje wszystkie rekordy wskazanej tabeli w zaimportowanej paczce. Każdy niezgodny rekord, także z NULL, oznacza jedno naruszenie tej reguły. Przykładowo 7 niezgodnych rekordów spośród 100 daje 7 naruszeń wśród 100 sprawdzonych. Wspólna zasada poniżej obejmuje również zakresy i zbiory. W wariancie porównania z pojedynczą stałą NULL nie może występować po stronie stałej. Definicje „równe NULL” i „różne od NULL” są nieobsługiwane w tym wariancie; aplikacja podaje czytelną przyczynę zamiast wykonywać zwykłe porównanie. Ewentualne osobne sprawdzanie obecności lub braku wartości pozostaje do ustalenia. Nie usuwa to uzgodnionego wymagania obsługi reguły warunkowej z wymaganą datą dostawy przy określonym statusie. Format stałych i zapis operatorów pozostają otwarte. Porównanie ze zbiorem obsługuje dwie operacje: „należy do zbioru” oraz „nie należy do zbioru”. Przykładowo status ma należeć do listy {nowy, opłacony, wysłany} albo nie należeć do listy {anulowany, odrzucony}. W obu operacjach porównania ze zbiorem definicja musi zawierać niepustą listę stałych innych niż NULL. Pusta lista lub NULL jako element oznacza błędną definicję z czytelną informacją o przyczynie, zamiast wykonania reguły. Dotyczy to listy w definicji, nie braku wartości w sprawdzanym rekordzie. Obie operacje zbioru korzystają z uzgodnionych zasad porównania z pojedynczą stałą: „należy” wymaga spełnienia porównania „równe” z co najmniej jednym elementem, a „nie należy” spełnienia porównania „różne” ze wszystkimi elementami. Każdy element musi być zgodny typowo z kolumną: liczby w grupie smallint/integer/bigint/numeric/decimal, tekst w grupie text/varchar, a date, timestamp, timestamptz, boolean i uuid każde ze swoim typem. Nie stosujemy konwersji między tymi grupami i nie pomijamy niezgodnych elementów definicji. Tekst porównujemy dokładnie, z uwzględnieniem wielkości liter i wszystkich spacji. NULL w sprawdzanej kolumnie oznacza naruszenie w obu operacjach. Reguła warunkowa w MVP ma postać „jeśli jeden warunek, to jedno wymaganie” i dotyczy tego samego rekordu jednej tabeli. Nie ma gałęzi „w przeciwnym razie” ani zagnieżdżonych reguł. Przykład: jeśli status jest równy „wysłany”, data dostawy musi być podana. Osobna reguła sumująca między tabelami pozostaje w MVP. Warunek i wymaganie korzystają z tego samego katalogu pojedynczych sprawdzeń: porównanie dwóch kolumn, porównanie z pojedynczą stałą, zakres, zbiór, „wartość jest NULL” oraz „wartość nie jest NULL”. Każdy człon jest jednym sprawdzeniem, bez łączenia przez „i”/„lub”; wszystkie odwołania dotyczą tego samego rekordu. „Wartość nie jest NULL” oznacza obecność wartości, nie sprawdzanie niepustości tekstu. Gdy warunek jest spełniony, oceniamy wymaganie: jego spełnienie oznacza zgodność, a niespełnienie naruszenie. Gdy warunek jest niespełniony przy dostępnych danych, wynik to „nie dotyczy”: wymagania nie oceniamy i nie zgłaszamy naruszenia. NULL w wartości potrzebnej do zwykłego porównania w warunku oznacza naruszenie całej reguły, a nie „nie dotyczy”. Jawne sprawdzenia „jest NULL” i „nie jest NULL” normalnie rozstrzygają warunek. Na przykład dla „jeśli status = wysłany, data dostawy nie jest NULL” status nowy daje „nie dotyczy”, status wysłany bez daty naruszenie, a status NULL również naruszenie. Reguła warunkowa obejmuje wszystkie rekordy wskazanej tabeli w zaimportowanej paczce. Raport rozlicza je w trzech rozłącznych grupach: zgodne, naruszenia i „nie dotyczy”. Każdy rekord trafia do jednej grupy i daje najwyżej jedno naruszenie danej reguły, również przy NULL w warunku. Rekordów „nie dotyczy” nie przedstawiamy jako spełniających wymaganie. Przykładowo 100 ocenionych rekordów to 35 zgodnych, 5 naruszeń i 60 „nie dotyczy”. Reguła sumująca obejmuje wszystkie pozycje danego rekordu nadrzędnego w paczce, powiązane jedną jawnie wskazaną obowiązującą relacją. Nie obejmuje dodatkowego filtrowania pozycji ani przechodzenia przez kolejne tabele. Relacja pochodzi z DDL albo jest zatwierdzona poza nim zgodnie z REQ-012; aplikacja nie wybiera jej domyślnie. Przykład: wartość zamówienia równa sumie ilość × cena wszystkich jego pozycji, a nie tylko pozycji wybranego statusu. Liczba miejsc po przecinku, do której zaokrąglamy iloczyn każdej pozycji, jest jawnym parametrem konkretnej reguły sumującej, widocznym w interpretacji do zatwierdzenia. Reguły mogą wskazywać różną precyzję, np. 2 albo 3 miejsca. Nie narzucamy dwóch miejsc wszystkim regułom ani nie wyprowadzamy precyzji po cichu ze schematu. W MVP stosujemy jeden tryb zaokrąglania iloczynu pozycji: do najbliższej wartości o zadanej liczbie miejsc, a przy dokładnej połowie — od zera. Dla 2 miejsc: 1,234 daje 1,23; 1,235 daje 1,24; −1,235 daje −1,24. Tryb jest stałą zasadą aplikacji, widoczną w interpretacji reguły, bez wyboru innego trybu. Dozwolony zakres parametru precyzji pozostaje otwarty. NULL w wartości rekordu nadrzędnego albo w którymkolwiek z dwóch mnożonych pól którejkolwiek powiązanej pozycji oznacza naruszenie reguły sumującej dla rekordu nadrzędnego. Nie zastępujemy NULL zerem i nie pomijamy niekompletnych pozycji. Na przykład zamówienie z pozycją bez ceny narusza regułę, zamiast być sprawdzane wyłącznie na podstawie sumy pozostałych pozycji. Przy braku powiązanych pozycji suma wynosi 0. Rekord nadrzędny bez pozycji spełnia regułę sumującą wyłącznie wtedy, gdy jego wartość wynosi 0; inna wartość daje naruszenie, a NULL pozostaje naruszeniem zgodnie z zasadą brakujących wartości. Brak pozycji sam w sobie nie narusza tej reguły. Nie zmienia to wymagań DDL ani innych reguł, które mogą wymagać istnienia pozycji. Wartość nadrzędną porównujemy dokładnie z sumą już zaokrąglonych pozycji, bez tolerancji różnicy i bez dodatkowego zaokrąglania wartości nadrzędnej lub sumy. Porównujemy wartość liczbową, nie liczbę zer w zapisie. Dla sumy 19,99 wartość nadrzędna 19,990 daje zgodność, a 19,991 naruszenie. Reguła sumująca operuje wyłącznie na typach smallint, integer, bigint i numeric/decimal we wszystkich trzech polach: wartości nadrzędnej oraz obu mnożonych polach pozycji. Obliczenia zachowują dokładność dziesiętną, bez przybliżania przez binarne liczby zmiennoprzecinkowe i bez automatycznej zamiany tekstu na liczby. Nie wybiera to biblioteki ani reprezentacji API. Pozostałe szczegóły reguły sumującej, format definicji i interfejs nadal są otwarte. |
| OD-07 | Konkretne wartości timeoutów i sposób zapisania niepełnych informacji o nieudanej lub niepewnej operacji, w tym dostępnych pomiarów. | Błąd techniczny kończy wykonanie bez automatycznego retry i zmiany wariantu. Naruszenia danych uruchamiają ograniczone poprawki. Ręczne ponowienie tworzy nowe wykonanie; nie ma wznawiania. |
| OD-08 | Dostępność częściowych lub niesprawdzonych artefaktów po anulowaniu i błędzie operacyjnym, techniczne przekazanie anulowania po opuszczeniu czatu i dokładny moment potwierdzenia zatrzymania. | Częściowo rozstrzygnięte 14 listopada 2026: wcześniejszy użyteczny kandydat z zapisanym raportem jest dostępny do pobrania także po anulowaniu lub błędzie (REQ-047, AC-35), dopóki użytkownik pozostaje w tym czacie (REQ-074). Opuszczenie czatu uruchamia anulowanie trwającego wykonania; rezygnacja z wyjścia go nie anuluje (REQ-077, AC-43). Nie ma wznawiania ani gwarancji natychmiastowego zatrzymania żądania u dostawcy. Wybieramy najnowszego użytecznego kandydata zgodnie z rozstrzygniętym OD-03. Sposób wykrycia wyjścia i przekazania anulowania oraz moment potwierdzenia zatrzymania nadal są otwarte. |
| OD-09 | Dostępność bieżącego czatu, wyniku i raportu, sprzątanie danych roboczych oraz zasady usuwania projektów. | Częściowo rozstrzygnięte 14 listopada 2026: nowy czat, wykonane odświeżenie i zamknięcie strony oraz pełne zamknięcie aplikacji kończą dostęp do poprzedniej rozmowy i plików; zapisane projekty pozostają. Przed odświeżeniem lub zamknięciem strony wymagane jest ostrzeżenie w granicach możliwości przeglądarki; rezygnacja zachowuje dane (REQ-074–REQ-075, AC-40–AC-41). Nadal otwarte: techniczny mechanizm zakończenia dostępu, fizyczne sprzątanie i usuwanie projektów. Nie wybrano magazynu ani terminu kasowania. Historia pozostaje kandydatem na rozwój poza MVP. |
| OD-10 | Szczegóły organizacji pracy modeli, kontrakt przekazania plików i obsługa kolejnych poleceń w czacie; konkretne warianty badawcze pozostają osobną pracą. | Częściowo rozstrzygnięte 14 listopada 2026: przy prośbie o zmianę danych LLM dostaje poprzednią paczkę jako kontekst i nowe polecenie, modyfikuje ją i zwraca poprawioną paczkę do walidacji (REQ-076, AC-42). Każda nowa prośba ma własny limit, domyślnie 3 automatyczne rundy naprawcze po pierwszym kandydacie (REQ-033–REQ-034, AC-44). Po nieudanej zmianie użytkownik dostaje komunikat i poprzednią sprawdzoną paczkę z jej raportem; może ręcznie zlecić dodatkowe 3 rundy. Ich wejściem jest ostatni nieudany kandydat z listą wykrytych w nim błędów, nie poprzednia sprawdzona paczka (REQ-078–REQ-079, AC-45–AC-46). Nadal otwarte: techniczne przypisanie prośby i dodatkowej serii do wykonania oraz liczników, kontrakt przekazania paczki i obsługa ograniczeń kontekstu. Po nieudanym pierwszym generowaniu bez użytecznej paczki akcja dodatkowych 3 prób nie jest dostępna (REQ-079, AC-47). Dla danej prośby można uruchomić tylko jedną dodatkową serię; po jej niepowodzeniu kończymy naprawy i nie pokazujemy ponownie przycisku (REQ-079, AC-46). Nadal nie ustalono dostępności tej akcji po anulowaniu ani błędzie technicznym. Nie generujemy niezależnego zestawu od zera ani nie wznawiamy procesu. |
| OD-11 | Lista modeli, sprzęt, parametry, szczegółowe definicje pomiarów i sposób wyboru zwycięzcy. | Badania są ręczne, obejmują modele lokalne i płatne oraz porównują wynik całego procesu na tym samym zadaniu. |
| OD-12 | Konkretny układ ekranów i szczegółowe interakcje użytkownika. | Częściowo rozstrzygnięte 14 listopada 2026: głównym widokiem jest czat z wyborem projektu, poleceniem, odpowiedzią, wynikiem i możliwością kontynuacji rozmowy. Akcja „Nowy czat” rozpoczyna nową rozmowę bez dostępu do poprzedniej (REQ-073–REQ-074). Po nieudanej zmianie pokazujemy poprzednią wersję i akcję „Podejmij kolejne 3 próby” zgodnie z REQ-078–REQ-079. Nadal otwarte są szczegółowy układ, zarządzanie projektami, pozostała prezentacja plików kolejnych odpowiedzi i zmiana projektu w trakcie rozmowy. |

Decyzje dotyczące implementacji nie powinny zastępować decyzji o wymaganiach. Przykładowo wybór biblioteki walidacyjnej nie rozstrzyga sam przez się, jakie elementy schematu aplikacja rzeczywiście potwierdza.

## 17. Powiązanie z ustaleniami wywiadu

Tabela zachowuje pochodzenie ustaleń. Wcześniejsze odpowiedzi dotyczące historii zastępuje rozstrzygnięcie zapisane w wersji 1.6; nie są podstawą do realizacji archiwum w MVP.

| Obszar | Podstawa w rozmowie |
| --- | --- |
| Ocena wyniku całego procesu | Q2: użytkownik wybrał ocenę końcowego procesu, nie osobny benchmark pierwszej odpowiedzi. |
| Ten sam scenariusz | Q3, Q9 i Q10: wspólne wymagania i liczebności, ale ręczne wykonywanie prób. |
| Warunek wykonania a jakość | Q4–Q7 i Q27: kompletność oraz importowalność są warunkiem wykonania; dodatkowe reguły opisują jakość. |
| Pusta baza i dane powiązane | Q8–Q9. |
| Historia i ocena zewnętrzna | Q11–Q12, Q23–Q24 oraz Q30–Q31. |
| Relacyjne MVP, PostgreSQL i wejściowy DDL | Q13–Q15. |
| Interpretacja reguł i projekty | Q16–Q17. |
| Ręczne zmiany wariantu, bez panelu workflow | Q18: użytkownik skorygował propozycję gotowych trybów wybieranych w interfejsie. |
| Modele płatne i lokalne | Q19. |
| Potwierdzanie domyślonych relacji i dopytywanie | Q20–Q21. |
| Brak celowo błędnych danych w MVP | Q22. |
| Jeden użytkownik i ograniczony zakres schematów | Q25–Q26. |
| Limit poprawek i zachowanie użytecznego kandydata | Q28–Q29. |
| Prosty raport, aktualizacja DDL i skala | Q31–Q33. |
| Odłożenie obowiązkowych zależności kołowych | Q34. |
| Anulowanie i pełna historia wiadomości | Q35–Q36. |
| Wybór wyniku i paczka CSV | Q37–Q38: użytkownik doprecyzował wybór CSV albo poleceń `INSERT`. |
| Brak zbiorczej punktacji | Q39. |
| Lokalne uruchomienie | Q40. |
| Reakcja na wykryte sprzeczności | Q41. |
| Potwierdzenie podstawy specyfikacji i zgoda na jej zapisanie | Q42. |
| Przygotowanie do hostowania, wielu użytkowników i logowania bez wdrażania tych funkcji w MVP | Dodatkowe uzgodnienie podczas projektowania architektury, 20 października 2026. |
| Lokalny interfejs webowy, gotowy wynik modelu, kolejność walidacji i brak wznawiania | Odpowiedzi na pięć pytań architektonicznych, 20 października 2026. |
| Rozróżnienie błędów technicznych i naruszeń danych | Potwierdzenie 20 października 2026: błędy techniczne kończą wykonanie, naruszenia danych nadal uruchamiają ograniczone poprawki. |
| Cztery etapy walidacji i rzeczywisty próbny import | Doprecyzowanie użytkownika i polecenie zapisania ustaleń, 21 października 2026. Wstępna kontrola typów poprzedza próbny import; końcowe sprawdzenie dodatkowych reguł działa na załadowanych danych. |
| Ograniczona reguła sumująca dane między tabelami | Potwierdzenie 14 listopada 2026 podczas analizy gotowości do implementacji: MVP ma automatycznie sprawdzać regułę typu „wartość zamówienia = suma ilość × cena jego pozycji”. Użytkownik wybrał stałą kolejność: najpierw zaokrąglenie wartości pozycji, potem suma, bez dodatkowego pytania w aplikacji. Pozostałe szczegóły obliczeń pozostają otwarte. |
| Obowiązkowość zatwierdzonych relacji poza DDL | Potwierdzenie 14 listopada 2026 podczas analizy gotowości: naruszenie zatwierdzonej relacji blokuje wykonanie zadania, nawet jeśli próbny import się udał. |
| Pobieranie sprawdzonej paczki po przerwaniu | Potwierdzenie 14 listopada 2026: wcześniej zapisany użyteczny kandydat z raportem jest dostępny po anulowaniu lub błędzie, bez zmiany statusu całego wykonania i bez wznawiania procesu. |
| Wybór jednej zwracanej paczki | Potwierdzenie 14 listopada 2026 w odpowiedzi „tylko najnowsza” na propozycję wyboru najnowszej paczki spełniającej wszystkie obowiązkowe warunki, bez porównywania jakości dodatkowych reguł. |
| Kolumny JSON/JSONB poza MVP | Polecenie 14 listopada 2026: obsługę tych kolumn w schematach użytkownika zapisujemy jako potencjalny kierunek rozwoju poza MVP, nie jako zobowiązanie do realizacji. |
| Proste hierarchie w jednej tabeli | Potwierdzenie 14 listopada 2026 po wyjaśnieniu przykładu: Anna bez przełożonego, Jan podległy Annie, Ola podległa Janowi. Generowanie takich danych należy do MVP; nie rozszerza to zakresu o zapętlone powiązania. |
| Badania poza aplikacją | Doprecyzowanie 14 listopada 2026: badaniami użytkownik zajmuje się osobno. Późniejsze rozstrzygnięcie z tego samego dnia wyłączyło również historię wykonań z MVP. |
| Brak historii w MVP — zastępuje wcześniejsze ustalenia o jej zachowaniu | Rozstrzygnięcie 14 listopada 2026 po doprecyzowaniu użytkownika: historii nie przechowujemy w MVP, pozostaje potencjalnym kierunkiem rozwoju. Nie usuwamy raportu bieżącego wyniku ani stanu potrzebnego do walidacji i poprawek. |
| Czat jako główny widok i granica dostępności rozmowy | Doprecyzowanie 14 listopada 2026: w głównym oknie czatu użytkownik wybiera projekt, podaje polecenie, otrzymuje wynik i może kontynuować rozmowę. „Nowy czat” lub całkowite zamknięcie i ponowne otwarcie aplikacji oznaczają nowy czat, bez starej rozmowy i jej plików. |
| Odświeżenie i zamknięcie strony z ostrzeżeniem | Doprecyzowanie 14 listopada 2026: odświeżenie również usuwa dostęp do bieżącej rozmowy i plików. Przed odświeżeniem lub zamknięciem strony ma pojawić się ostrzeżenie o utracie danych. Historia pozostaje kandydatem na dalszy rozwój poza MVP; ograniczenia techniczne ostrzeżenia opisuje sekcja 11.1. |
| Zmiana danych kolejnym poleceniem | Doprecyzowanie 14 listopada 2026: przekazujemy wygenerowaną paczkę jako kontekst do LLM, a model poprawia w niej to, o co prosi użytkownik, i zwraca poprawioną paczkę. Nie chodzi o niezależne generowanie danych od zera. |
| Anulowanie przy opuszczeniu czatu | Potwierdzenie 14 listopada 2026: „Nowy czat”, wykonane odświeżenie i zamknięcie strony mają także przerywać trwające generowanie. Pozostanie na stronie po ostrzeżeniu nie uruchamia anulowania. |
| Osobny limit napraw dla nowej prośby | Potwierdzenie 14 listopada 2026: każde nowe polecenie zmiany danych dostaje własny limit maksymalnie 3 automatycznych rund naprawczych przy domyślnym ustawieniu, niezależnie od wykorzystania limitu przy poprzedniej prośbie. |
| Nieudana zmiana i dodatkowa seria napraw | Doprecyzowanie 14 listopada 2026: po niepowodzeniu mimo 3 rund informujemy użytkownika i udostępniamy poprzednią sprawdzoną wersję. Użytkownik może ręcznie wybrać „Podejmij kolejne 3 próby”; nie uruchamiamy dodatkowej serii samoczynnie. |

## 18. Zmiany w wersji 1.4

21 października 2026 doprecyzowano REQ-030 oraz sekcję 7.1 i częściowo rozstrzygnięto OD-02 zgodnie z rozmową. Liczba identyfikatorów pozostaje bez zmian: 70 wymagań, 32 kryteria akceptacji i 12 punktów OD. Nie zatwierdzono macierzy OD-01 ani wykonywalnej reprezentacji reguł i agregacji z OD-06.

## 19. Zmiany w wersji 1.5

Poniższy zapis opisuje kolejność wcześniejszych ustaleń. Fragmenty o zachowaniu historii zastąpiła wersja 1.6.

14 listopada 2026 dodano REQ-071 i AC-33 oraz częściowo rozstrzygnięto OD-06: ograniczony rodzaj reguły sumującej dane między tabelami należy do MVP. Pozwala to sprawdzać zależności biznesowe między powiązanymi tabelami, bez obietnicy obsługi dowolnych obliczeń. Przed implementacją trzeba uzgodnić szczegółowe znaczenie reguły; sposób jej sprawdzenia opisuje AC-33. Samo dodanie tej reguły nie zmienia warunków wykonania zadania ani zasad poprawek.

W dalszym doprecyzowaniu tego samego dnia przyjęto stałą kolejność: najpierw zaokrąglenie wartości każdej pozycji, następnie suma tych wartości. Nie pytamy użytkownika aplikacji o wybór kolejności; AC-33 obejmuje jej weryfikację. Nie ustalono przez to jednej precyzji ani trybu zaokrąglania dla wszystkich schematów.

Następnie doprecyzowano REQ-012 i REQ-027: zatwierdzone relacje nieobecne w DDL są obowiązkowym warunkiem wykonania, a nie dodatkowymi regułami o łagodniejszej ocenie. Sprawdzamy je osobno i nie zmieniamy wyniku udanego importu ani oryginalnego DDL. Zaktualizowano powiązane zasady kwalifikacji kandydatów i dodano AC-34.

Potwierdzono też możliwość pobrania wcześniejszego użytecznego kandydata po anulowaniu lub błędzie, aby nie tracić sprawdzonego wyniku. Doprecyzowano REQ-047, dodano AC-35 i częściowo rozstrzygnięto OD-08. Paczka zachowuje powiązanie ze swoim raportem, a całe wykonanie nadal ma status anulowanego lub przerwanego błędem. Samo to ustalenie nie zatwierdza pobierania częściowych lub niesprawdzonych artefaktów ani polityki wyboru między kilkoma użytecznymi kandydatami.

Następnie rozstrzygnięto OD-03: zwracamy wyłącznie najnowszego użytecznego kandydata, nawet jeśli wcześniejszy ma mniej dodatkowych naruszeń biznesowych. Doprecyzowano REQ-039 i dodano AC-36. Nie zmienia to obowiązkowych warunków kwalifikacji, zachowania historii ani statusu przerwanego wykonania; OD-03 jest zamknięte.

Obsługę kolumn `json`/`jsonb` w schematach użytkownika odłożono poza MVP i zapisano jako potencjalny kierunek rozwoju. Częściowo rozstrzyga to OD-01, bez zatwierdzenia reszty macierzy PostgreSQL i bez zmiany liczby identyfikatorów. Jest to odrębne od generowania samodzielnych dokumentów JSON; nie ogranicza wewnętrznego użycia JSON w aplikacji. Nieobsługiwane kolumny podlegają zasadom diagnostyki z REQ-013, bez cichego pomijania danych lub modyfikowania DDL.

Potwierdzono też obsługę prostych hierarchii rekordów w jednej tabeli, np. pracowników i przełożonych. Doprecyzowano REQ-005, dodano AC-37 i uzupełniono częściowe rozstrzygnięcie OD-01. Nie zatwierdzono przez to dowolnych cykli ani całej macierzy PostgreSQL. Dokument obejmuje 71 wymagań, 37 kryteriów akceptacji i 12 punktów OD.

Doprecyzowano rozdzielenie generatora od badań: aplikacja nie organizuje badań i nie utrzymuje ich archiwum. Nie usunięto historii wykonań, eksportu danych ani raportu. OD-09 nadal jest otwarte; nie przyjęto bezterminowego przechowywania ani automatycznego usuwania.

## 20. Zmiany w wersji 1.6

14 listopada 2026 użytkownik doprecyzował, że **MVP nie przechowuje historii wykonań**. To zastępuje wcześniejsze zapisy o jej zachowaniu, także wcześniejsze doprecyzowanie z tego samego dnia. Historię pozostawiono wyłącznie jako potencjalny kierunek rozwoju, nie zaplanowaną funkcję.

- Dodano REQ-072 i AC-38.
- REQ-052–REQ-056 oraz REQ-058 oznaczono jako poza MVP. AC-24 nie jest kryterium odbioru MVP, a AC-23 dotyczy ochrony sekretów bez archiwizacji wiadomości.
- Zaktualizowano pozostałe opisy, aby dotyczyły bieżącego wykonania. Nadal obowiązują: zapisane projekty, niezmienne wymagania bieżącej próby, poprawki, wybór najnowszego użytecznego kandydata oraz pobranie dostępnej sprawdzonej paczki i raportu po przerwaniu.
- OD-09 częściowo rozstrzygnięto brakiem historii. Czas dostępności i sposób sprzątania bieżących danych nadal wymagają uzgodnienia; nie wybrano magazynu ani momentu usunięcia.

Zachowano 72 identyfikatory REQ, z czego 6 odłożono poza MVP, oraz 38 identyfikatorów AC, z czego AC-24 odłożono poza MVP. Rejestr obejmuje nadal 12 punktów OD. Nie jest to implementacja ani wynik testów aplikacji.

## 21. Zmiany w wersji 1.7

Poniższy zapis jest historyczny. Otwartą w tej wersji kwestię odświeżenia rozstrzyga wersja 1.8.

14 listopada 2026 doprecyzowano, że brak historii oznacza brak archiwum dawnych czatów, nie zakaz rozmowy z kolejnymi poleceniami w aktywnym oknie.

- Dodano REQ-073–REQ-074 i AC-39–AC-40: główny widok czatu z wyborem projektu i kolejnymi poleceniami; po „Nowy czat” lub całkowitym zamknięciu i ponownym otwarciu aplikacji nie wracamy do starej rozmowy ani związanych z nią plików.
- Doprecyzowano REQ-055, REQ-072 i AC-38, zachowując brak archiwum. Zapisane projekty pozostają dostępne.
- Częściowo rozstrzygnięto OD-09 i OD-12. Nadal otwarte są odświeżenie strony, techniczne sprzątanie, wpływ nowego czatu na trwające wykonanie oraz szczegóły obsługi kolejnego polecenia. Nie wybrano sposobu przechowywania ani momentu fizycznego usuwania danych.
- Pobranie sprawdzonej paczki po anulowaniu lub błędzie dotyczy nadal dostępnego czatu; nie daje dostępu do rozmowy porzuconej przez „Nowy czat” albo pełne zamknięcie aplikacji.

Dokument obejmuje 74 identyfikatory REQ, z czego 6 poza MVP, oraz 40 identyfikatorów AC, z czego AC-24 poza MVP. Pozostaje 12 punktów OD. Zmiana dotyczy wymagań, nie implementacji.

## 22. Zmiany w wersji 1.8

14 listopada 2026 uzgodniono, że odświeżenie strony i jej zamknięcie również kończą dostęp do bieżącego czatu i związanych z nim plików. Przed tymi czynnościami wymagamy ostrzeżenia o utracie danych z możliwością pozostania na stronie.

- Rozszerzono REQ-074 i AC-40; dodano REQ-075 i AC-41.
- Rezygnacja z opuszczenia strony nie usuwa rozmowy ani plików. Zapisane projekty i pliki pobrane na dysk pozostają poza zakresem utraty.
- Dopisano ograniczenia ostrzeżenia kontrolowanego przez przeglądarkę, bez obietnicy własnego tekstu ani działania przy każdym wymuszonym zamknięciu.
- Ponownie zaznaczono historię czatów i plików jako kandydata na dalszy rozwój, nie wymaganie MVP. Techniczne sprzątanie i obsługa trwającego wykonania pozostają otwarte.

Dokument obejmuje 75 identyfikatorów REQ, z czego 6 poza MVP, oraz 41 identyfikatorów AC, z czego AC-24 poza MVP. Pozostaje 12 punktów OD. To zapis wymagań i ograniczeń, nie implementacja ani wynik testów przeglądarki.

## 23. Zmiany w wersji 1.9

14 listopada 2026 doprecyzowano działanie prośby o zmianę danych w bieżącym czacie: LLM otrzymuje dotychczasową paczkę i nowe polecenie, modyfikuje wskazane dane i zwraca poprawioną paczkę. Nie generujemy niezależnego zestawu od zera.

- Dodano REQ-076 i AC-42 oraz częściowo rozstrzygnięto OD-10.
- Poprawiona paczka jest nowym kandydatem do walidacji. Nie dziedziczy pozytywnego raportu poprzedniej wersji.
- Oddzielono taką zmianę od technicznego retry i wznawiania procesu. Przypisanie prośby do wykonania, limit automatycznych poprawek i szczegóły przekazania kontekstu nadal pozostają otwarte.

Dokument obejmuje 76 identyfikatorów REQ, z czego 6 poza MVP, oraz 42 identyfikatory AC, z czego AC-24 poza MVP. Pozostaje 12 punktów OD. Zmiana dotyczy dokumentacji, nie implementacji.

## 24. Zmiany w wersji 1.10

14 listopada 2026 potwierdzono, że opuszczenie czatu ma również przerywać trwające generowanie, zamiast kontynuować pracę nad niedostępnym wynikiem.

- Dodano REQ-077 i AC-43 oraz częściowo rozstrzygnięto OD-08.
- Wybranie „Nowy czat”, wykonane odświeżenie lub zamknięcie strony uruchamia anulowanie. Samo otwarcie ostrzeżenia i rezygnacja z wyjścia nie anuluje wykonania.
- Po przyjęciu anulowania nie rozpoczynamy dalszych etapów i wywołań LLM. Spóźniona odpowiedź nie wznawia procesu ani nie trafia do nowej rozmowy.
- Nie obiecujemy natychmiastowego zatrzymania żądania u dostawcy. Techniczne wykrycie opuszczenia strony, przekazanie anulowania i moment potwierdzenia zatrzymania nadal wymagają projektu; nie zamknięto całych OD-08 i OD-09.

Dokument obejmuje 77 identyfikatorów REQ, z czego 6 poza MVP, oraz 43 identyfikatory AC, z czego AC-24 poza MVP. Pozostaje 12 punktów OD. Nie jest to implementacja ani wynik testów aplikacji.

## 25. Zmiany w wersji 1.11

Poniższy zapis jest historyczny. Zachowanie po nieudanej zmianie oraz ręczną dodatkową serię napraw doprecyzowuje wersja 1.12.

14 listopada 2026 uzgodniono osobny limit automatycznych napraw dla każdej nowej prośby użytkownika o zmianę danych.

- Doprecyzowano REQ-033–REQ-034, dodano AC-44 i częściowo rozstrzygnięto OD-10.
- Pierwsza paczka przygotowana dla nowej prośby może być naprawiana domyślnie w maksymalnie 3 rundach, niezależnie od limitu wykorzystanego wcześniej w czacie.
- Limit nie odnawia się przy kolejnej tabeli, wywołaniu modelu ani automatycznej poprawce. Nie zmieniono zasad błędów technicznych ani możliwości zmiany konfiguracji podczas badań.
- Techniczne przypisanie prośby do zlecenia i wykonania oraz zachowanie po nieudanej zmianie nadal są otwarte. Nie wybrano modelu danych ani nowych endpointów.

Dokument obejmuje 77 identyfikatorów REQ, z czego 6 poza MVP, oraz 44 identyfikatory AC, z czego AC-24 poza MVP. Pozostaje 12 punktów OD. Zmiana dotyczy dokumentacji, nie implementacji.

## 26. Zmiany w wersji 1.12

Poniższy zapis jest historyczny. Paczkę wejściową dodatkowej serii rozstrzyga wersja 1.13.

14 listopada 2026 uzgodniono zachowanie po wyczerpaniu napraw nieudanej zmiany danych: użytkownik dostaje jasny komunikat i poprzednią sprawdzoną paczkę, a dodatkowe naprawy zleca świadomie.

- Dodano REQ-078–REQ-079 i AC-45–AC-46. Poprzednia paczka pozostaje dostępna z własnym raportem, bez przedstawiania jej jako realizacji nowej prośby.
- Akcja „Podejmij kolejne 3 próby” zleca przy domyślnym ustawieniu maksymalnie 3 dodatkowe rundy naprawcze, nie pierwszego kandydata i jeszcze 3 rundy. Nie powstaje samoczynna kolejna seria.
- Doprecyzowano REQ-037 i REQ-059, rozdzielając tę akcję od technicznego ponowienia po anulowaniu, awarii lub utracie procesu. Nie zmieniono zakazu automatycznego retry ani zasad końca czatu.
- Częściowo rozstrzygnięto OD-10 i OD-12. Wejściowa paczka dodatkowej serii, powiązanie z wykonaniem i licznikami oraz kontrakt API nadal wymagają projektu. Nie zatwierdzono nowej maszyny stanów ani modelu danych.

Dokument obejmuje 79 identyfikatorów REQ, z czego 6 poza MVP, oraz 46 identyfikatorów AC, z czego AC-24 poza MVP. Pozostaje 12 punktów OD. Zmiana dotyczy dokumentacji, nie implementacji ani wykonanych testów aplikacji.

## 27. Zmiany w wersji 1.13

14 listopada 2026 uzgodniono, że ręcznie zlecona dodatkowa seria napraw zaczyna od ostatniej nieudanej wersji i listy wykrytych w niej błędów, zamiast ponownie modyfikować poprzednią sprawdzoną paczkę.

- Doprecyzowano REQ-079 i AC-46 oraz częściowo rozstrzygnięto OD-10. Zachowujemy dotychczasowe zmiany w kandydacie jako punkt wyjścia do napraw, nie traktując ich jako dowodu poprawności.
- Ostatni nieudany kandydat i wynik jego walidacji są potrzebnym stanem roboczym, nie archiwum. Poprzednia sprawdzona paczka i jej raport pozostają chronione i dostępne w bieżącym czacie.
- Nie zmieniono liczby rund ani zasad walidacji, anulowania i błędów technicznych. Przypisanie dodatkowej serii do wykonania i liczników oraz kontrakt przekazania kontekstu pozostają otwarte.

Liczba identyfikatorów pozostaje bez zmian: 79 REQ, 46 AC i 12 OD. To zapis wymagania, nie implementacja ani wynik testów aplikacji.

## 28. Zmiany w wersji 1.14

14 listopada 2026 uzgodniono, że po nieudanym pierwszym generowaniu, gdy nie uzyskano jeszcze użytecznej paczki, nie udostępniamy akcji „Podejmij kolejne 3 próby”.

- Doprecyzowano REQ-079 i OD-10 oraz dodano AC-47.
- Nadal obowiązuje pierwszy kandydat i domyślnie do 3 automatycznych rund naprawczych. Po ich wyczerpaniu bez użytecznej paczki pokazujemy niepowodzenie; nie dodajemy kolejnej serii.
- Nie zmieniono zachowania po nieudanej modyfikacji istniejącej paczki, zasad błędów technicznych ani anulowania.

Dokument obejmuje 79 identyfikatorów REQ, 47 AC i 12 OD. Poza MVP pozostaje 6 REQ oraz AC-24. Zmiana dotyczy dokumentacji, nie implementacji ani wykonanych testów aplikacji.

## 29. Zmiany w wersji 1.15

14 listopada 2026 użytkownik doprecyzował, że przycisku „Podejmij kolejne 3 próby” można użyć tylko raz dla danej prośby o zmianę danych. Nie chodzi o dowolną liczbę ręcznie uruchamianych serii.

- Doprecyzowano REQ-079 i AC-46 oraz częściowo rozstrzygnięto OD-10: dopuszczamy najwyżej jedną dodatkową serię po podstawowym limicie napraw.
- Jeżeli dodatkowa seria również nie da użytecznej poprawionej paczki, kończymy naprawy tej prośby, pokazujemy niepowodzenie i pozostawiamy poprzednią sprawdzoną paczkę z jej raportem. Nie pokazujemy ponownie przycisku dla tej prośby.
- Nie zmieniono niezależnego limitu dla nowej prośby, braku przycisku po nieudanym pierwszym generowaniu ani zasad walidacji, anulowania i błędów technicznych.

Liczba identyfikatorów pozostaje bez zmian: 79 REQ, 47 AC i 12 OD. To aktualizacja dokumentacji, nie implementacja ani wynik testów aplikacji.

## 30. Zmiany w wersji 1.16

14 listopada 2026, podczas planowania S3, użytkownik zatwierdził rozszerzenie katalogu reguł MVP o trzy rodzaje: porównanie kolumn, porównanie wartości z progiem, zakresem lub zbiorem oraz regułę warunkową. Wraz z ograniczoną regułą sumującą z REQ-071 tworzą cztery uzgodnione rodzaje.

- Uzupełniono sekcję 5.2 i częściowo rozstrzygnięto OD-06.
- Nie zatwierdzono jeszcze szczegółowych operatorów, typów, znaczenia NULL, zakresu sprawdzenia, jednostki naruszenia, reprezentacji ani organizacji reguł projektu i zlecenia.
- Nie zmieniono zasad zatwierdzania interpretacji, rozstrzygania konfliktów ani oddzielenia wskazówek jakościowych od automatycznych sprawdzeń.

Nie dodano identyfikatorów REQ, AC ani OD. To zapis uzgodnionego zakresu, nie implementacja ani wynik testów aplikacji.

## 31. Zmiany w wersji 1.17

14 listopada 2026, podczas planowania S3, użytkownik zatwierdził podział na reguły projektu i reguły pojedynczego zlecenia.

- Zatwierdzone reguły projektu obowiązują we wszystkich jego nowych zleceniach.
- Reguły dodane do pojedynczego zlecenia obowiązują tylko w nim i nie zapisują się automatycznie w projekcie.
- Wykryte konflikty wymagają wyjaśnienia. Reguła zlecenia nie nadpisuje po cichu reguły projektu.

Doprecyzowano REQ-015 i częściowo rozstrzygnięto OD-06. Szczegóły interfejsu, reprezentacji, zatwierdzania i zmiany reguł nadal wymagają uzgodnienia. Nie zmieniamy wstecz wymagań rozpoczętego wykonania (REQ-026). Nie dodano identyfikatorów REQ, AC ani OD. Nie wykonano implementacji ani testów aplikacji.

## 32. Zmiany w wersji 1.18

14 listopada 2026, podczas planowania S3, użytkownik ustalił obsługę reguły, której aplikacja nie potrafi automatycznie sprawdzić.

- Start generowania jest zablokowany. Użytkownik otrzymuje informację o problemie i wybiera kontynuowanie bez tej reguły albo jej poprawienie.
- Bez świadomego wyboru generowanie nie rusza. Przy poprawie nadal wymagane są obsługiwana interpretacja i jej zatwierdzenie.
- Pominięcie reguły nie oznacza jej spełnienia ani automatycznej zamiany we wskazówkę jakościową. Nie omija innych blokad rozpoczęcia generowania.
- Zakres pominięcia zapisanej reguły projektu pozostaje otwarty: nie ustalono, czy wybór dotyczy tylko bieżącego zlecenia, czy zmienia również projekt.

Doprecyzowano REQ-017 i AC-06 oraz częściowo rozstrzygnięto OD-06. Nie dodano identyfikatorów. Nie wykonano implementacji ani testów aplikacji.


## 33. Zmiany w wersji 1.19

14 listopada 2026, podczas planowania S3, użytkownik zatwierdził, że wybór „Kontynuuj bez tej reguły” pomija nieobsługiwaną regułę projektu wyłącznie w bieżącym zleceniu.

- Zapisana reguła projektu nie jest usuwana ani zmieniana.
- W kolejnych nowych zleceniach nadal obowiązuje; ponowne pominięcie wymaga świadomej decyzji użytkownika.
- Jest to jawny wyjątek dla bieżącego zlecenia, nie ciche nadpisanie reguły projektu. Nie uchyla pozostałych blokad generowania ani zasad zatwierdzania wymagań.

Doprecyzowano REQ-017, AC-06 i OD-06. Nie dodano identyfikatorów. Nie wykonano implementacji ani testów aplikacji.

## 34. Zmiany w wersji 1.20

14 listopada 2026, podczas planowania S3, użytkownik zatwierdził mechanizm interpretacji i sprawdzania reguł:

1. LLM proponuje rodzaj reguły z uzgodnionego katalogu i jej parametry.
2. Aplikacja sprawdza, czy obsługuje taką definicję.
3. Użytkownik zatwierdza czytelny opis znaczenia sprawdzenia.
4. Walidator sprawdza dane gotowym mechanizmem tego rodzaju, bez wykonywania kodu napisanego przez model.

Doprecyzowano REQ-016 i częściowo rozstrzygnięto OD-06. Nie zatwierdzono nazw pól, formatu definicji, kontraktów API ani szczegółowych operatorów i obliczeń. Nie dodano identyfikatorów REQ, AC ani OD. Nie wykonano implementacji ani testów aplikacji.

## 35. Zmiany w wersji 1.21

14 listopada 2026, podczas doprecyzowania S3-T1, użytkownik zatwierdził ograniczenie rodzaju „porównanie kolumn” do dwóch kolumn tego samego rekordu w jednej tabeli.

- Porównania kolumn różnych rekordów lub tabel nie należą do tego rodzaju reguły w MVP.
- Uzgodniona reguła sumująca między tabelami pozostaje osobnym rodzajem i nie została wyłączona.
- Operatory, obsługiwane pary typów, znaczenie NULL i szczegółowy kontrakt nadal pozostają otwarte.

Uzupełniono sekcję 5.2 i częściowo rozstrzygnięto OD-06. Nie dodano identyfikatorów REQ, AC ani OD. Nie wykonano implementacji ani testów aplikacji.

## 36. Zmiany w wersji 1.22

14 listopada 2026, podczas doprecyzowania S3-T1, użytkownik zatwierdził sześć operacji porównania dwóch kolumn: równe, różne, mniejsze, mniejsze lub równe, większe i większe lub równe.

To katalog operacji, nie zatwierdzenie ich dla dowolnej pary typów. Pary typów, dopuszczalne dla nich operacje, znaczenie NULL i zapis operatorów w definicji nadal wymagają uzgodnienia. Nie rozszerzono tej decyzji automatycznie na pozostałe rodzaje reguł.

Uzupełniono sekcję 5.2 i częściowo rozstrzygnięto OD-06. Nie dodano identyfikatorów REQ, AC ani OD. Nie wykonano implementacji ani testów aplikacji.

## 37. Zmiany w wersji 1.23

14 listopada 2026, podczas doprecyzowania S3-T1, użytkownik zatwierdził macierz typów i operacji porównania kolumn z sekcji 5.2.

- Dla dowolnej pary obsługiwanych typów liczbowych oraz osobno par `date`–`date`, `timestamp`–`timestamp` i `timestamptz`–`timestamptz` dostępnych jest sześć uzgodnionych operacji.
- Dla par spośród `text` i `varchar`, pary `boolean`–`boolean` i pary `uuid`–`uuid` dostępne są równość i różność.
- Inne pary są nieobsługiwane. Nie stosujemy automatycznego dopasowywania typów poza porównaniami wewnątrz wymienionych grup.
- Znaczenie NULL, szczegóły porównań tekstowych i format definicji nadal pozostają otwarte. Nie rozszerzono tej decyzji automatycznie na pozostałe rodzaje reguł.

Uzupełniono sekcję 5.2 i częściowo rozstrzygnięto OD-06. Nie dodano identyfikatorów REQ, AC ani OD. Nie wykonano implementacji ani testów aplikacji.

## 38. Zmiany w wersji 1.24

14 listopada 2026, podczas doprecyzowania S3-T1, użytkownik zatwierdził znaczenie NULL w regule porównującej dwie kolumny.

- NULL w którejkolwiek z porównywanych kolumn oznacza naruszenie reguły, także gdy obie wartości są NULL.
- Takiego rekordu nie pomijamy i nie uznajemy porównania za spełnione.
- Nie zmieniamy dopuszczalności NULL w oryginalnym DDL. Zasada dotyczy dodatkowej reguły porównania kolumn, nie wszystkich rodzajów reguł.

Uzupełniono sekcję 5.2 i częściowo rozstrzygnięto OD-06. Nie dodano identyfikatorów REQ, AC ani OD. Nie wykonano implementacji ani testów aplikacji.

## 39. Zmiany w wersji 1.25

14 listopada 2026, podczas doprecyzowania S3-T1, użytkownik zatwierdził dokładne porównywanie tekstu w regule porównania kolumn.

- Równość i różność uwzględniają wielkość liter i wszystkie spacje, bez automatycznego przekształcania wartości.
- „ABC” i „abc” są różne. „ABC” i „ABC ” również są różne, ponieważ druga wartość ma spację na końcu.
- Nie rozstrzyga to formatu definicji ani mechanizmu wykonania. Decyzji nie rozszerzono automatycznie na pozostałe rodzaje reguł.

Uzupełniono sekcję 5.2 i częściowo rozstrzygnięto OD-06. Nie dodano identyfikatorów REQ, AC ani OD. Nie wykonano implementacji ani testów aplikacji.

## 40. Zmiany w wersji 1.26

14 listopada 2026, podczas doprecyzowania S3-T1, użytkownik zatwierdził zakres i jednostkę naruszenia dla reguły porównania kolumn.

- Sprawdzamy wszystkie rekordy wskazanej tabeli w zaimportowanej paczce.
- Jeden niezgodny rekord oznacza jedno naruszenie tej reguły. Dotyczy to również rekordu, w którym obie porównywane wartości są NULL; nie liczymy go dwukrotnie.
- Wynik pokazuje liczbę naruszeń wobec liczby sprawdzonych rekordów, np. 7 wśród 100. Zasady nie rozszerzono automatycznie na pozostałe rodzaje reguł.

Uzupełniono sekcję 5.2 i częściowo rozstrzygnięto OD-06. Nie dodano identyfikatorów REQ, AC ani OD. Nie wykonano implementacji ani testów aplikacji.

## 41. Zmiany w wersji 1.27

14 listopada 2026, podczas doprecyzowania S3-T1, użytkownik zatwierdził zakres rodzaju „porównanie wartości z progiem, zakresem lub zbiorem”.

- Porównujemy pojedynczą kolumnę rekordu ze stałą wartością, stałymi granicami zakresu albo jawnym zbiorem stałych wartości.
- Ten rodzaj nie obejmuje obliczeń ani odwołań do innych rekordów lub tabel. Reguła sumująca pozostaje osobnym rodzajem.
- Nie ustalono jeszcze operatorów, granic zakresu, typów stałych, znaczenia NULL ani jednostki naruszenia.

Uzupełniono sekcję 5.2 i częściowo rozstrzygnięto OD-06. Nie dodano identyfikatorów REQ, AC ani OD. Nie wykonano implementacji ani testów aplikacji.

## 42. Zmiany w wersji 1.28

14 listopada 2026, podczas doprecyzowania S3-T1, użytkownik zatwierdził przedział domknięty dla wariantu „wartość w zakresie”.

- Obie granice należą do zakresu, np. dla 18–65 wartości 18 i 65 są dopuszczalne.
- W tym wariancie MVP nie ma wyboru granic otwartych.
- Decyzja nie rozstrzyga poprawności równych lub odwróconych granic, obsługiwanych typów, znaczenia NULL ani pozostałych operacji.

Uzupełniono sekcję 5.2 i częściowo rozstrzygnięto OD-06. Nie dodano identyfikatorów REQ, AC ani OD. Nie wykonano implementacji ani testów aplikacji.

## 43. Zmiany w wersji 1.29

14 listopada 2026, podczas doprecyzowania S3-T1, użytkownik zatwierdził poprawność granic wariantu „wartość w zakresie”.

Dolna granica musi być mniejsza lub równa górnej. Zakres 18–18 jest poprawny i dopuszcza tylko 18. Zakres 65–18 jest błędną definicją: aplikacja wyświetla zrozumiały błąd i nie zamienia granic automatycznie.

Decyzja nie rozstrzyga obsługiwanych typów, znaczenia NULL ani pozostałych operacji. Uzupełniono sekcję 5.2 i częściowo rozstrzygnięto OD-06. Nie dodano identyfikatorów REQ, AC ani OD. Nie wykonano implementacji ani testów aplikacji.

## 44. Zmiany w wersji 1.30

14 listopada 2026, podczas doprecyzowania S3-T1, użytkownik zatwierdził katalog operacji dla porównania kolumny z pojedynczą stałą.

Dla porównania kolumny z pojedynczą stałą uzgodniono sześć operacji: równe, różne, mniejsze, mniejsze lub równe, większe oraz większe lub równe. To katalog operacji, nie dopuszczenie każdej z nich dla każdego typu. Macierz typów, znaczenie NULL i zapis operatorów pozostają otwarte.

Uzupełniono sekcję 5.2 i częściowo rozstrzygnięto OD-06. Nie dodano identyfikatorów REQ, AC ani OD. Nie wykonano implementacji ani testów aplikacji.

## 45. Zmiany w wersji 1.31

14 listopada 2026, podczas doprecyzowania S3-T1, użytkownik zatwierdził macierz operacji według typu kolumny dla porównania z pojedynczą stałą.

- Wszystkie sześć operacji: `smallint`, `integer`, `bigint`, `numeric`/`decimal`, `date`, `timestamp`, `timestamptz`.
- Tylko równe i różne: `text`, `varchar`, `boolean`, `uuid`.
- Decyzja nie rozstrzyga zgodności typu stałej z kolumną, konwersji, porównywania tekstu, znaczenia NULL ani zapisu definicji. Nie rozszerza macierzy na zakresy ani zbiory.

Uzupełniono sekcję 5.2 i częściowo rozstrzygnięto OD-06. Nie dodano identyfikatorów REQ, AC ani OD. Nie wykonano implementacji ani testów aplikacji.

## 46. Zmiany w wersji 1.32

14 listopada 2026, podczas doprecyzowania S3-T1, użytkownik zatwierdził zgodność typów w porównaniu z pojedynczą stałą.

W porównaniu z pojedynczą stałą wymagamy zgodności typów: liczby porównujemy w grupie smallint/integer/bigint/numeric/decimal, tekst w grupie text/varchar, a date, timestamp, timestamptz, boolean i uuid każde wyłącznie ze stałą swojego typu. Pozostałe pary są nieobsługiwane, bez automatycznych konwersji między grupami, np. liczba–tekst i date–timestamp. Dotyczy to typów w definicji reguły, nie sposobu rozpoznawania polecenia przez LLM. Format stałych, znaczenie NULL, szczegóły porównywania tekstu i zapis operatorów pozostają otwarte.

Decyzji nie rozszerzono na zakresy ani zbiory. Uzupełniono sekcję 5.2 i częściowo rozstrzygnięto OD-06. Nie dodano identyfikatorów REQ, AC ani OD. Nie wykonano implementacji ani testów aplikacji.

## 47. Zmiany w wersji 1.33

14 listopada 2026, podczas doprecyzowania S3-T1, użytkownik zatwierdził znaczenie NULL w kolumnie porównywanej z pojedynczą stałą.

W porównaniu kolumny z pojedynczą stałą inną niż NULL brak wartości (NULL) w kolumnie zawsze oznacza naruszenie, także przy operacji „różne”. Rekordu nie pomijamy ani nie uznajemy za zgodny. Na przykład brak statusu narusza regułę „status różny od anulowany”. Nie zmieniamy oryginalnego DDL. Decyzja nie rozstrzyga użycia NULL jako stałej ani zasad dla zakresów i zbiorów.

Uzupełniono sekcję 5.2 i częściowo rozstrzygnięto OD-06. Nie dodano identyfikatorów REQ, AC ani OD. Nie wykonano implementacji ani testów aplikacji.

## 48. Zmiany w wersji 1.34

14 listopada 2026, podczas doprecyzowania S3-T1, użytkownik zatwierdził dokładne porównywanie tekstu z pojedynczą stałą.

Równość i różność tekstu w porównaniu kolumny z pojedynczą stałą dotyczą dokładnej treści, z uwzględnieniem wielkości liter i wszystkich spacji, bez automatycznego przekształcania. „ABC” jest różne od „abc” i od „ABC ” (ze spacją na końcu). Decyzji nie rozszerzono na zakresy ani zbiory.

Nie rozstrzygnięto formatu definicji ani mechanizmu wykonania. Uzupełniono sekcję 5.2 i częściowo rozstrzygnięto OD-06. Nie dodano identyfikatorów REQ, AC ani OD. Nie wykonano implementacji ani testów aplikacji.

## 49. Zmiany w wersji 1.35

14 listopada 2026, podczas doprecyzowania S3-T1, użytkownik zatwierdził zakres sprawdzania i jednostkę naruszenia dla porównania z pojedynczą stałą.

Porównanie z pojedynczą stałą obejmuje wszystkie rekordy wskazanej tabeli w zaimportowanej paczce. Każdy niezgodny rekord, także z NULL, oznacza jedno naruszenie tej reguły. Przykładowo 7 niezgodnych rekordów spośród 100 daje 7 naruszeń wśród 100 sprawdzonych. Decyzja nie ustala zakresu sprawdzania ani jednostki naruszenia dla zakresów i zbiorów.

Uzupełniono sekcję 5.2 i częściowo rozstrzygnięto OD-06. Nie dodano identyfikatorów REQ, AC ani OD. Nie wykonano implementacji ani testów aplikacji.

## 50. Zmiany w wersji 1.36

14 listopada 2026, podczas doprecyzowania S3-T1, użytkownik zatwierdził wykluczenie NULL po stronie stałej w zwykłym porównaniu.

W wariancie porównania z pojedynczą stałą NULL nie może występować po stronie stałej. Definicje „równe NULL” i „różne od NULL” są nieobsługiwane w tym wariancie; aplikacja podaje czytelną przyczynę zamiast wykonywać zwykłe porównanie. Ewentualne osobne sprawdzanie obecności lub braku wartości pozostaje do ustalenia. Nie usuwa to uzgodnionego wymagania obsługi reguły warunkowej z wymaganą datą dostawy przy określonym statusie.

Nie rozstrzygnięto zasad dla zakresów i zbiorów. Uzupełniono sekcję 5.2 i częściowo rozstrzygnięto OD-06. Nie dodano identyfikatorów REQ, AC ani OD. Nie wykonano implementacji ani testów aplikacji.

## 51. Zmiany w wersji 1.37

14 listopada 2026, podczas doprecyzowania S3-T1, użytkownik zatwierdził zestaw typów kolumn dla wariantu „wartość w zakresie”.

Wariant „wartość w zakresie” obsługuje wyłącznie kolumny smallint, integer, bigint, numeric/decimal, date, timestamp i timestamptz. Zakresy dla text, varchar, boolean i uuid są nieobsługiwane. Zgodność i zapis typów granic, znaczenie NULL, zakres sprawdzania i jednostka naruszenia nadal wymagają ustaleń.

Uzupełniono sekcję 5.2 i częściowo rozstrzygnięto OD-06. Nie dodano identyfikatorów REQ, AC ani OD. Nie wykonano implementacji ani testów aplikacji.

## 52. Zmiany w wersji 1.38

14 listopada 2026, podczas doprecyzowania S3-T1, użytkownik zatwierdził zgodność typów granic zakresu z typem kolumny.

Dla kolumny liczbowej obie granice zakresu są liczbami ze wspólnej grupy smallint/integer/bigint/numeric/decimal. Dla date, timestamp i timestamptz obie granice mają dokładnie ten sam typ co kolumna. Pozostałe połączenia są nieobsługiwane, bez automatycznych konwersji między tymi grupami, np. tekst–liczba i date–timestamp. Dotyczy to typów w definicji reguły, nie rozpoznawania polecenia przez LLM.

Format granic, znaczenie NULL, zakres sprawdzania i jednostka naruszenia nadal wymagają ustaleń. Uzupełniono sekcję 5.2 i częściowo rozstrzygnięto OD-06. Nie dodano identyfikatorów REQ, AC ani OD. Nie wykonano implementacji ani testów aplikacji.

## 53. Zmiany w wersji 1.39

14 listopada 2026, podczas doprecyzowania S3-T1, użytkownik zatwierdził znaczenie NULL w kolumnie sprawdzanej regułą zakresu.

W wariancie „wartość w zakresie” NULL w sprawdzanej kolumnie zawsze oznacza naruszenie reguły. Rekordu nie pomijamy i nie zmieniamy oryginalnego DDL. Na przykład brak wieku narusza regułę „wiek w zakresie 18–65”. Decyzja nie rozstrzyga dopuszczalności NULL lub braku granicy w definicji ani zakresu sprawdzania i jednostki naruszenia.

Uzupełniono sekcję 5.2 i częściowo rozstrzygnięto OD-06. Nie dodano identyfikatorów REQ, AC ani OD. Nie wykonano implementacji ani testów aplikacji.

## 54. Zmiany w wersji 1.40

14 listopada 2026, podczas doprecyzowania S3-T1, użytkownik zatwierdził wymaganie obu granic innych niż NULL w definicji zakresu.

Wariant „wartość w zakresie” wymaga obu granic innych niż NULL. Brak którejkolwiek granicy lub NULL zamiast niej oznacza błędną definicję z czytelnym komunikatem. Nie traktujemy brakującej granicy jako nieskończoności. Warunki jednostronne, np. „wiek co najmniej 18”, można opisać porównaniem z pojedynczą stałą.

Uzupełniono sekcję 5.2 i częściowo rozstrzygnięto OD-06. Nie dodano identyfikatorów REQ, AC ani OD. Nie wykonano implementacji ani testów aplikacji.

## 55. Zmiany w wersji 1.41

14 listopada 2026, podczas doprecyzowania S3-T1, użytkownik zatwierdził wspólny zakres sprawdzania i jednostkę naruszenia dla prostych porównań.

Dla prostych porównań (kolumna–kolumna, pojedyncza stała, zakres i zbiór) obowiązuje wspólna zasada: sprawdzamy wszystkie rekordy wskazanej tabeli w zaimportowanej paczce; każdy niezgodny rekord oznacza jedno naruszenie danej reguły. Wynik podaje liczbę naruszeń wobec liczby sprawdzonych rekordów, np. 7 wśród 100. Nie rozstrzyga to znaczenia NULL dla zbioru ani zasad reguł warunkowych i sumujących.

Zasada była już uzgodniona dla porównania kolumn i pojedynczej stałej; teraz obejmuje również zakres i zbiór. Uzupełniono sekcję 5.2 i częściowo rozstrzygnięto OD-06. Nie dodano identyfikatorów REQ, AC ani OD. Nie wykonano implementacji ani testów aplikacji.

## 56. Zmiany w wersji 1.42

14 listopada 2026, podczas doprecyzowania S3-T1, użytkownik zatwierdził obie operacje porównania ze zbiorem.

Porównanie ze zbiorem obsługuje dwie operacje: „należy do zbioru” oraz „nie należy do zbioru”. Przykładowo status ma należeć do listy {nowy, opłacony, wysłany} albo nie należeć do listy {anulowany, odrzucony}. Typy elementów, NULL, pusty zbiór i szczegóły porównywania tekstu nadal wymagają ustaleń.

Nie ustalono zapisu operatorów w definicji ani kontraktu API. Uzupełniono sekcję 5.2 i częściowo rozstrzygnięto OD-06. Nie dodano identyfikatorów REQ, AC ani OD. Nie wykonano implementacji ani testów aplikacji.

## 57. Zmiany w wersji 1.43

14 listopada 2026, podczas doprecyzowania S3-T1, użytkownik zatwierdził warunek poprawności zawartości zbioru.

W obu operacjach porównania ze zbiorem definicja musi zawierać niepustą listę stałych innych niż NULL. Pusta lista lub NULL jako element oznacza błędną definicję z czytelną informacją o przyczynie, zamiast wykonania reguły. Dotyczy to listy w definicji, nie braku wartości w sprawdzanym rekordzie.

Typy elementów, znaczenie NULL w sprawdzanej kolumnie i szczegóły porównywania tekstu nadal wymagają ustaleń. Uzupełniono sekcję 5.2 i częściowo rozstrzygnięto OD-06. Nie dodano identyfikatorów REQ, AC ani OD. Nie wykonano implementacji ani testów aplikacji.

## 58. Zmiany w wersji 1.44

14 listopada 2026, podczas doprecyzowania S3-T1, użytkownik zatwierdził oparcie znaczenia operacji zbioru na porównaniach z pojedynczymi stałymi.

Obie operacje zbioru korzystają z uzgodnionych zasad porównania z pojedynczą stałą: „należy” wymaga spełnienia porównania „równe” z co najmniej jednym elementem, a „nie należy” spełnienia porównania „różne” ze wszystkimi elementami. Każdy element musi być zgodny typowo z kolumną: liczby w grupie smallint/integer/bigint/numeric/decimal, tekst w grupie text/varchar, a date, timestamp, timestamptz, boolean i uuid każde ze swoim typem. Nie stosujemy konwersji między tymi grupami i nie pomijamy niezgodnych elementów definicji. Tekst porównujemy dokładnie, z uwzględnieniem wielkości liter i wszystkich spacji. NULL w sprawdzanej kolumnie oznacza naruszenie w obu operacjach.

Format zapisu nadal pozostaje otwarty. Uzupełniono sekcję 5.2 i częściowo rozstrzygnięto OD-06. Nie dodano identyfikatorów REQ, AC ani OD. Nie wykonano implementacji ani testów aplikacji.

## 59. Zmiany w wersji 1.45

14 listopada 2026, podczas doprecyzowania S3-T1, użytkownik zatwierdził postać i zakres reguły warunkowej.

Reguła warunkowa w MVP ma postać „jeśli jeden warunek, to jedno wymaganie” i dotyczy tego samego rekordu jednej tabeli. Nie ma gałęzi „w przeciwnym razie” ani zagnieżdżonych reguł. Przykład: jeśli status jest równy „wysłany”, data dostawy musi być podana. Osobna reguła sumująca między tabelami pozostaje w MVP.

Katalog warunków i wymagań, znaczenie NULL, wynik dla niespełnionego warunku oraz zakres sprawdzania i jednostka naruszenia reguły warunkowej nadal wymagają ustaleń. Uzupełniono sekcję 5.2 i częściowo rozstrzygnięto OD-06. Nie dodano identyfikatorów REQ, AC ani OD. Nie wykonano implementacji ani testów aplikacji.

## 60. Zmiany w wersji 1.46

14 listopada 2026, podczas doprecyzowania S3-T1, użytkownik zatwierdził wspólny katalog składników warunku i wymagania.

Warunek i wymaganie korzystają z tego samego katalogu pojedynczych sprawdzeń: porównanie dwóch kolumn, porównanie z pojedynczą stałą, zakres, zbiór, „wartość jest NULL” oraz „wartość nie jest NULL”. Każdy człon jest jednym sprawdzeniem, bez łączenia przez „i”/„lub”; wszystkie odwołania dotyczą tego samego rekordu. „Wartość nie jest NULL” oznacza obecność wartości, nie sprawdzanie niepustości tekstu.

Ocena całej reguły warunkowej, w tym NULL w warunku i wynik dla niespełnionego warunku, oraz zakres sprawdzania i jednostka naruszenia nadal wymagają ustaleń. Uzupełniono sekcję 5.2 i częściowo rozstrzygnięto OD-06. Nie dodano identyfikatorów REQ, AC ani OD. Nie wykonano implementacji ani testów aplikacji.

## 61. Zmiany w wersji 1.47

14 listopada 2026, podczas planowania S1, zapisano uzgodniony zakres
diagnostyki serwisów i regularnego monitorowania w sekcji 13.5.
Użytkownik zatwierdził tryb diagnostyczny mimo brakujących zmiennych
lub sekretów, z informacją o przyczynach i blokadą zależnych operacji.
Zastępuje to wcześniejszą architektoniczną zasadę zatrzymywania procesu
przy brakującej lub błędnej wymaganej konfiguracji.

Nie wybrano jeszcze szczegółowych prób ani kontraktu i mechanizmu
monitorowania. Nie dodano identyfikatorów REQ, AC ani OD.
Nie wykonano implementacji ani testów aplikacji.

## 62. Zmiany w wersji 1.48

14 listopada 2026, podczas doprecyzowania S3-T1, użytkownik zatwierdził model oceny reguły warunkowej.

Gdy warunek jest spełniony, oceniamy wymaganie: jego spełnienie oznacza zgodność, a niespełnienie naruszenie. Gdy warunek jest niespełniony przy dostępnych danych, wynik to „nie dotyczy”: wymagania nie oceniamy i nie zgłaszamy naruszenia. NULL w wartości potrzebnej do zwykłego porównania w warunku oznacza naruszenie całej reguły, a nie „nie dotyczy”. Jawne sprawdzenia „jest NULL” i „nie jest NULL” normalnie rozstrzygają warunek. Na przykład dla „jeśli status = wysłany, data dostawy nie jest NULL” status nowy daje „nie dotyczy”, status wysłany bez daty naruszenie, a status NULL również naruszenie.

Zakres sprawdzania, jednostka naruszenia i liczniki raportu reguły warunkowej nadal wymagają ustaleń. Uzupełniono sekcję 5.2 i częściowo rozstrzygnięto OD-06. Nie dodano identyfikatorów REQ, AC ani OD. Nie wykonano implementacji ani testów aplikacji.

## 63. Zmiany w wersji 1.49

14 listopada 2026, podczas planowania S1, użytkownik zatwierdził
niezależny proces wspólnego monitora. Ma sprawdzać również
`application-api`, tak aby wykrywać jego zatrzymanie bez polegania
wyłącznie na agregacji w tym API. Uzupełniono sekcję 13.5.

Nie wybrano narzędzia, technologii, sposobu uruchomienia ani prezentacji
wyników monitora. Nie dodano identyfikatorów REQ, AC ani OD.
Nie wykonano implementacji ani testów aplikacji.

## 64. Zmiany w wersji 1.50

14 listopada 2026, podczas doprecyzowania S3-T1, użytkownik zatwierdził zakres sprawdzania i raportowanie reguły warunkowej.

Reguła warunkowa obejmuje wszystkie rekordy wskazanej tabeli w zaimportowanej paczce. Raport rozlicza je w trzech rozłącznych grupach: zgodne, naruszenia i „nie dotyczy”. Każdy rekord trafia do jednej grupy i daje najwyżej jedno naruszenie danej reguły, również przy NULL w warunku. Rekordów „nie dotyczy” nie przedstawiamy jako spełniających wymaganie. Przykładowo 100 ocenionych rekordów to 35 zgodnych, 5 naruszeń i 60 „nie dotyczy”.

Format pól raportu i kontrakt API nadal pozostają otwarte. Uzupełniono sekcję 5.2 i częściowo rozstrzygnięto OD-06. Nie dodano identyfikatorów REQ, AC ani OD. Nie wykonano implementacji ani testów aplikacji.

## 65. Zmiany w wersji 1.51

14 listopada 2026, podczas planowania S1, użytkownik zatwierdził osobny
panel wyników monitorowania w przeglądarce. Panel i odczyt wyników mają
działać również przy niedostępnej głównej aplikacji, bez wymagania
działania `application-api`. Uzupełniono sekcję 13.5.

Nie wybrano technologii, wyglądu, adresu ani zabezpieczeń panelu.
Nie dodano identyfikatorów REQ, AC ani OD.
Nie wykonano implementacji ani testów aplikacji.

## 66. Zmiany w wersji 1.52

14 listopada 2026, podczas planowania S1, użytkownik zatwierdził
wyłącznie bezpłatne i niedestrukcyjne próby w automatycznych
health checkach. Sprawdzenia wymagające płatnego wywołania LLM
pozostają do ręcznego uruchomienia za zgodą użytkownika na daną próbę.
Uzupełniono sekcję 13.5.

Nie wybrano konkretnych prób ani mechanizmu ręcznego uruchomienia
i potwierdzania kosztu. Nie dodano identyfikatorów REQ, AC ani OD.
Nie wykonano implementacji, testów aplikacji ani płatnych wywołań.

## 67. Zmiany w wersji 1.53

14 listopada 2026, podczas doprecyzowania S3-T1, użytkownik zatwierdził powiązanie i zakres sumowania.

Reguła sumująca obejmuje wszystkie pozycje danego rekordu nadrzędnego w paczce, powiązane jedną jawnie wskazaną obowiązującą relacją. Nie obejmuje dodatkowego filtrowania pozycji ani przechodzenia przez kolejne tabele. Relacja pochodzi z DDL albo jest zatwierdzona poza nim zgodnie z REQ-012; aplikacja nie wybiera jej domyślnie. Przykład: wartość zamówienia równa sumie ilość × cena wszystkich jego pozycji, a nie tylko pozycji wybranego statusu.

Typy pól, precyzja i tryb zaokrąglania, NULL, brak pozycji i jednostka naruszenia nadal wymagają ustaleń. Uzupełniono sekcję 5.2 i częściowo rozstrzygnięto OD-06. Nie dodano identyfikatorów REQ, AC ani OD. Nie wykonano implementacji ani testów aplikacji.

## 68. Zmiany w wersji 1.54

14 listopada 2026, podczas planowania S1, użytkownik ustalił sprawdzanie
przy uruchamianiu, a następnie co 30 minut. Uzupełniono sekcję 13.5.
Jest to harmonogram sprawdzeń, nie gwarancja wykrycia awarii natychmiast
ani w ciągu dokładnie 30 minut; wpływa na to również czas oczekiwania
na odpowiedź, którego limit pozostaje do ustalenia.

Nie dodano identyfikatorów REQ, AC ani OD.
Nie wykonano implementacji ani testów aplikacji.

## 69. Zmiany w wersji 1.55

14 listopada 2026, podczas doprecyzowania S3-T1, użytkownik zatwierdził precyzję zaokrąglania jako jawny parametr reguły sumującej.

Liczba miejsc po przecinku, do której zaokrąglamy iloczyn każdej pozycji, jest jawnym parametrem konkretnej reguły sumującej, widocznym w interpretacji do zatwierdzenia. Reguły mogą wskazywać różną precyzję, np. 2 albo 3 miejsca. Nie narzucamy dwóch miejsc wszystkim regułom ani nie wyprowadzamy precyzji po cichu ze schematu.

Dozwolony zakres parametru precyzji i tryb zaokrąglania pozostają otwarte. Uzupełniono sekcję 5.2 i częściowo rozstrzygnięto OD-06. Nie dodano identyfikatorów REQ, AC ani OD. Nie wykonano implementacji ani testów aplikacji.

## 70. Zmiany w wersji 1.56

14 listopada 2026, podczas planowania S1, użytkownik zatwierdził
przycisk „Sprawdź teraz” w panelu monitora. Uruchamia nową, bezpłatną
i niedestrukcyjną diagnostykę bez czekania na kontrolę okresową.
Nie jest samym odświeżeniem zapisanego wyniku ani zgodą na płatne
próby LLM. Uzupełniono sekcję 13.5.

Na tym etapie wpływ ręcznego sprawdzenia na termin następnej kontroli
okresowej pozostawał otwarty; rozstrzyga go wersja 1.58.
Obsługa jednoczesnych kontroli nadal pozostaje do ustalenia.
Nie dodano identyfikatorów REQ, AC ani OD.
Nie wykonano implementacji ani testów aplikacji.

## 71. Zmiany w wersji 1.57

14 listopada 2026, podczas doprecyzowania S3-T1, użytkownik zatwierdził stały tryb zaokrąglania dla reguły sumującej.

W MVP stosujemy jeden tryb zaokrąglania iloczynu pozycji: do najbliższej wartości o zadanej liczbie miejsc, a przy dokładnej połowie — od zera. Dla 2 miejsc: 1,234 daje 1,23; 1,235 daje 1,24; −1,235 daje −1,24. Tryb jest stałą zasadą aplikacji, widoczną w interpretacji reguły, bez wyboru innego trybu.

Dozwolony zakres parametru precyzji pozostaje otwarty. Uzupełniono sekcję 5.2 i częściowo rozstrzygnięto OD-06. Nie dodano identyfikatorów REQ, AC ani OD. Nie wykonano implementacji ani testów aplikacji.

## 72. Zmiany w wersji 1.58

14 listopada 2026, podczas planowania S1, użytkownik ustalił, że
„Sprawdź teraz” nie wpływa na harmonogram automatycznych kontroli.
Nie przesuwa kolejnej kontroli i nie rozpoczyna od nowa odstępu
30 minut. Uzupełniono sekcję 13.5.

Obsługa jednoczesnych kontroli i technologia harmonogramowania
pozostają otwarte. Nie dodano identyfikatorów REQ, AC ani OD.
Nie wykonano implementacji ani testów aplikacji.

## 73. Zmiany w wersji 1.59

14 listopada 2026, podczas doprecyzowania S3-T1, użytkownik zatwierdził obsługę brakujących wartości w polach obliczenia reguły sumującej.

NULL w wartości rekordu nadrzędnego albo w którymkolwiek z dwóch mnożonych pól którejkolwiek powiązanej pozycji oznacza naruszenie reguły sumującej dla rekordu nadrzędnego. Nie zastępujemy NULL zerem i nie pomijamy niekompletnych pozycji. Na przykład zamówienie z pozycją bez ceny narusza regułę, zamiast być sprawdzane wyłącznie na podstawie sumy pozostałych pozycji.

Decyzja nie rozstrzyga pustej listy pozycji, NULL w kluczu relacji ani jednostki naruszenia. Uzupełniono sekcję 5.2 i częściowo rozstrzygnięto OD-06. Nie dodano identyfikatorów REQ, AC ani OD. Nie wykonano implementacji ani testów aplikacji.

## 74. Zmiany w wersji 1.60

14 listopada 2026, podczas doprecyzowania S3-T1, użytkownik zatwierdził sumę równą zeru przy braku pozycji.

Przy braku powiązanych pozycji suma wynosi 0. Rekord nadrzędny bez pozycji spełnia regułę sumującą wyłącznie wtedy, gdy jego wartość wynosi 0; inna wartość daje naruszenie, a NULL pozostaje naruszeniem zgodnie z zasadą brakujących wartości. Brak pozycji sam w sobie nie narusza tej reguły. Nie zmienia to wymagań DDL ani innych reguł, które mogą wymagać istnienia pozycji.

Uzupełniono sekcję 5.2 i częściowo rozstrzygnięto OD-06. Nie dodano identyfikatorów REQ, AC ani OD. Nie wykonano implementacji ani testów aplikacji.

## 75. Zmiany w wersji 1.61

14 listopada 2026, podczas doprecyzowania S3-T1, użytkownik zatwierdził dokładne porównanie wartości nadrzędnej z sumą zaokrąglonych pozycji.

Wartość nadrzędną porównujemy dokładnie z sumą już zaokrąglonych pozycji, bez tolerancji różnicy i bez dodatkowego zaokrąglania wartości nadrzędnej lub sumy. Porównujemy wartość liczbową, nie liczbę zer w zapisie. Dla sumy 19,99 wartość nadrzędna 19,990 daje zgodność, a 19,991 naruszenie.

Typy pól i techniczna reprezentacja obliczeń nadal wymagają ustaleń. Uzupełniono sekcję 5.2 i częściowo rozstrzygnięto OD-06. Nie dodano identyfikatorów REQ, AC ani OD. Nie wykonano implementacji ani testów aplikacji.

## 76. Zmiany w wersji 1.62

14 listopada 2026, podczas doprecyzowania S3-T1, użytkownik zatwierdził dziedzinę i dokładność obliczeń reguły sumującej.

Reguła sumująca operuje wyłącznie na typach smallint, integer, bigint i numeric/decimal we wszystkich trzech polach: wartości nadrzędnej oraz obu mnożonych polach pozycji. Obliczenia zachowują dokładność dziesiętną, bez przybliżania przez binarne liczby zmiennoprzecinkowe i bez automatycznej zamiany tekstu na liczby. Nie wybiera to biblioteki ani reprezentacji API.

Uzupełniono sekcję 5.2 i częściowo rozstrzygnięto OD-06. Nie dodano identyfikatorów REQ, AC ani OD. Nie wykonano implementacji ani testów aplikacji.

## 77. Zmiany w wersji 1.63

14 listopada 2026, podczas planowania S1, użytkownik wybrał automatyczne
uruchamianie przygotowanych migracji bazy aplikacji przy starcie
backendu zarządzającego. Dodano sekcję 13.6 i oddzielono ten etap
od niedestrukcyjnej diagnostyki oraz monitorowania.

Reakcja na błąd i ochrona przed równoczesnym wykonaniem pozostają
do uzgodnienia. Nie dodano identyfikatorów REQ, AC ani OD.
Nie wykonano implementacji, migracji ani testów aplikacji.

## 78. Zmiany w wersji 1.64

14 listopada 2026, podczas planowania S1, użytkownik zatwierdził
pozostawienie backendu w trybie diagnostycznym po błędzie migracji.
Serwis podaje przyczynę bez wartości sekretów i blokuje funkcje
wymagające bazy, zamiast całkowicie się wyłączać.
Uzupełniono sekcję 13.6.

Sposób ponowienia migracji i ochrona przed równoczesnym wykonaniem
pozostają do uzgodnienia. Nie dodano identyfikatorów REQ, AC ani OD.
Nie wykonano implementacji, migracji ani testów aplikacji.

## 79. Zmiany w wersji 1.65

14 listopada 2026, podczas planowania S1, użytkownik doprecyzował,
że migracje wykonujemy wyłącznie w fazie uruchamiania backendu,
także po restarcie. Po błędzie ponowienie wymaga restartu;
nie ponawiamy migracji podczas działania procesu.
Uzupełniono sekcję 13.6.

Ochrona przed równoczesnym wykonaniem pozostaje do uzgodnienia.
Nie dodano identyfikatorów REQ, AC ani OD.
Nie wykonano implementacji, migracji ani testów aplikacji.
