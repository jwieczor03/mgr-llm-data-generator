# mgr-llm-data-generator

Aplikacja do generowania syntetycznych danych testowych dla wielu powiązanych tabel PostgreSQL na podstawie schematu DDL, reguł biznesowych i polecenia w języku naturalnym.

Wynikiem są polecenia `INSERT` albo paczka CSV. Aplikacja ma sprawdzać kompletność i importowalność danych, wykonywać ograniczoną liczbę poprawek oraz zachowywać historię wykonania.

## Status

Projekt jest na etapie specyfikacji i projektu architektury. Repozytorium zawiera dokumentację, nie gotową aplikację. Zapisano kierunki technologiczne i szczegółową propozycję serwisów; konkretne wersje, część mechanizmów i fizyczny podział nadal wymagają potwierdzenia. Instrukcja uruchomienia powstanie wraz z działającym rozwiązaniem.

MVP jest jednoosobowe i uruchamiane lokalnie. Jego zakres nie obejmuje obowiązkowego wdrożenia AWS, generowania samodzielnych dokumentów JSON ani automatycznej platformy eksperymentalnej.

Interfejs działa w lokalnej przeglądarce. Model przygotowuje gotowy SQL albo treść CSV; aplikacja zapisuje, sprawdza i udostępnia wynik. Przerwanego wykonania nie wznawia się — ręczne ponowienie tworzy nową próbę od początku.

Naruszenia danych uruchamiają automatyczne poprawki, domyślnie do 3 rund dla całego wykonania. Błąd techniczny kończy wykonanie bez automatycznego retry lub zmiany wariantu; użytkownik może uruchomić nową próbę.

Architektura ma uwzględniać późniejsze hostowanie, logowanie, wielu użytkowników i skalowanie wykonania. W MVP przygotowujemy granice tych rozszerzeń, ale nie wdrażamy kont ani publicznego hostingu (REQ-066).

Zapisane kierunki to PostgreSQL jako źródło danych i wersji schematów, opcjonalny pgvector zamiast obowiązkowej osobnej bazy wektorowej oraz własny kontrakt LLM z LiteLLM SDK jako preferowaną implementacją po testach. Szczegółowy projekt korzysta z bazowego wariantu Python/FastAPI + React/TypeScript i proponuje trzy własne serwisy backendowe: zarządzanie, generowanie i walidację.

## Dokumentacja

| Dokument | Rola i status |
| --- | --- |
| [Specyfikacja MVP](docs/specyfikacja_mvp.md) | Obowiązujące wymagania, kryteria wykonania i akceptacji oraz jawne otwarte decyzje. Punkt wyjścia do pracy nad aplikacją. |
| [Rejestr ustaleń architektonicznych](docs/ustalenia_architektoniczne.md) | Zapis wymagań, kierunków LLM i bazy danych oraz statusów propozycji i otwartych decyzji. |
| [Serwisy i technologie](docs/serwisy_i_technologie.md) | Szczegółowa propozycja funkcji, narzędzi, kontraktów, własności danych, API, testów i lokalnego uruchomienia każdego komponentu. |
| [Architektura ogólna](docs/architektura.md) | Aktualny roboczy szkic odpowiedzialności, własności danych i przepływu, z uzgodnionym rozróżnieniem błędów technicznych i naruszeń danych. Podział procesów pozostaje propozycją. |
| [Analiza technologii](docs/analiza_technologii.md) | Wstępne porównanie FastAPI, NestJS i Django oraz narzędzi interfejsu, modeli, walidacji i uruchomienia. Rekomendacja do weryfikacji, nie zatwierdzony stos. |
| [Przepływy funkcjonalne](docs/przeplywy_funkcjonalne.md) | Objaśnienie zachowania opisanego w specyfikacji, bez narzucania architektury i technologii. |
| [Podział implementacji](docs/podzial_implementacji.md) | Robocza propozycja: własna logika produktu, gotowe mechanizmy i wymienne adaptery. Nie zatwierdza technologii ani liczby mikroserwisów. |
| [Przygotowanie do hostowania](docs/przygotowanie_do_hostowania.md) | Uzgodniony kierunek rozwoju i proponowane granice przyszłego logowania, izolacji danych i skalowania; bez wdrażania tych funkcji w MVP. |
| [Plan badań](docs/plan_badan.md) | Robocze pytania badawcze, proponowane warianty i zachowane hipotezy. Nie jest listą zatwierdzonych eksperymentów ani dodatkowymi wymaganiami MVP. |
| [Archiwum koncepcji](docs/archiwum/README.md) | Historyczne materiały zachowane do wglądu. Nie stanowią aktualnych wymagań ani wyborów technologicznych. |

W razie rozbieżności obowiązuje specyfikacja MVP. Dokumenty uzupełniające nie rozszerzają jej zakresu samodzielnie.

## Wykorzystanie w badaniach

Autor będzie ręcznie zmieniał modele lokalne i płatne modele przez API, prompty oraz organizację procesu, a następnie wykonywał te same zlecenia. Aplikacja zachowa dane i prosty raport potrzebny do późniejszego porównania całego procesu.

Realizm danych będzie oceniany poza generatorem, ewentualnie z pomocą LLM i przyszłego osobnego narzędzia. Docelowo aplikacja będzie korzystać z wariantu wybranego na podstawie badań.

## Jak czytać wymagania

- **Wykonanie zadania:** uzyskano kompletny wynik możliwy do poprawnego importu.
- **Zgodność biznesowa:** raport opisuje spełnienie poszczególnych dodatkowych reguł; ich naruszenia mogą pozostać w wykonanym zadaniu.
- **Realizm:** ocena zewnętrzna, nie automatyczna gwarancja generatora.

Lista nierozstrzygniętych szczegółów znajduje się w sekcji 16 specyfikacji. Nie należy zastępować tych decyzji założeniami zaczerpniętymi z archiwum.
