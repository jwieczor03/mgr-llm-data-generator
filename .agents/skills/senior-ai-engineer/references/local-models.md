# Modele lokalne: wykonalność przed instalacją

## Zbierz fakty

Sprawdź dostępne, niesekretne dane środowiska albo poproś użytkownika o:

- system i architekturę CPU, RAM, GPU/VRAM lub pamięć zunifikowaną, wolny dysk;
- model/rewizję, format i kwantyzację, wymagane modalności oraz kontekst;
- długość wejścia/wyjścia, współbieżność, akceptowalne opóźnienie i jakość;
- wymóg offline, prywatność, zastosowanie i ograniczenia licencji.

Nie zakładaj, że komputer bieżącej sesji jest maszyną docelową.
Nie potrzebujesz całej inwentaryzacji do ogólnego wyjaśnienia; do konkretnej
rekomendacji ujawnij brakujące parametry i ich wpływ.

## Oszacuj uczciwie

Rozdziel: **da się załadować**, **da się wykonać wymagany kontekst** oraz
**spełnia oczekiwaną jakość i wydajność**. Pierwsze nie dowodzi kolejnych.

- Same wagi to w przybliżeniu liczba parametrów × liczba bitów / 8 bajtów,
  ale to tylko dolne przybliżenie. Uwzględnij format/metadane, runtime, bufory,
  KV cache, kontekst, batch/współbieżność i pamięć potrzebną systemowi.
  Rozmiar pliku nie jest wiarygodnym kompletnym pomiarem RAM/VRAM.
- Nie dodawaj RAM i VRAM jak jednej puli; pamięć zunifikowana jest współdzielona.
  Offload CPU/GPU i swap zmieniają wydajność. Nie obiecuj tokens/s bez benchmarku.
- Sprawdź wsparcie backendu dla konkretnego OS/GPU, modelu i kwantyzacji
  w oficjalnej dokumentacji runtime oraz model card właściciela modelu.
  Nie wybieraj runtime wyłącznie na podstawie nazwy API.
- Niższa kwantyzacja i krótszy kontekst mogą zmniejszyć zużycie pamięci,
  lecz wpływ na zadanie trzeba zmierzyć. Nie proponuj zakupu sprzętu
  na podstawie samego rozmiaru wag.

Werdykt przedstaw jako: potwierdzony pomiarem, warunkowo wykonalny ze wskazaniem
warunków, niewykonalny na podanych zasobach albo brak danych. Szacunek nie jest
testem; nie wydawaj pewnego werdyktu, jeśli warunki są nieznane.

## Dobór i konfiguracja

- Rozważ istniejący runtime projektu. Ollama, llama.cpp i vLLM to kandydaci,
  nie obowiązkowy stack. Wybór uzasadniaj wsparciem sprzętu, formatu modelu,
  sposobem integracji i wymaganym obciążeniem.
- Dla wybranego rozwiązania podaj aktualne, właściwe dla OS kroki: instalacja,
  pobranie konkretnego modelu/rewizji, konfiguracja kontekstu i zasobów,
  start lokalnego endpointu, test minimalny i sposób zatrzymania.
  Polecenia najpierw sprawdź w oficjalnej dokumentacji dla wybranej wersji.
- Przed wykonaniem uzgodnij istotne zmiany systemowe, pobranie dużych wag,
  licencję oraz ewentualne koszty. Nie uruchamiaj w ciemno `curl | sh`,
  nie zmieniaj konfiguracji systemu na podstawie samej prośby o poradę.
- Domyślnie rekomenduj nasłuch loopback. Wystawienie do sieci wymaga świadomej
  decyzji, kontroli dostępu i ochrony transportu.
- Lokalny endpoint nie dowodzi przetwarzania offline. Sprawdź faktyczne miejsce
  inferencji, cloud fallback, telemetrię i zewnętrzne narzędzia. Jeśli wymagane
  jest offline, zweryfikuj działanie bez sieci po przygotowaniu zależności.

## Potwierdzenie działania

Uruchom najpierw pojedyncze reprezentatywne zadanie, potem wymagany kontekst
i obciążenie w uzgodnionych limitach. Zmierz pamięć szczytową, czas pierwszego
tokenu, czas całości, błędy i jakość na tym samym zestawie co wariant chmurowy.
Uwzględnij zimny start i rozgrzany runtime, jeżeli mają znaczenie.
Sprawdź adapter, chat template, tokenizer, structured output/tool calling,
zakończenie generacji i anulowanie, jeżeli funkcja ich wymaga.

Zapisz model/rewizję, kwantyzację, runtime/wersję, sprzęt, kontekst i parametry.
Bez tego wynik nie jest przenośną rekomendacją. Jeśli środowisko nie pozwala
na próbę, daj instrukcję weryfikacji użytkownikowi i oznacz brak pomiaru.

## Źródła do doboru konkretnej konfiguracji

Sprawdzone 2026-11-14; przed instalacją zweryfikuj ponownie. Nie utrwalaj
w skillu tabel „model X zawsze wymaga Y GB” ani rankingu najlepszych modeli.

- [Ollama: Local FAQ](https://docs.ollama.com/faq) — kontekst, CPU/GPU, konfiguracja i rozróżnienie local/cloud.
- [llama.cpp: build documentation](https://github.com/ggml-org/llama.cpp/blob/master/docs/build.md) — budowanie i backendy sprzętowe.
- [vLLM: Online Serving](https://docs.vllm.ai/en/latest/serving/online_serving/) — uruchamianie serwera i warstwa API; nie gwarancja zgodności wszystkich funkcji.
- Dodatkowo odczytaj model card, licencję i wymagania **wybranego** modelu
  w repozytorium jego właściciela. Brak wybranego modelu nie upoważnia
  do zgadywania licencji ani parametrów.
