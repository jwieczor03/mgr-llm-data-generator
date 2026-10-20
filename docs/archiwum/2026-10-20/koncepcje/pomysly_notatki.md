# Burza mózgów i notatki bieżące

## Luźne pomysły na architekturę hybrydową
* **Problem integralności referencyjnej:** Jak sprawić, by wygenerowany w JSON "użytkownik" miał prawidłowe powiązanie z wygenerowanym w innym JSON "zamówieniem"[cite: 1]? 
* *Pomysł:* Może skrypt w Pythonie (warstwa deterministyczna) powinien najpierw generować bazowe klucze (ID), a potem wstrzykiwać je jako kontekst do promptu dla LLM[cite: 1]?

## Pytania do opiekuna z Capgemini
1. W jakim dokładnie formacie oczekują finalnych danych (czysty JSON, gotowe inserty SQL, XML)[cite: 1]?
2. Czy dostanę od nich przykładową (zanonimizowaną) strukturę bazy danych, żeby wiedzieć, pod co pisać walidatory?
3. Jakie konkretnie więzy spójności (constraint violations) są dla nich najbardziej problematyczne w obecnych procesach[cite: 1]?

## Rzeczy do zbadania (Spike)
* Sprawdzić, jak biblioteka `Pydantic` radzi sobie z zagnieżdżonymi strukturami JSON.
* Przetestować, czy biblioteka `Faker` (do generowania losowych danych w Pythonie) może wspierać LLM w architekturze hybrydowej[cite: 1].