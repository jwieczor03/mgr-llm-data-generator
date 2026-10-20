# Plan badań — materiał roboczy

**Data uporządkowania:** 20 października 2026.

**Status:** propozycje do dalszego uzgodnienia. Dokument porządkuje wartościowe pomysły z wcześniejszych notatek; nie zatwierdza listy modeli, eksperymentów, mierników zbiorczych ani sposobu wyboru zwycięzcy.

Wymagania aplikacji określa [specyfikacja MVP](specyfikacja_mvp.md). Poniższy plan nie rozszerza jej o panel badawczy, automatyczne serie prób ani wbudowaną ocenę realizmu.

## 1. Ustalone ramy

- Badania są prowadzone ręcznie, przez zwykłe korzystanie z generatora.
- Autor zmienia modele lokalne i płatne modele przez API, prompty oraz organizację procesu.
- Porównanie dotyczy wyniku całego procesu, z jego walidacją i poprawkami.
- Porównywane wykonania realizują ten sam zatwierdzony scenariusz.
- Historia i prosty eksport dostarczają materiału do analizy poza generatorem.
- Realizm ocenia użytkownik, ewentualnie z pomocą zewnętrznego LLM i późniejszego osobnego narzędzia.
- Wariant docelowy zostaje wybrany na podstawie badań, a nie z góry przyjętej przewagi modeli płatnych, lokalnych lub zespołów agentów.

## 2. Proponowane pytania badawcze

| ID | Pytanie | Czego nie przesądzamy |
| --- | --- | --- |
| PB-01 | Jak badane modele radzą sobie z uzyskaniem kompletnych i importowalnych paczek dla powiązanych tabel? | Który dostawca lub klasa modelu okaże się najlepsza. |
| PB-02 | Jak zmiana promptów wpływa na wynik całego procesu, zgodność biznesową i nakład poprawek? | Czy bardziej rozbudowany prompt zawsze będzie korzystniejszy. |
| PB-03 | Czy rozdzielenie odpowiedzialności między role lub agentów daje korzyść względem prostszego procesu? | Czy dodatkowe role poprawiają wynik na tyle, aby uzasadnić ich czas i koszt. |
| PB-04 | Jak zakres pomocy deterministycznej zmienia skuteczność i charakter zadania wykonywanego przez LLM? | Że wynik rozwiązania hybrydowego jest miarą samodzielnych zdolności modelu. |
| PB-05 | Jak wyniki różnią się między scenariuszami o różnej liczbie tabel, relacji, reguł i rekordów? | Konkretnej granicy możliwości modelu bez wykonania prób. |

To propozycje pytań, nie zobowiązanie do pełnego badania wszystkich kombinacji.

## 3. Rozdzielenie osi porównania

| Oś | Przykładowe elementy opisu wariantu |
| --- | --- |
| Model | Rzeczywisty identyfikator i wersja, ustawienia generowania, model przypisany do każdej roli. |
| Prompty | Dokładne instrukcje wewnętrzne, przykłady i treść przekazana podczas poprawek. |
| Organizacja procesu | Jeden model, podział na etapy lub role, dodatkowa recenzja wygenerowanych danych. |
| Pomoc deterministyczna | Przygotowanie identyfikatorów, pilnowanie relacji, generowanie części wartości lub przygotowanie formatu wyjściowego. |
| Środowisko | Lokalne wykonanie lub API, sprzęt i istotne warunki uruchomienia. |

„Model lokalny”, „model płatny” i „multi-agent” nie są trzema rozłącznymi wariantami jednej osi. Zespół ról może korzystać z modeli lokalnych albo z API, a ten sam model może występować w różnych procesach.

Przy interpretacji wyniku należy wskazać, co rzeczywiście zmieniono. Jeśli jednocześnie zmieniono model, prompty, organizację procesu i pomoc deterministyczną, wniosek dotyczy porównania całych wariantów, a nie wyizolowanego wpływu jednego elementu.

## 4. Hipotezy zachowane z poprzednich materiałów

Poniższe pomysły **nie są potwierdzonymi wynikami ani wybraną architekturą**:

| ID | Hipoteza lub wariant do sprawdzenia | Ważne zastrzeżenie |
| --- | --- | --- |
| H-01 | Podział na planowanie, generowanie i recenzję może ograniczyć liczbę naruszeń. | Należy uwzględnić wszystkie wywołania i cały czas, a nie tylko odpowiedź ostatniego modelu. |
| H-02 | Przygotowanie identyfikatorów i powiązań poza LLM może zmniejszyć problemy z relacjami. | Oceniany jest wtedy model wspomagany przez aplikację; pomoc musi być jawnie opisana. |
| H-03 | Część prostych wartości może powstawać deterministycznie, a model może odpowiadać za treści i zależności wymagające interpretacji. | Zakres odpowiedzialności obu części musi być taki sam dla wariantów, których porównanie ma izolować wpływ modelu. |
| H-04 | Dodatkowy recenzent może pomóc przed niezależnym sprawdzeniem wyniku. | Opinia recenzenta nie zastępuje potwierdzenia kompletności i importowalności. |

W dawnych notatkach jako przykład pomocy przy wartościach pojawił się `Faker`. Zachowujemy sam pomysł eksperymentu; nie wybieramy tutaj tej ani żadnej innej biblioteki.

Role „planista”, „generator” i „recenzent” są przykładami odpowiedzialności, nie obowiązkowymi agentami. Nie ustalono, czy role mają używać tych samych czy różnych modeli.

## 5. Scenariusze i ręczny przebieg

### 5.1. Co należy ustalić w scenariuszu

- wersję DDL i zatwierdzone relacje;
- niezmienione polecenie użytkownika i ustalenia z doprecyzowań;
- potrzebne tabele oraz liczebności w każdej z nich;
- interpretacje sprawdzalnych reguł;
- wskazówki jakościowe;
- wybrany format wyniku;
- limit poprawek i sposób potwierdzania wykonania.

Wymagania scenariusza są odrębne od zmienianych promptów wewnętrznych i sposobu jego realizacji.

Przy porównaniu nastawionym na wpływ jednego czynnika proponuje się utrzymywać pozostałe warunki wspólne. Jeżeli zmiana warunków jest celowym przedmiotem badania, należy ją jawnie opisać; nie traktować jej jako przypadkowej różnicy pod tą samą nazwą zadania.

### 5.2. Propozycje rodzin scenariuszy

| Rodzina | Co pozwala obserwować |
| --- | --- |
| Proste powiązanie kilku tabel | Podstawową kompletność i zgodność relacji. |
| Zakupy, klienci, produkty i pozycje | Wiele powiązanych tabel, tabele łączące i różne liczebności. |
| Dodatkowe reguły między rekordami | Zgodność biznesową, np. sumy pozycji lub chronologię zdarzeń. |
| Ten sam schemat przy różnych wielkościach zlecenia | Zachowanie w skali setek do kilku tysięcy rekordów łącznie, zgodnie z MVP. |

Nie ustalono jeszcze dokładnych schematów, liczby scenariuszy ani liczby ręcznych powtórzeń. Wymagane zależności kołowe, testy negatywne i samodzielne dokumenty JSON nie wchodzą automatycznie do tego zestawu.

### 5.3. Przebieg pojedynczego porównania

1. Przygotować i zatwierdzić scenariusz w aplikacji.
2. Ręcznie podłączyć badany wariant.
3. Wykonać zlecenie i zachować dane wraz z raportem.
4. Zmienić wariant oraz ręcznie ponowić to samo historyczne zlecenie.
5. Zachować także próby nieudane, przerwane i anulowane, bez utożsamiania ich przyczyn.
6. Ocenić wyniki poza generatorem i opisać warunki porównania.

Plan nie wymaga automatyzacji tych działań.

## 6. Materiał do oceny

| Obszar | Dostępny materiał | Granica interpretacji |
| --- | --- | --- |
| Wykonanie | Kompletność i potwierdzenie importowalności. | Sam plik nie oznacza sukcesu. |
| Reguły biznesowe | Wynik każdej reguły, zakres sprawdzenia, liczba i przykłady naruszeń. | Nie ustalono wspólnej punktacji ani wag. |
| Poprawki | Liczba rund, limit, kandydaci i przebieg walidacji. | Runda nie jest pojedynczym wywołaniem modelu. |
| Czas | Dostępne pomiary całego procesu, z poprawkami. | Granice pomiaru, w tym udział przygotowania i oczekiwania na użytkownika, wymagają ustalenia. |
| Zasoby i koszt | Dostępne dane o wywołaniach, tokenach i koszcie. | Brak danych nie jest zerem; nie ustalono przeliczenia kosztu modeli lokalnych. |
| Realizm | Ocena autora, ewentualnie wsparta zewnętrznym LLM. | Generator nie deklaruje automatycznego sprawdzenia realizmu. |
| Diagnostyka | Faktyczne prompty, odpowiedzi i raporty kolejnych prób. | Pomagają wyjaśnić wynik, ale pierwsza odpowiedź nie jest osobnym głównym przedmiotem badania. |

Przed właściwymi badaniami trzeba ustalić kryteria oceny realizmu i sposób zapisywania jej poza generatorem. Jeżeli pomaga LLM, warto zachować również informację, jak dokonano tej oceny; nie tworzy to wymagania wbudowania oceniającego modelu do MVP.

## 7. Dostępne zasoby — zapis z wcześniejszych notatek

Poniższe informacje przeniesiono z [historycznego opisu sprzętu](archiwum/2026-10-20/koncepcje/wybor_llm.md). Nie zostały zweryfikowane pomiarem ani uzupełnione o wszystkie parametry.

| Środowisko | Informacja zapisana w notatkach | Do potwierdzenia lub uzupełnienia |
| --- | --- | --- |
| Komputer prywatny | MacBook Air M2. | RAM, warunki uruchomienia i faktycznie dostępne zasoby podczas prób. |
| Komputer firmowy | HP Book, Intel Core i7, 32 GB RAM, Nvidia RTX 1000 Ada, 6 GB VRAM; dodatkowy zapis „16GB Shared”. | Dokładna konfiguracja, znaczenie zapisu o pamięci współdzielonej i dostępność sprzętu do badań. |

Zapis „16GB Shared” nie jest przyjętym potwierdzeniem dodatkowej dedykowanej pamięci GPU. Nie przenosimy też starego ograniczenia „poniżej 8 mld parametrów” jako warunku udziału wszystkich modeli w badaniu.

Lista konkretnych modeli pozostaje do wyboru. Dla kandydatów trzeba później sprawdzić m.in. dostępność, wymagania uruchomienia, warunki użycia i możliwość zebrania potrzebnych pomiarów. Ten dokument nie potwierdza aktualnej oferty ani nie przedstawia rankingu.

## 8. Materiały do uzyskania od partnera biznesowego

Zachowane pytania, jeśli udział firmy lub opiekuna pozostaje aktualny:

1. Czy można otrzymać reprezentatywne schematy PostgreSQL i używać ich w badaniach?
2. Jakie relacje oraz ograniczenia są najbardziej problematyczne przy przygotowywaniu danych testowych?
3. Jakie realistyczne reguły biznesowe można ujawnić i jednoznacznie sprawdzać?
4. Które materiały można przesłać do zewnętrznych API, a które muszą pozostać w ograniczonym środowisku?

Nie otwieramy ponownie jako nieustalonych wymagań pytań o podstawowy dialekt ani format wyjściowy: MVP dotyczy PostgreSQL i wyboru `INSERT` albo CSV.

## 9. Decyzje potrzebne przed właściwymi badaniami

- Dokładne scenariusze i liczba ręcznych powtórzeń.
- Wariant odniesienia oraz kolejne zmieniane czynniki.
- Modele, ustawienia i skład ról w wariantach wieloagentowych.
- Granica między pracą modelu i pomocą deterministyczną.
- Jednolite znaczenie potwierdzenia importowalności i pomiarów.
- Kryteria realizmu oraz sposób dokumentowania pomocy zewnętrznego LLM.
- Sposób interpretacji prób nieudanych, anulowanych i przerwanych błędem.
- Kryterium wyboru rozwiązania docelowego z uwzględnieniem skuteczności, jakości i nakładu.

Nie deklarujemy, że model płatny wyznacza „górną granicę”, modele lokalne zapewniają „100% bezpieczeństwa”, większy model zawsze wygrywa lub multi-agent musi poprawiać wynik. Takie oceny nie są wynikiem jeszcze nieprzeprowadzonych badań.

Fine-tuning, chmura AWS oraz duże wolumeny nie są dopisywane do planu jako obowiązkowe eksperymenty. Ewentualne rozszerzenia wymagają osobnej decyzji i czasu poza podstawowym zakresem.

## 10. Pochodzenie zachowanych pomysłów

- [Pierwotna strategia modeli](archiwum/2026-10-20/koncepcje/strategia_modeli_ai.md): modele lokalne i płatne, podział ról, wariant recenzenta.
- [Pierwotny wybór LLM](archiwum/2026-10-20/koncepcje/wybor_llm.md): zapis dostępnego sprzętu.
- [Pierwotne notatki](archiwum/2026-10-20/koncepcje/pomysly_notatki.md): identyfikatory, pomoc deterministyczna i pytania o schematy.
- [Pierwotna architektura](archiwum/2026-10-20/dev/architektura.md): rozdzielenie generowania, relacji i niezależnego sprawdzania.

Są to źródła pochodzenia pomysłów, nie bibliografia potwierdzająca ich skuteczność. Bibliografię, dokumentację modeli i źródła uzasadniające tezy pracy należy zebrać osobno.
