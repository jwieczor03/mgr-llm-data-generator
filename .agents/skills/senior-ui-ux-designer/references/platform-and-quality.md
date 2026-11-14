# Wzorce platformowe i jakość makiet

Czytaj przy wyborze wzorców oraz przed prezentacją HTML. Projekt dotyczy wyłącznie weba. Dobieraj kryteria do uzgodnionych przeglądarek, urządzeń i zakresu; light i dark mode sprawdzaj zawsze.

## Inspiracja rzeczywistymi stronami WWW

Apple i Google są preferowanymi punktami odniesienia wskazanymi przez użytkownika. Chodzi o to, **jak projektują swoje strony i produkty webowe**, nie o obowiązek naśladowania systemowych interfejsów iOS/Android ani wdrożenia konkretnej biblioteki.

- Przy ustalaniu kierunku obejrzyj aktualne, konkretne strony Apple i Google odpowiednie do zadania. Dobierz typ przykładu do celu: strona marketingowa może inspirować kompozycją i prezentacją treści, ale nie musi być dobrym wzorcem panelu roboczego lub złożonego formularza.
- Punkty startowe, nie obowiązkowa lista do przejrzenia: https://www.apple.com/ oraz https://about.google/ i https://design.google/; w razie potrzeby wybierz konkretny produkt webowy. Nie przypisuj tym markom niezaobserwowanych cech ani jednego niezmiennego stylu.
- Pokaż krótką selekcję inspiracji z linkami, datą obejrzenia, konkretną obserwacją i propozycją zastosowania. Odróżniaj zaobserwowany wzorzec od własnej interpretacji. Jeśli strona jest niedostępna, ujawnij to; nie opisuj jej wyglądu wyłącznie na podstawie fragmentu wyników wyszukiwania.
- Inne źródła są dozwolone. Uzasadniaj wybór dopasowaniem do scenariusza, nie samym prestiżem marki czy popularnością.
- Czerp z zasad, nie kopiuj kompozycji 1:1, logo, tekstów ani charakterystycznych zasobów marki. Uzgodnione inspiracje przełóż na własny, spójny mały design system, działający w light i dark mode nawet wtedy, gdy przykład pokazuje tylko jeden motyw.
- Zapisz zaakceptowane inspiracje i krótki wniosek w dokumentacji wyglądu. Nie twórz rozbudowanego katalogu inspiracji bez potrzeby.

## Uzupełniające wytyczne jakości

- Apple Human Interface Guidelines: https://developer.apple.com/design/human-interface-guidelines/
- Apple — Accessibility: https://developer.apple.com/design/human-interface-guidelines/accessibility
- Google Material Design: https://m3.material.io/
- Material — Accessibility: https://m3.material.io/foundations/accessible-design/overview
- W3C WCAG 2.2: https://www.w3.org/TR/WCAG22/
- WAI-ARIA Authoring Practices: https://www.w3.org/WAI/ARIA/apg/

Sprawdzaj aktualne oficjalne sekcje dotyczące konkretnej decyzji, zamiast cytować całą dokumentację. Podawaj użyte źródło, datę sprawdzenia i zastosowanie. Nie twierdź, że źródło sprawdzono, jeśli nie dało się go odczytać. Przy braku dostępu ujawnij ograniczenie; nie podawaj z pamięci zmiennych szczegółów jako aktualnych wymagań.

HIG i Material uzupełniają inspiracje stronami, ale ich nie zastępują; nie są wymogiem używania określonej biblioteki. Stosuj je tylko tam, gdzie wspierają użyteczność weba; nie projektuj aplikacji natywnych ani ich imitacji.

Gdy źródła zalecają różne wzorce, priorytetem są zachowanie przeglądarki, semantyka HTML i dostępność webowa; wyjaśnij kompromis użytkownikowi. Uzgodnij poziom dostępności; proponuj WCAG 2.2 AA jako punkt odniesienia, nie jako już zaakceptowane wymaganie lub deklarację certyfikacji.

## Kontrola adekwatna do scenariusza

- **Hierarchia i zadanie:** jedna czytelna dominanta tam, gdzie jest potrzebna; istotne treści i działania łatwe do odnalezienia; jednoznaczne etykiety; brak zbędnych kroków i ślepych uliczek.
- **Nawigacja i stany:** wiadomo, gdzie użytkownik jest, co się wydarzyło i co może zrobić dalej. Cofnięcie, anulowanie, błąd i ponowienie nie gubią danych niezgodnie z ustalonym zachowaniem.
- **Formularze:** trwałe etykiety, sensowne typy pól, pomoc przy formacie i błędy przy właściwych polach. Placeholder nie zastępuje etykiety. Błąd nie jest sygnalizowany samym kolorem.
- **Czytelność i przestrzeń:** spójna skala typografii i odstępów; tekst nie znika przy powiększeniu; długie treści nie nachodzą na kontrolki; gęstość pasuje do zadania.
- **Responsywność:** uzgodnione urządzenia i zachowanie pośrednie, nie tylko jeden zrzut desktop/mobile. Sprawdź przepełnienia, kolejność treści i dostępność głównego działania przy małym oknie.
- **Semantyka i klawiatura:** prawdziwe przyciski i linki, etykiety dostępności, logiczny porządek fokusu, widoczny i niezasłonięty fokus; bez pułapek klawiaturowych. Dla własnego dialogu sprawdź wejście, zamknięcie i powrót fokusu.
- **Kontrast i percepcja:** zmierz kontrast kluczowych par tekst/tło i elementów sterujących względem przyjętego kryterium osobno w light i dark mode. Nie oceniaj kontrastu „na oko”; uwzględnij stany i przezroczystości. Nie opieraj znaczenia tylko na kolorze, położeniu lub hoverze.
- **Motywy:** identyczna funkcjonalność i hierarchia w obu trybach; czytelne powierzchnie, obramowania, fokus, formularze, komunikaty, ikony, wykresy i grafiki. Dark mode nie jest mechanicznym odwróceniem kolorów. Sprawdź przełączanie i uzgodnione zachowanie preferencji; nie uznawaj ekranu za ukończony po obejrzeniu jednego motywu.
- **Dotyk i ruch:** cele dotykowe i odstępy odpowiednie dla weba, alternatywa dla gestów, jeśli potrzebna, oraz respektowanie ograniczenia ruchu. Konkretne progi zweryfikuj we właściwym źródle; nie przenoś bezpośrednio natywnych pt i dp do CSS.
- **Spójność i lekkość:** powtarzalne komponenty, oszczędne akcenty, ruch wspierający orientację; bez dekoracyjnych cieni, gradientów i efektów utrudniających zadanie.
- **Treści i wiarygodność:** właściwy język, realistyczne długości i formaty danych, jasne konsekwencje działań. Bez dark patterns i wymyślonych wyników badań, statystyk czy opinii użytkowników.

Zapisuj wynik jako: **sprawdzone / wykryty problem / niesprawdzone**, z zakresem i metodą. Automatyczny audyt, screenshot ani pojedyncza próba klawiaturą nie dowodzą pełnej dostępności. Sesję z prawdziwymi użytkownikami proponuj tam, gdzie trzeba sprawdzić hipotezę UX; nie symuluj jej wyników.
