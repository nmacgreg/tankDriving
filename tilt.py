#!/usr/bin/python
# This doesn't work yet.  Just a bit of fooling around, trying to get a feeling for servo code...

from Adafruit_PWM_Servo_Driver import PWM


# Initialise the PWM device using the default address
pwm = PWM(0x40)
panAndTilt(350,300)



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
