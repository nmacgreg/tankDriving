#!/usr/bin/python
import sys
import time
from navControl import navControl

# Enable verbose debug logging if -v is passed as a parameter.   This may require attention, within the context of a class...
if len(sys.argv) == 2 and sys.argv[1].lower() == '-v':
   logging.basicConfig(level=logging.DEBUG)


# instantiate object
control=navControl()

# Let's try some driving!
print '\n *** Ready to run *** \n'
time.sleep(5)

initialHeading = control.getHeading()
print 'Initial heading: {0:0.2F}'.format(initialHeading)
while (True):
   direction = control.adjustHeading(initialHeading)
   print "Initial heading: {0:0.2F}; we should: {1} ".format(initialHeading, direction)
   time.sleep(0.5)

exit
#control.startDrive()
