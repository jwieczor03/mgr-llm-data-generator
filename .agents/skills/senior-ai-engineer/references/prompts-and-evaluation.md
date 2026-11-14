# Prompty, pętle naprawcze i pomiar

## Prompt jako wersjonowana część implementacji

- Ustal zadanie, źródła prawdy, format, reguły domenowe i zachowanie przy braku
  danych. Nie każ modelowi dopowiadać braków, gdy wymagania tego nie dopuszczają.
- Oddziel instrukcje od danych; dawaj tylko potrzebny kontekst i reprezentatywne
  przykłady. Dobieraj strukturę do modelu, zamiast kopiować jeden „superprompt”
  do wszystkich dostawców. Nie wymagaj ujawniania prywatnego toku rozumowania;
  proś o wynik i potrzebne weryfikowalne uzasadnienie lub źródła.
- Wersjonuj szablon, kontrakt wejścia/wyjścia, schemat i konfigurację generacji.
  Dane wejściowe wstawiaj bezpiecznie; nie sklejaj instrukcji z niezaufanym tekstem.
- Jeśli funkcja jest obsługiwana, rozważ structured output. Następnie sprawdź
  parsowanie, schemat i reguły domeny w kodzie. Schemat nie zapewnia poprawności
  faktów. Walidacja merytoryczna wymaga uzgodnionego źródła odniesienia.
- RAG, fine-tuning i łańcuchy promptów rozważ dopiero po diagnozie problemu.
  Wprowadzenie dodatkowego wywołania wymaga mierzalnej korzyści.

## Dwie różne pętle

**Retry transportowe** obsługuje kwalifikujące się awarie API bez zakładania,
że wynik jest merytorycznie błędny. **Repromptowanie** następuje po uzyskaniu
odpowiedzi, której określony walidator nie zaakceptował.

Przed implementacją ustal limity wywołań/prób (jasno: łącznie czy poza pierwszą
próbą), tokenów, kosztu i czasu oraz zachowanie po wyczerpaniu. Nie wymyślaj
wartości jako wymagań. Uwzględniaj retry SDK, fallbacki, oceniające modele
i podwywołania w jednym budżecie żądania.

Przepływ naprawczy:

1. Wygeneruj wynik i sklasyfikuj przyczynę zakończenia.
2. Zastosuj walidację składni, schematu i potwierdzonych reguł domenowych.
3. Jeśli naprawa ma sens i budżet na nią pozwala, przekaż krótki, konkretny
   feedback walidatora oraz minimalny niezbędny kontekst. Błędną odpowiedź
   dołączaj jako niezaufane dane, nie nowe instrukcje.
4. Sprawdź nową odpowiedź od początku. Wykryj powtarzający się błąd lub brak
   postępu; nie powiększaj bez końca historii rozmowy.
5. Po sukcesie zwróć zaakceptowany wynik; po limicie lub błędzie nienaprawialnym
   zakończ kontrolowanym błędem/eskalacją zgodną z ustalonym kontraktem.

Nie naprawiaj w ten sposób braku dostępu, złego żądania ani sprzecznych wymagań.
Odmowy nie traktuj jako zachęty do obchodzenia zabezpieczeń. Ucięcie odpowiedzi
wymaga osobnej diagnozy limitu/kontekstu. Nigdy nie zwracaj ostatniej niepoprawnej
odpowiedzi jako sukcesu ani nie poluzowuj walidatora, aby zakończyć pętlę.
Jeśli używasz modelu-oceniającego, niech nie będzie jedynym sędzią reguł,
które można sprawdzić deterministycznie.

## Optymalizacja na danych

- Najpierw zmierz baseline. Porównuj tę samą dystrybucję zadań i warunki,
  zapisując model/wersję, prompt, parametry, próbki i konfigurację środowiska.
- Uwzględniaj tokeny wejścia, wyjścia, cache i reasoning zgodnie z rozliczeniem
  dostawcy. Nie licz podwójnie nakładających się kategorii. Używaj właściwego
  tokenizera lub endpointu count; heurystykę znaków oznacz jako przybliżenie.
- Budżet kontekstu obejmuje instrukcje, historię, narzędzia, schematy i rezerwę
  wyjścia; zarezerwuj także przestrzeń kolejnej naprawy. Nie obcinaj po cichu
  reguł domeny, dowodów ani krytycznych danych wejściowych.
- Najpierw usuń zbędne wywołania, duplikaty i nadmiar kontekstu/wyjścia.
  Cache prefiksu, cache wyniku, batch, mniejszy model, routing i równoległość
  oceniaj osobno; każde ma inne skutki jakościowe i operacyjne.
- Cache wyniku musi uwzględniać wejście, model, prompt, parametry, uprawnienia
  i aktualność danych. Nie współdziel poufnych wyników między użytkownikami.
- Raportuj koszt całego zaakceptowanego wyniku, również nieudane próby
  i oceny, odsetek napraw/błędów oraz opóźnienie end-to-end. Dla streamingu
  rozdziel czas pierwszego tokenu i całej odpowiedzi. Percentyle podawaj
  z liczebnością próby; mały smoke test nie daje wiarygodnego p95.

## Ewaluacje i regresja

- Uzgodnij z użytkownikiem reprezentatywne przypadki i kryteria jakości:
  typowe, brzegowe, braki danych, błędne formaty i istotne nadużycia.
  Nie wymyślaj „złotych” odpowiedzi dla nieznanych reguł biznesowych.
- Oddziel zbiór rozwojowy od holdoutu; nie dostrajaj promptu do wszystkich
  przypadków, a potem nie przedstawiaj tego jako dowodu generalizacji.
- Deterministycznie sprawdzaj kontrakty i inwarianty. Jakość otwartej odpowiedzi
  oceniaj rubryką; LLM-as-judge kalibruj ocenami człowieka i sprawdzaj jego
  uprzedzenia. Nie wymagaj identycznego tekstu, jeśli istotna jest semantyka.
- Zapisuj wersję zbioru, rubric/gradera, modelu, promptu i konfiguracji.
  Powtarzaj próby proporcjonalnie do zmienności i uzgodnionego kosztu.
  `temperature=0` lub seed nie są gwarancją pełnej deterministyczności.
- Testy kodu powinny obejmować granice limitów, anulowanie, koniec bez sukcesu,
  odmowę, ucięcie, błędy serializacji, nieobsługiwane funkcje i retry SDK.
  Adaptery testuj na fixture/kontrolowanym serwerze, a zgodność z dostawcą
  dodatkowo zatwierdzonym testem live. Domyślne lokalne CI nie wymaga sekretów
  ani płatnych wywołań; testy live uruchamiaj jako jawną, ograniczoną ścieżkę.
- Zmiana baseline, progu lub usunięcie próbki wymaga merytorycznej przyczyny,
  nie wygody implementacji. Reguła diagnozy porażki z głównego skilla
  obowiązuje również dla ewaluacji statystycznych.

## Podstawa zaleceń

Źródła sprawdzone 2026-11-14. Stosuj zasady pomiaru niezależnie od produktu
do ewaluacji; przed wyborem konkretnej usługi sprawdź jej aktualny cykl życia.

- [OpenAI: Prompt engineering](https://developers.openai.com/api/docs/guides/prompt-engineering) — kontrakty, instrukcje i wersjonowanie.
- [Google: Prompt design strategies](https://aistudio.google.com/docs/prompting-strategies) — jasność, przykłady i iteracyjne dopasowanie.
- [Anthropic: Building effective agents](https://www.anthropic.com/research/building-effective-agents) — chaining, bramki walidacji i kompromisy złożoności.
- [OpenAI: Evaluation best practices](https://developers.openai.com/api/docs/guides/evaluation-best-practices) — ewaluacje zadaniowe, rzeczywiste dane i kalibracja z człowiekiem.
- [OpenAI: Latency optimization](https://developers.openai.com/api/docs/guides/latency-optimization) — mierzenie i ograniczanie zbędnej pracy.
