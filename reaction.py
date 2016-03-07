#!/usr/bin/python
# Neil wrote this, using GPIO to turn on an LED, mostly as a demo for Maxwell (and me)  
# Jan 29, 2016
# Context: got a GPIO breakout board in prep for the prototank
import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

led = 17

GPIO.setup(led, GPIO.OUT)

for num in range(1,6):
   GPIO.output(led, 1)
   time.sleep(1)
   GPIO.output(led, 0)
   time.sleep(1)

GPIO.cleanup()
