# Author: Neil MacGregor
# Date: Mar 6, 2016
# Purpose: A rewrite of existing code, going OO
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
import logging
#import sys
import random
import math
#import Quaternion
import time
import atexit
import calendar
import json

from Adafruit_BNO055 import BNO055

from Adafruit_MotorHAT import Adafruit_MotorHAT, Adafruit_DCMotor

from Adafruit_PWM_Servo_Driver import PWM


class navControl: 
   'General navigation: waypoints, object detection and mitigation, and strategy'
   # class variables go here
   DEBUG = False

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

      # Initialise the PWM device using the default address
      self.pwm = PWM(0x40)
      self.panAndTilt(350,350)

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

      #if self.DEBUG:  			# use this to force calibration
      if self.load_calibration():
         print "Successfully loaded calibration from file"
         loaded_cal=0
      else:
         loaded_cal=1
         sys=0
         while sys!=3:
            # Read the Euler angles for heading, roll, pitch (all in degrees).
            heading, roll, pitch = self.bno.read_euler()
            # Read the calibration status, 0=uncalibrated and 3=fully calibrated.
            sys, gyro, accel, mag = self.bno.get_calibration_status()
            # Print everything out.
            print('Heading={0:0.2F} Roll={1:0.2F} Pitch={2:0.2F}\tSys_cal={3} Gyro_cal={4} Accel_cal={5} Mag_cal={6}'.format(
                  heading, roll, pitch, sys, gyro, accel, mag))
            # Other values you can optionally read:
            # Orientation as a quaternion:
            #if DEBUG:
               #x,y,z,w = self.bno.read_quaternion()
               #print ('Quaternion: x={0:0.2F} y={1:0.2F} z={2:0.2F} w={3:0.2F}\t'.format(x, y, z, w))
               #print ('Quaternion: x= {0:0.2F} y={1:0.2F} z={2:0.2F},\t'.format(x,y,z))
            time.sleep(1)

      if loaded_cal==1:
         self.save_calibration()

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
      try:
        with open(self.CALIBRATION_FILE, 'r') as cal_file:
           data = json.load(cal_file)
      except IOError:
           print "Unable to load calibration file, try manual calibration"
           return False
      calibrationStatus = self.bno.set_calibration(data)
      return True
      #if calibrationStatus == True:
#	 return True
#      else:
#         return False

   def startDrive(self,initialHeading,duration):

      ################################# DC motor test!
      RightMotor = self.mh.getMotor(1)  # orange track... Right!
      LeftMotor  = self.mh.getMotor(2)  # blue track... Left!

      speed=155
      fwdTrim=5
      bkwFactor=2
      adjustRate=1

      print "Forward! "
      # before we start moving, note our heading...
      #initialHeading, roll, pitch = self.bno.read_euler()

      # initialize timestamps
      startTime=calendar.timegm(time.gmtime())	
      currentTime=calendar.timegm(time.gmtime())
      print 'Target Heading: {0:0.2F}, start time:{1:5d}'.format(initialHeading,startTime) 

      # set initial motor speed
      LeftMotor.setSpeed(speed+fwdTrim)
      RightMotor.setSpeed(speed)
      rightSpeed=speed+fwdTrim
      leftSpeed=speed
      range=30

      # start us rolling forward
      LeftMotor.run(Adafruit_MotorHAT.FORWARD)
      RightMotor.run(Adafruit_MotorHAT.FORWARD)
      self.trackXY()
      # get the current time; limit the amount of time for which we'll run 
      while startTime+duration > currentTime:
         currentTime=calendar.timegm(time.gmtime())
         self.trackXY()
         heading, roll, pitch = self.bno.read_euler()
         if self.DEBUG: 
            print 'Current Heading: {0:0.2F}, current time: {1:5d}, leftSpeed={2:3d} rightSpeed={3:3d}'.format(heading,currentTime,leftSpeed,rightSpeed) 
         #if (heading<initialHeading):           # we're tracking left, either slow the right, or speed up the left
	 if (self.adjustHeading(initialHeading) == "goStraight"):
            next
	 if (self.adjustHeading(initialHeading) == "turnRight"):
            if self.DEBUG:
                print "Turning Right -->"
            flip = random.randint(0, 1)
            if flip == 0:
               leftSpeed=leftSpeed+adjustRate
	       LeftMotor.setSpeed(leftSpeed)
            else:
               rightSpeed=rightSpeed-adjustRate		   
               RightMotor.setSpeed(rightSpeed)
         #if (heading>initialHeading): 	   # we're tracking clockwise, slow the left track
	 if (self.adjustHeading(initialHeading) == "turnLeft"):
            if self.DEBUG:
                print "Turning Left <--"
            flip = random.randint(0, 1)
            if flip == 0:
               rightSpeed=rightSpeed+adjustRate
               RightMotor.setSpeed(rightSpeed)
            else:
               leftSpeed=leftSpeed-adjustRate
               LeftMotor.setSpeed(leftSpeed)
         #if self.DEBUG: 
         #   x,y,z,w = self.bno.read_quaternion()
         #   print ('Quaternion: x={0:0.2F} y={1:0.2F} z={2:0.2F} w={3:0.2F}\t'.format(x, y, z, w))
         time.sleep(0.01)   

      print "Stop, done"
      self.trackXY()
      LeftMotor.run(Adafruit_MotorHAT.RELEASE)
      RightMotor.run(Adafruit_MotorHAT.RELEASE)
      self.trackXY()


   def adjustHeading(self, targetHeading):
      # Tricky: compare the current compass heading, to a target heading, and decide if we're tracking to the left or right of target
      # It's fine if the target it 90deg, and the current heading is 100, that's easy, turn left (100 > 90)
      # But if the target is 350deg, and the current heading is 5deg, the math goes sideways!

      # input validation: only valid compass readings will be accepted
      if  targetHeading < 0 or targetHeading > 360:
         print 'Input validation failed in adjustHeading'
         exit -1

      # We need a function that makes this true:  350 < 360 < 10  (eg target is 360)
      # and:  355 < 10 < 15   (when the target is 10) 

      # Retrieve the current heading from the IMU: 
      currentHeading=self.getHeading()

      # Piecemeal approach: 
      if currentHeading == targetHeading:
         return "goStraight"
      # if the difference between the two values is less than 180 degrees, we have no math problems: just compare the numbers 
      if abs(currentHeading-targetHeading) < 180:
         if currentHeading < targetHeading:
            return "turnRight"
         else:
            return "turnLeft"

      # Otherwise, there are a couple of scenarios I care about...
      if (targetHeading < 90 and currentHeading >270):   # target in Q1, current in Q4 --- this is the really weird part
         return "turnRight"
      if (targetHeading > 270 and currentHeading < 90 ): # target in Q4, current in Q1 --- equally weird
         return "turnLeft"

      # 
      # The difference between the two angles is *more* than 180 degrees, but we're not crossing 360... meaning it's faster to
      # turn the *wrong* direction, to get where we're going.
      if (currentHeading < targetHeading ):
          return "turnLeft"
      if (currentHeading > targetHeading ):
          return "turnRight"

  
      print "Unhandled..." 
      return "I do not know"

      #got Heading: 205.94
      #Initial heading: 23.50; we should: None 


      #if currentHeading < targetHeading:
         #return "turnRight"
      #else:
         #return "turnLeft"
      
   # local interface, simplifying use of the BNO055 IMU circuit board, for yaw heading, measured in degrees
   def getHeading(self):
      currentHeading, roll, pitch = self.bno.read_euler()
      #if DEBUG: 
      #   print ('got Heading: {0:0.2F}'.format(currentHeading))
      return currentHeading

   # this is currently limited to turning Right, clockwise!
   def turn(self,degreesToTurn): # Turn input # of Degrees ============================ 
      motorSpeed=180

      RightMotor = self.mh.getMotor(1)  # orange track... Right!
      LeftMotor  = self.mh.getMotor(2)  # blue track... Left!

      heading, roll, pitch = self.bno.read_euler()
      targetHeading=heading+degreesToTurn;
      if targetHeading> 360:
         targetHeading=targetHeading-360
      print '******** Starting {0:0.2F} degree turn, to targetHeading: {1:0.2F} ! ***********'.format (degreesToTurn,targetHeading)
      # flip a coin, to see if we'll turn left or right...  I think we need a generic "staticTurn" routine
      startTime=calendar.timegm(time.gmtime())	
      currentTime=calendar.timegm(time.gmtime())
      LeftMotor.setSpeed(motorSpeed)
      RightMotor.setSpeed(motorSpeed)
      LeftMotor.run(Adafruit_MotorHAT.FORWARD)
      RightMotor.run(Adafruit_MotorHAT.BACKWARD)
      while startTime+10 > currentTime:      # restrict me to 10 seconds to make the turn
         currentTime=calendar.timegm(time.gmtime())
         heading, roll, pitch = self.bno.read_euler()
         if self.DEBUG: 
            print 'Underway, Current Heading: {0:0.2F}, current time: {1:5d}'.format(heading,currentTime)
         if targetHeading < 180:
            if heading > 180:
               print "Continuing past 360 degrees.."
               time.sleep(0.05)
               next
            elif (heading>targetHeading):           # stop!
               LeftMotor.run(Adafruit_MotorHAT.RELEASE)
               RightMotor.run(Adafruit_MotorHAT.RELEASE)
               break
         elif (heading>targetHeading):           # stop!
            LeftMotor.run(Adafruit_MotorHAT.RELEASE)
            RightMotor.run(Adafruit_MotorHAT.RELEASE)
            break
         #if self.DEBUG:
            #x,y,z,w = self.bno.read_quaternion()
            #print ('Quaternion: x={0:0.2F} y={1:0.2F} z={2:0.2F} w={3:0.2F}\t'.format(x, y, z, w))
         time.sleep(0.05)
      
      print "Stop, done"
      LeftMotor.run(Adafruit_MotorHAT.RELEASE)
      RightMotor.run(Adafruit_MotorHAT.RELEASE)
      heading, roll, pitch = self.bno.read_euler()
      print 'Target Heading: {0:0.2F}, final heading:{1:0.2F}'.format(targetHeading,heading)
   

   def panAndTilt(self,pan,tilt):

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

      self.pwm.setPWMFreq(60)                        # Set frequency to 60 Hz

      # yes, we're only using the first 2 of 16 channels.  Lotsa room for more fun, later!
      self.pwm.setPWM(0, 0, tilt)
      self.pwm.setPWM(1, 0, pan)
      
      #self.pwm.setPWM(0, 0, servoMin)
      #self.pwm.setPWM(0, 0, servoMax)
      #self.pwm.setPWM(1, 0, servoMin)
      #self.pwm.setPWM(1, 0, servoMax)

      return True # maybe we need to examine return codes from pwm.setPWM, no?

   def trackXY(self):
      # Linear acceleration data (i.e. acceleration from movement, not gravity )
      # returned in meters per second squared):
      x,y,z = self.bno.read_linear_acceleration()
      #if self.DEBUG:
      #  print ('Acceleration: x={0:0.2F} y={1:0.2F}'.format(x, y))
      # How can we accumulate these over time & calculate our position?
      # Sum the second integral?  Ok, This is gonna be hard.

   # Destructor.  This isn't working yet -- can't seem to destroy the object - program keeps hanging
   def __del__(self):
       # 
       self.turnOffMotors()
       del self.bno
       del self.pwm
       del self.mh
