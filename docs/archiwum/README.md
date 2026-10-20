# Archiwum koncepcji

**Data uporządkowania:** 20 października 2026.

To archiwum zawiera pierwotne notatki projektu, zachowane **bez zmian treści**. Materiały dokumentują wcześniejsze pomysły, ale nie są obowiązującą specyfikacją ani potwierdzonymi decyzjami technologicznymi.

Aktualne wymagania znajdują się w [specyfikacji MVP](../specyfikacja_mvp.md). Dokumentację uzupełniają [przepływy funkcjonalne](../przeplywy_funkcjonalne.md) i [roboczy plan badań](../plan_badan.md).

## Zawartość i wykorzystanie

| Materiał historyczny | Powód archiwizacji | Co zachowano w aktywnej dokumentacji |
| --- | --- | --- |
| [Specyfikacja funkcjonalna](2026-10-20/dev/specyfikacja_funkcjonalna.md) | Zastąpiona uzgodnioną specyfikacją MVP; zawiera szerszy zakres i niezatwierdzone wybory. | Wymagania generatora w specyfikacji; pomysły podglądu i kopiowania jako niezatwierdzone propozycje UX w przepływach. |
| [Architektura](2026-10-20/dev/architektura.md) | Przedwcześnie przesądza technologie, RAG i mikroserwisy. | Rozróżnienie odpowiedzialności funkcjonalnych w przepływach oraz hipoteza pomocy deterministycznej w planie badań. |
| [Przepływy sekwencyjne](2026-10-20/dev/przeplywy_sekwencyjne.md) | Odnoszą się do wcześniejszego zakresu i nie pokazują wszystkich ustalonych zakończeń procesu. | Nowe przepływy zgodne z MVP, bez narzucania usług, bibliotek i układu ekranów. |
| [Strategia modeli AI](2026-10-20/koncepcje/strategia_modeli_ai.md) | Miesza osie porównań, zawiera nieudokumentowane oceny modeli i niespójny zakres fine-tuningu. | Pytania o modele, prompty, podział ról i sposób wspomagania generowania. |
| [Wybór LLM](2026-10-20/koncepcje/wybor_llm.md) | Dotyczy wyłącznie części lokalnej i nie jest aktualną listą wybranych modeli. | Zapisane informacje o sprzęcie i obszary do uzupełnienia przed badaniami. |
| [Założenia środowiska](2026-10-20/koncepcje/zalozenia.md) | Traktuje AWS i wymagania korporacyjne jako obowiązkowe, czego nie przyjęto dla MVP. | Możliwość późniejszego wdrożenia chmurowego jako rozszerzenie, bez zobowiązania do migracji. |
| [Pomysły i notatki](2026-10-20/koncepcje/pomysly_notatki.md) | Łączą hipotezy, zamknięte już pytania i pomysły spoza MVP. | Hipotezy dotyczące identyfikatorów i pomocy deterministycznej oraz pytania o reprezentatywne schematy i ograniczenia biznesowe. |

Pusty plik `docs/dev/instrukcja_setupu.md` usunięto podczas porządkowania. Nie zawierał instrukcji ani innych informacji; właściwa instrukcja powstanie wraz z działającą aplikacją.

## Zasady odczytu

- Deklaracje dotyczące konkretnych modeli i technologii są historyczne, nie stanowią aktualnej rekomendacji.
- Znaczniki `[cite: 1]` i `[cite: 2]` w oryginałach nie mają przypisanej bibliografii. Nie należy używać ich jako źródeł w pracy.
- Zapisy o gwarantowanym bezpieczeństwie, jakości lub łatwości migracji nie zostały w tym archiwum zweryfikowane.
- Informacje przypisane firmie lub opiekunowi nie potwierdzają same przez się obowiązujących wymagań projektu.
- Nie należy kopiować założeń z archiwum do implementacji bez jawnego uzgodnienia ich z aktualnym zakresem.
- Historyczne oryginały pozostają bez zmian; bieżące decyzje należy zapisywać w aktywnej dokumentacji.
