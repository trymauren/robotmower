import RPi.GPIO as GPIO
import asyncio
import random
from unittest.mock import patch
import control_robot.control as control

HIGH = GPIO.HIGH
LOW = GPIO.LOW


async def test_loop(robot):
    collision_task = asyncio.create_task(robot.collision_detection())

    try:
        await robot.cut()
        await robot.forward(duty_cycle=100, frequency=1000)
        await asyncio.sleep(5)  # Run for 5 seconds to observe behavior
    except asyncio.CancelledError:
        print("Test loop was cancelled.")
    finally:
        await robot.stop_movement()
        await robot.stop_cut()
        collision_task.cancel()
        await collision_task


# Mock GPIO input for testing
def mock_gpio_input(pin):
    return HIGH if random.random() < 0.1 else LOW


if __name__ == '__main__':
    GPIO.setmode(GPIO.BCM)
    collision_pins = [2, 3, 4]
    for pin in collision_pins:
        GPIO.setup(pin, GPIO.IN)

    robot = control.LawnRobot(collision_pins, verbose=1)

    with patch('RPi.GPIO.input', new=mock_gpio_input):
        try:
            asyncio.run(test_loop(robot))
        except asyncio.CancelledError:
            print("Program terminated.")
        finally:
            GPIO.cleanup()
