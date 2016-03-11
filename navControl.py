# Author: Neil MacGregor
# Date: Mar 6, 2016
# Purpose: A rewrite of existing code, going OO
import logging
#import sys
import time
import random
import math

from Adafruit_BNO055 import BNO055

from Adafruit_MotorHAT import Adafruit_MotorHAT, Adafruit_DCMotor

import time
import atexit
import calendar
import json


class navControl: 
   'General navigation: waypoints, object detection and mitigation, and strategy'
   # class variables go here

   def __init__(self):
      # create an object for communication with the DC motor hat, no changes to default I2C address or frequency
      self.mh = Adafruit_MotorHAT(addr=0x60)

      # This is a file which holds BNO sensor calibration
      self.CALIBRATION_FILE='calibration.json'

      # Create and configure the BNO sensor connection.  Raspberry Pi configuration with serial UART and RST connected to GPIO 18:
      self.bno = BNO055.BNO055(serial_port='/dev/ttyAMA0', rst=18)

      # It's important that we ensure motors are always turned off, here at the start!  The DCMotor hat doesn't have a 
      # watchdog, and will merely keep driving as long as the power is on!
      self.turnOffMotors()

      # Initialize the BNO055 and stop if something went wrong.
      if not self.bno.begin():
          raise RuntimeError('Failed to initialize BNO055! Is the sensor connected?')

      # Print system status and self test result.
      status, self_test, error = self.bno.get_system_status()
      print('System status: {0}'.format(status))
      print('Self test result (0x0F is normal): 0x{0:02X}'.format(self_test))
      # Print out an error if system status is in error mode.
      if status == 0x01:
          print('System error: {0}'.format(error))
          print('See datasheet section 4.3.59 for the meaning.')

      # Print BNO055 software revision and other diagnostic data.
      sw, bl, accel, mag, gyro = self.bno.get_revision()
      print('Software version:   {0}'.format(sw))
      print('Bootloader version: {0}'.format(bl))
      print('Accelerometer ID:   0x{0:02X}'.format(accel))
      print('Magnetometer ID:    0x{0:02X}'.format(mag))
      print('Gyroscope ID:       0x{0:02X}\n'.format(gyro))

      print('Reading BNO055 data, press Ctrl-C to quit...')

      if self.load_calibration():
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
            time.sleep(1)

      if loaded_cal==1:
         save_calibration()

      print "\nCalibration complete!\n"

   def turnOffMotors(self):
      # Ensure that motors are turned off, on shutdown!
      self.mh.getMotor(1).run(Adafruit_MotorHAT.RELEASE)
      self.mh.getMotor(2).run(Adafruit_MotorHAT.RELEASE)
      self.mh.getMotor(3).run(Adafruit_MotorHAT.RELEASE)
      self.mh.getMotor(4).run(Adafruit_MotorHAT.RELEASE)

      atexit.register(self.turnOffMotors)

   def save_calibration(self):
      # Save calibration data to disk.
      # First grab the lock on BNO sensor access to make sure nothing else is
      # writing to the sensor right now.
      data = self.bno.get_calibration()
      # Write the calibration to disk.
      with open(self.CALIBRATION_FILE, 'w') as cal_file:
          json.dump(data, cal_file)
      return 'OK'

   def load_calibration(self):
      # Load calibration from disk.
      with open(self.CALIBRATION_FILE, 'r') as cal_file:
          data = json.load(cal_file)
      # Use stored calibration data 
      self.bno.set_calibration(data)
      return 'OK'


   def startDrive(self):

      ################################# DC motor test!
      RightMotor = self.mh.getMotor(1)  # orange track... Right!
      LeftMotor  = self.mh.getMotor(2)  # blue track... Left!

      speed=155
      fwdTrim=10
      bkwFactor=2
      adjustRate=2

      print "Forward! "
      # before we start moving, note our heading...
      initialHeading, roll, pitch = self.bno.read_euler()

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
         heading, roll, pitch = self.bno.read_euler()
         print 'Current Heading: {0:0.2F}, current time: {1:5d}, leftSpeed={2:3d} rightSpeed={3:3d}'.format(heading,currentTime,leftSpeed,rightSpeed) 
	 #if (adjustHeading(initialHeading) == "turnRight"):
         if (heading<initialHeading):           # we're tracking left, either slow the right, or speed up the left
            flip = random.randint(0, 1)
            if flip == 0:
               leftSpeed=leftSpeed+adjustRate
	       LeftMotor.setSpeed(leftSpeed)
            else:
               rightSpeed=rightSpeed-adjustRate		   
               RightMotor.setSpeed(rightSpeed)
	 #if (adjustHeading(initialHeading) == "turnLeft"):
         if (heading>initialHeading): 	   # we're tracking clockwise, slow the left track
            flip = random.randint(0, 1)
            if flip == 0:
               rightSpeed=rightSpeed+adjustRate
               RightMotor.setSpeed(rightSpeed)
            else:
               leftSpeed=leftSpeed-adjustRate
               LeftMotor.setSpeed(leftSpeed)
         x,y,z,w = self.bno.read_quaternion()
         print ('Quaternion: x={0:0.2F} y={1:0.2F} z={2:0.2F} w={3:0.2F}\t'.format(x, y, z, w))
         time.sleep(0.1)   

      print "Stop, done"
      LeftMotor.run(Adafruit_MotorHAT.RELEASE)
      RightMotor.run(Adafruit_MotorHAT.RELEASE)


   def adjustHeading(self, targetHeading):
      # Tricky: compare the current compass heading, to a target heading, and decide if we're tracking to the left or right of target
      # It's fine if the target it 90deg, and the current heading is 100, that's easy, turn left (100 > 90)
      # But if the target is 350deg, and the current heading is 5deg, the math goes sideways!

      # We need a function that makes this true:  350 < 360 < 10  (eg target is 360)
      # and:  355 < 10 < 15   (when the target is 10) 

      # sin()?  cos()?  I merely want to know am I left or right from the target?
      # (pretty sure this is wrong)
      targetHeading = math.sin(targetHeading)
      currentHeading=self.getHeading()
      currentHeading=math.sin(currentHeading)

      if currentHeading < targetHeading:
         return "turnRight"
      else:
         return "turnLeft"

   # local interface, simplifying use of the BNO055 IMU circuit board, for yaw heading, measured in degrees
   def getHeading(self):
      currentHeading, roll, pitch = self.bno.read_euler()
      print ('got Heading: {0:0.2F}'.format(currentHeading))
      return currentHeading
