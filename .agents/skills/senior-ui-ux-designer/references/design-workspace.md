# Mały design system, dokumentacja i katalog makiet

Czytaj przed tworzeniem fundamentu wizualnego i układaniem plików. Celem jest jeden punkt wejścia dla dewelopera i wspólny wygląd wszystkich ekranów, bez osobnego portalu dokumentacyjnego ani rozbudowanej infrastruktury.

## Miejsce i struktura

Wykorzystaj istniejące miejsce na projekty UI, jeśli spełnia te potrzeby. Gdy go nie ma, zaproponuj użytkownikowi prosty katalog w repozytorium, np.:

```text
docs/ui/
  index.html                  # punkt wejścia: ekrany, przepływy, statusy i linki
  design-system.md            # krótki opis zasad wyglądu i decyzji
  design-system.html          # żywa galeria tokenów i komponentów w obu motywach
  shared/
    tokens.css                # semantyczne tokeny, wartości light/dark
    components.css            # wspólne komponenty
    preview.js                # wspólna obsługa podglądu, gdy potrzebna
  screens/
    <obszar>/
      <ekran>/
        index.html            # aktualna makieta z oboma motywami i stanami
        notes.md              # tylko informacje specyficzne dla tego ekranu
```

To przykład organizacji artefaktów projektu, nie struktura samego skilla ani wymóg tworzenia wszystkich pustych plików. Uzgodnij katalog główny i dopasuj nazwy do repozytorium. Nie przenoś istniejących materiałów bez uzgodnienia. Nie buduj makiet aplikacji podczas samej instalacji tego skilla.

## Minimalny fundament wizualny

- Zdefiniuj semantyczne role, np. tło strony, powierzchnia, tekst główny i pomocniczy, obramowanie, akcent, fokus, sukces, ostrzeżenie i błąd. Każda rola otrzymuje wartości light/dark. Komponenty korzystają z ról zamiast lokalnych kolorów.
- Wspólne tokeny obejmują też typografię, odstępy, promienie i inne faktycznie używane reguły. Dobór wartości jest propozycją do akceptacji, nie gotowym, narzuconym brandem.
- Galeria pokazuje tylko potrzebne teraz komponenty i ich istotne stany, np. przycisk, pole, karta czy komunikat. Dodawaj komponenty wtedy, gdy wynikają z przepływu.
- Te same pliki CSS obsługują galerię i wszystkie ekrany. W obu motywach zachowaj te same znaczenia i zachowanie komponentów.
- Zapewnij dostępny przełącznik podglądu light/dark na galerii i makietach, oznaczony jako narzędzie projektowe. Zachowanie motywu w docelowej aplikacji uzgodnij osobno. Nie twórz dwóch niezależnie utrzymywanych kopii HTML dla obu trybów.

## Prosta dokumentacja

W jednym krótkim dokumencie zapisuj:

- kierunek wizualny i zaakceptowane zasady typografii, odstępów, układu oraz responsywności;
- znaczenie tokenów i różnice między motywami, z odsyłaczem do CSS jako źródła aktualnych wartości — nie powielaj ręcznie całej tabeli wartości;
- używane komponenty, ich przeznaczenie i ważne reguły zachowania, z linkiem do galerii;
- decyzje z krótkim uzasadnieniem, statusem i datą akceptacji oraz otwarte kwestie.

Nie kopiuj wymagań biznesowych: linkuj do właściwej specyfikacji. Notatki ekranu opisują jego cel, powiązany scenariusz, specyficzne interakcje, stany, zachowanie na małym ekranie i symulacje; nie powtarzają wspólnych zasad.

## Dostępność makiet dla deweloperów

- Indeks HTML udostępnia link do dokumentacji i galerii oraz listę ekranów pogrupowaną według obszarów lub przepływów. Przy ekranie podaj stabilny identyfikator, nazwę, cel, status (roboczy/do akceptacji/zaakceptowany/wymaga ponownej akceptacji), datę aktualizacji i link do notatek.
- Linkuj do istotnych stanów lub napisz, jak je odtworzyć. Zapewnij łatwe przejścia między ekranami przepływu oraz powrót do indeksu.
- Trzymaj aktualną makietę pod stabilną ścieżką. Kolejne iteracje aktualizują ją w miejscu; nie mnoż plików `final-v2-new`. Historia repozytorium może przechowywać wcześniejsze wersje, ale nie wykonuj commitów w ramach samego projektowania. Archiwum lub wariant porównawczy twórz tylko, gdy potrzebny, z jednoznacznym oznaczeniem i linkiem.
- Przy zmianach aktualizuj indeks i dotknięte notatki. Zmiana wspólnego komponentu musi być odzwierciedlona w galerii, dokumentacji i sprawdzeniu używających go ekranów w obu motywach; oznacz utratę aktualności wcześniejszej akceptacji tam, gdzie zmienił się zatwierdzony wygląd.
- Zapewnij prosty sposób uruchomienia: bezpośrednie otwarcie indeksu, jeśli działa, albo jedna sprawdzona komenda lokalnego serwera zgodna z projektem. Umieść tę informację w istniejącej dokumentacji/indeksie. Sprawdź ścieżki względne, CSS, JS i linki po takim uruchomieniu; nie deklaruj testu, którego nie wykonano.
- Pokaż użytkownikowi lokalizację indeksu. Link do niego w istniejącym punkcie wejścia dokumentacji repozytorium dodaj w uzgodnionym zakresie, zamiast pozostawiać katalog możliwy do znalezienia tylko z historii czatu.
