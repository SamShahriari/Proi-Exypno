# -*- coding: utf-8 -*-
#Importerar viktiga filer för programmet
import time
import RPi.GPIO as GPIO 
import random
import sys
import os
import pygame
reload(sys)
sys.setdefaultencoding('utf-8')
from RPLCD.gpio import CharLCD
with open("fragor.txt", "r") as fragefil: #Här importeras frågefilen
    fragelista = fragefil.readlines()

#Definierar variabler och liknande
print fragelista
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
GPIO.cleanup()
lcd = CharLCD(cols=16, rows=2, pin_rs=37, pin_e=35, pins_data=[33, 31, 29, 23],numbering_mode=GPIO.BOARD, charmap="A00")
GPIO.setup(7, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(11, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(13, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
lcd.clear()
visaTid=True
knapp=True
alarmPa=False
stallAlarm=False
alarmH=int(time.strftime("%H"))
alarmM=int(time.strftime("%M"))
raknareAlarm=0
alarmRinger=False
forstaAlarm=True
a=0
b=0
c=0
svar=0
svarAnvandare=0
#Definierar specialkaraktärer
ae = (
    0b01010,
    0b00000,
    0b01110,
    0b00001,
    0b01111,
    0b10001,
    0b01111,
    0b00000
)

ao = (
    0b00100,
    0b00000,
    0b01110,
    0b00001,
    0b01111,
    0b10001,
    0b01111,
    0b00000
)

oe = (
    0b01010,
    0b00000,
    0b01110,
    0b10001,
    0b10001,
    0b10001,
    0b01110,
    0b00000
)
logga = (
    0b01010,
    0b01110,
    0b00100,
    0b01110,
    0b11111,
    0b11111,
    0b01010,
    0b11011
)
lcd.create_char(0, ao)
lcd.create_char(1, ae)
lcd.create_char(2, oe)
lcd.create_char(3, logga)

#Omvandlar dagar till svenska
if  time.strftime("%a") == "Mon":
    dag = "M"+unichr(0)+"n"
elif time.strftime("%a") == "Tue":
    dag = "Tis"
elif time.strftime("%a") == "Wed":
    dag = "Ons"
elif time.strftime("%a") == "Thu":
    dag = "Tors"
elif time.strftime("%a") == "Fri":
    dag = "Fre"
elif time.strftime("%a") == "Sat":
    dag = "L%sr" %(unichr(2))
elif time.strftime("%a") == "Sun":
    dag = "S%sn" %(unichr(2))



#Omvandlar månader till svenska
if  time.strftime("%b") == "May":
    man = "maj"
elif time.strftime("%b") == "Oct":
    man = "okt"
else:
    man = time.strftime("%b")





def tidsvisning():
    lcd.cursor_mode="hide"
    lcd.clear()
    lcd.cursor_pos = (0,0)
    lcd.write_string("Klockan %sr %s" %(unichr(1), time.strftime("%H:%M")))
    lcd.cursor_pos = (1, 0)
    lcd.write_string(dag + "%s" %time.strftime(" %d ")+ man.lower() )
    if (alarmPa):
        lcd.cursor_pos=(1,15)
        lcd.write_string(unichr(3))
    time.sleep(.7)
def alarmvisning():
    lcd.clear()
    lcd.cursor_pos = (0,0)
    lcd.write_string("St%sll in alarmet:" %unichr(1))
    lcd.cursor_pos = (1,0)
    lcd.write_string( str(alarmH) + ":" + str(alarmM))
    lcd.cursor_mode = "line"
    if (raknareAlarm==0): lcd.cursor_pos = (1,len(str(alarmH))-1)
    if (raknareAlarm==1): lcd.cursor_pos = (1, len(str(alarmH))+len(str(alarmM)))


def fragevisning():
    lcd.clear()
    lcd.cursor_pos=(0,0)
    if (slumpAlarmtyp>4):
        lcd.write_string(str(a)+"*"+str(b)+"+"+str(c)+"\n\r"+str(svarAnvandare))
    else:
        string =fragelista[2*a]
        if (len(string)>16): #För frågor som är längre än 16 tecken rullar texten
            for x in range(len(string)-16):
                lcd.cursor_pos=(0,0)
                lcd.write_string(string[x:x+16])
                time.sleep(.5)
        else:
            lcd.write_string(string)
        lcd.cursor_pos=(1,0)
        lcd.write_string("S:+ F:- >:Igen")
        print(str(a))
        print(fragelista[2*a])
        print(fragelista[2*a+1])


tidsvisning()

while True:
    if (visaTid and time.strftime("%S")=="00" and alarmRinger == False): #vid varje minutövergång uppdateras displayen 
        tidsvisning()
        print("tid visad")

    if (GPIO.input(7) == GPIO.HIGH and stallAlarm == False and alarmRinger == False): #initierar alarminställning
        visaTid=False
        stallAlarm=True
        time.sleep(.7)
        alarmvisning()
        print("alarm")

    if (GPIO.input(11) == GPIO.HIGH and visaTid and alarmRinger == False): #sätta på alarm
        alarmPa=False
        tidsvisning()

    if (GPIO.input(13) == GPIO.HIGH and visaTid and alarmRinger == False): #stänga av alarm
        alarmPa=True
        tidsvisning()
        print("Alarm pa")



    #Alarminställning
    while (stallAlarm):
        if (GPIO.input(11) == GPIO.HIGH and alarmH > 0 and raknareAlarm==0):
            alarmH-=1
            alarmvisning()
            time.sleep(.7)

        if (GPIO.input(13) == GPIO.HIGH and alarmH<23 and raknareAlarm==0):
            alarmH+=1
            alarmvisning()
            time.sleep(.7)

        if (GPIO.input(11) == GPIO.HIGH and alarmM > 0 and raknareAlarm==1):
            alarmM-=5
            alarmvisning()
            time.sleep(.7)

        if (GPIO.input(13) == GPIO.HIGH and alarmM < 55 and raknareAlarm==1):
            alarmM+=5
            alarmvisning()
            time.sleep(.7)
            print("+")

        if (GPIO.input(7)==GPIO.HIGH):
            raknareAlarm+=1
            alarmvisning()
            time.sleep(.7)

        if (raknareAlarm==2):
            raknareAlarm=0
            alarmPa=True
            tidsvisning()
            visaTid=True
            stallAlarm=False

    if (int(time.strftime("%H"))== alarmH and int(time.strftime("%M"))== alarmM and alarmPa):
        alarmRinger=True
        print("RING, RING!")
        pygame.mixer.init()
        pygame.mixer.music.load("/home/pi/Klocka/Godmorgon.mp3")
        pygame.mixer.music.play(-1)

    while alarmRinger:
        if (forstaAlarm):
            slumpAlarmtyp=random.randint(0,12) #Slumpar ifall det ska vara S/F eller matteproblem
            if(slumpAlarmtyp>4): #slmpar siffror för matteproblem
                a= random.randint(0,12)
                b= random.randint(0,12)
                c=random.randint(0,50)
                svar= a*b+c
                svarAnvandare= svar + random.randint(-30,30)
                lcd.cursor_mode = "blink"
            else:
                a=random.randint(0, len(fragelista)/2-1) #slumpar frågan
            fragevisning()
            forstaAlarm=False
        while(slumpAlarmtyp>4):
            if (GPIO.input(13) == GPIO.HIGH):
                svarAnvandare+=1
                fragevisning()
                time.sleep(.3)
            if (GPIO.input(11) == GPIO.HIGH):
                svarAnvandare-=1
                fragevisning()
                time.sleep(.3)
            if (GPIO.input(7)==GPIO.HIGH):
                if (svar==svarAnvandare):
                    lcd.clear()
                    lcd.cursor_pos=(0,0)
                    pygame.mixer.quit()
                    lcd.write_string("God morgon!")
                    time.sleep(2)
                    alarmPa=False
                    tidsvisning()
                    forstaAlarm=True
                    alarmRinger=False
                    print("gheoa")
                    break
                else:
                    lcd.clear()
                    lcd.write_string("Fel svar!")
                    time.sleep(2)
                    fragevisning()
        while (slumpAlarmtyp<=4):
            if (GPIO.input(13) == GPIO.HIGH):
                if ("1\n"==str(fragelista[2*a+1])): 
                    lcd.clear()
                    lcd.cursor_pos=(0,0)
                    pygame.mixer.quit()
                    lcd.write_string("God morgon!")
                    time.sleep(2)
                    alarmPa=False
                    tidsvisning()
                    forstaAlarm=True
                    alarmRinger=False
                    print("gheoa")
                    break
                else:
                    lcd.clear()
                    lcd.write_string("Fel svar!")
                    time.sleep(2)
                    forstaAlarm=True
                    break
            if (GPIO.input(11) == GPIO.HIGH):
                if ("0\n"==str(fragelista[2*a+1])):
                    lcd.clear()
                    lcd.cursor_pos=(0,0)
                    pygame.mixer.quit()
                    lcd.write_string("God morgon!")
                    time.sleep(2)
                    alarmPa=False
                    tidsvisning()
                    forstaAlarm=True
                    alarmRinger=False
                    print("gheoa")
                    break
                else:
                    lcd.clear()
                    lcd.write_string("Fel svar!")
                    time.sleep(2)
                    forstaAlarm=True
                    break
            if (GPIO.input(7) == GPIO.HIGH): #upprepar frågan
                fragevisning()


