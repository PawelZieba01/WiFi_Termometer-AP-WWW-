import machine
from machine import Pin


from time import sleep

import network

import socket

import uasyncio


########################
def blink(i):
    for k in range(i):
        led.value(1)
        sleep(0.1)
        led.value(0)
        sleep(0.1)
########################
        
        

#konfiguracja LAN
ssid = "bestconnect.pl 130"
password = "pawel130"
static_ip = "192.168.1.41"
mask_ip = "255.255.255.0"
gate_ip = "192.168.1.1"




#utworzenie socketu do komunikacji 
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#WLAN
sta_if = network.WLAN(network.STA_IF)


#inicjalizacja pinu LED
led = Pin(2, Pin.OUT)



#inicjalizacja WLAN
sta_if.active(True)
sta_if.ifconfig((static_ip, mask_ip, gate_ip, "8.8.8.8"))
sta_if.connect(ssid, password)




#oczekiwanie na podłączenie urządzenia Wi-Fi
print("Oczekiwanie na podłączenie urządzenia Wi-Fi")
while sta_if.isconnected() == False:
    led.value(1)
    sleep(0.2)
    led.value(0)
    sleep(0.2)
    print(".", end =" ")
    
print("")
print("Połączenie udane")
print("sta CONFIG:  ", end =" ")
print(sta_if.ifconfig())



#sygnalizacja podłączenia irządzenia Wi-Fi - LED
blink(5)





#nasłuchiwanie na porcie 80 
#s.bind(("0.0.0.0","80"))
#s.listen(3)




####################     DEFINICJE FUNKCJI     ####################


###################################################################


#---------------------------   GŁÓWNA PĘTLA PROGRAMU   ---------------------------
while True:
    pass

        