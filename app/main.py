import time
import random
import rp2
import network
import ubinascii
import urequests as requests
import socket
import re
from machine import I2C, Pin, Timer
import random

import mlx90614

LOCAL_MODE = False

CLOUDS_CLEAR_THRESHOLD = 4
CLOUDS_CLOUDY_THRESHOLD = 1

LOOP_SLEEP_SECONDS = 1

sensor = None

if not LOCAL_MODE:
    sda=machine.Pin(0)
    scl=machine.Pin(1)
    i2c = I2C(id=0, sda = sda, scl = scl, freq=100000)
    devices = i2c.scan()
    
    #I2C_MLX90614     = 0x5a
    sensor = mlx90614.MLX90614(i2c)

    if len(devices) == 0:
      print("No i2c device !")
    else:
      print('i2c devices found:',len(devices))

      for device in devices:
        print("Decimal address: ",device," | Hexa address: ",hex(device))

time.sleep_ms(500)

# Define blinking function for onboard LED to indicate error codes    
def blink_onboard_led(num_blinks):
    led = machine.Pin('LED', machine.Pin.OUT)
    for i in range(num_blinks):
        led.on()
        time.sleep(.2)
        led.off()
        time.sleep(.2)

blink_onboard_led(3)

import pinrelay
noCloudsSignal = pinrelay.PinRelay(2)
ackLed = pinrelay.PinRelay(3)
noCloudsLed = pinrelay.PinRelay(4)
cloudsLed = pinrelay.PinRelay(5)

while True:
    ackLed.toggle()
    blink_onboard_led(1)
    
    ambient_temp = random.randint(-20, 45) if LOCAL_MODE else sensor.read_ambient_temp()
    time.sleep_ms(100)
    
    sky_temp = random.randint(-40, 45) if LOCAL_MODE else sensor.read_object_temp()
    time.sleep_ms(100)

    diff = abs(sky_temp - ambient_temp)
    print(str(diff))
    
    try:
        r = requests.get(url='http://192.168.2.214:8855/?ambient_temp=' + str(ambient_temp) + "&sky_temp=" + str(sky_temp) + "&diff=" + str(diff))
        r.close()
    except:
        print("Can't send data to server...")
    
    if diff > CLOUDS_CLEAR_THRESHOLD:
        # clear
        noCloudsSignal.on()
        noCloudsLed.on()
        cloudsLed.off()
    elif diff > CLOUDS_CLOUDY_THRESHOLD:
        # cloudy
        noCloudsSignal.off()
        noCloudsLed.off()
        cloudsLed.on()
    else:
        # full clouds
        noCloudsSignal.off()
        noCloudsLed.off()
        cloudsLed.on()
    
    time.sleep(LOOP_SLEEP_SECONDS)
