# Zasady pracy nad projektem

## Zamysł projektu

Budujemy aplikację wykorzystującą LLM do przygotowywania syntetycznych danych
testowych na podstawie struktury danych, reguł biznesowych i poleceń użytkownika.
Projekt obejmuje również badania do pracy magisterskiej nad skutecznością
takich rozwiązań. Rozwój aplikacji i wnioski naukowe to odrębne rezultaty.

## Gdzie szukać aktualnych ustaleń

- [README](README.md) jest punktem wejścia do dokumentacji i opisu stanu projektu.
- Wymagania i kryteria akceptacji odczytuj z aktualnej
  [specyfikacji](docs/specyfikacja_mvp.md), a status decyzji technicznych
  z [rejestru ustaleń](docs/ustalenia_architektoniczne.md) i powiązanej dokumentacji.
- Przy pracy badawczej odczytaj [plan badań](docs/plan_badan.md) oraz istniejące
  protokoły i wyniki. Propozycja eksperymentu nie jest wymaganiem aplikacji.
- Ten plik nie ustala technologii, architektury ani szczegółowych reguł produktu.
  Nie kopiuj ich tutaj ze specyfikacji. Ustalenia mogą się zmieniać; przed pracą
  sprawdź bieżące źródła zamiast polegać na wcześniejszym podsumowaniu lub czacie.
- Rozróżniaj zaakceptowane decyzje, propozycje, historyczne notatki i rzeczywisty
  stan implementacji. Przy istotnej sprzeczności wskaż ją użytkownikowi
  i uzgodnij rozstrzygnięcie, zamiast wybierać wersję po cichu.

## Współpraca

- Rozmawiaj i dokumentuj po polsku, chyba że użytkownik wskaże inaczej.
- Korzystaj z ról opisanych w [.agents/skills](.agents/skills).
  Wczytuj tylko skill i referencje potrzebne do zadania; nie powielaj tutaj
  ich szczegółowych procedur. Dodatkowych agentów uruchamiaj tylko na zlecenie.
- Pracuj w uzgodnionym zakresie. Nie rozstrzygaj niejasności samodzielnie
  ani nie rozszerzaj zadania pod pozorem szczegółów wykonania.
- Ustalenia zapisuj we właściwej dokumentacji, a stan prac w istniejącym planie
  lub zadaniu. Nie twórz konkurencyjnych źródeł prawdy. Przy kontynuacji najpierw
  odczytaj zapisany stan; aktualizację wymagań uzgodnij z użytkownikiem.

## Niejasności i decyzje

- Zasada obowiązuje wszystkie role i na każdym etapie: od planowania
  i projektowania przez implementację i review po badania.
- Najpierw sprawdź dostępne źródła i wcześniejsze ustalenia. Jeśli nadal
  czegoś nie wiadomo, brakuje decyzji lub materiały są sprzeczne, zapytaj
  użytkownika przed podjęciem zależnej decyzji lub wykonaniem zmiany.
- Nie zastępuj odpowiedzi własnym założeniem, domyślnym wariantem ani typową
  praktyką. Możesz przedstawić propozycję i rekomendację z uzasadnieniem,
  ale nie traktuj ich jako zaakceptowanego rozwiązania. Milczenie nie jest zgodą.
- Zadawaj **jedno pytanie naraz** i poczekaj na odpowiedź przed kolejnym.
  Nie wysyłaj listy pytań ani nie łącz kilku niezależnych decyzji w jednym pytaniu.
  Wyjaśnij krótko, czego nie wiadomo i na co wpłynie odpowiedź. Do rozstrzygnięcia
  oznacz kwestię jako otwartą i wstrzymaj zależną pracę; możesz kontynuować
  niezależny, uzgodniony zakres.
- Każda rola może korzystać z dostępnego skilla `$grilling`, aby sprawdzić
  założenia i wspólnie doprecyzować decyzje w zakresie zadania. W tym projekcie
  stosuj go w trybie **jedno pytanie → odpowiedź użytkownika → kolejne pytanie**,
  zamiast opisanych w nim rund z wieloma pytaniami. Nie przejmuj decyzji
  użytkownika. Użycie skilla nie oznacza zgody na uruchamianie dodatkowych agentów.
- Nie pytaj ponownie o jednoznacznie zapisane ustalenia bez nowej sprzeczności.
  Jasno zlecone czynności wykonuj bez wymagania zgody na każdy krok.

## Prosta i zrozumiała dokumentacja

- Pisz dla użytkownika projektu, nie tylko dla specjalisty. Zaczynaj od
  krótkiego wyjaśnienia: czego dotyczy dokument i co czytelnik powinien wiedzieć.
- Używaj prostego języka, krótkich zdań, opisowych nagłówków i niewielkich
  sekcji. Listy, małe tabele i przykłady dodawaj wtedy, gdy pomagają zrozumieć treść.
- Wyjaśniaj potrzebne terminy techniczne i skróty przy pierwszym użyciu.
  Nie zastępuj wyjaśnienia samą nazwą narzędzia, wzorca lub angielskim żargonem.
- Jasno oddzielaj: **ustalone**, **propozycja** i **do wyjaśnienia**.
  Rozróżniaj planowane działanie od tego, co rzeczywiście zaimplementowano,
  sprawdzono lub zaobserwowano w badaniach.
- Po zmianie ustaleń aktualizuj dotknięte opisy i odnośniki. Czytelnik powinien
  móc ustalić, co obowiązuje, dlaczego i co pozostaje otwarte, bez odtwarzania czatu.
- Zachowuj informacje potrzebne do użycia, weryfikacji i zrozumienia ograniczeń.
  Prostota nie oznacza pomijania ważnych szczegółów ani mnożenia dokumentów.

## Implementacja, review i odbiór

- Deweloper odpowiada za realizację konkretnego zadania i adekwatne testy.
- Reviewer sprawdza jakość oraz zgodność implementacji z zadaniem dewelopera
  i jego kryteriami. Gdy nie zna zadania, prosi o brakujące źródło i nie deklaruje
  pełnej zgodności na podstawie samego kodu.
- Ręczna weryfikacja aplikacji i końcowy odbiór należą do użytkownika.
  Nie dodajemy osobnej roli QA. Review nie zastępuje odbioru, a odbiór
  użytkownika nie zwalnia dewelopera z testowania własnej zmiany.
- Przy przekazaniu podaj wykonany zakres, źródło zadania, zmienione artefakty,
  rzeczywiste wyniki sprawdzeń, ograniczenia i następny krok. Do odbioru
  przygotuj konkretne kroki ręcznej weryfikacji.
- Nie przedstawiaj planowanych testów jako wykonanych, propozycji jako decyzji
  ani hipotez jako wyników badań. Komendy i sposób uruchomienia sprawdzaj
  w bieżącej konfiguracji.

## Granice działań

Publikację, operacje Git, wdrożenia i płatne eksperymenty wykonuj wyłącznie
w zakresie zlecenia. Nie ujawniaj sekretów ani nie wysyłaj prywatnych danych
poza uzgodniony zakres. Zmiany w skillach tego repozytorium nie oznaczają
zgody na zmianę ich globalnych kopii.
