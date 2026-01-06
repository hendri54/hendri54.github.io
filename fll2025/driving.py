from hub import light_matrix, port, motion_sensor
from math import atan2, degrees, sqrt, pi, radians, cos, sin, isclose
import runloop, motor, motor_pair, sys, time, color_sensor

# ----------------------General notes
#
# The code keeps track of where the robot is at all times.
# The globals (XPOS, YPOS) record the distance from the bottom-left
# corner of the table to the current position in cm.
# Example: Going "east" increases only XPOS. Going "south" decreases only YPOS.
#
# The yaw sensor keeps track of the direction of the robot.
# Yaw = 0 points "north." Yaw = 270 points "west."
# The yaw is never reset to 0. It always points north.
# The yaw sensor drifts. It needs to be periodically updated when the
# direction of the robot is known, for example because it is aligned with a line.
# The yaw is hard to reset reliably. Instead, it is better to keep track of
# how far off the yaw is compared with the actual robot orientation. The
# global YAW_DRIFT does that.
#
# Driving is done to absolute positions. `drive_to_xy` takes as
# arguments an (x, y) target position on the table (in cm).
# It drives to that absolute position from anywhere on the table.
# This only works well if one has good measurement of known alignment point,
# such as lines.
#
# All distances are in cm.
# All angles are in degrees (0 to 360).
# All speeds are in percentages (-100 to 100). Negative values go backwards.
#
# Key functions:
# `gyro_straight` - drive in a straight line in a given direction for a given distance.
# `drive_distance` - drive straight without gyro; good for short distances.
# `turn_to_degrees` - turn the robot towards a fixed angle.
# `turn_left` and `turn_right` - turn to a fixed angle.
# `line_finder` - find a black-and-white line
# `line_align` - align that bot on a line
# `arm_up`, `arm_down` - move arm up / down to a fixed position. 0 is all the way down.
#    180 is vertically up.


# -------------------Constants
# Some of these need to updated when robot design changes.

# These constants just clarify intent of the code
LEFT = -1
RIGHT = 1
LEFT_OR_RIGHT = 33
BLACK = 11
WHITE = 12
BLACK_OR_WHITE = 44

# Robot configuration
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

# (x,y) values of right and north walls
MAX_XPOS = 198
MAX_YPOS = 108


# ------------------------------Locations
# Here we record known alignment points or
# where the robot should stand when carrying out a task.

# Right start box
# This is a `Dict`. `RIGHT_START["xpos"]` retrieves.
RIGHT_START = {"xpos": 165, "ypos": 10, "yaw": 0}

# Left start box
LEFT_START = {"xpos": 20, "ypos": 10, "yaw": 0}

# 45 degree black-and-white line in top right corner
TOP_RIGHT_LINE = {"xpos": 165, "ypos": 75, "yaw": 45}

# Silo approach position. Facing silo pointing east.
SILO = {"xpos": 165, "ypos": 71, "yaw": 90}


# --------------------Global variables

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

# Are two tuples approximately equal?
# Uses abs tolerance by default.
# Example: `approx_equal((1.0, 2.0), (0.999, 2.001), abs_tol = 1e-2)
def approx_equal(tuple1, tuple2, rel_tol = 1, abs_tol = 1e-4):
    if len(tuple1) != len(tuple2):
        return False
    return all(isclose(a, b, rel_tol=rel_tol, abs_tol=abs_tol)
            for a, b in zip(tuple1, tuple2))

# Print info message in console.
def info_msg(msg):
    print(msg)

# Report whether a test passed or failed.
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


# Printing helpers
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
    elif lr == LEFT_OR_RIGHT:
        return "Left or right"
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

# Return current (x, y) position
def get_current_xy():
    global XPOS, YPOS
    return XPOS, YPOS

# How far do we have to move (dx, dy) to get to (x,y)?
# Basically returns (x - XPOS, y - YPOS)
def get_current_dx_dy(x, y):
    xp, yp = get_current_xy()
    return x - xp, y - yp

# Record new (XPOS, YPOS). To be used when we know exactly where the
# robot sits.
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


# Update current position and yaw from a Dict describing a position
# Example: `update_current_pos(TOP_RIGHT_LINE)`
async def update_current_pos(d):
    if ("xpos" in d) and ("ypos" in d):
        update_xy(d["xpos"], d["ypos"])
    if "yaw" in d:
        await update_yaw(d["yaw"])


# Length of the vector (Pythagoras)
def vector_length(dx, dy):
    return sqrt(dx*dx + dy*dy)


# Convert distance in cm to motor rotations in degrees
# Used as input for `move_for_degrees`
def cm_to_degrees(distance_cm):
    # Add multiplier for gear ratio if needed
    return round((distance_cm/CM_PER_ROTATION) * 360)

# Convert motor rotations to distance
def degrees_to_cm(deg1):
    return (deg1/360) * CM_PER_ROTATION


# Speeds are always in percentage points.
# Negative is moving backwards.
def valid_speed(pct):
    return -100 <= pct <= 100

# Convert speed in percent to motor speed
# Returns `int` because that's what motors expect.
def pct_to_motor_speed(pct):
    assert valid_speed(pct)
    return round((pct / 100) * MAX_DRIVE_SPEED)

# The same for the arm motor
def pct_to_arm_speed(pct):
    assert valid_speed(pct)
    return round((pct / 100) * MAX_ARM_SPEED)


# Drive in direction `steering` (-100 to 100) at `speed` (0 to 100)
# Smooth acceleration: set `acceleration` to a low value, such as 300
def drive(steering, speed, acceleration = 300):
    motor_pair.move(DRIVE_MOTORS, steering, velocity = pct_to_motor_speed(speed), acceleration = acceleration)


# Drive straight (no gyro) for a given distance. Smooth acceleration.
# By default: update XPOS, YPOS.
# Returns (dx, dy) of vector driven.
async def drive_distance(dist, speed = 50, accel = 300, decel = 300, updateXY = True):
    deg1 = cm_to_degrees(dist)
    # print("Degrees" + str(deg1))
    await motor_pair.move_for_degrees(DRIVE_MOTORS, deg1, 0, velocity = pct_to_motor_speed(speed), acceleration = accel, deceleration = decel)

    # Return dx, dy based on distance and yaw
    yaw0 = read_yaw()
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




# ------------------------Turn angles

# Scale degrees into (0, 360)
# Example: `scale_degrees(370) == 10`
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
# Example: `turn_angle_right(350, 10) == 20`
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
# Example `turn_angle_left(10, 350) == 20`
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


# Should we turn left or right when turning from angle `a1` to `a2`?
# Example: `turn_left_or_right(10, 350) == LEFT`
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
# Example: `turn_angle_lr(10, 350) == -20`
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
# Example: `vector_to_angle(10, 10) == 45`
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
# Example: `angle_to_vector(45, 10) == (7, 7)`
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

# Check whether or not `deg1` is a valid degree number in (0, 360)
def check_degrees(deg1):
    return 0 <= deg1 <= 360

# Valid input for yaw?
def check_yaw(yaw1):
    return -179 <= yaw1 <= 180

# Convert yaw in (-179 to 180) into degrees (0 to 360)
# Example: `yaw_to_degrees(-179) == 181`
def yaw_to_degrees(yaw1):
    assert check_yaw(yaw1), "Invalid yaw: " + str(yaw1)
    if yaw1 >= 0:
        return yaw1
    else:
        return 360 + yaw1

# The inverse of yaw_to_degrees
# Example: `degrees_to_yaw(181) == -179`
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


# Return current yaw in degrees (0 to 360)
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
    # Read yaw sensor value without drift correction
    curYaw = read_yaw(addDrift = False)
    # Drift = (actual yaw) - (sensor reading)
    YAW_DRIFT = degree_diff(tgDeg, curYaw)

async def test_update_yaw():
    curYaw = read_yaw()
    tgDeg = add_degrees(curYaw, -20)
    await update_yaw(tgDeg)
    assert abs(read_yaw() - tgDeg) < 1
    await update_yaw(curYaw)


# Reset the yaw sensor
# Input is in degrees (0 to 360)
# Unreliable. Avoid. Use update_yaw instead.
async def reset_yaw(newDeg):
    info_msg("Resetting yaw")
    global YAW_DRIFT
    YAW_DRIFT = 0
    yaw1 = degrees_to_yaw(newDeg)
    # reset_yaw expects degrees in internal units
    motion_sensor.reset_yaw(yaw1 * -10)
    # It takes time for the yaw to become readable
    await runloop.sleep_ms(200)
    await runloop.until(motion_sensor.stable)
    curYaw = read_yaw()
    assert abs(curYaw - newDeg) < 3, "Yaw not correctly reset. Expecting " + str(newDeg) + "Actual: " + str(curYaw)
    await update_yaw(newDeg)
    show_elapsed_time()


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
async def spin_turn(deg, speed = 10, steering = 100):
    if abs(deg) < 1:
        # No need to turn
        return True
    # Add a multiplier for gear ratios if you’re using gears
    spinCircumference = TRACK * pi
    motor_degrees = int((spinCircumference / CM_PER_ROTATION) * abs(deg))
    # Speed always positive
    v = pct_to_motor_speed(abs(speed))
    if deg > 0:
        # spin clockwise
        steer = steering
    else:
        #spin counter clockwise
        steer = -steering
    await motor_pair.move_for_degrees(DRIVE_MOTORS, motor_degrees, steer, velocity = v)


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


# Turn left to deg1 degrees
async def turn_left(deg1, speed = 10):
    prep_turn(speed)
    startDeg = read_yaw()
    if deg1 == startDeg:
        return startDeg

    turnDeg = turn_angle_left(startDeg, deg1)
    await spin_turn(-turnDeg, speed = speed)


# Turn left or right, whichever is shorter
async def turn_to_degrees(deg1):
    prep_turn(10)
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
# Turns are not precise. One should not expect to end up very close
# to target angle.
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
# To be used inside the driving loop.
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



# ------------------------Pushing aside
# Experimental

# Pushes edge of the attachment approximate to one side
# in a straight line.
# Just a right turn with steering.
# The steering depends on robot and attachment geometry. Experiment.
async def push_aside(deg, speed = 10, steering = 50):
    await spin_turn(deg, speed = speed, steering = steering)

# Can do better.
# Start angled. Then push to straight.
# So right motor must move back faster than left motor moves forward.
# Run motors until angle is reached. But at different speeds.
# Math unclear. How many degrees do the motors have to run? +++


# Turning with less steering
# Work in progress. Only works approximately.
async def turn_with_steering(deg, steering, speed = 30):
    if abs(deg) < 1:
        # No need to turn
        return True
    spinDeg = round(deg * 95 / steering)
    # Add a multiplier for gear ratios if you’re using gears
    spinCircumference = TRACK * pi
    motor_degrees = int((spinCircumference / CM_PER_ROTATION) * abs(spinDeg))
    v = pct_to_motor_speed(speed)
    if deg > 0:
        # spin clockwise
        steer = steering
    else:
        #spin counter clockwise
        steer = -steering
    await motor_pair.move_for_degrees(DRIVE_MOTORS, motor_degrees, steer, velocity = v)



async def test_turn_with_steering():
    await boot_robot()
    deg1 = 180
    steer = 40
    await turn_with_steering(-deg1, steer, speed = -20)


# -----------------Line Finding
# White lines are not found reliably. Black lines are.

# Return light reflected by left or right sensor.
# Example: `light_reflected(LEFT)`
def light_reflected(lr):
    if lr == LEFT:
        return color_sensor.reflection(LTSENSOR_LEFT)
    elif lr == RIGHT:
        return color_sensor.reflection(LTSENSOR_RIGHT)
    else:
        raise ValueError("lr must be LEFT or RIGHT")

# Has a white line been found?
def white_line(lr):
    if lr == LEFT_OR_RIGHT:
        return (light_reflected(LEFT) > 80) or (light_reflected(RIGHT) > 80)
    else:
        return light_reflected(lr) > 80

# Has a black line been found?
def black_line(lr):
    if lr == LEFT_OR_RIGHT:
        return (light_reflected(LEFT) < 22) or (light_reflected(RIGHT) < 22)
    else:
        return light_reflected(lr) < 22

# Has a line been found?
# Example: `line_found(LEFT, BLACK)`
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
# - lr: LEFT or RIGHT (sensor) or with either sensor
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
# async def drive_to_line(line1, speed = 50, dx = -5, dy = -5):
#    await drive_to_xy(line1["xpos"] + dx, line1["ypos"] + dy)
#    await turn_to_degrees(line1["yaw"])

# Align on a named line.
# This is not sufficiently reliable to be used. +++
# async def align_to_line(line1, speed = 20, dx = -5, dy = -5):
#    await drive_to_line(line1, speed = speed)
#    # Drive forward until BLACK line is found with RIGHT sensor
#    line_finder(RIGHT, BLACK)
#    # Align so that both sensors see the line
#    line_align(BLACK)
#    await update_yaw(45)
#    update_xy(line1["xpos"], line1["ypos"])



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

async def arm_to_degrees(deg1, speed = 50, deceleration = 3000):
    armPos = degrees_to_arm_pos(deg1)
    await motor.run_to_relative_position(ARM_MOTOR, armPos, pct_to_arm_speed(speed), deceleration = deceleration)
    return check_arm_pos(deg1)


# Move arm up, unless it is already up
async def arm_up(deg1, speed = 50, deceleration = 3000):
    if get_arm_pos() < deg1:
        # armPos = degrees_to_arm_pos(deg1)
        await arm_to_degrees(deg1, speed = speed, deceleration = deceleration)
        # await motor.run_to_relative_position(ARM_MOTOR, armPos, pct_to_arm_speed(speed))

# Move arm down, unless it is already down
async def arm_down(deg1, speed = 50, deceleration = 3000):
    if get_arm_pos() > deg1:
        # armPos = degrees_to_arm_pos(deg1)
        await arm_to_degrees(deg1, speed = speed, deceleration = deceleration)
        # await motor.run_to_relative_position(ARM_MOTOR, armPos, pct_to_arm_speed(speed))

async def arm_vertical(speed = 80):
    global MAX_ARM_POS
    await arm_up(180, speed = speed)


# Strike down with max force
async def strike_down(deg1):
    if get_arm_pos() > deg1:
        armPos = degrees_to_arm_pos(deg1)
        await motor.run_to_relative_position(ARM_MOTOR, armPos, MAX_ARM_SPEED, acceleration = 10000, deceleration = 10000, stop = motor.COAST)



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
    info_msg("Booting robot.")
    set_run_start_time()
    config_robot()
    await reset_yaw(0)
    await calibrate_arm_pos()
    show_elapsed_time()


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



# --------------------------------Mission Run From Right

# To be called first when a mission starts from the right start box.
async def start_from_right():
    global RIGHT_START
    await update_current_pos(RIGHT_START)
    # update_xy(RIGHT_START["xpos"], RIGHT_START["ypos"])
    # await update_yaw(RIGHT_START["yaw"])
    # set_run_start_time()# removed11/13/2025 (now in boot robot)
    # await calibrate_arm_pos()# removed 11/13/2025 (in boot robot)


# 🐋Julia rightside code -> Heavy lifting
# start at right
# end ready to drive to NE line between silo and balldrop
async def start_circle():
    info_msg("Heavy Lifting")
    await arm_vertical()

    info_msg("Driving to heavy lifting")
    # Move from wall
    await drive_distance(20, speed= 80, accel = 1000, decel = 1000)
    # Move to east wall
    await turn_right(45, speed = 20)# was speed = 10
    await drive_distance(35, speed = 65, accel = 1000, decel = 1000)# was speed 6011/13/2025
    # Drive north along wall
    await turn_left(0, speed = 20)# was speed 1011/13/2025
    await gyro_straight(tgDeg= 0, speed= 55, dist= 45)# was speed 4611/13/2025
    # align against target
    await turn_left(310, speed = 20)# was speed 1011/13/2025
    await drive_distance(4, speed= 30)# was dist 2
    show_elapsed_time()

    # Try pushing
    # new 11/16 +++
    # await drive_distance(8, speed = -30)
    # await arm_down(45, speed = 100)
    # await drive_distance(4, speed= 30)
    # await arm_down(40)
    # await drive_distance(6, speed = 30)
    # await drive_distance(1, speed = -30)
    # await arm_vertical()
    # await drive_distance(8, speed = -30)
    # sys.exit()

    info_msg("Grabbing circle")
    await arm_down(50)
    # pull back
    await drive_distance(8, speed= -30)
    # Second grab, this time by base
    await arm_up(85, speed = 90)# was speed = 5011/13/2025
    await drive_distance(6, speed= 40)
    await arm_down(20)
    await drive_distance(5, speed= -40)
    show_elapsed_time()

    info_msg("Backing up along wall")
    await drive_distance(3, speed= 30, accel = 1000, decel = 1000)# was just speed 2011/13/2025
    await turn_right(0, speed = 20)# was speed = 10
    await drive_distance(14, speed= -50, accel = 500, decel = 500)# was defaul accel11/13/2025
    show_elapsed_time()


# start against eastwall end top right line
async def rightwall_to_tr_line():
    info_msg("Right wall to top right line")
    await arm_vertical()
    await turn_left(270, speed = 15)# was 270 degrees speed 1011/13/2025
    await gyro_straight(tgDeg= 270, speed= 50, dist= 48)
    await turn_right(65, speed = 30)# was speed = 1011/13/2025
    line_finder(LEFT, BLACK)
    line_align(BLACK)
    show_elapsed_time()


# Balldrop action, starting from top right line
async def balldrop_action():
    info_msg("Ball drop action")
    await update_current_pos(TOP_RIGHT_LINE)
    await arm_vertical()
    # Move a little closer to target
    await turn_to_degrees(42)# was 4511/13/2025
    await drive_distance(1, speed = 15)
    # Arm down to the right of lever
    await turn_to_degrees(78)
    await arm_down(75, speed = 30, deceleration = 300)# was speed 2011/13/2025
    # Push lever left
    await turn_to_degrees(5)
    show_elapsed_time()

async def test_balldrop_action():
    global TOP_RIGHT_LINE
    await boot_robot()
    await update_current_pos(TOP_RIGHT_LINE)
    await balldrop_action()


# Starting from balldrop
async def table_action():
    info_msg("Table action. Starting from balldrop.")
    # Drive to the right of table lever
    # await arm_up(75)
    # await turn_to_degrees(350)
    await drive_distance(6, speed = 10)
    # await drive_distance(2, speed = -10)
    # Push lever left
    await arm_down(60, speed = 15, deceleration = 300)
    await turn_left(320, speed = 20)# was 30011/13/2025
    # Pull back so we can turn
    await drive_distance(2, speed = -40, accel = 1000, decel = 1000)# was just speed = -2011/13/2025
    await arm_vertical()
    await turn_to_degrees(350)
    show_elapsed_time()


async def test_table_action():
    info_msg("Test table action starting from TR line")
    await boot_robot()
    await update_current_pos(TOP_RIGHT_LINE)
    await balldrop_action()
    await table_action()


# After table action, find the top right line again
async def table_to_tr_line():
    info_msg("Driving: table to top right line")
    # Back away from table to a point where we can find line
    await arm_vertical()
    # Turn right. Need to make room first.
    # await drive_distance(1, speed = -10)# removed 11/14; table action already pulls back
    await turn_right(30)
    # Back up and turn towards line
    await drive_distance(10, speed=-30)
    await turn_right(40)
    line_finder(RIGHT, BLACK)
    line_align(BLACK)
    await update_current_pos(TOP_RIGHT_LINE)
    show_elapsed_time()


# Top right line to bucket and bucket action.
async def tr_line_to_bucket():
    info_msg("Top right line to bucket and bucket action")
    await update_current_pos(TOP_RIGHT_LINE)
    await arm_vertical()
    # Drive to north of bucket
    await turn_left(290, speed = 25)
    await drive_distance(46, speed = 60, accel = 500, decel = 500)# was default accel11/13/2025
    # Turn south
    await turn_left(185, speed = 20)# was default speed11/13/2025 angle 180
    # Align and lower arm
    await drive_distance(4, speed = 50)
    await arm_down(55)
    # Back away
    await drive_distance(4, speed = -30, accel = 800, decel = 800)# was default accel11/13/2025
    await arm_vertical()
    show_elapsed_time()


async def test_tr_line_to_bucket():
    await boot_robot()
    await update_current_pos(TOP_RIGHT_LINE)
    await tr_line_to_bucket()
    await raise_roof()


# ----------------------Updated right mission-----------------------------
# Bucket -> raise roof -> statue tail -> mine cart -> left home

# Drive from right start box to bucket.
# Start from leftmost thick black line. End facing bucket.
async def right_start_2_bucket():
    info_msg("Right start to bucket.")
    await drive_distance(80, speed= 90, accel= 3000, decel= 3000)
    await turn_left(285, speed= 30)
    await drive_distance(38, speed= 50, accel= 1000, decel= 1000)
    await turn_left(182, speed= 25)
    show_elapsed_time()

async def test_right_start_2_bucket():
    info_msg("Testing right start to bucket")
    await boot_robot()
    await right_start_2_bucket()

# Bucket action. Starting facing bucket. Ending backed away from bucket facing south.
async def bucket_action():
    info_msg("Bucket action")
    await drive_distance(5, speed = 30)
    await arm_down(55)
    # Back away
    await drive_distance(2, speed = -30, accel = 1000, decel = 1000)
    await arm_vertical()
    show_elapsed_time()


# Starting facing bucket
# ends up backed away from raising roof; facing SE
async def raise_roof():
    info_msg("Raise roof. Starting from bucket.")
    await arm_vertical()
    # await drive_distance(2, speed = 20)
    await turn_left(140, speed = 15)
    # await drive_distance(-1)

    info_msg("Pushing against bottom bar")
    await arm_down(35, speed = 60)
    await arm_down(24, speed = 10)
    await drive_distance(15, speed = 45, decel = 1000)
    # Raise arm further
    # await drive_distance(-2, speed = 50)
    await arm_up(60, speed = 45)
    await drive_distance(12, speed = 50, decel = 2000)
    # await drive_distance(5, speed = -10)
    # await arm_up(70, speed = 20)
    # await drive_distance(15, speed = 20)
    # Back away
    await drive_distance(-23, speed = 50, accel = 2000, decel = 2000)
    await arm_vertical()
    show_elapsed_time()


# Drive from raising roof to back wall for alignment
# Starting facing raise roof at about 135 degree angle
# End up facing south approximately on black square
async def roof_to_back_wall():
    info_msg("Roof to back wall")
    await arm_vertical()
    await turn_right(177, speed = 25)# was speed 10
    await drive_distance(25, speed= -50, accel = 2000, decel = 1000)
    await update_yaw(179)
    show_elapsed_time()



# Drive to statue tail and hit it
# End up behind statue, in position so one can turn left
# towards mineshaft
async def back_wall_to_statue_tail():
    info_msg("Back wall to statue tail")
    # approach statue tail directly from behind
    await drive_distance(6, speed = 40, accel = 2000, decel = 2000)
    await turn_right(220, speed = 25)
    # Drive to back of statue
    await gyro_straight(tgDeg = 220, speed = 55, dist = 34)
    # Push down tail and pull back
    await arm_down(20, speed = 65)
    await drive_distance(2, speed = -10, decel = 1000)
    await arm_down(18, speed = 65)
    await drive_distance(10, speed = -20, decel = 3000)
    await arm_vertical()
    show_elapsed_time()

async def test_wall_to_statue():
    await boot_robot()
    await update_yaw(179)
    await back_wall_to_statue_tail()
    await statue_tail_to_indy()


# Ends with arm down facing Indy target
async def statue_tail_to_indy():
    info_msg("Driving Statue Tail to Mineshaft")
    # Drive south -> west
    # await drive_distance(10, speed= 80)
    await turn_right(270, speed = 25)
    # is that sufficiently precise?
    await drive_distance(19, speed = 50, accel = 2000, decel = 2000)
    # await gyro_straight(tgDeg = 270, speed = 45, dist = 18)
    await turn_left(240, speed = 30)
    await drive_distance(16, speed = 50, accel = 2000, decel = 2000)
    # await gyro_straight(tgDeg = 250, speed = 35, dist = 14)
    # Turn north
    await arm_down(45, speed = 40)
    await turn_right(280, speed = 30)
    await arm_down(22, speed = 40)
    await turn_right(355, speed = 20)
    show_elapsed_time()


async def indy_action():
    info_msg("Indy action")
    # Align against mission model to get distance right
    await drive_distance(8, speed = 20, accel = 1000, decel = 1000)
    # Back up
    await drive_distance(5, speed = -20, accel = 1000, decel = 1000)
    # Raise arm and let mine cart roll off
    await arm_up(110, speed = 15)
    # await drive_distance(3)
    # await arm_up(160, speed = 10)
    # Give the mine cart time to roll
    # await drive_distance(2, speed = 10, accel = 1000, decel = 1000)
    # await arm_up(140, speed = 10)
    await runloop.sleep_ms(300)
    # await arm_vertical()
    # await drive_distance(5, speed = -20, accel = 3000, decel = 3000)# was default accel11/13/2025
    show_elapsed_time()

async def test_indy():
    await boot_robot()
    await update_yaw(140)
    await roof_to_back_wall()
    await back_wall_to_statue_tail()
    await statue_tail_to_indy()
    await indy_action()
    # await statue_start()

async def indy_to_left():
    info_msg("Indy to left")
    await turn_left(290, speed = 30)
    await drive_distance(37, speed = 95, accel= 3000, decel= 3000)
    await turn_left(190, speed = 30)
    await drive_distance(65, speed = 95, accel = 3000, decel= 3000)
    show_elapsed_time()

async def test_indy_to_left():
    await boot_robot()
    await indy_to_left()


# Run the complete mission, starting from right start box.
# Robot set up so one can drive straight to TR line.
async def run_from_right():
    info_msg("Starting run from right start box")
    await right_start_2_bucket()
    await bucket_action()
    await raise_roof()
    await roof_to_back_wall()
    await back_wall_to_statue_tail()
    await statue_tail_to_indy()
    await indy_action()
    await indy_to_left()
    sys.exit()# added so that stop button need not be pressed at the end11/13/2025


# --------------------Silo Mission--------------------------
# Silo and 3 targets on NE side of table.
# Start from position where silo can be struck without driving
# Return home at the end
async def silo_mission():
    await boot_robot()
    info_msg("Silo Mission start")
    await silo_action()
    await silo_to_tr_line()
    await heavy_lifting_action()
    await home_from_heavy_lifting()
    show_elapsed_time()
    sys.exit()


async def silo_action():
    info_msg("Silo action (no driving)")
    for j in range(3):
        await arm_up(170, speed = 70)
        await runloop.sleep_ms(50)
        await arm_down(65, speed = 85)
    await arm_vertical()
    show_elapsed_time()


async def test_silo_action():
    info_msg("Test Silo Action")
    await boot_robot()
    await silo_action()
    sys.exit()



# Drive to top right line. For heavy lifting mission.
# Start from due south of tr line in right start box
# Be clear about how far from south wall we start +++
# async def straight_to_tr_line():
#    info_msg("Drive straight north to TR line.")
#    await update_yaw(0)
#    await arm_vertical()
#    await gyro_straight(tgDeg = 0, dist = 35, speed = 80)
#    # Align on top-right line
#    line_finder(RIGHT, BLACK, speed = 10)
#    line_align(BLACK)
#    await update_current_pos(TOP_RIGHT_LINE)
#    show_elapsed_time()


# Drive from Silo (right start box) to TR line.
async def silo_to_tr_line():
    info_msg("Driving Silo to TR line")
    # Drive to west of Silo
    await drive_distance(20, speed= 60, accel= 2000, decel= 2000)
    # Drive diagnonally around Silo
    await turn_left(310, speed = 15)
    await drive_distance(20, speed = 60, accel= 1000, decel= 1000)
    # Drive north
    await gyro_straight(tgDeg = 0, dist = 20, speed = 40)
    # await turn_right(35, speed = 10)
    # await gyro_straight(tgDeg= 30, dist= 10, speed = 40)
    # Pull away from TR line for alignment
    await turn_right(30, speed = 15)
    # await drive_distance(10, speed = -20)
    # Align on TR line
    line_finder(RIGHT, BLACK)
    line_align(BLACK)
    await update_current_pos(TOP_RIGHT_LINE)
    show_elapsed_time()

async def test_silo_to_trline():
    await boot_robot()
    info_msg("Testing Silo to TR line")
    await silo_to_tr_line()
    show_elapsed_time()
    sys.exit()


# Heavy lifting from TR line.
# Also does balldrop and table action in one movement.
async def heavy_lifting_action():
    info_msg("Heavy lifting action")
    await update_current_pos(TOP_RIGHT_LINE)
    await turn_to_degrees(41)
    # Pull back and lower arm
    # Arm comes to rest on back of balldrop model
    await drive_distance(7, speed = -30, accel = 800, decel = 800)
    await arm_down(75, speed= 20)
    # Push arm through loop of heavy lifting
    # Bot stops when it runs into model
    await drive_distance(3, speed = 20, accel = 500, decel = 500)
    # Pick up ring
    # await arm_up(175, speed= 20)

    # Try push right then left
    await turn_right(80, speed = 35)
    await arm_down(65, speed = 30)
    await arm_up(95, speed = 30)
    await runloop.sleep_ms(200)
    await turn_left(10, speed = 30)
    await runloop.sleep_ms(200)
    # Back up so arm can be raised
    await drive_distance(3, speed = -20)
    # await turn_right(20, speed = 20)
    # await runloop.sleep_ms(200)
    # await turn_right(70, speed = 10)

    info_msg("Table action")
    await arm_up(180, speed = 25)
    await turn_left(2, speed= 20)
    await drive_distance(12, speed= 20)
    await turn_left(310, speed= 20)
    await drive_distance(2, speed= -70, accel = 2000, decel = 2000)
    # await turn_left(10, speed= 20)
    # await arm_down(70)
    # # await drive_distance(2, -20)
    # # await drive_distance(5, speed= 10)
    # await turn_left(270)

    # Plan: try to push ring and balls at same time
    # - align slightly to right of ring
    # - take out picking up action

    # Bring arm back down on back of mission model
    # await drive_distance(4, speed = -20)
    # await arm_down(80, speed = 15)
    # # Push lever left for balldrop
    # await drive_distance(6, speed = 10)
    # await turn_left(15, speed = 10)
    # await arm_up(180, speed = 20)
    show_elapsed_time()

async def test_heavy_lifting_action():
    info_msg("Testing Heavy Lifting Action. Starting from TR line")
    await boot_robot()
    await update_current_pos(TOP_RIGHT_LINE)
    await heavy_lifting_action()
    await home_from_heavy_lifting()
    show_elapsed_time()
    sys.exit()


# Drive home after heavy lifting.
# Starting facing balldrop. Pulled back about 10 cm.
async def home_from_heavy_lifting():
    info_msg("Home from heavy lifting")
    await arm_vertical()
    await turn_to_degrees(355)
    # await gyro_straight(tgDeg = 355, speed = -100, dist = 65)
    await drive_distance(80, speed = -100, accel = 3000, decel = 2000)
    show_elapsed_time()



# -----------------Main------------------------

async def mission_right():
    await boot_robot()
    await run_from_right()
    sys.exit()


# Exploratory code
async def main():
    global RIGHT, BLACK
    await boot_robot()
    await arm_down(20, speed= 10)
    info_msg("Exiting")
    sys.exit()


# runloop.run(main())

# runloop.run(test_silo_action())
# runloop.run(test_heavy_lifting_action())

# Slot 0
runloop.run(silo_mission())

# Slot 1
# runloop.run(mission_right())


# -----------------------------------------