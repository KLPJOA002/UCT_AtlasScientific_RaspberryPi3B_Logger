import io
import sys
import fcntl
import time
import copy
import string
from AtlasI2C import (AtlasI2C)
from New_USB_Writer import *
import RPi.GPIO as GPIO

Sensor1_Addresses = [97,102]
Sensor2_Addresses = [98,103]

Num_samples_per_measurement = 10

#function obtains an array of all Atlas scientific devices connected to the I2C bus
#source: Atlas Scientific EZO python Library
def get_devices():
    device = AtlasI2C()
    device_address_list = device.list_i2c_devices()
    device_list = []
    
    Device1 = []
    Device2= []

    Device1_Address = []
    Device2_Address= []
    
    Atlas_Devices = []
    
    #ReturnList = []
    
    for i in device_address_list:
        if i in Sensor1_Addresses:
            Device1_Address.append(i)
        elif i in Sensor2_Addresses:
            Device2_Address.append(i)
        
    Atlas_Devices = Device1_Address+Device2_Address
    
    
    
    for i in device_address_list:
        device.set_i2c_address(i)
        response = device.query("I")
        try:
            moduletype = response.split(",")[1] 
            response = device.query("name,?").split(",")[1]
        except IndexError:
            print(">> WARNING: device at I2C address " + str(i) + " has not been identified as an EZO device, and will not be queried") 
            continue
        
        if i in Sensor1_Addresses:
            Device1.append(AtlasI2C(address = i, moduletype = moduletype, name = response))
        elif i in Sensor2_Addresses:
            Device2.append(AtlasI2C(address = i, moduletype = moduletype, name = response))
            
    device_list = Device1+Device2        
    return device_list,Atlas_Devices

def wake():
    device_list,ignore = get_devices()
    
    if device_list:
        delaytime = 0.6 #reads require 600ms delay before getting data.

        for dev in device_list: #any command but read to wake the reader
            dev.write("i")    
        time.sleep(delaytime) 
        
def SendSleep():
    device_list,ignore = get_devices()
    
    if device_list:
        #delaytime = 0.6 #reads require 600ms delay before getting data.
        for dev in device_list:# put reader to sleep
            dev.write("Sleep")
    
        
def read():
    #get array of connected devices using i2c.py library
    Out = []
    device_list,device_addresses= get_devices()
    
    if device_list:
        #get the first device in the list to be used to get the time delays required.
        #DeviceTemplate = device_list[0]
        delaytime = 0.6 #reads require 600ms delay before getting data.   
            
        for dev in device_list: #issue read command and read the result
            dev.write("R")
            
        time.sleep(delaytime)
        for dev in device_list:
            Out.append(dev.read())
        
        
    return Out,device_addresses
    
#dummy function to test just values
def dummy():
    
    device_address_list = [97,98,102,103]
    Device_Info = ["Success DO 97 : 10.2","Success DO 98 : 10.2","Success RTD 102 : 100","Success RTD 103 : 100"]
    
    Device1 = []
    Device2= []
    device_list=[]
    
    Device1_Address = []
    Device2_Address= []
    
    Atlas_Devices = []
    
    #ReturnList = []
    
    for i in device_address_list:
        if i in Sensor1_Addresses:
            Device1_Address.append(i)
        elif i in Sensor2_Addresses:
            Device2_Address.append(i)
        
    Atlas_Devices = Device1_Address+Device2_Address
    
    #ReturnList = []
    
    for i in device_address_list:
        if i in Sensor1_Addresses:
            Device1.append(Device_Info[device_address_list.index(i)])
        elif i in Sensor2_Addresses:
            Device2.append(Device_Info[device_address_list.index(i)])
        
    device_list = Device1+Device2
    
    
    for i in range(2):
        time.sleep(0.1)
    return device_list,Atlas_Devices

def main():
    
    #GPIO.setmode(GPIO.BOARD)
    #GPIO.setup(7,GPIO.OUT)
    #GPIO.output(7,1)
    
    #average of the 10 readings per sample
    average_DO = float
    average_RTD = float
    Averages = None
    
    AverageString = None
    dataRaw = None
    
    dataRaw_Sensor1 = ""
    dataRaw_Sensor2 = ""
    
    Average_Sensor1 = None
    Average_Sensor2 = None
    
    AverageString_Sensor1 = ""
    AverageString_Sensor2 = ""
    
    wake()
    
    #get 10 readings per sample
    for i in range(Num_samples_per_measurement):
        print(i)
        
        #temp,temp2 = dummy()
        #print(temp)
        #read from connected devies.
        temp,temp2 = read()
        
        #average_DO += temp[0].split(":")[1]
        
        if Average_Sensor1 is None:
            Average_Sensor1 = [0.0]*len(temp)
            
        if Average_Sensor2 is None:
            Average_Sensor2 = [0.0]*len(temp)
            
        Count1=0
        Count2=0
        
        if Averages is None:
            Averages = [0.0]*len(temp)
        
        if dataRaw is None:
            dataRaw = [""]*len(temp)
            
        if AverageString is None:
            AverageString = [""]*len(temp)
        
        if not temp:
            dataRaw += "Unsuccessful Read\n"
        
        else:
            
            for j in range(len(temp)):
                #print(temp[j])
                
                if temp2[j] in Sensor1_Addresses:
                    temp[j] = temp[j].rstrip('\x00') #remove empty byte values at end of reading
                    dataRaw_Sensor1 += f"{time.ctime()},{temp[j].split(":")[0].rstrip('\x00')},{temp[j].split(":")[1]}\n"
                    Average_Sensor1[Count1] += float(temp[j].split(":")[1])
                    Count1 += 1
                
                elif temp2[j] in Sensor2_Addresses:
                    temp[j] = temp[j].rstrip('\x00') #remove empty byte values at end of reading
                    dataRaw_Sensor2 += f"{time.ctime()},{temp[j].split(":")[0].rstrip('\x00')},{temp[j].split(":")[1]}\n"
                    Average_Sensor2[Count2] += float(temp[j].split(":")[1])
                    Count2 += 1
                    
            '''Below works
            for j in range(0,len(temp),2):
                
                temp[j] = temp[j].rstrip('\x00') #remove empty byte values at end of reading
                temp[j+1] = temp[j+1].rstrip('\x00') #remove empty byte values at end of reading
                
                dataRaw[j] += f"{time.ctime()},{temp[j].split(":")[0].rstrip('\x00')},{temp[j].split(":")[1]}\n"
                Averages[j] += float(temp[j].split(":")[1])
                
                dataRaw[j] += f"{time.ctime()},{temp[j+1].split(":")[0].rstrip('\x00')},{temp[j+1].split(":")[1]}\n"
                Averages[j+1] += float(temp[j+1].split(":")[1])
            
            '''
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
    Average_Sensor1 = [x/Num_samples_per_measurement for x in Average_Sensor1]
    Average_Sensor2 = [x/Num_samples_per_measurement for x in Average_Sensor2]
    
    SendSleep()
    
    '''
    for j in range(0,len(temp),2):
                
        AverageString[j] += f"Average,{temp[j].split(":")[0].rstrip('\x00')},{Averages[j]}\n"
        AverageString[j] += f"Average,{temp[j+1].split(":")[0].rstrip('\x00')},{Averages[j+1]}\n"
    
    for j in range(0,len(temp),2):
        dataRaw[j]+=AverageString[j] + AverageString[j+1]
        
    for j in range(0,len(temp),2):
        if int(temp[0].split(" ")[2]) == 97:
            #Write_USB(dataRaw[j],"Sensor_1")
            print("Device 1")
            print(dataRaw[j])
        else:
            #Write_USB(dataRaw[j],"Sensor_2")
            print("Device 2")
            print(dataRaw[j])
            
    '''
        
    Device1 = []
    Device2 = []
    for i in range(len(temp)):
        if temp2[i] in Sensor1_Addresses:
            Device1.append(temp[i])
        if temp2[i] in Sensor2_Addresses:
            Device2.append(temp[i])
        
    for i in range(len(Device1)):
        AverageString_Sensor1 += f"Average,{Device1[i].split(":")[0].rstrip('\x00')},{Average_Sensor1[i]}\n"
        
    for i in range(len(Device2)):
        AverageString_Sensor2 += f"Average,{Device2[i].split(":")[0].rstrip('\x00')},{Average_Sensor2[i]}\n"
        
    dataRaw_Sensor1+=AverageString_Sensor1
    dataRaw_Sensor2+=AverageString_Sensor2
    
    if Device1:
        Write_USB(dataRaw_Sensor1,"Sensor_1")
        
    if Device2:
        Write_USB(dataRaw_Sensor2,"Sensor_2")

    
    #GPIO.output(7,0)
    #GPIO.cleanup()
    
    #print(dataRaw)
    
    
    
if __name__=='__main__':
    main()
    