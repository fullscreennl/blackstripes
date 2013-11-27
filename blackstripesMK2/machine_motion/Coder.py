import struct
import os

def encode(left_engine=0, right_engine=0,p1=0,p2=0,p3=0,even=0,speed=0):
    enc = 0 << 31
    enc = enc | (left_engine << 29)
    enc = enc | (right_engine << 27)
    enc = enc | (p1 << 25)
    enc = enc | (p2 << 23)
    enc = enc | (p3 << 21)
    enc = enc | (even << 19)
    enc = enc | speed
    return enc
    
def decode(data):

    mask =          0b1100000000000000000000000000000
    speed_mask =    0b0000000000000000000000111111111
    
    #print "mask ",mask
    #print "speed_mask ",speed_mask

    left_engine = (data & mask) >> 29
    right_engine = (data & mask >> 2) >> 27
    p1 = (data & mask >> 4) >> 25
    p2 = (data & mask >> 6) >> 23
    p3 = (data & mask >> 8) >> 21
    even = (data & mask >> 10) >> 19
    speed = (data & speed_mask)
    return (left_engine, right_engine,p1,p2,p3,even,speed)

    

if __name__ == "__main__":
    pass

