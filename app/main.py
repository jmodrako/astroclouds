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

# Define blinking function for onboard LED to indicate error codes    
def blink_onboard_led(num_blinks):
    led = machine.Pin('LED', machine.Pin.OUT)
    for i in range(num_blinks):
        led.on()
        time.sleep(.2)
        led.off()
        time.sleep(.2)

blink_onboard_led(3)

