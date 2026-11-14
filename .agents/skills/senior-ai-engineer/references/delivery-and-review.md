# Dostarczenie zmiany: commity → PR → review → merge

## Zakres upoważnienia

Docelowy workflow obejmuje logiczne commity, PR, kolejne rundy review i merge.
Stosuj go w zakresie faktycznie zleconej pracy: instrukcja roli nie jest
bezterminową zgodą na publikację lub mergowanie dowolnej przyszłej zmiany.
Jeśli użytkownik zlecił cały cykl wraz z merge, nie pytaj ponownie o każdy
standardowy krok. Sama konsultacja lub prośba o kod nie oznacza zgody
na push, publiczny PR, merge, wdrożenie ani płatne wywołania.
Jeśli brak jasnego upoważnienia do potrzebnej operacji, poproś o nie przed nią.

## Logiczne commity

- Sprawdź instrukcje repozytorium, stan pracy, gałąź i diff. Przed commitem
  obejrzyj staged diff; dodawaj tylko własne, uzgodnione zmiany.
  Nie nadpisuj ani nie włączaj cudzych zmian.
- Dziel po spójnym, zrozumiałym rezultacie: kod, odpowiednie testy i dokumentacja
  mogą stanowić jeden commit. Nie twórz osobnego commita na każdy plik
  ani niesprawnego pośredniego stanu tylko dla liczby commitów.
- Korzystaj z konwencji projektu. Gdy jej brak, używaj Conventional Commits:
  `type(scope): imperative summary`, po angielsku; scope jest opcjonalny.
  Podsumowanie ma mówić, co konkretnie zmieniono.
- W razie potrzeby dodaj body: dlaczego, istotny kompromis, wpływ na kompatybilność
  i powiązane zadanie. Breaking change oznacz zgodnie z konwencją.
  „update”, „fix stuff”, „WIP” i deklaracje bez pokrycia nie są dobrym opisem.
- Przykłady: `feat(llm): add provider capability validation`,
  `fix(llm): bound repair attempts by request deadline`,
  `test(llm): cover malformed structured responses`.
- Przed pushem potwierdź remote i gałąź. Nie force-pushuj i nie przepisuj
  opublikowanej historii bez osobnego uzgodnienia. Nie omijaj hooków.

## Pull request

Sprawdź gałąź docelową, cały diff i szablon PR. Jeśli cel jest niejasny, zapytaj.
Tytuł ma przedstawiać rezultat. Opis powinien ułatwiać review, nie być dziennikiem:

- **Cel i zakres:** co zmieniono, po co, powiązane wymagania/issue.
- **Realizacja:** istotne decyzje, adaptery/prompty i zmiany kontraktów.
- **Weryfikacja:** rzeczywiste testy i wyniki; przy optymalizacji baseline,
  wynik, model/wersja i warunki, także zaobserwowane regresje.
- **Ryzyka i użycie:** konfiguracja, migracja, prywatność, koszty, ograniczenia
  i rollback, jeśli zmiana go wymaga. Wskaż niewykonane sprawdzenia.

Nie publikuj sekretów, surowych danych użytkownika ani poufnych promptów.
Przy niejednoznacznym wyniku utworzenia PR najpierw sprawdź stan, zamiast
tworzyć duplikat. Jeśli aplikacja udostępnia narzędzie do załączenia PR do chatu,
po utworzeniu użyj go z faktycznym URL.

## Wiele rund review

- Przygotuj zmianę do zewnętrznego code review; samodzielny przegląd własnego
  kodu nie oznacza niezależnego approve. Po publikacji PR przekaż go do review
  zgodnie z procesem repozytorium. Nie wybieraj samowolnie reviewera ani
  nie uruchamiaj dodatkowego agenta bez odpowiedniego upoważnienia.
  Jeżeli reviewer lub sposób przekazania nie jest określony, uzgodnij to
  z użytkownikiem. Nie pomijaj oczekiwanego review tylko dlatego, że CI jest zielone.
- Dla każdej uwagi przeczytaj kontekst i aktualny diff. Zasadną uwagę wdroż,
  dodaj właściwą regresję, uruchom weryfikację i odpowiedz dowodem/commitem.
  Publikuj poprawki na tym samym PR.
- Jeśli się nie zgadzasz, dyskutuj rzeczowo w odpowiednim wątku: wymaganie,
  dowód z kodu/testu/eval, kompromis i propozycja rozwiązania. Nie ignoruj uwagi
  ani nie wprowadzaj jej tylko dlatego, że pochodzi od reviewera.
- Spór o wymagania, budżet, prywatność lub architekturę eskaluj użytkownikowi.
  Własna odpowiedź nie jest zgodą reviewera. Nie zamykaj nierozstrzygniętej uwagi
  jako wdrożonej. Po poprawkach zastosuj zasady zespołu dotyczące re-review.
- Po każdej rundzie sprawdź kontrole dla aktualnego HEAD i ważność approvals.
  Konflikty rozwiązuj zachowując intencję zmian, nie mechanicznym wyborem strony;
  ponownie przetestuj połączone zachowanie.
- Nie zakładaj ciągłego monitorowania po zakończeniu sesji. Jeśli review
  jeszcze nie ma, podaj stan oczekiwania. Monitoring/automatyzację ustawiaj
  wyłącznie na zlecenie; nie odpytuj bez końca.

## Merge i faktyczne zakończenie

Gdy merge został zlecony, wykonaj go dopiero po sprawdzeniu aktualnego HEAD,
wymaganych approvals, rozwiązania blokujących uwag, zielonych wymaganych
kontroli i braku konfliktów. Jeśli review lub kontrola jest w toku, poczekaj
w ramach dostępnej sesji lub zgłoś oczekiwanie — nie obchodź zabezpieczeń.
Zastosuj ustaloną metodę merge; jeśli nie wynika z polityki repo, uzgodnij ją.
Potwierdź stan zdalny i identyfikator wyniku. „Gotowy do merge” nie znaczy
„zmergowany”; merge nie oznacza automatycznej zgody na deploy.

## Źródło konwencji

[Conventional Commits 1.0.0](https://www.conventionalcommits.org/en/v1.0.0/)
— sprawdzone 2026-11-14. Repozytorium może mieć inną uzgodnioną konwencję;
nie zmieniaj jej tylko na potrzeby tego skilla.
