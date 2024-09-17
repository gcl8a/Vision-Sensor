# ---------------------------------------------------------------------------- #
#                                                                              #
# 	Module:       main.py                                                      #
# 	Author:       glewin                                                       #
# 	Created:      9/11/2023, 8:28:37 AM                                        #
# 	Description:  V5 project                                                   #
#                                                                              #
# ---------------------------------------------------------------------------- #

# Library imports
from vex import *

# Brain should be defined by default
brain=Brain()

left_motor = Motor(Ports.PORT1, GearSetting.RATIO_18_1, False)
right_motor = Motor(Ports.PORT10, GearSetting.RATIO_18_1, True)

Vision3__RED_TSHIRT = Signature (1, 11131, 11623, 11377, -1223, -731, -977, 8.8, 0)
Vision3__SEAFOAM_TSHIRT = Signature (2, -2251, -1827, -2039, 2299, 2997, 2648, 3.7, 0)
Vision3 = Vision (Ports.PORT3, 72, Vision3__RED_TSHIRT, Vision3__SEAFOAM_TSHIRT)

brain.screen.print("Hello V5")

ROBOT_IDLE = 0
ROBOT_SEARCHING = 1

state = ROBOT_SEARCHING
left_motor.spin(FORWARD, 30)
right_motor.spin(FORWARD, -30)

target_x = 160

K_x = 0.5

# first center
while True:
    objects = Vision3.take_snapshot(Vision3__RED_TSHIRT)
    
    if objects:
        cx = Vision3.largest_object().centerX
        cy = Vision3.largest_object().centerY

        if state == ROBOT_SEARCHING:

            error = cx - target_x
            turn_effort = K_x * error

            left_motor.spin(REVERSE, turn_effort)
            right_motor.spin(FORWARD, turn_effort)
           
    sleep(20)
