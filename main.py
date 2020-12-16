import machine
from machine import Pin

import network

import socket

from microDNSSrv import MicroDNSSrv

from time import sleep

import onewire
import ds18x20


#zmienne globalne
ds_ok = False     #flaga obecności czujnika temperatury


#definicje wiadomości msg
msg_ds_error = "Nie wykryto czujnika temperatury"



#konfiguracja AP
ap_ip = "192.168.2.1"
ap_mask = "255.255.255.0"
ap_gate = "192.168.2.1"
ap_dns = "8.8.8.8"
ap_ssid = "Termometr WI-FI"


#nazwa strony www  *dowolna domena
termo_url = "termometr.*"



#utworzenie socketu do komunikacji 
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#WLAN
ap = network.WLAN(network.AP_IF)

#RTC
rtc = machine.RTC()

#DS18B20
ds_pin = machine.Pin(15)
ds = ds18x20.DS18X20(onewire.OneWire(ds_pin))



#inicjalizacja pinu LED
led = Pin(2, Pin.OUT)



#inicjalizacja WLAN
ap.active(True)
ap.ifconfig((ap_ip, ap_mask, ap_gate, ap_dns))
ap.config(essid = ap_ssid)



#oczekiwanie na podłączenie urządzenia Wi-Fi
print("Oczekiwanie na podłączenie urządzenia Wi-Fi")
while ap.isconnected() == False:
    led.value(1)
    sleep(0.2)
    led.value(0)
    sleep(0.2)
    print(".", end =" ")
    
print("")
print("Połączenie udane")
print("AP CONFIG:  ", end =" ")
print(ap.ifconfig())



#sygnalizacja podłączenia irządzenia Wi-Fi - LED
led.value(1)
sleep(2)
led.value(0)
sleep(0.1)
led.value(1)
sleep(0.1)
led.value(0)
sleep(0.1)
led.value(1)
sleep(0.1)
led.value(0)
sleep(0.1)
led.value(1)
sleep(0.1)
led.value(0)
sleep(0.1)
led.value(1)
sleep(0.1)
led.value(0)
sleep(0.1)
led.value(1)
sleep(0.1)
led.value(0)



#uruchomienie serwera DNS
try:
    if MicroDNSSrv.Create( {termo_url : ap_ip } ) :
      print("Serwer DNS uruchomiony")
    else :
      print("Błąd serwera DNS")
except:
    pass



#skan urzadzeń 1-wire
roms = ds.scan()
print('Znaleziono urządzenie 1-wire: ', roms)

#ustawienie rozdzielczości czujnika temp na 12 bit 
if roms:
    ds.write_scratch(roms[0], b'\x00\x00\x7f')



#konfiguracja RTC
rtc.datetime((2014, 5, 1, 4, 0, 0, 0, 0))



#nasłuchiwanie na porcie 80 
s.bind(("0.0.0.0","80"))
s.listen(3)




####################     DEFINICJE FUNKCJI     ####################


#FUNKCJA WYSZUKUJĄCA CZUJNIKI TEMPERATURY (zwraca listę z adresami czujników 1-wire)========
def ZnajdzCzujniki():
    global ds_ok
    
    #skan lini 1-wire
    roms = ds.scan()
    
    if roms: 
        ds_ok = True
    else:
        ds_ok = False

    return roms
    


#FUNKCJA MIERZĄCA TEMPERATURĘ (zwraca temperature z czujnika)===============================
def ZmierzTemperature(rom):
    global ds_ok
    
    try:
        #rozkaz wykonania pomiaru temperatury
        ds.convert_temp()
        
        #oczekiwanie na pomiar 1s + sygnalizacja LED
        led.value(1)
        sleep(0.5)
        led.value(0)
        sleep(0.5)
        
        #odczytanie i zaokrąglenie temperatury
        temp = round(ds.read_temp(rom[0]), 1)

        return temp
    except:
         ds_ok = False
         return 0
    
    
       
#FUNKCJA POBIERAJĄCA I KONWERTUJĄCA CZAS 3>03 (zwraca czas w odpowiednim formacie)==========
def PobierzGodzine():
    #pobiera godzinę z RTC
    hours = rtc.datetime()[4]
    minutes = rtc.datetime()[5]
    seconds = rtc.datetime()[6]
    
    
    #dopisz '0' gdy <10
    if hours < 10:
        hours = "0" + str(hours)
    else:
        hours = str(hours)
        
    
    #dopisz '0' gdy <10
    if minutes < 10:
        minutes = "0" + str(minutes)
    else:
        minutes = str(minutes)
        
    
    #dopisz '0' gdy <10
    if seconds < 10:
        seconds = "0" + str(seconds)
    else:
        seconds = str(seconds)
        
    #godzina     
    time = hours + ":" + minutes + ":" + seconds
    
    return time
 

    
#FUNKCJA PRZYGOTOWYWUJĄCA DANE DO WYSŁANIA (zwraca wiadomość gotową do wysłania)============
def PrzygotujWiadomosc(temp, time):
    
    #jeżeli pomiar się wykonał - czujnik temperatury jest podłączony
    if ds_ok == True:
        
        #przygotowanie wiadomości (OK)
        msg = time + "Temperatura:" + str(temp)
        
        led.value(0)
 
    else:
        #przygotowanie wiadomości (NIE OK)
        #informacja o braku czujnika temperatury
        msg = time + msg_ds_error
        
        led.value(1)
         
    return msg


###################################################################







#---------------------------   GŁÓWNA PĘTLA PROGRAMU   ---------------------------
while True:
    #zmienna na zapytanie z urządzenia
    request = ""
    
    #jeżeli urządzenie Wi-Fi podłączone 
    if ap.isconnected() == True:
        
        try:
            #połączenie przychodzące
            conn, addr = s.accept()
            
            print("Nawiązano połączenie z " + str(addr))
            
            #odebranie danych i potwierdzenie
            request = conn.recv(1024)
            conn.sendall('HTTP/1.1 200 OK\nConnection: close\nServer: nanoWiPy\nContent-Type: text/html\n\n')
        except:
            pass
        
        #konwersja treści zapytania na string
        request = str(request)
        
        #jeżeli odebrano żądanie wysłania temperatury
        if(request.find("getTemp") > 0):
            
            #wykrycie czujników temperatury - pobranie adresów
            ds_rom = ZnajdzCzujniki()
            #zmierzenie temperatury
            ds_temp = ZmierzTemperature(ds_rom)
            #pobranie czasu
            time = PobierzGodzine()
            
            #przygotowanie wiadomości do wysłania
            ready_msg = PrzygotujWiadomosc(ds_temp, time)
            
            print(ready_msg)
            
            
            try:
                #wyślij wiadomość
                conn.send(ready_msg)
            except:
                pass
        
        #jeżeli łączy pierwszy raz
        else:
            try:
                #załaduj z pliku i wyślij html
                with open('index.html', 'r') as html:
                    conn.send(html.read())
            except:
                pass
        
        
        
        #zakończenie i zamknięcie połączenia
        try:
            conn.sendall('\n')
        except:
            pass
        conn.close()
        print("Zamknięto połączenie z " + str(addr))
        print("")
        
        
        
    #jeżeli urządzenie Wi-Fi odłączone
    else:
        print("Oczekiwanie na podłączenie urządzenia Wi-Fi")
        
        #czekaj na ponowne podłączenie urządzenia Wi-Fi
        while ap.isconnected() == False:
            led.value(1)
            sleep(0.2)
            led.value(0)
            sleep(0.2)
            print(".", end =" ")
            
        print("")
        print("Połączenie udane")

        print("AP CONFIG:  ", end =" ")
        print(ap.ifconfig())
        