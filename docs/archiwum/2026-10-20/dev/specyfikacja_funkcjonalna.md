# Specyfikacja Funkcjonalna i Przepływ Danych (User Flow)

Dokument opisuje działanie aplikacji z perspektywy użytkownika końcowego oraz ukrytą logikę biznesową odpowiedzialną za przetwarzanie i walidację.

## 1. Frontend (Warstwa Interfejsu Użytkownika)

Aplikacja będzie podzielona na dwie główne sekcje (zakładki), aby oddzielić konfigurację od codziennej pracy.

### Zakładka 1: Generator Danych (Główny widok)
**Cel:** Zlecanie zadań i odbieranie wygenerowanych danych testowych.

* **User Stories (Funkcjonalności):**
  * Jako użytkownik chcę wprowadzić w formie tekstowej opis danych, których potrzebuję (np. "Wygeneruj 100 unikalnych transakcji").
  * Jako użytkownik nie muszę wiedzieć, z jakich konkretnie tabel składa się system – oczekuję, że aplikacja sama dobierze odpowiednie schematy na podstawie mojego zapytania.
  * Jako użytkownik chcę widzieć wygenerowany wynik i móc na niego zareagować (zaakceptować lub poprosić o reprompt z poprawkami).
* **Rozwiązania UX/UI:**
  * **Obsługa dużych plików:** Aplikacja wyświetli jedynie podgląd wygenerowanych danych (np. pierwsze 50 linii z kolorowaniem składni), aby nie obciążać interfejsu. Poniżej znajdą się opcje: `[Pobierz plik .sql / .json]` oraz `[Kopiuj do schowka]`.

### Zakładka 2: Baza Wiedzy i Schematy (Zarządzanie Kontekstem)
**Cel:** Konfiguracja systemu, dodawanie definicji i zarządzanie regułami.

* **User Stories (Funkcjonalności):**
  * Jako użytkownik chcę wgrać dokumentację API (Swagger/OpenAPI), przykładowe pliki JSON lub schematy relacyjnych baz danych (DDL).
  * Jako użytkownik chcę mieć podgląd obecnych schematów w bazie i możliwość aktualizacji ich pojedynczych fragmentów, ponieważ systemy korporacyjne często ulegają zmianom.
* **Rozwiązania UX/UI:**
  * **Mapowanie Relacji (Klucze obce):** Po wgraniu schematów system automatycznie próbuje wykryć relacje (np. łączy pole `client_id` z `id` z tabeli `clients`). Użytkownik widzi te powiązania na liście i może je zaakceptować lub ręcznie edytować.
  * **Reguły Biznesowe:** Użytkownik ma możliwość dodawania specyficznych reguł tekstowych do konkretnych pól (np. adnotacja: "Pole 'country' musi zawsze przyjmować wartość 2-literowego kodu ISO, np. PL").

---

## 2. Backend (Logika Biznesowa i Architektura Hybrydowa)

### Krok 1: Ingestia i Zapis (Obsługa Zakładki 2)
Po wgraniu plików przez użytkownika, Backend parsuje je (np. wyciągając strukturę tabel SQL lub definicje obiektów JSON) i zapisuje w formacie czytelnym dla modeli sztucznej inteligencji w bazie wektorowej/relacyjnej.

### Krok 2: Zrozumienie intencji i dobór schematów (Agentic Routing)
Kiedy użytkownik zleca wygenerowanie danych w Zakładce 1, system pod maską wykonuje dodatkowy krok:
1. Analizuje zapytanie (np. "transakcje i produkty").
2. Pobiera z bazy wiedzy tylko te schematy, które są potrzebne (tabele `Transactions`, `Products`, `Clients`), aby nie zaśmiecać pamięci modelu całą bazą danych firmy.

### Krok 3: Generowanie i Trójpoziomowa Walidacja
Model LLM generuje surowy ciąg znaków, który trafia do walidatora (warstwa deterministyczna w kodzie Python):
1. **Walidacja Strukturalna:** Sprawdzenie, czy format (JSON, XML, SQL) jest poprawny syntaktycznie (np. czy domknięto wszystkie nawiasy).
2. **Walidacja Typów (np. za pomocą Pydantic):** Sprawdzenie podstawowej poprawności danych (np. imiona nie zawierają cyfr, pesel ma 11 znaków, a kwota to wartość liczbowa).
3. **Walidacja Reguł Użytkownika:** Weryfikacja dodatkowych zasad ustawionych w Zakładce 2 (np. walidacja kodów krajów, brak halucynacji w słownikach).

### Krok 4: Auto-healing (Samonaprawianie)
Jeśli wygenerowane dane nie przejdą walidacji w Kroku 3, system nie pokazuje błędu użytkownikowi. Zamiast tego kod automatycznie wysyła reprompt do modelu LLM (np. *"Popraw wynik. W wierszu 4 wystąpił błąd: oczekiwano liczby całkowitej w polu 'wiek'."*). Dopiero po osiągnięciu sukcesu (lub wyczerpaniu np. 3 prób poprawy) dane trafiają na Frontend.