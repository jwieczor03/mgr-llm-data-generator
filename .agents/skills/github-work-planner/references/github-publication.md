# Publikacja uzgodnionego planu

Czytaj tylko przy publikowaniu lub aktualizacji planu na GitHubie. Nie zapisuj niczego zewnętrznie podczas samego projektowania skilla ani przygotowywania szkicu backlogu.

## Ustal cel i dostęp

- Ustal konkretne repozytorium `owner/repo` i docelowy GitHub Project. Remote repozytorium jest wskazówką, nie dowodem wyboru właściwej tablicy. Jeżeli brak jednoznacznego celu, zapytaj o niego przed zapisem.
- Sprawdź istniejące instrukcje i szablony issues, zadania otwarte i zamknięte istotne dla planu oraz elementy projektu. Nie ograniczaj deduplikacji do tytułu: porównaj cel i zakres.
- Potwierdź właściciela projektu, jego identyfikator, istniejące pola i dopuszczalne wartości. Nie utożsamiaj repozytorium z właścicielem projektu ani utworzenia issue z dodaniem go na tablicę.
- Preferuj dostępny GitHub connector/MCP; w lokalnym środowisku można użyć uwierzytelnionego `gh`. Sprawdź dostęp do repozytorium i projektu oddzielnie. Przy braku narzędzia sprawdź integrację GitHub; nie instaluj ani nie inicjuj logowania bez zlecenia.
- Błąd uprawnień nie uzasadnia poszerzania zakresów tokenu ani zmiany widoczności projektu. Wyjaśnij wymagany dostęp; nie odczytuj i nie wypisuj sekretów.

## Uzgodnij zakres zapisu

Pokaż lub wykorzystaj wcześniej zaakceptowaną listę tworzeń/aktualizacji: story, zadania, podzadania, istniejące issues do ponownego użycia oraz projekt docelowy. Publikuj tylko uzgodnioną partię, nie nierozstrzygnięte szkice z innych obszarów. Wskaż istotne odstępstwa od uzgodnionego planu.

Wymagana jest jednoznaczna dyspozycja publikacji lub aktualizacji. „Podoba mi się plan” nie znaczy „utwórz issues”. Natomiast „dodaj uzgodniony plan do projektu X w repo Y” wystarcza dla tych konkretnych operacji. Zmiany zakresu, brakujące rozstrzygnięcia i dodatkowe operacje uzgadniaj osobno.

Nie twórz projektu, etykiet, milestone'ów ani pól jako ubocznego skutku publikacji zadań. Używaj istniejących wartości zgodnie z ustalonym mapowaniem. Nie przypisuj osób ani terminów na podstawie domysłów. Nie publikuj materiałów wewnętrznych w publicznym repozytorium bez sprawdzenia, że są przeznaczone dla tego odbiorcy.

## Zapis i hierarchia

1. Zmapuj stabilne identyfikatory planu na znalezione lub nowo utworzone issues. Twórz wyłącznie brakujące elementy, zapisując zwrócony numer, identyfikator i URL po każdej operacji.
2. Odwzoruj uzgodnioną hierarchię `story → zadanie → podzadanie`: utwórz/reużyj elementy od nadrzędnych do podrzędnych i połącz każdy poziom natywną relacją sub-issue, gdy docelowe narzędzie i GitHub ją obsługują. Sprawdź możliwość zagnieżdżenia przed zapisem; nie zakładaj, że link w opisie tworzy tę relację ani że wymagany jest osobny typ issue nazwany „Story”.
3. Brak obsługi natywnej hierarchii zgłoś użytkownikowi. Zaproponuj uzgodniony wariant z linkami/checklistą albo narzędzie obsługujące relację; nie zastępuj wymaganej hierarchii bez słowa i nie deklaruj jej utworzenia.
4. Dodaj issues do właściwego projektu, uwzględniając uzgodniony sposób prezentacji rodziców i dzieci. Ustawiaj tylko uzgodnione pola; respektuj istniejący workflow. Nie oznaczaj nowego zadania jako rozpoczętego lub ukończonego.
5. Zależności realizuj przez obsługiwane relacje blokowania, jeżeli są dostępne, albo jawne odnośniki w opisach. W raporcie rozróżnij relację natywną i link opisowy.

Nie utrwalaj z pamięci payloadów ani nazw mutacji API dla sub-issues i Projects. Sprawdź schematy dostępnych narzędzi, lokalne `gh … --help` i, gdy potrzeba, aktualną oficjalną dokumentację. Nie zgaduj identyfikatorów pól ani opcji.

Źródła do sprawdzania możliwości:

- GitHub Issues: https://docs.github.com/en/issues
- GitHub Projects: https://docs.github.com/en/issues/planning-and-tracking-with-projects
- GitHub CLI: https://cli.github.com/manual/

## Ponowienia i częściowy sukces

- Przy timeoutcie lub niejednoznacznym wyniku zapisu najpierw odczytaj stan: znajdź issue, relację lub element projektu. Nie ponawiaj tworzenia w ciemno.
- Gdy issue powstało, lecz dodanie do projektu zawiodło, zachowaj issue i wznów od brakującego etapu. Nie twórz drugiego ani nie usuwaj pierwszego jako automatycznego rollbacku.
- Przy błędzie autoryzacji, braku obsługiwanej relacji lub powtarzającym się błędzie zatrzymaj zależne operacje, podaj stan i wymagane działanie. Nie prowadź nieograniczonych ponowień; pojedyncze ponowienie po sprawdzeniu stanu ma sens dla przejściowego błędu.
- Przy aktualizacji zachowuj ręczne zmiany i obcy zakres istniejącego issue. Jeżeli plan wymaga ich nadpisania lub zamknięcia zadania, uzgodnij to zamiast traktować jako synchronizację techniczną.

## Odczyt kontrolny i wynik

Po zapisie sprawdź opis i URL każdego zmienionego issue, faktyczne relacje rodzic–dziecko, członkostwo w projekcie oraz zapisane pola. Sam udany zapis issue nie potwierdza obecności na tablicy ani w konkretnej filtrowanej perspektywie.

Zwróć link do projektu i mapowanie `ID planu → issue URL`, z rozróżnieniem: utworzone, użyte ponownie, zaktualizowane, dodane do projektu i nieukończone. Raportuj częściowy sukces zamiast ogłaszać pełną publikację, gdy pozostały błędy. Nie przedstawiaj szkicu jako zapisanego issue.
