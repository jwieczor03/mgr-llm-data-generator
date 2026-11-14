# Planowanie i interpretacja eksperymentów

## Od pytania do protokołu

Wybierz pytanie pozwalające zdobyć wiedzę, nie tylko pokazać działanie systemu.
Hipotezę stosuj tam, gdzie pomaga; badanie eksploracyjne nie wymaga
dopisania z góry oczekiwanego kierunku wyniku.

Przed zbieraniem wyników do głównego porównania ustal z autorem:

- pytanie, ewentualną hipotezę i uzasadnienie w literaturze;
- jednostkę próby oraz populację lub zakres zadań, na które ma się odnosić wniosek;
- wariant odniesienia, zmieniany czynnik i wspólne warunki;
- scenariusze, dane, sposób ich wyboru i podział materiału do strojenia i oceny;
- mierniki z definicją, mianownikiem i kierunkiem poprawy oraz kryteria sukcesu;
- powtórzenia, sposób uwzględnienia losowości, limity zasobów i warunki zatrzymania;
- sposób analizy, obsługę braków, niepowodzeń i odstępstw;
- artefakty potrzebne do odtworzenia próby.

Nie narzucaj pełnej siatki kombinacji. Proponuj etapowanie: mały pilotaż
wykonalności i pomiaru, następnie wybrane porównanie główne. Liczbę powtórzeń
uzasadniaj zmiennością, oczekiwaną precyzją lub analizą mocy, jeśli jest zasadna,
i budżetem. Ograniczona próba wymaga ograniczenia wniosków, nie fikcyjnej
uniwersalnej reguły „wystarczą trzy próby”.

## Uczciwe porównanie AI

- Nie mieszaj wpływu modelu, promptu, liczby ról, pomocy deterministycznej
  i budżetu. Albo izoluj czynnik, albo jawnie porównuj kompletne systemy.
  „Lokalny”, „płatny” i „multi-agent” nie są rozłącznymi kategoriami.
- Zapisuj wersje modeli i aplikacji, prompty, ustawienia, seed tam, gdzie
  jest dostępny, oraz datę i środowisko. Seed nie gwarantuje pełnej powtarzalności.
  Dla API odnotuj niekontrolowalne aktualizacje i niedostępne parametry.
- Uzgodnij znaczenie uczciwego budżetu: wspólny limit albo jawne zestawienie
  jakości względem pełnego kosztu. Uwzględniaj poprawki, recenzentów, retry,
  liczbę wywołań i pracę ręczną. Nie porównuj ostatniego wywołania jednego
  wariantu z całym przebiegiem drugiego.
- Rozważ przeplatanie lub losowanie kolejności wariantów, gdy zmiana warunków
  w czasie może wpłynąć na wynik. Nie wymagaj tego, gdy nie ma takiego ryzyka.
- Nie dostrajaj wariantów do końcowych przypadków oceny bez ujawnienia.
  Pilot i eksploracja nie stają się wstecznie testem potwierdzającym.
  Istotną zmianę metody po obejrzeniu wyników oznacz i wersjonuj.

## Mierniki i niezależność oceny

Dobieraj mierniki do pytania. W generatorze relacyjnym rozdzielaj kompletność,
importowalność, integralność relacji, sprawdzalne reguły biznesowe, realizm,
różnorodność, czas i zasoby. Poprawny format nie dowodzi realizmu, a podobieństwo
rozkładów nie dowodzi użyteczności danych testowych. Oceniaj prywatność tylko,
gdy należy do pytania i istnieje odpowiednia metoda — syntetyczność sama jej
nie gwarantuje.

Nie wprowadzaj zbiorczego rankingu ani wag po zobaczeniu zwycięzcy.
Wielowymiarowy kompromis może być lepszą odpowiedzią niż jedna punktacja.

Jeśli ocenia człowiek lub LLM, przygotuj rubrykę z obserwowalnymi kryteriami
i przykładami. Jeśli wykonalne, ukryj wariant i zmieniaj kolejność wyników.
Zewnętrznego sędziego LLM opisuj przez model, prompt, wersję i ustawienia;
oceń zgodność z oceną człowieka na dostępnym podzbiorze i ujawnij jej brak.
Recenzent będący częścią generowania nie jest niezależnym sędzią sukcesu.

## Wyniki i wnioski

Analizuj wyłącznie dostarczone lub faktycznie odczytane wyniki. Nie uruchamiaj
eksperymentów na podstawie samej prośby o propozycję badania.
Przed obliczeniami sprawdź jednostkę obserwacji i kompletność materiału.
Wiersze jednej paczki lub kolejne rundy tej samej próby nie są niezależnymi
powtórzeniami. Brak pomiaru nie oznacza zera.

Zachowuj próby nieudane. Oddziel błąd metody, awarię infrastruktury,
przekroczenie budżetu i anulowanie. Jawnie podaj licznik i mianownik
skuteczności; nie usuwaj niewygodnych prób. Stosuj wcześniej określone zasady
wyłączeń i raportuj odstępstwa.

Pokaż wielkość efektu i zmienność; przedziały niepewności i testy dobieraj
do projektu, zależności obserwacji i liczby porównań. Przy małej próbie
preferuj uczciwy opis zamiast pozornej precyzji. Nie wyprowadzaj przyczynowości
z porównania wariantów różniących się wieloma cechami. Nie utożsamiaj
braku istotności z równoważnością.

Dobieraj prezentację do pytania: skuteczność z liczebnością prób, rozkład czasu
zamiast samej średniej, jakość względem kosztu, tabela typów błędów z przykładami.
Nie ukrywaj niepowodzeń przez wykresy tylko udanych prób.
Każdy wniosek powiąż z pytaniem i danymi, porównaj z literaturą oraz ogranicz
do zbadanych modeli, scenariuszy i warunków. Wynik negatywny też dokumentuj.
