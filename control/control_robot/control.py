import RPi.GPIO as GPIO
import asyncio
import time

HIGH = GPIO.HIGH
LOW = GPIO.LOW


class Motor:

    def __init__(self, name, pwm_pin, enable1_pin, enable2_pin):
        self.name = name
        self.enable1_pin = enable1_pin
        self.enable2_pin = enable2_pin
        self.pwm_pin = pwm_pin

        GPIO.setup(self.enable1_pin, GPIO.OUT)
        GPIO.setup(self.enable2_pin, GPIO.OUT)
        GPIO.setup(self.pwm_pin, GPIO.OUT)

        self.pwm = GPIO.PWM(self.pwm_pin, 0.1)

    async def forward(self, duty_cycle=100, frequency=1000):
        GPIO.output(self.enable1_pin, HIGH)
        GPIO.output(self.enable2_pin, LOW)
        self.pwm.start(duty_cycle)

    async def backward(self, duty_cycle=100, frequency=1000):
        GPIO.output(self.enable2_pin, HIGH)
        GPIO.output(self.enable1_pin, LOW)
        self.pwm.start(duty_cycle)

    async def stop(self):
        GPIO.output(self.enable1_pin, LOW)
        GPIO.output(self.enable2_pin, LOW)
        self.pwm.stop()


class LawnRobot:

    def __init__(self, collision_pins, verbose=0):

        self.left_motor = Motor('left', 12, 23, 24)
        self.right_motor = Motor('right', 13, 6, 5)
        self.cutter_motor = Motor('cutter', 17, 27, 22)

        self.collision_pins = collision_pins
        for pin in collision_pins:
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        self.collision_handling_task = None
        self.verbose = verbose

    async def forward(self, duty_cycle=100, frequency=1000):
        await asyncio.gather(
            self.left_motor.forward(duty_cycle=duty_cycle, frequency=frequency),
            self.right_motor.forward(duty_cycle=duty_cycle, frequency=frequency)
        )
        if self.verbose:
            print('Moving forward...')

    async def backward(self, duration=0, duty_cycle=100, frequency=1000):
        await asyncio.gather(
            self.left_motor.backward(duty_cycle=duty_cycle, frequency=frequency),
            self.right_motor.backward(duty_cycle=duty_cycle, frequency=frequency)
        )
        if self.verbose:
            print('Moving backward...')
        await asyncio.sleep(duration)
        await self.stop_movement()

    async def rotate_right(self, duration=0):
        try:
            await asyncio.gather(
                self.left_motor.forward(duty_cycle=50, frequency=1000),
                self.right_motor.backward(duty_cycle=50, frequency=1000)
            )
            if self.verbose:
                print('Turning right...')
            await asyncio.sleep(duration)
        except asyncio.CancelledError:
            if self.verbose:
                print('Rotation interrupted, stopping...')
            raise
        finally:
            await self.stop_movement()

    async def rotate_left(self, duration=0):
        try:
            await asyncio.gather(
                self.left_motor.backward(duty_cycle=50, frequency=1000),
                self.right_motor.forward(duty_cycle=50, frequency=1000)
            )
            if self.verbose:
                print('Turning right...')
            await asyncio.sleep(duration)
        except asyncio.CancelledError:
            if self.verbose:
                print('Rotation interrupted, stopping...')
            raise
        finally:
            await self.stop_movement()

    async def cut(self):
        await self.cutter_motor.forward(duty_cycle=100, frequency=1000)
        if self.verbose:
            print('Cutting...')

    async def stop_movement(self):
        await asyncio.gather(
            self.left_motor.stop(),
            self.right_motor.stop()
        )
        if self.verbose:
            print('Stopped movement.')

    async def stop_cut(self):
        await self.cutter_motor.stop()
        if self.verbose:
            print('Stopped cutting.')

    async def handle_collision(self):
        if self.collision_handling_task:
            self.collision_handling_task.cancel()
            await self.collision_handling_task  # Ensure previous task finishes

        async def collision_motion():
            try:
                await self.stop_movement()
                await asyncio.sleep(1.5)
                await self.backward(duration=4, duty_cycle=50, frequency=1000)
                await asyncio.sleep(1.5)
                await self.rotate_right(duration=2.5)
                await asyncio.sleep(1.5)
                await self.forward(duty_cycle=100, frequency=1000)
            except asyncio.CancelledError:
                await self.stop_movement()  # Ensure movement stops if canceled
                raise

        self.collision_handling_task = asyncio.create_task(collision_motion())
        await self.collision_handling_task

    async def collision_detection(self):
        try:
            while True:
                if any(GPIO.input(pin) == LOW for pin in self.collision_pins):
                    await self.handle_collision()
                    print('Found collision')
                await asyncio.sleep(0.1)
        except asyncio.CancelledError:
            if self.verbose:
                print("Collision detection task canceled.")
            raise

    async def STOP(self):
        await asyncio.gather(
            self.left_motor.stop(),
            self.right_motor.stop(),
            self.cutter_motor.stop()
        )
        if self.verbose:
            print('STOPPED')
