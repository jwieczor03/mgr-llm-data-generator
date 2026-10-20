## 6. Środowisko Uruchomieniowe i Ścieżka Migracji (Chmura AWS)
Zgodnie z wymogami środowiska korporacyjnego Capgemini, projekt opiera się na dwufazowym cyklu życia (SDLC), co pozwala na bezpieczne prototypowanie i ostateczne skalowanie w chmurze.

### Faza 1: Środowisko Deweloperskie (DEV - Lokalnie)
* **Cel:** Szybkie tworzenie Proof of Concept (PoC), implementacja logiki walidacyjnej i testowanie architektury hybrydowej.
* **Infrastruktura:** Lokalne stacje robocze dewelopera.
* **Technologia:** Uruchamianie modeli otwartych z wykorzystaniem technik kwantyzacji (GGUF/EXL2) w celu zapewnienia wydajności na zasobach stacji roboczej[cite: 1]. Serwowanie modeli poprzez narzędzie Ollama[cite: 2].

### Faza 2: Środowisko Produkcyjne (PROD - Chmura AWS)
* **Cel:** Testy wydajnościowe na rzeczywistych, złożonych strukturach danych Capgemini, uruchomienie pełnowymiarowych modeli oraz weryfikacja środowisk Multi-Agent.
* **Infrastruktura:** Zamknięte środowisko chmurowe (AWS Virtual Private Cloud). Takie rozwiązanie gwarantuje zachowanie najwyższych standardów bezpieczeństwa cyfrowego (Data Sovereignty), eliminując ryzyko eksfiltracji danych do zewnętrznych, publicznych usług chmurowych[cite: 1].
* **Potencjalne usługi docelowe:** 
  * *Amazon Bedrock:* Do bezserwerowego odpytywania komercyjnych modeli (np. Claude 3.5).
  * *Amazon EC2 z GPU:* Do hostowania własnych modeli Open Source z użyciem serwera vLLM, zoptymalizowanego pod masową produkcję danych[cite: 2].

### Warstwa Abstrakcji (LLM Gateway)
Kluczowym założeniem architektonicznym ułatwiającym migrację jest zunifikowany router (np. LiteLLM)[cite: 2]. Działa on jako pośrednik obsługujący standaryzację komunikacji do API[cite: 2]. Dzięki temu przejście z Fazy 1 (localhost) do Fazy 2 (AWS) wymaga jedynie zmiany konfiguracji (adresów endpointów), pozostawiając główny kod aplikacji w Pythonie (walidatory, parser, frontend) w stanie nienaruszonym.