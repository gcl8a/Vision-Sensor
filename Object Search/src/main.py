'''
This code demonstrates a basic search and drive towards behaviour with the camera.

The robot has three states:
    IDLE - waiting for the button press
    SEARCHING - spins slowly until it finds an object
    APPROACHING - drives towards the object
'''

# Library imports
from vex import *

# Brain should be defined by default
brain = Brain()

## Define states and state variable
ROBOT_IDLE = 0
ROBOT_SEARCHING = 1
ROBOT_APPROACHING = 2

current_state = ROBOT_IDLE

# Define the motors
left_motor = Motor(Ports.PORT1, GearSetting.RATIO_18_1, False)
right_motor = Motor(Ports.PORT10, GearSetting.RATIO_18_1, True)


## Define the camera (vision)
## Note that we define the signatures first and then pass them to the Vision constructor --
## I don't know if that is truly needed or not
Vision3__RED_TSHIRT = Signature (1, 11131, 11623, 11377, -1223, -731, -977, 8.8, 0)
Vision3__SEAFOAM_TSHIRT = Signature (2, -2251, -1827, -2039, 2299, 2997, 2648, 3.7, 0)
Vision3 = Vision (Ports.PORT19, 72, Vision3__RED_TSHIRT, Vision3__SEAFOAM_TSHIRT)

'''
The button (bumper) makes use of the built-in event system.
'''
button = Bumper(brain.three_wire_port.g)

def handleButton():
    global current_state

    if(current_state == ROBOT_IDLE):
        print('IDLE -> SEARCHING') ## Pro-tip: print out state _transitions_
        current_state = ROBOT_SEARCHING
        left_motor.spin(FORWARD, 30)
        right_motor.spin(FORWARD, -30)
        cameraTimer.event(cameraTimerCallback, 50)


    else: ## failsafe; go to IDLE from any other state
        print(' -> IDLE')
        current_state = ROBOT_IDLE
        left_motor.stop()
        right_motor.stop()
        cameraTimer.reset()

button.pressed(handleButton)

target_x = 160
K_x = 0.5

'''
We'll keep track of missed detections. If it exceeds some threshold, go back to SEARCHING
'''
missedDetections = 0
def handleMissedDetections():
    global current_state
    if current_state == ROBOT_APPROACHING:
        print('APPROACHING -> SEARCHING') ## Pro-tip: print out state _transitions_
        current_state = ROBOT_SEARCHING
        left_motor.spin(FORWARD, 30)
        right_motor.spin(FORWARD, -30)

'''
We'll use a timer to read the camera every cameraInterval milliseconds
'''
cameraInterval = 50
cameraTimer = Timer()

def cameraTimerCallback():
    global current_state
    global missedDetections

    print("camera")

    ## Here we use a checker-handler, where the checker is looking to see if there is a new object detection
    ## We don't use a "CheckForObjects()" function because take_snapshot acts in that capacity.
    ## It returns a non-empty list if there is a detection
    objects = Vision3.take_snapshot(Vision3__RED_TSHIRT)
    if objects: handleObjectDetection()
    else: missedDetections = missedDetections + 1

    if(missedDetections > 20):
        handleMissedDetections()

    # restart the timer
    if(current_state != ROBOT_IDLE):
        cameraTimer.event(cameraTimerCallback, 50)


def handleObjectDetection():
    global current_state
    global object_timer
    global missedDetections

    cx = Vision3.largest_object().centerX
    cy = Vision3.largest_object().centerY

    if current_state == ROBOT_SEARCHING:
        print('SEARCHING -> APPROACHING') ## Pro-tip: print out state _transitions_
        current_state = ROBOT_APPROACHING

    ## Not elif, because we want the logic to cascade
    if current_state == ROBOT_APPROACHING:
        error = cx - target_x
        turn_effort = K_x * error

        left_motor.spin(REVERSE, 10 + turn_effort)
        right_motor.spin(REVERSE, 10 - turn_effort)

    ## reset the time out timer
    missedDetections = 0

## Our main loop
while True:
    pass