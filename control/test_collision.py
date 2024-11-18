import RPi.GPIO as GPIO
import time

# Set up the GPIO
collision_pin = 26  # Use the collision pin
GPIO.setmode(GPIO.BCM)
GPIO.setup(collision_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

try:
    while True:
        pin_state = GPIO.input(collision_pin)
        if pin_state == GPIO.LOW:
            print("Collision detected!")
        else:
            print("No collision detected.")
        time.sleep(0.5)
except KeyboardInterrupt:
    print("Exiting...")
finally:
    GPIO.cleanup()