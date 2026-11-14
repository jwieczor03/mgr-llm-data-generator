# Kryteria review

Wybierz sekcje właściwe dla zmiany. To pytania diagnostyczne, nie wymóg dopisywania każdej warstwy, komentarza lub rodzaju testów. Punktem odniesienia są kontrakty i wymagania projektu.

## Poprawność i odporność

- Czy nowe zachowanie spełnia wymagania, a zmiana nie psuje istniejących callerów, formatów danych, API, konfiguracji ani kompatybilności?
- Czy reprezentatywne wartości graniczne, puste/brakujące dane, błędne wejście i częściowa awaria dają zamierzony wynik? Sprawdź jednostki, zaokrąglenia i strefy czasowe, jeśli wpływają na logikę.
- Czy błędy są propagowane lub obsługiwane bez udawania sukcesu? Czy zasoby są zwalniane również po wyjątku i anulowaniu?
- Przy współbieżności: czy współdzielony stan i kolejność operacji powodują race condition, deadlock lub podwójny efekt? Przy retry: czy operacja jest idempotentna albo chroni przed duplikatem?
- Przy bazie/migracjach: oceń atomowość, integralność, blokady i zgodność z kolejnością wdrożenia. Cofnięcie kodu nie musi bezpiecznie cofać migracji danych.

## Czytelność, clean code i utrzymywalność

- Czy nazwy ujawniają intencję i domenę? Czy kod ma czytelny przepływ sterowania, jawne zależności i przewidywalne efekty uboczne?
- Czy moduł ma spójną odpowiedzialność? Sygnałem problemu są niezależne powody zmiany i trudne testowanie, nie sama liczba linii.
- Czy typy i kontrakty ograniczają niepoprawne stany? Czy nieuzasadnione casty, wyłączenia lintera i obchodzenie typechecka ukrywają problem?
- Czy powielono wiedzę biznesową, którą trzeba aktualizować równolegle? Nie łącz przypadkowo podobnego kodu w trudną, wielowariantową abstrakcję tylko dla DRY.
- Czy zmiana pasuje do granic modułów i wzorców repozytorium? Nie utrwalaj jednak istniejącej luki lub błędu w imię spójności.
- Preferuj udokumentowane konwencje i istniejący formatter. Nie zgłaszaj ręcznie każdego błędu formatowania, który jedno narzędzie potrafi zbiorczo wykryć.

## Prostota i skalowalność bez overengineeringu

- Czy dodatkowa warstwa, fabryka, interfejs, konfigurowalność lub zależność realizuje aktualną potrzebę? Czy zwykła funkcja lub istniejąca biblioteka wystarczy?
- Porównaj koszt proponowanego uproszczenia: liczba pojęć, zależności, punktów konfiguracji i trudność testowania; nie tylko liczbę linii.
- Nie żądaj elastyczności „na przyszłość” ani mikroserwisów, cache czy kolejki bez wymagań. Nie usuwaj uzasadnionych granic bezpieczeństwa i transakcji w imię prostoty.
- Oceniaj wzrost przy realnym lub jasno oznaczonym zakładanym wolumenie: czy liczba zapytań, pamięć lub czas nie rosną nieakceptowalnie? Nie zakładaj nieskończonej skali.

## Komentarze i dokumentacja

- Wymagaj wyjaśnienia tam, gdzie z kodu nie wynika istotna decyzja: reguła biznesowa, ograniczenie integracji, workaround, invariant współbieżności, nietrywialny algorytm.
- Nie wymagaj komentarza do każdej funkcji lub linii. Jeśli komentarz tłumaczy tylko zawiłą implementację, najpierw rozważ prostszy kod lub lepszą nazwę.
- Sprawdź zgodność istniejących komentarzy i dokumentacji z nowym zachowaniem. Fałszywy komentarz może być gorszy niż jego brak.
- Dokumentacja publicznego kontraktu powinna ujawniać ograniczenia i istotne efekty uboczne. Zmiana uruchamiania, konfiguracji lub API może wymagać aktualizacji instrukcji.

## Testy

- Dla nowego/zmienionego zachowania wymagaj ochrony odpowiedniej do ryzyka; już istniejące testy mogą ją zapewniać. Dla bugfixa preferuj test reprodukujący błąd, który zawiedzie przed poprawką.
- Unit test sprawdza regułę; integration test granicę systemów, bazę lub kontrakt; e2e krytyczny przepływ użytkownika. Nie żądaj wszystkich poziomów dla każdej zmiany.
- Sprawdź istotne ścieżki błędu, granice i regresje; dla uprawnień uwzględnij odmowę dostępu, nie tylko sukces.
- Czy asercje sprawdzają wymagany wynik, stan lub efekt? Test „nie rzuca wyjątku”, snapshot bez kontroli lub mock zwracający oczekiwany wynik może niczego nie chronić.
- Czy mocki nie zastępują właśnie zmienionej logiki i nie fałszują kontraktu? Czy fixture odzwierciedla realne ograniczenia?
- Czy testy są izolowane i deterministyczne? Szukaj zależności od czasu, kolejności, sieci i współdzielonego stanu. Coverage jest wskazówką, nie kryterium poprawności ani sztywnym progiem z tego skilla.

## Wydajność i koszty

- Śledź konkretną ścieżkę: N+1, zagnieżdżone skany, blokujące I/O, nieograniczone pobieranie, brak paginacji, kosztowna serializacja, nadmiar renderów lub alokacji.
- Oceń wzrost liczby zapytań/wywołań, timeouty, limity i backpressure. Cache wymaga oceny unieważniania i izolacji użytkowników.
- Zgłoszenie ma zawierać mechanizm oraz warunki: rozmiar wejścia, częstotliwość lub zmieniony koszt. Jeśli potrzeba pomiaru, poproś o profil/benchmark zamiast podawać wymyślone czasy.
- Nie proponuj mikrooptymalizacji bez wykazanego znaczenia. Rozróżniaj oczywisty problem złożoności od niepotwierdzonego podejrzenia.

## Bezpieczeństwo i prywatność

- Prześledź niezaufane wejście do operacji wrażliwej oraz miejsce faktycznego egzekwowania kontroli. Walidacja w UI nie zastępuje kontroli po stronie zaufanej.
- Sprawdź tożsamość, autoryzację obiektu/operacji i izolację tenantów, również dla odczytu, eksportu, cache i zadań asynchronicznych.
- Zależnie od kodu sprawdź injection, XSS, CSRF, SSRF, traversal, uploady i deserializację. Uwzględnij rzeczywiste zachowanie frameworka i biblioteki; nie zgłaszaj podatności z samego dopasowania wzorca.
- Oceń ekspozycję sekretów/PII w logach, błędach i odpowiedziach, uprawnienia domyślne, zarządzanie sesją i granice zużycia zasobów. Nie cytuj wartości sekretu w raporcie.
- Dla kodu LLM/narzędzi: czy niezaufana treść może zmienić instrukcje, uruchomić uprzywilejowaną akcję lub ujawnić dane? Oceniaj egzekwowanie uprawnień poza samym promptem.
- Dla nowych zależności i CI sprawdź potrzebę, uprawnienia i pochodzenie; przy podejrzeniu CVE weryfikuj konkretną wersję w źródle producenta/advisory.
- To ukierunkowane review zmiany, nie certyfikacja bezpieczeństwa. Sygnalizuj potrzebę osobnego audytu, gdy ryzyko przekracza zweryfikowany zakres.

## Źródła i ich zastosowanie

Źródła sprawdzono 2026-11-13. Poniżej własna synteza kryteriów, nie kopia standardów. W razie wątpliwości technologicznej odczytaj właściwą aktualną dokumentację; nie trzeba otwierać wszystkich źródeł przy każdym review.

- [Google Engineering Practices — What to look for in a code review](https://google.github.io/eng-practices/review/reviewer/looking-for.html): punkt odniesienia dla oceny projektu zmiany, testów, czytelności, komentarzy i unikania nadmiernej ogólności. Pomaga oddzielić istotną uwagę od osobistej preferencji stylistycznej.
- [Martin Fowler — Yagni](https://martinfowler.com/bliki/Yagni.html): uzasadnienie unikania spekulatywnych funkcji i abstrakcji; nie usprawiedliwia rezygnacji z utrzymywalności ani testów.
- [OWASP — Secure Code Review Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Secure_Code_Review_Cheat_Sheet.html): punkt odniesienia dla review granic zaufania, przepływu danych, kontroli dostępu i logiki biznesowej. Wyniki skanerów wspierają analizę, ale jej nie zastępują.
