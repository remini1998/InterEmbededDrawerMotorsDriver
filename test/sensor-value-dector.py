# coding=utf-8
import time
import RPi.GPIO as GPIO

sensorPin = 38

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)

GPIO.setup(sensorPin, GPIO.IN)

while True:
    time.sleep(0.20)
    print(GPIO.input(sensorPin))
