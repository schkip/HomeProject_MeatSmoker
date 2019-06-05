#!/usr/bin/env python

# This project is to control the temperature of a vertical meat smoker
# by using thermocouples connected into the meat and the furnace
# as well as a small blower fan to the furnace (pit)
# the sensors are K-type thermocouples
# and the actuator is a small blower fan blowing into the meat smoker
# the thermocouple amplifier is the MAX31855 chip.
# note that the Banggood evaluation module had a circuit issue (short differential)
#for the blower fan made use of the H-bridge driver from Sparkfun electronics and driving the fan from a 240-12V regulator
#github will have the photo of the pinouts for soldering
#Project in November 2018
###################################

#imports
import time
import RPi.GPIO as GPIO
import Adafruit_GPIO.SPI as SPI
import Adafruit_MAX31855.MAX31855 as MAX31855

###################################

#temperature setpoint for meat smoking (pork)
#https://www.smokedbbqsource.com/smoking-times-temperatures/Pork_smoking_times_and_temperatures
DoneTemp = 95
PitTemp = 107
smoking_time = 60 * 12 #12 hour smoking time
blower_time = 60 #blower wait time in seconds

#####motor setup
GPIO.setmode(GPIO.BCM) #BCM broadcom setting for pins

###################################

##variables for motor
PWMA = 4
AIN1 = 21
AIN2 = 20
STBY = 13

#variables for SPI therm1 (this is the pit or furnace temperature)
# Raspberry Pi software SPI configuration (thermocouple1)
CLK = 25
CS  = 24
DO  = 18
sensor = MAX31855.MAX31855(CLK, CS, DO)


#variables for SPI therm2 (this is the meat or done temperature)
# Raspberry Pi software SPI configuration (thermocouple2)
CLK2 = 16
CS2  = 19
DO2  = 26
sensor2 = MAX31855.MAX31855(CLK2, CS2, DO2)

###################################

#pins setup
GPIO.setup(PWMA, GPIO.OUT)
GPIO.setup(AIN2, GPIO.OUT)
GPIO.setup(AIN1, GPIO.OUT)
GPIO.setup(STBY, GPIO.OUT)

###################################

def FunctionMotorOn():
    GPIO.output(AIN1, GPIO.HIGH)
    GPIO.output(AIN2, GPIO.LOW)
    GPIO.output(PWMA, GPIO.HIGH)
    GPIO.output(STBY, GPIO.HIGH)

def FunctionMotorOff():
    GPIO.output(AIN1, GPIO.LOW)
    GPIO.output(AIN2, GPIO.LOW)
    GPIO.output(PWMA, GPIO.LOW)
    GPIO.output(STBY, GPIO.LOW)

###################################

#state machine (BLOWER CONTROL)
    # check that the done temperature hasn't been reached (therm2)
    # while the pit temperature is less than optimum (therm1)
    # switch the blower fan on for 60s
    # check again

for x in range (0,smoking_time-1):
    temp = sensor.readTempC()
    temp2 = sensor2.readTempC()
    print('Pit Temp: {0:0.3F}*C '.format(temp))
    print('Meat Temp: {0:0.3F}*C '.format(temp2))
    if temp > PitTemp:
        print('Pit is up to temperature')
        FunctionMotorOff()
    if temp < PitTemp:
        print('Warming up the pit')
        FunctionMotorOn()
    if temp2 > DoneTemp:
        print('Meat is done')
        break
    time.sleep(blower_time)

FunctionMotorOff()
