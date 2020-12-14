# WiFi_Termometer-AP-WWW-
[ESP32] [Micropython]

Termometr Wi-Fi (WWW Server)

Paweł Zięba 05.04.2020

ESP32 wysyła czas, liczony od startu nadawania i  temperaturę z czujnika ds18b20 na stronę WWW.
Wykrywanie braku czujnika 1-wire i podłączonego urządzenia Wi-Fi.
Praca w trybie ACCES POINT jako server.
Serwer DNS.
Adres strony WWW: termometr.pl (dowolna domena działa) lub 192.168.2.1

Po uruchomieniu dioda mruga co 0,4s - czeka na połączenie,
po udanym połączeniu z telefonem dioda kilka razy mruga co 0,2s.
Następnie zaczyna nasłuchiwać na porcie 80 - dioda nie świeci.
Po odebraniu zapytania, jeżeli client żąda strony - odsyła stronę html, jeżeli client żąda danych z czujnika temperatury -
odsyła te dane w tle.

dioda mruga co 0,4s: oczekiwanie na podłączenie urządzenia Wi-Fi
dioda mruga co 1s: pomiar temperatury i wysyłanie danych
dioda świeci cały czas: brak czujnika temperatury
dioda nie świeci - oczekiwanie na zapytanie od przeglądarki lub nie podłączone urządzenie Wi-Fi

*jeżeli urządzenie Wi-Fi zostanie odłączone w trakcie obsługi zapytania to dioda mruga co 0,4s*

dane AP:
SSID: Termometr Wi-Fi
HASŁO: <BRAK HASŁA>
IP: 192.168.2.1
maska: 255.255.255.0
brama: 192.168.2.1
dns: 8.8.8.8

W przeglądarce należy wpisać adres IP esp32: 192.168.2.1