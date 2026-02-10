import io
import sys
#import fcntl
import time
import copy
import string
#from AtlasI2C import (AtlasI2C)
from New_USB_Writer import *

#function obtains an array of all Atlas scientific devices connected to the I2C bus
#source: Atlas Scientific EZO python Library
def get_devices():
    device = AtlasI2C()
    device_address_list = device.list_i2c_devices()
    device_list = []
    
    for i in device_address_list:
        device.set_i2c_address(i)
        response = device.query("I")
        try:
            moduletype = response.split(",")[1] 
            response = device.query("name,?").split(",")[1]
        except IndexError:
            print(">> WARNING: device at I2C address " + str(i) + " has not been identified as an EZO device, and will not be queried") 
            continue
        device_list.append(AtlasI2C(address = i, moduletype = moduletype, name = response))
    return device_list 

def read():
    #get array of connected devices using i2c.py library
    Out = []
    device_list = get_devices()
    
    if device_list:
        #get the first device in the list to be used to get the time delays required.
        DeviceTemplate = device_list[0]
        delaytime = 0.6 #reads require 600ms delay before getting data.

        for dev in device_list:
            dev.write("i")
        for dev in device_list:
            dev.write("R")
        time.sleep(delaytime)
        for dev in device_list:
            Out.append(dev.read())
        
        for dev in device_list:
            dev.write("Sleep")
        
    return Out
    
#dummy function to test just values
def dummy():
    
    for i in range(2):
        time.sleep(0.1)
    return ["Success DO 97 : 10.2","Success RTD 102 : 100"]
            #,"Success DO 98 : 10.2","Success RTD 103 : 100"]

def main():
    
    #average of the 10 readings per sample
    average_DO = float
    average_RTD = float
    Averages = None
    
    AverageString = None
    dataRaw = None
    
    #get 10 readings per sample
    for i in range(10):
        print(i)
        
        #temp = dummy()
        #read from connected devies.
        temp = read()
        
        #average_DO += temp[0].split(":")[1]
        if Averages is None:
            Averages = [0.0]*len(temp)
        
        if dataRaw is None:
            dataRaw = [""]*len(temp)
            
        if AverageString is None:
            AverageString = [""]*len(temp)
        
        if not temp:
            dataRaw += "Unsuccessful Read\n"
        
        else:
            
            for j in range(0,len(temp),2):
                
                temp[j] = temp[j].rstrip('\x00') #remove empty byte values at end of reading
                temp[j+1] = temp[j+1].rstrip('\x00') #remove empty byte values at end of reading
                
                dataRaw[j] += f"{time.ctime()},{temp[j].split(":")[0]},{temp[j].split(":")[1]}\n"
                Averages[j] += float(temp[j].split(":")[1])
                
                dataRaw[j] += f"{time.ctime()},{temp[j+1].split(":")[0]},{temp[j+1].split(":")[1]}\n"
                Averages[j] += float(temp[j+1].split(":")[1])
            
            '''
            average_DO += temp[0].split(":")[1]
            average_RTD += temp[1].split(":")[1]
            
            dataRaw += f"{time.ctime()},{temp[0].split(":")[0]},{temp[0].split(":")[1]}\n"
            dataRaw += f"{time.ctime()},{temp[1].split(":")[0]},{temp[1].split(":")[1]}\n"
            
            
        elif temp[0].split(" ")[1] == "RTD":
            
            average_DO += temp[1].split(":")[1]
            average_RTD += temp[0].split(":")[1]
            
            dataRaw += f"{time.ctime()},{temp[1].split(":")[0]},{temp[0].split(":")[1]}\n"
            dataRaw += f"{time.ctime()},{temp[0].split(":")[0]},{temp[1].split(":")[1]}\n"
            '''
    Averages = [x/10 for x in Averages]
    
    for j in range(0,len(temp),2):
                
        AverageString[j] += f"Average,{temp[j].split(":")[0]},{Averages[j]}\n"
        AverageString[j] += f"Average,{temp[j+1].split(":")[0]},{Averages[j+1]}\n"
    
    for j in range(0,len(temp),2):
        dataRaw[j]+=AverageString[j] + AverageString[j+1]
        
    for j in range(0,len(temp),2):
        if int(temp[0].split(" ")[2]) == 97:
            Write_USB(dataRaw,"Sensor 1")
            #print("Device 1")
            #print(dataRaw[j])
        else:
            Write_USB(dataRaw,"Sensor 2")
            #print("Device 2")
            #print(dataRaw[j])
    
    #print(dataRaw)
    
    
    
if __name__=='__main__':
    main()
    