import os
print "## settings: "+os.path.basename(__file__)+" ##"

DOTSIZE = 1.5
TRANSITION_DOTSIZE = 5
LEFT_STEPPER_POS = (0.0,0.0)
RIGHT_STEPPER_POS = (2915.0,0.0)
CANVAS_SIZE = (1060,1060)
PADDING = 300
LINE_SPACING = 12.5 * (1060.0/1500.0)
CURVED_ITERATIONS = int(round(250 / (1060.0/1500.0)))
STRAIGHT_ITERATIONS = int(round(150 / (1060.0/1500.0)))
LINE_ALPHA = 255

STEPS_PER_MM_PREVIEW = 2.5 
STEPS_PER_MM = 42.5532
Z_STEPS_PER_MM = 2 

###### globals #####
g_Offset = (RIGHT_STEPPER_POS[0] - CANVAS_SIZE[0]) / 2
g_MachineWidth = int(RIGHT_STEPPER_POS[0])
#g_NullPosition = lengthFromPos(750,750)
g_NullPosition = (1580,1580)