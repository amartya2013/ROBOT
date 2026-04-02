import RPi.GPIO as GPIO
import time

# Use BCM pin numbering
GPIO.setmode(GPIO.BCM)
SOUND_PIN = 15 # Match your physical wiring (e.g., Pin 7 is GPIO 4)

# Set pin as input with a pull-down resistor
GPIO.setup(SOUND_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

try:
    print("Listening for sound...")
    while True:
        if GPIO.input(SOUND_PIN):
            print("Sound Detected!")
            time.sleep(0.1) # Debounce delay
        time.sleep(0.01)
except KeyboardInterrupt:
    GPIO.cleanup()
