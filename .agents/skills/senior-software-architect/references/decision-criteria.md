# Kryteria decyzji architektonicznych

Czytaj sekcje istotne dla bieżącej decyzji. To narzędzie porównania, nie obowiązkowa ankieta ani nakaz zastosowania konkretnej architektury.

## Cel i wymagania jakościowe

- Jaki problem lub ograniczenie rozwiązujemy i po czym poznamy poprawę? Czy problem wynika z pomiaru, konkretnego przepływu, czy jest hipotezą?
- Które jakości są tu najważniejsze: łatwość zmian, wydajność, niezawodność, bezpieczeństwo, koszt, użyteczność operacyjna? Wskaż konflikty, np. spójność danych kontra dostępność w czasie awarii.
- Ogólne „szybko” i „skalowalnie” zamień na scenariusz: **w jakich warunkach → jakie zdarzenie → oczekiwana odpowiedź → miara akceptacji**. Wartości progowe uzgodnij; nie wymyślaj SLA, ruchu, RTO/RPO ani budżetu.
- Oddziel potrzeby dziś od wiarygodnego wzrostu i spekulacji. Uwzględnij koszt opóźnienia oraz koszt ewentualnej zmiany decyzji.

## Wybór lub zmiana technologii

Porównuj tylko kryteria wpływające na wybór:

- Dopasowanie do wymagań, obecnego stosu, środowiska wdrożenia i kontraktów; ograniczenia i dojrzałość potrzebnych funkcji.
- Kompetencje zespołu, dostępność narzędzi i bibliotek, łatwość diagnozowania i onboardingu, utrzymywalność przez juniora.
- Aktualny stan wsparcia, polityka aktualizacji, zgodność wersji, bezpieczeństwo łańcucha dostaw i licencja. Przy kwestii prawnej zaznacz potrzebę właściwej weryfikacji, nie deklaruj zgodności z samej nazwy licencji.
- Łączny koszt: rozwój, nauka, migracja, infrastruktura, obsługa awarii, aktualizacje i wyjście z rozwiązania. Aktualną cenę potwierdzaj dla właściwego planu i założeń użycia, bez fikcyjnej precyzji estymat.
- Uzależnienie od dostawcy, eksport/przenoszenie danych, możliwość wymiany i odwracalność decyzji.
- Nie wprowadzaj nowej technologii tylko z powodu trendu. Nie odrzucaj jej wyłącznie dlatego, że jest nowa. Przedstaw dowody i braki wiedzy; nie stosuj arbitralnej punktacji maskującej kompromisy. Wagi, jeśli potrzebne, uzgodnij z użytkownikiem.

## Architektura i jakość kodu

- Granice modułów zgodne z odpowiedzialnością biznesową; jawna własność danych, reguł i kontraktów. Sprawdź cykle i przeciekanie szczegółów między obszarami.
- Spójność reguł, kontrola efektów ubocznych, czytelne interfejsy, testowalność i możliwość niezależnej zmiany. Uzasadniaj problem skutkiem, np. zmiana jednej reguły wymaga edycji kilku niespójnych implementacji.
- Obsługa błędów i zależności: timeouty, retry, idempotencja, anulowanie, częściowe niepowodzenie — wtedy, gdy dany przepływ ich potrzebuje.
- Uprawnienia i granice zaufania, walidacja wejścia, wrażliwe dane i sekrety, retencja oraz audyt, stosownie do zakresu.
- Dobieraj zabezpieczenia do ryzyka: test reguły biznesowej, kontrakt/integracja, krytyczny e2e, reguła zależności modułów, typecheck/lint. Każde ma chronić konkretne zachowanie; nie narzucaj pełnego zestawu narzędzi ani celu coverage bez powodu.
- SOLID, DRY, DDD, CQRS czy Clean Architecture nie są wynikami analizy. Proponuj wzorzec dopiero po nazwaniu problemu, korzyści i kosztu. Rozdzielenie modułów nie wymaga rozdzielenia usług.

## Skalowalność i eksploatacja

- Rozpoznaj charakter pracy: synchroniczna/asynchroniczna, CPU/I/O, rozmiar i przyrost danych, równoległość, piki, limity integracji. Najpierw wskaż prawdopodobne wąskie gardło i brakujący pomiar.
- Oceń wpływ zapytań i indeksów, transakcji, blokad, puli połączeń, kolejek, cache i limitów; nie proponuj ich wszystkich z góry. Przy cache uwzględnij nieaktualność i unieważnianie; przy kolejce duplikaty, opóźnienia i zaległości.
- Rozważ odporność na przeciążenie, limity zasobów, obserwowalność, odtwarzanie po awarii oraz koszt utrzymania. Skalowanie infrastruktury nie naprawia automatycznie modelu danych czy algorytmu.
- Przy braku danych zaproponuj ograniczony eksperyment: hipoteza, reprezentatywny scenariusz, potrzebne dane, metryki, uzgodniony próg i decyzja zależna od wyniku. Nie uruchamiaj go ani nie implementuj w tej roli.

## Zmiana istniejącego rozwiązania

- Wykaż przewagę nad pozostawieniem stanu obecnego i najmniejszym usprawnieniem. Uwzględnij okres przejściowy oraz nowe tryby awarii.
- Preferuj etapy możliwe do sprawdzenia, jeśli pasują do problemu. Pełne przepisanie też wymaga uzasadnienia; nie wykluczaj ani nie wybieraj go odruchowo.
- Opisz zgodność kontraktów, migrację i walidację danych, kolejność zależności, przełączenie oraz warunki odwrotu. Jeżeli po zapisie nowych danych rollback jest niemożliwy lub stratny, nazwij to i omów kopię/odtworzenie lub naprawę do przodu.
- Zaproponuj sygnał do ponownej oceny decyzji, np. przekroczenie uzgodnionego limitu lub zmiana wymagania, zamiast projektować na dowolną przyszłą skalę.

## Źródła i sposób ich stosowania

Sprawdzone 2026-11-14. To podstawy rozumowania, nie aktualny katalog produktów ani obowiązkowy formalny proces. Przy rekomendacji konkretnej technologii sięgnij osobno do jej bieżącej dokumentacji.

- **CMU SEI — Architecture Tradeoff Analysis Method (ATAM)**: https://www.sei.cmu.edu/library/architecture-tradeoff-analysis-method-collection/ — ocena względem celów jakościowych, scenariuszy, ryzyk i kompromisów. Stosuj tę logikę proporcjonalnie; zwykłej konsultacji nie nazywaj przeprowadzonym formalnym ATAM.
- **AWS Well-Architected — General design principles**: https://docs.aws.amazon.com/wellarchitected/latest/framework/general-design-principles.html — pomiary, eksperymenty i ewolucja zamiast zgadywania pojemności. Materiał jest chmurowy; nie oznacza rekomendacji AWS ani wymogu użycia chmury.
- **Martin Fowler — Monolith First**: https://martinfowler.com/bliki/MonolithFirst.html — koszt złożoności rozproszenia i trudność ustalania granic z góry. Autor zaznacza ograniczenia dowodów; to nie uniwersalny zakaz mikroserwisów.
- **Michael Nygard — Documenting Architecture Decisions**: https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions — krótkie zapisy kontekstu, decyzji, statusu i konsekwencji; zachowanie historii zastąpionych decyzji.
- **Simon Brown — C4 model, Diagrams**: https://c4model.com/diagrams — dobór poziomu diagramu do odbiorcy i celu; nie trzeba tworzyć wszystkich czterech poziomów.

Kryteria powyżej są praktyczną syntezą na potrzeby tej roli, nie cytatem ani deklaracją zgodności ze standardem. Gdy rekomendacja wynika z wnioskowania, odróżniaj ją od twierdzeń źródła.
