# Architektura i wielu dostawców

## Rozpoznanie modelu i dostawcy przed implementacją

Gdy zadanie wskazuje konkretny model, wykonaj research internetowy **przed**
pisaniem jego integracji. Tak samo postępuj przy zmianie dostawcy lub migracji
modelu. Zakres badań dopasuj do używanej funkcji, nie do całego katalogu dostawcy.

1. **Tożsamość i dostępność:** potwierdź dokładny identyfikator/rewizję modelu,
   sposób hostowania i endpoint, wersję API, wymagany dostęp, region oraz status
   wsparcia/deprecacji. Nie utożsamiaj aliasu z niezmienną wersją ani modelu
   z usługą hostującą. Niejasny identyfikator wyjaśnij z użytkownikiem.
2. **Praca z modelem:** przeczytaj model card i oficjalny przewodnik promptowania
   dla tej rodziny/wersji. Sprawdź zalecaną strukturę instrukcji, role, przykłady,
   obsługę kontekstu i dostępne ustawienia generacji/reasoning. Uwzględnij
   structured output, narzędzia, streaming i modalności tylko, gdy są potrzebne.
   Nie przenoś bez dowodu zaleceń z innego modelu.
3. **SDK i kontrakt API:** przeczytaj oficjalną dokumentację, przykłady oraz
   istotne release notes dla wersji SDK w projekcie. Potwierdź inicjalizację,
   autoryzację, kształt żądań/wyników, async/streaming, timeouty, anulowanie,
   domyślne retry i raportowanie usage w zakresie potrzebnym integracji.
   Sprawdź zgodność API/SDK/modelu; konieczną aktualizację zależności uzgodnij,
   zamiast robić ją przy okazji.
4. **Efektywna współpraca z dostawcą:** sprawdź aktualne limity kontekstu/wyjścia,
   rate limits, błędy i backoff, ceny oraz dostępne mechanizmy cache, batch
   i zarządzania współbieżnością. Zbadaj zasady retencji/przetwarzania danych.
   Wybieraj mechanizmy adekwatne do zadania i uzgodnionego budżetu; oszczędność
   nie uzasadnia samowolnej zmiany jakości, prywatności lub opóźnienia.
5. **Wniosek do implementacji:** przedstaw krótko „co potwierdzono → jak wpływa
   to na kod/prompt/testy → co wymaga decyzji”, podając źródła i datę sprawdzenia.
   Istotne ustalenia utrwal w istniejącej dokumentacji integracji lub opisie PR,
   bez kopiowania podręcznika dostawcy.

Preferuj oficjalną dokumentację, model cards, repozytoria SDK, changelogi
i przykłady dostawcy. Otwórz i przeczytaj odpowiednie strony, nie poprzestawaj
na wynikach wyszukiwania. Materiały społecznościowe traktuj pomocniczo jako
hipotezy do sprawdzenia; przy konflikcie szukaj aktualnego źródła pierwotnego.
Dokumentacja opisuje deklarowane wsparcie, a test potwierdza działanie
w środowisku projektu. Jeśli brak dokumentacji lub dostępu blokuje ustalenie
kontraktu, zgłoś to użytkownikowi; nie implementuj zgadywanego API.
W zapytaniach wyszukiwarki nie ujawniaj sekretów ani poufnych danych projektu.

## Granice, nie framework na zapas

- Zachowuj konwencje projektu. Wydziel odpowiedzialności: przypadek użycia,
  składanie promptu, walidacja, polityka wykonania oraz adapter API.
  Nie muszą oznaczać osobnych klas, pakietów czy usług.
- Kod domenowy nie powinien importować SDK dostawcy ani interpretować jego
  surowych wyjątków. Minimalny kontrakt wyprowadzaj z faktycznych potrzeb.
  Zależności kieruj ku kontraktom aplikacji, a SDK zamknij w adapterach.
- Stosuj czytelne nazwy, małe spójne funkcje, jawne efekty uboczne i konfigurację.
  Duplikację reguł usuwaj, ale nie łącz pozornie podobnych przepływów
  o innych wymaganiach. SOLID/DRY/KISS/YAGNI to wskazówki, nie nakaz tworzenia
  hierarchii klas i fabryk. Komentarz wyjaśnia przyczynę, nie przepisuje kodu.
- Zaproponuj najprostszy przepływ spełniający wymagania; złożoną orkiestrację
  uzasadniaj wynikiem ewaluacji lub rzeczywistym ograniczeniem.

## Kontrakt adaptera

Ustal tylko potrzebne elementy:

- wejście: instrukcje/wiadomości, identyfikator modelu, parametry, opcjonalny
  schemat odpowiedzi i narzędzia, deadline i anulowanie;
- wynik: treść lub dane strukturalne, przyczyna zakończenia, model i wersja,
  identyfikator żądania oraz dostępne usage;
- błędy: konfiguracja/uwierzytelnienie, nieobsługiwana funkcja, limit,
  awaria przejściowa, timeout, odmowa, ucięcie i niepoprawny wynik.

Brak usage oznacza „nieznane”, nie zero. Koszt wyliczony z estymacji tokenów
nie jest kosztem potwierdzonym przez dostawcę. Zachowaj potrzebne metadane
specyficzne dla dostawcy bez rozlewania zależności po domenie.

Przed wysłaniem sprawdzaj możliwości wybranego modelu: structured output,
obsługiwany podzbiór schematów, tool calling, streaming, modalności, parametry,
kontekst i limity wyjścia. Nie ignoruj nieobsługiwanego parametru po cichu.
Ta sama nazwa parametru nie gwarantuje tego samego zachowania. Wymagaj testów
kontraktowych dla każdego adaptera, także serwera „OpenAI-compatible”.
Model, dostawca i endpoint muszą być rozróżnialne w konfiguracji i diagnostyce.

## Niezawodność i skalowanie

- Utrzymuj jednoznaczną odpowiedzialność za retry. Uzgodnij limity SDK
  z limitem orkiestracji; zagnieżdżone retry mogą mnożyć liczbę wywołań.
- Timeout, anulowanie i łączny budżet propaguj przez całą ścieżkę.
  Stosuj ograniczoną współbieżność i backpressure, nie nieograniczone zadania.
  Kolejkę, circuit breaker lub batch dodawaj wtedy, gdy uzasadnia je obciążenie.
- Retry awarii przejściowych może korzystać z backoff/jitter i wskazań API.
  Błędu autoryzacji lub schematu żądania nie naprawia ponawianie tego samego.
- Timeout po wysłaniu nie dowodzi, że dostawca nic nie wykonał i nie naliczył.
  Dla narzędzi z efektami ubocznymi stosuj idempotencję/deduplikację lub
  uzgodnienie stanu. Nie odtwarzaj całego workflow w ciemno.
- Częściowy stream nie jest gotowym wynikiem. Rozróżnij zakończenie, przerwanie,
  ucięcie i odmowę; nie łącz fragmentów z dwóch prób jak jednej odpowiedzi.
- Fallback/routing uzgadniaj względem funkcji, jakości, prywatności, regionu,
  kosztu i dostępności. Niedostępność jednego API nie upoważnia do wysłania
  danych innemu dostawcy. Nie ukrywaj użytego fallbacku.

## Bezpieczeństwo i obserwowalność

- Dane użytkownika, dokumenty i wynik modelu traktuj jako niezaufane dane,
  nie instrukcje systemowe. Oddzielanie sekcji pomaga, lecz nie eliminuje
  prompt injection. Uprawnienia, walidacja i autoryzacja muszą działać poza LLM.
- Nie wykonuj wygenerowanego kodu, SQL ani wywołań narzędzi bez sprawdzenia
  argumentów, uprawnień i skutków. Ogranicz dostęp do niezbędnego zakresu.
- Sekrety trzymaj poza repozytorium i promptami. W logach domyślnie zapisuj
  metadane zamiast pełnej treści; redaguj PII i sekrety. Retencję i użycie
  danych do ewaluacji uzgadniaj. „Loguj wszystko” nie jest zasadą dla danych poufnych.
- Mierz model/wersję promptu, etap, próby, przyczyny błędów, czas, usage,
  cache i wynik walidacji; identyfikator korelacji łączy cały workflow.
  Metryki nie powinny ujawniać surowego promptu ani danych osobowych.

## Podstawa zaleceń

Źródła sprawdzone 2026-11-14. To zasady projektowe, nie wymaganie używania
technologii z przykładów. Przed konkretną integracją odczytaj aktualną
dokumentację wybranego dostawcy i wersji.

- [Google Engineering Practices: code review](https://google.github.io/eng-practices/review/reviewer/looking-for.html) — projekt, złożoność, nazwy, komentarze i testy.
- [Microsoft: common application architectures](https://learn.microsoft.com/en-us/dotnet/architecture/modern-web-apps-azure/common-web-application-architectures) — separacja odpowiedzialności i kierunek zależności; nie nakaz .NET ani mikroserwisów.
- [Anthropic: Building effective agents](https://www.anthropic.com/research/building-effective-agents) — proste, kompozycyjne przepływy; szczegóły dawnych narzędzi mogą być nieaktualne.
- [OWASP: Prompt Injection](https://genai.owasp.org/llmrisk/llm01-prompt-injection/) — granice zaufania i obrona warstwowa.
