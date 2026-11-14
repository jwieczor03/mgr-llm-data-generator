# CHAT-01 — czat z wynikiem

Makieta pozwala ocenić czytelność rozmowy, karty wyniku i rozróżnienia
wykonania zadania od zgodności biznesowej. Aktualizacja: 14 listopada 2026.
Status: **referencja zaakceptowanego fundamentu wizualnego v0.1**.
Akceptacja użytkownika z 14 listopada 2026 dotyczy kierunku i wspólnych
komponentów, nie pełnego przepływu, treści ani gotowości produkcyjnej.

## Aktualna iteracja 02

Na prośbę użytkownika mocniej wykorzystano konkretne wzorce Google Fonts
i początkowego widoku Gemini: tonalne powierzchnie, obłe kontenery,
przyciski kapsułkowe oraz większy i lżejszy nagłówek.
Zmieniono wspólne tokeny, galerię i ten sam ekran. Nie dodano nowych
funkcji, modeli ani nawigacji. Źródła i ograniczenia opisuje
[dokumentacja wyglądu](../../design-system.md).

## Scenariusz i źródło

[Specyfikacja](../../../specyfikacja_mvp.md): REQ-024–027 (zatwierdzony zakres),
REQ-029–031 (warunki wyniku), REQ-043–051 (eksport i raport),
REQ-073–078 (czat i dalsze polecenia).
Fikcyjny sklep: 50 klientów, 30 produktów, 200 zamówień, 600 pozycji.
W scenariuszu wynik jest wykonany, ale po 3 rundach pozostają 3 naruszenia
dodatkowej reguły dat dostawy, niebędącej ograniczeniem DDL.
To treść demonstracyjna, nie pomiar skuteczności ani domyślne proporcje.

## Co działa w podglądzie

- Jasny/ciemny motyw — wyłącznie narzędzie makiety.
- Raport można rozwinąć przyciskiem albo natywną sekcją szczegółów.
- Pobranie `.sql` zapisuje wyłącznie komentarz o demonstracji, nie paczkę.
- Wysłanie pustego pola pokazuje błąd; wpisanego polecenia nie wysyłamy do LLM.
  Komunikat jawnie informuje, że to demonstracja i niczego nie zmieniono.
- „Nowy czat” otwiera modalne potwierdzenie; rezygnacja zachowuje widok,
  potwierdzenie pokazuje pustą rozmowę z zachowanym projektem.
- Na małym ekranie znika panel boczny, ale projekt pozostaje w nagłówku.

## Co jest poza demonstracją

Brak prawdziwego wyboru projektu (pokazano statyczny kontekst), wgrywania DDL,
zatwierdzania planu, generowania, próbnego importu, kompletnych plików
i kontraktu eksportowanego raportu. Brak prawdziwego cyklu życia czatu:
odświeżenie przywraca przykład, nie symuluje REQ-074–075.
Brak połączeń z backendem i dostawcami LLM.

## Kontrola pierwszej iteracji — historyczna

Poniższe pomiary dotyczą poprzednich tokenów. Nie potwierdzają nowego
wyglądu ani kontrastu iteracji 02. Aktualne sprawdzenie podano niżej.

**Sprawdzone:** rzeczywisty render w przeglądarce podglądu, oba motywy,
przy szerokościach 1280, 768 i 390 px. Pomiar szerokości dokumentu
nie wykazał poziomego przepełnienia. Na małym ekranie projekt
pozostaje widoczny, a „Nowy czat” jest dostępny w nagłówku.
Obejrzano również galerię komponentów w obu motywach.

Sprawdzono rozwijanie/zamykanie raportu oraz formularz z pustym
i wpisanym poleceniem w obu motywach. Pobranie utworzyło demonstracyjny
plik `.sql`, nie paczkę danych. Potwierdzenie nowego czatu pokazało pusty
widok bez zmiany projektu. To testy makiety, nie aplikacji.

Klawiatura: wejście do dialogu na „Zostań”, Tab, Escape i powrót
fokusu do przycisku otwierającego. Fokus klawiaturowy ma obrys 3 px
w obu motywach. Wykrytą podczas sprawdzenia niejednoznaczność
przejścia Tab za ostatni przycisk usunięto jawnym zawijaniem fokusu;
ponowiono to sprawdzenie. Nie jest to pełny test czytnika ekranu.

Pomiar kontrastu z tokenów odczytanych z uruchomionej strony:

| Para | Jasny | Ciemny |
| --- | --- | --- |
| Tekst / tło strony | 15,18:1 | 15,71:1 |
| Tekst pomocniczy / tło strony | 5,40:1 | 8,59:1 |
| Tekst pomocniczy / tło subtelne | 4,94:1 | 6,87:1 |
| Tekst przycisku / akcent | 6,10:1 | 8,07:1 |
| Sukces / tło sukcesu | 6,21:1 | 7,59:1 |
| Ostrzeżenie / tło ostrzeżenia | 6,42:1 | 7,89:1 |
| Obramowanie kontrolki / powierzchnia | 3,65:1 | 4,68:1 |
| Błąd / tło strony | 6,33:1 | 8,83:1 |

Są to wybrane pary, nie dowód pełnej zgodności z WCAG.
`node --check` nie zgłosił błędów JS. Sprawdzono lokalne odnośniki
i zasoby trzech plików HTML — brak brakujących plików.
W konsoli podglądu czatu nie zaobserwowano błędów ani ostrzeżeń.
Komendę lokalnego serwera uruchomiono i użyto do kontroli.

**Niesprawdzone:** pełna macierz przeglądarek, czytniki ekranu,
powiększenie 200–400%, rzeczywiste urządzenia dotykowe, wszystkie stany
hover, pełne przejście wszystkich kontrolek samą klawiaturą,
bezpośrednie otwarcie przez `file://` oraz użyteczność z użytkownikami.
Nie wykonano generowania, walidacji PostgreSQL ani płatnych wywołań LLM.

## Kontrola iteracji 02

**Sprawdzone 14 listopada 2026:** rzeczywisty render czatu w przeglądarce
podglądu, light i dark, przy szerokościach 1280, 768, 390 i 320 px.
Pomiar szerokości dokumentu nie wykazał poziomego przepełnienia.
Na telefonicznym układzie projekt i „Nowy czat” pozostają w nagłówku.
Obejrzano również katalog i galerię komponentów w obu motywach przy 320 px
oraz galerię na desktopie.

W obu motywach sprawdzono rozwijanie i zamykanie raportu, walidację pustego
polecenia i komunikat o symulacji po wpisaniu tekstu. Dialog nowego czatu:
fokus na „Zostań”, przejście Tab, zawijanie fokusu, widoczny obrys 3 px,
Escape i powrót do przycisku otwierającego. Potwierdzenie nowego czatu
przy 320 px w dark pokazało pustą rozmowę z zachowanym projektem.
Pobrania SQL nie ponawiano — kod tej interakcji nie zmienił się.

Kontrast obliczony z bieżących tokenów odczytanych z uruchomionej strony:

| Para | Jasny | Ciemny |
| --- | --- | --- |
| Tekst / tło strony | 16,48:1 | 14,47:1 |
| Tekst pomocniczy / tło subtelne | 6,11:1 | 7,07:1 |
| Tekst pomocniczy / powierzchnia karty | 6,80:1 | 8,74:1 |
| Tekst przycisku / akcent | 6,39:1 | 7,50:1 |
| Tekst przycisku / akcent hover | 9,14:1 | 8,98:1 |
| Tekst tonalny / tło tonalne | 7,04:1 | 9,01:1 |
| Sukces / tło sukcesu | 5,75:1 | 8,05:1 |
| Ostrzeżenie / tło ostrzeżenia | 6,50:1 | 8,96:1 |
| Obramowanie kontrolki / tło subtelne | 3,89:1 | 4,70:1 |
| Błąd / tło strony | 6,54:1 | 10,87:1 |

`node --check` nie zgłosił błędów JavaScript. Ponowna kontrola lokalnych
odnośników i zasobów trzech plików HTML nie wykazała brakujących plików.
W konsoli podglądu nie zaobserwowano błędów ani ostrzeżeń.

**Niesprawdzone:** pełna macierz przeglądarek, czytniki ekranu,
powiększenie 200–400%, rzeczywiste urządzenia dotykowe, wszystkie stany hover
i pełne przejście każdej kontrolki klawiaturą. Nie sprawdzono `file://`,
nie przeprowadzono badań użyteczności ani rzeczywistego generowania danych.
Powyższe kontrole nie są deklaracją pełnej zgodności z WCAG.

## Ręczna ocena

1. Otwórz [ekran](index.html). Sprawdź, gdzie wpisujesz kolejne polecenie.
2. Odszukaj status zadania i informację o naruszeniach reguł — powinny być odrębne.
3. Rozwiń raport, sprawdź liczebności i przykład naruszenia.
4. Przełącz motyw. Oceń tekst pomocniczy, kartę i ostrzeżenie.
5. Użyj Tab, aby przejść po kontrolkach, i Escape, aby zamknąć dialog nowego czatu.
6. Wyślij puste, a następnie dowolne wpisane polecenie. Nie powinna powstać
   pozorna odpowiedź modelu.
7. Oceń przy wąskim oknie. To pierwszy eksperyment, nie odbiór mobilnego produktu.

Kierunek wizualny zapisano jako zaakceptowany fundament v0.1. Kolejne ekrany
korzystają z [instrukcji dla dewelopera](../../design-system.md), ale wymagają
własnego uzgodnienia przepływu i odbioru.
