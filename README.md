# pdm-helpers

Problem:

PDM usuwa wirtualne środowisko virtualenv po wywołaniu pozornie niezwiązanych komend np. "pdm list"

Odtworzenie problemu:
1. Utworzenie pustego projektu 
2. Wykonanie FINDPYTHON_GET_VERSION_TIMEOUT=0.1 
3. pdm list

Problem z PDM występuje podczas sprawdzania wersji Pythona. 
Jest ona sprawdzana przy wykonaniu jakiejkolwiek komendy pdm-a
Jeśli Python nie uruchomi się w ciągu 0.1 sekundy, narzędzie zgłasza błąd, co sugeruje, że instalacja Pythona jest uszkodzona.

Przyczyna:

Paczka findpython uznaje instalację Pythona za uszkodzoną, jeśli uruchomienie interpretera trwa dłużej niż 5 sekund.

Proponowane rozwiązanie:

W tym przypadku, sugeruje się sprawdzenie wersji Pythona za pomocą argumentu -S, co wyłącza automatyczny import modułu site. 
Dzięki temu Python uruchamia się znacznie szybciej, ponieważ nie ładuje żadnych zainstalowanych bibliotek. 
To podejście pozwala na uniknięcie timeoutu podczas sprawdzania wersji Pythona przez PDM.

Po głębszej analizie problemu i związanych bibliotek odkryliśmy, że problem został już rozwiązany w bibliotece findpython rok temu przez push bezpośrednio na branch main przez głównego maintainera: 
https://github.com/frostming/findpython/commit/0213bdb843fc8d82717c01e5f58d71faf45a9c53?fbclid=IwZXh0bgNhZW0CMTAAAR2-Ti9QydVjWVLr6OK1_Bg4zCT0kAm15cqojzB8pSv1u9ChqmJEatrG9MA_aem_AU60VrNhC9G_CpLFzDdC6QKWZm68NqA7i7P_wTI_e4-jeH81y8GyZu8QAnE81-Z1rem4Awyx6pSZp0sfTYvtmqqn

Testowanie:

1. Tworzenie projektu w pdmie
2. Testuje długości wykonywania komend
3. Instalacje dependency
4. Ponowienie
5. Wyświetlenie różnicy między oboma odtworzeniami ( procedura jest powtarzana, a wyniki uśredniane)

W normalnych warunkach na szybkim komputerze python uruchamia się w ułamku sekundy. Przez to bardzo ciężko jest wystarczająco spowolnić jego pracę, aby uruchomienie interpretera zajęło ponad 5s
