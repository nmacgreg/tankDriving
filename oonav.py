#!/usr/bin/python
import sys

from navControl import navControl

# Enable verbose debug logging if -v is passed as a parameter.   This may require attention, within the context of a class...
if len(sys.argv) == 2 and sys.argv[1].lower() == '-v':
   logging.basicConfig(level=logging.DEBUG)


# instantiate object
control=navControl()

# Let's try some driving!
print '\n *** Ready to run *** \n'
control=0
exit
control.startDrive()
