# Rejestr ustaleń architektonicznych

**Data:** 21 października 2026.

**Status:** zapis dotychczasowych ustaleń i kierunków projektowych. Nie jest potwierdzeniem działania bibliotek ani zgodności konkretnych wersji.

**Podstawa:** [specyfikacja MVP](specyfikacja_mvp.md), rozmowa o technologiach, adapterze LLM i przechowywaniu kontekstu.

## 1. Jak rozumieć status decyzji

- **Uzgodnione wymaganie** — zachowanie określone w specyfikacji.
- **Zapisany kierunek** — rozwiązanie, na którym opieramy dalszy projekt, z zachowaniem podanych warunków.
- **Propozycja szczegółowa** — konkretna rekomendacja przygotowana do oceny; nie zatwierdza samodzielnie otwartych decyzji specyfikacji.
- **Otwarte** — wybór nadal wymaga rozstrzygnięcia albo próby technicznej.

Polecenie zapisania ustaleń nie oznacza przyjęcia nieomówionej reprezentacji reguł, całego dialektu PostgreSQL, konkretnych wersji zależności ani dowolnego sposobu wykonywania SQL.

## 2. Wymagania zachowane bez zmian

| Obszar | Ustalenie |
| --- | --- |
| Uruchomienie | Lokalna aplikacja webowa, jeden użytkownik, bez logowania w MVP. |
| Rozwój | Granice umożliwiające przyszłe hostowanie, tożsamość użytkowników, izolację danych i współbieżne wykonania; nie wdrażamy ich na zapas. |
| Wejście i wynik | DDL PostgreSQL, reguły i polecenie; model przygotowuje gotowy SQL `INSERT` albo treść CSV. |
| Walidacja | Najpierw składnia i format, potem typy, schemat, relacje i kompletność, na końcu dodatkowe reguły biznesowe. |
| Poprawki | Naruszenia danych uruchamiają ograniczone poprawki, domyślnie maksymalnie 3 globalne rundy po pierwszym wygenerowaniu. |
| Błędy techniczne | Zatrzymanie bez automatycznego retry i bez przełączenia modelu lub wariantu. |
| Przerwanie | Można anulować; nie ma wznawiania po anulowaniu, błędzie ani utracie procesu. Ręczne ponowienie tworzy nowe wykonanie. |
| Historia | Niezmienne wymagania wykonania, rozróżnialni kandydaci, rzeczywiste wiadomości i dostępne pomiary; bez poświadczeń. |
| Ocena | Sukces wymaga kompletności i importowalności. Dodatkowe naruszenia biznesowe są odrębne, realizm oceniamy poza generatorem. |
| Zachowanie kandydata | Późniejsza nieudana poprawka nie usuwa wcześniejszego kompletnego i importowalnego wyniku. Raport i eksport dotyczą tego samego kandydata. |

## 3. Zapisane kierunki technologiczne

| ID | Kierunek | Status i warunek |
| --- | --- | --- |
| DA-01 | Wymienność przez Ports & Adapters, wstrzykiwanie zależności i testy kontraktowe. | Zapisany kierunek. Mikroserwisy nie zastępują stabilnych kontraktów. |
| DA-02 | PostgreSQL jako podstawowy magazyn danych aplikacji, wersji schematów i historii. | Zapisany kierunek po omówieniu baz. Nie oznacza współdzielenia kont i danych z walidatorem. |
| DA-03 | Oryginalny DDL oraz model strukturalny i wersje jako źródło prawdy. | Zapisany kierunek. Embedding nie zastępuje dokładnej definicji. |
| DA-04 | Bez osobnej bazy wektorowej w bazowym MVP; opcjonalnie pgvector w PostgreSQL. | Zapisany kierunek. Dodanie embeddingów po wykazaniu potrzeby, nie obowiązkowa funkcja. |
| DA-05 | Dobór kontekstu za `ContextProvider`; początkowo schemat i jawne zależności. | Zapisany kierunek. Późniejszy wariant hybrydowy nie może pomijać obowiązkowych zależności ani zmieniać zatwierdzonego zakresu. |
| DA-06 | Własny port `LlmClient` oraz `LiteLlmAdapter` wykorzystujący LiteLLM Python SDK. | Preferowany kierunek dla backendu Python. Przyjęcie zależności wymaga testów wiadomości, metryk i braku ponowień oraz przeglądu konkretnej wersji. |
| DA-07 | LiteLLM jako biblioteka w usłudze generowania, bez osobnego Proxy/Gateway. | Zapisany kierunek dla MVP. Bezpośredni adapter SDK dostawcy pozostaje rozwiązaniem zastępczym pod tym samym portem. |
| DA-08 | Nie piszemy własnych mechanizmów technicznych, jeśli pasujące rozwiązanie jest dostępne. | Zapisany kierunek: gotowe API HTTP, parser, baza, migracje, inferencja, UI i narzędzia testowe; własna semantyka produktu i integracja. |

LiteLLM pozostaje zależnością warunkową. W [analizie technologii](analiza_technologii.md), sekcja 8.1, zapisano incydent łańcucha dostaw dotyczący wydań PyPI `1.82.7` i `1.82.8`, wymagania przeglądu wersji i testów. Nie przyjmujemy automatycznie żadnego wydania jako bezpiecznego.

## 4. Bazowy wariant do szczegółowego projektowania

Do rozpisania serwisów wykorzystujemy **wariant A: Python + FastAPI oraz TypeScript + React** z [analizy technologii](analiza_technologii.md).

To wybrana podstawa tego projektu szczegółowego, a nie twierdzenie, że porównanie z NestJS i Django zostało zakończone prototypami. Nadal trzeba potwierdzić komfort samodzielnego code review i zgodność zależności.

| Element | Proponowane narzędzia | Status |
| --- | --- | --- |
| Interfejs | TypeScript, React, Vite, Mantine; TanStack Query do danych serwera. | Propozycja szczegółowa. |
| Backend zarządzający | Python, FastAPI, Pydantic, SQLAlchemy, Alembic, Psycopg. | Propozycja szczegółowa. |
| Generowanie | Python, FastAPI, LiteLLM za własnym adapterem. | Propozycja szczegółowa z kierunkiem DA-06. |
| Walidacja | Python, FastAPI, parser SQL, `csv`; Psycopg i osobny PostgreSQL przy wyborze próbnego importu. | Propozycja szczegółowa, zależna od OD-01 i OD-02. |
| Lokalny model | Ollama jako gotowe środowisko udostępniania modeli. | Preferowany kandydat, bez wyboru modelu i pobierania go. |
| Komunikacja | HTTP + JSON + OpenAPI, HTTPX po stronie klientów Python. | Propozycja szczegółowa, bez brokera w bazowym MVP. |
| Uruchomienie | Docker Compose; lokalny magazyn artefaktów za adapterem. | Propozycja szczegółowa. |
| Narzędzia jakości | uv, Ruff, mypy, pytest, Playwright. | Propozycja szczegółowa, wersje po próbie zgodności. |

Projekt zakłada trzy własne procesy backendowe: zarządzanie, generowanie i walidację, plus aplikację przeglądarkową. Backend zarządzający zawiera osobne moduły projektów i wykonań, a nie osobne mikroserwisy dla każdej tabeli. Fizyczny podział pozostaje rekomendacją do oceny.

Szczegółowe funkcje, operacje, kontrakty i granice opisano w [serwisach i technologiach](serwisy_i_technologie.md).

## 5. Co nadal jest otwarte

1. **OD-01:** macierz obsługiwanych typów, konstrukcji DDL, ograniczeń i wersji dialektu.
2. **OD-02:** potwierdzenie mechanizmu importowalności. Próbny import do odizolowanego PostgreSQL jest rekomendacją, nie przyjętym wymaganiem.
3. **OD-03:** reguła wyboru między kilkoma użytecznymi kandydatami, bez domyślnej zbiorczej punktacji.
4. **OD-04–OD-06:** dokładny profil SQL/CSV, raport, wykonywalna postać reguł oraz ich prezentacja do zatwierdzenia.
5. **OD-07–OD-09:** wartości timeoutów, szczegóły anulowania, dostępność artefaktów po błędzie oraz retencja.
6. **OD-10–OD-12:** warianty badawcze, kontrakt przekazania plików przez model, modele i sprzęt oraz szczegóły UI.
7. Parser: SQLGlot jako pierwszy kandydat do próby; pglast tylko po ocenie zgodności i licencji.
8. Wykonawca długich operacji: ograniczony lokalny wykonawca za portem `ExecutionRunner`; gotowe narzędzie dopiero, jeśli zmniejszy nakład i spełni zasady braku retry i wznowień.
9. Konkretne wersje języków, bibliotek i obrazów; pliki blokad oraz przegląd bezpieczeństwa i licencji.

Nie zamykamy tych punktów samym wyborem frameworka. Pełna lista znaczeń OD pozostaje w specyfikacji.

## 6. Co zostało wykonane

Zapisano dokumentację i sprawdzono jej spójność. Nie zaimplementowano serwisów, nie zainstalowano pakietów, nie utworzono baz, nie pobrano modeli i nie wykonano płatnych wywołań.
