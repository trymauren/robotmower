import RPi.GPIO as GPIO
import asyncio
import control_robot.control as control

HIGH = GPIO.HIGH
LOW = GPIO.LOW


async def test_loop(robot):
    # Start collision detection as a separate task
    collision_task = asyncio.create_task(robot.collision_detection())

    try:
        # Start the cutting motor
        await robot.cut()

        # Start forward movement and keep it going unless a collision occurs
        await robot.forward(duty_cycle=100, frequency=1000)

        # Run indefinitely, allowing the collision detection task to handle events
        await asyncio.sleep(float('inf'))  # This keeps the forward motion running
    except asyncio.CancelledError:
        print("Test loop was cancelled.")
    finally:
        # Stop movement and cutting on exit
        await robot.stop_movement()
        await robot.stop_cut()
        collision_task.cancel()
        await collision_task  # Ensure collision detection task completes


if __name__ == '__main__':
    GPIO.setmode(GPIO.BCM)
    collision_pins = [26]  # Replace with your actual GPIO pins for collision sensors

    robot = control.LawnRobot(collision_pins, verbose=0)

    try:
        asyncio.run(test_loop(robot))
    except asyncio.CancelledError:
        print("Program terminated.")
    finally:
        GPIO.cleanup()