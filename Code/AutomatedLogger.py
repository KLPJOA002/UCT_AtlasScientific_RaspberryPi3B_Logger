# Python code written for the purpose of reading I2C data from an Atlas Scientific i4 InterLink board connected to two Industrial DO and RTD Sensors
# Written for the University of Cape Town Research Group
# Written by Joab Gray Kloppers: KLPJOA002
# Disclaimer: Parts of this code were created with the use of AI tools including: ChatGPT, ClaudeAi

import io
import sys
import fcntl
import time
import copy
import string
from AtlasI2C import (AtlasI2C)
from New_USB_Writer import *
import RPi.GPIO as GPIO

Sensor1_Addresses = [97,102]#addresses of the two sensors per atlas scientific i4 interlink
Sensor2_Addresses = [98,103]

Num_samples_per_measurement = 10

delaytime = 0.6 #reads require 600ms delay before getting data.  

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
    
    Device_Addresses = []
    
    #get the addresses of each sensor, grouped and ordered by sensor.
    for i in device_address_list:
        if i in Sensor1_Addresses:
            Device1_Address.append(i)
        elif i in Sensor2_Addresses:
            Device2_Address.append(i)
        
    Device_Addresses = Device1_Address+Device2_Address
    
    
    #get the full device for each sensor, grouped and ordered by sensor.
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
    return device_list,Device_Addresses

def wake(device_list):
    #Wake the devices in the given list
    if device_list:

        for dev in device_list: #any command but read to wake the reader
            dev.write("i")    
        time.sleep(delaytime) #wait for some time to prevent pottential issues with following commands
        
def SendSleep(device_list):
    #send the devices in the given list to sleep
    
    if device_list:
        for dev in device_list:# put module to sleep
            dev.write("Sleep")
    
        
def read(device_list):
    #get array of the sensor data using the given device list
    Out = []
    
    if device_list: 
        for dev in device_list: #issue read command and read the result
            dev.write("R")
            
        time.sleep(delaytime) #after the delay required for sensor to process command and send data, read the data.
        for dev in device_list:
            Out.append(dev.read())
            
    return Out
    
#dummy function to test just values. Ignore
def dummy():
    
    device_address_list = [97,98,102,103]
    Device_Info = ["Success DO 97 : 10.2","Success DO 98 : 10.2","Success RTD 102 : 100","Success RTD 103 : 100"]
    
    Device1 = []
    Device2= []
    device_list=[]
    
    Device1_Address = []
    Device2_Address= []
    
    Atlas_Devices = []
    
    
    for i in device_address_list:
        if i in Sensor1_Addresses:
            Device1_Address.append(i)
        elif i in Sensor2_Addresses:
            Device2_Address.append(i)
        
    Atlas_Devices = Device1_Address+Device2_Address
    
    
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
    
    #initilise Variables
    dataRaw_Sensor1 = ""
    dataRaw_Sensor2 = ""
    
    Average_Sensor1 = None
    Average_Sensor2 = None
    
    AverageString_Sensor1 = ""
    AverageString_Sensor2 = ""
    
    #Get a list of Atlas Scientific devices and a list of the addresses. 
    Device_list, Device_Addresses = get_devices()
    
    #wake up the Sensor modules
    wake(Device_list)
    
    #Group the sensors based on the pre-defines sensor addresses.
    Device1 = []
    Device2 = []
    for i in range(len(Device_list)):
        if Device_Addresses[i] in Sensor1_Addresses:
            Device1.append(Device_list[i].moduletype)
        if Device_Addresses[i] in Sensor2_Addresses:
            Device2.append(Device_list[i].moduletype)    
    
    #get 10 readings per sample
    for i in range(Num_samples_per_measurement):
        
        print(i)
        read_data = read(Device_list) #read the data from the devices in device list
        
        #varible initilisation
        if Average_Sensor1 is None:
            Average_Sensor1 = [0.0]*len(Device1)
            
        if Average_Sensor2 is None:
            Average_Sensor2 = [0.0]*len(Device2)
            
        Count1=0
        Count2=0
        
        if not read_data:
            dataRaw += "Unsuccessful Read\n" #check if there was a failed read
        
        else:
            
            for j in range(len(read_data)): #using the read data, orgagnize into lists of raw data for each sensor, and get average for all parameters for each sensor.
                
                if Device_Addresses[j] in Sensor1_Addresses:
                    read_data[j] = read_data[j].rstrip('\x00') #remove empty byte values at end of reading
                    dataRaw_Sensor1 += f"{time.strftime("%Y-%M-%d %H:%M:%S",time.localtime())},{read_data[j].split(":")[0].rstrip('\x00')},{read_data[j].split(":")[1]}\n"
                    Average_Sensor1[Count1] += float(read_data[j].split(":")[1])
                    Count1 += 1
                
                elif Device_Addresses[j] in Sensor2_Addresses:
                    read_data[j] = read_data[j].rstrip('\x00') #remove empty byte values at end of reading
                    dataRaw_Sensor2 += f"{time.strftime("%Y-%M-%d %H:%M:%S",time.localtime())},{read_data[j].split(":")[0].rstrip('\x00')},{read_data[j].split(":")[1]}\n"
                    Average_Sensor2[Count2] += float(read_data[j].split(":")[1])
                    Count2 += 1

    Average_Sensor1 = [x/Num_samples_per_measurement for x in Average_Sensor1] #Compute the average of the raw data
    Average_Sensor2 = [x/Num_samples_per_measurement for x in Average_Sensor2]
    
    SendSleep(Device_list) #send sensor devies to sleep
    
    #Add the average to the raw data for file writing    
    for i in range(len(Device1)):
        AverageString_Sensor1 += f"Average,{Device1[i].split(":")[0].rstrip('\x00')},{Average_Sensor1[i]}\n"
        
    for i in range(len(Device2)):
        AverageString_Sensor2 += f"Average,{Device2[i].split(":")[0].rstrip('\x00')},{Average_Sensor2[i]}\n"
        
    dataRaw_Sensor1+=AverageString_Sensor1
    dataRaw_Sensor2+=AverageString_Sensor2
    
    #write the relavent data to the corresponding file. e.g. if sensor 1 presemt, write sensor 1 data to file labeled sensor 1
    if Device1:
        Write_USB(dataRaw_Sensor1,"Sensor_1")
        
    if Device2:
        Write_USB(dataRaw_Sensor2,"Sensor_2")    
    
if __name__=='__main__':
    main()