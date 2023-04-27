import time
import random
import rp2
import network
import ubinascii
import urequests as requests
import socket
import re
from machine import I2C, Pin, Timer, WDT
import pinrelay
import mlx90614

VERSION = 1.33

LOCAL_MODE = False
WITH_HTTP_LOGGING = True
LOOP_SLEEP_SECONDS = 2

FIRST_SKY_READING_DELAY_S = 5
CLOSING_ROOF_INTERVAL_S = 10
CLEAR_SKY_DIFF_C = 15
LOG_HTTP_EACH = 15
logHttpEach = 0

sensor = None
onboardLed = machine.Pin('LED', machine.Pin.OUT)
ackLed = pinrelay.PinRelay(2)
cloudsSignal = pinrelay.PinRelay(4)
cloudsLed = pinrelay.PinRelay(3)

currentState = "CLOSED"

if not LOCAL_MODE:
    sda=machine.Pin(0)
    scl=machine.Pin(1)
    i2c = I2C(id=0, sda = sda, scl = scl, freq=100000)
    devices = i2c.scan()
    
    #I2C_MLX90614 = 0x5a
    sensor = mlx90614.MLX90614(i2c)

    if len(devices) == 0:
      print("No i2c device !")
    else:
      print('i2c devices found:',len(devices))

      for device in devices:
        print("Decimal address: ",device," | Hexa address: ",hex(device))

time.sleep_ms(500)

# Define blinking function for onboard LED to indicate error codes
def blink_led(num_blinks, led_pin, blink_ms = 200):
    for i in range(num_blinks):
        led_pin.on()
        time.sleep_ms(blink_ms)
        led_pin.off()
        time.sleep_ms(blink_ms)

def logHttp(ambient_temp, sky_temp, diff, isCloudy, isRoofOpened):
    try:
        # r = requests.get(url='http://192.168.2.214:8855/?ambient_temp=' + str(ambient_temp) + "&sky_temp=" + str(sky_temp) + "&diff=" + str(diff))
        r = requests.get(url='http://astrokanciapa.pl:8321/astroclouds?version=' + str(VERSION) + '&ambient_temp=' + str(ambient_temp) + "&sky_temp=" + str(sky_temp) + "&diff=" + str(diff) + "&isCloudy=" + str(isCloudy) + "&isRoofOpened=" + str(isRoofOpened))
        r.close()
    except:
        print("Can't send data to server...")

def isRoofOpened():
    # TODO: Read input from switch.
    return LOCAL_MODE or False;

def readMlxCheckClouds():
    ambient_temp = random.randint(-20, 45) if LOCAL_MODE else round(sensor.read_ambient_temp(), 2)
    time.sleep_ms(100)
    sky_temp = random.randint(-40, 45) if LOCAL_MODE else round(sensor.read_object_temp(), 2)
    time.sleep_ms(100)

    diff = round(ambient_temp - sky_temp, 1)
    isCloudy = diff < CLEAR_SKY_DIFF_C

    if WITH_HTTP_LOGGING:
        global logHttpEach
        logHttpEach = logHttpEach - 1

        if logHttpEach <= 0:
            logHttpEach = LOG_HTTP_EACH
            logHttp(ambient_temp, sky_temp, diff, isCloudy, isRoofOpened())
    
    global currentState
    print("Current state: {}, Sky: {}, Ambient: {}, Diff:{}, isCloudy:{}, isRoofOpened:{}".format(currentState, sky_temp, ambient_temp, diff, isCloudy, isRoofOpened()))
    
    return isCloudy

def initiateRoofClosing():
    print("Relay HIGH...")
    cloudsSignal.on()
    time.sleep(4)
    print("Relay LOW...")
    cloudsSignal.off()

blink_led(6, onboardLed, blink_ms=75)
time.sleep(2)

#wdt = WDT(timeout=7000)

while True:
    blink_led(1, ackLed, blink_ms=50)
    blink_led(1, onboardLed, blink_ms=50)

    isCloudy = readMlxCheckClouds()

    if currentState == "CLOSED":
        if isRoofOpened():
            # Wait a bit before first sky readings.
            time.sleep(FIRST_SKY_READING_DELAY_S)
            currentState = "OPENED"
    elif currentState == "OPENED":
        if isCloudy:
            cloudsLed.on()
            initiateRoofClosing()
            # Give some time to close the roof.
            print("Waiting {} seconds for roof to close.".format(CLOSING_ROOF_INTERVAL_S))
            time.sleep(CLOSING_ROOF_INTERVAL_S)
            print("Roof closed!")
            currentState = "CLOSED"
        else:
            cloudsSignal.off()
            cloudsLed.off()

    #wdt.feed()

    time.sleep(LOOP_SLEEP_SECONDS)
