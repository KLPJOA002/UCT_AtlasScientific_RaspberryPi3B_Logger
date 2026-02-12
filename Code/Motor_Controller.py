import RPi.GPIO as GPIO
import time

Frequency = 0.1
Duty_Cycle = 0.5

On_Time = (1/Frequency)*Duty_Cycle
Off_Time = (1/Frequency)-On_Time

def main():
    
    while True:
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(7,GPIO.OUT)
        GPIO.output(7,1)
        
        
        time.sleep(On_Time)
        
        GPIO.output(7,0)
        GPIO.cleanup()
        
        time.sleep(Off_Time)
    
    
if __name__=='__main__':
    main()