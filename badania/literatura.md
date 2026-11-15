# Podobne badania — wstępne rozeznanie

Zebrane źródła pokazują, że generowanie danych testowych i relacyjnych przez
modele językowe jest już badanym zagadnieniem. Pomagają ocenić podobieństwo
projektu, ale nie potwierdzają jego oryginalności ani skuteczności.

**Data wyszukiwania i sprawdzenia źródeł:** 14 listopada 2026.  
**Status:** przegląd celowany, nie systematyczny.  
**Powiązania:** [ocena koncepcji](ocena-koncepcji.md),
[stan badań](stan-badan.md), [plan](../docs/plan_badan.md).

## 1. Jak szukano i czego nie sprawdzono

Korzystano z wyszukiwania internetowego oraz stron pierwotnych publikacji:
arXiv, Springer, Google Research, ICLR i VLDB. Repozytoria autorów i uczelni
pomagały sprawdzać pochodzenie materiałów. Nie przeprowadzono osobnego
wyszukiwania w Scopus ani Web of Science. Nie deklarujemy przeszukania
Google Scholar tylko dlatego, że strona publikacji ma do niego odnośnik.

Zakres: prace dostępne do dnia przeglądu, bez dolnej granicy roku.
Uwzględniono starsze metody bez LLM, aby nie utożsamiać nowego interfejsu
z nowym problemem. Włączano prace o danych relacyjnych, ograniczeniach,
danych testowych i ocenie. Odrzucano jako podstawę argumentacji reklamy,
automatyczne streszczenia, niezweryfikowane kopie oraz prace dotyczące
wyłącznie generowania tekstów treningowych.

Przykłady rzeczywiście użytych zapytań:

- `LLM relational synthetic test data generation schema business rules constraints validation repair`
- `large language models multi table synthetic data generation schema only database constraints`
- `"LLM" "test data generation" "relational" paper`
- `"synthetic" "relational" "LLM" "schema" arxiv`
- `"relational data generation" "business rules" "LLM"`
- `"High-Fidelity and Complex Test Data Generation"`
- `"On the Reliability of Open-Weight Language Models"`
- `"Generative AI to Generate Test Data Generators"`
- `"REaLTabFormer" "Generating Realistic Relational and Tabular Data"`
- `"Mixed-Type Relational Database Synthesis"`
- `"DataSynth" "Arasu"`
- `"DataFiller" "Coelho"`

Sprawdzono wybrane odniesienia i późniejsze prace znalezione po tytułach,
np. DataSynth jako wcześniejszą metodę oraz REMIX jako nowszą syntezę
relacyjną. Nie wykonano kompletnej analizy sieci cytowań. Niektóre strony
były niedostępne bezpośrednio; zakres dostępu podano przy źródłach.
ArXiv nie jest sam w sobie potwierdzeniem recenzji naukowej.

## 2. Najbliższe publikacje

### L-01. Niezawodność lokalnych modeli w generowaniu relacyjnym

**Saba Zamankhani, Kai-Uwe Sattler.**
*On the Reliability of Open-Weight Language Models for Relational Data
Generation Under Structural Constraints.*
DEXA 2026, LNCS 16859, s. 236–247.
[DOI](https://doi.org/10.1007/978-3-032-34374-1_17).

**Wersja i dostęp:** abstrakt i metadane wydawcy odczytane przez indeks
wyszukiwarki; bez pełnego rozdziału. [Metadane tomu](https://link.springer.com/book/10.1007/978-3-032-34374-1)
podają wydanie eBook 2 sierpnia i drukowane 3 sierpnia 2026, lecz
rok cytowania rozdziału i copyright 2027. To jeden rozdział, nie dwie prace.

**Problem, metoda, wynik:** według abstraktu 1975 wykonań obejmuje lokalne
modele 3B–7B, trzy tryby inferencji i dwie strategie. Generowanie tabel
w kolejności zależności z katalogiem identyfikatorów uzyskało 86,5% sukcesów,
a jednorazowy pełny skrypt 21,3%.

**Znaczenie i ograniczenie:** bardzo bliskie PB-01 i PB-05. To wynik autorów
w ich warunkach, nie prognoza dla naszego MVP. Bez pełnego tekstu nie
rozstrzygamy pokrycia naszych reguł, budżetów i semantyki sukcesu.

### L-02. Dane testowe dla usług generujących SQL

**Shivasankari Kannan, Yeounoh Chung, Amita Gondi, Tristan Swadell,
Fatma Ozcan.**
*High-Fidelity And Complex Test Data Generation For Google SQL Code
Generation Services.*
[arXiv:2504.17203v4](https://arxiv.org/abs/2504.17203v4);
[strona Google Research](https://research.google/pubs/high-fidelity-and-complex-test-data-generation-for-real-world-sql-code-generation-services/).

**Wersja i dostęp:** preprint od 24 kwietnia 2025, v4 z 25 lutego 2026;
odczytano tekst, zwłaszcza sekcje II–III i tabelę II. Google Research wskazuje
ICDE 2026 i wariant tytułu z „Real-World” zamiast „Google”. Nie sprawdzono
zgodności z końcowym wydaniem konferencyjnym; nie liczymy wersji oddzielnie.

**Problem i metoda:** dane dla testów usług SQL bez swobodnego dostępu
do produkcji. Proces łączy Gemini z przygotowaniem kontekstu,
przetwarzaniem danych i walidacją.

**Wynik istotny:** tabela II pokazuje lepsze pokrycie pól trudnego schematu
niż w prostym wariancie LLM.

**Znaczenie i ograniczenie:** uzasadnia badanie całego procesu, nie samych
modeli. Zadanie jest związane z testowanymi zapytaniami i GoogleSQL.
MVP ma inny kontrakt: PostgreSQL i brak cichego poprawiania wyniku przez kod.

### L-03. SynSQL — generowanie baz z pytania i schematu

**Mohammadamin Habibollah, Davood Rafiei.**
*SynSQL: Synthesizing Relational Databases for Robust Evaluation of
Text-to-SQL Systems.*
[arXiv:2604.27261v1](https://arxiv.org/abs/2604.27261v1),
29 kwietnia 2026.

**Wersja i dostęp:** preprint; odczytano pełny dostępny tekst,
zwłaszcza sekcje 3, 4.3–4.5. Nie potwierdzono wydania recenzowanego.

**Problem i metoda:** tworzenie alternatywnych baz do oceny tłumaczenia
języka naturalnego na SQL. Dobór schematu, synteza tabel i krytyka
z poprawkami są bardzo bliskie planowanemu procesowi.

**Wynik istotny:** sekcja 4.3 raportuje wysoką poprawność strukturalną;
4.4 nadal opisuje błędy znaczeniowe. Nie utożsamiamy ich „success rate”
z naszym REQ-027.

**Znaczenie i ograniczenie:** sama krytyka i iteracja nie uzasadniają nowości.
Sekcja 3.2 dopuszcza m.in. dopełnianie wartościami NULL i obcinanie pól.
To różnica względem zakazu cichej zmiany danych w REQ-068, nie dowód
przewagi któregoś rozwiązania.

### L-04. REMIX — relacje, treść i naprawa zależności

**Yuxiang Sun, Mengshi Chen, Jianwei Wang, Wenjie Zhang, Kai Wang.**
*Mixed-Type Relational Database Synthesis with Graph-Prompted Language Model.*
[arXiv:2611.02373v1](https://arxiv.org/abs/2611.02373v1),
2 listopada 2026.

**Wersja i dostęp:** preprint; odczytano abstrakt z indeksu arXiv.
Próby otwarcia pełnego tekstu w arXiv nie powiodły się. Nie opierano
wniosków na znalezionej kopii w nieoficjalnym serwisie.
Nie potwierdzono wydania recenzowanego.

**Problem i metoda:** synteza powiązanych tabel z różnymi typami atrybutów.
Uczenie mniejszego modelu na źródłowej bazie łączy się z programami
naprawczymi przygotowywanymi przez LLM.

**Wynik istotny:** autorzy raportują poprawę spójności i użyteczności
na siedmiu bazach; nie wykonano niezależnej replikacji.

**Znaczenie i ograniczenie:** zależności znaczeniowe i naprawa danych
relacyjnych mają poprzedników. Nasz projekt ma działać z opisem i regułami
bez dostarczonej produkcyjnej bazy treningowej. To nie jest równoważne
zadanie; dokładne pokrycie reguł agregacyjnych trzeba sprawdzić w pełnym tekście.

### L-05. LLM generujący dane albo ich generatory

**Benoit Baudry, Khashayar Etemadi, Sen Fang, Yogya Gamage, Yi Liu,
Yuxin Liu, Martin Monperrus, Javier Ron, André Silva, Deepika Tiwari.**
*Generative AI to Generate Test Data Generators.*
IEEE Software 41(6), 55–64, 2024.
[Preprint](https://arxiv.org/abs/2401.17626);
[DOI wydania](https://doi.org/10.1109/MS.2024.3418570).

**Wersja i dostęp:** odczytano abstrakt arXiv; metadane publikacji
i status recenzowania potwierdza repozytorium KTH.
Preprint i artykuł liczymy jako jedną pracę.

**Problem, metoda, wynik:** trzy warianty obejmują surowe dane, kod
generatora i kod używający bibliotek Faker. Autorzy oceniają 11 dziedzin
i raportują wykonalność tych podejść.

**Znaczenie i ograniczenie:** generowanie danych oraz kodu generatora
to już opisane pomysły. Nie jest to jednak odpowiednik oceny całych paczek
wielotabelowych. Generator kodu byłby osobnym porównaniem, nie cichą zmianą MVP.

## 3. Kontekst metodyczny i wcześniejsze podejścia

### L-06. Odkrywanie i egzekwowanie reguł przez agentów

**Jianxing Zhao, Mao Guan, Dongyu Liu.**
*Constraint-Aware Synthetic Tabular Data Generation via Inter-Column
Constraint Discovery with LLM Agents.*
[arXiv:2608.15109](https://arxiv.org/abs/2608.15109),
15 sierpnia 2026.

**Dostęp:** preprint, abstrakt z indeksu arXiv; pełny tekst niedostępny
w użytym narzędziu. Nie potwierdzono wydania recenzowanego.

Reguły są wykonywalnymi hipotezami sprawdzanymi na tabeli referencyjnej;
diagnostyka i kontrprzykłady służą ich poprawianiu. Autorzy raportują brak
zmierzonych naruszeń zachowanych, mających zastosowanie reguł po naprawie.
To nie gwarancja zgodności ze wszystkimi możliwymi regułami.

**Nasza ocena:** ważne dla PB-03 i niezależności pomiaru. Naprawa przez
postprocesor różni się od bezpośredniego generowania niezmienionych
plików SQL/CSV. Abstrakt nie wystarcza do oceny pełnej porównywalności.

### L-07. Poprawne rozkłady nie wystarczają

**Mihaela Stoian, Salijona Dyrmishi, Maxime Cordy, Thomas Lukasiewicz,
Eleonora Giunchiglia.**
*How Realistic Is Your Synthetic Data? Constraining Deep Generative Models
for Tabular Data.* ICLR 2024.
[Publikacja](https://proceedings.iclr.cc/paper_files/paper/2024/hash/887932131fddf943e8fe3310b62c0147-Abstract-Conference.html).

**Dostęp:** abstrakt w oficjalnych materiałach konferencji.

Autorzy wprowadzają warstwę wymuszającą określone ograniczenia w modelach
generujących dane tabelaryczne. Raportują, że modele bez niej mogą często
naruszać reguły mimo dobrego odwzorowania danych.

**Nasza ocena:** wspiera rozdzielenie zgodności reguł i podobieństwa
statystycznego. Nie dowodzi skuteczności naszego walidatora ani zdolności
LLM do samodzielnego spełniania reguł relacyjnych.

### L-08. REaLTabFormer — wcześniejsza synteza relacyjna

**Aivin V. Solatorio, Olivier Dupriez.**
*REaLTabFormer: Generating Realistic Relational and Tabular Data using
Transformers.*
[arXiv:2302.02041](https://arxiv.org/abs/2302.02041), 2023;
[repozytorium autorów](https://github.com/worldbank/REaLTabFormer).

**Dostęp:** preprint, abstrakt; nie potwierdzono tutaj
osobnego wydania recenzowanego.

Model generuje tabelę nadrzędną oraz zależne rekordy za pomocą modeli
transformerowych uczonych na danych. Autorzy raportują lepsze uchwycenie
struktury relacyjnej niż w ich wariancie odniesienia.

**Nasza ocena:** ważne tło, ale nie równoważny punkt odniesienia dla zadania
bez danych treningowych użytkownika. Samo użycie transformera do relacji
nie jest nowością projektu.

### L-09. DataSynth — generowanie według ograniczeń bez LLM

**Arvind Arasu, Raghav Kaushik, Jian Li.**
*DataSynth: Generating Synthetic Data using Declarative Constraints.*
Proceedings of the VLDB Endowment 4(12), 1418–1421, 2011.
[Tekst](https://www.vldb.org/pvldb/vol4/p1418-arasu.pdf).

**Dostęp:** tekst demonstracyjny, zwłaszcza sekcje 1–2. Nie traktujemy
demonstracji jako współczesnego porównania jakości LLM.

Ograniczenia liczebności opisują oczekiwane cechy bazy; algorytmy generują
instancję spełniającą deklaracje. Praca uwzględnia klucze, zależności
i zastosowania testowe.

**Nasza ocena:** uzasadnia uwzględnienie prostszego odniesienia bez LLM.
Nie oznacza, że narzędzie obsłuży bez zmian wszystkie nasze reguły.
Nie należy utożsamiać tej demonstracji z osobnym artykułem autorów
*Data Generation Using Declarative Constraints* z SIGMOD 2011.

### L-10. Zależności między kolumnami a kolejność generowania

**Shengzhe Xu, Cho-Ting Lee, Mandar Sharma, Raquib Bin Yousuf,
Nikhil Muralidhar, Naren Ramakrishnan.**
*Why LLMs Are Bad at Synthetic Table Generation (and what to do about it).*
[arXiv:2406.14541v3](https://arxiv.org/abs/2406.14541v3), 13 marca 2025.

**Wersja i dostęp:** odczytano tekst HTML i metadane v3. Pierwsza wersja
z 20 czerwca 2024 ma tytuł *Are LLMs Naturally Good at Synthetic Tabular
Data Generation?* Nie potwierdzono tutaj osobnego wydania recenzowanego;
nie liczymy tytułów jako niezależnych prac.

Sekcje 1 i 3–4 opisują trudności zachowania zależności przy generowaniu
kolumn i metodę PAFT, uwzględniającą ich kolejność podczas dostrajania.
Autorzy wskazują ograniczenia typowych ocen rozkładów i użyteczności ML.

**Nasza ocena:** argument za pomiarem naruszeń konkretnych reguł,
nie za twierdzeniem, że każdy współczesny LLM jest nieprzydatny.

### Dodatkowy trop wymagający weryfikacji

*Enhancing Synthetic Test Data Generation with Language Models Using a More
Expressive Domain-Specific Language* (2023),
[DOI](https://doi.org/10.1007/978-3-031-43240-8_2).

Odnaleziono tytuł i identyfikator w wynikach wyszukiwania. Nie uzyskano
w tym przeglądzie zweryfikowanej strony pierwotnej ani tekstu, więc nie
przypisujemy publikacji autorów, metody ani wyników. To pozycja do sprawdzenia,
nie dowód wspierający ocenę.

## 4. Narzędzie do rozważenia jako odniesienie, nie publikacja naukowa

**Fabien Coelho, DataFiller.**
[Dokumentacja autorska](https://www.cri.minesparis.psl.eu/people/coelho/sw/datafiller/).

Odczytano indeksowaną dokumentację. Narzędzie generuje dane z DDL
uzupełnionego dyrektywami; PostgreSQL jest domyślnym celem.
To kandydat na porównanie bez LLM, nie wybrana zależność ani sprawdzone
rozwiązanie. Trzeba osobno ocenić zgodność z naszymi przypadkami.

## 5. Co z tego wynika dla wkładu pracy

**Ustalone z przeglądu:** istnieją zarówno bezpośrednio pokrewne procesy LLM,
jak i starsze metody generowania baz według ograniczeń.

**Interpretacja:** sensowniejszą obietnicą pracy jest kontrolowane badanie
skuteczności, kosztu i granic konkretnego procesu niż ogólne „pierwsze
zastosowanie LLM do danych relacyjnych”.

**Kandydat na węższe pytanie, nie potwierdzona luka:** generowanie bez
produkcyjnych danych wejściowych, z kontrolą reguł między tabelami,
informacją zwrotną z wykonywalnego walidatora i jawnym budżetem napraw.
Poszczególne składniki mają poprzedników. Nie sprawdzono, czy ich dokładne
połączenie i zaproponowane porównanie zostały już wyczerpująco zbadane.
Pełny tekst L-01 jest szczególnie ważny przed deklaracją różnicy.

Brak identycznego tytułu lub interfejsu nie dowodzi nowości. Nawet przy
dalszym podobieństwie pozostaje możliwość jawnej replikacji i badania granic,
jeśli taki wkład zostanie zaakceptowany przez promotora.
