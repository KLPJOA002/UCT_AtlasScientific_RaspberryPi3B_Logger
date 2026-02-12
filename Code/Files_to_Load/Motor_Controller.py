# Python code written for the purpose of controlling a motorised pump for circulation purposes whilst performing long term measurements within water.
# Written for the University of Cape Town Research Group
# Written by Joab Gray Kloppers: KLPJOA002

import RPi.GPIO as GPIO
import time

Frequency = 0.1 #define the frequency and duty cycle of the motorised pump
Duty_Cycle = 0.5

Default_Mode = 0 #Default mode to determing weather the motor is on by default or off by default. 0: Motor on when GPIO pin goes high, 1: Motor off when GPIO pin goes high


def main():
    if not Default_Mode: #assign the correct pin duty cycle to match the desired motor duty cycle depending on default motor mode.
        Pin_High_Time = (1/Frequency)*Duty_Cycle
        Pin_Low_Time = (1/Frequency)-Pin_High_Time
    else:
        Pin_Low_Time = (1/Frequency)*Duty_Cycle
        Pin_High_Time = (1/Frequency)-Pin_Low_Time
        

    while True:
        GPIO.setmode(GPIO.BOARD) #initilise the board GPIO pins
        GPIO.setup(7,GPIO.OUT)  #using GPIO 4 or Pin 7
        GPIO.output(7,1) #set the GPIO pin high
        
        
        time.sleep(Pin_High_Time) #wait for the desired Pin High Time
        
        GPIO.output(7,0) #set the GPIO pin Low
        GPIO.cleanup() #do the GPIO Cleanup procedure
        
        time.sleep(Pin_Low_Time) #wait for the desired Pin Low Time
    
    
if __name__=='__main__':
    main()