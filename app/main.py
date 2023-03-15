import time
import random
import rp2
import network
import ubinascii
import urequests as requests
import socket
import re
from machine import I2C, Pin, Timer, WDT

import mlx90614

VERSION = 1.31

LOCAL_MODE = False
WITH_HTTP_LOGGING = True

CLOUDS_CLEAR_THRESHOLD = -20

LOOP_SLEEP_SECONDS = 2

sensor = None
led = machine.Pin('LED', machine.Pin.OUT)

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
def blink_onboard_led(num_blinks, led_pin, blink_ms = 200):
    for i in range(num_blinks):
        led_pin.on()
        time.sleep_ms(blink_ms)
        led_pin.off()
        time.sleep_ms(blink_ms)

def logHttp(ambient_temp, sky_temp, diff):
    try:
        # r = requests.get(url='http://192.168.2.214:8855/?ambient_temp=' + str(ambient_temp) + "&sky_temp=" + str(sky_temp) + "&diff=" + str(diff))
        r = requests.get(url='http://astrokanciapa.pl:8321/astroclouds?version=' + str(VERSION) + '&ambient_temp=' + str(ambient_temp) + "&sky_temp=" + str(sky_temp) + "&diff=" + str(diff))
        r.close()
    except:
        print("Can't send data to server...")

import pinrelay
noCloudsSignal = pinrelay.PinRelay(2)
ackLed = pinrelay.PinRelay(3)
noCloudsLed = pinrelay.PinRelay(4)
cloudsLed = pinrelay.PinRelay(5)

blink_onboard_led(6, led, blink_ms=75)
time.sleep(2)


wdt = WDT(timeout=7000)
while True:
    blink_onboard_led(1, ackLed, blink_ms=50)
    blink_onboard_led(1, led, blink_ms=50)
    
    ambient_temp = random.randint(-20, 45) if LOCAL_MODE else round(sensor.read_ambient_temp(), 2)
    time.sleep_ms(100)
    
    sky_temp = random.randint(-40, 45) if LOCAL_MODE else round(sensor.read_object_temp(), 2)
    time.sleep_ms(100)

    diff = sky_temp - ambient_temp
    print("Sky: {}, Ambient: {}, Diff:{}".format(sky_temp, ambient_temp, diff))
    
    if WITH_HTTP_LOGGING:
        logHttp(ambient_temp, sky_temp, diff)
    
    if diff < CLOUDS_CLEAR_THRESHOLD:
        # clear
        noCloudsSignal.on()
        noCloudsLed.on()
        cloudsLed.off()
    else:
        # full clouds
        noCloudsSignal.off()
        noCloudsLed.off()
        cloudsLed.on()
    
    wdt.feed()

    time.sleep(LOOP_SLEEP_SECONDS)
