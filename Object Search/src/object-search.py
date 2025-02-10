'''
This code demonstrates a basic search and drive towards behaviour with the camera.

The robot has three states:
    IDLE - waiting for the button press
    SEARCHING - spins slowly until it finds an object
    APPROACHING - drives towards the object

Camera checking is done on a timer. If no object is found, a counter is incremented and
if the counter reaches a threshold, the robot goes back into searching mode.
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

Vision__ORANGE_PEEL = Signature (1, 3271, 5567, 4419, -3011, -1697, -2354, 0.7, 0)


Vision19 = Vision (Ports.PORT19, 50)

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

        ## start the timer for the camera
        cameraTimer.event(cameraTimerCallback, 50)

    else: ## failsafe; go to IDLE from any other state when button is pressed
        print(' -> IDLE')
        current_state = ROBOT_IDLE
        left_motor.stop()
        right_motor.stop()

button.pressed(handleButton)

'''
We'll keep track of missed detections. If it exceeds some threshold, go back to SEARCHING
'''
missedDetections = 0
def handleLostObject():
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

    ## Here we use a checker-handler, where the checker checks if there is a new object detection.
    ## We don't use a "CheckForObjects()" function because take_snapshot() acts as the checker.
    ## It returns a non-empty list if there is a detection.
    objects = Vision19.take_snapshot(Vision__ORANGE_PEEL)
    if objects: handleObjectDetection()
    else: missedDetections = missedDetections + 1

    # restart the timer
    if(current_state != ROBOT_IDLE):
        cameraTimer.event(cameraTimerCallback, 50)


def handleObjectDetection():
    global current_state
    global object_timer
    global missedDetections

    cx = Vision19.largest_object().centerX
    cy = Vision19.largest_object().centerY

    ## TODO: Add code to print out the coordinates and size


    if current_state == ROBOT_SEARCHING:
        print('SEARCHING -> APPROACHING') ## Pro-tip: print out state _transitions_
        current_state = ROBOT_APPROACHING

    ## Not elif, because we want the logic to cascade
    if current_state == ROBOT_APPROACHING:

        target_x = 160
        K_x = 0.5

        error = cx - target_x
        turn_effort = K_x * error


        ## TODO: Edit code to approach or back up to hold the right position
        left_motor.spin(REVERSE, 10 + turn_effort)
        right_motor.spin(REVERSE, 10 - turn_effort)

    ## reset the time out timer
    missedDetections = 0

def checkForLostObject():
    ## this is not a "proper" event checker -- need to be reasonable
    if(missedDetections > 20): return True
    else: return False

## Our main loop
while True:
    ## if enough cycles have passed without a detection, we've lost the object
    if(checkForLostObject()): handleLostObject()
