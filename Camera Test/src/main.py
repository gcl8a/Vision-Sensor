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

    else: ## failsafe; go to IDLE from any other state
        print(' -> IDLE')
        current_state = ROBOT_IDLE
        left_motor.stop()
        right_motor.stop()

button.pressed(handleButton)


target_x = 160
K_x = 0.5

last_detection = 0
objectTimer = Timer()
def objectTimerCallback():
    global current_state

    print('timer expired ')
    if current_state == ROBOT_APPROACHING:
        print('APPROACHING -> SEARCHING') ## Pro-tip: print out state _transitions_
        current_state = ROBOT_SEARCHING
        left_motor.spin(FORWARD, 30)
        right_motor.spin(FORWARD, -30)


def handleObjectDetection():
    global current_state
    global object_timer
    global last_detection

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
    last_detection = objectTimer.value()


def checkObjectTimerExpired():
    if(objectTimer.value() - last_detection > 2):
        return True
    else:
        return False


## Our main loop
while True:
    ## Here we use a checker-handler, where the checker is looking to see if there is a new object detection
    ## We don't use a "CheckForObjects()" function because take_snapshot acts in that capacity.
    ## It returns a non-empty list if there is a detection
    objects = Vision3.take_snapshot(Vision3__RED_TSHIRT)
    if objects: handleObjectDetection()

    ## a checker to see if one second has passed since the last detection
    if(checkObjectTimerExpired()): objectTimerCallback()
           
    ## for sanity, sleep before we check again
    sleep(50)
