# Techniczne zadania dla junior fullstack developera

Czytaj przy rozpisywaniu uzgodnionego obszaru na szczegółowe zadania i podzadania. Opis ma pozwolić juniorowi zacząć pracę bez zgadywania wymagań i architektury; nie jest gotowym kodem rozwiązania ani wykładem o całym projekcie.

## Poziom konkretu

- Tytuł zaczynaj od konkretnej czynności i obiektu zmiany. Zamiast „Obsłużyć dane” nazwij uzgodniony odczyt, zapis, widok lub integrację.
- Podaj istniejący moduł, plik, komponent lub analogiczny fragment kodu, na którym junior może się oprzeć. Ścieżki istniejących elementów sprawdź w repozytorium.
- Nowy plik lub moduł wskazuj jako **do utworzenia**, zgodnie z uzgodnioną strukturą. Proponowanej ścieżki nie przedstawiaj jako istniejącej ani zatwierdzonej.
- Rozpisz czynności w kolejności wykonania. Zamiast „dodaj walidację” podaj konkretne uzgodnione reguły i wynik niepoprawnych danych. Zamiast „napisz testy” wskaż zachowania i oczekiwane wyniki.
- Używaj kontraktów danych, nazw pól, metod, tras, statusów odpowiedzi i stanów UI tylko wtedy, gdy wynikają ze sprawdzonych źródeł lub decyzji użytkownika. Brak kontraktu to powód do pytania, nie do jego wymyślenia.
- Uwzględnij potrzebne szczegóły właściwe danemu zadaniu: np. zmianę schematu i migrację, dostęp do endpointu, stany formularza czy zachowanie integracji po błędzie. Nie dodawaj pełnej listy zagadnień fullstack do każdego opisu.
- Zrozumiały język nie oznacza pomijania technicznych szczegółów. Krótko wyjaśnij skrót lub nieoczywistą regułę, jeśli jest potrzebna do wykonania pracy.

## Szablon zadania / podzadania

Dopasuj długość do wielkości zmiany, zachowując poniższe informacje:

```markdown
### [ID] Tytuł opisujący konkretną zmianę

**Story / zadanie nadrzędne:** ID i nazwa
**Cel:** jaki mały rezultat ma powstać i po co.
**Źródło:** specyfikacja/sekcja i istotne uzgodnienia.
**Punkt startowy:** sprawdzone moduły/pliki oraz istniejący wzorzec.
**Zależności:** co musi być gotowe przed rozpoczęciem; „brak”, jeśli brak.

**Co należy zrobić:**
1. Konkretna czynność w określonym miejscu.
2. Następna czynność, z uzgodnionym zachowaniem i kontraktem.
3. Istotna obsługa błędów lub stanów brzegowych.

**Poza zakresem:** istotne rzeczy, których nie wykonywać w tym zadaniu.

**Kryteria ukończenia:**
- Obserwowalny rezultat pozwalający ocenić poprawność.
- Oczekiwany wynik dla uzgodnionego przypadku błędnego/brzegowego.

**Jak sprawdzić:**
- Konkretne przypadki testowe i oczekiwane wyniki.
- Sprawdzona komenda projektu lub ręczne kroki weryfikacji.

**Do wyjaśnienia:** nierozstrzygnięte decyzje lub „brak”.
```

To szablon opisu, nie źródło wymagań. Sekcję niewystępującą w danym zadaniu można pominąć. Nie kopiuj ogólników jako gotowej treści.

## Sprawdzenie przed uznaniem za gotowe

Sprawdź, czy junior wie, od czego zacząć, co zmienić i jaki wynik pokazać. Kryteria ukończenia opisują zachowanie, nie tylko istnienie pliku lub „działa poprawnie”.

Nie wpisuj niezweryfikowanych komend jako działających. Jeśli projekt nie ma ustalonego narzędzia testowego albo sposobu uruchomienia, wyjaśnij to z użytkownikiem zamiast wybierać go samodzielnie.

Zadanie z brakującą decyzją konieczną do implementacji pozostaje **do wyjaśnienia**. Akceptacja opisu nie może maskować braku kontraktu, reguły lub punktu integracji. Estymatę i harmonogram dopisuj wyłącznie po ich uzgodnieniu.
