from hub import light_matrix, port, motion_sensor
from math import atan2, degrees, sqrt, pi, radians, cos, sin, isclose
import runloop, motor, motor_pair, sys, time, color_sensor

# General notes
#
# The code keeps track of where the robot is at all times.
# The globals (XPOS, YPOS) record the distance from the bottom-left
# corner of the table to the current position in cm.
# Example: Going "east" increases only XPOS. Going "south" decreases only YPOS.
#
# The yaw sensor keeps track of the direction of the robot.
# Yaw = 0 points "north." Yaw = 270 points "west."
# The yaw is never reset to 0. It always points north.
#
# Driving is done to absolute positions. `drive_to_xy` takes as
# arguments an (x, y) target position on the table (in cm).
# It drives to that absolute position from anywhere on the table.
#
# All distances are in cm.
# All angles are in degrees (0 to 360).
# All speeds are in percentages (-100 to 100). Negative values go backwards.
#
# Key functions:
# `gyro_straight` - drive in a straight line in a given direction for a given distance.
# `turn_to_degrees` - turn the robot towards a fixed angle.
# `line_finder` - find a black-and-white line
# `line_align` - align that bot on a line
# `arm_up`, `arm_down` - move arm up / down to a fixed position. 0 is all the way down.
#    180 is vertically up.

# -------------------Constants

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
ARM_GEAR_RATIO = 1.85
# Max arm position in degrees
# Calibrate such that arm is vertical at 180 degrees
MAX_ARM_POS = 220 
MIN_ARM_POS = 0
# medium motor
MAX_ARM_SPEED = 1100

LTSENSOR_LEFT = port.C
LTSENSOR_RIGHT = port.F

# Wheel curcumference
CM_PER_ROTATION = 17.5
# Used for spins without gyro. Width between wheels.
TRACK = 10.2

# XPOS for right start box
RIGHT_START_XPOS = {"xpos": 165, "ypos": 10, "yaw": 0}

# 45 degree black-and-white line in top right corner
TOP_RIGHT_LINE = {"xpos": 165, "ypos": 75, "yaw": 45}

# Silo approach position
SILO = {"xpos": 165, "ypos": 68, "yaw": 90}


# --------------------Globals

# Keep track of (x,y) position on the table
XPOS = 0.0
YPOS = 0.0

# When robot is aligned, e.g. against a wall, do not reset the yaw.
# Resetting may not be reliable and may be slow.
# Instead record by how much the yaw sensor is off. Then always add this
# number to yaw readings.
YAW_DRIFT = 0

# Start time of current run
RUN_START_TIME = 0


# ---------------------Helpers

# Are two tuples approximately equal. 
# Uses abs tolerance by default
def approx_equal(tuple1, tuple2, rel_tol = 1, abs_tol = 1e-4):
    if len(tuple1) != len(tuple2):
        return False
    return all(isclose(a, b, rel_tol=rel_tol, abs_tol=abs_tol)
            for a, b in zip(tuple1, tuple2))

def info_msg(msg):
    print(msg)

def pass_fail_msg(txt, passed):
    info_msg(txt + ":" + ("passed" if passed else "failed"))

def set_run_start_time():
    global RUN_START_TIME
    RUN_START_TIME = time.ticks_ms()

# Time since start of run in seconds
def elapsed_runtime():
    global RUN_START_TIME
    return round((time.ticks_ms() - RUN_START_TIME) / 1000)

def show_elapsed_time():
    info_msg("Time since start: " + str(elapsed_runtime()) + " seconds.")

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



# -----------------------Moving helpers

def get_current_xy():
    global XPOS, YPOS
    return XPOS, YPOS# should copy those +++

# How far do we have to move (dx, dy) to get to (x,y)?
def get_current_dx_dy(x, y):
    xp, yp = get_current_xy()
    return x - xp, y - yp

def update_xy(x, y):
    global XPOS, YPOS
    XPOS = x
    YPOS = y

# Update (x, y) position after driving along vector (dx, dy)
def update_dx_dy(dx, dy):
    global XPOS, YPOS
    XPOS = XPOS + dx
    YPOS = YPOS + dy

# Is the robot close enough to (x,y) that no futher driving
# needed?
def at_xy(x, y):
    dx, dy = get_current_dx_dy(x, y)
    return (abs(dx) < 1) and (abs(dy) < 1)


def vector_length(dx, dy):
    return sqrt(dx*dx + dy*dy)

# Convert distance in cm to motor rotations in degrees
def cm_to_degrees(distance_cm):
    # Add multiplier for gear ratio if needed
    return round((distance_cm/CM_PER_ROTATION) * 360)

# Convert motor rotations to distance
def degrees_to_cm(deg1):
    return (deg1/360) * CM_PER_ROTATION


# Speeds are always in percentage points.
def valid_speed(pct):
    return -100 <= pct <= 100

# Convert speed in percent to motor speed
# Returns `int` because that's what motors expect.
def pct_to_motor_speed(pct):
    assert valid_speed(pct)
    return round((pct / 100) * MAX_DRIVE_SPEED)

def pct_to_arm_speed(pct):
    assert valid_speed(pct)
    return round((pct / 100) * MAX_ARM_SPEED)

# Drive in direction `steering` (-100 to 100) at `speed` (0 to 100)
def drive(steering, speed, acceleration = 300):
    motor_pair.move(DRIVE_MOTORS, steering, velocity = pct_to_motor_speed(speed), acceleration = acceleration)


# Drive straight (no gyro) for a given distance.
# By default: update XPOS, YPOS.
# Returns (dx, dy) of vector driven.
async def drive_distance(dist, speed = 50, updateXY = True):
    yaw0 = read_yaw()
    # if (dist > 10):
    #    # Drive fast for part the distance
    #    dist1 = dist - 5
    deg1 = cm_to_degrees(dist)
    await motor_pair.move_for_degrees(DRIVE_MOTORS, deg1, 0, velocity = pct_to_motor_speed(speed), acceleration = 300, deceleration = 300)
    # # Slower for the rest for smoother stopping
    # deg2 = cm_to_degrees(dist)
    # if speed > 30:
    #    speed2 = speed / 2
    # else:
    #    speed2 = speed
    # await motor_pair.move_for_degrees(DRIVE_MOTORS, deg2, 0, velocity = pct_to_motor_speed(speed2), acceleration = 360, deceleration = 360)

    # Return dx, dy based on distance and yaw
    dx, dy = angle_to_vector(yaw0, dist)
    if updateXY:
        update_dx_dy(dx, dy)
    return dx, dy


def test_moving_helpers():
    print("Test moving helpers")
    assert abs(degrees_to_cm(360) - CM_PER_ROTATION) < 0.1, "Expecting 360"
    d1 = degrees_to_cm(12)
    cm1 = cm_to_degrees(d1)
    assert (cm1 == 12), "Expecting 12. Getting " + str(cm1)
    speed = pct_to_motor_speed(50)
    assert abs(speed - 0.5 * MAX_DRIVE_SPEED) < 0.1
    print("Passed")




# ----------Turn angles

# Scale degrees into (0, 360)
def scale_degrees(a1):
    return a1 % 360


# Add two degree values, correctly handling rollover across 360
# Inputs can be negative. Then they are subtracted.
# Example: `add_degrees(10, -20) == 350`
def add_degrees(a1, a2):
    return (a1 + a2) % 360

# Returns a1 - a2, but taking into account that rollover across 360 degrees may occur.
# Example: `degree_diff(10, 350) == 20`
def degree_diff(a1, a2):
    return turn_angle_left(a1, a2)


def test_add_degrees():
    info_msg("Test add degrees")
    assert add_degrees(50, 200) == 250
    assert add_degrees(260, 200) == 100
    assert add_degrees(50, -60) == 350
    assert add_degrees(50, -20) == 30
    assert add_degrees(359, 0) == 359
    assert add_degrees(359, 1) == 0
    assert add_degrees(359, 2) == 1

    assert degree_diff(60, 20) == 40
    assert degree_diff(10, 350) == 20
    assert degree_diff(350, 10) == 340
    assert degree_diff(30, 30) == 0
    assert degree_diff(360, 0) == 0
    assert degree_diff(0, 360) == 0
    info_msg("Passed")


# Right turn angle in (0, 360) from a1 to a2
def turn_angle_right(a1, a2):
    d1 = scale_degrees(a1)
    d2 = scale_degrees(a2)
    if d2 > d1:
        return d2 - d1
    elif d2 == d1:
        return 0
    else:
        return 360 - d1 + d2

def test_turn_angle_right():
    print('Testing turn angle right')
    assert(turn_angle_right(10, 30) == 20)
    assert(turn_angle_right(30, 10) == 340)
    assert(turn_angle_right(30, 0) == 330)
    assert(turn_angle_right(359, 2) == 3)
    assert(turn_angle_right(2, 1) == 359)
    assert(turn_angle_right(0, 0) == 0)
    print('Passed')


# Left turn angle in (0, 360) from a1 to a2
def turn_angle_left(a1, a2):
    d1 = scale_degrees(a1)
    d2 = scale_degrees(a2)
    if d1 > d2:
        return d1 - d2
    elif d1 == d2:
        return 0
    else:
        return 360 - d2 + d1


def test_turn_angle_left():
    print('Testing turn angle left')
    assert(turn_angle_left(30, 10) == 20)
    assert(turn_angle_left(10, 30) == 340)
    assert(turn_angle_left(10, 350) == 20)
    assert(turn_angle_left(30, 0) == 30)
    assert(turn_angle_left(0, 0) == 0)
    assert(turn_angle_left(350, 0) == 350)
    print('Passed')


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
    print('Passed')


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



# -----------------------------Vector to angle

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


# Convert angle and length to dx and dy components.
# Parameters:
# angle (float): Angle in degrees (0-359), where 0 points up along y-axis
# length (float): Vector length
# Returns:
# tuple: (dx, dy) coordinate distances
def angle_to_vector(deg1, dist):
    # Convert angle to radians and adjust so 0 degrees points up
    angle_rad = radians(deg1 - 90)

    dx = dist * cos(angle_rad)
    dy = -dist * sin(angle_rad)
    return dx, dy    


def test_vector_to_angle():
    print('Test vector to angle')
    assert(vector_to_angle(1, 0) == 90)
    assert(vector_to_angle(0, 1) == 0)
    assert(vector_to_angle(0, -1) == 180)
    assert(vector_to_angle(-1, 0) == 270)
    assert(vector_to_angle(1, 1) == 45)
    assert(vector_to_angle(10, 1) == 84)
    assert(vector_to_angle(-10, -1) == 264)

    assert approx_equal(angle_to_vector(0, 10), (0, 10))    
    assert approx_equal(angle_to_vector(90, 0), (10, 0))
    assert approx_equal(angle_to_vector(180, 10), (0, -10))
    assert approx_equal(angle_to_vector(270, 10), (-10, 0))
    assert approx_equal(angle_to_vector(45, 10), (0, 10))
    print('Passed')



# -----------------------Yaw sensor

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
# By default corrects for current yaw drift. Unless `addDrift = False`
def read_yaw(addDrift = True):
    global YAW_DRIFT
    yaw1 = round(motion_sensor.tilt_angles()[0] * -0.1)
    # Handles rounding to 180
    if yaw1 == -180:
        yaw1 = -179
    # Convert into degrees (0 to 360)
    yawDeg = yaw_to_degrees(yaw1)
    if addDrift:
        yawDeg = add_degrees(yawDeg, YAW_DRIFT)
    return yawDeg


# Update yaw drift given that current angle is tgDeg degrees.
# To be called after aligning bot, for example against a wall.
async def update_yaw(tgDeg):
    global YAW_DRIFT
    curYaw = read_yaw(addDrift = False)
    # print("curYaw: " + str(curYaw))
    YAW_DRIFT = degree_diff(tgDeg, curYaw)
    # print("drift: " + str(YAW_DRIFT))

async def test_update_yaw():
    curYaw = read_yaw()
    tgDeg = add_degrees(curYaw, -20)
    await update_yaw(tgDeg)
    assert abs(read_yaw() - tgDeg) < 1
    await update_yaw(curYaw)


# Input is in degrees (0 to 360)
# Unreliable. Avoid. Use update_yaw instead.
async def reset_yaw(newDeg):
    global YAW_DRIFT
    YAW_DRIFT = 0
    yaw1 = degrees_to_yaw(newDeg)
    # reset_yaw expects degrees in internal units
    motion_sensor.reset_yaw(yaw1 * -10)
    # It takes time for the yaw to become readable
    await runloop.sleep_ms(500)
    await runloop.until(motion_sensor.stable)
    curYaw = read_yaw()
    assert abs(curYaw - newDeg) < 3, "Yaw not correctly reset. Expecting " + str(newDeg) + "Actual: " + str(curYaw)
    await update_yaw(newDeg)

async def test_reset_yaw():
    oldYaw = read_yaw()
    newYaw = 45
    await reset_yaw(newYaw)
    assert(read_yaw() == newYaw)
    await reset_yaw(oldYaw)


async def test_yaw_functions():
    print('Test yaw functions')
    test_yaw_to_degrees()
    await test_reset_yaw()
    await test_update_yaw()
    print('Passed')



# ----------------------Turning
# Turning at high speed is imprecise

def stop_moving():
    motor_pair.stop(DRIVE_MOTORS)


def prep_turn(speed):
    stop_moving()



# Turn without gyro BY deg degrees
# speed always positive
# Negative deg (degrees) means turn left
# Precise for small turn angles. Not for larger ones. (Why?)
async def spin_turn(deg, speed = 10):
    if abs(deg) < 1:
        return True
    # Add a multiplier for gear ratios if you’re using gears
    spinCircumference = TRACK * pi
    motor_degrees = int((spinCircumference / CM_PER_ROTATION) * abs(deg))
    v = pct_to_motor_speed(abs(speed))
    if deg > 0:
        # spin clockwise
        steering = 100
    else:
        #spin counter clockwise
        steering = -100
        # await motor_pair.move_for_degrees(DRIVE_MOTORS, motor_degrees, -100, velocity = v)
    await motor_pair.move_for_degrees(DRIVE_MOTORS, motor_degrees, steering, velocity = v)


async def test_spin_turn():
    info_msg("Testing spin turn. Should end up facing forward again.")
    deg1 = 45
    for j in range(8):
        await spin_turn(deg1)
        time.sleep(0.3)
    for j in range(8):
        await spin_turn(-deg1)
        time.sleep(0.3)
    info_msg("Passed")


# Turn right to deg1 degrees
async def turn_right(deg1, speed = 10):
    prep_turn(speed)
    startDeg = read_yaw()
    if deg1 == startDeg:
        return startDeg

    turnDeg = turn_angle_right(startDeg, deg1)
    await spin_turn(turnDeg, speed = speed)

    # Gyro version
    # done = False
    # # Already turned past 360?
    # if startDeg > deg1:
    #    past360 = False
    # else:
    #    past360 = True

    # v = pct_to_motor_speed(speed)
    # motor_pair.move_tank(DRIVE_MOTORS, v, -v)
    # while not done:
    #    curDeg = read_yaw()
    #    if curDeg < startDeg:
    #        # We passed 360
    #        past360 = True
    #    if (curDeg >= deg1 and past360):
    #        done = True
    # stop_moving()
    # Need to give yaw sensor time to be read
    # await runloop.sleep_ms(100)
    # return read_yaw()


# Turn left to deg1 degrees
async def turn_left(deg1, speed = 10):
    prep_turn(speed)
    startDeg = read_yaw()
    if deg1 == startDeg:
        return startDeg

    turnDeg = turn_angle_left(startDeg, deg1)
    await spin_turn(-turnDeg, speed = speed)

    # done = False
    # # Already turned past 360?
    # if startDeg < deg1:
    #    past360 = False
    # else:
    #    past360 = True

    # v = pct_to_motor_speed(speed)
    # motor_pair.move_tank(motor_pair.PAIR_1, -v, v)
    # while not done:
    #    curDeg = read_yaw()
    #    if curDeg > startDeg:
    #        # We passed 360
    #        past360 = True
    #    if (curDeg <= deg1 and past360):
    #        done = True
    # stop_moving()

    # Need to give yaw sensor time to be read
    # await runloop.sleep_ms(100)
    # return read_yaw()


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
    # return read_yaw()



# Check if robot has turned to near target angle (in degrees)
def check_turn(tg):
    curDeg = read_yaw()
    # Need to use left or right turn angle
    # b/c of 360 degree rollover
    gap = turn_angle_lr(curDeg, tg)
    if abs(gap) < 5:
        return True
    else:
        print("Turn failed. Tg: " + str(tg) + "Actual: " + str(curDeg))
        return False


async def test_turning():
    await update_yaw(0)
    print("Test turning")
    passed = True

    # Test going past 360
    for deg in [60, 10, 0]:
        await turn_right(deg)
        if not check_turn(deg):
            passed = False
    pass_fail_msg("Turning right", passed)

    passed = True
    for deg in [350, 90, 340, 0]:
        await turn_left(deg)
        if not check_turn(deg):
            passed = False
    pass_fail_msg("Turning left", passed)

    passed = True
    for deg in [350, 10, 0]:
        await turn_to_degrees(deg)
        if not check_turn(deg):
            passed = False
    pass_fail_msg("Turning to degrees", passed)
    # info_msg("Done")



# ---------------------------------------Gyro driving

# While driving, adjust direction to point to `tgDeg`
def adjust_direction(tgDeg, speed):
    curDeg = read_yaw()
    # How far do we need to turn?
    turnAngle = turn_angle_lr(curDeg, tgDeg)
    correction = round(2 * turnAngle)
    correction = min(20, max(correction, -20))
    if speed < 0:
        correction = -correction
    drive(correction, speed)
    time.sleep(0.05)


# Drive straight using gyro in direction `tgDeg`
# at speed `speed`
# for distance `dist` in cm
# for at most `maxTime` seconds
# Can drive backwards. Set speed < 0 (Lego convention)
async def gyro_straight(tgDeg = 0, speed = 50, dist = 10.0, maxTime = 5):
    assert check_degrees(tgDeg)
    await turn_to_degrees(tgDeg)
    # Need to use right motor. The left one runs backwards.
    startDeg = motor.relative_position(RIGHT_MOTOR)
    distDeg = cm_to_degrees(dist)
    if speed < 0:
        distDeg = -distDeg
    tgMotorDeg = startDeg + distDeg

    startTime = time.ticks_ms()
    drive(0, speed)

    done = False
    while not done:
        adjust_direction(tgDeg, speed)
        relPos = motor.relative_position(RIGHT_MOTOR)
        if (speed > 0) and (relPos >= tgMotorDeg):
            done = True
        if (speed < 0) and (relPos <= tgMotorDeg):
            done = True
        if (time.ticks_ms() - startTime) > 1000 * maxTime:
            done = True
    stop_moving()


# Turn towards point (x,y). If not forward: turn bot's back that way.
async def turn_to_xy(x, y, forward = True):
    dx, dy = get_current_dx_dy(x, y)
    if not forward:
        dx = -dx
        dy = -dy
    tgDeg = vector_to_angle(dx, dy)
    await turn_to_degrees(tgDeg)
    return tgDeg

async def test_turn_to_xy():
    info_msg("Testing turn to xy")
    await turn_to_xy(10, 10)
    assert check_turn(45)
    await turn_to_xy(10, 10, forward = False)
    # These are not precise
    check_turn(45 + 180)
    await turn_to_xy(0, 10)
    check_turn(0)
    info_msg("Passed")


# Drive in a straight line to point (x, y)
# Update XPOS and YPOS globals.
async def drive_to_xy(x, y, speed = 50, maxTime = 5):
    if at_xy(x, y):
        return True
    tgDeg = await turn_to_xy(x, y, forward = (speed >= 0))
    dx, dy = get_current_dx_dy(x, y)
    dist = vector_length(dx, dy)
    await gyro_straight(tgDeg = tgDeg, speed = speed, dist = dist, maxTime = maxTime)
    update_xy(x, y)


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
# Inputs are:
# - lr: LEFT or RIGHT (sensor)
# - bw: BLACK or WHITE (line color)
# - steering: between -100 (left turn) and 100 (right turn)
def line_finder(lr, bw, speed = 10, maxTime = 5, steering = 0):
    if line_found(lr, bw):
        return True
    done = False
    startTime = time.ticks_ms()
    drive(steering, speed)
    # motor_pair.move(DRIVE_MOTORS, steering, velocity = pct_to_motor_speed(speed))
    while not done:
        if line_found(lr, bw):
            done = True
        if time.ticks_ms() - startTime > 1000 * maxTime:
            done = True
    stop_moving()
    return line_found(lr, bw)


# Align robot on a line. Robot already found the line.
# Usually update_yaw and XPOS, YPOS afterwards.
def line_align(bw):
    if line_found(LEFT, bw):
        return line_align_lr(RIGHT, bw)
    elif line_found(RIGHT, bw):
        return line_align_lr(LEFT, bw)
    else:
        print("Cannot align on line. Need to find line first.")
        return False


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


# Drive to a line with an offset of (dx, dy)
# Arrive such that the robot can be aligned
# This is not sufficiently reliable to be used. +++
async def drive_to_line(line1, speed = 50, dx = -5, dy = -5):
    await drive_to_xy(line1["xpos"] + dx, line1["ypos"] + dy)
    await turn_to_degrees(line1["yaw"])

# Align on a named line.
# This is not sufficiently reliable to be used. +++
async def align_to_line(line1, speed = 20, dx = -5, dy = -5):
    await drive_to_line(line1, speed = speed)
    # Drive forward until BLACK line is found with RIGHT sensor
    line_finder(RIGHT, BLACK)
    # Align so that both sensors see the line
    line_align(BLACK)
    await update_yaw(45)
    update_xy(line1["xpos"], line1["ypos"])



# ---------------------Arm movement
# Assumes that clockwise movement raises arm
# At startup, and periodically during the run, reset the arm position.
#That means: raise arm as down as it goes. Store the relative motor position.

# Valid arm position (in degrees)?
def valid_arm_pos(deg1):
    global MIN_ARM_POS, MAX_ARM_POS
    return MIN_ARM_POS <= deg1 <= MAX_ARM_POS

# Clamp arm position in DEGREES
def clamp_arm_pos(deg):
    global MIN_ARM_POS, MAX_ARM_POS
    return min(MAX_ARM_POS, max(MIN_ARM_POS, deg))

# At startup, the arm is all the way down. We call that zero degrees.
# def store_arm_zero_pos():
#    global MIN_ARM_POS
#    motor.reset_relative_position(ARM_MOTOR, MIN_ARM_POS)

# Convert motor degrees into actual degrees
# Depends on gear ratio
def arm_pos_to_degrees(armPos):
    return round(armPos / ARM_GEAR_RATIO)

def degrees_to_arm_pos(deg):
    return round(ARM_GEAR_RATIO * clamp_arm_pos(deg))

# Get arm position in degrees. 180 = vertically up
def get_arm_pos():
    mDeg = motor.relative_position(ARM_MOTOR)
    return arm_pos_to_degrees(mDeg)

def check_arm_pos(tgDeg):
    deg = get_arm_pos()
    if abs(deg - tgDeg) > 2:
        print("Invalid arm position: Expecting " + str(tgDeg) + "Actual: " + str(deg))
        return False
    else:
        return True

async def arm_to_degrees(deg1, speed = 50, deceleration = 1000):
    armPos = degrees_to_arm_pos(deg1)
    await motor.run_to_relative_position(ARM_MOTOR, armPos, pct_to_arm_speed(speed), deceleration = deceleration)
    return check_arm_pos(deg1)


# Move arm up, unless it is already up
async def arm_up(deg1, speed = 50, deceleration = 1000):
    if get_arm_pos() < deg1:
        # armPos = degrees_to_arm_pos(deg1)
        await arm_to_degrees(deg1, speed = speed, deceleration = deceleration)
        # await motor.run_to_relative_position(ARM_MOTOR, armPos, pct_to_arm_speed(speed))

# Move arm down, unless it is already down
async def arm_down(deg1, speed = 50, deceleration = 1000):
    if get_arm_pos() > deg1:
        # armPos = degrees_to_arm_pos(deg1)
        await arm_to_degrees(deg1, speed = speed, deceleration = deceleration)
        # await motor.run_to_relative_position(ARM_MOTOR, armPos, pct_to_arm_speed(speed))

async def arm_vertical(speed = 80):
    global MAX_ARM_POS
    await arm_up(MAX_ARM_POS, speed = speed)


# Reset arm position. Runs arm all the way up. Associates
# resulting relative motor position with known MAX_ARM_POS degree angle.
# Run periodically to ensure arm is in reproducible position.
async def calibrate_arm_pos():
    # Raise arm by 200 degrees. It will stall at MAX_ARM_POS.
    await motor.run_for_degrees(ARM_MOTOR, degrees_to_arm_pos(200), 500)
    maxArmPos = degrees_to_arm_pos(MAX_ARM_POS)
    motor.reset_relative_position(ARM_MOTOR, maxArmPos)

# Visually check that arm is at 90 degrees afterwards
async def test_calibrate_arm_pos():
    await calibrate_arm_pos()
    await arm_down(90)
    assert check_arm_pos(90)


async def test_arm_movements():
    info_msg("Testing arm movements")
    await test_calibrate_arm_pos()

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
    await arm_up(180)
    info_msg("Passed")


# Code to check that arm movements are repeatable
async def try_arm_movements():
    # await calibrate_arm_pos()
    print("Arm pos: " + str(get_arm_pos()))

    # for j in range(5):
    #    await arm_down(90)
    #    time.sleep(0.1)
    #    await arm_up(180)

    await arm_down(90)
    time.sleep(0.5)
    await arm_up(150)
    time.sleep(0.5)
    await arm_down(90)
    time.sleep(0.5)
    await arm_down(20)
    time.sleep(0.5)
    await arm_up(150)
    time.sleep(0.5)
    await arm_down(45)
    time.sleep(0.5)
    await arm_up(180)



# -------------Startup

def config_robot():
    motor_pair.pair(DRIVE_MOTORS, LEFT_MOTOR, RIGHT_MOTOR)

async def boot_robot():
    config_robot()
    await reset_yaw(0)
    await calibrate_arm_pos()
    info_msg("Boot sequence complete.")


# ----------------------Testing

# Does not drive the robot, but performs turns and arm
# movements.
# Should return robot back to original orientation.
async def test_no_driving():
    info_msg("Test no driving")
    test_add_degrees()
    test_moving_helpers()
    test_turn_angle_right()
    test_turn_angle_left()
    test_turn_left_or_right()
    test_turn_angle_lr()
    await test_turn_to_xy()
    await test_arm_movements()
    test_vector_to_angle()
    await test_yaw_functions()
    await test_spin_turn()
    await test_turning()
    info_msg("Passed")


# Test with driving. Requires space around the bot.
# Success means that the bot returns to start position.
async def test_driving_forward():
    info_msg("Test driving forward")
    x0, y0 = get_current_xy()
    await update_yaw(0)
    # await drive_distance(12, speed = 50)
    await drive_to_xy(x0, y0 + 12)
    await turn_left(250)
    await drive_to_xy(x0 - 12, y0 + 5)
    await drive_to_xy(x0, y0, speed = 30)
    await turn_to_degrees(0)
    info_msg("Passed")


# Should return bot to start position
async def test_driving_backward():
    info_msg("Test driving backward")
    x0, y0 = get_current_xy()
    await update_yaw(0)
    await drive_to_xy(x0, y0 + 12)
    await drive_to_xy(x0, y0, speed = -30)
    await drive_to_xy(x0, y0 + 12)
    await turn_left(250)
    await drive_to_xy(x0 - 12, y0 + 5)
    await drive_to_xy(x0, y0, speed = -30)
    await turn_to_degrees(0)
    info_msg("Passed")


# Run all tests. Requires space for driving.
# Should return bot to start position.
async def test_all():
    await test_no_driving()
    await test_driving_forward()
    await test_driving_backward()



# --------------------------------Mission Runs

# To be called first when a mission starts from the right start box.
async def start_from_right():
    global RIGHT_START_XPOS
    update_xy(RIGHT_START_XPOS["xpos"], RIGHT_START_XPOS["ypos"])
    await update_yaw(RIGHT_START_XPOS["yaw"])
    set_run_start_time()
    await calibrate_arm_pos()


# Drive to Silo
async def right_start_to_silo():
    global RIGHT_START_XPOS
    info_msg("Driving: right start to Silo")
    await arm_vertical()
    # Drive north
    x0 = RIGHT_START_XPOS["xpos"]
    y0 = SILO["ypos"]
    await drive_to_xy(x0, y0, speed = 50)
    # Turn to face target
    await turn_right(90)
    # Drive east 2cm
    await drive_to_xy(x0 - 2, y0, speed = -20)
    show_elapsed_time()


async def silo_action():
    info_msg("Silo action")
    for j in range(3):
        await arm_down(20, speed = 100)
        await arm_vertical()
    show_elapsed_time()


async def silo_to_balldrop():
    global TOP_RIGHT_LINE, BLACK, RIGHT
    info_msg("Driving Silo to BallDrop (top right line)")
    await arm_vertical()
    # Back up from Silo
    # await drive_to_xy(160, 65, speed = -30)
    await turn_left(20)
    # Drive to near the line TOP_RIGHT_LINE. Then find and align.
    # await align_to_line(TOP_RIGHT_LINE, speed = 50)
    line_finder(RIGHT, BLACK)
    line_align(BLACK)
    info_msg("Aligned on top-right line")
    show_elapsed_time()

async def test_silo_to_balldrop():
    info_msg("Testing driving from Silo to Balldrop (top right line)")
    update_xy(SILO["xpos"], SILO["ypos"])
    await update_yaw(SILO["yaw"])
    time.sleep(0.5)
    await silo_to_balldrop()


# Balldrop action, starting from top right line
async def balldrop_action():
    info_msg("Ball drop action")
    await arm_vertical()
    # need simpler function for driving straight short distances +++++
    # drive_distance, but needs to update XPOS, YPOS
    await gyro_straight(tgDeg = 45, speed = 10, dist = 1)
    # Arm down to the right of lever
    await turn_to_degrees(80)
    await arm_down(55)
    # Push lever left
    await turn_to_degrees(0)
    # May have to calibrate arm position
    await arm_vertical()
    show_elapsed_time()

# continue here +++++

async def balldrop_to_tr_line():
    global TOP_RIGHT_LINE
    info_msg("Driving: BallDrop to top right line")
    # Back up from BallDrop, behind the line
    await arm_vertical()
    await turn_to_degrees(45)
    await gyro_straight(tgDeg = 45, speed = -50, dist = 10)
    # Align again on the line
    await align_to_line(TOP_RIGHT_LINE)
    show_elapsed_time()


async def tr_line_to_table():
    info_msg("Driving Top Right line to table")
    global TOP_RIGHT_LINE
    update_xy(TOP_RIGHT_LINE["xpos"], TOP_RIGHT_LINE["ypos"])
    await update_yaw(TOP_RIGHT_LINE["yaw"])
    await arm_vertical()
    # Back up 20 cm
    await gyro_straight(tgDeg = 45, speed = -20, dist = 18)# drives too far
    await turn_left(0)
    await gyro_straight(355, dist = 15)
    show_elapsed_time()


async def table_action():
    info_msg("Table action")
    # Arm down to the left of lever
    await arm_down(55)
    # Push lever right
    await turn_right(25)
    await arm_vertical()
    # Back up to
    await gyro_straight(tgDeg = 90, dist = 15, speed = -25)
    # should perhaps raise arm and use table to align yaw +++
    show_elapsed_time()

# Starts aligned on TOP_RIGHT_LINE. Driving function sets coordinates.
# Can be run without prep
async def test_tr_line_to_table():
    await tr_line_to_table()
    await table_action()
    await table_to_tr_line()


async def table_to_tr_line():
    info_msg("Driving: table to top right line")
    # Back away from table to a point where we can find line
    await drive_to_xy(160, 70, speed = -30)
    await turn_right(35)
    line_finder(RIGHT, BLACK)
    line_align(BLACK)
    update_xy(TOP_RIGHT_LINE["xpos"], TOP_RIGHT_LINE["ypos"])
    await update_yaw(TOP_RIGHT_LINE["yaw"])
    show_elapsed_time()


# Start position not clear +++
# But can start on top right line
# Then just turn to 270 degrees and drive straight for 45 cm
async def table_to_bucket():
    info_msg("Driving Table to Bucket")
    # Drive to north of bucket
    x0 = 125
    await drive_to_xy(x0, 90, speed = 60, maxTime = 7)
    # Drive towards bucket
    await drive_to_xy(x0, 75, speed = 60, maxTime = 7)
    await arm_down(30)
    await arm_vertical()
    # Try again closer
    await drive_to_xy(x0, 70, speed = 60, maxTime = 7)
    await arm_down(30)
    await arm_vertical()
    info_msg("Done")


async def bucket_to_north_wall():
    info_msg("Aligning against north wall")
    await drive_to_xy(125, 115, speed = -50)
    # Update position facing south
    update_xy(125, 110)
    await update_yaw(-179)
    info_msg("Aligned")

async def north_wall_to_raise_table():
    info_msg("North wall to raise roof")
    await drive_to_xy(125, 85)
    await turn_to_degrees(135)
    await gyro_straight(135, speed = 30, dist = 20)


# Alternative: Drive from table to raise roof
async def table_to_raise_roof():
    info_msg("Drive table to raise roof")
    await turn_right(135)
    await gyro_straight(tgDeg = 135, speed = -20, dist = 10)
    await gyro_straight(tgDeg = 130, speed = 50, dist = 25, maxTime = 3)
    show_elapsed_time()



# Run the complete mission, starting from right start box.
async def run_from_right():
    await start_from_right()
    await right_start_to_silo()
    await silo_action()
    await silo_to_balldrop()

    await balldrop_action()
    await balldrop_to_tr_line()

    await tr_line_to_table()
    await table_action()
    await table_to_tr_line()
    return True


    await table_to_bucket()
    await bucket_to_north_wall()
    await north_wall_to_raise_table()
    show_elapsed_time()
    return True



# -----------------Main


async def main():
    global RIGHT, BLACK
    await boot_robot()

    test_vector_to_angle()
    # print(angle_to_vector(0, 10))
    # print(approx_equal(angle_to_vector(0, 10), (0, 10)))

    return True

    # await test_turning()
    # await test_arm_movements()
    # await test_no_driving()
    # await test_driving_forward()
    # await test_driving_backward()
    # await test_all()

    # await test_silo_to_balldrop()
    await test_tr_line_to_table()

    # await run_from_right()

    return True
    # Not the best way of exiting; raises an error.
    # But avoids having to press stop after each run.
    # sys.exit()


runloop.run(main())


# -----------------------------------------