# Design system — zaakceptowany fundament v0.1

Ten dokument mówi deweloperowi, jak zachować wspólny wygląd kolejnych
ekranów generatora. Fundament opiera się na iteracji 02 ekranu czatu.
Nie jest implementacją aplikacji ani dodatkową specyfikacją produktu.
Punkt wejścia: [katalog makiet](index.html).

## Status na 14 listopada 2026

**Uzgodnione przez użytkownika:** eksperyment z jednym ekranem czatu po
wygenerowaniu danych, kontekst projektu, rozmowa, wynik i raport; spokojne
neutralne powierzchnie z niebieskim akcentem; light/dark; demonstracyjny
sklep i polskie treści; lokalny HTML w `docs/ui/`. Źródło: potwierdzenie
„tak” po propozycji zakresu w rozmowie projektowej.

**Zaakceptowany fundament wizualny v0.1:** kolory obu motywów, typografia,
odstępy, zaokrąglenia, tonalne powierzchnie i wygląd istniejących komponentów.
Źródło: wiadomość użytkownika z 14 listopada 2026:
„spoko całkiem mi sie podoba mozesz zapisac jako design system aby
deweleporem tworzacy ekrany wiedzial czego sie trzymac”.
Jest to punkt odniesienia dla kolejnych ekranów, nie akceptacja wszystkich
przepływów, tekstów, interakcji, mobilnej nawigacji ani całego produktu.

**Zlecona korekta:** 14 listopada 2026 użytkownik poprosił o mocniejszą
inspirację Google Design oraz stronami i produktami Google. Zaktualizowano
ten sam ekran i wspólne komponenty; nie rozszerzono funkcji produktu.
Po prezentacji użytkownik zaakceptował kierunek jako design system.
Aktualne pliki wspólne zachowują wygląd tej iteracji; przy zapisie v0.1
nie zmieniono wartości CSS ani działania makiety.

**Otwarte:** docelowy język aplikacji (polski uzgodniono dla demonstracji),
obsługiwane przeglądarki i urządzenia, docelowy poziom dostępności,
domyślny motyw, preferencja systemowa i zapamiętywanie wyboru,
wybór biblioteki UI oraz pełna organizacja projektów i reguł.
Proponowany punkt odniesienia dostępności: WCAG 2.2 AA; bez deklaracji zgodności.

## Fundament

[Tokeny](shared/tokens.css) są źródłem wartości, a
[wspólne komponenty](shared/components.css) obsługują galerię i ekran.
[Galeria](design-system.html) pokazuje użyte teraz elementy i ich stany.

- Jasny motyw: niebieskoszare tło kontekstu, biała przestrzeń robocza
  w dużym zaokrąglonym kontenerze i delikatnie tonowana karta wyniku.
- Ciemny motyw: neutralne antracytowe powierzchnie, rozróżnione jasnością,
  oraz jasnoniebieskie akcje. Bez mechanicznego odwracania kolorów.
- Niebieski służy działaniom; zieleń warunkom wykonania, bursztyn naruszeniom.
  Znaczeniu zawsze towarzyszy tekst, nie sam kolor.
- Lżejszy nagłówek 34 px, tekst odpowiedzi 14 px, większe pole polecenia 15 px.
  Lokalny Arial z alternatywą Helvetica Neue; nie pobieramy ani nie
  udajemy użycia Google Sans. Nazwy tabel mają stałą szerokość znaków.
- Zaokrąglenia 12/24/28 px, przyciski i statusy w kształcie kapsułek.
  Wypełnienie tonalne oznacza pomocniczą akcję albo kontekst projektu;
  nie dodano pozornych opcji nawigacji.
- Ruch, poświaty i dekoracyjne gradienty nie są potrzebne do oceny
  tego scenariusza; nie dodano ich w ramach inspiracji.
- Karta wyniku porządkuje dane, zamiast zmieniać cały ekran w dashboard.
- Poniżej 720 px panel kontekstu jest ukryty, nazwa projektu pozostaje w nagłówku.
  To wzorzec układu referencyjnego czatu, nie kompletna nawigacja mobilna.
- Przełącznik motywu jest narzędziem podglądu. Jasny start, bez pamięci wyboru;
  nie przesądza o zachowaniu produkcyjnym.

## Jak korzystać — instrukcja dla dewelopera

1. Przed tworzeniem ekranu przeczytaj jego wymagania w specyfikacji.
   Design system określa wygląd, nie dodaje funkcji produktu.
2. Sprawdź [galerię](design-system.html) i [referencyjny czat](screens/czat/index.html).
   Nowe makiety podłączaj do `shared/components.css`, który importuje tokeny.
   Nie kopiuj palety i definicji komponentów do osobnych arkuszy ekranów.
3. W aplikacji produkcyjnej zachowaj te same role tokenów i wygląd.
   Wspólne komponenty aplikacji wydziel zgodnie z jej architekturą.
   Nie kopiuj całego arkusza makiet ani `preview.js` bezpośrednio do produktu:
   zawierają narzędzia podglądu, style konkretnego czatu i symulacje.
4. Jeśli komponent już istnieje, użyj go. Gdy brakuje wariantu, zaproponuj
   rozszerzenie i dodaj je do wspólnego systemu oraz galerii po uzgodnieniu.
   Nie twórz lokalnego „prawie takiego samego” przycisku lub pola.
5. Każdy ekran przygotuj w obu motywach. Sprawdź długie treści, małe okno,
   błąd, fokus i stany wynikające z zadania. Podgląd na szerokościach
   320, 390, 768 i 1280 px jest istniejącą próbą regresji, nie deklaracją
   obsługi wszystkich urządzeń.

### Źródła wyglądu i pierwszeństwo

| Artefakt | Do czego służy |
| --- | --- |
| [Ten dokument](design-system.md) | Zasady stosowania i zakres akceptacji. |
| [Tokeny CSS](shared/tokens.css) | Aktualne wartości obu motywów: kolory, fonty, odstępy, promienie, szerokość treści. |
| [Komponenty CSS](shared/components.css) | Szczegółowe style, rozmiary i reguły responsywne użyte w makietach. |
| [Galeria HTML](design-system.html) | Wizualny wzorzec podstawowych komponentów i ich stanów. |
| [CHAT-01](screens/czat/index.html) i [notatki](screens/czat/notes.md) | Kompozycja referencyjna, demonstracyjne zachowania i rzeczywiste wyniki kontroli. |

Wymagania funkcjonalne rozstrzyga specyfikacja MVP. Dla wartości wyglądu
źródłem jest wspólny CSS, a nie kolor pobrany ze zrzutu ekranu. Sprzeczność
CSS z opisem należy wyjaśnić, a nie wybierać wygodniejszą wersję po cichu.

### Tokeny: wybieraj znaczenie, nie konkretny kolor

| Rola | Tokeny i zastosowanie |
| --- | --- |
| Powierzchnie | `--canvas`: obszar pracy; `--sidebar`: kontekst; `--surface`: np. dialog; `--surface-container`: karta; `--subtle`: tonalne pole lub wiadomość. |
| Tekst i granice | `--text`, `--muted`, `--border` dla podziałów, `--control-border` dla kontrolek. Nie zastępuj czytelnej granicy pola słabym separatorem. |
| Akcje | `--accent`, `--accent-hover`, `--on-accent`; wariant tonalny: `--accent-soft`, `--on-accent-soft`. Stosuj pasujące pary tekst/tło. |
| Informacja zwrotna | Pary `--success` / `--success-soft`, `--warning` / `--warning-soft`; `--error` dla błędów. Zawsze dodaj zrozumiały tekst. |
| Fokus | `--focus`; istniejący obrys `:focus-visible` ma 3 px. Nie usuwaj go bez dostępnego odpowiednika. |
| Rytm i kształt | `--space-1`–`--space-7`, `--radius-sm/md/lg/pill`; `--shadow: none`. Korzystaj z tej skali zamiast własnej skali na każdym ekranie. |

Font podstawowy jest lokalny; nie dodawaj Google Sans ani CDN w ramach
„zgodności z Google”. Tekst podstawowy ma 14 px / 1,55, nagłówek strony
34 px (30 px w wąskim układzie), nagłówek sekcji 20 px, tekst pola rozmowy
15 px. Mniejsze rozmiary w istniejącym CSS służą metadanym i zwartym danym,
nie są domyślnym rozmiarem treści nowych ekranów.

### Komponenty i reguły stosowania

| Wzorzec w makiecie | Kiedy i jak używać |
| --- | --- |
| `.button.primary` | Główna akcja danej strefy, wypełnienie akcentem. Nie wyróżniaj tak wszystkich działań. |
| `.button.tonal`, `.button`, `.button.quiet` | Odpowiednio akcja tonalna, obramowana i dyskretna. Wybieraj według hierarchii, nie losowo między ekranami. |
| `.field`, `.input`, `.error-text` | Widoczna etykieta, opis i błąd przy polu; `aria-invalid` oraz powiązanie komunikatu z polem. Placeholder nie zastępuje etykiety. |
| `.card`, `.card-pad` | Grupowanie powiązanych treści na tonalnej powierzchni, delikatna granica i zaokrąglenie. Bez dekoracyjnych cieni. |
| `.badge.success`, `.badge.warning` | Krótki status z tekstem i znakiem. Wykonanie zadania i naruszenia dodatkowych reguł pozostają osobnymi informacjami. |
| `.result-table` | Zwarta tabela danych; nagłówki i czytelne wyrównanie wartości. Semantykę tabeli zachowaj także po zmianie frameworka. |
| `.report`, `.report-content` | Szczegóły dostępne po rozwinięciu. Wygląd nie przesądza o kontrakcie raportu. |
| `.composer` | Obłe pole rozmowy z etykietą i akcją wysłania; wzorzec specyficzny dla czatu. |
| `dialog` | Wzorzec wizualny potwierdzenia; sprawdzaj fokus, zamknięcie i powrót do wywołującej kontrolki. Kiedy wymagać potwierdzenia, określa zadanie. |
| `.icon` | Proste ikony konturowe, domyślnie 18 px, kolor odziedziczony z tekstu; bez logo i zasobów marki Google. |

Domyślny przycisk ma minimum 44 px wysokości; istnieją zwarte warianty
40 px w karcie wyniku i polu rozmowy. Pasek narzędzi makiety nie jest
wzorcem rozmiarów kontrolek aplikacji. Wariantu zwartego nie rozszerzaj
automatycznie na wszystkie formularze.

### Układ i responsywność

- Dla układu czatu: panel kontekstu 264 px, przy szerokości okna
  do 1000 px — 220 px; treść rozmowy ma maksymalnie `--content-width`.
- Przy szerokości do 720 px włącznie czat przechodzi w jedną kolumnę.
  Projekt i „Nowy czat” zostają w nagłówku. Inne ekrany nie mają automatycznie
  ukrywać ważnych działań razem z panelem — ich przepływ trzeba zaprojektować.
- Karty i rzędy akcji mogą się zawijać. Długie etykiety i komunikaty nie mogą
  nachodzić na kontrolki ani wymuszać poziomego przewijania całego dokumentu.
- Zachowuj hierarchię w obu motywach. Nie dodawaj dekoracyjnych gradientów,
  poświat, przypadkowych kolorów ani animacji, których nie ma w fundamencie.

### Kontrola nowego ekranu przed przekazaniem

- Wspólne tokeny i komponenty, bez osobnej palety dla ekranu.
- Ten sam sens statusów i hierarchia akcji w light/dark.
- Czytelne etykiety, komunikaty i widoczny fokus; obsługa klawiaturą.
- Sprawdzony rzeczywisty render, małe i pośrednie szerokości oraz długie treści.
- Zmierzone nowe pary kontrastu; dotychczasowe pomiary nie obejmują nowych zestawień.
- Stany i zachowanie wynikają z zadania; demonstracyjne dane nie trafiły do logiki.
- Galeria i notatki zaktualizowane, jeżeli rozszerzono wspólny wzorzec.

Zmiana wspólnych tokenów lub wyglądu komponentów wymaga sprawdzenia
używających ich ekranów w obu motywach oraz ponownego uzgodnienia
zmienionego wyglądu. Nie oznaczaj nowego ekranu jako zaakceptowanego
wyłącznie dlatego, że korzysta z zaakceptowanego fundamentu.

## Inspiracje i granice ich zastosowania

W tej iteracji obejrzano 14 listopada 2026 konkretne interfejsy,
bez logowania i bez wysyłania poleceń:

| Źródło | Zaobserwowane | Własne zastosowanie w makiecie |
| --- | --- | --- |
| [Google Fonts](https://fonts.google.com/) — oba motywy | Boczny kontekst oddzielony od treści, jasne niebieskoszare i ciemne neutralne powierzchnie, zaokrąglone wypełnione pola, kapsułkowe kontrolki. | Miękki panel projektu, tonalny „Nowy czat”, zaokrąglony obszar roboczy i kapsułki statusów. Nie przenosimy filtrów ani dodatkowej szyny nawigacyjnej. |
| [Gemini — interfejs bez logowania](https://gemini.google.com/app) — motyw ciemny | Duży lekki nagłówek, panel boczny, centralne obłe pole polecenia i niewiele konkurujących elementów. | Lżejszy nagłówek i wyraźna strefa pisania. Nie kopiujemy logo, selektora modeli, głosu, kont ani poświaty tła. Obejrzano stan początkowy, nie rozmowę z wygenerowanym wynikiem. |
| [Google Design — Illustrating the Gemini App](https://design.google/library/gemini-ai-visual-design) | Odczytano opis roli zaokrąglonych kształtów, kierowania uwagą i celowego ruchu. Obejrzano strukturę artykułu; multimedia nie odtwarzały się poprawnie. | Obłość kontenerów i spójność kształtów. To interpretacja tekstu i widocznego układu, nie analiza nieobejrzanej animacji. |

[Publiczna prezentacja Gemini](https://gemini.google/about/) została otwarta,
ale multimedia nie działały poprawnie. Nie jest podstawą odwzorowania
interakcji produktu. W pierwszej iteracji obejrzano też stronę główną
Google Design; próba Apple Support zakończyła się błędem połączenia.

Nie kopiujemy identyfikacji marek, czterokolorowego znaku ani układu 1:1.
Nie zatwierdzamy tym samym Material UI, biblioteki Material Web ani
wyboru technologii produkcyjnej. Nadal jest to własny HTML/CSS.

## Powiązanie z wymaganiami

Źródło: [specyfikacja MVP](../specyfikacja_mvp.md), zwłaszcza REQ-024–027,
REQ-029–031, REQ-043–051 i REQ-072–078.
Czat jest głównym widokiem; nie dodano archiwum ani selektora modeli.
Karta odróżnia spełnienie obowiązkowych warunków od naruszeń reguł biznesowych.
Żadne przedstawione sprawdzenie nie zostało wykonane na rzeczywistych danych.

## Sprawdzenie i dalszy rozwój

Zakres i wyniki kontroli znajdują się w [notatkach CHAT-01](screens/czat/notes.md).
Fundament wizualny jest zaakceptowany. Kolejne ekrany mogą z niego korzystać,
ale wymagają własnego uzgodnionego zakresu i odbioru. Rozbudowujemy system
według rzeczywistych potrzeb, nie tworzymy biblioteki na zapas.
