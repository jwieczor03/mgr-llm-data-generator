# Dyskusja i wielorundowe review

## Punkt odniesienia i zakres

- Dla każdej rundy odnotuj oceniony head SHA, bazę/merge-base i zakres pokrycia. W kolejnej rundzie odczytaj poprzedni raport, odpowiedzi autora, aktualny stan PR-a i CI dla właściwej rewizji. Użyj istniejących identyfikatorów komentarzy albo własnych stabilnych ID.
- Przy niezmienionej historii porównaj ostatni faktycznie przejrzany head z aktualnym head, nie tylko ostatni commit. Sprawdź wszystkie zmiany od review, również niezwiązane z uwagami. Wcześniejsze nieprzejrzane fragmenty pozostają luką do uzupełnienia.
- Przeczytaj otoczenie poprawek, callerów i testy potrzebne do sprawdzenia skutków. To, że plik nie zmienił się od poprzedniej rundy, nie wyklucza regresji w nim wskutek zmienionego kontraktu.
- Dla lokalnych zmian sam HEAD ani lista plików nie identyfikują poprzedniego stanu staged/unstaged/untracked. Review przyrostowe wymaga dostępnego wcześniejszego snapshotu/diffa z zawartością objętą review. Jeśli go nie ma, ponownie oceń aktualny uzgodniony zakres i wyjaśnij powód. Nie twórz commitów ani plików w repozytorium tylko dla pamięci review.
- Rebase/force-push nie oznacza automatycznie konieczności czytania wszystkiego od nowa, ale podważa porównanie zwykłą listą nowych commitów. Gdy stare rewizje są dostępne, porównaj serie patchy (np. `git range-diff`) oraz aktualny łączny diff PR-a; nie traktuj samego mapowania commitów jako dowodu równoważności zachowania.
- Zmiana bazy/merge-base wymaga sprawdzenia, jak zmienił się kontekst integracji i łączny diff. Poszerz review, gdy zmieniono kontrakty, model danych, uprawnienia, architekturę lub wspólne mechanizmy. Pełne review wykonaj, gdy wpływ jest przekrojowy, poprzedniego zakresu nie da się wiarygodnie odtworzyć lub użytkownik tego żąda. Sam upływ kolejnej rundy nie wymaga pełnego review.
- Przed końcowym podsumowaniem sprawdź, czy oceniony stan nadal odpowiada bieżącemu. Jeśli head się przesunął, wyraźnie wskaż nowe nieprzejrzane zmiany; nie rozciągaj rekomendacji na nieznaną rewizję.

## Reakcja na odpowiedź autora

Ustal, czy autor dostarczył nowy dowód, wyjaśnił wymaganie, zaproponował równoważną naprawę czy świadomie akceptuje ryzyko. Odnieś się do jego rzeczywistego argumentu, a nie powtarzaj pierwotnego komentarza.

- Jeśli problem zabezpiecza inna warstwa, zweryfikuj, czy obejmuje kwestionowaną ścieżkę. Po potwierdzeniu wycofaj uwagę i krótko wyjaśnij błędne założenie.
- Jeśli poprawka różni się od zaproponowanej, oceń osiągnięty rezultat. Nie wymagaj swojej implementacji, gdy alternatywa spełnia kontrakt i usuwa ryzyko.
- Jeśli dowody nadal potwierdzają problem, pokaż konkretny scenariusz, test lub ścieżkę wywołania. Przy sporze o wymaganie zadaj pytanie rozstrzygające.
- Jeśli brakuje dowodów, nazwij niepewność i potrzebną weryfikację. Nie przedstawiaj domysłu jako pewnika, ale też nie traktuj braku reprodukcji jako dowodu braku błędu.
- Jeśli rozbieżność sprowadza się do stylu bez wymogu projektowego i istotnego kosztu, uznaj ją za nieblokującą.
- Gdy po wymianie argumentów brakuje nowych faktów, podsumuj spór i decyzję potrzebną od właściciela wymagania/ryzyka. Nie przeciągaj dyskusji przez powtarzanie tego samego.

## Stan wcześniejszych uwag

Zachowaj ID przy zmianie lokalizacji, priorytetu lub treści; podaj powód korekty. Używaj stanów:

| Stan | Kiedy go użyć |
| --- | --- |
| Otwarta | Problem nadal istnieje; wskaż aktualne dowody. |
| Do wyjaśnienia | Oczekuje na konkretną informację lub weryfikację; nie udawaj rozstrzygnięcia. |
| Naprawiona | Zmiana usuwa wskazaną przyczynę; podaj sposób sprawdzenia i ograniczenia, np. test przeczytany, lecz nieuruchomiony. |
| Wycofana | Uwaga była nietrafiona lub nie dotyczy aktualnego zakresu; podaj powód. |
| Ryzyko zaakceptowane | Uprawniony decydent jawnie zaakceptował opisany skutek; odnotuj przez kogo i w jakim zakresie. To nie znaczy „naprawiona”. |

Zapewnienie autora lub ręczne oznaczenie wątku jako resolved nie zastępuje weryfikacji. Nie przyjmuj akceptacji ryzyka od dowolnego komentującego. Akceptacja nie zmienia technicznej oceny; pozostałe ryzyko ma być widoczne w rekomendacji.

## Nowe ustalenia i domknięcie rundy

- Szukaj regresji wprowadzonych poprawkami. Nie wymagaj wykonania poprzednio sugerowanej zmiany, jeśli problem skutecznie rozwiązano inaczej.
- Nie ukrywaj istotnego problemu przeoczonego wcześniej, ale nazwij go jako nowe ustalenie dotyczące wcześniej obecnego kodu. Nie wymyślaj nowych wymagań i stylistycznych blokad w każdej rundzie.
- Dobierz ponowne testy do poprawek i ich wpływu. Poprzedni wynik CI nie dowodzi poprawności nowego head.
- Podsumuj krótko: tryb i rewizje rundy, statusy wcześniejszych uwag, nowe findings, wyniki sprawdzeń, luki i rekomendację. Zamknięta uwaga nie znika z historii, ale nie musi być ponownie szczegółowo opisywana.
- Zakończ rundę po ocenie dostępnych dowodów. Nie czekaj w pętli na commity ani odpowiedzi; następna runda wymaga kolejnego zlecenia. Przegląd przyrostowy nie jest pełną ponowną oceną całego PR-a — nazwij ten zakres wprost.
