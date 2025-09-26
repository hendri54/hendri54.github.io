from hub import light_matrix, port, motion_sensor
from math import atan2, degrees, sqrt
import runloop, motor, motor_pair, sys, time, color_sensor


# -------------------  Constants

LEFT = -1
RIGHT = 1
BLACK = 11
WHITE = 12

DRIVE_MOTORS = motor_pair.PAIR_1
LEFT_MOTOR = port.A
RIGHT_MOTOR = port.E
# Max speed of hardware motor (large)
MAX_DRIVE_SPEED = 1050

ARM_MOTOR = port.D
# Arm gear ratio. Each rotation of the motor raises arm by this many degrees
ARM_GEAR_RATIO = 2
# Max arm position in degrees
MAX_ARM_POS = 180
MAX_ARM_SPEED = 1100  # medium motor

LTSENSOR_LEFT = port.C
LTSENSOR_RIGHT = port.F
CM_PER_ROTATION = 17.5

# Keep track of (x,y) position on the table
XPOS = 0.0
YPOS = 0.0


# ---------------------  Helpers

def color_name(bw):
    if bw == BLACK:
        return "Black"
    elif bw == WHITE:
        return "White"
    else:
        raise ValueError("Invalid bw: " + str(bw))


def side_name(lr):
    if lr == LEFT:
        return "Left"
    elif lr == RIGHT:
        return "Right"
    else:
        raise ValueError("Invalid lr: " + str(lr))


def other_side(lr):
    if lr == LEFT:
        return RIGHT
    elif lr == RIGHT:
        return LEFT
    else:
        raise ValueError("Invalid lr: " + str(lr))



# -----------------------  Moving helpers

def vector_length(dx, dy):
    return sqrt(dx*dx + dy*dy)

def cm_to_degrees(distance_cm):
    # Add multiplier for gear ratio if needed
    return round((distance_cm/CM_PER_ROTATION) * 360)

def degrees_to_cm(deg1):
    return (deg1/360) * CM_PER_ROTATION


# Speeds are always in percentage points.
def valid_speed(pct):
    return 0 <= pct <= 100

# Convert speed in percent to motor speed
# Returns `int` because that's what motors expect.
def pct_to_motor_speed(pct):
    assert valid_speed(pct)
    return round((pct / 100) * MAX_DRIVE_SPEED)

def pct_to_arm_speed(pct):
    assert valid_speed(pct)
    return round((pct / 100) * MAX_ARM_SPEED)

def test_moving_helpers():
    print("Test moving helpers")
    assert abs(degrees_to_cm(360) - CM_PER_ROTATION) < 0.1, "Expecting 360"
    d1 = degrees_to_cm(12)
    cm1 = cm_to_degrees(d1)
    assert (cm1 == 12), "Expecting 12. Getting " + str(cm1)
    speed = pct_to_motor_speed(50)
    assert abs(speed - 0.5 * MAX_DRIVE_SPEED) < 0.1
    print("  Passed")




# ----------  Turn angles

# Right turn angle in (0, 360) from a1 to a2
def turn_angle_right(a1, a2):
    if a2 > a1:
        return a2 - a1
    elif a2 == a1:
        return 0
    else:
        return 360 - a1 + a2

def test_turn_angle_right():
    print('Testing turn angle right')
    assert(turn_angle_right(10, 30) == 20)
    assert(turn_angle_right(30, 10) == 340)
    assert(turn_angle_right(30, 0) == 330)
    assert(turn_angle_right(359, 2) == 3)
    assert(turn_angle_right(2, 1) == 359)
    assert(turn_angle_right(0, 0) == 0)
    print('  Passed')


def turn_angle_left(a1, a2):
    if a1 > a2:
        return a1 - a2
    elif a1 == a2:
        return 0
    else:
        return 360 - a2 + a1


def test_turn_angle_left():
    print('Testing turn angle left')
    assert(turn_angle_left(30, 10) == 20)
    assert(turn_angle_left(10, 30) == 340)
    assert(turn_angle_left(10, 350) == 20)
    assert(turn_angle_left(30, 0) == 30)
    assert(turn_angle_left(0, 0) == 0)
    assert(turn_angle_left(350, 0) == 350)
    print('  Passed')


def turn_left_or_right(a1, a2):
    aLeft = turn_angle_left(a1, a2)
    aRight = turn_angle_right(a1, a2)
    if aLeft < aRight:
        return LEFT
    else:
        return RIGHT

def test_turn_left_or_right():
    print('Test turn left or right')
    assert(turn_left_or_right(10, 20) == RIGHT)
    assert(turn_left_or_right(20, 10) == LEFT)
    assert(turn_left_or_right(330, 20) == RIGHT)
    assert(turn_left_or_right(10, 330) == LEFT)
    assert(turn_left_or_right(10, 0) == LEFT)
    assert(turn_left_or_right(190, 0) == RIGHT)
    print('  Passed')


# If the heading is curDeg degrees and we want to point in the direction of
# tgDeg degrees, how far do we need to turn left (negative) or right (positive)?
def turn_angle_lr(curDeg, tgDeg):
    if abs(curDeg - tgDeg) < 1:
        return 0
    aLeft = turn_angle_left(curDeg, tgDeg)
    aRight = turn_angle_right(curDeg, tgDeg)
    if aLeft < aRight:
        return -aLeft
    else:
        return aRight

def test_turn_angle_lr():
    print("Test turn lr towards degrees")
    assert(turn_angle_lr(0, 10) == 10)
    assert(turn_angle_lr(0, 350) == -10)
    assert(turn_angle_lr(350, 10) == 20)
    assert(turn_angle_lr(10, 350) == -20)
    print("Passed")



# -----------------------------  Vector to angle

# Convert a Vector (dx, dy) into degrees (0 to 360)
# 0 degrees is "straight up" (0, 1)
def vector_to_angle(dx, dy):
    # Use atan2(dx, dy) to make up = 0 degrees
    angle_radians = atan2(dx, dy)
    angle_degrees = degrees(angle_radians)

    # Convert from -180 to 180 range to 0 to 360 range
    if angle_degrees < 0:
        angle_degrees += 360

    return round(angle_degrees)


def test_vector_to_angle():
    print('Test vector to angle')
    assert(vector_to_angle(1, 0) == 90)
    assert(vector_to_angle(0, 1) == 0)
    assert(vector_to_angle(0, -1) == 180)
    assert(vector_to_angle(-1, 0) == 270)
    assert(vector_to_angle(1, 1) == 45)
    assert(vector_to_angle(10, 1) == 84)
    assert(vector_to_angle(-10, -1) == 264)
    print('  Passed')



# -----------------------  Yaw sensor

def check_degrees(deg1):
    return 0 <= deg1 <= 360

def check_yaw(yaw1):
    return -179 <= yaw1 <= 180

# Convert yaw in (-179 to 180) into degrees (0 to 360)
def yaw_to_degrees(yaw1):
    assert check_yaw(yaw1), "Invalid yaw: " + str(yaw1)
    if yaw1 >= 0:
        return yaw1
    else:
        return 360 + yaw1

# The inverse of yaw_to_degrees
def degrees_to_yaw(deg1):
    assert check_degrees(deg1)
    if deg1 <= 180:
        return deg1
    else:
        return deg1 - 360


def test_yaw_to_degrees():
    assert(yaw_to_degrees(0) == 0)
    assert(degrees_to_yaw(0) == 0)
    assert(yaw_to_degrees(-1) == 359)
    assert(degrees_to_yaw(359) == -1)
    assert(yaw_to_degrees(180) == 180)
    assert(degrees_to_yaw(180) == 180)
    assert(yaw_to_degrees(-179) == 181)
    assert(degrees_to_yaw(181) == -179)


# Return yaw in degrees (0 to 360)
def read_yaw():
    yaw1 = round(motion_sensor.tilt_angles()[0] * -0.1)
    # Handles rounding to 180
    if yaw1 == -180:
        yaw1 = -179
    return yaw_to_degrees(yaw1)

# Input is in degrees (0 to 360)
async def reset_yaw(newDeg):
    yaw1 = degrees_to_yaw(newDeg)
    # reset_yaw expects degrees in internal units
    motion_sensor.reset_yaw(yaw1 * -10)
    # It takes time for the yaw to become readable
    await runloop.sleep_ms(500)
    await runloop.until(motion_sensor.stable)
    curYaw = read_yaw()
    assert abs(curYaw - newDeg) < 3, "Yaw not correctly reset. Expecting " + str(newDeg) + "  Actual: " + str(curYaw)


async def test_reset_yaw():
    newYaw = 45
    await reset_yaw(newYaw)
    assert(read_yaw() == newYaw)

async def test_yaw_functions():
    print('Test yaw functions')
    test_yaw_to_degrees()
    await test_reset_yaw()
    print('  Passed')



# ----------------------  Turning

def stop_moving():
    motor_pair.stop(DRIVE_MOTORS)


def prep_turn(speed):
    stop_moving()



# Turn right to deg1 degrees
async def turn_right(deg1, speed = 30):
    prep_turn(speed)
    startDeg = read_yaw()
    if deg1 == startDeg:
        return startDeg

    done = False
    # Already turned past 360?
    if startDeg > deg1:
        past360 = False
    else:
        past360 = True

    motor_pair.move_tank(DRIVE_MOTORS, 100, -100)# how to set velocities? +++
    while not done:
        curDeg = read_yaw()
        if curDeg < startDeg:
            # We passed 360
            past360 = True
        if (curDeg >= deg1 and past360):
            done = True
    stop_moving()
    # Need to give yaw sensor time to be read
    await runloop.sleep_ms(100)
    return read_yaw()


# Turn left to deg1 degrees
async def turn_left(deg1, speed = 30):
    prep_turn(speed)
    startDeg = read_yaw()
    if deg1 == startDeg:
        return startDeg

    done = False
    # Already turned past 360?
    if startDeg < deg1:
        past360 = False
    else:
        past360 = True

    motor_pair.move_tank(motor_pair.PAIR_1, -100, 100)# how to set velocities? +++
    while not done:
        curDeg = read_yaw()
        if curDeg > startDeg:
            # We passed 360
            past360 = True
        if (curDeg <= deg1 and past360):
            done = True
    stop_moving()
    # Need to give yaw sensor time to be read
    await runloop.sleep_ms(100)
    return read_yaw()


# Turn left or right, whichever is shorter
async def turn_to_degrees(deg1):
    stop_moving()
    curDeg = read_yaw()
    if curDeg == deg1:
        return curDeg
    lr = turn_left_or_right(curDeg, deg1)
    if lr == LEFT:
        await turn_left(deg1)
    else:
        await turn_right(deg1)
    return read_yaw()


# Check if robot has turned to near target angle (in degrees)
def check_turn(tg):
    curDeg = read_yaw()
    # Need to use left or right turn angle 
    # b/c of 360 degree rollover
    gap = turn_angle_lr(curDeg, tg)
    if abs(gap) < 5:
        return True
    else:
        print("Turn failed. Tg: " + str(tg) + "  Actual: " + str(curDeg))
        return False


async def test_turning():
    print("Test turning")
    deg1 = await turn_right(60)
    assert check_turn(60)
    # Turn past 360
    deg2 = await turn_right(10)
    assert check_turn(10)
    # Turn to 0
    deg3 = await turn_right(0)
    assert check_turn(0)

    deg1 = await turn_left(350)
    assert check_turn(350)
    deg2 = await turn_left(90)
    assert check_turn(90)

    deg1 = await turn_to_degrees(350)
    assert check_turn(350)
    deg2 = await turn_to_degrees(10)
    assert check_turn(10)
    deg2 = await turn_to_degrees(0)
    assert check_turn(0)
    print("  Passed")


# --------------------  Gyro driving


# While driving, adjust direction to point to `tgDeg`
def adjust_direction(tgDeg, speed):
    curDeg = read_yaw()
    # How far do we need to turn?
    turnAngle = turn_angle_lr(curDeg, tgDeg)
    correction = round(2 * turnAngle)
    correction = min(20, max(correction, -20))
    motor_pair.move(DRIVE_MOTORS, correction, velocity = pct_to_motor_speed(speed))
    time.sleep(0.05)

# Drive straight using gyro in direction `tgDeg`
# at speed `speed`
# for distance `dist` in cm
# for at most `maxTime` seconds
def gyro_straight(tgDeg = 0, speed = 50, dist = 10.0, maxTime = 5):
    assert check_degrees(tgDeg)
    # first turn to tgDeg +++
    # Need to use right motor. The left one runs backwards.
    startDeg = motor.relative_position(RIGHT_MOTOR)
    tgMotorDeg = startDeg + cm_to_degrees(dist)
    done = False
    startTime = time.ticks_ms()
    motor_pair.move(DRIVE_MOTORS, 0, velocity = pct_to_motor_speed(speed))

    while not done:
        adjust_direction(tgDeg, speed)
        if motor.relative_position(RIGHT_MOTOR) >= tgMotorDeg:
            done = True
        if (time.ticks_ms() - startTime) > 1000 * maxTime:
            done = True
    stop_moving()


async def turn_to_xy(x, y):
    global XPOS, YPOS
    dx = x - XPOS
    dy = y - YPOS
    tgDeg = vector_to_angle(dx, dy)
    await turn_to_degrees(tgDeg)
    return tgDeg


# Drive in a straight line to point (x, y)
# Update XPOS and YPOS globals.
async def drive_to_xy(x, y, speed = 50, maxTime = 5):
    global XPOS, YPOS
    tgDeg = await turn_to_xy(x, y)
    dx = x - XPOS
    dy = y - YPOS
    dist = vector_length(dx, dy)
    gyro_straight(tgDeg = tgDeg, speed = speed, dist = dist, maxTime = maxTime)
    XPOS = x
    YPOS = y


# -----------------Line Finding
# White lines are not found reliably. Black lines are.

def light_reflected(lr):
    if lr == LEFT:
        return color_sensor.reflection(LTSENSOR_LEFT)
    elif lr == RIGHT:
        return color_sensor.reflection(LTSENSOR_RIGHT)
    else:
        raise ValueError("lr must be LEFT or RIGHT")

def white_line(lr):
    return light_reflected(lr) > 80

def black_line(lr):
    return light_reflected(lr) < 22

def line_found(lr, bw):
    if bw == BLACK:
        return black_line(lr)
    elif bw == WHITE:
        return white_line(lr)
    else:
        raise ValueError("Invalid bw: " + str(bw))


def print_lines_found():
    for lr in [LEFT, RIGHT]:
        for bw in [BLACK, WHITE]:
            if line_found(lr, bw):
                print("Line found: " + side_name(lr) + " / " + color_name(bw))


# Find a line, either with a given sensor and color.
def line_finder(lr, bw, speed = 20, maxTime = 5, steering = 0):
    if line_found(lr, bw):
        return True
    done = False
    startTime = time.ticks_ms()
    motor_pair.move(DRIVE_MOTORS, steering, velocity = pct_to_motor_speed(speed))
    while not done:
        if line_found(lr, bw):
            done = True
        if time.ticks_ms() - startTime > 1000 * maxTime:
            done = True
    return line_found(lr, bw)


# Align robot on a line. Robot already found the line.
def line_align(bw):
    if line_found(LEFT, bw):
        return line_align_lr(RIGHT, bw)
    elif line_found(RIGHT, bw):
        return line_align_lr(LEFT, bw)
    else:
        print("Cannot align on line. Need to find line first.")


def line_align_lr(lr, bw):
    stop_moving()
    if not line_found(other_side(lr), bw):
        print("Cannot align on line. Need to find line first.")
        return False
    if lr == LEFT:
        # Found right. Need to turn right
        steering = 70
    else:
        steering = -70
    return line_finder(lr, bw, steering = steering)



# ---------------------  Arm movement
# Assumes that clockwise movement raises arm

# Valid arm position (in degrees)?
def valid_arm_pos(deg1):
    return 0 <= deg1 <= 120

def clamp_arm_pos(deg1):
    return min(120, max(0, deg1))

# At startup, the arm is all the way down. We call that zero degrees.
def store_arm_zero_pos():
    motor.reset_relative_position(ARM_MOTOR, 0)

# Convert motor degrees into actual degrees
# Depends on gear ratio
def arm_pos_to_degrees(armPos):
    return round(armPos / ARM_GEAR_RATIO)

def degrees_to_arm_pos(deg):
    return round(ARM_GEAR_RATIO * clamp_arm_pos(deg))

# Get arm position in degrees. 90 = vertically up
def get_arm_pos():
    mDeg = motor.relative_position(ARM_MOTOR)
    return arm_pos_to_degrees(mDeg)

def check_arm_pos(tgDeg):
    deg = get_arm_pos()
    if abs(deg - tgDeg) > 2:
        print("Invalid arm position: Expecting " + str(tgDeg) + "  Actual: " + str(deg))
        return False
    else:
        return True

# Move arm up, unless it is already up
async def arm_up(deg1, speed = 50):
    if get_arm_pos() < deg1:
        armPos = degrees_to_arm_pos(deg1)
        await motor.run_to_relative_position(ARM_MOTOR, armPos, pct_to_arm_speed(speed))

# Move arm down, unless it is already down
async def arm_down(deg1, speed = 50):
    if get_arm_pos() > deg1:
        armPos = degrees_to_arm_pos(deg1)
        await motor.run_to_relative_position(ARM_MOTOR, armPos, pct_to_arm_speed(speed))

async def test_arm_movements():
    print("Testing arm movements")
    mDeg = get_arm_pos()
    assert valid_arm_pos(mDeg)
    await arm_down(1)
    await arm_up(60)
    assert check_arm_pos(60)
    # Not moving up b/c already above
    await arm_up(50)
    assert check_arm_pos(60)
    await arm_down(5)
    assert check_arm_pos(5)
    print("  Passed")



# ----------------------  Testing

# Run all tests. Does not drive the robot, but performs turns and arm 
# movements.
async def test_all():
    test_moving_helpers()
    test_turn_angle_right()
    test_turn_angle_left()
    test_turn_left_or_right()
    test_turn_angle_lr()
    await test_arm_movements()
    test_vector_to_angle()
    await test_yaw_functions()
    await test_turning()


# -------------  Startup

def config_robot():
    motor_pair.pair(DRIVE_MOTORS, LEFT_MOTOR, RIGHT_MOTOR)

async def boot_robot():
    config_robot()
    await reset_yaw(0)
    store_arm_zero_pos()
    print("Boot sequence complete.")



# -----------------------  Runs

async def start_from_right():
    global XPOS, YPOS
    XPOS = 160
    YPOS = 10
    await reset_yaw(0)

async def right_start_to_silo():
    print("Driving: right start to Silo")

async def silo_action():
    print("Silo action")

async def silo_to_balldrop():
    print("Driving Silo to BallDrop")

async def balldrop_action():
    print("Ball drop action")

async def balldrop_to_table():
    print("Driving: BallDrop to Table")

async def table_action():
    print("Table action")


async def run_from_right():
    await start_from_right()
    await right_start_to_silo()
    await silo_action()
    await silo_to_balldrop()
    await balldrop_action()
    await balldrop_to_table()
    await table_action()



# -----------------  Main


async def main():
    global XPOS, YPOS
    await boot_robot()
    await test_all()


    # Not the best way of exiting; raises an error.
    # But avoids having to press stop after each run.
    sys.exit()


runloop.run(main())


