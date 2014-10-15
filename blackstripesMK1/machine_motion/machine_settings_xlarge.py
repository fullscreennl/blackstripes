import os
print "## settings: "+os.path.basename(__file__)+" ##"

DOTSIZE = 1.5
TRANSITION_DOTSIZE = 5
LEFT_STEPPER_POS = (0.0,0.0)
RIGHT_STEPPER_POS = (2915.0,0.0)
CANVAS_SIZE = (1500,1500)
PADDING = 300
LINE_SPACING = 12.5 * (1000.0/1500.0)
CURVED_ITERATIONS = 825
STRAIGHT_ITERATIONS = 250
LINE_ALPHA = 255

STEPS_PER_MM_PREVIEW = 2.5 
STEPS_PER_MM = 42.5532
Z_STEPS_PER_MM = 2 

###### globals #####
g_Offset = (RIGHT_STEPPER_POS[0] - CANVAS_SIZE[0])
g_MachineWidth = int(RIGHT_STEPPER_POS[0])
#g_NullPosition = lengthFromPos(750,750)
g_NullPosition = (1580,1580)