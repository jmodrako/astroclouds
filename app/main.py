import time
import random
import rp2
import network
import ubinascii
import urequests as requests
import socket
import re
from machine import I2C, Pin, Timer

import mlx90614

sda=machine.Pin(0)
scl=machine.Pin(1)
i2c = I2C(id=0, sda = sda, scl = scl, freq=100000)
devices = i2c.scan()

if len(devices) == 0:
  print("No i2c device !")
else:
  print('i2c devices found:',len(devices))

  for device in devices:
    print("Decimal address: ",device," | Hexa address: ",hex(device))

time.sleep_ms(500)

#I2C_MLX90614     = 0x5a
sensor = mlx90614.MLX90614(i2c)

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
outRelay = pinrelay.PinRelay(2)

CLOUDS_THRESHOLD = 30

while True:
    amb = sensor.read_ambient_temp()
    time.sleep_ms(100)
    obj = sensor.read_object_temp()
    time.sleep_ms(100)

    diff = obj - amb
    
    time.sleep(1)
    
    if abs(obj) > CLOUDS_THRESHOLD:
        outRelay.on()
    else:
        outRelay.off()
    
    blink_onboard_led(1)
