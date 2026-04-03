from gpiozero import Button
from time import sleep

FLAME_PIN = 25

sound_sensor = Button(FLAME_PIN, pull_up=False)

try:
    print("Looking for Flame...")
    while True:
        if sound_sensor.is_pressed:
            print("Flame Detected!")
            sleep(0.1)  # Debounce delay
        sleep(0.01)
except KeyboardInterrupt:
    pass
