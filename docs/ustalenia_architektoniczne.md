# Rejestr ustaleń architektonicznych

**Data:** 21 października 2026.

**Aktualizacja:** 16 listopada 2026.

**Status:** zapis dotychczasowych ustaleń i kierunków projektowych. Nie jest potwierdzeniem działania bibliotek ani zgodności konkretnych wersji.

**Podstawa:** [specyfikacja MVP](specyfikacja_mvp.md), rozmowa o technologiach, adapterze LLM i przechowywaniu kontekstu.

**Stan implementacji S1-T3 — 16 listopada 2026:** dostarczono podstawowy
Compose, obrazy backendów, podawanie frontendu przez API, sieci i wolumen
bazy. Python 3.14.10, Node.js 26.13.1, uv 0.11.1 i PostgreSQL 18.7
sprawdzono przez budowanie i testy rzeczywistych kontenerów na macOS arm64.
Nazwy, ścieżki i wyniki testów zapisano w [planie S1-T3](plan_realizacji_mvp.md#s1-t3--przygotować-lokalne-uruchomienie-backendów-i-baz-w-docker-compose).
Migracje T4 zostały zaimplementowane i sprawdzone testami opisanymi
w [planie S1-T4](plan_realizacji_mvp.md#s1-t4--podłączyć-bazę-aplikacji-i-przygotować-mechanizm-migracji).
Magazyn T5 i monitor T9 nie są dostarczone.
Wcześniejsze wpisy „nie wykonano” opisują stan w momencie danej decyzji.

## 1. Jak rozumieć status decyzji

- **Uzgodnione wymaganie** — zachowanie określone w specyfikacji.
- **Zapisany kierunek** — rozwiązanie, na którym opieramy dalszy projekt, z zachowaniem podanych warunków.
- **Propozycja szczegółowa** — konkretna rekomendacja przygotowana do oceny; nie zatwierdza samodzielnie otwartych decyzji specyfikacji.
- **Otwarte** — wybór nadal wymaga rozstrzygnięcia albo próby technicznej.

Polecenie zapisania ustaleń nie oznacza przyjęcia nieomówionej reprezentacji reguł, całego dialektu PostgreSQL, konkretnych wersji zależności ani dowolnego sposobu wykonywania SQL.

## 2. Uzgodnione wymagania i doprecyzowania

| Obszar | Ustalenie |
| --- | --- |
| Uruchomienie | Lokalna aplikacja webowa, jeden użytkownik, bez logowania w MVP. |
| Rozwój | Granice umożliwiające przyszłe hostowanie, tożsamość użytkowników, izolację danych i współbieżne wykonania; nie wdrażamy ich na zapas. |
| Skala schematu | Uzgodnione 14 listopada 2026 w S2: docelowo nawet kilkaset tabel w jednym projekcie MVP, z możliwością objęcia wszystkich jednym zleceniem generowania, w granicach uzgodnionego dialektu PostgreSQL. To cel, nie zweryfikowana wydajność ani sztywny limit. Nie wymaga jednego wywołania LLM ani równoległego przetwarzania wszystkich tabel; podział pracy pozostaje otwarty. Nie zmieniono skali łącznej liczby rekordów z REQ-007. Nie zaakceptowano limitu 10 MiB DDL; limity wejścia są otwarte. |
| Wejście i wynik | DDL PostgreSQL, reguły i polecenie; model przygotowuje gotowy SQL `INSERT` albo treść CSV. |
| Paczki DDL | Uzgodnione 14 listopada 2026 w S2-T2: MVP dopuszcza również paczki wielu plików DDL, bez ograniczenia do pojedynczego pliku SQL. Użytkownik zaznacza wiele plików SQL i wysyła je razem w formularzu, bez konieczności tworzenia archiwum. Nie uzgodniono obsługi ZIP. Pliki wysłane razem tworzą jedną pełną wersję schematu, dopuszczaną do użycia tylko w całości. Błąd analizy w jednym pliku blokuje całą nową wersję, bez częściowego zastępowania dotychczasowego schematu; nieudaną wersję zachowujemy z diagnostyką. Użytkownik może ustawić kolejność plików przed wysłaniem; aplikacja traktuje je w tej kolejności jako jeden skrypt DDL, bez samodzielnego przestawiania. Limity pozostają otwarte; awarię wgrywania opisano w osobnym wierszu. |
| Kodowanie DDL | Uzgodnione 14 listopada 2026 w S2-T2: wyłącznie UTF-8, z dopuszczeniem BOM na początku każdego pliku. Niepoprawne kodowanie zgłaszamy jako czytelny błąd, bez automatycznego zgadywania i konwersji. W MVP błąd choćby jednego pliku odrzuca całą paczkę przed utworzeniem wersji i uruchomieniem analizy DDL; ponownie wysyłana jest pełna poprawiona paczka. Oryginalne przyjęte pliki zachowujemy bez zmian; BOM pomijamy wyłącznie na potrzeby analizy. Podmiana pojedynczego pliku jest kierunkiem rozszerzenia po MVP, nie częścią bieżących zadań. |
| Puste pliki DDL | Uzgodnione 14 listopada 2026 w S2-T2: pusty plik, plik zawierający wyłącznie białe znaki lub wyłącznie komentarze SQL i ewentualne białe znaki, bez instrukcji SQL, odrzuca całą paczkę przed utworzeniem wersji. Nie pomijamy go automatycznie. Zasada dotyczy również pojedynczego pliku. |
| Nazwy plików DDL | Uzgodnione 14 listopada 2026 w S2-T2: nazwy w jednej paczce są unikalne bez rozróżniania wielkości liter. Konflikt, np. `schema.sql` i `SCHEMA.sql`, odrzuca całą paczkę przed utworzeniem wersji. Techniczny sposób porównania nazw pozostaje otwarty. |
| Zbiorcze błędy paczki DDL | Uzgodnione 14 listopada 2026 w S2-T2: dla kompletnie odebranej paczki pokazujemy razem wykryte błędy kodowania, pustych plików i konfliktów nazw, bez zatrzymania sprawdzania na pierwszym błędzie. Odrzucamy paczkę przed utworzeniem wersji i analizą DDL. Nie gwarantuje to zebrania wszystkich błędów późniejszej analizy ani sprawdzenia treści pliku o niepoprawnym kodowaniu. Format diagnostyki pozostaje otwarty. |
| Wyjście podczas wysyłania DDL | Uzgodnione 14 listopada 2026 w S2-T2/S2-T6: podczas przesyłania ostrzegamy, że odświeżenie lub zamknięcie strony/aplikacji anuluje przesyłanie. Rezygnacja z wyjścia pozostawia transfer aktywny; wykonane wyjście ma go anulować. Obowiązują ograniczenia ostrzeżenia z sekcji 11.1 specyfikacji. Mechanizm anulowania i jego potwierdzenia pozostaje otwarty; los paczki zapisanej bez odebranego potwierdzenia rozstrzyga następny wiersz. Nie zaakceptowano przywracania nierozstrzygniętej próby po ponownym otwarciu. |
| Wyjście przed potwierdzeniem zapisu DDL | Doprecyzowanie 14 listopada 2026 w S2-T2/S2-T6 rozstrzygające przypadek wskazany powyżej: jeśli użytkownik wykona wyjście przed odebraniem potwierdzenia przez przeglądarkę, nie zachowujemy nowej wersji, nawet gdy backend zapisał już całą paczkę. Pliki anulowanej próby usuwamy bez zmiany wcześniejszych wersji. Mechanizm wykrycia tego przypadku, anulowania i sprzątania oraz moment uruchomienia analizy pozostają otwarte; samo przerwanie transferu nie stanowi dowodu usunięcia danych. |
| Potwierdzenie odbioru paczki DDL | Uzgodnione 14 listopada 2026 w S2-T2/S2-T6, doprecyzowujące moment uruchomienia analizy: serwer zapisuje paczkę roboczo i wysyła komunikat o zapisie. Analiza może ruszyć dopiero po otrzymaniu dodatkowego, automatycznego potwierdzenia z przeglądarki, że odebrała ten komunikat. Bez dodatkowego kliknięcia użytkownika. Sam zapis lub wysłanie odpowiedzi przez serwer nie uruchamiają analizy. Kontrakt, obsługa utraty potwierdzenia i porzuconego zapisu oraz sprzątanie pozostają otwarte. |
| Analiza DDL po zamknięciu strony | Uzgodnione 14 listopada 2026 w S2-T2/S2-T6: po przyjęciu dodatkowego potwierdzenia analiza działa asynchronicznie, niezależnie od otwartej strony. Odświeżenie lub zamknięcie strony nie anuluje rozpoczętej analizy przyjętej paczki. Nadal obowiązuje osobna akcja ręcznego przerwania analizy. Nie zmienia to anulowania podczas przesyłania ani zasad awarii po zatrzymaniu backendu. |
| Wyczerpanie ponowień analizy DDL | Uzgodnione 14 listopada 2026 w S2-T2/S2-T6, rozstrzygające dalszą ręczną obsługę awarii: po pierwszym uruchomieniu i wyczerpaniu trzech automatycznych ponowień nie udostępniamy ręcznego ponowienia analizy zapisanej paczki. Użytkownik musi ponownie wgrać całą paczkę plików, bez podmiany jednego pliku i bez wznawiania zakończonej analizy. |
| Współbieżność analiz DDL | Uzgodnione 14 listopada 2026 w S2-T2/S2-T6: w całym MVP jednocześnie działa tylko jedna analiza DDL, również między różnymi projektami. Nie ogranicza to liczby zapisanych projektów. Blokada wgrywania DDL we wszystkich projektach obowiązuje już od rozpoczęcia wysyłania jednej paczki, również w innych kartach przeglądarki, podczas analizy i podczas oczekiwania na jej automatyczne ponowienie po awarii. Nie zwalniamy blokady pomiędzy próbami. Nie przyjmujemy kolejnych paczek do kolejki ani do równoczesnego wysyłania przed analizą. Mechanizm egzekwowania pozostaje otwarty. |
| Odmowa wysłania DDL podczas blokady | Uzgodnione 14 listopada 2026 w S2-T2/S2-T6: HTTP `409`, kod `DDL_PROCESSING_IN_PROGRESS` i komunikat interfejsu „Trwa przesyłanie lub analiza DDL. Poczekaj na zakończenie”. Ścieżka uploadu i pozostałe pola kontraktu nadal wymagają dopracowania. |
| Analiza DDL w tle | Uzgodnione 14 listopada 2026 w S2-T2: po odebraniu i zapisaniu plików potwierdzamy wgranie, a analizę wykonujemy w tle, pokazując jej stan w interfejsie. Żądanie wgrywania nie czeka na zakończenie analizy. Potwierdzenie zapisu nie oznacza gotowości do generowania. Po awarii przerywającej analizę aplikacja automatycznie uruchamia analizę zapisanej paczki ponownie, gdy jest to możliwe, bez ponownego wgrywania i ręcznej akcji. Nie dotyczy to naprawiania DDL ani ponawiania generowania danych. Dopuszczamy maksymalnie trzy automatyczne ponowienia poza pierwszym uruchomieniem, następnie zatrzymanie z czytelnym błędem, bez kolejnego automatycznego ponowienia. Limit jest odrębny od rund naprawczych generowania. Kontynuujemy od zachowanego postępu, jeżeli jest to technicznie możliwe i zapewnia poprawny, kompletny wynik; wykonalność i zapis postępu wymagają weryfikacji. Gdy kontynuacja jest niemożliwa, automatycznie analizujemy zapisaną paczkę od początku, bez ponownego wgrywania i w ramach tego samego limitu trzech ponowień. Mechanizm, dokładne stany, odstępy ponowień i dalsza ręczna obsługa pozostają otwarte. Nie ustalono procentowego postępu. |
| Lokalizacja błędów DDL | Uzgodnione 14 listopada 2026 w S2: diagnostyka wskazuje nazwę oryginalnego pliku i numer wiersza w tym pliku, gdy miejsce błędu można ustalić. Sama pozycja w połączonym skrypcie nie wystarcza. Dla problemu całej paczki pokazujemy opis bez sztucznej lokalizacji. Kontrakt i mapowanie pozycji pozostają otwarte. |
| Zmiana DDL podczas analizy | Uzgodnione 14 listopada 2026 w S2-T2: użytkownik najpierw przerywa bieżącą analizę, a po jej zatrzymaniu może wgrać kolejną wersję DDL. Nie analizujemy obu wersji równolegle w tym samym projekcie. Świadome przerwanie nie uruchamia automatycznych ponowień przewidzianych dla awarii. Nie zachowujemy jej plików jako wersji oznaczonej „przerwana”. Po potwierdzonym ręcznym zatrzymaniu usuwamy pliki wgrane dla tej analizy i jej częściowy wynik, bez zmiany wcześniejszych wersji. Interfejs wymaga uprzedniego potwierdzenia z ostrzeżeniem o usunięciu tych danych; rezygnacja nie zatrzymuje analizy ani nie usuwa danych. Techniczne potwierdzenie zatrzymania, sposób sprzątania i obsługa jego błędu pozostają otwarte. Nie zmienia to zasad obsługi awarii ani błędów analizy. |
| Dane projektu | Uzgodnione 14 listopada 2026 w S2-T1: wymagana nazwa (1–100 znaków) i opcjonalny opis (do 2000 znaków), bez zamkniętej listy dziedzin. Przed walidacją długości i zapisem usuwamy brzegowe białe znaki; pusta nazwa jest błędem, pusty opis oznacza brak opisu. Przekroczenie limitu powoduje czytelny błąd bez obcinania treści. Opis nie zastępuje DDL ani zatwierdzonych reguł. Projekt można zapisać przed wgraniem DDL i dodać schemat później; bez schematu nie jest gotowy do generowania. Nazwy są unikalne w instalacji bez rozróżniania wielkości liter; duplikat odrzucamy bez nadpisania projektu. Realizacja ograniczenia w bazie pozostaje otwarta. |
| Nieudana analiza DDL | Uzgodnione 14 listopada 2026 w S2-T2: przesłany DDL zachowujemy jako osobną wersję z diagnostyką, bez dopuszczenia jej do generowania i bez zastępowania dotychczasowej używanej wersji schematu. Poprawiony pełny DDL jest kolejną wersją. Dotyczy kompletnej, odebranej i zapisanej paczki, nie błędu jej transferu lub zapisu. |
| Awaria wgrywania DDL | Uzgodnione 14 listopada 2026 w S2-T2: przy przerwanym transferze lub nieudanym zapisie paczki nie tworzymy nowej wersji i nie zmieniamy dotychczasowego schematu. Użytkownik musi ponownie wysłać całą paczkę. Utrata odpowiedzi serwera sama nie potwierdza nieudanego zapisu. Aplikacja najpierw sprawdza wynik wysłania paczki, zamiast od razu proponować ponowienie, aby uniknąć duplikatu. Frontend tworzy unikalny identyfikator każdej próby przed wysłaniem plików; po utracie odpowiedzi sprawdza po nim wynik tej samej próby w backendzie, bez ponownego przesyłania paczki. Przy nadal nieznanym wyniku blokujemy ponowne wysłanie tej paczki do ustalenia wyniku i pokazujemy przycisk „Sprawdź ponownie”, który odczytuje wynik tej samej próby bez wysyłania plików. Format i przechowywanie identyfikatora, zachowanie po odświeżeniu strony, techniczny zapis, sprzątanie plików i kontrakt odczytu wyniku pozostają otwarte. |
| Domyślna wersja DDL | Uzgodnione 14 listopada 2026 w S2-T2: nowa wersja po poprawnej analizie, bez blokad uniemożliwiających jej użycie, automatycznie staje się domyślną dla nowych zleceń. Rozpoczęte wykonania zachowują wcześniej przypięte wymagania (REQ-014). Dotychczasowe reguły biznesowe i zatwierdzone relacje spoza DDL pokazujemy jako propozycje do przeglądu, bez konieczności wpisywania ich od początku. Wymagają ponownej weryfikacji i zatwierdzenia przed użyciem z nową wersją. Start generowania na nowym schemacie jest zablokowany do rozpatrzenia każdej propozycji: zatwierdzenia po weryfikacji albo świadomego odrzucenia dla nowej wersji. Wersja domyślna nie oznacza gotowości do generowania; przegląd nie omija innych blokad. |
| Kolumny JSON/JSONB | Uzgodnione 14 listopada 2026: obsługa kolumn `json`/`jsonb` w schematach użytkownika pozostaje poza MVP, jako potencjalny kierunek rozwoju, nie zaplanowana funkcja (OD-01, sekcje 4.2 i 15 specyfikacji). Nie ogranicza to wewnętrznego użycia JSON w aplikacji. |
| Hierarchie w jednej tabeli | Uzgodnione 14 listopada 2026: proste hierarchie, np. pracownicy i przełożeni, należą do MVP (REQ-005, AC-37). Korzeń nie ma rodzica zgodnie z dopuszczeniami schematu, wskazani rodzice należą do paczki, nie ma zapętleń. Nie oznacza to obsługi dowolnych cykli. |
| Walidacja | Składnia/format → wstępna zgodność ze schematem i typami → rzeczywisty próbny import do pustego, odizolowanego PostgreSQL, obowiązujące relacje i kompletność → dodatkowe reguły biznesowe. |
| Poprawki | Naruszenia danych uruchamiają ograniczone poprawki, domyślnie maksymalnie 3 rundy po pierwszym kandydacie dla danej prośby. Każda nowa prośba użytkownika o zmianę danych ma własny limit, niezależny od poprzedniej. Limit jest wspólny dla tabel i wywołań danej prośby; automatyczna poprawka go nie odnawia (REQ-033–REQ-034, AC-44). |
| Pierwsze generowanie bez użytecznej paczki | Uzgodnione 14 listopada 2026: po wyczerpaniu domyślnych 3 rund naprawczych pokazujemy niepowodzenie. Nie udostępniamy przycisku „Podejmij kolejne 3 próby” ani nie uruchamiamy dodatkowej serii (REQ-079, AC-47). |
| Błędy techniczne | Zatrzymanie bez automatycznego retry i bez przełączenia modelu lub wariantu. |
| Przerwanie | Można anulować; nie ma wznawiania po anulowaniu, błędzie ani utracie procesu. Ręczne ponowienie tworzy nowe wykonanie. |
| Historia poza MVP | Rozstrzygnięte 14 listopada 2026, zastępuje wcześniejszy zakres: nie przechowujemy archiwum wykonań, wiadomości ani funkcji ponawiania z historycznego zapisu (REQ-072, AC-38). Bieżąca rozmowa, stan wykonania, wynik i raport nie są archiwum. |
| Główny widok czatu | Uzgodnione 14 listopada 2026: wybór projektu, polecenie, odpowiedź i dostępny wynik w czacie; użytkownik może kontynuować rozmowę kolejnymi poleceniami (REQ-073, AC-39). |
| Zmiana otrzymanych danych | Uzgodnione 14 listopada 2026: przy prośbie o zmianę LLM dostaje poprzednią paczkę jako kontekst i nowe polecenie, poprawia wskazane dane i zwraca poprawioną paczkę do walidacji (REQ-076, AC-42). Nie jest to generowanie niezależnego zestawu od zera ani wznowienie procesu. Własny limit napraw określają REQ-033–REQ-034; techniczne przypisanie do wykonania i szczegóły transportu pozostają w OD-10. |
| Nieudana zmiana i dodatkowe naprawy | Uzgodnione 14 listopada 2026: po wyczerpaniu napraw bez użytecznej poprawionej paczki informujemy o niepowodzeniu i zachowujemy poprzednią sprawdzoną paczkę z jej raportem, nie jako realizację nowej prośby. Akcja „Podejmij kolejne 3 próby” jest jednorazowa dla danej prośby i zleca do 3 dodatkowych rund, bez dodatkowego pierwszego kandydata poza limitem (REQ-078–REQ-079, AC-45–AC-46). Po niepowodzeniu tej serii kończymy naprawy, nie pokazujemy ponownie przycisku i zachowujemy poprzednią sprawdzoną paczkę z jej raportem. Nie wznawia procesu po anulowaniu lub awarii. Dodatkowa seria naprawia ostatniego nieudanego kandydata z listą wykrytych w nim błędów; nie zaczyna od poprzedniej sprawdzonej paczki. Powiązanie serii z wykonaniem i licznikami oraz kontrakt kontekstu pozostają w OD-10. |
| Koniec bieżącego czatu | Uzgodnione 14 listopada 2026: „Nowy czat”, wykonane odświeżenie i zamknięcie strony oraz pełne zamknięcie aplikacji kończą dostęp do poprzedniej konwersacji i jej plików. Po powrocie widzimy nowy czat; zapisane projekty pozostają (REQ-074, AC-40). Historia czatów i plików to kandydat na dalszy rozwój poza MVP. |
| Anulowanie przy opuszczeniu czatu | Uzgodnione 14 listopada 2026: opuszczenie czatu ma także anulować trwające wykonanie (REQ-077, AC-43). Po przyjęciu anulowania nie rozpoczynamy dalszych etapów ani wywołań LLM; spóźniona odpowiedź nie wznawia pracy i nie trafia do nowego czatu. Samo otwarcie ostrzeżenia i pozostanie na stronie nie anuluje wykonania. Mechanizm wykrycia wyjścia i potwierdzenie zatrzymania pozostają otwarte; nie gwarantujemy natychmiastowego przerwania żądania u dostawcy. |
| Ostrzeżenie o utracie danych | Uzgodnione 14 listopada 2026: przed odświeżeniem lub zamknięciem strony wymagane jest ostrzeżenie z możliwością pozostania. Rezygnacja zachowuje rozmowę i pliki (REQ-075, AC-41). Ograniczenia przeglądarki, w tym brak kontroli nad tekstem okna i brak gwarancji przy wymuszonym zamknięciu, opisuje sekcja 11.1 specyfikacji. |
| Oddzielenie badań | Autor organizuje badania i ich archiwum poza aplikacją. Nie dodajemy generatorowi obowiązków badawczych. Dostępność bieżącego czatu określa REQ-074; techniczny mechanizm zakończenia dostępu i sprzątanie danych roboczych pozostają w OD-09. |
| Ocena | Sukces wymaga kompletności, importowalności i zgodności wszystkich obowiązujących relacji. Dodatkowe naruszenia biznesowe są odrębne, realizm oceniamy poza generatorem. |
| Relacje zatwierdzone poza DDL | Uzgodnione 14 listopada 2026: po zatwierdzeniu są obowiązkowym warunkiem wykonania zadania (REQ-012, REQ-027, AC-34). Sprawdzamy je osobno po imporcie. Naruszenie blokuje sukces, ale nie zmienia wyniku udanego importu ani oryginalnego DDL. |
| Reguła sumująca dane między tabelami | Uzgodnione 14 listopada 2026: MVP obejmuje ograniczony rodzaj reguły „wartość zamówienia = suma ilość × cena jego pozycji” (REQ-071, AC-33). Najpierw zaokrąglamy wartość każdej pozycji, następnie sumujemy te wartości; aplikacja nie pyta użytkownika o tę kolejność. Reguła sumująca obejmuje wszystkie pozycje danego rekordu nadrzędnego w paczce, powiązane jedną jawnie wskazaną obowiązującą relacją. Nie obejmuje dodatkowego filtrowania pozycji ani przechodzenia przez kolejne tabele. Relacja pochodzi z DDL albo jest zatwierdzona poza nim zgodnie z REQ-012; aplikacja nie wybiera jej domyślnie. Przykład: wartość zamówienia równa sumie ilość × cena wszystkich jego pozycji, a nie tylko pozycji wybranego statusu. Liczba miejsc po przecinku, do której zaokrąglamy iloczyn każdej pozycji, jest jawnym parametrem konkretnej reguły sumującej, widocznym w interpretacji do zatwierdzenia. Reguły mogą wskazywać różną precyzję, np. 2 albo 3 miejsca. Nie narzucamy dwóch miejsc wszystkim regułom ani nie wyprowadzamy precyzji po cichu ze schematu. W MVP stosujemy jeden tryb zaokrąglania iloczynu pozycji: do najbliższej wartości o zadanej liczbie miejsc, a przy dokładnej połowie — od zera. Dla 2 miejsc: 1,234 daje 1,23; 1,235 daje 1,24; −1,235 daje −1,24. Tryb jest stałą zasadą aplikacji, widoczną w interpretacji reguły, bez wyboru innego trybu. Dozwolony zakres parametru precyzji pozostaje otwarty. NULL w wartości rekordu nadrzędnego albo w którymkolwiek z dwóch mnożonych pól którejkolwiek powiązanej pozycji oznacza naruszenie reguły sumującej dla rekordu nadrzędnego. Nie zastępujemy NULL zerem i nie pomijamy niekompletnych pozycji. Na przykład zamówienie z pozycją bez ceny narusza regułę, zamiast być sprawdzane wyłącznie na podstawie sumy pozostałych pozycji. Przy braku powiązanych pozycji suma wynosi 0. Rekord nadrzędny bez pozycji spełnia regułę sumującą wyłącznie wtedy, gdy jego wartość wynosi 0; inna wartość daje naruszenie, a NULL pozostaje naruszeniem zgodnie z zasadą brakujących wartości. Brak pozycji sam w sobie nie narusza tej reguły. Nie zmienia to wymagań DDL ani innych reguł, które mogą wymagać istnienia pozycji. Wartość nadrzędną porównujemy dokładnie z sumą już zaokrąglonych pozycji, bez tolerancji różnicy i bez dodatkowego zaokrąglania wartości nadrzędnej lub sumy. Porównujemy wartość liczbową, nie liczbę zer w zapisie. Dla sumy 19,99 wartość nadrzędna 19,990 daje zgodność, a 19,991 naruszenie. Reguła sumująca operuje wyłącznie na typach smallint, integer, bigint i numeric/decimal we wszystkich trzech polach: wartości nadrzędnej oraz obu mnożonych polach pozycji. Obliczenia zachowują dokładność dziesiętną, bez przybliżania przez binarne liczby zmiennoprzecinkowe i bez automatycznej zamiany tekstu na liczby. Nie wybiera to biblioteki ani reprezentacji API. Pozostałe szczegóły obliczeń i wykonania pozostają w OD-06; nie zatwierdzono dowolnych agregacji. |
| Mechanizm interpretacji reguł | Uzgodnione 14 listopada 2026 podczas planowania S3: LLM proponuje rodzaj reguły z katalogu i parametry; aplikacja sprawdza obsługiwalność; użytkownik zatwierdza czytelny opis znaczenia; walidator sprawdza dane gotowym mechanizmem danego rodzaju, bez wykonywania kodu modelu (REQ-016). Format definicji i szczegółowe kontrakty pozostają w OD-06. |
| Zakres porównania kolumn | Uzgodnione 14 listopada 2026 podczas doprecyzowania S3-T1: dwie kolumny tego samego rekordu w jednej tabeli. Ten rodzaj nie obejmuje porównań kolumn różnych rekordów lub tabel; osobna reguła sumująca między tabelami pozostaje w MVP. Uzgodniono operacje: równe, różne, mniejsze, mniejsze lub równe, większe i większe lub równe. Zatwierdzono macierz par typów i dostępnych operacji z sekcji 5.2 specyfikacji; inne pary są nieobsługiwane i nie stosujemy automatycznego dopasowywania poza wymienionymi grupami. NULL w którejkolwiek z dwóch kolumn jest naruszeniem, także gdy obie wartości są NULL; rekordu nie pomijamy i nie zmieniamy DDL. Zasada nie dotyczy automatycznie innych rodzajów reguł. Równość i różność tekstu dotyczą dokładnej treści z uwzględnieniem wielkości liter i wszystkich spacji, bez automatycznego przekształcania wartości. Sprawdzamy wszystkie rekordy wskazanej tabeli w zaimportowanej paczce; jeden niezgodny rekord to jedno naruszenie tej reguły, także gdy obie wartości są NULL. Zapis operatorów i kontrakt pozostają w OD-06. |
| Zakres porównania ze stałą | Uzgodnione 14 listopada 2026 podczas doprecyzowania S3-T1: pojedyncza kolumna rekordu porównywana ze stałą wartością, stałymi granicami zakresu albo jawnym zbiorem stałych wartości, bez obliczeń i odwołań do innych rekordów lub tabel. Nie zmienia to osobnej reguły sumującej. Wariant „wartość w zakresie” obejmuje obie granice, np. 18 i 65 dla 18–65, bez wyboru granic otwartych w MVP. Wariant „wartość w zakresie” obsługuje wyłącznie kolumny smallint, integer, bigint, numeric/decimal, date, timestamp i timestamptz. Zakresy dla text, varchar, boolean i uuid są nieobsługiwane. Dla kolumny liczbowej obie granice zakresu są liczbami ze wspólnej grupy smallint/integer/bigint/numeric/decimal. Dla date, timestamp i timestamptz obie granice mają dokładnie ten sam typ co kolumna. Pozostałe połączenia są nieobsługiwane, bez automatycznych konwersji między tymi grupami, np. tekst–liczba i date–timestamp. Dotyczy to typów w definicji reguły, nie rozpoznawania polecenia przez LLM. W wariancie „wartość w zakresie” NULL w sprawdzanej kolumnie zawsze oznacza naruszenie reguły. Rekordu nie pomijamy i nie zmieniamy oryginalnego DDL. Na przykład brak wieku narusza regułę „wiek w zakresie 18–65”. Zakres sprawdzania i jednostkę naruszenia określa wspólna zasada prostych porównań poniżej. Wariant „wartość w zakresie” wymaga obu granic innych niż NULL. Brak którejkolwiek granicy lub NULL zamiast niej oznacza błędną definicję z czytelnym komunikatem. Nie traktujemy brakującej granicy jako nieskończoności. Warunki jednostronne, np. „wiek co najmniej 18”, można opisać porównaniem z pojedynczą stałą. Dla prostych porównań (kolumna–kolumna, pojedyncza stała, zakres i zbiór) obowiązuje wspólna zasada: sprawdzamy wszystkie rekordy wskazanej tabeli w zaimportowanej paczce; każdy niezgodny rekord oznacza jedno naruszenie danej reguły. Wynik podaje liczbę naruszeń wobec liczby sprawdzonych rekordów, np. 7 wśród 100. Nie ustala to zasad reguł warunkowych i sumujących. Format granic nadal wymaga ustalenia. Dolna granica musi być mniejsza lub równa górnej. Zakres 18–18 jest poprawny i dopuszcza tylko 18. Zakres 65–18 jest błędną definicją: aplikacja wyświetla zrozumiały błąd i nie zamienia granic automatycznie. Dla porównania kolumny z pojedynczą stałą uzgodniono sześć operacji: równe, różne, mniejsze, mniejsze lub równe, większe oraz większe lub równe. To katalog operacji, nie dopuszczenie każdej z nich dla każdego typu. Dla kolumn smallint, integer, bigint, numeric/decimal, date, timestamp i timestamptz dostępne są wszystkie sześć operacji. Dla text, varchar, boolean i uuid dostępne są tylko równe i różne. W porównaniu z pojedynczą stałą wymagamy zgodności typów: liczby porównujemy w grupie smallint/integer/bigint/numeric/decimal, tekst w grupie text/varchar, a date, timestamp, timestamptz, boolean i uuid każde wyłącznie ze stałą swojego typu. Pozostałe pary są nieobsługiwane, bez automatycznych konwersji między grupami, np. liczba–tekst i date–timestamp. Dotyczy to typów w definicji reguły, nie sposobu rozpoznawania polecenia przez LLM. W porównaniu kolumny z pojedynczą stałą inną niż NULL brak wartości (NULL) w kolumnie zawsze oznacza naruszenie, także przy operacji „różne”. Rekordu nie pomijamy ani nie uznajemy za zgodny. Na przykład brak statusu narusza regułę „status różny od anulowany”. Nie zmieniamy oryginalnego DDL. NULL w sprawdzanej kolumnie narusza obie operacje zbioru. Równość i różność tekstu w porównaniu kolumny z pojedynczą stałą dotyczą dokładnej treści, z uwzględnieniem wielkości liter i wszystkich spacji, bez automatycznego przekształcania. „ABC” jest różne od „abc” i od „ABC ” (ze spacją na końcu). Decyzji nie rozszerzono na zakresy ani zbiory. Porównanie z pojedynczą stałą obejmuje wszystkie rekordy wskazanej tabeli w zaimportowanej paczce. Każdy niezgodny rekord, także z NULL, oznacza jedno naruszenie tej reguły. Przykładowo 7 niezgodnych rekordów spośród 100 daje 7 naruszeń wśród 100 sprawdzonych. Wspólna zasada poniżej obejmuje również zakresy i zbiory. W wariancie porównania z pojedynczą stałą NULL nie może występować po stronie stałej. Definicje „równe NULL” i „różne od NULL” są nieobsługiwane w tym wariancie; aplikacja podaje czytelną przyczynę zamiast wykonywać zwykłe porównanie. Ewentualne osobne sprawdzanie obecności lub braku wartości pozostaje do ustalenia. Nie usuwa to uzgodnionego wymagania obsługi reguły warunkowej z wymaganą datą dostawy przy określonym statusie. Format stałych i zapis operatorów pozostają otwarte. Porównanie ze zbiorem obsługuje dwie operacje: „należy do zbioru” oraz „nie należy do zbioru”. Przykładowo status ma należeć do listy {nowy, opłacony, wysłany} albo nie należeć do listy {anulowany, odrzucony}. W obu operacjach porównania ze zbiorem definicja musi zawierać niepustą listę stałych innych niż NULL. Pusta lista lub NULL jako element oznacza błędną definicję z czytelną informacją o przyczynie, zamiast wykonania reguły. Dotyczy to listy w definicji, nie braku wartości w sprawdzanym rekordzie. Obie operacje zbioru korzystają z uzgodnionych zasad porównania z pojedynczą stałą: „należy” wymaga spełnienia porównania „równe” z co najmniej jednym elementem, a „nie należy” spełnienia porównania „różne” ze wszystkimi elementami. Każdy element musi być zgodny typowo z kolumną: liczby w grupie smallint/integer/bigint/numeric/decimal, tekst w grupie text/varchar, a date, timestamp, timestamptz, boolean i uuid każde ze swoim typem. Nie stosujemy konwersji między tymi grupami i nie pomijamy niezgodnych elementów definicji. Tekst porównujemy dokładnie, z uwzględnieniem wielkości liter i wszystkich spacji. NULL w sprawdzanej kolumnie oznacza naruszenie w obu operacjach. Format zapisu stałych pozostaje w OD-06. |
| Postać reguły warunkowej | Uzgodnione 14 listopada 2026 podczas doprecyzowania S3-T1: Reguła warunkowa w MVP ma postać „jeśli jeden warunek, to jedno wymaganie” i dotyczy tego samego rekordu jednej tabeli. Nie ma gałęzi „w przeciwnym razie” ani zagnieżdżonych reguł. Przykład: jeśli status jest równy „wysłany”, data dostawy musi być podana. Osobna reguła sumująca między tabelami pozostaje w MVP. Warunek i wymaganie korzystają z tego samego katalogu pojedynczych sprawdzeń: porównanie dwóch kolumn, porównanie z pojedynczą stałą, zakres, zbiór, „wartość jest NULL” oraz „wartość nie jest NULL”. Każdy człon jest jednym sprawdzeniem, bez łączenia przez „i”/„lub”; wszystkie odwołania dotyczą tego samego rekordu. „Wartość nie jest NULL” oznacza obecność wartości, nie sprawdzanie niepustości tekstu. Gdy warunek jest spełniony, oceniamy wymaganie: jego spełnienie oznacza zgodność, a niespełnienie naruszenie. Gdy warunek jest niespełniony przy dostępnych danych, wynik to „nie dotyczy”: wymagania nie oceniamy i nie zgłaszamy naruszenia. NULL w wartości potrzebnej do zwykłego porównania w warunku oznacza naruszenie całej reguły, a nie „nie dotyczy”. Jawne sprawdzenia „jest NULL” i „nie jest NULL” normalnie rozstrzygają warunek. Na przykład dla „jeśli status = wysłany, data dostawy nie jest NULL” status nowy daje „nie dotyczy”, status wysłany bez daty naruszenie, a status NULL również naruszenie. Reguła warunkowa obejmuje wszystkie rekordy wskazanej tabeli w zaimportowanej paczce. Raport rozlicza je w trzech rozłącznych grupach: zgodne, naruszenia i „nie dotyczy”. Każdy rekord trafia do jednej grupy i daje najwyżej jedno naruszenie danej reguły, również przy NULL w warunku. Rekordów „nie dotyczy” nie przedstawiamy jako spełniających wymaganie. Przykładowo 100 ocenionych rekordów to 35 zgodnych, 5 naruszeń i 60 „nie dotyczy”. |
| Katalog reguł biznesowych | Uzgodnione 14 listopada 2026 podczas planowania S3: obok ograniczonej reguły sumującej MVP obejmuje porównanie kolumn, porównanie wartości z progiem/zakresem/zbiorem i regułę warunkową. Operatory, obsługiwane typy, NULL, zakres sprawdzenia, jednostka naruszenia i reprezentacja pozostają w OD-06. |
| Zakres obowiązywania reguł | Uzgodnione 14 listopada 2026 podczas planowania S3: zatwierdzone reguły projektu obowiązują we wszystkich jego nowych zleceniach. Reguła pojedynczego zlecenia dotyczy tylko jego i nie zapisuje się automatycznie w projekcie. Wykryty konflikt wymaga wyjaśnienia, bez cichego nadpisania reguły projektu (REQ-015, REQ-019). Szczegóły UI, reprezentacji i zmian pozostają w OD-06. |
| Nieobsługiwana reguła | Uzgodnione 14 listopada 2026 podczas planowania S3: blokada startu i informacja z wyborem kontynuowania bez reguły albo jej poprawienia. Bez świadomego wyboru generowanie nie rusza; poprawiona reguła wymaga obsługiwanej i zatwierdzonej interpretacji. Pominięcie nie oznacza spełnienia ani automatycznej zamiany we wskazówkę jakościową (REQ-017, AC-06). Pominięcie reguły projektu dotyczy wyłącznie bieżącego zlecenia, bez zmiany lub usunięcia reguły w projekcie. W kolejnych nowych zleceniach reguła nadal obowiązuje; ponowne pominięcie wymaga świadomej decyzji użytkownika. |
| Zachowanie kandydata | Późniejsza nieudana poprawka nie usuwa wcześniejszego użytecznego wyniku, spełniającego wszystkie warunki REQ-027. Raport i eksport dotyczą tego samego kandydata. |
| Wybór kandydata | Uzgodnione 14 listopada 2026: zwracamy wyłącznie najnowszego użytecznego kandydata bieżącego wykonania, także przy pobieraniu po przerwaniu (REQ-039, AC-36; OD-03 zamknięte). Nie porównujemy liczby ani wag dodatkowych naruszeń i nie wymagamy archiwum starszych wersji. |
| Pobieranie po przerwaniu | Uzgodnione 14 listopada 2026: wcześniej zapisany użyteczny kandydat i jego raport są dostępne także po anulowaniu lub błędzie (REQ-047, AC-35). Nie zmieniamy statusu wykonania ani nie wznawiamy procesu. Dostępność niesprawdzonych lub częściowych artefaktów nadal jest otwarta. |

## Kontekst właściciela i polityka dostępu — S1-T6

**Decyzja architekta w procesie delivery-orchestrator, 17 listopada 2026:**
Dla zadania [#21](https://github.com/jwieczor03/mgr-llm-data-generator/issues/21)
przyjęto minimalną wymienną granicę, aby przyszła integracja tożsamości
nie wymagała przenoszenia szczegółów logowania do logiki zasobów.

- Niemutowalny `ActorContext` przechowuje `subject`: niepusty tekst,
  bez normalizacji. Pusty, zawierający tylko białe znaki i nietekstowy
  identyfikator są odrzucane.
- Synchroniczny `ActorContextProvider.get_context()` zwraca kontekst albo
  `None`. Lokalny adapter zwraca stały `local-owner`, określony w adapterze,
  nie z konfiguracji, żądania ani odpowiedzi modelu. Nie uwierzytelnia on
  przeglądarki.
- `AccessPolicy.require_owner(actor, owner_subject)` dopuszcza wyłącznie
  dokładną zgodność. Obcy lub brakujący/pusty właściciel daje `AccessDenied`,
  brak kontekstu `ActorContextUnavailable`. Właściciel ma docelowo pochodzić
  z zaufanych metadanych; referencja artefaktu nie jest uprawnieniem.
- Każda instancja aplikacji składa własny adapter i politykę, możliwe do
  podmiany. Zależność FastAPI zamienia `None` i jawny błąd niedostępności
  na HTTP 503 z kodem `actor_context_unavailable`, bez szczegółów źródła.
  Błędy podmienionego źródła nie uruchamiają lokalnego mechanizmu awaryjnego.
  Mapowanie `AccessDenied` należy do story konkretnego zasobu; nie ustalono
  wspólnej odpowiedzi 403 ani 404. Diagnostyka nie wymaga kontekstu.

Kontrakty są w płaskich modułach `application_api/identity.py` i `access.py`,
bez zależności od FastAPI; ich składanie znajduje się w `bootstrap.py`.
To fundament, nie kontrola dostępu do istniejących zasobów, pełna realizacja
AC-28 ani zabezpieczenie hostingu. Logowanie i integracje pozostają przyszłą pracą.

## 3. Zapisane kierunki technologiczne

**API projektów — uzgodnienie S2-T1 z 14 listopada 2026:**
zatwierdzono `POST /api/v1/projects` (`201`),
`GET /api/v1/projects` (`200`) i `GET /api/v1/projects/{project_id}`
(`200`). Tworzenie przyjmuje `name` i opcjonalne `description`, bez DDL.
Zatwierdzone błędy: `422` dla niepoprawnych pól, `409` dla zajętej nazwy
i `404` dla nieistniejącego projektu. Zatwierdzono również pola obiektu
projektu: `id`, `name`, `description` (opis albo `null`) i `created_at`.
Identyfikator i czas utworzenia nadaje backend; te same pola obowiązują
po utworzeniu, w odczycie projektu i w każdym elemencie listy.
Zatwierdzono format `id` jako tekstowy UUID i `created_at` jako datę
i czas ISO 8601 w UTC z końcówką `Z`. Lista ma postać `{"items": [...]}`,
obejmuje wszystkie projekty bez podziału na strony w MVP i jest sortowana
po `created_at` malejąco, przy remisie po `id` rosnąco. Brak projektów
daje `200` i `{"items": []}`. Dla błędów `422`, `409` i `404` zatwierdzono
strukturę `error` z polami `code`, `message`, `request_id`,
`automatic_retry_allowed=false` i `details`. Zatwierdzono kody
`VALIDATION_ERROR` (`422`), `PROJECT_NAME_CONFLICT` (`409`)
i `PROJECT_NOT_FOUND` (`404`) oraz `details` jako `{"fields": [...]}`
z pozycjami `field` i `message`. Konflikt wskazuje `name`, a nieistniejący
projekt daje pustą listę. Zatwierdzono ścisłą walidację wejścia:
wymagany tekst `name`, opcjonalny tekst lub `null` w `description`,
bez konwersji innych typów na tekst i bez dodatkowych pól.
Niepoprawny UUID w ścieżce również daje `422 VALIDATION_ERROR`.
Pominięty opis, `null` i pusty opis oznaczają brak opisu.
Zapis znajduje się
w [kontraktach API](lld/kontrakty_api.md).

**Doprecyzowanie S2-T1 — 14 listopada 2026:** unikalność nazw projektów
jest zatwierdzona: w danej instalacji nie dopuszczamy nazw różniących się
wyłącznie wielkością liter lub brzegowymi białymi znakami. Duplikat
powoduje czytelny błąd bez nadpisania projektu. Techniczna realizacja porównania i ograniczenia w bazie pozostaje otwarta.

| ID | Kierunek | Status i warunek |
| --- | --- | --- |
| DA-01 | Wymienność przez Ports & Adapters, wstrzykiwanie zależności i testy kontraktowe. | Zapisany kierunek. Mikroserwisy nie zastępują stabilnych kontraktów. |
| DA-02 | PostgreSQL jako podstawowy magazyn danych aplikacji i schematów. | Kierunek zachowany. Nie obejmuje archiwum wykonań ani wiadomości. Zapis roboczy wymaga przeglądu zgodnie z REQ-074: po nowym czacie, odświeżeniu lub zamknięciu strony i pełnym zamknięciu aplikacji nie przywracamy poprzedniej rozmowy i plików. Mechanizm zakończenia dostępu i fizyczne sprzątanie pozostają w OD-09. Nie oznacza współdzielenia kont i danych z walidatorem. |
| DA-03 | Oryginalny DDL oraz model strukturalny i wersje jako źródło prawdy. | Zapisany kierunek. Embedding nie zastępuje dokładnej definicji. |
| DA-04 | Bez osobnej bazy wektorowej w bazowym MVP; opcjonalnie pgvector w PostgreSQL. | Zapisany kierunek. Dodanie embeddingów po wykazaniu potrzeby, nie obowiązkowa funkcja. |
| DA-05 | Dobór kontekstu za `ContextProvider`; początkowo schemat i jawne zależności. | Zapisany kierunek. Późniejszy wariant hybrydowy nie może pomijać obowiązkowych zależności ani zmieniać zatwierdzonego zakresu. |
| DA-06 | Własny port `LlmClient` oraz `LiteLlmAdapter` wykorzystujący LiteLLM Python SDK. | Preferowany kierunek dla backendu Python. Przyjęcie zależności wymaga testów wiadomości, metryk i braku ponowień oraz przeglądu konkretnej wersji. |
| DA-07 | LiteLLM jako biblioteka w usłudze generowania, bez osobnego Proxy/Gateway. | Zapisany kierunek dla MVP. Bezpośredni adapter SDK dostawcy pozostaje rozwiązaniem zastępczym pod tym samym portem. |
| DA-08 | Nie piszemy własnych mechanizmów technicznych, jeśli pasujące rozwiązanie jest dostępne. | Zapisany kierunek: gotowe API HTTP, parser, baza, migracje, inferencja, UI i narzędzia testowe; własna semantyka produktu i integracja. |
| DA-09 | Rzeczywisty próbny import potwierdza importowalność po wstępnej kontroli składni, schematu i typów, przed dodatkowymi regułami biznesowymi. | Uzgodnione 21 października 2026; REQ-030 w specyfikacji v1.4. Szczegóły organizacji środowiska OD-02 pozostają otwarte. |

LiteLLM pozostaje zależnością warunkową. W [analizie technologii](analiza_technologii.md), sekcja 8.1, zapisano incydent łańcucha dostaw dotyczący wydań PyPI `1.82.7` i `1.82.8`, wymagania przeglądu wersji i testów. Nie przyjmujemy automatycznie żadnego wydania jako bezpiecznego.

## 4. Zatwierdzony stos i propozycje jego realizacji

Do rozpisania serwisów wykorzystujemy **wariant A: Python + FastAPI oraz TypeScript + React** z [analizy technologii](analiza_technologii.md).

**Uzgodnione 14 listopada 2026 podczas planowania S1:** użytkownik zatwierdził Python + FastAPI na backendzie oraz React + TypeScript na frontendzie jako stos do implementacji MVP. Decyzja nie oznacza akceptacji trzech osobnych serwisów, pozostałych bibliotek, wersji ani wszystkich propozycji LLD. Nie jest też twierdzeniem, że porównanie z NestJS i Django zostało zakończone prototypami; zgodność konkretnych zależności nadal wymaga sprawdzenia.

| Element | Proponowane narzędzia | Status |
| --- | --- | --- |
| Interfejs | TypeScript, React, Vite, npm; proponowane Mantine i TanStack Query. | React, TypeScript, Vite i npm zatwierdzone; biblioteki UI, obsługa danych serwera i konkretne wersje pozostają do uzgodnienia. |
| Backend zarządzający | Python, FastAPI, Pydantic, SQLAlchemy, Alembic, Psycopg. | Python, FastAPI oraz SQLAlchemy, Psycopg i Alembic dla bazy aplikacji zatwierdzone. Pydantic Settings zatwierdzono do konfiguracji backendów. Pozostałe szczegóły kontraktów i dokładne wersje wymagają uzgodnienia lub sprawdzenia. |
| Generowanie | Python, FastAPI, LiteLLM za własnym adapterem. | Python, FastAPI i osobny serwis zatwierdzone; LiteLLM pozostaje kierunkiem warunkowym DA-06. |
| Walidacja | Python, FastAPI, parser SQL, `csv`, Psycopg; proponowana osobna instancja PostgreSQL do prób. | Python, FastAPI, osobny serwis oraz metoda próbnego importu uzgodnione; pozostałe narzędzia, zakres OD-01 i organizacja OD-02 wymagają potwierdzenia. |
| Lokalny model | Ollama jako gotowe środowisko udostępniania modeli. | Preferowany kandydat, bez wyboru modelu i pobierania go. |
| Komunikacja | HTTP + JSON + OpenAPI, HTTPX po stronie klientów Python. | HTTP + JSON + OpenAPI między serwisami zatwierdzone; HTTPX i szczegóły kontraktów pozostają propozycją. |
| Uruchomienie | Docker Compose; lokalny magazyn artefaktów za adapterem. | Docker Compose zatwierdzony dla backendów i potrzebnych baz; lokalny adapter i kontrakt magazynu ustalił architekt w procesie S1-T5, zgodnie z decyzją poniżej. Implementację i testy odnotowujemy osobno. |
| Zależności i narzędzia jakości | uv, Ruff, mypy, pytest, Playwright. | uv zatwierdzone do zarządzania zależnościami i środowiskami backendów Python; pytest zatwierdzone do testów automatycznych wszystkich trzech backendów. Pozostałe narzędzia oraz wersje nadal są propozycją. |

**Osobna decyzja z 14 listopada 2026 podczas planowania S1:** użytkownik zatwierdził trzy osobno uruchamiane serwisy backendowe: zarządzanie (`application-api`), generowanie (`generation-service`) i walidację (`validation-service`), obok aplikacji przeglądarkowej. Backend zarządzający zawiera osobne moduły projektów i wykonań, a nie osobne mikroserwisy dla każdej tabeli. Ta akceptacja nie rozstrzyga sposobu lokalnego uruchomienia, bibliotek komunikacji, zabezpieczeń ani szczegółowych kontraktów usług.

**Kolejna decyzja z 14 listopada 2026 podczas planowania S1:** użytkownik zatwierdził Docker Compose jako podstawowy sposób lokalnego uruchamiania trzech serwisów backendowych i potrzebnych baz. Decyzja nie zatwierdza wersji obrazów, szczegółów sieci i wolumenów, organizacji izolowanego środowiska próbnego importu (OD-02) ani sposobu uruchamiania frontendu i lokalnego modelu.

**Decyzja z 15 listopada 2026 — lokalizacja konfiguracji S1-T3:**
główny plik Docker Compose będzie miał nazwę `compose.yaml`
i znajdzie się w katalogu głównym repozytorium. Instrukcja będzie
opisywać uruchamianie środowiska z tego katalogu. Plik nie został
jeszcze utworzony; decyzja dotyczy planu implementacji.

**Decyzja z 15 listopada 2026 — trwałość bazy aplikacji w S1-T3:**
dane PostgreSQL aplikacji przechowujemy w nazwanym wolumenie Docker.
Zwykłe zatrzymanie i odtworzenie kontenerów zachowuje wolumen i dane.
Nie rozstrzyga to magazynu plików ani trwałości środowiska próbnego
importu (OD-02). Nazwa wolumenu i punkt montowania pozostają do
określenia w konfiguracji. Nie wykonano implementacji ani testu trwałości.

**Decyzja z 15 listopada 2026 — dobór wersji obrazów S1-T3:**
deweloper dobiera i przypina dokładne wersje obrazów po sprawdzeniu
oficjalnej dokumentacji i próbie zgodności. Obowiązują Python 3.14
i Node.js 26. Upoważnienie obejmuje również wersję PostgreSQL bazy
aplikacji, bez rozstrzygania środowiska próbnego importu (OD-02).
Ewentualny konflikt wymagający zmiany ustaleń należy przedstawić
użytkownikowi przed zmianą. Dobór i weryfikacja należą do przyszłej
implementacji; nie wybrano jeszcze obrazów ani nie wykonano prób.

**Decyzja z 15 listopada 2026 — szczegóły wykonawcze S1-T3:**
deweloper dobiera nazwy sieci i wolumenu, porty wewnętrzne oraz ścieżkę
zasobów frontendu w obrazie, przy zachowaniu wszystkich zaakceptowanych
ustaleń. Te szczegóły nie wymagają osobnego zatwierdzenia. Nie jest to
zgoda na zmianę granic dostępu, kontraktów diagnostyki ani rozstrzygnięcie
OD-02. Plan etapów i zależności zapisano w S1-T3 w planie realizacji MVP;
nie rozpoczęto implementacji.

**Kolejna decyzja z 14 listopada 2026 podczas planowania S1:** użytkownik zatwierdził komunikację między serwisami przez HTTP z danymi JSON i opisem API w OpenAPI. Nie zatwierdzono tym samym konkretnych endpointów, pól, timeoutów, bibliotek klienckich ani zabezpieczeń. Decyzja nie określa sposobu przesyłania plików.

Szczegółowe funkcje, operacje, kontrakty i granice opisano w [serwisach i technologiach](serwisy_i_technologie.md).

**Decyzja z 14 listopada 2026 — dopracowanie S1-T1:** użytkownik
zatwierdził jeden wspólny układ obecnego repozytorium: frontend
w `apps/web/`, backendy w `services/application-api/`,
`services/generation-service/` i `services/validation-service/`.
Są to katalogi do utworzenia, nie istniejący kod. Akceptacja nie obejmuje
całego wewnętrznego drzewa modułów LLD ani narzędzi zarządzania
zależnościami.

**Decyzja z 14 listopada 2026 — narzędzia frontendu S1-T1:**
użytkownik zatwierdził React + TypeScript + Vite oraz npm. React służy
do budowania interfejsu, Vite do uruchamiania go podczas pracy
deweloperskiej i budowania zasobów, a npm do zarządzania pakietami
i uruchamiania poleceń projektu. Narzędzia uzupełniają się, nie zastępują
się nawzajem. Ten podział ról był podstawą akceptacji.
Decyzja nie obejmuje Mantine, TanStack Query, wersji Node.js i pakietów
ani sposobu podawania zbudowanego frontendu. Zestaw nie został jeszcze
zainstalowany ani sprawdzony w tym repozytorium.

**Decyzja z 14 listopada 2026 — zależności backendów S1-T1:**
użytkownik zatwierdził uv do zarządzania zależnościami i środowiskami
backendów Python. Wybrano je jako jeden sposób pracy z deklaracjami
zależności, plikiem blokady wersji i środowiskiem projektu, zamiast
osobnego składania obsługi `venv` i `pip`. W osobnej odpowiedzi użytkownik
zatwierdził niezależny projekt uv dla każdego z trzech backendów,
z własnymi deklaracjami zależności, plikiem blokady wersji
i środowiskiem wirtualnym, zamiast wspólnego workspace, czyli obszaru
roboczego. Zestawy bibliotek utrzymujemy osobno zgodnie z granicami
serwisów. Dokładne wersje uv i Pythona oraz pozostałe
narzędzia jakości pozostają otwarte. Nie zainstalowano ani nie sprawdzono
uv w tym repozytorium.

**Decyzja z 14 listopada 2026 — wersja Pythona S1-T1:** użytkownik
zatwierdził Python 3.14 jako bazową linię dla wszystkich trzech backendów.
Dokładne wydanie poprawkowe wymaga przypięcia po przeglądzie
i próbie zgodności wybranych zależności. Akceptacja linii 3.14 nie oznacza,
że wykonano taką próbę ani potwierdzono zgodność całego zestawu bibliotek.
Ewentualną niezgodność należy przedstawić do decyzji, nie zmieniać
samodzielnie zatwierdzonej linii.

**Decyzja z 14 listopada 2026 — środowisko frontendu S1-T1:** użytkownik
zatwierdził Node.js 26 LTS jako bazową linię środowiska narzędziowego
frontendu. Nie zastępuje ono backendów Python. Dokładne wersje Node.js,
npm i bibliotek wymagają przypięcia oraz sprawdzenia zgodności.
Nie wykonano instalacji ani próby uruchomienia zestawu w repozytorium.

**Decyzja z 14 listopada 2026 — udostępnianie frontendu S1:**
podczas zwykłego lokalnego korzystania `application-api` udostępnia
zbudowany frontend i API pod jednym adresem. Osobny serwer Vite służy
wyłącznie do pracy deweloperskiej nad frontendem; nie dodajemy osobnego
serwera frontendu do podstawowego sposobu korzystania z aplikacji.
Decyzja wpływa na S1-T1, S1-T3 i S1-T8. Nie określa konkretnych tras,
portów, konfiguracji pośredniczenia żądań w development ani zasad
obsługi brakujących zasobów. Sposób budowania obrazu rozstrzyga decyzja
z 15 listopada 2026 poniżej; zabezpieczenia pozostają do doprecyzowania.
Nie wykonano implementacji podawania frontendu przez backend.

**Decyzja z 15 listopada 2026 — budowanie frontendu w S1-T3:**
obraz `application-api` powstaje przez wieloetapowy Dockerfile.
Etap Node.js buduje frontend z `apps/web/`, a gotowe pliki trafiają
do końcowego obrazu backendu Python i są udostępniane przez FastAPI.
Nie uruchamiamy serwera Vite podczas zwykłego korzystania z tego obrazu.
Dokładne obrazy bazowe i lokalizacja plików w obrazie pozostają otwarte.
Nie wykonano implementacji ani testu budowania.

**Decyzja z 14 listopada 2026 — podział adresów w `application-api`:**
frontend udostępniamy od `/`, publiczne operacje biznesowe pod
`/api/v1`, a `/health/live` pozostaje osobną trasą techniczną.
Rozdzielamy adresy interfejsu i API bez zatwierdzania tym samym
poszczególnych operacji, pól i wewnętrznego API z projektu LLD.
Nieznany adres pod `/api/v1` zwraca HTTP 404 z odpowiedzią JSON,
nigdy stronę HTML frontendu. Nie ustalono tym samym wspólnego
formatu błędów. W początkowym szkielecie ekran startowy jest dostępny
pod `/`; nieznane adresy stron i brakujące pliki zwracają HTTP 404
zamiast strony startowej. Nie dodajemy obsługi wielu ekranów na zapas;
decyzja nie ustala docelowej nawigacji MVP.
Proxy Vite opisuje osobna decyzja poniżej.
Nie wykonano implementacji ani testów tras.

**Decyzja z 14 listopada 2026 — połączenie frontendu z API w development:**
frontend używa adresów względnych. Serwer deweloperski Vite przekazuje
żądania pod `/api/v1` oraz `/health/live` do `application-api`
na `http://127.0.0.1:8000`, bez zmiany ścieżek.
Przeglądarka nie wywołuje bezpośrednio generatora ani walidatora.
Proxy nie udostępnia wewnętrznego API. Ten układ pozwala zachować
adresy względne także przy podawaniu gotowego frontendu przez
`application-api`; Vite nie uczestniczy w zwykłym lokalnym użyciu.
Nie wykonano konfiguracji ani sprawdzenia połączenia.

**Decyzja z 14 listopada 2026 — dobór dokładnych wersji w S1-T1:**
deweloper dobiera i przypina dokładne wersje zaakceptowanych narzędzi
oraz ich wymaganych zależności w pierwszym kroku S1-T1. Najpierw
sprawdza oficjalną dokumentację, następnie zgodność przez instalację
i testy. Pozostają obowiązujące Python 3.14, Node.js 26 LTS
i zaakceptowany stos. Konflikt wymagający zmiany tych ustaleń wraca
do użytkownika przed zmianą. Nie jest to zgoda na dobieranie nowych
opcjonalnych narzędzi ani rozpoczęcie implementacji w tej konsultacji.
Dokładne wersje nie zostały jeszcze wybrane ani sprawdzone.

**Decyzja z 14 listopada 2026 — walidacja wymaganej konfiguracji S1-T2:**
użytkownik zastąpił wcześniejszą zasadę blokowania startu przy brakującej
lub błędnej konfiguracji trybem diagnostycznym. Mimo brakujących zmiennych
lub sekretów serwis udostępnia health check z przyczynami i ograniczeniami,
ale blokuje operacje biznesowe wymagające tej konfiguracji. Pozwala to
poznać problem od razu, bez odtwarzania go podczas debugowania.
Wymagalność dotyczy uruchamianego zakresu, nie kluczy niewykorzystywanych
dostawców. Raport nie ujawnia wartości sekretów. Nie jest to gwarancja
uruchomienia endpointu przy awarii samego serwera diagnostyki, np. zajętym
porcie; sposób zgłaszania takich błędów pozostaje do ustalenia.
Nie wykonano implementacji ani testów.

**Decyzja z 14 listopada 2026 — lokalne pliki konfiguracji S1-T2:**
każdy z trzech backendów ma własny lokalny `.env` z konfiguracją,
nieprzechowywany w Git, oraz wersjonowany `.env.example` z opisem
wymaganych zmiennych, bez prawdziwych sekretów. Pliki są do utworzenia
w katalogach odpowiednich serwisów. Zmienne środowiskowe przekazane
przy uruchomieniu procesu lub kontenera mają pierwszeństwo przed
wartościami z `.env`; pozwala to zmienić ustawienia bez edycji pliku.
Do odczytu i walidacji konfiguracji we wszystkich trzech backendach
zatwierdzono Pydantic Settings. Dokładnej wersji ani zgodności zależności
jeszcze nie sprawdzono. Nie ustalono nazw i pełnego zestawu zmiennych.
Konfiguracja jest wczytywana przy starcie; zastosowanie jej zmian
wymaga restartu danego serwisu. Nie dodajemy automatycznego przeładowania
`.env` podczas działania. Diagnostyka ocenia konfigurację używaną przez
uruchomiony proces, a nie nowe wartości w pliku przed restartem.
Decyzja nie wybiera konfiguracji frontendu ani niezależnego monitora.
Integracja biblioteki ma zachować tryb diagnostyczny przy błędach
konfiguracji: błędy walidacji nie mogą bez obsługi kończyć procesu.
Nie oznacza to wypełniania brakujących sekretów fikcyjnymi wartościami.
Nie utworzono plików i nie wykonano testów.

**Decyzja z 15 listopada 2026 — podłączenie konfiguracji backendów w S1-T3:**
Compose wczytuje konfigurację każdego backendu z jego osobnego,
lokalnego `.env` w katalogu serwisu, bez kopiowania tych plików do
obrazów. Zachowujemy wymagania T2 dotyczące walidacji, ochrony sekretów
i pierwszeństwa zmiennych przekazanych przy uruchomieniu kontenera.
Nie rozstrzyga to konfiguracji monitora. Organizację plików Compose
i bazy opisuje kolejna decyzja. Nie wykonano implementacji ani testów odczytu.

**Decyzja z 15 listopada 2026 — pliki konfiguracji Compose i bazy w S1-T3:**
parametry samego Compose i bazy aplikacji będą w lokalnym `.env`
w katalogu głównym repozytorium, poza Git. Towarzyszy mu wersjonowany
`.env.example` bez prawdziwych sekretów. Każdy backend zachowuje osobne
pliki konfiguracji z T2. Nie ustalono jeszcze katalogu parametrów ani
szczegółów przekazywania poświadczeń bazy do `application-api`.
Nie utworzono plików ani nie wykonano testów konfiguracji.

**Decyzja z 14 listopada 2026 — dostęp do bazy i migracje S1-T4:**
zatwierdzono SQLAlchemy i Psycopg do obsługi PostgreSQL aplikacji
w `application-api` oraz Alembic do wersjonowanych zmian struktury
tej bazy. Wybór nie dotyczy schematów DDL wgrywanych przez użytkownika
ani nie przyznaje generatorowi i walidatorowi dostępu do bazy aplikacji.
Nie zatwierdza proponowanych modeli tabel. Użytkownik wybrał automatyczne
uruchamianie migracji przy starcie `application-api`, bez wymagania
osobnej ręcznej komendy przy zwykłym uruchomieniu. Dotyczy to stosowania
przygotowanych migracji, nie ich automatycznego projektowania.
Migracje wykonujemy wyłącznie w fazie uruchamiania serwisu, także
po restarcie, nigdy podczas dalszego działania procesu.
Nie są częścią health checków,
kontroli co 30 minut ani akcji „Sprawdź teraz”.
Po błędzie migracji `application-api` pozostaje w trybie diagnostycznym,
podaje przyczynę bez wartości sekretów i blokuje funkcje wymagające bazy,
zamiast całkowicie się wyłączać. Po usunięciu przyczyny błędu kolejna
próba następuje dopiero po restarcie serwisu; nie ma samoczynnego
ponawiania w działającym procesie. Zabezpieczenie przed równoczesnym
wykonaniem pozostaje do uzgodnienia.
Dokładne wersje, zgodność z Pythonem 3.14, tryb obsługi połączeń
i transakcji oraz szczegóły konfiguracji pozostają do sprawdzenia
lub uzgodnienia. Nie zainstalowano bibliotek, nie przygotowano migracji
ani nie wykonano testów.

### Decyzje architekta z 16 listopada 2026 — realizacja S1-T4

**Status: ustalone przez rolę senior-software-architect w procesie
realizacji zadania #19.** Użytkownik delegował tej roli decyzje techniczne
w granicach zadania. Nie jest to ręczna akceptacja szczegółów przez użytkownika
ani potwierdzenie implementacji. Poniższy zapis rozstrzyga techniczne
niewiadome poprzedniej decyzji S1-T4; nie zatwierdza modeli tabel domenowych.

**Połączenia i transakcje.** Używamy synchronicznego SQLAlchemy z Psycopg 3
(`postgresql+psycopg`). Start migracji i zamknięcie zasobów wykonujemy poza
pętlą obsługi asynchronicznych żądań FastAPI; synchroniczne operacje HTTP
korzystają z jego puli wątków. To prostsze od utrzymywania dwóch trybów
połączeń dla krótkich operacji lokalnego MVP. Silnik i fabryka sesji mogą
należeć do procesu, ale sesja, transakcja i zajęte połączenie wyłącznie do
konkretnej operacji. Sukces zatwierdza zapis, błąd wycofuje transakcję,
a wyjście zawsze zamyka sesję. Nie przechowujemy jej w czacie ani podczas
wywołań LLM. Pula: najwyżej 5 połączeń, bez dodatkowych połączeń ponad limit,
oczekiwanie na połączenie 3 s, sprawdzenie połączenia przed ponownym użyciem.
Połączenie z PostgreSQL ma limit 3 s; zapytanie limit 15 s. Są to lokalne
limity techniczne T4, nie gwarancja czasu odpowiedzi całej aplikacji.

**Migracje.** Jeden przebieg `upgrade head` odbywa się raz w fazie startu.
Na tym samym połączeniu otwieramy jedną transakcję i najpierw uzyskujemy
transakcyjną blokadę doradczą PostgreSQL (`pg_advisory_xact_lock`) ze stałym,
udokumentowanym kluczem wspólnym dla wszystkich startów tej aplikacji.
Blokada obejmuje także sprawdzenie i utworzenie `alembic_version`.
Oczekiwanie na blokadę ogranicza `lock_timeout` 5 s; przekroczenie limitu
kończy tę próbę diagnostycznym błędem. Blokada zwalnia się po zatwierdzeniu,
wycofaniu albo utracie połączenia. Alembic otrzymuje istniejące połączenie
w ramach tej transakcji. Początkowa rewizja nie tworzy tabel domenowych;
zapisuje jedynie wersję mechanizmu migracji w `app.alembic_version`.
Nie stosujemy `create_all`, automatycznego projektowania migracji, `stamp`
zamiast wykonania ani migracji wymagających autocommit. Potrzeba takiej
migracji w przyszłości wymaga ponownego rozpatrzenia transakcji i blokady.
Pliki rewizji i środowisko Alembic muszą wejść również do obrazu serwisu.

**Konto i schemat.** Jedno konto `APP_DB_USER` służy w lokalnym MVP do
migracji i zwykłych operacji. To konto z hasłem, bez `SUPERUSER`, `CREATEDB`
i `CREATEROLE`, odrębne od inicjalizacyjnego `POSTGRES_USER`. Ma `CONNECT`
do bazy aplikacji oraz jest właścicielem dedykowanego schematu `app`;
nie otrzymuje administracji klastrem. Obiekty i tabela wersji powstają
wyłącznie w `app`, a połączenia jawnie wybierają ten schemat. Start sprawdza
brak tych trzech uprawnień administracyjnych i dostęp do schematu;
nie tworzy kont ani nie podnosi uprawnień. Rozdzielenie konta migracji
od konta zwykłych operacji pozostaje możliwością przed hostowaniem,
bez dodatkowego zestawu sekretów w tym zadaniu.

Inicjalizację konta i schematu zapewnia skrypt obrazu PostgreSQL, wykonywany
przez konto inicjalizacyjne tylko przy tworzeniu pustego wolumenu. Rootowy
`.env` dostarcza do niego `APP_DB_USER` i `APP_DB_PASSWORD`; plik `.env`
`application-api` zachowuje własne `APP_DB_*` z T2. Użytkownik wpisuje zgodne
wartości w obu miejscach; backend nie otrzymuje poświadczeń administratora.
Brak obu parametrów nie blokuje startu samej bazy ani diagnostyki backendu;
nie tworzy wówczas konta aplikacji. Parametry nie mogą wskazywać roli
inicjalizacyjnej. Skrypt nie zmienia hasła istniejącej roli. Dla istniejącego
wolumenu README musi podać jawną procedurę utworzenia brakującego konta
i schematu przez administratora, bez usuwania wolumenu. To przygotowanie
infrastruktury; zwykłe stosowanie migracji nadal nie wymaga ręcznej komendy.

**Diagnostyka i blokada operacji.** Zachowujemy znaczenie `/health/live`
i `/health/config`. Nowy `GET /health/database` zwraca HTTP 200 i raport
wyłącznie zależności bazodanowej, nie deklaruje gotowości całego serwisu.
Raport zawiera `service: application-api`, `dependency: database`,
`status: ready | unavailable`, `migration_status: applied | failed | not_run`,
`issues` z bezpiecznym kodem i stałym komunikatem, `blocked_capabilities`
(pusta lista albo `database`) oraz `checked_at` w UTC. Katalog kodów rozróżnia
brak konfiguracji, brak połączenia, niewłaściwe uprawnienia, przekroczenie
czasu blokady, błąd migracji i brak wymaganej wersji schematu. Nazwy pól
konfiguracji mogą być podane, ich wartości, SQL i surowe wyjątki nie trafiają
do odpowiedzi ani logów aplikacji.

Po udanym starcie każde sprawdzenie bazy wykonuje tylko odczyt kontrolny
połączenia i wersji schematu. Utrata bazy daje `unavailable`; odzyskanie
połączenia i właściwej wersji może dać `ready` bez restartu, bez migracji.
Natomiast błąd lub pominięcie migracji podczas startu jest zapamiętane do
końca procesu: samo usunięcie przyczyny i wywołanie diagnostyki nie przywraca
gotowości. Kolejna próba migracji wymaga restartu. Wspólny strażnik
`require_capabilities('database')` łączy konfigurację, wynik startu i bieżącą
niedestrukcyjną próbę bazy; zwraca 503 przed operacją wymagającą niedostępnej
bazy. Sam strażnik nie gwarantuje powodzenia późniejszego zapytania.
Pozostałe capability zachowują reguły T2. W tym zadaniu nie dodajemy
produktowego endpointu pokazującego działanie bazy ani monitora z T9.

**Weryfikacja.** Testy korzystają z jednorazowego PostgreSQL 18.7 z osobnymi
poświadczeniami, losowym portem i zasobami należącymi wyłącznie do testu.
Nie łączą się z bazą z lokalnych `.env`. Kontrolowane rewizje tworzące tabelę
lub wymuszające błąd istnieją jedynie w izolowanej kopii migracji testu.
Sprawdzamy pierwszy i kolejny start, wycofanie nieudanej rewizji, brak retry
bez restartu, równoległe starty i timeout blokady, niedestrukcyjną diagnostykę,
utratę i odzyskanie połączenia po udanym starcie, strażnik 503, sekrety,
uprawnienia oraz obecność migracji w zbudowanym obrazie. Wersje bibliotek
wykonawca dobiera po sprawdzeniu zgodności z Pythonem 3.14 i zapisuje
w deklaracji oraz blokadzie zależności. Ten zapis nie jest wynikiem testów.

Podstawy mechanizmu sprawdzono 16 listopada 2026 w oficjalnej dokumentacji:
[blokady doradcze PostgreSQL](https://www.postgresql.org/docs/18/functions-admin.html#FUNCTIONS-ADVISORY-LOCKS),
[przekazanie połączenia do Alembic](https://alembic.sqlalchemy.org/en/latest/cookbook.html#sharing-a-connection-across-one-or-more-programmatic-migration-commands)
i [cykl sesji SQLAlchemy](https://docs.sqlalchemy.org/en/20/orm/session_basics.html).
Dobór powyższych limitów, jednego konta i kontraktu diagnostyki jest decyzją
architekta dla tego projektu, nie zaleceniem ilościowym tych źródeł.

**Doprecyzowanie użytkownika z 14 listopada 2026 — diagnostyka uruchomienia:**
użytkownik wymaga sprawdzenia działania serwisów i połączeń przy
uruchamianiu, tak aby było wiadomo, które części działają.
Zatwierdzono podział odpowiedzialności: każdy backend sprawdza własne
bezpośrednie zależności, a `application-api` zbiera statusy serwisów
i własne wyniki w obraz całości. Nie wprowadzamy sprawdzania wszystkich
przez wszystkich ani rekurencyjnego pobierania zbiorczego statusu.
Użytkownik zatwierdził pozostawienie procesu uruchomionego przy
poprawnej konfiguracji i niedostępnej zależności, z diagnostyką braku
gotowości i blokadą operacji wymagających tej zależności.
Nie jest to zgoda na ponawianie generowania lub walidacji.

**Rozszerzony zakres uzgodniony w tej samej rozmowie:** health check
każdego serwisu sprawdza poprawność uruchomienia, kompletność i poprawność
wymaganych zmiennych środowiskowych oraz sekretów, poprawność połączeń
z wykorzystywanymi zewnętrznymi API, a także istnienie i dostępność
wymaganych zasobów wewnętrznych. Raport rozróżnia zdolność do działania,
częściową zdolność i całkowity brak zdolności, z wyjaśnieniem przyczyn
i ograniczeń. Sekrety nie trafiają do raportu.
Jeden wspólny mechanizm ma regularnie wywoływać health checki serwisów
także po uruchomieniu i zbierać wyniki; nie jest to tylko jednorazowy
test startu. Zatwierdzony harmonogram: przy uruchamianiu, a następnie
co 30 minut. Awaria między kontrolami może pozostać niewykryta niemal
30 minut, powiększone o czas oczekiwania na odpowiedź; jego limit
pozostaje do ustalenia. To harmonogram, nie gwarancja czasu wykrycia.
Dotychczasowy podział odpowiedzialności z `application-api`
jako agregatorem pozostaje przyjęty.

**Kolejna decyzja z 14 listopada 2026 — niezależny monitor:**
wspólny monitor działa jako osobny proces, niezależny od trzech
backendów. Sprawdza także `application-api`, aby wykrywać jego
zatrzymanie; nie może polegać wyłącznie na zbiorczym raporcie tego API.
Każdy backend nadal diagnozuje własne bezpośrednie zależności,
a `application-api` zachowuje wcześniej uzgodnioną agregację.
Nie wybrano narzędzia ani technologii monitora. Sposób uruchomienia
rozstrzyga poniższa decyzja z 15 listopada 2026.

**Decyzja z 15 listopada 2026 — uruchomienie monitora w S1-T3:**
monitor z panelem diagnostycznym będzie osobną usługą w tym samym
Docker Compose co backendy i bazy. Panel pozostaje dostępny niezależnie
od działania `application-api`. Akceptacja dotyczy sposobu uruchomienia;
technologia, obraz, porty, sieci i pozostała konfiguracja usługi
pozostają do uzgodnienia. Nie wykonano implementacji.
Osobny proces nie oznacza odporności na awarię całego hosta.

**Decyzja z 15 listopada 2026 — ekspozycja usług S1-T3:**
na hoście publikujemy wyłącznie port aplikacji (`application-api`
z frontendem) i port panelu monitora, oba na `127.0.0.1`.
Generator, walidator i baza nie mają publikowanych portów;
korzystają z połączeń wewnątrz uzgodnionych sieci Compose.
Nie przyznaje to generatorowi ani walidatorowi dostępu do bazy aplikacji.
Domyślny adres aplikacji w Compose to `http://127.0.0.1:8000`
(kolejna decyzja użytkownika z 15 listopada 2026). Domyślny adres panelu
monitora to `http://127.0.0.1:8080` (następna decyzja z tej samej daty).
Porty wewnętrzne pozostają otwarte; podział sieci opisano poniżej.
Nie wykonano implementacji ani testów ekspozycji.

**Decyzja z 15 listopada 2026 — sieć bazy aplikacji w S1-T3:**
baza aplikacji i `application-api` będą połączone osobną siecią Compose,
do której należą wyłącznie te dwie usługi. Generator, walidator
i monitor nie są do niej podłączone i nie mają bezpośredniego połączenia
z bazą. Stan zależności bazy monitor odczytuje przez diagnostykę
`application-api`, zgodnie z zasadą sprawdzania bezpośrednich zależności
przez backend. Sieć komunikacji HTTP opisuje kolejna decyzja.
Nie wykonano implementacji ani testów izolacji.

**Decyzja z 15 listopada 2026 — sieć komunikacji HTTP w S1-T3:**
druga, wspólna sieć Compose łączy trzy backendy (`application-api`,
`generation-service`, `validation-service`) i monitor. Baza aplikacji
nie jest do niej podłączona. Monitor odpytuje każdy backend niezależnie,
bez wymagania działania `application-api`. Decyzja nie rozstrzyga
środowiska próbnego importu ani kontraktów i zabezpieczeń HTTP.
Nie wykonano implementacji ani testów połączeń.

**Kolejna decyzja z 14 listopada 2026 — niezależny panel monitora:**
wyniki monitorowania są dostępne w osobnym panelu w przeglądarce.
Panel działa również przy niedostępnej głównej aplikacji, w tym
`application-api`; udostępnianie panelu i odczyt wyników nie mogą
wymagać działania tego backendu. Nie wybrano wyglądu, technologii,
adresu ani zabezpieczeń panelu. Nie oznacza to odporności na awarię
samego monitora lub całego hosta.

**Kolejna decyzja z 14 listopada 2026 — „Sprawdź teraz”:**
panel monitora udostępnia przycisk uruchamiający nową, bezpłatną
i niedestrukcyjną diagnostykę bez czekania na kontrolę okresową.
Nie jest to samo odświeżenie poprzedniego wyniku ani zgoda na płatne
próby LLM. Użytkownik doprecyzował, że ręczna kontrola nie wpływa
na harmonogram automatyczny: nie przesuwa następnej kontroli i nie
zeruje odstępu 30 minut. Nie jest to wybór konkretnego narzędzia
harmonogramowania. Obsługa jednoczesnych kontroli pozostaje otwarta.
Nie wykonano implementacji ani testów.

Nie ustalono jeszcze szczegółowej listy prób, formatu i zabezpieczenia
raportu, szczegółów prezentacji w osobnym panelu, limitów czasu, zasad
świeżości wyniku ani obsługi awarii samego monitora.
Obecność sekretu i działające połączenie nie są automatycznie dowodem
uprawnień do każdej operacji; zakres sprawdzenia danego API wymaga
konkretnej próby.

**Kolejna decyzja z 14 listopada 2026 — koszty i bezpieczeństwo prób:**
automatyczne health checki wykonują wyłącznie bezpłatne i niedestrukcyjne
próby. Sprawdzenia wymagające płatnego wywołania LLM pozostają do
ręcznego uruchomienia za zgodą użytkownika na daną próbę.
Nie zatwierdzono automatycznych płatnych wywołań ani nie wykonano
żadnej takiej próby. Konkretne sprawdzenia, sposób ręcznego uruchomienia
i potwierdzania kosztu pozostają do uzgodnienia.

Wymaga wyjaśnienia relacja z niezależnym startem szkieletów S1-T1;
nie zastąpiono po cichu wcześniejszego kontraktu `/health/live`
sprawdzaniem zależności. Zmiany zależne od tego rozstrzygnięcia
pozostają otwarte; nie wykonano sprawdzeń.

**Decyzja z 14 listopada 2026 — niezależny start szkieletów S1-T1:**
szkielety uruchamiają się bez działających baz, magazynu plików,
Ollamy i kluczy dostawców LLM. Każdy backend udostępnia wtedy
`GET /health/live` zgodnie z uzgodnionym kontraktem.
Pozwala to sprawdzić fundament niezależnie od późniejszych integracji.
Nie dodajemy atrap odpowiedzi biznesowych ani nie przedstawiamy
działania procesu jako gotowości do generowania danych.
Decyzja dotyczy zakresu S1-T1; wymagania konfiguracji rzeczywistych
integracji pozostają w odpowiednich zadaniach.
Nie sprawdzono uruchomienia ani testów aplikacji.

**Decyzja z 14 listopada 2026 — adresy deweloperskie S1-T1:**
przy bezpośrednim uruchamianiu poza Docker Compose wszystkie serwery
wiążemy z `127.0.0.1`. Domyślne porty: `application-api` — 8000,
`generation-service` — 8001, `validation-service` — 8002, Vite — 5173.
Pozwala to opisać osobne punkty sprawdzenia szkieletów na komputerze
dewelopera. Nie jest to decyzja o publikacji portów kontenerów,
sieci Compose ani konfiguracji przekazywania żądań przez Vite.
Nie uruchomiono serwerów ani nie sprawdzono dostępności tych portów.

**Decyzja z 14 listopada 2026 — serwer backendów S1-T1:** użytkownik
zatwierdził Uvicorn jako serwer uruchamiający każdą z trzech aplikacji
FastAPI. Wersja, wariant instalacji oraz parametry uruchomienia wymagają
doprecyzowania i sprawdzenia zgodności z Pythonem 3.14 oraz wybraną
wersją FastAPI. Nie zainstalowano serwera ani nie uruchomiono aplikacji.

**Decyzja z 14 listopada 2026 — minimalny frontend S1-T1:**
użytkownik zatwierdził prosty ekran techniczny z nazwą aplikacji
i informacją „Szkielet aplikacji”. Bez czatu, formularzy i logiki
biznesowej. Sprawdzenie połączenia z API należy do S1-T8.
Nie jest to projekt docelowego interfejsu ani rozstrzygnięcie OD-12.
Ekran nie został zaimplementowany.

**Decyzja z 14 listopada 2026 — minimalna struktura backendów S1-T1:**
każdy backend ma kod w `src/<pakiet>/bootstrap.py`, gdzie tworzymy
aplikację FastAPI i obsługujemy `/health/live`, oraz własny
`tests/test_health.py` z testem kontraktu. Nazwy pakietów:
`application_api`, `generation_service`, `validation_service`.
Nie tworzymy pustych warstw domeny i adapterów na zapas.
Pełne ścieżki i granicę względem proponowanego docelowego drzewa
opisuje [struktura LLD](lld/README.md#3-proponowana-struktura-kodu).
To ustalenie struktury do utworzenia, nie wykonana implementacja.

**Decyzja z 14 listopada 2026 — testy backendów S1:**
użytkownik zatwierdził pytest jako narzędzie testów automatycznych
wszystkich trzech backendów. W S1 obejmie m.in. sprawdzenie odpowiedzi
`GET /health/live` zgodnie z poniższym kontraktem, bez wywołań LLM.
Konfiguracja wspólnych zasad należy do S1-T7, a testy zachowania
szkieletów do S1-T1. Decyzja nie zatwierdza konkretnej wersji pytest,
dodatkowych bibliotek ani wtyczek. Nie zainstalowano narzędzia
ani nie wykonano testów aplikacji.

**Decyzja z 14 listopada 2026 — sprawdzenie szkieletów S1-T1:**
każdy backend udostępnia `GET /health/live`, który zwraca HTTP 200
i JSON `{"status":"ok"}`. Operacja nie wywołuje LLM, nie sprawdza baz
ani magazynów i nie ujawnia konfiguracji. Potwierdza tylko, że proces
obsłużył żądanie, nie gotowość do generowania lub walidacji.
Nie zastępuje proponowanego sprawdzenia gotowości
`GET /internal/v1/health/ready` z projektu kontraktów API.
Nie zatwierdzono tym samym mechanizmu identyfikacji instancji,
zabezpieczeń ani ekspozycji usług w sieci. Endpoint nie został
jeszcze zaimplementowany ani przetestowany.

Kolejnym poziomem jest [LLD v0.1](lld/README.md): struktura modułów, proponowane tabele i klucze, kontrakty API oraz maszyna stanów z transakcjami i fencing. To projekt do przeglądu; propozycje LP nie są nowymi zatwierdzonymi wymaganiami i nie zamykają OD.

[Projekt walidacji](lld/walidacja.md) rozróżnia potwierdzony czteroetapowy przebieg i cztery rodzaje reguł objęte MVP od niezatwierdzonej macierzy typów oraz otwartych szczegółów wykonania reguł.

### Decyzje architekta z 16 listopada 2026 — realizacja S1-T5

**Status: ustalone przez rolę senior-software-architect w procesie
realizacji zadania [#20](https://github.com/jwieczor03/mgr-llm-data-generator/issues/20).**
Użytkownik delegował tej roli decyzje techniczne w granicach zadania.
Nie jest to ręczna akceptacja szczegółów ani potwierdzenie implementacji.
Zapis rozstrzyga techniczne niewiadome szkicu T5. Nie zmienia zasad
przyjmowania paczki DDL, dostępności czatu ani fizycznego sprzątania z OD-09.

**Granica i odpowiedzialność.** W `application-api` powstaje moduł
`artifact_store.py`: niezależny od FastAPI kontrakt `ArtifactStore`,
logiczna referencja `ArtifactRef` oraz implementacja `LocalArtifactStore`.
Wykorzystujemy bibliotekę standardową Pythona 3.14, bez nowej zależności.
Lokalny adapter jest wystarczający dla jednoosobowego MVP. Magazyn sieciowy
wymagałby teraz dodatkowej infrastruktury bez wymagania produktu.
Kontrakt pozwala podstawić inną implementację bez udostępniania ścieżek
logice funkcji. Nie powstają jeszcze funkcje biznesowe używające plików.

**Minimalny kontrakt.** `put(namespace, content: bytes) -> ArtifactRef`
zapisuje niezmieniony ciąg bajtów jako nowy plik. `get(ref) -> bytes`
odczytuje cały plik; `delete(ref) -> bool` usuwa dokładnie ten obiekt,
zwracając `True`, gdy go usunięto, i `False`, gdy już nie istniał.
Przestrzenie mają zamknięte nazwy `project` (oryginały DDL) i `working`
(pliki robocze). Referencja zawiera tylko przestrzeń i kanoniczny tekstowy
UUID v4 wygenerowany przez adapter. Nie zawiera nazwy wgranego pliku,
identyfikatora właściciela ani lokalnej ścieżki. Jej poprawność sprawdzamy
również przy odczycie i usuwaniu. Nie ma operacji nadpisania, listowania,
usuwania katalogu ani sprzątania według wieku. Każdy zapis otrzymuje nową
referencję. Powiązanie z projektem, wersją schematu i czatem należy do
późniejszych funkcji; sama znajomość referencji nie nadaje praw dostępu.
Brak strumieniowania jest jawnym ograniczeniem pierwszego kontraktu,
nie limitem wielkości pliku ani akceptacją limitu uploadu S2.

**Konfiguracja i przygotowanie zasobów.** Wymagane są dwa ustawienia
wyłącznie `application-api`: `ARTIFACT_PROJECT_ROOT` i
`ARTIFACT_WORKING_ROOT`. Muszą być niepustymi bezwzględnymi ścieżkami
odrębnych katalogów; po normalizacji żaden nie może zawierać drugiego.
Zmienne procesu mają dotychczasowe pierwszeństwo przed `.env`.
Brak lub błędna wartość blokuje capability `artifacts`, zachowując HTTP,
frontend, `/health/live` i niezależną diagnostykę bazy.
Adapter nie tworzy brakujących katalogów i nie zmienia ich uprawnień.
Operator przygotowuje je przed startem; instrukcja opisuje to dla hosta.
Compose montuje tylko do API dwa nazwane wolumeny `artifact-project-data`
i `artifact-working-data` pod `/var/lib/application-api/project`
i `/var/lib/application-api/working`. Obraz przygotowuje te katalogi dla
obecnego UID/GID 10001. Zwykłe odtworzenie kontenera zachowuje oba wolumeny;
nie oznacza przywracania rozmowy ani bezterminowej retencji danych roboczych.
Generator i walidator nie otrzymują tych montowań. Komunikację plikową
między serwisami zaprojektujemy w ich właściwych zadaniach.

**Zapis i błędy.** Przed publikacją kompletna treść trafia do wyłącznie
utworzonego pliku tymczasowego w tym samym katalogu; zapis należy opróżnić
i wykonać `fsync` pliku. Dopiero później następuje atomowa publikacja
pod nowym identyfikatorem, bez zastępowania istniejącego obiektu.
W razie kolizji identyfikatora generujemy nowy, bez utraty poprzednich danych.
Nieudany zapis przed publikacją nie udostępnia częściowego obiektu ani
referencji; adapter próbuje usunąć tylko własny plik tymczasowy.
Może on pozostać po nagłym zabiciu procesu lub błędzie sprzątania;
nie jest dostępny przez referencję. Nie dodajemy skanowania i kasowania
pozostałości przy starcie. Publikacja jest punktem sukcesu zapisu;
niepowodzenie usunięcia pomocniczej nazwy już po publikacji nie wycofuje
kompletnego obiektu. Nie deklarujemy odporności na awarię całego dysku.
Atomowość dotyczy pojedynczego pliku, nie transakcji paczki DDL i bazy S2.
Usuwanie działa pojedynczo, bez automatycznych ponowień i bez rekurencji.

Błędy kontraktu mają stałe kody bez surowej treści wyjątku systemowego:
`invalid_reference`, `not_found`, `permission_denied`, `missing_root`,
`invalid_resource` (np. katalog lub dowiązanie zamiast pliku) i `io_error`.
`get` brakującego obiektu zgłasza `not_found`; `delete` tego samego obiektu
jest idempotentne według wyniku `False`. Brak korzenia nie jest brakiem
obiektu i nie może dać fałszywego sukcesu usunięcia. Błąd dostępu lub I/O
zachowuje dotychczasowe obiekty i jest błędem technicznym, bez retry.
Publiczny komunikat, diagnostyka i zwykły zapis błędu nie ujawniają
fizycznych ścieżek, treści plików ani konfiguracji.

**Granica bezpieczeństwa.** Jedyny segment nazwy obiektu pochodzi ze
sprawdzonego UUID, nie z danych klienta/modelu. Operacje nie podążają
za dowiązaniami symbolicznymi korzenia ani obiektu; sprawdzają, że obiekt
jest zwykłym plikiem. Operacje względem otwartego katalogu i `O_NOFOLLOW`
pozwalają uniknąć podmiany ścieżki pomiędzy sprawdzeniem a użyciem.
Przodkowie ścieżki konfiguracyjnej są zaufaną konfiguracją operatora
(np. systemowe `/tmp` może wskazywać `/private/tmp` na macOS).
MVP wspiera tu POSIX: Linux w Compose i macOS dewelopera. Nie obiecujemy
odporności na administratora hosta ani inny proces działający jako ten sam
użytkownik i celowo modyfikujący prywatny magazyn. Katalogi nie są
statycznie publikowane; T5 nie tworzy HTTP do odczytu ani zapisu plików.
Kontrola własności zasobu pozostaje po stronie przyszłego wywołującego
kodu aplikacji i T6, a nie wewnątrz adaptera systemu plików.

**Diagnostyka i blokada operacji.** `GET /health/artifacts` zwraca HTTP 200
z `service: application-api`, łącznym `status: ready|unavailable`,
`blocked_capabilities` (puste albo `artifacts`) oraz odrębnym wynikiem
`project` i `working` (`status: ready|unavailable`, `code: null|kod`).
Dla braku/błędu konfiguracji kod to `configuration_unavailable`;
pozostałe kody wynikają z kontraktu powyżej. Raport nie pokazuje ścieżek.
Sprawdzenie tworzy, zapisuje, odczytuje i usuwa wyłącznie własny plik próbny,
sprawdzając rzeczywisty dostęp zamiast samych bitów uprawnień.
Nie modyfikuje istniejących artefaktów i nie tworzy brakujących katalogów.
Odtwarzamy probe przy każdym wywołaniu; po przywróceniu zasobu kolejny
raport i operacja mogą działać bez restartu. Zmiana samej konfiguracji
nadal wymaga restartu. Strażnik `require_capabilities("artifacts")`
odrzuca operacje zależne kodem 503 (`configuration_unavailable` albo
`artifacts_unavailable`). Nie dodajemy w T5 biznesowego endpointu tylko
na potrzeby pokazania tej blokady; test może zarejestrować własną trasę.

**Dowody i ograniczenia.** Wykonawca sprawdzi kontrakt na katalogach
tymczasowych, niepełny zapis i błąd usuwania, niezmienność starych obiektów,
symlinki, błędne referencje, brak korzenia, odmowę dostępu oraz odzyskanie
dostępności. Test rzeczywistych kontenerów sprawdzi uprawnienia UID 10001,
oba wolumeny po odtworzeniu API i brak ich montowania innym serwisom.
Odmowę dostępu należy sprawdzić w procesie bez uprawnień administratora
albo przez kontrolowane wstrzyknięcie błędu systemowego, opisując różnicę.
Nie implementujemy harmonogramu kasowania, rozliczania właścicieli,
przyjmowania DDL ani eksportu. OD-09 pozostaje otwarte w swoim zakresie.

Źródła techniczne sprawdzone 16 listopada 2026: dokumentacja Python 3.14
[`os`](https://docs.python.org/3.14/library/os.html) — operacje względem
katalogu, `link`, `replace`, `fsync`, `O_NOFOLLOW`; oraz
[`tempfile`](https://docs.python.org/3.14/library/tempfile.html) — bezpieczne
tworzenie plików tymczasowych i ograniczenia sprzątania po zabiciu procesu.
To podstawa doboru mechanizmów; działanie adaptera potwierdzą testy zadania.

### Decyzje architekta — realizacja S1-T7

**Status: ustalone przez rolę architekta w procesie zadania [#22](https://github.com/jwieczor03/mgr-llm-data-generator/issues/22).** Nie jest to ręczny odbiór użytkownika.

Zachowujemy trzy osobne środowiska uv i npm frontendu. Ruff 0.15.13
sprawdza E4, E7, E9, F i I dla Python 3.14 we wspólnej konfiguracji;
nie uruchamiamy globalnego formatowania. Pytest ma jawny katalog testów,
ścisłe markery i osobne uruchomienia. Frontend korzysta z istniejącego
ścisłego TypeScript oraz kontroli nieużywanych deklaracji, Vitest 4.1.12,
jsdom 29.0.0 i React Testing Library. Test ekranu w jsdom nie jest testem
rzeczywistej przeglądarki. Wspólny skrypt zatrzymuje się przy błędzie;
integracje bazy i Compose uruchamia się jawnie, na izolowanych zasobach.
Nie dodajemy mypy, ESLint, Prettier, Playwright, coverage, xdist ani CI.

Podstawy doboru: [Ruff](https://docs.astral.sh/ruff/configuration/),
[Vitest](https://vitest.dev/guide/), [środowiska Vitest](https://vitest.dev/guide/environment),
[Testing Library](https://testing-library.com/docs/react-testing-library/intro/),
[markery pytest](https://docs.pytest.org/en/stable/how-to/mark.html) i
[tmp_path](https://docs.pytest.org/en/stable/how-to/tmp_path.html).

## 5. Co nadal jest otwarte

**Doprecyzowanie S2 — 14 listopada 2026:** zatwierdzono również obsługę
wielokolumnowych `PRIMARY KEY`, `FOREIGN KEY` i `UNIQUE` w DDL
(sekcja 5.1 specyfikacji). Poniższy otwarty zakres OD-01 nie obejmuje
ponownego wyboru tej postaci kluczy; pozostałe warianty ograniczeń
nadal wymagają uzgodnienia.

**Kolejne doprecyzowanie S2 — 14 listopada 2026:** zatwierdzono zakres
`CHECK`: porównania, zakresy (`BETWEEN`), zbiory wartości (`IN`),
`AND`, `OR` i `NOT` w obrębie rekordu, bez wywołań funkcji.
Potwierdzono niezależność od dziedziny projektu (np. bankowość, sklep,
e-commerce): strukturę i ograniczenia odczytujemy z DDL, bez stałego
katalogu nazw tabel, kolumn i wartości. Szczegóły zapisano w sekcji 5.1
specyfikacji. Nie zatwierdzono przez to całego OD-01.
Następnie zatwierdzono `DEFAULT` obejmujące stałe zgodne z obsługiwanymi
typami oraz `CURRENT_DATE` i `CURRENT_TIMESTAMP`, bez innych wywołań
funkcji i dowolnych wyrażeń.

**Automatyczne ID — uzgodnienie S2 z 14 listopada 2026:** obsługiwany
DDL obejmuje `serial`, `bigserial`, `GENERATED BY DEFAULT AS IDENTITY`
i `GENERATED ALWAYS AS IDENTITY`. Użytkownik zatwierdził również jawne
ID przygotowywane przez model w paczce, wraz z powiązaniami rekordów,
także dla tych kolumn. Szczegóły importu SQL/CSV i obsługa sekwencji
nadal wymagają uzgodnienia i próby technicznej.
Nie rozszerza to ogólnej listy wyrażeń `DEFAULT` ani nie zezwala na
modyfikowanie DDL użytkownika.

1. **OD-01 — częściowo rozstrzygnięte:** kolumny `json`/`jsonb` w schematach użytkownika są poza MVP, a proste hierarchie rekordów w jednej tabeli należą do MVP. Podczas planowania S2, 14 listopada 2026, zatwierdzono typy: `smallint`, `integer`, `bigint`, `numeric`/`decimal` z precyzją i skalą, `text`, `varchar` z długością, `boolean`, `uuid`, `date`, `timestamp` i `timestamptz` (sekcja 5.1 specyfikacji). Pozostałe konstrukcje DDL, postacie ograniczeń i wyrażeń, automatyczne identyfikatory oraz wersja dialektu wymagają uzgodnienia.
2. **OD-02 — częściowo rozstrzygnięte:** mechanizmem jest rzeczywisty próbny import do pustego, odizolowanego PostgreSQL. Otwarte pozostają wersja silnika, profil transakcji, provisioning, role i dokładna organizacja zasobów.
3. **OD-03 — zamknięte:** wybieramy najnowszego kandydata spełniającego wszystkie obowiązkowe warunki, bez rankingu jakości. Ten punkt nie blokuje już implementacji.
4. **OD-04–OD-06:** dokładny profil SQL/CSV, raport, wykonywalna postać reguł oraz ich prezentacja do zatwierdzenia.
5. **OD-07–OD-09:** wartości timeoutów, szczegóły anulowania, dostępność niesprawdzonych artefaktów i fizyczne sprzątanie. W dostępnym czacie sprawdzoną paczkę można pobrać po anulowaniu lub błędzie bez zmiany statusu. Dostęp kończy się po nowym czacie, odświeżeniu lub zamknięciu strony i pełnym zamknięciu aplikacji; przed odświeżeniem lub zamknięciem strony wymagane jest ostrzeżenie (REQ-074–REQ-075). Opuszczenie czatu ma anulować trwające wykonanie (REQ-077). Otwarte pozostają techniczne wykrycie wyjścia, przekazanie anulowania i moment potwierdzenia zatrzymania, mechanizm zakończenia dostępu, sprzątanie oraz usuwanie projektów.
6. **OD-10–OD-12:** uzgodniono czat, zmianę poprzedniej paczki przez LLM i osobny limit napraw dla każdej nowej prośby (REQ-033–REQ-034, REQ-073, REQ-076). Po nieudanej zmianie zachowujemy poprzednią paczkę, a dodatkowe 3 rundy wymagają ręcznej akcji (REQ-078–REQ-079). Nadal otwarte są przypisanie prośby i serii do wykonania oraz liczników, kontrakt plików i obsługa ograniczeń kontekstu oraz pozostałe szczegóły UI. Warianty badawcze, modele i sprzęt należą do osobnej pracy badawczej.
7. Parser: SQLGlot jako pierwszy kandydat do próby; pglast tylko po ocenie zgodności i licencji.
8. Wykonawca długich operacji: ograniczony lokalny wykonawca za portem `ExecutionRunner`; gotowe narzędzie dopiero, jeśli zmniejszy nakład i spełni zasady braku retry i wznowień.
9. Konkretne wersje języków, bibliotek i obrazów; pliki blokad oraz przegląd bezpieczeństwa i licencji.

Nie zamykamy tych punktów samym wyborem frameworka. Pełna lista znaczeń OD pozostaje w specyfikacji.

## 6. Co zostało wykonane

Istnieją szkielety backendów i frontendu oraz konfiguracja T2. W S1-T3
zbudowano obrazy, uruchomiono izolowane środowisko Compose i PostgreSQL
oraz sprawdzono podstawowy zakres testami. W S1-T4 zaimplementowano
i przetestowano dostęp do bazy oraz migracje; ręczny odbiór pozostaje
oddzielnym krokiem. Nie dostarczono jeszcze funkcji generowania ani
monitora T9. Nie wykonywano płatnych
wywołań modeli. Kontrola frontendu w przeglądarce pozostaje niewykonana
z powodu braku dostępnego narzędzia i uprawnień Computer Use.
