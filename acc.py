#!/usr/bin/python
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

import sys
import time
import calendar
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

def headingTest():
   initialHeading = control.getHeading()
   print 'Initial heading: {0:0.2F}'.format(initialHeading)
   while (True):
      direction = control.adjustHeading(initialHeading)
      print "Initial heading: {0:0.2F}; we should: {1} ".format(initialHeading, direction)
      time.sleep(0.5)


# Let's get a feel for the data, by *walking* the 'bot around the room, and printing the values returned
startTime=calendar.timegm(time.gmtime())
currentTime=calendar.timegm(time.gmtime())
while startTime+4 > currentTime:      # restrict me to 10 seconds to make the turn
    currentTime=calendar.timegm(time.gmtime())
    control.trackXY()
    time.sleep(0.1)

# Is this any help, getting the main program to end? (no!)
del control

