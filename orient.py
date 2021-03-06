#!/usr/bin/python
# Author: Neil MacGregor
# Date: Mar 6, 2016
# Purpose: orient.py is an effort to understand the magnetometer reading, and euler calls
# This is an exercise in calibration & tuning
# Let's start with something simple: can we turn this sucker 90 degrees clockwise with any degree of accuracy?
#
# I learned about python exception handling & return codes, so that's good.  This informed improvements in handling calibration. 
# That is, even if you loaded calibration from a file, that might not apply in the current building or physical location, and you 
# might want to try re-calibrating.   I don't try to pretend I understand the values in the calibration.json, but I see considerable
# variance among them, when I run multiple calibration runs & compare them.  
# I also learned that unless you wait at least 5 seconds after *applying* a calibration from a file, you might get utter garbage
# in terms of absolute compass positioning.  So, begin driving, sure, but be prepared for a *wild* compass swing, after you get
# underway!
# In general, I found that it is possible to turn approximately 90 degrees.  One factor not working in our favour, is the relatively 
# high minimum speed required to get the tracks to spin.  There's a high initial torque resistance to overcome: need sorta 120
# out of 255 just to get 'er rolling, and sometimes even that's not enough!  (And, we're makin' 9V, I think.) For finer-grained 
# control, consider spinning just one track, not both!.
# I need to spend a minute thinking about the mathematical concept of spinning 90 degrees from 300 degrees, implies spinning until we 
# hit 30 degrees, which is the target.
# I also learned that in the final analysis perhaps I ought to mount the IMU circuit board 180 degrees from the initial install, 
# because North is pointing out the tail of the beast!

# 
# This is based on the Adafruit examples for the BNO055, and the DC Motor Hat.
import logging
import sys
import time
import random

from Adafruit_BNO055 import BNO055

from Adafruit_MotorHAT import Adafruit_MotorHAT, Adafruit_DCMotor

import time
import atexit
import calendar
import json

# create a default object, no changes to I2C address or frequency
mh = Adafruit_MotorHAT(addr=0x60)

# recommended for auto-disabling motors on shutdown!
def turnOffMotors():
	mh.getMotor(1).run(Adafruit_MotorHAT.RELEASE)
	mh.getMotor(2).run(Adafruit_MotorHAT.RELEASE)
	mh.getMotor(3).run(Adafruit_MotorHAT.RELEASE)
	mh.getMotor(4).run(Adafruit_MotorHAT.RELEASE)

atexit.register(turnOffMotors)

CALIBRATION_FILE='calibration.json'
def save_calibration():
    # Save calibration data to disk.
    # First grab the lock on BNO sensor access to make sure nothing else is
    # writing to the sensor right now.
    data = bno.get_calibration()
    # Write the calibration to disk.
    with open(CALIBRATION_FILE, 'w') as cal_file:
        json.dump(data, cal_file)
    return 'OK'

def load_calibration():
    # Load calibration from disk.
    try:
        with open(CALIBRATION_FILE, 'r') as cal_file:
           data = json.load(cal_file)
    except IOError:
  	   print "Unable to load calibration file, try manual calibration"
           return 'FAIL'
    # Use stored calibration data 
    bno.set_calibration(data)
    return 'OK'

# It's important that we ensure motors are always turned off, here at the start!  The PWM card doesn't have a 
# watchdog, and will merely keep driving as long as the power is on!
turnOffMotors()

# Create and configure the BNO sensor connection.  Make sure only ONE of the
# below 'bno = ...' lines is uncommented:
# Raspberry Pi configuration with serial UART and RST connected to GPIO 18:
bno = BNO055.BNO055(serial_port='/dev/ttyAMA0', rst=18)
# BeagleBone Black configuration with default I2C connection (SCL=P9_19, SDA=P9_20),
# and RST connected to pin P9_12:
#bno = BNO055.BNO055(rst='P9_12')


# Enable verbose debug logging if -v is passed as a parameter.
if len(sys.argv) == 2 and sys.argv[1].lower() == '-v':
    logging.basicConfig(level=logging.DEBUG)

# Initialize the BNO055 and stop if something went wrong.
if not bno.begin():
    raise RuntimeError('Failed to initialize BNO055! Is the sensor connected?')

# Print system status and self test result.
status, self_test, error = bno.get_system_status()
print('System status: {0}'.format(status))
print('Self test result (0x0F is normal): 0x{0:02X}'.format(self_test))
# Print out an error if system status is in error mode.
if status == 0x01:
    print('System error: {0}'.format(error))
    print('See datasheet section 4.3.59 for the meaning.')

# Print BNO055 software revision and other diagnostic data.
sw, bl, accel, mag, gyro = bno.get_revision()
print('Software version:   {0}'.format(sw))
print('Bootloader version: {0}'.format(bl))
print('Accelerometer ID:   0x{0:02X}'.format(accel))
print('Magnetometer ID:    0x{0:02X}'.format(mag))
print('Gyroscope ID:       0x{0:02X}\n'.format(gyro))

print('Reading BNO055 data, press Ctrl-C to quit...')

if load_calibration()=="OK":
   print "Successfully loaded calibration from file"
   loaded_cal=0
else:
   loaded_cal=1
   sys=0
   while sys!=3:
      # Read the Euler angles for heading, roll, pitch (all in degrees).
      heading, roll, pitch = bno.read_euler()
      # Read the calibration status, 0=uncalibrated and 3=fully calibrated.
      sys, gyro, accel, mag = bno.get_calibration_status()
      # Print everything out.
      print('Heading={0:0.2F} Roll={1:0.2F} Pitch={2:0.2F}\tSys_cal={3} Gyro_cal={4} Accel_cal={5} Mag_cal={6}'.format(
            heading, roll, pitch, sys, gyro, accel, mag))
      # Other values you can optionally read:
      # Orientation as a quaternion:
      x,y,z,w = bno.read_quaternion()
      #print ('Quaternion: x={0:0.2F} y={1:0.2F} z={2:0.2F} w={3:0.2F}\t'.format(x, y, z, w))
      #print ('Quaternion: x= {0:0.2F} y={1:0.2F} z={2:0.2F},\t'.format(x,y,z))
      # Sensor temperature in degrees Celsius:
      #temp_c = bno.read_temp()
      #print ('Temperature={0:0.2F}'.format(temp_c))
      # Magnetometer data (in micro-Teslas):
      #x,y,z = bno.read_magnetometer()
      # Gyroscope data (in degrees per second):
      #x,y,z = bno.read_gyroscope()
      # Accelerometer data (in meters per second squared):
      #x,y,z = bno.read_accelerometer()
      # Linear acceleration data (i.e. acceleration from movement, not gravity--
      # returned in meters per second squared):
      #x,y,z = bno.read_linear_acceleration()
      # Gravity acceleration data (i.e. acceleration just from gravity--returned
      # in meters per second squared):
      #x,y,z = bno.read_gravity()
      # Sleep for a second until the next reading.
      time.sleep(1)

if loaded_cal==1:
   save_calibration()

# Let's check that
# Read the calibration status, 0=uncalibrated and 3=fully calibrated.
sys, gyro, accel, mag = bno.get_calibration_status()
if sys!=3 and loaded_cal==0:
   print "Sorry, loaded calibration from file, but status says we're not fully calibrated";
   exit

print "\nCalibration complete!  Please put me down...\n"
time.sleep(5)
################################# DC motor test!
RightMotor = mh.getMotor(1)  # orange track... Right!
LeftMotor  = mh.getMotor(2)  # blue track... Left!

# set the speed to start, from 0 (off) to 255 (max speed)
LeftMotor.setSpeed(200)
RightMotor.setSpeed(225)
#
#LeftMotor.run(Adafruit_MotorHAT.FORWARD);
#RightMotor.run(Adafruit_MotorHAT.FORWARD);

speed=130

print "Rotating! "
# before we start moving, note our heading...
initialHeading, roll, pitch = bno.read_euler()
targetHeading=initialHeading+90
if targetHeading> 360:
   targetHeading=targetHeading-360

# initialize timestamps
startTime=calendar.timegm(time.gmtime())	
currentTime=calendar.timegm(time.gmtime())
print 'Initial Heading: {0:0.2F}, start time:{1:5d}'.format(initialHeading,startTime) 

# set initial motor speed
LeftMotor.setSpeed(speed)
RightMotor.setSpeed(speed)


# start us rotating
LeftMotor.run(Adafruit_MotorHAT.FORWARD)
RightMotor.run(Adafruit_MotorHAT.BACKWARD)
# get the current time; limit the amount of time for which we'll run 
while startTime+10 > currentTime:
   currentTime=calendar.timegm(time.gmtime())
   heading, roll, pitch = bno.read_euler()
   print 'Underway, Current Heading: {0:0.2F}, current time: {1:5d}'.format(heading,currentTime) 
   if targetHeading < 90:
      if heading > 270:
         print "Continuing past 360 degrees.."
	 next
      elif (heading>targetHeading):           # stop!
         LeftMotor.run(Adafruit_MotorHAT.RELEASE)
         RightMotor.run(Adafruit_MotorHAT.RELEASE)
         break
   elif (heading>targetHeading): 	   # stop!
      LeftMotor.run(Adafruit_MotorHAT.RELEASE)
      RightMotor.run(Adafruit_MotorHAT.RELEASE)
      break
   #x,y,z,w = bno.read_quaternion()
   #print ('Quaternion: x={0:0.2F} y={1:0.2F} z={2:0.2F} w={3:0.2F}\t'.format(x, y, z, w))
   time.sleep(0.05)   

print "Stop, done"
LeftMotor.run(Adafruit_MotorHAT.RELEASE)
RightMotor.run(Adafruit_MotorHAT.RELEASE)
heading, roll, pitch = bno.read_euler()
print 'Target Heading: {0:0.2F}, final heading:{1:0.2F}'.format(targetHeading,heading) 
