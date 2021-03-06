# coding=utf-8
import time
import RPi.GPIO as GPIO

stepPin = 8
stepDir = 10
sleepTime = 0.02

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)

GPIO.setup(stepPin, GPIO.OUT)
GPIO.setup(stepDir, GPIO.OUT)
GPIO.output(stepDir, True)

while True:
    GPIO.output(stepPin, True)
    time.sleep(sleepTime)
    GPIO.output(stepPin, False)
    time.sleep(sleepTime)
