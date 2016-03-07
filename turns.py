#!/usr/bin/python
from Adafruit_MotorHAT import Adafruit_MotorHAT, Adafruit_DCMotor

import time
import atexit

# create a default object, no changes to I2C address or frequency
mh = Adafruit_MotorHAT(addr=0x60)

# recommended for auto-disabling motors on shutdown!
def turnOffMotors():
	mh.getMotor(1).run(Adafruit_MotorHAT.RELEASE)
	mh.getMotor(2).run(Adafruit_MotorHAT.RELEASE)
	mh.getMotor(3).run(Adafruit_MotorHAT.RELEASE)
	mh.getMotor(4).run(Adafruit_MotorHAT.RELEASE)

atexit.register(turnOffMotors)

################################# DC motor test!
# select which motor...
LeftMotor  = mh.getMotor(1)  # blue track... Left!
RightMotor = mh.getMotor(2)  # orange track... Right!

# set the speed to start, from 0 (off) to 255 (max speed)
LeftMotor.setSpeed(200)
RightMotor.setSpeed(225)
#
LeftMotor.run(Adafruit_MotorHAT.FORWARD);
RightMotor.run(Adafruit_MotorHAT.FORWARD);
# turn on motor
LeftMotor.run(Adafruit_MotorHAT.RELEASE);
RightMotor.run(Adafruit_MotorHAT.RELEASE);

speed=150
LeftMotor.setSpeed(speed)
RightMotor.setSpeed(speed)

# There is a problem with motor speed: when moving forward, RH track turns faster, & we turn left. 
# And when we go backwards, the LH track turns faster, & we turn the same direction. 


print "Left! "
LeftMotor.run(Adafruit_MotorHAT.BACKWARD)
RightMotor.run(Adafruit_MotorHAT.FORWARD)
time.sleep(3.0)

print "Stop a moment... "
LeftMotor.run(Adafruit_MotorHAT.RELEASE)
RightMotor.run(Adafruit_MotorHAT.RELEASE)
time.sleep(0.5)

print "Right! "
LeftMotor.run(Adafruit_MotorHAT.FORWARD)
RightMotor.run(Adafruit_MotorHAT.BACKWARD)
time.sleep(3.0)

print "Release"
LeftMotor.run(Adafruit_MotorHAT.RELEASE)
RightMotor.run(Adafruit_MotorHAT.RELEASE)
time.sleep(1.0)
