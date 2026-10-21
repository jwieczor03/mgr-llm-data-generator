# LLD — walidacja: uzgodniony przebieg i otwarty zakres

**Data:** 21 października 2026.

**Status:** kolejność czterech etapów i rzeczywisty próbny import są uzgodnione; macierz PostgreSQL, katalog reguł i szczegóły środowiska pozostają propozycjami.

**Podstawa:** [specyfikacja MVP v1.4](../specyfikacja_mvp.md), w szczególności REQ-027–REQ-031, REQ-032–REQ-040, REQ-068 i REQ-070. Ten dokument rozwija [LLD](README.md), nie jest implementacją walidatora.

## 1. Co zostało potwierdzone

Użytkownik potwierdził następującą kolejność:

```text
1. Składnia i format
        ↓
2. Wstępna zgodność ze schematem i typami
        ↓
3. Rzeczywisty próbny import oraz kompletność
        ↓
4. Dodatkowe reguły biznesowe
```

- Dla SQL wykonujemy gotowe `INSERT` przygotowane przez model.
- Dla CSV odpowiednikiem jest rzeczywisty import oryginalnych plików; projekt przewiduje `COPY FROM STDIN`, bez konwersji na własne `INSERT`.
- Próbę prowadzimy na pustych danych, w odizolowanym PostgreSQL, z zatwierdzonym schematem.
- Wstępna kontrola typów nie zastępuje ostatecznej kontroli przez silnik.
- Udany import nie zastępuje sprawdzenia liczebności i zakresu.
- Walidacja nie zmienia plików kandydata. Poprawka modelu tworzy nowego kandydata.
- Brak możliwości sprawdzenia nie jest wynikiem pozytywnym. Awaria techniczna nie jest naruszeniem danych i nie uruchamia poprawki.

Potwierdzenie tego przebiegu nie oznacza przyjęcia wszystkich wcześniejszych rekomendacji, w szczególności agregacji między tabelami.

## 2. Odpowiedzialność etapów

| Etap | Sprawdzenia | Granica |
| --- | --- | --- |
| 1. `FORMAT` | Poprawna budowa SQL/CSV, dozwolone instrukcje i wyrażenia, identyfikacja plików i tabel. | Nie wykonujemy SQL kandydata; poprawne parsowanie nie oznacza prawa do wykonania dowolnego kodu. |
| 2. `SCHEMA_PRECHECK` | Istnienie tabel i kolumn, liczba wartości/pól, dopuszczone typy i możliwe do wiarygodnego wykrycia niezgodności wartości. | Nie odtwarzamy całego systemu konwersji PostgreSQL i nie stosujemy cichej koercji Pydantic do danych modelu. |
| 3. `TRIAL_IMPORT` i `COMPLETENESS` | Rzeczywisty import całej paczki, typy, obsługiwane `NOT NULL`, PK, FK, `UNIQUE`, `CHECK`, wymagane rozstrzygnięcie ograniczeń odroczonych; następnie rzeczywiste liczebności i zakres wobec planu. | Sukces jest dowodem dla zapisanego silnika, schematu i profilu próby, nie całego PostgreSQL ani realizmu danych. |
| 4. `BUSINESS` | Dodatkowe, zatwierdzone reguły na załadowanych danych, ze wskazaniem zakresu, jednostki i przykładów naruszeń. | Nie uruchamiamy dowolnego kodu modelu. Naruszenie dodatkowej reguły jest czymś innym niż brak importowalności. |

Nazwy techniczne etapów są propozycją kontraktu. Walidator może wykonywać kilka sprawdzeń w jednym etapie. Nie gwarantujemy zebrania wszystkich błędów naraz.

Jeśli błąd wcześniejszego etapu uniemożliwia dalszy, wynik dalszego sprawdzenia to `NOT_RUN` z przyczyną. Sama niezgodna liczebność po udanym imporcie nie musi uniemożliwiać sprawdzenia reguły; raport pokazuje wtedy rzeczywisty zakres, a nie zatwierdzoną liczbę jako rzekomo sprawdzoną.

## 3. Klasyfikacja i wynik

| Sytuacja | Znaczenie |
| --- | --- |
| Niepoprawna treść SQL/CSV, niezgodny typ, klucz lub relacja | Naruszenie danych; może uruchomić poprawkę w dostępnym globalnym limicie. |
| Poprawny import, ale zła liczebność albo zakres | Brak kompletności; może uruchomić poprawkę. |
| Kompletność i importowalność potwierdzone, dodatkowa reguła naruszona | Użyteczny kandydat z naruszeniem biznesowym; zachowujemy go podczas dalszych poprawek. |
| Niedostępne środowisko, timeout, błąd transportu lub silnika sprawdzeń | Przerwanie techniczne, bez automatycznego retry i bez nowej rundy naprawczej. |
| Brak dowodu obowiązkowego sprawdzenia | Brak potwierdzenia sukcesu, nie domyślne `PASS`. |

Po wyczerpaniu limitu kompletny i importowalny kandydat może oznaczać zadanie wykonane mimo pozostałych dodatkowych naruszeń biznesowych. Reguła będąca także ograniczeniem DDL nie korzysta z tego rozróżnienia, jeśli jej naruszenie uniemożliwia import.

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

| Obszar | Propozycja pierwszego profilu |
| --- | --- |
| Tabele | Zwykłe tabele, także łączące relacje wiele-do-wielu. |
| Liczby | `smallint`, `integer`, `bigint`, `numeric`/`decimal`, także precyzja i skala. |
| Tekst | `text`, `varchar`, także ograniczenie długości. |
| Pozostałe typy | `boolean`, `uuid`, `date`, `timestamp`, `timestamptz`. |
| Klucze | PK, FK i `UNIQUE`, również wielokolumnowe. |
| Wymagalność | `NOT NULL`. |
| `CHECK` | Porównania, zakresy, zbiory wartości i operatory logiczne w obrębie rekordu; bez dowolnych funkcji. |
| `DEFAULT` | Stałe i jawnie dopuszczone przypadki, np. `CURRENT_DATE` i `CURRENT_TIMESTAMP`, nie dowolny kod. |
| Automatyczne ID | `serial`/`bigserial` i identity, z jawnymi ID w paczce potrzebnymi do powiązania rekordów. Dokładne postacie DDL i importu wymagają próby. |
| Zależności | Propozycja startowa: acykliczne zależności między tabelami. Samoodwołania i pozostałe cykle do osobnego rozstrzygnięcia. |

Proponowano odłożyć tablice, JSONB, własne typy i domeny, typy przestrzenne, kolumny wyliczane, partycjonowanie, rozszerzenia, wyzwalacze i procedury. Nie jest to jeszcze zatwierdzenie wykluczenia każdego z tych elementów.

Nieobsługiwana konstrukcja jest diagnozowana przed generowaniem zależnego od niej zlecenia. Nie usuwamy jej po cichu i nie rozszerzamy obsługi tylko dlatego, że silnik PostgreSQL ją rozpoznaje.

Profil musi zachować semantykę NULL i dopuszczonych konwersji silnika. W szczególności `CHECK` nie zastępuje `NOT NULL`. Dla jawnych ID w `GENERATED ALWAYS AS IDENTITY` trzeba uwzględnić odpowiednią postać `INSERT`; aplikacja nie dopisuje jej do niepoprawnego wyniku modelu.

## 6. Reguły biznesowe — zapisana propozycja OD-06

Uzgodnione wymaganie: użytkownik zna i zatwierdza interpretację reguły przed generowaniem. Dokładna reprezentacja wykonawcza nadal jest otwarta.

Proponowany mechanizm:

```text
Tekst użytkownika
    → propozycja ustrukturyzowanej interpretacji od LLM
    → sprawdzenie jej obsługiwalności przez aplikację
    → opis znaczenia i zatwierdzenie przez użytkownika
    → deterministyczne sprawdzenie danych
```

Proponowany ograniczony katalog:

- porównanie kolumn, np. data dostawy późniejsza niż data zakupu;
- porównanie wartości z progiem, zakresem lub zbiorem;
- reguła warunkowa, np. wymaganie daty dostawy przy określonym statusie.

Każdy szablon wymaga jawnego znaczenia NULL, zakresu, jednostki naruszenia i zasad przedstawiania przykładów. Model nie dostarcza dowolnego SQL lub Pythona do bezpośredniego wykonania.

**Nierozstrzygnięte pytanie:** czy MVP obejmie agregacje między tabelami, np. wartość zamówienia równą sumie `ilość × cena` jego pozycji. Nie otrzymano jeszcze odpowiedzi. Jeśli zostaną wybrane, trzeba ustalić zaokrąglanie, NULL, brak pozycji, klucze relacji i zakres sumowania.

Nieobsługiwana reguła jest jawnie nieobsługiwana. Nie zmieniamy jej automatycznie we wskazówkę jakościową. Realizm pozostaje oceną zewnętrzną.

## 7. Powiązanie z LLD i otwartymi decyzjami

- [Kontrakty API](kontrakty_api.md) wymagają wyników poszczególnych etapów i przyczyn niewykonania, nie tylko `valid=true`.
- [Model danych](model_danych.md) zachowuje niezmiennych kandydatów, raporty i historię.
- [Cykl wykonania](cykl_wykonania.md) rozróżnia naruszenie danych, błąd techniczny i anulowanie.
- OD-02 jest częściowo rozstrzygnięte wyborem próbnego importu; szczegóły środowiska nadal są otwarte.
- OD-01, OD-04 i OD-06 nie zostały zamknięte przez sam wybór kolejności walidacji.
- Pozostałe decyzje, w szczególności wybór kandydata, timeouty, dostępność po przerwaniu i retencja, zachowują dotychczasowy status.
