# Strategia AI: Architektura, Wybór i Porównanie Modeli

Zgodnie z rekomendacją firmy Capgemini, projekt nie ogranicza się wyłącznie do modeli lokalnych, ale zakłada budowę elastycznej platformy testowej. Pozwala to na przeprowadzenie rzetelnych badań porównawczych (benchmarków) pomiędzy różnymi klasami sztucznej inteligencji.

## 1. Architektura "Plug-and-Play" (Gateway)
Aby uniknąć przepisywania kodu przy zmianie modelu, system wykorzysta wzorzec warstwy abstrakcji (LLM Gateway).
*   **Technologia:** Wykorzystana zostanie biblioteka (np. `LiteLLM` lub interfejs `LangChain`), która tłumaczy wszystkie zapytania na jeden uniwersalny standard (format OpenAI).
*   **Mechanizm:** Zmiana modelu odbywa się wyłącznie poprzez zmianę jednej linijki w pliku konfiguracyjnym (np. zmiana zmiennej środowiskowej z `MODEL_NAME=gpt-4o` na `MODEL_NAME=ollama/qwen2.5`). Główna logika aplikacji (walidacja, UI, RAG) pozostaje nietknięta.

## 2. Grupy badawcze (Jakie podejścia porównujemy?)
W ramach badań magisterskich przetestowane zostaną cztery różne podejścia do generowania danych:

### Kategoria A: Giganci Chmurowi (Złoty Standard / Baseline)
Modele komercyjne uruchamiane przez API. Posłużą jako punkt odniesienia do oceny, jak dobrze radzą sobie modele lokalne.
*   **Przykłady:** GPT-4o (OpenAI), Claude 3.5 Sonnet (Anthropic).
*   **Zalety:** Najwyższa zdolność rozumowania (schema awareness), znikoma liczba halucynacji.
*   **Wady:** Brak prywatności (dane opuszczają firmę), koszty zapytań API.

### Kategoria B: Lokalne Modele "Z Pudełka" (Zero-shot)
Małe, wydajne modele open-source uruchamiane na stacji roboczej (np. przez Ollama).
*   **Przykłady:** Qwen 2.5 Coder (7B), Llama 3.1 (8B).
*   **Zalety:** 100% bezpieczeństwa danych (Data Sovereignty), darmowe użytkowanie.
*   **Wady:** Mogą gubić kontekst przy bardzo dużych schematach baz danych.

### Kategoria C: Lokalne Modele po Douczeniu (Fine-tuning)
Wykorzystanie technik PEFT/LoRA do "douczania" bazowego modelu z Kategorii B na specyficznych strukturach danych używanych w Capgemini.
*   **Cel badawczy:** Sprawdzenie, czy mały model (np. 8B parametrów) po douczeniu na firmowych JSON-ach potrafi dorównać skutecznością gigantom klasy GPT-4 w tym konkretnym zadaniu.

### Kategoria D: Zespoły Agentów (Multi-Agent / Ensemble)
Zamiast jednego modelu, który robi wszystko, dzielimy zadanie na mniejsze kroki wykonywane przez różne (lub te same) lokalne modele.
*   **Przepływ (Workflow):**
    1.  *Model "Architekt":* Analizuje zapytanie i wybiera schematy tabel.
    2.  *Model "Robotnik":* Generuje surowe dane na podstawie schematu.
    3.  *Model "Krytyk":* Analizuje wygenerowane dane i wytyka błędy przed ostatecznym wysłaniem do walidatora w Pythonie.
*   **Cel badawczy:** Weryfikacja, czy współpraca mniejszych modeli zmniejsza odsetek błędów walidacyjnych.

## 2. Zestawienie Modeli do Badań (Benchmark)

W ramach części badawczej pracy magisterskiej ewaluacji zostaną poddane trzy klasy modeli. Pozwoli to na miarodajne porównanie skuteczności, wydajności oraz kosztów w różnych środowiskach uruchomieniowych.

### Klasa A: Giganci Komercyjni (Punkt Odniesienia / Baseline)
Modele te posłużą do wyznaczenia "górnej granicy" możliwości obecnej sztucznej inteligencji w zakresie trzymania się formatu JSON i rozumienia relacji bazodanowych.
*   **GPT-4o (OpenAI):** Aktualny standard rynkowy, uruchamiany przez publiczne API.

### Klasa B: Modele Lokalne na stacji roboczej (Edge AI)
Małe, skwantyzowane modele uruchamiane lokalnie u programisty (bez dostępu do internetu), gwarantujące maksymalne bezpieczeństwo kosztem mniejszych zdolności poznawczych.
*   **Qwen 2.5 Coder (7B):** Wiodący, lekki model wyspecjalizowany w kodzie i danych strukturalnych.
*   **DeepSeek-R1 (wersja 7B/8B):** Sprawdzenie, czy modele z mechanizmem wymuszonego rozumowania (wykorzystujące tag `<think>`) popełniają mniej błędów przy mapowaniu kluczy obcych.

### Klasa C: Otwarty Standard w zamkniętej chmurze (AWS VPC)
Większe wersje modeli Open Source uruchamiane w odizolowanym środowisku korporacyjnym (AWS), łączące potężne możliwości z wymogami Data Sovereignty.
*   **Llama 3.1 (wersja 70B) lub Qwen 2.5 (32B+):** Uruchamiane np. przez Amazon Bedrock lub instancje EC2. Zbadanie różnicy w jakości względem małych modeli z Klasy B.

## 3. Eksperyment Architektoniczny: Single-Agent vs Multi-Agent
Oprócz porównywania samych modeli, badaniu poddany zostanie wpływ architektury na poprawność danych. Zmierzone zostanie, czy odsetek błędów maleje w przypadku:
1.  **Podejścia Single-Agent:** Pojedynczy model (np. Qwen) otrzymuje prompt i generuje cały plik.
2.  **Podejścia Multi-Agent:** Zadanie jest dzielone na współpracujące instancje modelu:
    *   *Agent Planista:* Analizuje schemat i decyduje o kolejności.
    *   *Agent Wykonawca:* Generuje kod.
    *   *Agent Recenzent:* Krytykuje kod przed przekazaniem go do twardego walidatora w Pythonie.

*Uwaga:* Z uwagi na obszerny zakres testów architektonicznych (Multi-Agent, AWS, hybrydowy walidator), proces douczania modeli (Fine-Tuning) zostaje celowo wyłączony z głównego zakresu prac i zostanie omówiony w sekcji kierunków dalszych badań.