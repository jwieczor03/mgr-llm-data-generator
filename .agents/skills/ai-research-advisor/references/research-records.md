# Prosta dokumentacja badawcza

## Miejsce i trwałość

Dokumentacja badań ma być osobna od specyfikacji, architektury i instrukcji
aplikacji. Używaj istniejącego obszaru badawczego; przy jego braku domyślnie
utwórz `badania/` w katalogu projektu. Ten wybór odnotuj przy pierwszym zapisie.
Nie twórz pustego drzewa katalogów ani kompletu szablonów „na zapas”.

Jeżeli plan istnieje już w dokumentacji aplikacji, najpierw go odczytaj.
Nie przenoś go ani nie twórz konkurencyjnej kopii bez uzgodnienia.
Do czasu migracji podlinkuj istniejący plan jako źródło ustaleń, a nowe
notatki i raporty prowadź w obszarze badań. Propozycja przeniesienia powinna
obejmować korektę odsyłaczy i zachowanie statusu dotychczasowych ustaleń.

W ramach zleconego prowadzenia badań zapisuj istotne ustalenia, źródła,
propozycje i raporty lokalnie bez pytania o każdą notatkę. Zapis propozycji
nie zatwierdza protokołu. Krótka porada bez nowej treści nie wymaga osobnego pliku.
Nie kończ na sugestii „warto to udokumentować”: utwórz lub zaktualizuj właściwy
dokument na podstawie dostępnego materiału. Jeśli zapis jest niemożliwy,
ujawnij przeszkodę i podaj gotową treść zamiast twierdzić, że ją zapisano.
Nie publikuj dokumentów, nie commituj ani nie zmieniaj systemów zewnętrznych
bez osobnego zlecenia.

Utrzymuj mały indeks, np. `badania/stan-badan.md`: cel, aktualny etap,
odnośnik do obowiązującego planu i protokołu, lista pytań z ich statusem,
ostatnie wyniki, otwarte decyzje i najbliższy krok.
Rozwijaj pozostałe pliki dopiero, gdy pojawia się treść, np. `literatura.md`,
`dziennik.md`, `eksperymenty/EXP-001.md`, `raporty/EXP-001.md`.
Zachowaj istniejące nazewnictwo i ID, zamiast narzucać nowy system.

Przy merytorycznej aktualizacji sprawdź powiązane dokumenty: popraw statusy,
podsumowania i odsyłacze dotknięte zmianą. Sprzeczności oznacz i wyjaśnij,
nie nadpisując historycznych wyników ani nie zatwierdzając otwartych decyzji.
Indeks ma jasno pokazywać studentowi, od czego zacząć, gdzie jest aktualny
plan, co już zbadano i co pozostaje do wykonania.

## Styl i ślad dowodowy

Pisz krótkie akapity i niewielkie tabele po polsku, z objaśnieniem skrótów.
Czytelnik powinien zrozumieć po co coś badano, co zrobiono i co z tego wynika,
bez czytania kodu lub logów. Szczegóły techniczne linkuj w razie potrzeby.
Nie produkuj dziennika każdego wywołania narzędzia.
Dokument naukowy nie musi brzmieć urzędowo: zaczynaj od krótkiego wyjaśnienia
celu i najważniejszej treści, używaj opisowych nagłówków i objaśniaj terminy
przy pierwszym użyciu. Szczegóły metody i dowody zachowaj w dalszej części
lub pod odnośnikiem; uproszczenie języka nie oznacza pomijania ograniczeń.

Rozróżniaj datę zapisu, datę eksperymentu i datę publikacji.
Łącz pytanie, źródło, protokół, wykonania i wniosek stabilnymi ID lub linkami.
Wyniki muszą wskazywać pliki źródłowe i identyfikatory prób. Surowych eksportów
nie zastępuj ręcznie poprawioną tabelą; analizę trzymaj osobno i opisuj
przekształcenia. Nie zmieniaj dawnych wyników bez jawnej korekty.

Przy zmianie przyjętej metody zachowaj wersję, datę i uzasadnienie.
Nie przedstawiaj hipotezy sformułowanej po eksperymencie jako wcześniejszej.
Wpisy „zaakceptowane” muszą mieć podstawę w rzeczywistej decyzji autora.

Duże lub poufne artefakty pozostaw we właściwym, dozwolonym miejscu; zapisz
identyfikator i sposób dostępu bez sekretów. Nie kopiuj prywatnych schematów,
rekordów ani kluczy API do publicznych materiałów lub zapytań wyszukiwarki.

## Formy dopasowywane do zadania

Poniższe pola są pomocą, nie obowiązkiem wypełnienia całego formularza
przy każdej rozmowie. Brak danych oznacz wprost.

### Notatka z ustalenia

- **Data i temat.**
- **Co wiemy i skąd:** dane, publikacja lub wcześniejsza decyzja.
- **Co proponujemy / co ustalono:** rozdziel te statusy.
- **Dlaczego to ważne dla pytania badawczego.**
- **Następny krok i otwarta decyzja.**

### Karta eksperymentu — przed wykonaniem

- **ID, wersja i status:** propozycja / uzgodniony / pilot / w toku / zakończony.
- **Pytanie i cel:** czego chcemy się dowiedzieć; hipoteza, jeśli dotyczy.
- **Podstawa w literaturze i oczekiwany wkład:** z odsyłaczami.
- **Porównanie:** baseline, warianty, zmieniane i stałe warunki.
- **Materiał i przebieg:** scenariusze, jednostka próby, powtórzenia,
  kolejność, ustawienia i limity.
- **Ocena:** mierniki, kryteria, zasady analizy, braków i wyłączeń.
- **Odtwarzalność i ryzyka:** co zachować i czego nie kontrolujemy.
- **Decyzje do podjęcia przed właściwą próbą.**

### Raport — po wykonaniu

Zacznij krótkim podsumowaniem dla człowieka, potem pokaż dowody:

- **Co sprawdzaliśmy:** pytanie i wersja protokołu.
- **Co faktycznie wykonaliśmy:** daty, warianty, liczby prób, odstępstwa,
  wersje środowiska i odnośniki do artefaktów.
- **Co zaobserwowaliśmy:** tabela lub wykres z jednostkami, liczebnością,
  zmiennością i niepowodzeniami; brakujące pomiary jawnie oznaczone.
- **Co to znaczy:** odpowiedź na pytanie, zakres pewności, porównanie
  z literaturą i alternatywne wyjaśnienia.
- **Czego nie możemy stwierdzić:** ograniczenia i zagrożenia trafności.
- **Co dalej:** uzasadniony kolejny eksperyment albo powód zakończenia.

Jeśli dane są częściowe, nazwij dokument raportem częściowym.
Przykład liczbowy oznacz jako ilustrację i nie umieszczaj go w tabeli wyników.

## Wykorzystanie w pracy magisterskiej

Pomagaj składać materiał w argumentację: problem i stan wiedzy → luka/pytania →
metodyka → wyniki → dyskusja i ograniczenia → wnioski.
Gdy układ uczelni jest inny, dostosuj go bez zmiany znaczenia badań.
Każda tabela, rycina i istotna teza powinna mieć wskazane źródło lub raport.
Opis aplikacji służy odtworzeniu metody, a nie zastępuje wyników.
Nie kopiuj notatek w wiele konkurencyjnych dokumentów; rozdziały odsyłają
do aktualnych źródeł, a stwierdzenia bez dowodu pozostają do uzupełnienia.
