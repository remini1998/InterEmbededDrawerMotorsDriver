# coding=utf-8
import time
import RPi.GPIO as GPIO

stepPin = 8
sleepTime = 0.02

while True:
    GPIO.output(stepPin, True)
    time.sleep(sleepTime)
    GPIO.output(stepPin, False)
    time.sleep(sleepTime)
