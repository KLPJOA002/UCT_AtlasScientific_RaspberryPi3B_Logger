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
    
    #ReturnList = []
    
    for i in device_address_list:
        if i in Sensor1_Addresses:
            Device1_Address.append(i)
        elif i in Sensor2_Addresses:
            Device2_Address.append(i)
        
    Device_Addresses = Device1_Address+Device2_Address
    
    
    
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
    #device_list,ignore = get_devices()
    
    if device_list:

        for dev in device_list: #any command but read to wake the reader
            dev.write("i")    
        time.sleep(delaytime) 
        
def SendSleep(device_list):
    #device_list,ignore = get_devices()
    
    if device_list:
        #delaytime = 0.6 #reads require 600ms delay before getting data.
        for dev in device_list:# put reader to sleep
            dev.write("Sleep")
    
        
def read(device_list):
    #get array of connected devices using i2c.py library
    Out = []
    #device_list,device_addresses= get_devices()
    
    
    if device_list:
        #get the first device in the list to be used to get the time delays required.
        #DeviceTemplate = device_list[0] 
            
        for dev in device_list: #issue read command and read the result
            dev.write("R")
            
        time.sleep(delaytime)
        for dev in device_list:
            Out.append(dev.read())
        
        
    return Out#,device_addresses
    
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
    #average_DO = float
    #average_RTD = float
    #Averages = None
    
    #AverageString = None
    #dataRaw = None
    
    dataRaw_Sensor1 = ""
    dataRaw_Sensor2 = ""
    
    Average_Sensor1 = None
    Average_Sensor2 = None
    
    AverageString_Sensor1 = ""
    AverageString_Sensor2 = ""
    
    
    
    Device_list, Device_Addresses = get_devices()
    
    wake(Device_list)
    
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
        
        #read_data,Device_Addresses = dummy()
        #print(read_data)
        #read from connected devies.
        read_data = read(Device_list)
        
        #average_DO += read_data[0].split(":")[1]
        
        if Average_Sensor1 is None:
            Average_Sensor1 = [0.0]*len(Device1)
            
        if Average_Sensor2 is None:
            Average_Sensor2 = [0.0]*len(Device2)
            
        Count1=0
        Count2=0
        
        '''
        if Averages is None:
            Averages = [0.0]*len(read_data)
        
        if dataRaw is None:
            dataRaw = [""]*len(read_data)
            
        if AverageString is None:
            AverageString = [""]*len(read_data)
        
        '''
        if not read_data:
            dataRaw += "Unsuccessful Read\n"
        
        else:
            
            for j in range(len(read_data)):
                #print(read_data[j])
                
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
                    
            '''Below works
            for j in range(0,len(read_data),2):
                
                read_data[j] = read_data[j].rstrip('\x00') #remove empty byte values at end of reading
                read_data[j+1] = read_data[j+1].rstrip('\x00') #remove empty byte values at end of reading
                
                dataRaw[j] += f"{time.ctime()},{read_data[j].split(":")[0].rstrip('\x00')},{read_data[j].split(":")[1]}\n"
                Averages[j] += float(read_data[j].split(":")[1])
                
                dataRaw[j] += f"{time.ctime()},{read_data[j+1].split(":")[0].rstrip('\x00')},{read_data[j+1].split(":")[1]}\n"
                Averages[j+1] += float(read_data[j+1].split(":")[1])
            
            '''
            '''
            average_DO += read_data[0].split(":")[1]
            average_RTD += read_data[1].split(":")[1]
            
            dataRaw += f"{time.ctime()},{read_data[0].split(":")[0]},{read_data[0].split(":")[1]}\n"
            dataRaw += f"{time.ctime()},{read_data[1].split(":")[0]},{read_data[1].split(":")[1]}\n"
            
            
        elif read_data[0].split(" ")[1] == "RTD":
            
            average_DO += read_data[1].split(":")[1]
            average_RTD += read_data[0].split(":")[1]
            
            dataRaw += f"{time.ctime()},{read_data[1].split(":")[0]},{read_data[0].split(":")[1]}\n"
            dataRaw += f"{time.ctime()},{read_data[0].split(":")[0]},{read_data[1].split(":")[1]}\n"
            '''
    Average_Sensor1 = [x/Num_samples_per_measurement for x in Average_Sensor1]
    Average_Sensor2 = [x/Num_samples_per_measurement for x in Average_Sensor2]
    
    SendSleep(Device_list)
    
    '''
    for j in range(0,len(read_data),2):
                
        AverageString[j] += f"Average,{read_data[j].split(":")[0].rstrip('\x00')},{Averages[j]}\n"
        AverageString[j] += f"Average,{read_data[j+1].split(":")[0].rstrip('\x00')},{Averages[j+1]}\n"
    
    for j in range(0,len(read_data),2):
        dataRaw[j]+=AverageString[j] + AverageString[j+1]
        
    for j in range(0,len(read_data),2):
        if int(read_data[0].split(" ")[2]) == 97:
            #Write_USB(dataRaw[j],"Sensor_1")
            print("Device 1")
            print(dataRaw[j])
        else:
            #Write_USB(dataRaw[j],"Sensor_2")
            print("Device 2")
            print(dataRaw[j])
            
    '''
        
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