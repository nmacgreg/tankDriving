#!/usr/bin/python
import sys
import time
from navControl import navControl

# Enable verbose debug logging if -v is passed as a parameter.   This may require attention, within the context of a class...
if len(sys.argv) == 2 and sys.argv[1].lower() == '-v':
   logging.basicConfig(level=logging.DEBUG)


# instantiate object
control=navControl()

print '\n *** Ready to run, but need 5 seconds for the IMUs compass to calibrate, despite initial calibration! *** \n'
for countdown in range (5,0,-1):
   print '{0:1d}'.format(countdown)
   time.sleep(1)
print '\n I am off to the races \n'

# Let's try some driving!
def headingTest():
   initialHeading = control.getHeading()
   print 'Initial heading: {0:0.2F}'.format(initialHeading)
   while (True):
      direction = control.adjustHeading(initialHeading)
      print "Initial heading: {0:0.2F}; we should: {1} ".format(initialHeading, direction)
      time.sleep(0.5)

# clockwise square
initialHeading = control.getHeading()
driveTo=initialHeading
duration=4
corners=80
for counter in range(1,5):
   print '*** Leg: {0:2d}'.format(counter)
   #if counter == 3:
      #control.DEBUG=1
   control.startDrive(driveTo, duration)
   control.turn(corners)
   driveTo=driveTo+90
   if driveTo > 360:
      driveTo=driveTo-360
   
