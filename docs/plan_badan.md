# Plan badań — porównanie LLM w generowaniu danych testowych

Ten dokument opisuje, czego chcemy dowiedzieć się w pracy magisterskiej.
Aplikacja jest narzędziem pomocniczym do badań, a nie ich głównym rezultatem.

**Aktualizacja:** 15 listopada 2026.  
**Status:** cel, główne pytanie i ogólne ramy porównania uzgodniono z autorem
14–15 listopada 2026. Pytania szczegółowe pozostają robocze.
Osobne porównanie technik promptowania jest poza głównym zakresem.
Szczegółowy protokół ustalimy po uzyskaniu aplikacji, przed właściwymi pomiarami.  
**Własne eksperymenty i wyniki:** jeszcze ich nie przeprowadzono.

Plan nie zmienia [specyfikacji MVP](specyfikacja_mvp.md), czyli wymagań
podstawowej wersji aplikacji. Aktualny etap wskazuje
[stan badań](../badania/stan-badan.md). Wcześniejsza
[ocena koncepcji](../badania/ocena-koncepcji.md) i
[rozeznanie literatury](../badania/literatura.md) są materiałami pomocniczymi,
nie zatwierdzonym protokołem ani dowodem nowości pracy.

## 1. Cel i główne pytanie

**Ustalone:** porównujemy modele językowe (LLM) w generowaniu złożonych
relacyjnych danych testowych przy wsparciu deterministycznego walidatora.
Taki walidator sprawdza dane według jednoznacznych reguł, nie na podstawie
opinii kolejnego modelu.

**Główne pytanie zaakceptowane przez autora 15 listopada 2026:**

> Jak dobór modelu LLM i organizacja procesu generowania wpływają
> na poprawność, czas i koszt tworzenia złożonych danych testowych —
> przy generowaniu bezpośrednim oraz ze wsparciem aplikacji
> z deterministycznym walidatorem?

Nie zakładamy z góry przewagi droższych modeli, aplikacji ani zespołów
agentów. Wyniki mają dotyczyć faktycznie zbadanych modeli i zadań,
nie wszystkich możliwych LLM.

## 2. Co generujemy

Na wejściu są wyłącznie:

- DDL, czyli definicje tabel, kolumn i ograniczeń bazy danych;
- oryginalne polecenie użytkownika;
- jego reguły biznesowe.

Nie ma istniejących rekordów ani przykładowego zbioru wejściowego.
Potrzebne dane, również w tabelach powiązanych, trzeba wygenerować.
W kontekście obecnej aplikacji pracujemy z PostgreSQL, z wynikiem
w postaci poleceń `INSERT` albo CSV. Konkretny format prób wybierzemy później.

**Złożoność** dotyczy prostszych i trudniejszych schematów oraz konieczności
przygotowania spójnych danych w wielu powiązanych tabelach.
Przykład autora: schemat sklepu ma 50 tabel, a polecenie dotyczy
100 zamówień. Wynik obejmuje zamówienia oraz potrzebne rekordy powiązane,
niekoniecznie dane we wszystkich 50 tabelach. Liczby ilustrują zamysł,
nie są jeszcze obowiązkowym scenariuszem ani granicą trudności.

Schematów autor planuje poszukać na GitHubie, ewentualnie część wygenerować.
Nie wybrano repozytoriów ani sposobu generowania przykładów.
W tej rozmowie nie przeprowadzono ich wyszukiwania.

## 3. Porównywane modele i procesy

### Modele

Zakres obejmuje modele tańsze, droższe oraz modele o otwartych wagach.
Mogą być dostępne przez API albo uruchamiane lokalnie. Nie wymagamy
uruchomienia każdego modelu na oba sposoby.

Cena, dostępność wag, środowisko i podział na role to różne cechy.
Na przykład otwarte wagi nie oznaczają obowiązkowo lokalnego wykonania.
Konkretne modele, wersje i środowiska wybierzemy później.

### Trzy sposoby realizacji zadania

| Wariant | Uzgodniony zakres |
| --- | --- |
| Czysty LLM | Pełny DDL, oryginalne polecenie i reguły; jedno wywołanie, bez poprawek i bez kontekstu dodatkowo przygotowanego przez aplikację. |
| Aplikacja bez podziału na agentów | Ten sam model realizuje zadanie w procesie aplikacji, z przygotowaniem kontekstu, walidacją i poprawkami. Wiele wywołań nie oznacza wielu agentów. |
| Aplikacja z podziałem na role | Ten sam model wykonuje różne zadania jako planista, wykonawca i reviewer. Szczegóły opisuje sekcja 4. |

Każdy wybrany model porównujemy bez aplikacji oraz w jej procesie bez
podziału na agentów: model A z jego własnym odpowiednikiem, analogicznie B.
W procesie wieloagentowym nie mieszamy obecnie różnych modeli.

Wynik czystego LLM również ocenia deterministyczny walidator, ale dopiero
po generowaniu, bez przekazywania modelowi błędów do naprawy.
To ocena wyniku, a nie wsparcie generowania.

Badamy całe sposoby realizacji zadania. Aplikacja wnosi nie tylko walidację,
ale też przygotowanie kontekstu i organizację procesu. Różnicy wyników
nie można przypisać wyłącznie walidatorowi. Większą liczbę wywołań aplikacji
uwzględniamy w całkowitym czasie i koszcie. Nie ustalono jeszcze dokładnej
zawartości jej dodatkowego kontekstu.

## 4. Role i ograniczona pętla poprawek

**Ustalone role:** planista, wykonawca i reviewer, czyli recenzent,
korzystający z tego samego modelu do różnych zadań.

Reviewer wyłącznie ocenia wynik i przekazuje ocenę wykonawcy.
Sam nie zmienia danych; poprawki wykonuje wykonawca.
Uzgodniono maksymalnie **3 rundy poprawek po pierwszym generowaniu**.
Ocena reviewera nie oznacza jeszcze ustalonej punktacji liczbowej.

Reviewer nie zastępuje deterministycznego walidatora. Jego pozytywna
opinia nie wystarcza do uznania pełnego sukcesu badawczego.

Szczegółowe obowiązki, kontekst ról, komunikacja, miejsce walidacji w pętli,
sposób liczenia rund i wcześniejszego zakończenia zostają do dopracowania
po uzyskaniu aplikacji. Nie ustalamy ich teraz.

## 5. Poprawność, czas i koszt

### Pełny sukces badawczy

Wynik musi jednocześnie:

- być kompletny względem zatwierdzonego scenariusza i jego liczebności;
- nadawać się do importu;
- zachowywać wszystkie wymagane relacje;
- spełniać wszystkie reguły biznesowe scenariusza sprawdzane deterministycznie.

Wspólna interpretacja oczekiwanego wyniku jest punktem odniesienia do oceny.
Nie oznacza to identycznie rozbudowanego kontekstu wejściowego w wariantach.
Głównym przedmiotem są błędy generowania, nie osobne badanie rozumienia.

To kryterium jest surowsze od statusu wykonania zadania w aplikacji,
który dopuszcza naruszenia dodatkowych reguł biznesowych.
Plan badań nie zmienia statusów ani wymagań MVP.

### Główne obszary oceny

| Obszar | Co chcemy porównać |
| --- | --- |
| Poprawność | Uzyskanie pełnego sukcesu oraz liczba i rodzaje błędów w wynikach częściowych. |
| Czas | Czas całego badanego procesu, z pracą ról i poprawkami, nie tylko ostatnią odpowiedź modelu. |
| Koszt | Nakład wszystkich wywołań procesu, nie tylko wywołania końcowego; sposób uwzględnienia wykonania lokalnego ustalimy później. |

Dokładne mierniki, jednostki, granice pomiarów i obsługa brakujących danych
należą do późniejszego protokołu. Braku pomiaru nie przedstawiamy jako zera.

### Obserwacje poboczne

Realizm danych i rozumienie zadania mogą zostać omówione, jeśli podczas prób
pojawią się warte opisania przypadki. Nie są osobnymi obowiązkowymi badaniami,
głównymi miernikami ani warunkami pełnego sukcesu. Nie ustalono osobnego
badania różnorodności. Zgodność z walidatorem nie dowodzi realizmu.

## 6. Oczekiwany rezultat pracy

**Uzgodnione 15 listopada 2026:** wynikiem mają być rekomendacje i opis
kompromisów między poprawnością, czasem i kosztem, a nie wymuszony jeden
zbiorczy ranking. Chcemy wskazać, które modele i procesy są korzystne
przy różnych priorytetach i poziomach trudności zadań.

Może się okazać, że jeden wariant jest skuteczniejszy, a inny tańszy lub
szybszy. To możliwy wynik, nie przyjęta hipoteza o konkretnych modelach.
Nie ustalamy wspólnej punktacji ani wag po to, aby wskazać zwycięzcę.

Opis aplikacji wyjaśnia narzędzie badawcze. Wnioski wymagają pomiarów,
analizy i wskazania ograniczeń; liczba funkcji ani agentów ich nie zastępuje.
[Wstępne rozeznanie literatury](../badania/literatura.md) nie wykazało nowości
projektu. Nie przedstawiamy samej pętli poprawek jako nowego odkrycia.

## 7. Robocze pytania szczegółowe

Poniżej zachowano identyfikatory z wcześniejszego planu. Brzmienie pytań
jest robocze; tabela nie zatwierdza dodatkowych eksperymentów.

| ID | Pytanie i jego obecny status |
| --- | --- |
| PB-01 | Jak badane modele radzą sobie z uzyskaniem kompletnych i importowalnych paczek dla powiązanych tabel? Kierunek uzgodniony; dopracowanie pytania powinno objąć także wszystkie deterministycznie sprawdzane reguły sukcesu. |
| PB-02 | Jak zmiana promptów wpływa na wynik procesu, zgodność biznesową i nakład poprawek? Wcześniejsza propozycja; decyzją autora z 15 listopada 2026 osobne porównanie technik promptowania pozostaje poza głównym zakresem. |
| PB-03 | Czy rozdzielenie odpowiedzialności między role daje korzyść względem prostszego procesu? Kierunek uzgodniony; uwzględniamy też czas i koszt ról. |
| PB-04 | Jak zakres pomocy deterministycznej zmienia skuteczność i charakter zadania? Wcześniejsze szerokie pytanie; obecnie wybrano porównanie całej aplikacji z czystym LLM, nie izolowany pomiar walidatora lub kodu pomocniczego. |
| PB-05 | Jak wyniki różnią się między schematami o różnej liczbie tabel i strukturze powiązań oraz zadaniami o różnym zakresie danych? Kierunek porównania prostszych i trudniejszych schematów jest uzgodniony; konkretne poziomy i scenariusze pozostają otwarte. |

Prompty przygotujemy jako część porównywanych procesów, nie jako osobną oś
eksperymentów. Różnice promptów między procesami należą do opisu wariantów;
nie wyprowadzamy z takiego porównania osobnych wniosków o przewadze technik
promptowania.

## 8. Co dopracujemy po uzyskaniu aplikacji

Na prośbę autora odkładamy szczegółowy protokół, m.in.:

- konkretne modele, wersje, ustawienia i dostępne środowiska;
- schematy, reguły, scenariusze, poziomy trudności i format wyników;
- prompty, dodatkowy kontekst oraz dokładny przebieg pracy ról;
- powtórzenia, kolejność prób, limity czasu, kosztu i wywołań;
- definicje mierników, obsługę niepowodzeń i sposób analizy;
- zapis materiałów pozwalających odtworzyć próbę.

Szczegóły trzeba ustalić przed właściwymi pomiarami porównawczymi,
ale ich brak nie blokuje obecnej koncepcji. Termin, budżet i formalne
wymagania uczelni nie zostały podane. Wskazany cel pracy pozostaje aktualny;
nie traktujemy braku odrębnego formalnego tytułu jako blokady rozmowy.

Organizacja badań pozostaje poza aplikacją. MVP nie zapewnia historii
wykonań, czatów ani pełnego archiwum promptów. Autor musi zachować materiały
poza generatorem przed utratą dostępu do bieżącego czatu; dokładny sposób
zdecydujemy później. Plan nie dodaje panelu badawczego, automatycznych serii
prób ani obowiązkowego systemu archiwizacji do MVP.

## 9. Wcześniejsze pomysły i materiały pomocnicze

Poniższe hipotezy zachowano z planu uporządkowanego 20 października 2026.
Nie są wynikami ani dodatkowymi obowiązkowymi eksperymentami.

| ID | Zachowany pomysł i ograniczenie |
| --- | --- |
| H-01 | Planowanie, generowanie i recenzja mogą ograniczać naruszenia. Wybrano takie role do porównania, ale ich przewagi jeszcze nie sprawdzono. |
| H-02 | Przygotowanie identyfikatorów i powiązań poza LLM może pomagać. Nie wybrano tego wariantu; zmieniałby zakres pracy modelu. |
| H-03 | Część prostych wartości może powstawać deterministycznie. To niezatwierdzony wariant; nie zmienia wymogu gotowego SQL/CSV zwracanego przez LLM w MVP. |
| H-04 | Dodatkowy recenzent może pomagać przed niezależnym sprawdzeniem wyniku. Reviewer jest wybraną rolą, nie gwarancją poprawy. |

Modele mieszane w jednym zespole, fine-tuning, chmura AWS, zależności kołowe,
Faker i automatyczna ocena realizmu nie stają się wymaganiami badania.
Ewentualne rozszerzenie wymaga odrębnego uzgodnienia.

Źródła wcześniejszych pomysłów:

- [Strategia modeli](archiwum/2026-10-20/koncepcje/strategia_modeli_ai.md) — podział ról i modele lokalne oraz API.
- [Wybór LLM](archiwum/2026-10-20/koncepcje/wybor_llm.md) — historyczny opis sprzętu, nie potwierdzenie jego dostępności do prób. Zapis „16GB Shared” nie oznacza dodatkowej dedykowanej pamięci GPU; nie przyjmujemy limitu 8 mld parametrów dla wszystkich modeli.
- [Notatki](archiwum/2026-10-20/koncepcje/pomysly_notatki.md) — identyfikatory, pomoc deterministyczna i pytania do ewentualnego partnera biznesowego.
- [Architektura](archiwum/2026-10-20/dev/architektura.md) — oddzielenie generowania i sprawdzania.

Jeśli materiały będą pochodziły od firmy, trzeba wcześniej ustalić zgodę
na użycie schematów i reguł oraz przesyłanie ich do API. Udział partnera nie
jest obecnie potwierdzony. Źródła pomysłów nie zastępują bibliografii naukowej.

## 10. Historia uzgodnień i dalsza praca

- **20 października 2026:** uporządkowano wcześniejsze pomysły jako materiał roboczy.
- **14 listopada 2026:** autor określił zakres generowania, kryterium sukcesu, trzy procesy porównania, role i poboczny status realizmu oraz rozumienia. Szczegółowy protokół odłożono do czasu uzyskania aplikacji.
- **15 listopada 2026:** autor zaakceptował główne pytanie oraz rekomendacje oparte na kompromisach zamiast jednego zbiorczego rankingu. Osobne badanie technik promptowania (PB-02) pozostawiono poza głównym zakresem. Plan scalono, zachowując oddzielenie ustaleń od wcześniejszych propozycji.

**Punkt kontynuacji:** ogólne ramy są uzgodnione. Nie rozwijamy teraz
szczegółów eksperymentów. Po uzyskaniu aplikacji wrócimy do sekcji 8,
dopracujemy pytania szczegółowe i protokół przed właściwymi pomiarami.
