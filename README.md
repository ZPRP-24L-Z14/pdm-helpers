# pdm-helpers

## Problem:

PDM usuwa wirtualne środowisko virtualenv po wywołaniu pozornie niezwiązanych komend np. "pdm list"

[link do oryginalnego issue](https://github.com/pdm-project/pdm/issues/1701)

## Szukanie źródła problemu:

Początkowo mieliśmy sporo problemów z reprodukcją tego issue. Nawet przy instalacji setek paczek nie udało się odpowiednio spowolnić Pythona, aby powtórzyć ten problem na względnie szybkiej maszynie.
Podczas szukania tego błędu, stworzyliśmy narzędzia do znajdowania najlżejszych paczek z pip, oraz do automatycznego tworzenia projektów w pdm, instalowaniu wszystkich paczek oraz testowaniu jak zmienił się czas wykonywania różnych skryptów.

Kiedy nie udało nam się wydłużyć czasu uruchomienia do 5s, zaczęliśmy przeszukiwać kod pdma, w poszukiwaniu miejsc, które mogłyby spowodować ten błąd.

Wtedy trafiliśmy na opcję `FINDPYTHON_GET_VERSION_TIMEOUT` w bibliotece findpython, którą pdm używa do znajdowania i weryfikacji wersji pythona. Po ustawieniu tego parametru na bardzo niską wartość (dokładnie to 0.01), udało się uzyskać ten sam efekt, co w oryginalnym błędzie: venv został usunięty.

Dzięki temu wiedzieliśmy, że problem jest całkowicie niezależny od pdma, bo występuje tylko jak findpython uzna że instalacja Pythona jest uszkodzona (uruchamia się zbyt długo)

Korzystając z tej informacji, wiedzieliśmy, że szukamy powodu, dla którego Python się dłużej inicjalizuje, jeżeli mamy zainstalowane wiele bibliotek. Wtedy dotarliśmy do naszego proponowanego rozwiązania.

## Symulacja problemu:

1. Utworzenie pustego projektu
2. Wykonanie `export FINDPYTHON_GET_VERSION_TIMEOUT=0.01`
3. `pdm list`

Podczas wykonywania dowolnej komendy, pdm sprawdza wersję Pythona przy pomocy findpython. Jako że nadpisaliśmy domyślny timeout, to jeżeli ten proces zajmie więcej niż 0.01s, to findpython się "poddaje" i pdm uznaje że instalacja jest uszkodzona i usuwa virtualenv.

## Przyczyna:

Paczka findpython uznaje instalację Pythona za uszkodzoną, jeśli uruchomienie interpretera trwa dłużej niż 5 sekund.

## Proponowane rozwiązanie:

W tym przypadku, sugerujemy się użycie argumentu -S podczas sprawdzania wersji Pythona, co wyłącza automatyczny import modułu site.
Dzięki temu Python uruchamia się znacznie szybciej, ponieważ nie ładuje żadnych zainstalowanych bibliotek.
To podejście pozwala na uniknięcie timeoutu podczas sprawdzania wersji Pythona przez pdm.

Po głębszej analizie problemu i związanych bibliotek odkryliśmy, że problem został już rozwiązany w bibliotece findpython rok temu przez push bezpośrednio na branch main przez głównego maintainera:
https://github.com/frostming/findpython/commit/0213bdb843fc8d82717c01e5f58d71faf45a9c53

Ze względu na to jak ukryte było to rozwiązanie, to nie udało nam się go zidentyfikować wcześniej.

To tłumaczy nasze problemy z odtworzeniem problemu bez argumentu `FINDPYTHON_GET_VERSION_TIMEOUT`, ponieważ było to niemożliwe. Można zauważyć, że nie ma różnicy w czasach wykonywania testu z findpython w naszym narzędziu, co potwierdza naszą teorię że błąd ten został rozwiązany.

W związku z tym nie tworzyliśmy własnego pull requesta.

Jeżeli Python uruchamia się ponad 5s z argumentem -S to błąd ten nadal wystąpi, ale jest to sytuacja ekstremalna.
Jeżeli jednak ma się na tyle wolne urządzenie, można ręcznie ustawić parametr `FINDPYTHON_GET_VERSION_TIMEOUT` na odpowiednio dużą wartość.

## Testowanie:

Nasze narzędzie `test_runner` wykonuje następujące operacje:

1. Tworzy projektu w pdmie
2. Testuje czas wykonywania komend
3. Instalacje dependency
4. Ponowienie testuje czas wykonywania komend
5. Wyświetla różnicę czasu między oboma odtworzeniami

Wykonywane jest wiele pomiarów czasu, aby zminimalizować wpływ obciążenia komputera i innych zmiennych losowych.

Dzięki temu narzędziu udało nam się zauważyć, że nasze próby powtórzenia tego issue nie mogły się udać.
