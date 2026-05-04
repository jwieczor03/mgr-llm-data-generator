# Wybór i ewaluacja lokalnych modeli LLM

## 1. Dostępne zasoby sprzętowe
Projekt zakłada wykorzystanie lokalnych modeli LLM w celu zapewnienia bezpieczeństwa danych[cite: 1]. Środowisko badawcze opiera się na dwóch stacjach roboczych:
* **Komputer prywatny:** MacBook Air M2.
* **Komputer firmowy:** HP Book (Intel Core i7, 32GB RAM, Nvidia RTX 1000 Ada 6GB VRAM / 16GB Shared).
* **Wniosek:** Ograniczona pamięć VRAM (6GB na dedykowanej karcie) wymusza stosowanie mniejszych modeli (parametry rzędu 7B-8B) oraz technik kwantyzacji (np. GGUF/EXL2)[cite: 1].

## 2. Kryteria wyboru modeli do testów
Aby model został zakwalifikowany do fazy Proof of Concept, musi spełniać następujące warunki:
* Licencja Open Source (możliwość komercyjnego użycia offline).
* Wsparcie dla generowania strukturyzowanego wyjścia (Schema Awareness / JSON Mode)[cite: 1].
* Dobry stosunek wielkości (poniżej 8 mld parametrów) do jakości logiki.

## 3. Wytypowane modele do fazy PoC
1. **Qwen 2.5 Coder (np. wersja 7B):** Według literatury bardzo silny model do zadań związanych z kodem i formatowaniem danych[cite: 1].
2. **Llama 3.1 (wersja 8B):** Najpopularniejszy otwarty model od Meta, znany z dobrego podążania za instrukcjami[cite: 1].
3. **[Do ustalenia]:** (np. Mistral NeMo lub Phi-3 Mini).