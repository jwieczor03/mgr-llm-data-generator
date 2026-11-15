# Czy projekt ma potencjał na pracę magisterską?

**Moja ocena: tak, warunkowo.** Projekt daje podstawę do empirycznej pracy
o skuteczności LLM w tworzeniu relacyjnych danych testowych. Sama aplikacja
nie dowodzi jednak wkładu badawczego, a podobne badania już istnieją.

**Data:** 14 listopada 2026.  
**Status:** ocena doradcza i propozycje; nie decyzja promotora, nie
zatwierdzony protokół i nie raport z własnych eksperymentów.  
**Źródła zewnętrzne:** [literatura L-01–L-10](literatura.md).  
**Aktualny plan:** [plan badań](../docs/plan_badan.md).

**Późniejsze ustalenia — 15 listopada 2026:** autor doprecyzował cel,
zaakceptował główne pytanie i ogólne ramy porównania. Poniższa ocena
opisuje wcześniejszy stan dokumentacji; jej listy braków nie należy
odczytywać jako ponownego otwarcia już podjętych decyzji. Aktualne ustalenia
zawiera plan, a punkt kontynuacji wskazuje [stan badań](stan-badan.md).

## 1. Co faktycznie oceniono

Podstawą były README, specyfikacja MVP v1.15, plan badań,
rejestr ustaleń, architektura ogólna oraz projekt walidacji.
Pomocniczo sprawdzono odniesienia w dokumentacji usług i LLD.
Nie potraktowano archiwalnych koncepcji jako aktualnych decyzji.

Repozytorium i README opisują etap dokumentacji, nie działającą aplikację.
Nie znaleziono protokołów wykonanych eksperymentów ani własnych wyników.
Nie sprawdzano działania modeli, baz i walidatora.

Nie znamy oficjalnego tytułu zaakceptowanego przez promotora, wymagań
uczelni, terminu oddania ani budżetu badań. Ocena dotyczy potencjału
poznawczego koncepcji, nie formalnego dopuszczenia pracy.

## 2. Mocne strony dokumentacji

| Element | Dlaczego pomaga badaniom |
| --- | --- |
| Jednoznaczne wejście: DDL PostgreSQL, reguły i zatwierdzone zlecenie | Można przygotować stałe zadania dla porównywanych wariantów. |
| Ocena całego procesu, nie tylko pierwszej odpowiedzi | Pozwala uwzględnić walidację, poprawki i ich nakład. |
| Rzeczywisty import i osobne sprawdzenie relacji poza DDL | Dają obserwowalne kryteria, nie deklarację modelu. |
| Oddzielenie kompletności, zgodności biznesowej i realizmu | Zapobiega uznaniu poprawnego pliku za realistyczne dane. |
| Rozdzielenie modelu, promptów, ról i pomocy deterministycznej | Ułatwia ustalenie, co rzeczywiście odpowiada za różnicę wyników. |
| Limity napraw i jawne niepowodzenia | Umożliwiają badanie skuteczności przy skończonym nakładzie. |

To mocne strony projektu metody, nie dowody, że rozwiązanie już działa.

## 3. Czego brakuje do obronnej części badawczej

### Jednego głównego pytania

PB-01–PB-05 obejmują modele, prompty, role, pomoc kodu, złożoność i skalę.
Nie proponuję badać wszystkich kombinacji. W obecnym planie nie wybrano,
które porównanie ma dać główny wniosek pracy.

### Punktu odniesienia i uczciwego budżetu

Punkt odniesienia to prostszy wariant, z którym porównujemy metodę.
Bez niego wynik „udało się wygenerować bazę” niewiele mówi o korzyści.
Trzeba też odróżnić efekt lepszej informacji zwrotnej od efektu większej
liczby wywołań.

Modele lokalne i dostępne przez API nie są kategoriami jakości.
Przy porównaniu zmieniającym kilka czynników naraz wniosek dotyczy
całych systemów, a nie samodzielnie „wpływu agenta”.

### Powtórzeń, miar i zasad analizy

Nie ustalono liczby prób, mianowników mierników, obsługi awarii
i granic czasu. Jedną obserwacją powinno być wykonanie całego zlecenia;
tysiąc wierszy z tej samej paczki nie jest tysiącem niezależnych prób.
Liczbę powtórzeń należy dobrać po pilotażu i ocenie budżetu.

### Materiałów pozwalających odtworzyć próbę

Brak historii w aplikacji jest uzgodnionym ograniczeniem, nie błędem do
samodzielnego naprawienia. Stwarza jednak potrzebę zachowania materiałów
badawczych poza nią: wersji scenariusza, promptów, modelu i ustawień,
wyników, raportów, pomiarów oraz nieudanych wykonań.

Pełny ślad każdej rundy nie jest obecnie gwarantowany. Należy ustalić,
co można zebrać ręcznie i czy to wystarczy do wybranego pytania.
Ewentualny brak pomiarowy jest potrzebą do osobnego uzgodnienia,
nie nowym wymaganiem aplikacji.

## 4. Czy podobne badania już istnieją?

**Tak, również bardzo bliskie.** Szczegóły, dostęp i źródła podano
w [notatkach literaturowych](literatura.md).

| Rodzina prac | Co oznacza dla naszej argumentacji |
| --- | --- |
| L-01: niezawodność generowania relacyjnego przez lokalne modele | Porównanie modeli i strategii ma bezpośredniego poprzednika. |
| L-02–L-03: procesy tworzenia danych do testów SQL | Sam proces z walidacją i poprawkami nie wystarcza jako argument nowości. |
| L-04: REMIX | Także spójność zależności między tabelami ma aktualnych poprzedników. |
| L-05: dane i kod generatorów | Zastosowanie LLM do danych testowych nie jest nowym pomysłem. |
| L-06–L-10: reguły, synteza relacyjna i metody bez LLM | Należy rozdzielać poprawność, realizm i wartość dodatkowej złożoności. |

Nie oznacza to automatycznie, że projekt należy porzucić. Proponuję
uczciwie umiejscowić go jako badanie porównawcze, replikację z rozszerzeniem
lub analizę granic. Nie mamy podstaw do deklaracji „nikt tego nie badał”.

## 5. Jaki wkład proponuję

**Propozycja kierunku:**

> Zbadać, jak informacja zwrotna z wykonywalnej walidacji wpływa na
> końcową skuteczność i nakład generowania relacyjnych danych testowych
> z DDL i jawnych reguł, bez danych produkcyjnych jako wejścia.

To nie jest potwierdzona luka w literaturze. Wartość własnej pracy może
polegać na odtwarzalnym porównaniu w jasno opisanych warunkach, z analizą
klas błędów i granic skuteczności. Sam wybór PostgreSQL, nowszego modelu,
czatu lub większej liczby usług nie stanowi jeszcze takiego wkładu.

Proponowany łańcuch argumentacji:

| Ogniwo | Propozycja |
| --- | --- |
| Problem | Dane mogą poprawnie się importować, lecz nadal naruszać jawne wymagania zadania. |
| Pytanie | Czy naprawy kierowane wykrytymi naruszeniami pomagają bardziej niż kolejne generowanie przy porównywalnym nakładzie? |
| Porównanie | Ten sam model i zadania; naprawa z diagnostyką wobec niezależnych kandydatów bez tej diagnostyki. |
| Pomiar | Końcowe wykonanie REQ-027, spełnienie dodatkowych reguł, czas, wywołania, tokeny i niepowodzenia. |
| Możliwy wniosek | Dla których przypadków diagnostyka poprawia końcowy wynik i jakim kosztem; również możliwy brak korzyści. |
| Ograniczenia | Wybrane scenariusze i modele, ograniczony zakres DDL, brak dowodu wierności produkcji i ogólnej skuteczności. |

### Alternatywy, a nie dodatkowe obowiązki

- Kontrolowane porównanie generowania całej paczki i kolejnych tabel:
  bliskie L-01, więc raczej jawna replikacja/rozszerzenie.
- Porównanie z prostym generatorem bez LLM: pozwala sprawdzić, czy
  język naturalny i treść uzasadniają dodatkowy koszt.
- Zachowanie niezmienianych danych przy kolejnych poleceniach w czacie:
  potencjalne odrębne pytanie, lecz nie wykonano przeglądu właściwego
  dla tej węższej tematyki. Nie deklarujemy tu nowości.

Nie proponuję teraz nowego algorytmu uczenia, fine-tuningu, rozbudowy
wieloagentowej ani platformy automatycznych eksperymentów.

## 6. Najmniejszy sensowny następny eksperyment

**Status: szkic pilotażu, wymaga decyzji autora. Nie wykonano prób.**

1. Jeden ustalony model, jeden format wyniku i jawne ustawienia.
2. Mały przypadek relacyjny oraz przypadek z regułą sumującą dane
   między tabelami. Znaczenie obliczeń najpierw trzeba rozstrzygnąć
   zgodnie z OD-06; obowiązującej kolejności zaokrąglania nie otwieramy ponownie.
3. Dwa procesy: kolejne niezależne kandydatury oraz poprawki z tą samą
   walidacją i konkretną diagnostyką. Oba mają identyczne wymagania.
4. Uzgodniony limit całego nakładu. Przykładowy limit liczby kandydatów
   to cztery, odpowiadające pierwszemu wynikowi i trzem naprawom MVP.
   Taka sama liczba kandydatów nie gwarantuje tego samego kosztu,
   więc trzeba mierzyć także tokeny, czas i wszystkie wywołania.
5. Ocena końcowej paczki wybranej według ustalonej polityki, bez
   wybierania po fakcie najlepszej według naruszeń biznesowych.
6. Zachowanie materiałów także z niepowodzeń. Pilot służy sprawdzeniu
   wykonalności i zmienności, nie końcowemu dowodowi przewagi.

Niezależne generowanie jest tutaj propozycją wariantu badawczego,
nie zmianą uzgodnionego zachowania napraw aplikacji. Nie przyjmujemy
istnienia przełącznika takiego procesu. Wariant można przygotować
osobno; ewentualne wdrożenie wymaga odrębnego zlecenia.

Pierwsza odpowiedź może pomóc diagnozować błędy, ale nie staje się
głównym kryterium wbrew zapisanej ocenie wyniku całego procesu.

## 7. Jak mierzyć bez zmiany znaczenia wymagań

- **Wykonanie zadania:** liczba wykonań zakończonych wynikiem
  spełniającym REQ-027 względem wszystkich rozpoczętych wykonań;
  dodatkowo rozbicie według przyczyny zakończenia.
- **Pełna zgodność sprawdzalna:** osobno odsetek wykonań, których
  wynik spełnia także wszystkie dodatkowe reguły. To miara badawcza,
  nie zmiana statusu aplikacji z REQ-029.
- **Reguły:** wyniki każdej reguły z własną jednostką i mianownikiem,
  np. zamówienia, a nie automatycznie wszystkie wiersze każdej tabeli.
  Reguły niewykonanej po błędzie importu nie liczymy jako spełnionej.
- **Nakład:** cały proces, w tym poprawki i role; czas przygotowania
  przez człowieka można pokazać osobno. Brak pomiaru kosztu nie jest zerem.
- **Naprawa i pogorszenie:** jeśli uda się zachować kolejne raporty,
  sprawdzić również, czy naprawa jednej reguły nie psuje innych.
  Dostępność takich materiałów trzeba najpierw ustalić.

Walidator wymaga sprawdzenia na znanych poprawnych i błędnych przykładach,
w tym granicznych przypadkach reguł. Samo użycie deterministycznego kodu
nie dowodzi poprawności miernika. Recenzent LLM będący częścią procesu
nie może być jedynym sędzią jego sukcesu.

Realizm oceniany przez autora może pozostać eksploracyjny, z jawną rubryką
i ograniczeniem subiektywności. Bez danych lub uzgodnionego rozkładu
odniesienia nie należy twierdzić, że odtworzono statystykę produkcji.
Importowalność nie dowodzi też zdolności wykrywania błędów aplikacji.
Jeżeli użyteczność testowa ma być główną tezą, potrzebny jest osobny,
uzgodniony pomiar na zadaniach testowych.

## 8. Granice aktualnej specyfikacji

1. **REQ-068:** model ma zwracać gotowy SQL lub CSV. Pomysłów PB-04
   o pomocy deterministycznej nie wolno interpretować jako zgody na
   zastąpienie wyniku modelu własnym generatorem lub cichą naprawą danych.
   Taki generator może być zewnętrznym odniesieniem.
2. **REQ-039:** aplikacja wybiera najnowszego użytecznego kandydata,
   nie najlepszy biznesowo. Badanie powinno zachować tę politykę
   lub jawnie badać inną poza aplikacją. Poprawa nie musi być monotoniczna.
3. **REQ-074:** wyjście z czatu kończy dostęp do materiałów.
   Przed pilotażem trzeba ustalić ich zewnętrzny zapis.
4. **OD-01, OD-02, OD-04–OD-06:** otwarte szczegóły dialektu, importu,
   formatu i reguł wpływają na definicję poprawności. Nie zamykamy ich
   propozycją badawczą.

Te ograniczenia nie przekreślają badań. Określają, jakie wnioski będzie
można wyciągać i jakie porównania wymagają osobnej aparatury.

## 9. Rekomendacja i następna decyzja

**Rekomenduję kontynuowanie tematu**, ale nie jako dowodu oryginalności
samej aplikacji. Najpierw uzgodnić oczekiwany wkład z promotorem,
następnie wybrać jedno porównanie i wykonać mały pilotaż.

Przykładowy tytuł do rozmowy, **nie zatwierdzona zmiana tematu**:

> Ocena wpływu walidacji i iteracyjnych poprawek na skuteczność
> generowania relacyjnych danych testowych przez duże modele językowe.

Nie ma jeszcze podstaw do oszacowania wykonalności czasowej ani kosztowej.
Najpilniejszy brak informacji: czy promotor oczekuje nowej metody,
czy akceptuje rzetelne badanie porównawcze lub replikacyjne.
