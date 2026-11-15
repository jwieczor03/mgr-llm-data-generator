# Stan badań

To punkt wejścia do badań pracy magisterskiej. Wskazuje aktualne ustalenia,
materiały i następny krok; nie zastępuje planu.

**Aktualizacja:** 15 listopada 2026.  
**Etap:** uzgodniono ogólne ramy i zakres porównań.
Szczegółowy protokół powstanie po uzyskaniu aplikacji.  
**Własne eksperymenty i wyniki:** brak.

## Gdzie zacząć

1. [Plan badań](../docs/plan_badan.md) — źródło celu, zaakceptowanego pytania,
   ram porównania i otwartych decyzji. Nie przeniesiono go z dotychczasowej lokalizacji.
2. [Literatura](literatura.md) — wstępne rozeznanie z 14 listopada 2026;
   opisuje zakres sprawdzenia źródeł i ograniczenia przeglądu.
3. [Ocena koncepcji](ocena-koncepcji.md) — wcześniejsza analiza doradcza,
   nie aktualny protokół ani decyzja promotora.
4. [Specyfikacja aplikacji](../docs/specyfikacja_mvp.md) — wymagania narzędzia,
   nie wymagania badań.

## Co jest uzgodnione

- **Cel:** porównanie modeli LLM w generowaniu złożonych danych testowych
  przy wsparciu deterministycznego walidatora; aplikacja jest pomocnicza.
- **Pytanie główne:** zaakceptowano 15 listopada 2026 pytanie o wpływ modelu
  i procesu na poprawność, czas i koszt, przy generowaniu bezpośrednim
  i wspieranym aplikacją. Pełne brzmienie zawiera sekcja 1 planu.
- **Wejście:** DDL, polecenie i reguły, bez istniejących rekordów.
  Potrzebne dane w tabelach powiązanych również trzeba wygenerować.
- **Materiał:** prostsze i trudniejsze schematy. Autor planuje szukać na GitHubie,
  ewentualnie część wygenerować; nie wybrano źródeł ani nie wykonano wyszukiwania.
- **Wariant odniesienia:** czysty LLM, pełny DDL, oryginalne polecenie i reguły,
  jedno wywołanie bez poprawek. Późniejsza walidacja nie wraca do modelu.
- **Porównania:** ten sam model bez aplikacji i w jej procesie bez agentów;
  dodatkowo proces z planistą, wykonawcą i reviewerem tego samego modelu.
- **Pętla:** reviewer tylko ocenia i przekazuje ocenę wykonawcy, który poprawia
  dane; do 3 rund poprawek po pierwszym generowaniu. Szczegóły ustalimy później.
- **Sukces:** kompletność, importowalność, wymagane relacje i wszystkie
  deterministycznie sprawdzane reguły scenariusza. Nie jest tożsamy ze statusem
  wykonania w aplikacji; nie zmienia specyfikacji MVP.
- **Ocena:** poprawność i błędy, czas, koszt; realizm i rozumienie tylko pobocznie.
- **Prompty:** część przygotowania wariantów, bez osobnego badania technik
  promptowania; decyzja autora z 15 listopada 2026.
- **Modele:** tańsze, droższe i o otwartych wagach, przez API lub lokalnie.
  Konkretne modele i środowiska nie są wybrane.
- **Rezultat:** rekomendacje i kompromisy między poprawnością, czasem i kosztem,
  zamiast wymuszania jednego zbiorczego rankingu; zaakceptowano 15 listopada 2026.

## Status pytań szczegółowych

Identyfikatory zachowano z wcześniejszego planu. Pełne brzmienie i zastrzeżenia
zawiera sekcja 7 planu; nie jest to lista zatwierdzonych eksperymentów.

| ID | Aktualny status |
| --- | --- |
| PB-01 — modele | Kierunek uzgodniony; dopracowanie brzmienia powinno objąć pełne kryterium sukcesu. |
| PB-02 — prompty | Starsza propozycja; decyzją autora z 15 listopada 2026 poza głównym zakresem. Prompty pozostają częścią przygotowania procesów. |
| PB-03 — role | Wybrano trzy role tego samego modelu; szczegółowy przebieg odłożono. |
| PB-04 — pomoc deterministyczna | Wybrano porównanie całego procesu aplikacji z czystym LLM, nie izolowany pomiar wpływu walidatora lub kodu pomocniczego. |
| PB-05 — złożoność | Porównujemy prostsze i trudniejsze schematy; nie wybrano poziomów i scenariuszy. |

## Granice obecnych ustaleń

Nie wykonano pomiarów ani nie wykazano przewagi żadnego wariantu.
Porównanie aplikacji z czystym LLM nie izoluje wpływu walidatora:
zmieniają się również kontekst, liczba wywołań i organizacja procesu.
Opinia reviewera nie zastępuje deterministycznej oceny sukcesu.

Wstępna literatura nie wykazała nowości projektu. Przed zamrożeniem protokołu
warto uzupełnić dostęp do pełnego tekstu najbliższej pracy DEXA,
opisanej jako L-01 w literaturze. Nie wykonano nowego przeglądu w ramach
obecnego porządkowania dokumentacji.

## Następny krok i sprawy odłożone

**Teraz:** ogólny zakres jest uzgodniony. Nie rozwijamy szczegółów protokołu
i nie wracamy do rozstrzygniętego PB-02.

**Po uzyskaniu aplikacji, przed właściwymi pomiarami:** ustalić modele,
scenariusze, warunki porównania, powtórzenia, limity, mierniki i zachowanie
materiałów. Nie podano terminu, budżetu ani formalnych wymagań uczelni.
Nie wracamy przez to do wyboru wskazanego już przez autora celu.

Organizacja badań i materiały pozostają poza aplikacją, która w MVP
nie zapewnia historii wykonań ani pełnego archiwum promptów.
Nie dodano funkcji aplikacji i nie zatwierdzono płatnych prób.
