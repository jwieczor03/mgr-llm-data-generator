# Przygotowanie do hostowania i wielu użytkowników

**Data:** 20 października 2026.

**Status:** uzgodniony kierunek rozwoju; szczegóły poniżej są propozycją architektoniczną, nie wyborem technologii.

**Podstawa:** REQ-066 i sekcja 13.4 [specyfikacji MVP](specyfikacja_mvp.md). Dokument uzupełnia [podział implementacji](podzial_implementacji.md).

## 1. Co oznacza gotowość do rozwoju

MVP pozostaje lokalne i jednoosobowe, bez logowania. Projektujemy je jednak tak, żeby przyszłe konta, hosting i współbieżne wykonania nie wymagały zastąpienia logiki przygotowania zlecenia, generowania, walidacji i raportowania.

Przygotowujemy granice i minimalny model własności danych, a nie pełną platformę wieloużytkownikową. Nie obiecujemy, że publiczne wdrożenie będzie wymagało wyłącznie zmiany konfiguracji. Nadal będą potrzebne integracje, migracje, testy izolacji i bezpieczeństwa oraz pomiary obciążenia.

Osobno rozpatrujemy:

- **hostowanie:** uruchomienie poza komputerem użytkownika;
- **wielu użytkowników:** rozpoznawanie tożsamości i kontrola dostępu do danych;
- **skalowanie pracy:** współbieżne wykonywanie zadań i rozdzielenie dostępnych zasobów.

Żaden z tych celów nie przesądza liczby mikroserwisów ani technologii wdrożenia.

## 2. Przygotowanie w MVP a późniejsze funkcje

| Obszar | Przygotowanie w MVP | Dopiero przy rozszerzeniu |
| --- | --- | --- |
| Tożsamość | Jawny kontekst wykonującego operację; lokalny adapter zwraca jeden stały wewnętrzny identyfikator właściciela. Bez ekranu logowania, hasła i rejestru kont. | Adapter weryfikujący rzeczywistą tożsamość oraz mapowanie konta na wewnętrzny identyfikator. |
| Własność danych | Projekt ma właściciela. Zlecenia, wykonania i artefakty mają jednoznaczny zakres dostępu wynikający z projektu. Nie musimy kopiować identyfikatora właściciela do każdej tabeli. | Wielu właścicieli oraz egzekwowanie dostępu w wariancie hostowanym. Współdzielenie i organizacje wymagają osobnej decyzji. |
| Sprawdzanie dostępu | Jedna granica polityki dostępu używana przez przypadki użycia; minimalna lokalna polityka obsługująca jedynego właściciela. | Polityka obsługująca rzeczywistych użytkowników. Bez konieczności dodawania obsługi tokenów do generatora i walidatora. |
| Długie wykonania | Identyfikator zadania, trwała historia, rozdzielenie startu od statusu i anulowania. Dopuszczalny pojedynczy wykonawca; bez wznawiania utraconej próby. | Współbieżność, dystrybucja pracy i wykrywanie utraty wykonawców. Automatyczne wznawianie wymagałoby osobnej zmiany zakresu. |
| Dane i pliki | Zapis przez adaptery; artefakty identyfikowane przez logiczne referencje, nie publiczne ścieżki lokalne. Lokalne pliki są dopuszczalne. | Współdzielony magazyn oraz migracja istniejących danych, jeżeli wymaga tego wdrożenie. |
| Konfiguracja | Adresy modeli, magazynów i usług oraz katalogi i limity nie są zaszyte w logice. | Konfiguracja dla wybranego środowiska hostowanego i zarządzanie sekretami tego środowiska. |
| Stan operacji | Brak globalnej „aktualnej rozmowy”, „aktualnego projektu” lub „ostatniego wyniku” współdzielonego przez wszystkie operacje. | Wiele równoległych kontekstów, odpowiednia synchronizacja i testy współbieżności. |
| Zasoby | Jawne granice wykonywania pracy i miejsce na politykę limitów; w MVP może obowiązywać jedno wykonanie naraz. | Limity per użytkownik, sprawiedliwy przydział zasobów i kontrola współdzielonego kosztu. |
| Ekspozycja sieciowa | Wariant bez logowania uruchamiany jako lokalny; nie traktujemy go jako konfiguracji do publicznego udostępnienia. | Zabezpieczone punkty wejścia, uwierzytelnianie, autoryzacja, ochrona komunikacji i przegląd wdrożenia. |

## 3. Kontekst tożsamości bez wdrażania logowania

Proponowany przepływ:

```text
MVP: lokalny adapter kontekstu ───────┐
                                     ▼
                         wewnętrzny kontekst operacji
                                     │
                                     ▼
                         kontrola dostępu do zasobu
                                     │
                                     ▼
                       przypadek użycia i zapis danych

Później: adapter logowania ──────────► ten sam rodzaj kontekstu
```

Kontekst powinien zawierać wewnętrzną tożsamość wykonującego operację oraz identyfikatory potrzebne do korelacji. Nie powinien wprowadzać tokenów, haseł lub struktur konkretnego dostawcy logowania do logiki generowania i walidacji.

Źródło kontekstu jest zaufaną częścią aplikacji. Nie przyjmujemy skutecznej tożsamości z dowolnego `user_id` przesłanego w poleceniu, pliku lub odpowiedzi modelu. OWASP wskazuje ustalanie tożsamości z uwierzytelnionego kontekstu i kontrolowanie dostępu do wskazanych obiektów jako ochronę przed IDOR [S2].

Lokalny adapter **nie uwierzytelnia użytkownika** i nie jest zabezpieczeniem wariantu hostowanego. Po dodaniu logowania brak lub błąd uwierzytelnienia nie może powodować automatycznego przejścia na lokalnego właściciela.

Uwierzytelnianie i prawo do konkretnego projektu pozostają odrębnymi odpowiedzialnościami. Sam poprawny login nie uprawnia do dowolnego wykonania lub pliku [S1].

## 4. Izolacja danych obejmuje cały przebieg

Właściciel i zakres zadania muszą być rozpoznawalne nie tylko przy liście projektów, ale także przy:

- odczycie, zmianie i ponowieniu zlecenia;
- uruchomieniu, odczycie statusu i anulowaniu wykonania;
- historii promptów, odpowiedzi modeli, raportów i kosztów;
- dostępie do plików wejściowych, kandydatów, eksportów i diagnostyki;
- przetwarzaniu w tle, odwołaniach do artefaktów i ewentualnej pamięci podręcznej.

Należy planować sprawdzanie uprawnień przy każdej operacji wymagającej dostępu, a nie tylko ukrywanie elementów interfejsu [S1]. Zgadywalność identyfikatora nie jest podstawą decyzji o dostępie; trudny do odgadnięcia identyfikator także nie zastępuje autoryzacji [S2].

Generator i walidator dostają wymagania oraz uprawniony kontekst zadania lub ograniczone referencje do jego artefaktów, nie swobodny dostęp do wszystkich projektów. Osobne usługi nie mogą ufać identyfikatorowi użytkownika z dowolnego niezaufanego nagłówka.

Wiadomości, wyniki i pliki tymczasowe nie mogą trafiać do jednego współdzielonego „bieżącego” miejsca bez identyfikacji wykonania. Przypisanie właściciela projektu nie wystarcza, jeśli pobieranie pliku omija kontrolę dostępu.

## 5. Przygotowanie do skalowania wykonawców

Proponujemy oddzielić cykl zadania od czasu życia żądania i interfejsu. Stan wykonania, migawka wymagań, kandydaci i pomiary są zapisami trwałymi, a nie wyłącznie zmiennymi procesu.

Proces obsługujący interakcję z użytkownikiem nie powinien być jedynym miejscem przechowywania stanu niezbędnego do kontynuowania i raportowania zadania. Jest to zgodne z rozdzieleniem procesów aplikacji od trwałego stanu opisywanym przez Twelve-Factor App [S3].

Na etapie MVP nie wymaga to brokera, wielu workerów ani automatycznego wznawiania po awarii. Potrzebujemy jednak kontraktów pozwalających później określić:

- kto przejął zadanie i do kiedy;
- jak uniknąć podwójnego zastosowania skutków ponowionego polecenia;
- jak aktualizować stan, liczniki rund i wybór kandydata bez wyścigów;
- jak obsłużyć anulowanie, utratę wykonawcy i spóźnioną odpowiedź;
- jakie limity obowiązują dla zadania i użytkownika.

Uzgodniono brak automatycznego retry po błędzie technicznym (REQ-070). Po timeoutcie model może nadal obsługiwać żądanie; nie deklarujemy wycofania jego skutków u dostawcy. Szczegóły timeoutów i zapis dostępnych informacji o niepewnym rezultacie pozostają częścią OD-07.

Uzgodnione REQ-069 wyklucza wznawianie anulowanego, zakończonego błędem lub utraconego wykonania w MVP. Trwały zapis służy historii, statusowi i raportowaniu; nowa próba zaczyna się od początku jako osobne wykonanie. Nie projektujemy tu wymaganego mechanizmu kontynuacji z checkpointu.

Skalowanie generowania zależy także od dostępności modeli, sprzętu i limitów API. Dodanie kolejnej instancji aplikacji samo nie zwiększa pojemności lokalnego modelu.

## 6. Konfiguracja, magazyny i modele

Proponujemy rozdzielenie konfiguracji od kodu oraz traktowanie magazynów i usług modeli jako podłączanych zależności. Twelve-Factor App opisuje takie rozdzielenie konfiguracji i usług zaplecza [S4, S5].

Nie oznacza to wspólnej bazy dostępnej bezpośrednio dla wszystkich usług. Każdy komponent pozostaje właścicielem swojego kontraktu zapisu i odczytu.

W szczególności:

- pozostałe komponenty korzystają z referencji do artefaktów, a nie z założenia, że mają dostęp do tego samego dysku;
- rdzeń nie zna ścieżek konkretnego laptopa ani stałych adresów lokalnych;
- model lokalny po przeniesieniu aplikacji musi być dostępny dla hosta wykonującego pracę; nie zakładamy automatycznego dostępu do modelu na komputerze użytkownika;
- poświadczenia są poza wiadomościami i raportami; przyszłe zasady kluczy wspólnych lub indywidualnych wymagają osobnej decyzji;
- migracja danych lokalnego właściciela do konta jest jawnym krokiem, bez nadpisywania migawek dawnych wymagań.

## 7. Co bierzemy gotowe później

Przy dodawaniu logowania proponujemy integrację gotowego rozwiązania tożsamości, nie pisanie własnej obsługi haseł i odzyskiwania kont. Dobór produktu i sposobu integracji odkładamy. OpenID Connect jest przykładem standardu uwierzytelniania, ale nie wybieramy go tutaj jako obowiązującego protokołu [S6].

Kontrola dostępu do naszych projektów, wykonań i artefaktów pozostaje odpowiedzialnością aplikacji nawet wtedy, gdy tożsamość dostarcza gotowy produkt.

Do przyszłego wdrożenia pozostawiamy także dobór trwałej kolejki, współdzielonego magazynu, mechanizmów dystrybucji pracy, infrastruktury i obserwowalności. Samo przygotowanie granic nie wymaga implementowania ich wszystkich w MVP.

## 8. Jak sprawdzić przygotowanie, zanim powstaną konta

Proponowane testy architektoniczne i kontraktowe, bez prawdziwego logowania:

1. Zastąpienie lokalnego źródła kontekstu kontrolowaną implementacją testową nie wymaga zmian generatora i walidatora.
2. Dwa sztuczne konteksty testowe nie pozwalają odczytać, anulować ani ponowić cudzych zadań lub pobrać cudzych artefaktów.
3. Zmiana identyfikatora zasobu lub deklarowanego `user_id` nie daje uprawnienia do innego właściciela.
4. Dwie niezależne operacje nie dzielą bieżącej rozmowy, kandydatów ani plików tymczasowych.
5. Odczyt statusu i historii korzysta z trwałego zapisu, a nie wyłącznie pamięci interfejsu.
6. Konfiguracja oraz testowy adapter magazynu mogą się zmienić bez modyfikowania reguł wykonania.

Sztuczne konteksty służą sprawdzeniu granic, nie udostępnieniu wielu kont w MVP. Testy te nie są certyfikacją bezpieczeństwa publicznego wdrożenia ani gwarancją wydajności.

## 9. Czego nadal nie wdrażamy

Logowania, rejestracji, odzyskiwania haseł, sesji wielu kont, ról zespołowych, organizacji, współdzielenia projektów, rozliczeń użytkowników, publicznego hostingu, automatycznego skalowania i rozbudowanej platformy orkiestracji.

W szczególności nie dodajemy nieużywanego mikroserwisu użytkowników ani kompletnej bazy kont „na zapas”.

## 10. Źródła

Dokumentacja pierwotna sprawdzona 20 października 2026; źródła uzasadniają zasady, nie stanowią wyboru gotowego stosu technologicznego.

| ID | Źródło |
| --- | --- |
| S1 | OWASP Authorization Cheat Sheet: `https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html` |
| S2 | OWASP Insecure Direct Object Reference Prevention Cheat Sheet: `https://cheatsheetseries.owasp.org/cheatsheets/Insecure_Direct_Object_Reference_Prevention_Cheat_Sheet.html` |
| S3 | The Twelve-Factor App — Processes: `https://12factor.net/processes` |
| S4 | The Twelve-Factor App — Config: `https://12factor.net/config` |
| S5 | The Twelve-Factor App — Backing services: `https://12factor.net/backing-services` |
| S6 | OpenID Connect Core 1.0: `https://openid.net/specs/openid-connect-core-1_0.html` |
