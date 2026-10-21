# Specyfikacja funkcjonalna MVP — generator relacyjnych danych testowych

**Wersja:** 1.3

**Data:** 20 października 2026

**Podstawa:** wywiad dotyczący wymagań i potwierdzenie zakresu w pytaniu Q42 oraz późniejsze uzgodnienia rozwoju do wielu użytkowników, lokalnego interfejsu webowego, gotowego wyniku modelu, etapów walidacji i braku wznawiania.

**Status:** zatwierdzony zakres MVP; szczegóły wymienione w sekcji 16 wymagają dalszych decyzji.

## 1. Rola dokumentu

Dokument określa, **co ma robić aplikacja**, jakie wyniki ma dostarczać i kiedy można uznać jej zachowanie za prawidłowe. Nie określa sposobu implementacji.

W szczególności nie wybiera języka, frameworka, bibliotek, architektury wdrożeniowej, sposobu przechowywania danych, narzędzi do obsługi modeli ani mechanizmu budowy walidatorów.

Wymagania oznaczone identyfikatorami `REQ-…` należą do uzgodnionego zakresu. Przykłady ilustrują zachowanie, ale nie narzucają nazw tabel, domeny biznesowej ani konkretnych liczebności. Punkty `OD-…` są jawnie nierozstrzygnięte — nie należy traktować ich jako domyślnie zatwierdzonych rozwiązań.

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

**Przedmiotem oceny jest wynik całego procesu**, z uwzględnieniem walidacji, poprawek, czasu i dostępnych informacji o zużyciu zasobów. Pierwsza odpowiedź modelu nie stanowi osobnego głównego kryterium porównania, ale pozostaje w historii.

Aplikacja nie ma automatycznie prowadzić eksperymentów ani wybierać zwycięzcy. Po badaniach do docelowej aplikacji zostaje podłączone rozwiązanie wybrane przez autora.

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
| Wykonane zadanie | Zlecenie, dla którego istnieje wynik kompletny i importowalny. |

## 4. Zakres MVP

### 4.1. W zakresie

| ID | Wymaganie |
| --- | --- |
| REQ-001 | Aplikacja jest przeznaczona dla jednego użytkownika w danej instalacji. |
| REQ-002 | MVP można uruchomić lokalnie; wdrożenie samej aplikacji na AWS nie jest warunkiem ukończenia. |
| REQ-003 | Wejściowym opisem struktury jest plik SQL DDL dla PostgreSQL. |
| REQ-004 | Podstawowy zakres obejmuje tabele, typy kolumn, klucze główne i obce, `NOT NULL`, `UNIQUE`, `CHECK` oraz wartości domyślne w jawnie określonym obsługiwanym zakresie. |
| REQ-005 | Aplikacja obsługuje generowanie danych dla wielu powiązanych tabel, w tym tabel łączących. |
| REQ-006 | Dane są generowane jako samodzielna paczka dla bazy bez istniejących danych; nie zakłada się dostępności klientów, produktów ani innych rekordów poza paczką. |
| REQ-007 | Docelowa skala MVP obejmuje setki do kilku tysięcy rekordów łącznie we wszystkich uzupełnianych tabelach. Jest to zakres oczekiwanego użycia, a nie zatwierdzony sztywny limit liczbowy. |
| REQ-008 | Użytkownik wybiera wynik w postaci poleceń `INSERT` albo CSV. Generowanie obu formatów jednocześnie nie jest wymagane. |
| REQ-067 | MVP jest aplikacją webową uruchamianą lokalnie i obsługiwaną przez przeglądarkę. Nie wybiera to frameworka interfejsu ani backendu. |

### 4.2. Poza zakresem MVP

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

Rozszerzenia można rozpatrywać po uzyskaniu działającego MVP i w zależności od dostępnego czasu. Techniczny raport wykonania nie jest „generowaniem dokumentów JSON” w znaczeniu odłożonej rodziny zadań; jego format pozostaje do ustalenia.

## 5. Projekty i przygotowanie kontekstu

### 5.1. Wgranie i rozpoznanie schematu

| ID | Wymaganie |
| --- | --- |
| REQ-009 | Użytkownik może zapisać projekt i wielokrotnie korzystać z jego schematu oraz reguł bez ponownego przygotowywania całego kontekstu. |
| REQ-010 | Po wgraniu DDL aplikacja rozpoznaje tabele, kolumny i obsługiwane ograniczenia, w tym jawne relacje. |
| REQ-011 | Relacje jawnie zadeklarowane w DDL są obowiązujące i nie wymagają odgadywania na podstawie nazw pól. |
| REQ-012 | Aplikacja może zaproponować relacje brakujące w DDL, ale nie może używać domyślonej relacji jako obowiązującej bez zatwierdzenia przez użytkownika. |
| REQ-013 | Wykryte elementy nieobsługiwane i obowiązkowe zależności kołowe są jawnie zgłaszane. Generowanie zależne od takiego przypadku nie rozpoczyna się jako rzekomo obsługiwane. |
| REQ-014 | Aktualizacja schematu odbywa się przez wgranie nowej wersji całego DDL. Nie zmienia to schematu przypisanego do wcześniejszych wykonań. |

Wgranie schematu nie oznacza zgody na jego automatyczne modyfikowanie. Aplikacja nie może usuwać ograniczeń ani zmieniać struktury wyłącznie po to, aby wygenerowany wynik uzyskał pozytywną ocenę.

### 5.2. Reguły biznesowe i wskazówki jakościowe

| ID | Wymaganie |
| --- | --- |
| REQ-015 | Użytkownik może podawać reguły biznesowe w języku naturalnym w kontekście projektu lub przygotowywanego zlecenia. Dokładny sposób organizacji tych informacji w interfejsie pozostaje do ustalenia. |
| REQ-016 | Przed generowaniem użytkownik zatwierdza interpretację reguły i znaczenie jej sprawdzenia. Aplikacja nie ocenia konfiguracji według nieujawnionej interpretacji wymagania. |
| REQ-017 | Reguła niejednoznaczna lub nieweryfikowalna automatycznie jest jawnie oznaczana; aplikacja nie przypisuje jej fikcyjnego wyniku „spełniona”. |
| REQ-018 | Wskazówki jakościowe pozostają częścią wymagań przekazywanych do generowania, ale ich spełnienie podlega ocenie poza automatycznym raportem zgodności. |
| REQ-019 | Wykryty konflikt między wymaganiami wymaga wyjaśnienia przed rozpoczęciem generowania. Aplikacja nie zmienia ani nie ignoruje po cichu jednej ze stron konfliktu. |

Przykładowy podział:

| Wymaganie | Traktowanie |
| --- | --- |
| Kolumna wymagana w DDL nie może być pusta | Warunek zgodności ze schematem, wpływający na importowalność. |
| Dokładnie 200 rekordów zakupów | Warunek kompletności, wpływający na wykonanie zadania. |
| Data dostawy ma być późniejsza niż data zakupu, bez takiego ograniczenia w DDL | Dodatkowa reguła biznesowa, o ile zatwierdzono sposób jej sprawdzania. |
| Łączna wartość zakupu ma odpowiadać sumie pozycji | Reguła biznesowa wymagająca jednoznacznego ustalenia uwzględnianych pól i obliczeń. |
| Zakupy mają wyglądać realistycznie | Wskazówka jakościowa, oceniana przez użytkownika lub jego zewnętrzne narzędzie. |

**Istotne rozróżnienie:** jeśli reguła biznesowa jest również ograniczeniem zapisanym w DDL i jej naruszenie uniemożliwia import, stanowi także warunek importowalności. Nie można wtedy uznać wyniku za wykonany, powołując się na zasadę łagodniejszego traktowania dodatkowych reguł.

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
| Wykonanie | Czy istnieje kompletny i importowalny wynik? | Rozstrzyga wykonanie zadania. |
| Zgodność biznesowa | Które sprawdzalne dodatkowe reguły są spełnione? | Opisuje jakość i uruchamia poprawki, ale samo naruszenie nie musi oznaczać niewykonania. |
| Realizm i użyteczność | Czy dane są wiarygodne i przydatne do zamierzonego testu? | Ocena użytkownika poza generatorem, ewentualnie ze wsparciem LLM. |

| ID | Wymaganie |
| --- | --- |
| REQ-027 | Zadanie jest wykonane wyłącznie wtedy, gdy wybrany wynik jest kompletny i importowalny. |
| REQ-028 | Brak wymaganej liczby rekordów oznacza niewykonanie zadania, nawet jeśli dostępna część nadaje się do importu. |
| REQ-029 | Naruszenia dodatkowych reguł biznesowych obniżają zgodność jakościową, ale nie odbierają statusu wykonania wynikowi kompletnemu i importowalnemu. |
| REQ-030 | Potwierdzenie importowalności może opierać się na systemie walidacyjnym albo próbie importu. Wybrany mechanizm musi mieć jawny zakres; sama deklaracja modelu nie jest dowodem poprawności. |
| REQ-031 | Niewykonane, nieobsługiwane lub nierozstrzygnięte sprawdzenie nie może zostać przedstawione jako pozytywna weryfikacja. Jeśli dotyczy obowiązkowego warunku wykonania, aplikacja nie może potwierdzić sukcesu. |

Uzgodniono kolejność warstw walidacji: najpierw składnia i format, następnie zgodność typów i schematu, a na końcu dodatkowe reguły biznesowe. Zachowane są również wymagania sprawdzenia ograniczeń, integralności relacji i kompletności; nie zastępujemy ich samym sprawdzeniem typów. Dokładne rozmieszczenie sprawdzeń w warstwie zgodności schematu pozostaje szczegółem projektu.

Jeżeli wcześniejszy etap uniemożliwia dalsze sprawdzenia, są one oznaczane jako niewykonane, a nie pozytywne. Kolejność warstw nie wybiera mechanizmu potwierdzania importowalności.

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
| 200 zakupów, wymagana reszta paczki, importowalność potwierdzona, brak naruszeń dodatkowych reguł | Wykonane; brak wykrytych naruszeń sprawdzalnych reguł. |
| Taka sama kompletna paczka, ale 7 zakupów narusza dodatkową regułę dat dostawy | Wykonane z naruszeniami biznesowymi; naruszenia są raportowane i mogą uruchomić poprawki. |
| 150 zamiast wymaganych 200 zakupów | Niewykonane z powodu niekompletności. |
| 200 zakupów, ale odwołanie do nieistniejącego wymaganego klienta | Niewykonane z powodu braku potwierdzonej importowalności. |
| Prawidłowe pliki, ale obowiązkowego sprawdzenia nie udało się przeprowadzić | Wykonanie niepotwierdzone, a nie sukces. |
| Poprawny i kompletny wynik zawiera mało realistyczne, powtarzalne opisy, których nie ograniczała żadna sprawdzalna reguła | Może być wykonane; realizm pozostaje do oceny zewnętrznej. |

„Brak wykrytych naruszeń” nie oznacza gwarancji realizmu ani sprawdzenia wymagań oznaczonych jako jakościowe.

## 8. Generowanie, poprawki i zakończenie

### 8.1. Główny przebieg

1. Użytkownik wybiera zapisany projekt i wprowadza zlecenie.
2. Aplikacja ustala znaczenie i zakres polecenia.
3. Użytkownik rozstrzyga wykryte niejasności, brakujące relacje i interpretacje reguł.
4. Powstaje zatwierdzony plan danych z liczebnościami i formatem wyniku.
5. Aplikacja rozpoczyna wykonanie, przypisując do niego wymagania i faktycznie używany wariant generowania.
6. Proces przygotowuje pierwszy kandydat wyniku.
7. Aplikacja sprawdza kompletność, importowalność i dodatkowe reguły.
8. Naruszenia uruchamiają poprawki, jeśli pozostał dopuszczalny limit.
9. Nowe kandydaty są sprawdzane, a wcześniejsze wyniki pozostają rozróżnialne w historii.
10. Proces kończy się po uzyskaniu wymaganego wyniku bez dalszych wykrytych naruszeń sprawdzalnych reguł, wyczerpaniu limitu, anulowaniu lub wystąpieniu błędu uniemożliwiającego kontynuację.
11. Użytkownik otrzymuje status, dostępny wynik i prosty raport.

| ID | Wymaganie |
| --- | --- |
| REQ-068 | Model przygotowuje gotowy wynik w wybranym formacie: polecenia `INSERT` albo treść plików CSV. Aplikacja może wyodrębniać, zapisywać, sprawdzać i pakować tę zawartość, ale nie zastępuje jej deterministycznym generowaniem SQL/CSV z pośrednich rekordów ani nie poprawia po cichu danych. Zmieniona wersja danych jest osobnym kandydatem. |

### 8.2. Zasady poprawek

| ID | Wymaganie |
| --- | --- |
| REQ-032 | Błędy kompletności, importowalności oraz sprawdzalnych reguł biznesowych uruchamiają automatyczne poprawki w granicach ustalonego limitu. |
| REQ-033 | Domyślny limit wynosi 3 rundy poprawek po pierwszym wygenerowaniu danych. |
| REQ-034 | Limit dotyczy całego zlecenia, może zostać zmieniony podczas badań i jest zapisany przy wykonaniu. Nie odnawia się automatycznie dla każdej tabeli. |
| REQ-035 | Liczba rund poprawek i liczba wywołań modeli są rejestrowane jako odrębne informacje. Wariant wieloagentowy może wykonywać wiele wywołań w ramach jednego etapu. |
| REQ-036 | Poprawki muszą odnosić się do wykrytych problemów, bez samowolnej zmiany zatwierdzonych wymagań. Sposób i szczegółowość naprawy pozostają częścią badanego wariantu. |
| REQ-037 | Po wyczerpaniu limitu wykonanie kończy się z rzeczywistym wynikiem weryfikacji. Nie powstaje kolejna niejawna seria prób. |

Limit 3 rund oznacza pierwszy kandydat i maksymalnie 3 kolejne rundy naprawcze, a nie łącznie 3 wywołania modelu. Wykryte naruszenie danych jest wynikiem walidacji i uruchamia poprawki w granicach tego limitu. Błąd techniczny nie jest rundą naprawczą: kończy wykonanie bez automatycznego ponowienia.

### 8.3. Zachowanie wcześniejszego wyniku

| ID | Wymaganie |
| --- | --- |
| REQ-038 | Kompletny i importowalny kandydat nie może zostać utracony tylko dlatego, że proces próbuje poprawić jego zgodność biznesową. |
| REQ-039 | Jeśli późniejsze poprawki uszkodzą wynik, po zakończeniu można zwrócić wcześniejszego kompletnego i importowalnego kandydata. Raport wskazuje wybraną wersję i jej pozostałe naruszenia. |
| REQ-040 | Raport i eksportowane dane muszą dotyczyć tego samego kandydata. Nie wolno łączyć danych z jednej próby z pozytywnym raportem innej. |

Nie ustalono jeszcze reguły wyboru między kilkoma kompletnymi i importowalnymi kandydatami mającymi różne naruszenia biznesowe. Nie należy utożsamiać wymagania zachowania użytecznego wyniku z zatwierdzeniem automatycznej zbiorczej punktacji jakości.

### 8.4. Anulowanie

| ID | Wymaganie |
| --- | --- |
| REQ-041 | Użytkownik może zlecić przerwanie trwającego wykonania. |
| REQ-042 | Anulowane wykonanie zachowuje dotychczasową historię oraz dostępne pomiary i jest odróżnione od niepowodzenia modelu. |

Nie zakłada się, że anulowanie zawsze natychmiast przerwie już obsługiwane zewnętrzne żądanie. Szczegóły momentu zatrzymania i dostępności częściowego wyniku pozostają do doprecyzowania.

### 8.5. Brak wznawiania i błędy techniczne

| ID | Wymaganie |
| --- | --- |
| REQ-069 | MVP nie wznawia wykonania po anulowaniu, błędzie kończącym proces ani utracie procesu aplikacji. Użytkownik może uruchomić nowe wykonanie od początku zgodnie z zasadami ręcznego ponawiania. Historia poprzedniej próby pozostaje zachowana. |
| REQ-070 | Błąd techniczny uniemożliwiający kontynuację, np. błąd połączenia z modelem lub awaria walidatora, kończy wykonanie jako przerwane błędem. MVP nie ponawia automatycznie nieudanej operacji, nie przełącza po takim błędzie wariantu i nie rozpoczyna rundy naprawczej. Użytkownik może ręcznie uruchomić nowe wykonanie od początku. |

Uzgodniono rozróżnienie błędu technicznego od naruszeń wykrytych w danych. REQ-032–REQ-037 o ograniczonych poprawkach pozostają obowiązujące. Otrzymany wynik z niepoprawną składnią, typem, relacją, liczebnością lub naruszeniem reguły biznesowej jest kandydatem z naruszeniami, a nie sam przez się awarią techniczną. Brak wznawiania nie oznacza rezygnacji z trwałej historii ani odczytu statusu istniejącego wykonania.

Zakaz technicznego retry obejmuje także konfigurację wykorzystywanych klientów i bibliotek. Timeout kończy nieudaną operację; nie zakłada się, że zewnętrzny dostawca natychmiast przerwał jej obsługę. Historia zachowuje dostępne informacje o próbie, a spóźniona odpowiedź nie wznawia zakończonego procesu.

## 9. Statusy i prezentacja wyniku

Poniższe nazwy opisują znaczenie stanów, a nie narzucone nazwy pól, enumów lub elementów interfejsu.

| Stan | Znaczenie |
| --- | --- |
| Przygotowywanie / wymaga wyjaśnienia | Nie ma jeszcze zatwierdzonego, wystarczająco jednoznacznego zlecenia. |
| Gotowe do rozpoczęcia | Wymagania są zatwierdzone i nie ma wykrytej blokady rozpoczęcia. |
| W toku | Trwa generowanie, walidacja lub poprawianie danych. |
| Zakończone — wykonane | Istnieje wybrany wynik kompletny i importowalny; zgodność biznesową opisuje osobny raport. |
| Zakończone — niewykonane | Nie uzyskano wyniku spełniającego warunki wykonania. Raport opisuje przyczynę i pozostałe błędy. |
| Przerwane błędem | Kontynuację uniemożliwił błąd operacyjny, np. niedostępność używanego modelu; nie jest to to samo co wygenerowanie błędnych danych. |
| Anulowane przez użytkownika | Proces został przerwany na żądanie użytkownika. |

Samo istnienie pliku nie jest dowodem wykonania zadania. Ewentualne artefakty nieudanego procesu nie mogą być przedstawiane jako gotowa paczka do poprawnego importu. Szczegółowa dostępność takich plików do diagnostyki pozostaje do ustalenia.

## 10. Wyniki i eksport

### 10.1. Wybór formatu

| ID | Wymaganie |
| --- | --- |
| REQ-043 | Użytkownik wybiera CSV albo polecenia `INSERT`; wybrany format jest częścią zapisu zlecenia i wykonania. |
| REQ-044 | Wynik w postaci `INSERT` jest przeznaczony dla PostgreSQL i obejmuje dane potrzebne do realizacji zatwierdzonego planu. |
| REQ-045 | Wynik CSV zawiera osobny plik dla każdej uzupełnianej tabeli, pobierany wraz z pozostałymi jako jedna paczka. |
| REQ-046 | Paczka CSV zawiera prostą informację o przypisaniu plików do tabel i kolejności importu. |
| REQ-047 | Użytkownik może pobrać dane oraz prosty raport wykonania w postaci możliwej do automatycznego odczytania w przyszłym narzędziu oceniającym. |

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
- wyniki sprawdzeń kompletności i importowalności wraz z informacją, jak je potwierdzono;
- wyniki poszczególnych dodatkowych reguł;
- liczbę wykorzystanych rund poprawek i ich limit;
- czas wykonania oraz dostępne dane o tokenach, wywołaniach i koszcie;
- możliwość powiązania z historią wiadomości i prób.

Nie oznacza to obowiązku stworzenia rozbudowanego formatu analitycznego, dashboardu ani osadzania każdej dużej odpowiedzi modelu w głównym pliku raportu. Dokładne minimum eksportu i sposób dołączenia szczegółów wymagają ustalenia.

### 10.3. Raportowanie reguł

| ID | Wymaganie |
| --- | --- |
| REQ-048 | Wynik każdej sprawdzalnej reguły jest raportowany oddzielnie, z liczbą naruszeń i przykładami pozwalającymi zrozumieć problem. |
| REQ-049 | Raport w miarę znaczenia danej reguły wskazuje zakres sprawdzenia, np. 7 naruszeń wśród 200 sprawdzonych zakupów. Nie sprowadza wszystkich reguł do pojedynczych pól. |
| REQ-050 | MVP nie wylicza jednej zbiorczej oceny punktowej jakości ani automatycznej oceny realizmu. |
| REQ-051 | Wskazówki jakościowe i niewykonane sprawdzenia są wyraźnie odróżnione od sprawdzeń zakończonych wynikiem pozytywnym. |

Wynik reguły musi odpowiadać jej zatwierdzonemu znaczeniu. Jednostką naruszenia może być rekord, para rekordów, relacja albo cały zbiór; nie wolno przyjmować jednej jednostki dla wszystkich wymagań bez określenia jej znaczenia.

## 11. Historia i ponawianie

| ID | Wymaganie |
| --- | --- |
| REQ-052 | Każde rozpoczęte wykonanie ma osobny zapis historii, obejmujący również niepowodzenia i anulowania. |
| REQ-053 | Historia zachowuje wymagania faktycznie użyte w wykonaniu. Późniejsza zmiana projektu nie nadpisuje jego schematu, reguł ani zatwierdzonych liczebności w poprzednich wykonaniach. |
| REQ-054 | Historia zachowuje wygenerowane wyniki, błędy walidacji, przebieg poprawek i informację o ostatecznie zwróconej wersji danych. |
| REQ-055 | Historia zachowuje dokładne wiadomości wysłane do modeli i otrzymane od modeli, w tym wiadomości związane z poprawkami. |
| REQ-056 | Historia rozróżnia używane modele i ich rolę w procesie, jeśli wykonanie korzysta z wielu modeli lub agentów. |
| REQ-057 | Klucze API i inne dane uwierzytelniające nie są częścią zapisów wiadomości ani raportu badawczego. |
| REQ-058 | Użytkownik może ręcznie ponowić wcześniejsze zlecenie z tym samym schematem, regułami, poleceniem i liczebnościami, używając aktualnie podłączonego wariantu generowania. |
| REQ-059 | Ponowienie tworzy nowe wykonanie. Nie nadpisuje wcześniejszych wyników i nie uruchamia automatycznej serii prób. |

Zapis wiadomości dotyczy treści faktycznie wysłanych i otrzymanych przez aplikację. Nie oznacza żądania dostępu do niewidocznych wewnętrznych procesów rozumowania modelu.

Ponawianie starego zlecenia musi odróżniać **dawne wymagania zadania** od **aktualnego wariantu jego realizacji**. Zmiana promptu wewnętrznego podczas badań jest zmianą wariantu, a nie pozwoleniem na niejawne zmienienie pierwotnego polecenia użytkownika.

## 12. Wsparcie badań bez budowania platformy eksperymentalnej

| ID | Wymaganie |
| --- | --- |
| REQ-060 | Podczas badań można stosować modele lokalne i płatne modele udostępniane przez zewnętrzne API. |
| REQ-061 | Autor może ręcznie zmieniać modele, prompty i organizację procesu, w tym sprawdzać warianty wieloagentowe. Nie wymaga to edytora workflow ani panelu eksperymentów w aplikacji. |
| REQ-062 | Wykonanie zapisuje rzeczywiście zastosowany wariant i dostępne parametry modeli w zakresie potrzebnym do późniejszego rozróżnienia prób. |
| REQ-063 | Porównywane próby realizują ten sam zatwierdzony scenariusz. Zmiany jego wymagań muszą być widoczne, a nie ukryte pod tą samą etykietą zadania. |
| REQ-064 | Czas całego procesu obejmuje również przeprowadzone poprawki. Dostępne informacje o wywołaniach, tokenach i koszcie nie mogą pomijać prób naprawczych. |
| REQ-065 | Brak danych pomiarowych jest oznaczany jako brak dostępności, a nie jako wartość zero. Sam fakt działania modelu lokalnie nie stanowi podstawy do przypisania wyliczonego kosztu. |

### 12.1. Ręczny przebieg badania

1. Autor przygotowuje projekt i zatwierdzone zlecenie.
2. Podłącza pierwszy badany wariant i wykonuje zlecenie.
3. Zachowuje dane, historię i prosty raport.
4. Ręcznie zmienia model, prompty wewnętrzne lub organizację procesu.
5. Ponawia to samo zlecenie jako nowe wykonanie.
6. Powtarza próby według własnego planu, bez automatycznego harmonogramu.
7. Ocenia realizm i porównuje wyniki poza generatorem.
8. Wybiera wariant do docelowego użytkowania.

Nie ustanawia się tutaj liczby powtórzeń eksperymentu, listy konkretnych modeli, metod analizy statystycznej ani definicji „najlepszego” rozwiązania. Należą one do późniejszego planu badań, a nie do obowiązkowych funkcji generatora.

## 13. Wymagania przekrojowe i granice obietnic

### 13.1. Przejrzystość

- Użytkownik musi odróżnić wynik wykonany, niewykonany, przerwany błędem i anulowany.
- Wykryte naruszenia nie mogą zostać ukryte przez samo zakończenie procesu generowania.
- Powinno być jasne, czy trwa generowanie, sprawdzanie czy poprawianie. Szczegółowy układ interfejsu nie jest ustalony.
- Historia i raport muszą odzwierciedlać rzeczywisty przebieg, a nie wyłącznie ostatnią pozytywną odpowiedź.

### 13.2. Bezpieczeństwo znaczeniowe i poufność

- Treść wygenerowanych danych nie może samodzielnie zmieniać wymagań ani kryteriów oceny.
- Wariant generowania nie może zatwierdzić własnej poprawności wyłącznie przez deklarację tekstową.
- Materiały przekazywane do zewnętrznych API muszą być materiałami, które wolno wysłać poza środowisko użytkownika.
- Zgoda na porównanie modeli przez API nie oznacza zgody na wysyłanie dowolnych poufnych schematów.
- Aplikacja nie może deklarować pełnej prywatności tylko dlatego, że jest uruchamiana lokalnie, jeśli używany wariant komunikuje się z zewnętrznym modelem.

Nie ustalono wymogu automatycznego wykrywania poufnych danych ani rozbudowanego systemu polityk firmowych. Nie są one domyślną funkcją MVP.

### 13.3. Skala i wydajność

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

## 14. Scenariusze i kryteria akceptacji

Poniższe kryteria opisują oczekiwane zachowanie. Nie narzucają narzędzi testowych ani sposobu implementacji testów.

| ID | Scenariusz i oczekiwany rezultat | Powiązane wymagania |
| --- | --- | --- |
| AC-01 | Użytkownik wgrywa obsługiwany DDL PostgreSQL, zapisuje projekt i może później zlecić generowanie bez ponownego wgrywania schematu. | REQ-003, REQ-009, REQ-010 |
| AC-02 | DDL jawnie definiuje klucz obcy. Relacja jest wykorzystywana jako część schematu bez zastępowania jej zgadywaniem na podstawie nazw. | REQ-011 |
| AC-03 | Aplikacja podejrzewa niezadeklarowane powiązanie `buyer_id`. Do czasu zatwierdzenia nie przedstawia go jako obowiązującej relacji. | REQ-012 |
| AC-04 | Zlecenie wymaga nieobsługiwanej obowiązkowej zależności kołowej. Użytkownik otrzymuje informację przed generowaniem, a aplikacja nie zużywa limitu na udawane próby obsługi. | REQ-013 |
| AC-05 | Użytkownik wgrywa nową wersję DDL. Nowe zlecenie może z niej korzystać, ale poprzednie wykonanie zachowuje dawny schemat. | REQ-014, REQ-053 |
| AC-06 | Reguła biznesowa jest niejednoznaczna. Użytkownik widzi potrzebę wyjaśnienia i zatwierdza znaczenie sprawdzenia przed generowaniem. | REQ-016, REQ-017 |
| AC-07 | Wskazówka „dane mają być realistyczne” jest przekazana do generowania, lecz raport nie przedstawia jej jako automatycznie zaliczonego testu. | REQ-018, REQ-051 |
| AC-08 | Wykryto sprzeczność polecenia z DDL. Generowanie nie startuje, dopóki użytkownik jej nie rozstrzygnie. | REQ-019 |
| AC-09 | Polecenie wymienia nieokreślonych klientów VIP. Aplikacja prosi o doprecyzowanie zamiast sama tworzyć definicję VIP. | REQ-020, REQ-022 |
| AC-10 | Użytkownik prosi o 200 zakupów. Przed wykonaniem zatwierdza także liczby klientów, produktów i pozycji, bez konieczności samodzielnego wskazywania wszystkich tabel od początku. | REQ-021, REQ-024, REQ-025 |
| AC-11 | Każdy wygenerowany zakup odwołuje się wyłącznie do właściwych rekordów zawartych w paczce. Wynik nie zakłada wcześniej istniejących danych. | REQ-005, REQ-006, REQ-027 |
| AC-12 | Wynik zawiera 150 zamiast 200 wymaganych zakupów, mimo że jest importowalny. Status nie wskazuje wykonania zadania. | REQ-028 |
| AC-13 | Wynik jest kompletny i importowalny, ale narusza dodatkową regułę biznesową. Uruchamia poprawki w granicach limitu; jeśli naruszenie pozostaje po zakończeniu, status wykonania może pozostać pozytywny z jawnym raportem naruszenia. | REQ-029, REQ-032, REQ-037 |
| AC-14 | Reguła jest również ograniczeniem DDL, a jej naruszenie uniemożliwia import. Wynik nie zostaje uznany za wykonany wyłącznie na podstawie łagodniejszej oceny biznesowej. | REQ-027, REQ-030 |
| AC-15 | Obowiązkowego sprawdzenia nie udało się wykonać. Raport oznacza brak rozstrzygnięcia, a aplikacja nie deklaruje potwierdzonej importowalności. | REQ-031 |
| AC-16 | Ustawiono domyślny limit. Po pierwszym kandydacie aplikacja wykonuje najwyżej 3 rundy poprawek dla całego zlecenia i nie odnawia limitu przy następnej tabeli. | REQ-033, REQ-034, REQ-037 |
| AC-17 | Wariant wieloagentowy wykonuje kilka wywołań modeli w jednej rundzie. Historia nie przedstawia tej rundy jako pojedynczego wywołania. | REQ-035, REQ-056 |
| AC-18 | Pierwszy kandydat jest kompletny i importowalny, ale ma naruszenia biznesowe. Wszystkie późniejsze poprawki go uszkadzają. Po zakończeniu dostępny jest wcześniejszy użyteczny wynik ze swoim rzeczywistym raportem. | REQ-038, REQ-039, REQ-040 |
| AC-19 | Użytkownik anuluje wykonanie. Historia zachowuje dotychczasowy przebieg, a status odróżnia anulowanie od niepowodzenia modelu. | REQ-041, REQ-042, REQ-052 |
| AC-20 | Użytkownik wybiera `INSERT`. Wynikiem są dane w postaci przeznaczonej dla PostgreSQL; aplikacja nie wymaga jednoczesnego wygenerowania CSV. | REQ-008, REQ-043, REQ-044 |
| AC-21 | Użytkownik wybiera CSV dla wielu tabel. Otrzymuje jedną paczkę, osobny plik na tabelę i informację o przypisaniu oraz kolejności importu. | REQ-045, REQ-046 |
| AC-22 | Regułę narusza 7 z 200 zakupów. Raport pokazuje wynik tej reguły, zakres, liczbę i przykłady naruszeń, bez wyliczania ogólnej punktacji realizmu. | REQ-048, REQ-049, REQ-050 |
| AC-23 | Zakończone wykonanie ma dokładne zapisy wysłanych i otrzymanych wiadomości, także z poprawek. Klucze API nie występują w tych zapisach ani w raporcie. | REQ-055, REQ-057 |
| AC-24 | Użytkownik ponawia historyczne zlecenie po zmianie projektu i podłączeniu innego wariantu. Nowe wykonanie używa dawnych wymagań zadania oraz aktualnego wariantu i nie nadpisuje starego zapisu. | REQ-053, REQ-058, REQ-059, REQ-062 |
| AC-25 | Dane wraz z prostym raportem można pobrać i powiązać w przyszłym zewnętrznym narzędziu oceniającym z konkretnym wykonaniem. | REQ-047, REQ-052 |
| AC-26 | Dostawca nie udostępnia liczby tokenów albo nie ustalono kosztu lokalnego. Raport oznacza brak danych, zamiast wpisywać zero. | REQ-064, REQ-065 |
| AC-27 | Autor ręcznie podłącza kolejny lokalny lub zewnętrzny wariant i ponawia zadanie. Nie musi budować workflow ani uruchamiać automatycznej serii eksperymentów w interfejsie. | REQ-060, REQ-061, REQ-063 |
| AC-28 | Przegląd architektury identyfikuje granice kontekstu użytkownika, własności danych, kontroli dostępu, trwałego stanu zadań i zależności wdrożeniowych oraz wskazuje drogę rozwoju bez zastępowania rdzenia generatora. Odbiór MVP nie wymaga działającego logowania, wielu kont ani testów obciążeniowych przyszłego wdrożenia. | REQ-001, REQ-002, REQ-066 |
| AC-29 | Użytkownik korzysta z lokalnie uruchomionej aplikacji przez przeglądarkę. Nie jest wymagane logowanie ani publiczny hosting. | REQ-001, REQ-002, REQ-067 |
| AC-30 | Model przygotowuje wynik w wybranym formacie. Raport odnosi się do wyodrębnionej zawartości konkretnego kandydata, a pakowanie lub pobieranie nie zmienia sprawdzonych danych. Błędy nie są ukrywane przez ciche poprawianie danych przez aplikację. | REQ-040, REQ-043, REQ-068 |
| AC-31 | Po anulowaniu lub przerwaniu błędem użytkownik uruchamia nowe wykonanie od początku. Aplikacja nie kontynuuje starej próby z checkpointu ani nie nadpisuje jej historii. | REQ-052, REQ-058, REQ-059, REQ-069 |
| AC-32 | Błąd połączenia z modelem lub awaria walidatora kończy wykonanie bez automatycznego retry, zmiany wariantu i uruchamiania rundy naprawczej. Natomiast poprawnie odebrany SQL/CSV z wykrytym naruszeniem danych uruchamia poprawki w granicach limitu. | REQ-032, REQ-033, REQ-069, REQ-070 |

## 15. Kierunki rozszerzeń

Poniższa lista nie jest zatwierdzonym harmonogramem ani zobowiązaniem do realizacji:

1. Szersza obsługa PostgreSQL, w tym trudniejszych zależności i większego zakresu typów.
2. Generowanie samodzielnych złożonych dokumentów JSON.
3. Inne formaty schematów i wyników, jeśli będą potrzebne.
4. Uzupełnianie istniejących zbiorów danych.
5. Testy negatywne z odróżnieniem zamierzonych i niezamierzonych naruszeń.
6. Większe wolumeny.
7. Wdrożenie chmurowe lub udostępnienie zespołowi.
8. Osobna prosta aplikacja do oceny realizmu i porównywania wyników.

Żaden z tych punktów nie powinien blokować ukończenia uzgodnionego MVP.

## 16. Otwarte decyzje

Zakres MVP jest potwierdzony, ale nie wszystkie szczegóły kontraktów są już ustalone. Ta sekcja zapobiega dopisywaniu ukrytych założeń podczas implementacji.

| ID | Decyzja do podjęcia | Co już wiadomo |
| --- | --- | --- |
| OD-01 | Dokładna macierz obsługiwanych elementów PostgreSQL: typy, postacie kluczy, wyrażenia `CHECK` i `DEFAULT`, ewentualne dodatkowe wymagania importu. | Obsługiwany jest jawnie określony podzbiór tabel i ograniczeń. Nie obiecano obsługi całego PostgreSQL. |
| OD-02 | Mechanizm potwierdzania importowalności i jego szczegółowy zakres. | Dopuszczono system walidacyjny albo próbę importu; nie wybrano rozwiązania. Ustalono kolejność warstw: składnia/format, typy i schemat, dodatkowe reguły biznesowe. |
| OD-03 | Wybór między kilkoma kompletnymi i importowalnymi kandydatami o różnej zgodności biznesowej. | Użyteczny kandydat nie może zostać utracony przez późniejsze nieudane poprawki. Nie zatwierdzono wag ani zbiorczej punktacji. |
| OD-04 | Dokładny profil CSV i postać eksportu poleceń `INSERT`. | Użytkownik wybiera jeden format, a CSV dla wielu tabel jest paczką plików z kolejnością importu. |
| OD-05 | Minimalny format prostego raportu oraz sposób powiązania go z obszerniejszą historią wiadomości. | Raport ma być maszynowo czytelny i prosty; nie budujemy modułu analitycznego. |
| OD-06 | Szczegółowa postać prezentacji i zatwierdzania interpretacji reguł oraz organizacja reguł projektu i zlecenia. | Użytkownik zna kryterium sprawdzenia przed generowaniem; wskazówki jakościowe są odrębne. |
| OD-07 | Konkretne wartości timeoutów i sposób zapisania niepełnych informacji o nieudanej lub niepewnej operacji, w tym dostępnych pomiarów. | Błąd techniczny kończy wykonanie bez automatycznego retry i zmiany wariantu. Naruszenia danych uruchamiają ograniczone poprawki. Ręczne ponowienie tworzy nowe wykonanie; nie ma wznawiania. |
| OD-08 | Dostępność użytecznego kandydata lub częściowych artefaktów po anulowaniu i błędzie operacyjnym oraz dokładny moment zatrzymania. | Historia jest zachowana; nie ma wznawiania. Anulowanie i błąd nie są utożsamiane z normalnym niepowodzeniem generowania. |
| OD-09 | Zasady usuwania projektów, historii, dużych odpowiedzi i eksportów oraz czas ich przechowywania. | Wymagana jest historia potrzebna do badań; nie ustalono jej limitów ani polityki retencji. |
| OD-10 | Konkretne warianty badawcze i szczegóły organizacji pracy modeli w granicach gotowego wyniku. | Model przygotowuje gotowy SQL/CSV. Aplikacja nie generuje go z pośrednich rekordów i nie poprawia danych po cichu. Dokładny kontrakt przekazania plików i organizacja pracy modeli pozostają do ustalenia. |
| OD-11 | Lista modeli, sprzęt, parametry, szczegółowe definicje pomiarów i sposób wyboru zwycięzcy. | Badania są ręczne, obejmują modele lokalne i płatne oraz porównują wynik całego procesu na tym samym zadaniu. |
| OD-12 | Konkretny układ ekranów i szczegółowe interakcje użytkownika. | Ustalono lokalną aplikację webową w przeglądarce. Są projekty, przygotowanie zlecenia, wynik i historia; liczba zakładek i framework UI pozostają otwarte. |

Decyzje dotyczące implementacji nie powinny zastępować decyzji o wymaganiach. Przykładowo wybór biblioteki walidacyjnej nie rozstrzyga sam przez się, jakie elementy schematu aplikacja rzeczywiście potwierdza.

## 17. Powiązanie z ustaleniami wywiadu

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
