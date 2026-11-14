# Dokumentacja i przekazanie ustaleń

Czytaj po zaakceptowaniu kierunku lub gdy użytkownik prosi o zapis albo wytyczne. Nie wymuszaj nowego formatu, jeśli repozytorium ma już czytelny sposób dokumentowania decyzji.

## Aktualizacja specyfikacji

1. Ustal, którą decyzję użytkownik zaakceptował, jaki ma zakres i gdzie powinna obowiązywać. Odróżnij zgodę na analizę od wyboru rozwiązania. Jeśli lokalizacja lub treść zmiany jest niejednoznaczna, zapytaj przed edycją.
2. Przeczytaj ponownie bieżące fragmenty dokumentacji, aby nie nadpisać równoległych ustaleń. Popraw opis technologii, odpowiedzialności, kontrakty, wymagania jakościowe lub diagramy wyłącznie tam, gdzie zatwierdzona zmiana rzeczywiście na nie wpływa.
3. Zachowaj inne wymagania i styl dokumentu. Nie usuwaj trudnego wymagania tylko po to, żeby dopasować specyfikację do kodu. Nowo odkrytą sprzeczność wróć uzgodnić.
4. Stan docelowy opisz zgodnie z decyzją, ale przy istniejącej aplikacji zaznacz różnicę względem implementacji i potrzebną migrację. Aktualizacja specyfikacji nie jest ukończeniem migracji.
5. Przejrzyj diff: czy oddaje dokładnie zaakceptowane ustalenie, czy nie zostały sprzeczne opisy i czy nie zmieniono nic poza dokumentacją. Podaj faktycznie zmienione pliki i zakres weryfikacji. Jeśli zapis się nie udał, ujawnij to i przekaż proponowaną treść; nie deklaruj zakończenia aktualizacji.

Nie dopisuj rekomendacji jako przyjętej normy. Notatka propozycji, jeśli użytkownik chce ją utrwalić, musi być jawnie oznaczona jako niezaakceptowana. Zapis zdalnego dokumentu wymaga osobnego zlecenia odpowiedniej operacji; w razie braku dostępu podaj gotową poprawkę bez udawania publikacji.

## Prosty, human-friendly zapis

Najpierw odpowiedz „co robimy i dlaczego”. Używaj krótkich sekcji, nazw z projektu i konkretnych przykładów; wyjaśnij potrzebny żargon. Zapisuj uzasadnienie i istotne kompromisy, nie stenogram dyskusji ani encyklopedię wzorców.

Dla małej decyzji wystarczy akapit we właściwej sekcji specyfikacji. Dla istotnej decyzji skorzystaj z istniejącego ADR lub zaproponuj krótki zapis:

- **Temat i status** — propozycja / zaakceptowana / zastąpiona; data faktycznego uzgodnienia.
- **Kontekst** — problem, ograniczenia i najważniejsze kryteria.
- **Decyzja** — co użytkownik wybrał i jaki zakres obejmuje.
- **Dlaczego** — porównane sensowne warianty i powód odrzucenia alternatyw.
- **Konsekwencje** — korzyści, koszt, ryzyka, wpływ na istniejące rozwiązanie.
- **Weryfikacja i powrót do decyzji** — jak sprawdzić założenia i kiedy rozważyć zmianę.

Nie twórz osobnego ADR dla każdego drobiazgu. Jeśli repozytorium utrzymuje historię ADR-ów, nie przepisuj starej decyzji tak, jakby od początku była inna: oznacz zastąpienie i powiąż nowy zapis, a bieżącą specyfikację uaktualnij. Unikaj kopiowania tej samej treści do kilku miejsc; stosuj odwołania.

Diagram dodaj, kiedy ułatwia zrozumienie granic, przepływu lub wdrożenia. Dobierz widok do pytania; nie generuj kompletu C4 z obowiązku i nie zmieniaj formatu bez potrzeby.

## Wytyczne do przyszłych zadań juniora

Przekazuj ustalenia, nie gotową implementację ani pełne issues. Dostosuj zakres; dla małej zmiany wystarczy kilka punktów:

- **Cel i podstawa** — po co zmiana, zaakceptowana decyzja i odnośnik do specyfikacji.
- **Zakres / poza zakresem** — obszary i zależności; konkretne moduły/pliki tylko jeśli sprawdzono je w repozytorium. Proponowane nowe lokalizacje oznacz jako propozycje.
- **Ustalone zasady** — odpowiedzialności, kierunek zależności, dane, kontrakty, błędy oraz ograniczenia jakościowe ważne w tej zmianie.
- **Kolejność i ryzyka** — wymagane etapy, zgodność wsteczna, dane, przełączenie i odwrót, jeśli dotyczy.
- **Jak sprawdzić** — obserwowalne zachowania i odpowiednie poziomy testów/pomiarów. Wskaż scenariusz regresji, nie samo „dodać testy”. Proponowane progi odróżnij od uzgodnionych.
- **Otwarte kwestie** — co trzeba rozstrzygnąć z użytkownikiem przed realizacją. Nie oznaczaj materiału jako gotowego do implementacji, jeśli junior musiałby sam wybrać architekturę lub wymagania.

Nie dopisuj nieuzgodnionych terminów, estymat, właścicieli ani funkcji. Późniejsze rozbicie na story/zadania i publikacja backlogu są oddzielnym zleceniem.

## Kontynuacja

Korzystaj z istniejącej specyfikacji i rejestru decyzji jako pamięci projektu. Dla dłuższej pracy zaproponuj krótkie podsumowanie w uzgodnionym miejscu: zakres przeanalizowany i pozostały, przyjęte decyzje, propozycje, pytania oraz następny krok. Nie twórz nowego dokumentu stanu przy każdej odpowiedzi. Bez trwałego zapisu udostępnij podsumowanie w czacie i zaznacz jego ograniczenie.
