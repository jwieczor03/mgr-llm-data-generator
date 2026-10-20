# mgr-llm-data-generator

Aplikacja do generowania syntetycznych danych testowych dla wielu powiązanych tabel PostgreSQL na podstawie schematu DDL, reguł biznesowych i polecenia w języku naturalnym.

Wynikiem są polecenia `INSERT` albo paczka CSV. Aplikacja ma sprawdzać kompletność i importowalność danych, wykonywać ograniczoną liczbę poprawek oraz zachowywać historię wykonania.

## Status

Projekt jest na etapie specyfikacji. Repozytorium zawiera dokumentację, nie gotową aplikację. Technologie i szczegóły implementacji nie zostały wybrane; instrukcja uruchomienia powstanie wraz z działającym rozwiązaniem.

MVP jest jednoosobowe i uruchamiane lokalnie. Jego zakres nie obejmuje obowiązkowego wdrożenia AWS, generowania samodzielnych dokumentów JSON ani automatycznej platformy eksperymentalnej.

## Dokumentacja

| Dokument | Rola i status |
| --- | --- |
| [Specyfikacja MVP](docs/specyfikacja_mvp.md) | Obowiązujące wymagania, kryteria wykonania i akceptacji oraz jawne otwarte decyzje. Punkt wyjścia do pracy nad aplikacją. |
| [Przepływy funkcjonalne](docs/przeplywy_funkcjonalne.md) | Objaśnienie zachowania opisanego w specyfikacji, bez narzucania architektury i technologii. |
| [Plan badań](docs/plan_badan.md) | Robocze pytania badawcze, proponowane warianty i zachowane hipotezy. Nie jest listą zatwierdzonych eksperymentów ani dodatkowymi wymaganiami MVP. |
| [Archiwum koncepcji](docs/archiwum/README.md) | Historyczne materiały zachowane do wglądu. Nie stanowią aktualnych wymagań ani wyborów technologicznych. |

W razie rozbieżności obowiązuje specyfikacja MVP. Przepływy i plan badań nie rozszerzają jej zakresu samodzielnie.

## Wykorzystanie w badaniach

Autor będzie ręcznie zmieniał modele lokalne i płatne modele przez API, prompty oraz organizację procesu, a następnie wykonywał te same zlecenia. Aplikacja zachowa dane i prosty raport potrzebny do późniejszego porównania całego procesu.

Realizm danych będzie oceniany poza generatorem, ewentualnie z pomocą LLM i przyszłego osobnego narzędzia. Docelowo aplikacja będzie korzystać z wariantu wybranego na podstawie badań.

## Jak czytać wymagania

- **Wykonanie zadania:** uzyskano kompletny wynik możliwy do poprawnego importu.
- **Zgodność biznesowa:** raport opisuje spełnienie poszczególnych dodatkowych reguł; ich naruszenia mogą pozostać w wykonanym zadaniu.
- **Realizm:** ocena zewnętrzna, nie automatyczna gwarancja generatora.

Lista nierozstrzygniętych szczegółów znajduje się w sekcji 16 specyfikacji. Nie należy zastępować tych decyzji założeniami zaczerpniętymi z archiwum.
