import math

def Sigmoid(Value):    
    return 1.0/(1.0+math.exp(-float(Value)))

enddelay = 2000.0
begindelay = 20000.0
numsteps = 40.0

delta = (begindelay-enddelay)

print delta

vals = []
for p in range(int(round(numsteps))):
    inp = (p-(numsteps/2.0))/ (numsteps/12.0)
    print inp
    outp = Sigmoid(inp);
    print outp
    ease = (outp * delta) + enddelay
    ease = int(round( ease))
    vals.append(ease)

vals.reverse()
vals.append(int(enddelay))
print "SIGMOID - IN-OUT"
print vals
print len(vals)

for v in vals:
	print int(round(v/200))*"*"

vals = []
for p in range(int(round(numsteps))):
    ease = (p * (delta/numsteps)) + enddelay
    ease = int(round( ease))
    vals.append(ease)

vals.reverse()
vals.append(int(enddelay))
print "LINEAR"
print vals
print len(vals)

for v in vals:
	print int(round(v/200))*"*"
