# LLD — walidacja: uzgodniony przebieg i otwarty zakres

**Data:** 21 października 2026.

**Aktualizacja:** 14 listopada 2026.

**Status:** kolejność czterech etapów, rzeczywisty próbny import, obowiązkowe sprawdzanie relacji zatwierdzonych poza DDL i cztery rodzaje reguł z sekcji 6 są uzgodnione. Kolumny `json`/`jsonb` w schematach użytkownika odłożono poza MVP. Szczegóły reguł i relacji, reszta macierzy PostgreSQL i szczegóły środowiska pozostają otwarte.

**Podstawa:** [specyfikacja MVP v1.9](../specyfikacja_mvp.md), w szczególności REQ-012, REQ-027–REQ-031, REQ-032–REQ-040, REQ-068, REQ-070, REQ-071 i REQ-076. Ten dokument rozwija [LLD](README.md), nie jest implementacją walidatora. Zgodnie z REQ-072–REQ-075 nie projektujemy archiwum wykonań; raport i kandydat należą do pracy w bieżącym czacie. Paczka zmieniona przez LLM na prośbę użytkownika jest nowym kandydatem i wymaga nowej walidacji; nie dziedziczy pozytywnego raportu poprzednika (AC-42).

## 1. Co zostało potwierdzone

Użytkownik potwierdził następującą kolejność:

```text
1. Składnia i format
        ↓
2. Wstępna zgodność ze schematem i typami
        ↓
3. Rzeczywisty próbny import, obowiązujące relacje i kompletność
        ↓
4. Dodatkowe reguły biznesowe
```

- Dla SQL wykonujemy gotowe `INSERT` przygotowane przez model.
- Dla CSV odpowiednikiem jest rzeczywisty import oryginalnych plików; projekt przewiduje `COPY FROM STDIN`, bez konwersji na własne `INSERT`.
- Próbę prowadzimy na pustych danych, w odizolowanym PostgreSQL, z zatwierdzonym schematem.
- Wstępna kontrola typów nie zastępuje ostatecznej kontroli przez silnik.
- Udany import nie zastępuje sprawdzenia liczebności i zakresu.
- Uzgodnione 14 listopada 2026: na załadowanych danych osobno sprawdzamy relacje zatwierdzone przez użytkownika, których nie ma w DDL. Ich naruszenie lub brak potwierdzenia blokuje sukces zadania, mimo udanego importu. Nie dopisujemy ich do oryginalnego DDL.
- Walidacja nie zmienia plików kandydata. Poprawka modelu tworzy nowego kandydata.
- Brak możliwości sprawdzenia nie jest wynikiem pozytywnym. Awaria techniczna nie jest naruszeniem danych i nie uruchamia poprawki.

Potwierdzenie tego przebiegu nie oznacza przyjęcia wszystkich wcześniejszych rekomendacji. Osobno, 14 listopada 2026, potwierdzono objęcie MVP ograniczonym rodzajem reguły sumującej dane między tabelami (REQ-071); szczegóły opisano w sekcji 6.

## 2. Odpowiedzialność etapów

| Etap | Sprawdzenia | Granica |
| --- | --- | --- |
| 1. `FORMAT` | Poprawna budowa SQL/CSV, dozwolone instrukcje i wyrażenia, identyfikacja plików i tabel. | Nie wykonujemy SQL kandydata; poprawne parsowanie nie oznacza prawa do wykonania dowolnego kodu. |
| 2. `SCHEMA_PRECHECK` | Istnienie tabel i kolumn, liczba wartości/pól, dopuszczone typy i możliwe do wiarygodnego wykrycia niezgodności wartości. | Nie odtwarzamy całego systemu konwersji PostgreSQL i nie stosujemy cichej koercji Pydantic do danych modelu. |
| 3. `TRIAL_IMPORT`, sprawdzenie zatwierdzonych relacji i `COMPLETENESS` | Rzeczywisty import całej paczki, typy, obsługiwane `NOT NULL`, PK, FK, `UNIQUE`, `CHECK`, wymagane rozstrzygnięcie ograniczeń odroczonych; następnie osobne sprawdzenie relacji zatwierdzonych poza DDL oraz rzeczywistych liczebności i zakresu wobec planu. | Udany import nie dowodzi zgodności relacji nieobecnych w DDL. Raport rozdziela te wyniki; każdy obowiązkowy warunek wymaga potwierdzenia. |
| 4. `BUSINESS` | Dodatkowe, zatwierdzone reguły na załadowanych danych, ze wskazaniem zakresu, jednostki i przykładów naruszeń. | Nie uruchamiamy dowolnego kodu modelu. Naruszenie dodatkowej reguły jest czymś innym niż brak importowalności. |

Nazwy techniczne etapów są propozycją kontraktu. Walidator może wykonywać kilka sprawdzeń w jednym etapie. Nie gwarantujemy zebrania wszystkich błędów naraz.

Jeśli błąd wcześniejszego etapu uniemożliwia dalszy, wynik dalszego sprawdzenia to `NOT_RUN` z przyczyną. Sama niezgodna liczebność po udanym imporcie nie musi uniemożliwiać sprawdzenia reguły; raport pokazuje wtedy rzeczywisty zakres, a nie zatwierdzoną liczbę jako rzekomo sprawdzoną.

## 3. Klasyfikacja i wynik

| Sytuacja | Znaczenie |
| --- | --- |
| Niepoprawna treść SQL/CSV, niezgodny typ, klucz lub relacja | Naruszenie danych; może uruchomić poprawkę w dostępnym globalnym limicie. |
| Poprawny import, ale zła liczebność albo zakres | Brak kompletności; może uruchomić poprawkę. |
| Poprawny import, ale naruszona relacja zatwierdzona poza DDL | Brak spełnienia obowiązkowego warunku wykonania; uruchamia poprawkę w dostępnym limicie. Nie fałszujemy wyniku importu. |
| Kompletność, importowalność i obowiązujące relacje potwierdzone, dodatkowa reguła naruszona | Użyteczny kandydat z naruszeniem biznesowym; zachowujemy go podczas dalszych poprawek. |
| Niedostępne środowisko, timeout, błąd transportu lub silnika sprawdzeń | Przerwanie techniczne, bez automatycznego retry i bez nowej rundy naprawczej. |
| Brak dowodu obowiązkowego sprawdzenia | Brak potwierdzenia sukcesu, nie domyślne `PASS`. |

Po wyczerpaniu limitu kandydat spełniający wszystkie obowiązkowe warunki REQ-027 może oznaczać zadanie wykonane mimo pozostałych dodatkowych naruszeń biznesowych. Ograniczenia DDL blokujące import oraz relacje zatwierdzone poza DDL nie korzystają z łagodniejszej oceny dodatkowych reguł.

Weryfikacja obejmuje AC-34: poprawna i błędna referencja w relacji zatwierdzonej poza DDL przy udanym imporcie. AC-15 obejmuje brak rozstrzygnięcia takiej relacji. To wymagane scenariusze przyszłych testów, nie wykonane sprawdzenia aplikacji. Dokładne zasady relacji, m.in. dla NULL i kluczy złożonych, oraz ich reprezentacja w kontraktach nadal wymagają doprecyzowania.

Raport wiąże `candidate_id`, hash manifestu, migawkę wymagań, profil i wersję walidatora. Eksport wskazuje dokładnie tego samego kandydata. Brakujące pomiary i liczby naruszeń są jawnie nieznane, nie zerowe.

## 4. Środowisko próby — szczegóły nadal projektowane

Wybrano metodę rzeczywistego importu. Proponowana realizacja OD-02:

1. Osobna instancja `validation-db`, bez dostępu do `app-db` i baz użytkownika.
2. Pusta baza tymczasowa dla każdej operacji walidacyjnej; nazwy zasobów generuje aplikacja, nie model.
3. Rozdzielenie uprawnień provisioningu od ograniczonej roli importującej dane.
4. Lista dopuszczonych konstrukcji zarówno dla DDL, jak i SQL kandydata, także funkcji i wyrażeń.
5. Limity czasu, zasobów i sieci; bez gniazda Docker, `COPY PROGRAM` i dostępu do plików hosta.
6. Jedna przypięta wersja silnika oraz jawny profil transakcji i obsługi ograniczeń odroczonych.
7. Sprzątanie po sukcesie, błędzie i anulowaniu; pozostałości po awarii nie powodują wznowienia sprawdzeń.

Topologia, dokładne role, wartości limitów i wersja silnika wymagają przeglądu oraz testów. Sam kontener nie stanowi dowodu bezpiecznej izolacji. Nie pomijamy błędnych wierszy, nie wyłączamy ograniczeń ani nie przepisujemy danych dla uzyskania pozytywnego wyniku.

## 5. Macierz PostgreSQL — zapisana propozycja OD-01

Poniższy zakres omówiono jako kandydata `postgresql-mvp-v1`. **Nie został jeszcze zatwierdzony w całości.**
Podczas planowania S2, 14 listopada 2026, użytkownik zatwierdził listę
typów z wierszy „Liczby”, „Tekst” i „Pozostałe typy”, wraz z podaną
obsługą precyzji, skali i długości. Nie oznacza to zatwierdzenia
automatycznych ID ani pozostałych propozycji tej macierzy.
Następnie użytkownik zatwierdził również wielokolumnowe `PRIMARY KEY`,
`FOREIGN KEY` i `UNIQUE`. Pozostałe warianty tych ograniczeń nadal
wymagają doprecyzowania.

**Kolejne uzgodnienie S2 — 14 listopada 2026:** zatwierdzono `CHECK`
obejmujące porównania, zakresy (`BETWEEN`), zbiory wartości (`IN`)
i operatory logiczne `AND`, `OR`, `NOT` w obrębie rekordu, bez wywołań
funkcji. Jest to zakres niezależny od dziedziny projektu: nazwy pól
i dopuszczone wartości pochodzą z DDL, nie z zaszytych przykładów sklepu,
banku ani innej branży. Nieobsługiwane konstrukcje nadal wymagają diagnostyki.

| Obszar | Propozycja pierwszego profilu |
| --- | --- |
| Tabele | Zwykłe tabele, także łączące relacje wiele-do-wielu. |
| Liczby | `smallint`, `integer`, `bigint`, `numeric`/`decimal`, także precyzja i skala. |
| Tekst | `text`, `varchar`, także ograniczenie długości. |
| Pozostałe typy | `boolean`, `uuid`, `date`, `timestamp`, `timestamptz`. |
| Klucze | PK, FK i `UNIQUE`, również wielokolumnowe. |
| Wymagalność | `NOT NULL`. |
| `CHECK` | Porównania, zakresy, zbiory wartości i operatory logiczne w obrębie rekordu; bez dowolnych funkcji. |
| `DEFAULT` | Uzgodnione 14 listopada 2026: stałe zgodne z obsługiwanymi typami oraz `CURRENT_DATE` i `CURRENT_TIMESTAMP`. Bez innych wywołań funkcji i dowolnych wyrażeń. Automatyczne ID opisano osobno. |
| Automatyczne ID | Uzgodnione 14 listopada 2026: `serial`, `bigserial`, `GENERATED BY DEFAULT AS IDENTITY` i `GENERATED ALWAYS AS IDENTITY` w obsługiwanym DDL oraz jawne ID przygotowane przez model w paczce, wraz z powiązaniami rekordów. Szczegóły importu SQL/CSV i obsługa sekwencji wymagają uzgodnienia i próby. |
| Zależności | Propozycja startowa: acykliczne zależności między tabelami. Uzgodnione osobno: proste hierarchie rekordów w jednej tabeli, bez zapętleń i z brakiem rodzica dopuszczonym dla korzenia (REQ-005, AC-37). Nie zatwierdza to dowolnych cykli. |

**Uzgodnione 14 listopada 2026:** obsługa kolumn `json`/`jsonb` w schematach, dla których generujemy dane, pozostaje poza MVP. To potencjalny kierunek rozwoju, nie zaplanowana funkcja ([specyfikacja, sekcja 15](../specyfikacja_mvp.md#15-kierunki-rozszerzeń)). Decyzja nie ogranicza JSON w API, raportach ani wewnętrznym modelu danych aplikacji.

**Uzgodnione tego samego dnia:** MVP obsługuje proste hierarchie w jednej tabeli, np. pracowników i ich przełożonych. Relacji do tej samej tabeli nie wolno automatycznie klasyfikować jako nieobsługiwanej zależności kołowej: dla hierarchii bez zapętleń musi istnieć ścieżka generowania i rzeczywistego importu zarówno SQL, jak i CSV. Korzeń może nie mieć rodzica wyłącznie zgodnie z oryginalnym schematem. AC-37 opisuje przyszłe sprawdzenie tego zachowania; nie wykonano jeszcze testów. Dokładny profil importu nadal pozostaje w OD-02 i OD-04.

Proponowano również odłożyć tablice, własne typy i domeny, typy przestrzenne, kolumny wyliczane, partycjonowanie i rozszerzenia. Te wykluczenia nadal wymagają zatwierdzenia. Poprawność zależną od wyzwalaczy, procedur i własnych funkcji bazodanowych już wyłączono z MVP w sekcji 4.2 specyfikacji; nie oznacza to zatwierdzenia całej macierzy.

Nieobsługiwana konstrukcja jest diagnozowana przed generowaniem zależnego od niej zlecenia. Nie usuwamy jej po cichu i nie rozszerzamy obsługi tylko dlatego, że silnik PostgreSQL ją rozpoznaje.

Profil musi zachować semantykę NULL i dopuszczonych konwersji silnika. W szczególności `CHECK` nie zastępuje `NOT NULL`. Dla jawnych ID w `GENERATED ALWAYS AS IDENTITY` trzeba uwzględnić odpowiednią postać `INSERT`; aplikacja nie dopisuje jej do niepoprawnego wyniku modelu.

## 6. Reguły biznesowe — ustalenia i otwarte szczegóły OD-06

Uzgodnione wymaganie: użytkownik zna i zatwierdza interpretację reguły przed generowaniem. Uzgodniono mechanizm poniżej; szczegółowy format definicji i kontrakty nadal pozostają otwarte.

**Zakres obowiązywania — uzgodniony 14 listopada 2026 podczas planowania S3:** zatwierdzone reguły projektu obowiązują we wszystkich jego nowych zleceniach. Reguła dodana do pojedynczego zlecenia dotyczy tylko jego i nie zapisuje się automatycznie w projekcie. Wykryty konflikt wymaga wyjaśnienia, bez cichego nadpisania reguły projektu. Nie rozstrzyga to sposobu przechowywania ani szczegółów interfejsu.

**Mechanizm uzgodniony 14 listopada 2026 podczas planowania S3:** LLM proponuje rodzaj reguły z uzgodnionego katalogu i jego parametry. Aplikacja sprawdza obsługiwalność, użytkownik zatwierdza czytelny opis znaczenia, a walidator korzysta z gotowego mechanizmu danego rodzaju, zamiast wykonywać kod modelu. Nie zatwierdzono przez to nazw pól ani formatu zapisu definicji.

```text
Tekst użytkownika
    → propozycja ustrukturyzowanej interpretacji od LLM
    → sprawdzenie jej obsługiwalności przez aplikację
    → opis znaczenia i zatwierdzenie przez użytkownika
    → deterministyczne sprawdzenie danych
```

**Uzgodnione 14 listopada 2026 podczas planowania S3:** obok ograniczonej reguły sumującej katalog MVP obejmuje:

- porównanie dwóch kolumn tego samego rekordu w jednej tabeli, np. data dostawy późniejsza niż data zakupu; ograniczenie do jednego rekordu uzgodniono podczas doprecyzowania S3-T1;
- porównanie pojedynczej kolumny rekordu ze stałą wartością, stałymi granicami zakresu albo jawnym zbiorem stałych wartości, bez obliczeń i odwołań do innych rekordów lub tabel; ten zakres doprecyzowano i zatwierdzono w S3-T1;
- reguła warunkowa, np. wymaganie daty dostawy przy określonym statusie.

**Postać reguły warunkowej — uzgodniona 14 listopada 2026 podczas doprecyzowania S3-T1:** Reguła warunkowa w MVP ma postać „jeśli jeden warunek, to jedno wymaganie” i dotyczy tego samego rekordu jednej tabeli. Nie ma gałęzi „w przeciwnym razie” ani zagnieżdżonych reguł. Przykład: jeśli status jest równy „wysłany”, data dostawy musi być podana. Osobna reguła sumująca między tabelami pozostaje w MVP. Warunek i wymaganie korzystają z tego samego katalogu pojedynczych sprawdzeń: porównanie dwóch kolumn, porównanie z pojedynczą stałą, zakres, zbiór, „wartość jest NULL” oraz „wartość nie jest NULL”. Każdy człon jest jednym sprawdzeniem, bez łączenia przez „i”/„lub”; wszystkie odwołania dotyczą tego samego rekordu. „Wartość nie jest NULL” oznacza obecność wartości, nie sprawdzanie niepustości tekstu. Gdy warunek jest spełniony, oceniamy wymaganie: jego spełnienie oznacza zgodność, a niespełnienie naruszenie. Gdy warunek jest niespełniony przy dostępnych danych, wynik to „nie dotyczy”: wymagania nie oceniamy i nie zgłaszamy naruszenia. NULL w wartości potrzebnej do zwykłego porównania w warunku oznacza naruszenie całej reguły, a nie „nie dotyczy”. Jawne sprawdzenia „jest NULL” i „nie jest NULL” normalnie rozstrzygają warunek. Na przykład dla „jeśli status = wysłany, data dostawy nie jest NULL” status nowy daje „nie dotyczy”, status wysłany bez daty naruszenie, a status NULL również naruszenie. Reguła warunkowa obejmuje wszystkie rekordy wskazanej tabeli w zaimportowanej paczce. Raport rozlicza je w trzech rozłącznych grupach: zgodne, naruszenia i „nie dotyczy”. Każdy rekord trafia do jednej grupy i daje najwyżej jedno naruszenie danej reguły, również przy NULL w warunku. Rekordów „nie dotyczy” nie przedstawiamy jako spełniających wymaganie. Przykładowo 100 ocenionych rekordów to 35 zgodnych, 5 naruszeń i 60 „nie dotyczy”.

**Operacje porównania z pojedynczą stałą — uzgodnione 14 listopada 2026 podczas doprecyzowania S3-T1:** Dla porównania kolumny z pojedynczą stałą uzgodniono sześć operacji: równe, różne, mniejsze, mniejsze lub równe, większe oraz większe lub równe. To katalog operacji, nie dopuszczenie każdej z nich dla każdego typu. Dla kolumn smallint, integer, bigint, numeric/decimal, date, timestamp i timestamptz dostępne są wszystkie sześć operacji. Dla text, varchar, boolean i uuid dostępne są tylko równe i różne. W porównaniu z pojedynczą stałą wymagamy zgodności typów: liczby porównujemy w grupie smallint/integer/bigint/numeric/decimal, tekst w grupie text/varchar, a date, timestamp, timestamptz, boolean i uuid każde wyłącznie ze stałą swojego typu. Pozostałe pary są nieobsługiwane, bez automatycznych konwersji między grupami, np. liczba–tekst i date–timestamp. Dotyczy to typów w definicji reguły, nie sposobu rozpoznawania polecenia przez LLM. W porównaniu kolumny z pojedynczą stałą inną niż NULL brak wartości (NULL) w kolumnie zawsze oznacza naruszenie, także przy operacji „różne”. Rekordu nie pomijamy ani nie uznajemy za zgodny. Na przykład brak statusu narusza regułę „status różny od anulowany”. Nie zmieniamy oryginalnego DDL. Porównanie ze zbiorem obsługuje dwie operacje: „należy do zbioru” oraz „nie należy do zbioru”. Przykładowo status ma należeć do listy {nowy, opłacony, wysłany} albo nie należeć do listy {anulowany, odrzucony}. W obu operacjach porównania ze zbiorem definicja musi zawierać niepustą listę stałych innych niż NULL. Pusta lista lub NULL jako element oznacza błędną definicję z czytelną informacją o przyczynie, zamiast wykonania reguły. Dotyczy to listy w definicji, nie braku wartości w sprawdzanym rekordzie. Obie operacje zbioru korzystają z uzgodnionych zasad porównania z pojedynczą stałą: „należy” wymaga spełnienia porównania „równe” z co najmniej jednym elementem, a „nie należy” spełnienia porównania „różne” ze wszystkimi elementami. Każdy element musi być zgodny typowo z kolumną: liczby w grupie smallint/integer/bigint/numeric/decimal, tekst w grupie text/varchar, a date, timestamp, timestamptz, boolean i uuid każde ze swoim typem. Nie stosujemy konwersji między tymi grupami i nie pomijamy niezgodnych elementów definicji. Tekst porównujemy dokładnie, z uwzględnieniem wielkości liter i wszystkich spacji. NULL w sprawdzanej kolumnie oznacza naruszenie w obu operacjach. NULL w sprawdzanej kolumnie narusza obie operacje zbioru. Równość i różność tekstu w porównaniu kolumny z pojedynczą stałą dotyczą dokładnej treści, z uwzględnieniem wielkości liter i wszystkich spacji, bez automatycznego przekształcania. „ABC” jest różne od „abc” i od „ABC ” (ze spacją na końcu). Decyzji nie rozszerzono na zakresy ani zbiory. Porównanie z pojedynczą stałą obejmuje wszystkie rekordy wskazanej tabeli w zaimportowanej paczce. Każdy niezgodny rekord, także z NULL, oznacza jedno naruszenie tej reguły. Przykładowo 7 niezgodnych rekordów spośród 100 daje 7 naruszeń wśród 100 sprawdzonych. Wspólna zasada poniżej obejmuje również zakresy i zbiory. W wariancie porównania z pojedynczą stałą NULL nie może występować po stronie stałej. Definicje „równe NULL” i „różne od NULL” są nieobsługiwane w tym wariancie; aplikacja podaje czytelną przyczynę zamiast wykonywać zwykłe porównanie. Ewentualne osobne sprawdzanie obecności lub braku wartości pozostaje do ustalenia. Nie usuwa to uzgodnionego wymagania obsługi reguły warunkowej z wymaganą datą dostawy przy określonym statusie. Format stałych i zapis operatorów pozostają otwarte.

**Granice zakresu — uzgodnione 14 listopada 2026 podczas doprecyzowania S3-T1:** wariant „wartość w zakresie” obejmuje obie granice (przedział domknięty z obu stron). Dla 18–65 wartości 18 i 65 są dopuszczalne. W tym wariancie MVP nie ma wyboru granic otwartych. Wariant „wartość w zakresie” obsługuje wyłącznie kolumny smallint, integer, bigint, numeric/decimal, date, timestamp i timestamptz. Zakresy dla text, varchar, boolean i uuid są nieobsługiwane. Dla kolumny liczbowej obie granice zakresu są liczbami ze wspólnej grupy smallint/integer/bigint/numeric/decimal. Dla date, timestamp i timestamptz obie granice mają dokładnie ten sam typ co kolumna. Pozostałe połączenia są nieobsługiwane, bez automatycznych konwersji między tymi grupami, np. tekst–liczba i date–timestamp. Dotyczy to typów w definicji reguły, nie rozpoznawania polecenia przez LLM. W wariancie „wartość w zakresie” NULL w sprawdzanej kolumnie zawsze oznacza naruszenie reguły. Rekordu nie pomijamy i nie zmieniamy oryginalnego DDL. Na przykład brak wieku narusza regułę „wiek w zakresie 18–65”. Zakres sprawdzania i jednostkę naruszenia określa wspólna zasada prostych porównań poniżej. Wariant „wartość w zakresie” wymaga obu granic innych niż NULL. Brak którejkolwiek granicy lub NULL zamiast niej oznacza błędną definicję z czytelnym komunikatem. Nie traktujemy brakującej granicy jako nieskończoności. Warunki jednostronne, np. „wiek co najmniej 18”, można opisać porównaniem z pojedynczą stałą. Dla prostych porównań (kolumna–kolumna, pojedyncza stała, zakres i zbiór) obowiązuje wspólna zasada: sprawdzamy wszystkie rekordy wskazanej tabeli w zaimportowanej paczce; każdy niezgodny rekord oznacza jedno naruszenie danej reguły. Wynik podaje liczbę naruszeń wobec liczby sprawdzonych rekordów, np. 7 wśród 100. Nie ustala to zasad reguł warunkowych i sumujących. Format granic nadal wymaga ustalenia. Dolna granica musi być mniejsza lub równa górnej. Zakres 18–18 jest poprawny i dopuszcza tylko 18. Zakres 65–18 jest błędną definicją: aplikacja wyświetla zrozumiały błąd i nie zamienia granic automatycznie. Obie granice muszą być podane i inne niż NULL.

**Operacje porównania kolumn — uzgodnione 14 listopada 2026 podczas doprecyzowania S3-T1:** równe, różne, mniejsze, mniejsze lub równe, większe i większe lub równe. Zatwierdzono także macierz par typów i dostępnych operacji z [sekcji 5.2 specyfikacji](../specyfikacja_mvp.md#52-reguły-biznesowe-i-wskazówki-jakościowe). Pozostałe pary są nieobsługiwane; nie stosujemy automatycznych konwersji poza porównaniami wewnątrz wymienionych grup.

**NULL w porównaniu kolumn — uzgodnione 14 listopada 2026 podczas doprecyzowania S3-T1:** brak wartości w którejkolwiek z dwóch kolumn jest naruszeniem reguły, także gdy obie wartości są NULL. Rekordu nie pomijamy ani nie uznajemy porównania za spełnione. Nie zmieniamy oryginalnego DDL. To ustalenie nie dotyczy NULL w pozostałych rodzajach reguł.

**Tekst w porównaniu kolumn — uzgodnione 14 listopada 2026 podczas doprecyzowania S3-T1:** równość i różność dotyczą dokładnej treści, z uwzględnieniem wielkości liter i wszystkich spacji, bez automatycznego przekształcania wartości. „ABC” i „abc” są różne, podobnie „ABC” i „ABC ”. Nie rozstrzyga to mechanizmu wykonania.

**Zakres i jednostka naruszenia porównania kolumn — uzgodnione 14 listopada 2026 podczas doprecyzowania S3-T1:** sprawdzamy wszystkie rekordy wskazanej tabeli w zaimportowanej paczce. Jeden niezgodny rekord to jedno naruszenie tej reguły, także gdy obie porównywane wartości są NULL. Wynik pokazuje np. 7 naruszeń wśród 100 sprawdzonych rekordów. Nie ustala to zakresu ani jednostki dla pozostałych rodzajów reguł.

Zatwierdzono rodzaje reguł, katalog operacji, macierz typów oraz powyższe znaczenie NULL, porównań tekstowych, zakres i jednostkę naruszenia dla porównania kolumn, nie pełne kontrakty wykonawcze. Pozostają do uzgodnienia szczegóły pozostałych rodzajów reguł, w tym ich znaczenie NULL, zakres, jednostka naruszenia i zasady przedstawiania przykładów. Model nie dostarcza dowolnego SQL lub Pythona do bezpośredniego wykonania.

**Uzgodnione 14 listopada 2026:** MVP obejmuje automatyczne sprawdzanie ograniczonego rodzaju reguły sumującej dane między tabelami: wartość rekordu nadrzędnego równa sumie iloczynów dwóch pól jego rekordów podrzędnych, np. wartość zamówienia równa sumie `ilość × cena` jego pozycji (REQ-071). Wraz z trzema rodzajami powyżej tworzy to uzgodniony katalog MVP, bez obsługi dowolnych obliczeń.

**Powiązanie i zakres sumowania — uzgodnione 14 listopada 2026 podczas doprecyzowania S3-T1:** Reguła sumująca obejmuje wszystkie pozycje danego rekordu nadrzędnego w paczce, powiązane jedną jawnie wskazaną obowiązującą relacją. Nie obejmuje dodatkowego filtrowania pozycji ani przechodzenia przez kolejne tabele. Relacja pochodzi z DDL albo jest zatwierdzona poza nim zgodnie z REQ-012; aplikacja nie wybiera jej domyślnie. Przykład: wartość zamówienia równa sumie ilość × cena wszystkich jego pozycji, a nie tylko pozycji wybranego statusu.

**Uzgodniona kolejność obliczeń:** najpierw obliczamy i zaokrąglamy wartość każdej pozycji, następnie sumujemy te wartości. To stała zasada MVP, nie osobne pytanie do użytkownika aplikacji. Przykładowo przy precyzji dwóch miejsc dwie wartości `0,334` dają `0,33 + 0,33 = 0,66`, a nie `0,67` uzyskane przez zaokrąglenie dopiero sumy. Przykład nie narzuca dwóch miejsc wszystkim schematom ani nie oznacza poprawiania plików kandydata.

**Precyzja zaokrąglania — uzgodniona 14 listopada 2026 podczas doprecyzowania S3-T1:** Liczba miejsc po przecinku, do której zaokrąglamy iloczyn każdej pozycji, jest jawnym parametrem konkretnej reguły sumującej, widocznym w interpretacji do zatwierdzenia. Reguły mogą wskazywać różną precyzję, np. 2 albo 3 miejsca. Nie narzucamy dwóch miejsc wszystkim regułom ani nie wyprowadzamy precyzji po cichu ze schematu.

**Tryb zaokrąglania — uzgodniony 14 listopada 2026 podczas doprecyzowania S3-T1:** W MVP stosujemy jeden tryb zaokrąglania iloczynu pozycji: do najbliższej wartości o zadanej liczbie miejsc, a przy dokładnej połowie — od zera. Dla 2 miejsc: 1,234 daje 1,23; 1,235 daje 1,24; −1,235 daje −1,24. Tryb jest stałą zasadą aplikacji, widoczną w interpretacji reguły, bez wyboru innego trybu.

**Brak wartości w sumowaniu — uzgodnione 14 listopada 2026 podczas doprecyzowania S3-T1:** NULL w wartości rekordu nadrzędnego albo w którymkolwiek z dwóch mnożonych pól którejkolwiek powiązanej pozycji oznacza naruszenie reguły sumującej dla rekordu nadrzędnego. Nie zastępujemy NULL zerem i nie pomijamy niekompletnych pozycji. Na przykład zamówienie z pozycją bez ceny narusza regułę, zamiast być sprawdzane wyłącznie na podstawie sumy pozostałych pozycji.

**Brak pozycji — uzgodnione 14 listopada 2026 podczas doprecyzowania S3-T1:** Przy braku powiązanych pozycji suma wynosi 0. Rekord nadrzędny bez pozycji spełnia regułę sumującą wyłącznie wtedy, gdy jego wartość wynosi 0; inna wartość daje naruszenie, a NULL pozostaje naruszeniem zgodnie z zasadą brakujących wartości. Brak pozycji sam w sobie nie narusza tej reguły. Nie zmienia to wymagań DDL ani innych reguł, które mogą wymagać istnienia pozycji.

**Porównanie wyniku sumowania — uzgodnione 14 listopada 2026 podczas doprecyzowania S3-T1:** Wartość nadrzędną porównujemy dokładnie z sumą już zaokrąglonych pozycji, bez tolerancji różnicy i bez dodatkowego zaokrąglania wartości nadrzędnej lub sumy. Porównujemy wartość liczbową, nie liczbę zer w zapisie. Dla sumy 19,99 wartość nadrzędna 19,990 daje zgodność, a 19,991 naruszenie.

**Dziedzina i dokładność sumowania — uzgodnione 14 listopada 2026 podczas doprecyzowania S3-T1:** Reguła sumująca operuje wyłącznie na typach smallint, integer, bigint i numeric/decimal we wszystkich trzech polach: wartości nadrzędnej oraz obu mnożonych polach pozycji. Obliczenia zachowują dokładność dziesiętną, bez przybliżania przez binarne liczby zmiennoprzecinkowe i bez automatycznej zamiany tekstu na liczby. Nie wybiera to biblioteki ani reprezentacji API.

**Do wyjaśnienia przed implementacją:** dozwolony zakres parametru precyzji, NULL w kluczu relacji, jednostka naruszenia oraz wykonywalna reprezentacja reguły, w tym format wskazania pól i relacji. Nie przyjmujemy tych szczegółów domyślnie. Weryfikację po ich uzgodnieniu opisuje AC-33 w specyfikacji.

**Nieobsługiwana reguła — uzgodnione 14 listopada 2026 podczas planowania S3:** aplikacja blokuje start generowania, informuje użytkownika o problemie i daje wybór: kontynuowanie bez tej reguły albo jej poprawienie. Bez świadomego wyboru nie rozpoczyna generowania. Wybranie poprawy zachowuje blokadę do uzyskania obsługiwanej interpretacji i jej zatwierdzenia. Kontynuowanie bez reguły nie oznacza jej spełnienia, automatycznej zamiany we wskazówkę jakościową ani obejścia pozostałych blokad. Uzgodniono także, że pominięcie reguły projektu dotyczy wyłącznie bieżącego zlecenia, bez usuwania lub zmiany reguły w projekcie. W kolejnych nowych zleceniach reguła nadal obowiązuje; ponowne pominięcie wymaga świadomej decyzji użytkownika.

Realizm pozostaje oceną zewnętrzną.

## 7. Powiązanie z LLD i otwartymi decyzjami

- [Kontrakty API](kontrakty_api.md) wymagają wyników poszczególnych etapów i przyczyn niewykonania, nie tylko `valid=true`.
- [Model danych](model_danych.md) wiąże raport z niezmiennym kandydatem bieżącego wykonania. Archiwum historii i wiadomości jest poza MVP.
- [Cykl wykonania](cykl_wykonania.md) rozróżnia naruszenie danych, błąd techniczny i anulowanie.
- OD-02 jest częściowo rozstrzygnięte wyborem próbnego importu; szczegóły środowiska nadal są otwarte.
- OD-01, OD-04 i OD-06 nie zostały zamknięte przez sam wybór kolejności walidacji.
- OD-08 częściowo rozstrzygnięto 14 listopada 2026: wcześniej zapisany użyteczny kandydat z raportem jest dostępny po anulowaniu lub błędzie bez ponawiania walidacji i zmiany statusu wykonania (REQ-047, AC-35). Dostępność częściowych lub niesprawdzonych artefaktów nadal jest otwarta.
- OD-03 rozstrzygnięto 14 listopada 2026: spośród kandydatów z potwierdzonymi obowiązkowymi warunkami wybieramy wyłącznie najnowszego, bez rankingu dodatkowych naruszeń (REQ-039, AC-36).
- OD-09 częściowo rozstrzygnięto: bieżący czat może zawierać kolejne polecenia, ale zdarzenia z REQ-074, także odświeżenie i zamknięcie strony, kończą dostęp do rozmowy i plików. W tej granicy obowiązuje pobranie po przerwaniu. Ostrzeżenie i zachowanie danych po rezygnacji określa REQ-075. Nadal otwarte są mechanizm zakończenia dostępu i fizyczne sprzątanie. Timeouty pozostają otwarte.
