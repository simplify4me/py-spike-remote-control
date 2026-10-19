from pybricks.pupdevices import Motor
from pybricks.parameters import Port, Direction, Stop
from pybricks.tools import wait

# Standard MicroPython modules for input
from usys import stdin, stdout
from uselect import poll

DEFAULT_ANGLE = 10
DEFAULT_SPEED = 100
NUM_WHEEL_ROTATIONS = 4

Arm_motor = Motor(Port.C, Direction.CLOCKWISE)

back_wheel_motor = Motor(Port.A, Direction.COUNTERCLOCKWISE)
front_wheel_motor = Motor(Port.B, Direction.CLOCKWISE)

keyboard = poll()
keyboard.register(stdin)

angle_to_turn = DEFAULT_ANGLE
speed_to_move = 100

# Signal computer that hub is ready
stdout.buffer.write(b"rdy")

def goleft():
    front_wheel_motor.run_angle(5, angle_to_turn, Stop.HOLD, False)

def goright():
    front_wheel_motor.run_angle(5, -angle_to_turn, Stop.HOLD, False)

def goforward():
    back_wheel_motor.run_target(DEFAULT_SPEED, 360 * NUM_WHEEL_ROTATIONS, then=Stop.NONE, wait=False)

def gobackward():
    back_wheel_motor.run_target(DEFAULT_SPEED, 30 * NUM_WHEEL_ROTATIONS, then=Stop.NONE, wait=False)

def armleft():
    Arm_motor.run_angle(5, angle_to_turn, then=Stop.HOLD, wait=False)

def armright():
    Arm_motor.run_target(-DEFAULT_SPEED, 360 * NUM_WHEEL_ROTATIONS, then=Stop.NONE, wait=False)

def brake():
    back_wheel_motor.brake()


def handleSingleKey(char):
    char = char.strip()
    if char == 'a':
        goleft()
    elif char == 'd':
        goright()
    elif char == 's':
        brake()
    elif char == 'w':
        goforward()
    elif char == 'x':
        gobackward()
    elif char == 'l':
        armleft()
    elif char == 'k':
        armright()

no_key = 1

while True:
    # Read the key pressed
    data = keyboard.poll(1000)

    if data:
        no_key = 1
        char = stdin.read(1)
        print(f"Received serial string: {repr(char)}")
        handleSingleKey(char)
    else:
        if no_key > 100:
            break
        else:
            no_key = no_key+1
