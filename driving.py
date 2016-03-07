# Author: Neil MacGregor
# Date: Mar 5, 2016
# Purpose: Diddling with combining the example code from both the BNO055 & DC Motor Hat. 
# This is an exercise in calibration & tuning
# 1. Get the sensors calibrated.
# 2. Drive a distance *in a straight line*, using (probably) the compass as a directional aide, and 
#    vary the speed of the tracks to keep us in line!
# 3. Spin 180 degrees & come back!
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
    with open(CALIBRATION_FILE, 'r') as cal_file:
        data = json.load(cal_file)
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

if load_calibration():
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

speed=155
fwdTrim=10
bkwFactor=2
adjustRate=2

print "Forward! "
# before we start moving, note our heading...
initialHeading, roll, pitch = bno.read_euler()

# initialize timestamps
startTime=calendar.timegm(time.gmtime())	
currentTime=calendar.timegm(time.gmtime())
print 'Initial Heading: {0:0.2F}, start time:{1:5d}'.format(initialHeading,startTime) 

# set initial motor speed
LeftMotor.setSpeed(speed+fwdTrim)
RightMotor.setSpeed(speed)
rightSpeed=speed+fwdTrim
leftSpeed=speed
range=30

# start us rolling forward
LeftMotor.run(Adafruit_MotorHAT.FORWARD)
RightMotor.run(Adafruit_MotorHAT.FORWARD)
# get the current time; limit the amount of time for which we'll run 
while startTime+10 > currentTime:
   currentTime=calendar.timegm(time.gmtime())
   heading, roll, pitch = bno.read_euler()
   print 'Current Heading: {0:0.2F}, current time: {1:5d}, leftSpeed={2:3d} rightSpeed={3:3d}'.format(heading,currentTime,leftSpeed,rightSpeed) 
   if (heading<initialHeading):           # we're tracking left, either slow the right, or speed up the left
      flip = random.randint(0, 1)
      if flip == 0:
         leftSpeed=leftSpeed+adjustRate
	 LeftMotor.setSpeed(leftSpeed)
      else:
         rightSpeed=rightSpeed-adjustRate		   
         RightMotor.setSpeed(rightSpeed)
   if (heading>initialHeading): 	   # we're tracking clockwise, slow the left track
      flip = random.randint(0, 1)
      if flip == 0:
         rightSpeed=rightSpeed+adjustRate
         RightMotor.setSpeed(rightSpeed)
      else:
         leftSpeed=leftSpeed-adjustRate
         LeftMotor.setSpeed(leftSpeed)
   x,y,z,w = bno.read_quaternion()
   print ('Quaternion: x={0:0.2F} y={1:0.2F} z={2:0.2F} w={3:0.2F}\t'.format(x, y, z, w))
   time.sleep(0.1)   

print "Stop, done"
LeftMotor.run(Adafruit_MotorHAT.RELEASE)
RightMotor.run(Adafruit_MotorHAT.RELEASE)
