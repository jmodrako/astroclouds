import gc
import machine
import network
import time
from machine import Pin

ackLed = machine.Pin('LED', machine.Pin.OUT)

def connect_wlan(ssid, password):
    """Connects build-in WLAN interface to the network.
    Args:
        ssid: Service name of Wi-Fi network.
        password: Password for that Wi-Fi network.
    Returns:
        True for success, Exception otherwise.
    """
    sta_if = network.WLAN(network.STA_IF)
    ap_if = network.WLAN(network.AP_IF)
    sta_if.active(True)
    ap_if.active(False)

    if not sta_if.isconnected():
        print("Connecting to WLAN ({})...".format(ssid))
        sta_if.active(True)
        sta_if.connect(ssid, password)
        while not sta_if.isconnected():
            pass

    return True

# Define blinking function for onboard LED to indicate error codes
def blink_onboard_led(num_blinks, led_pin, blink_ms = 200):
    for i in range(num_blinks):
        led_pin.on()
        time.sleep_ms(blink_ms)
        led_pin.off()
        time.sleep_ms(blink_ms)

def main():
    """Main function. Runs after board boot, before main.py
    Connects to Wi-Fi and checks for latest OTA version.
    """

    gc.collect()
    gc.enable()

    # Wi-Fi credentials
    import secrets
    SSID = secrets.ssid
    PASSWORD = secrets.password

    connect_wlan(SSID, PASSWORD)

    import senko
    OTA = senko.Senko(user="jmodrako", repo="astroclouds", branch="test", gh_token=secrets.gh_token)
    if OTA.update():
        blink_onboard_led(5, ackLed, 25)
        blink_onboard_led(5, ackLed, 100)
        print("Updated to the latest version! Rebooting...")
        machine.reset()
    else:
        blink_onboard_led(5, ackLed, 25)
        blink_onboard_led(5, ackLed, 100)
        blink_onboard_led(5, ackLed, 25)
        blink_onboard_led(5, ackLed, 100)
        print("Up to date!")

if __name__ == "__main__":
    main()
