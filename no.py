#!/usr/bin/python
import sys
import time
from Adafruit_PWM_Servo_Driver import PWM
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

def panAndTilt(pwm,pan,tilt):

    servoMin = 150  # Min pulse length out of 4096
    servoMax = 600  # Max pulse length out of 4096

    # input validation:
    if pan < servoMin: 
        pan=servoMin
    if pan > servoMax:
        pan = servoMax
    if tilt< servoMin:
        tilt=servoMin
    if tilt> servoMax:
        tilt=servoMax

    pwm.setPWMFreq(60)                        # Set frequency to 60 Hz

    # yes, we're only using the first 2 of 16 channels.  Lotsa room for more fun, later!
    pwm.setPWM(0, 0, tilt)
    pwm.setPWM(1, 0, pan)
      
    return True # maybe we need to examine return codes from pwm.setPWM, no?


# Initialise the PWM device using the default address
pwm = PWM(0x40)


# snap-to
panAndTilt(pwm,350,350)
for counter in range(1,3):
    panAndTilt(pwm,200,350)
    time.sleep(0.25)
    panAndTilt(pwm,500,350)
    time.sleep(0.25)
panAndTilt(pwm,350,350)


