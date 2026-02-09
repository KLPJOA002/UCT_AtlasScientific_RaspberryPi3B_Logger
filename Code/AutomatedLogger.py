import io
import sys
#import fcntl
import time
import copy
import string
#from AtlasI2C import (AtlasI2C)
from Media_Scanner import *
from util import *
from database import *
from log import *

# Source - https://stackoverflow.com/a/6935354
# Posted by Michael Dillon
# Retrieved 2026-02-09, License - CC BY-SA 3.0

def write_and_verify(f_n,data):
    f = file(f_n,'w')
    f.write(data)
    f.flush()
    os.fsync(f.fileno())
    f.close()
    f = file(f_n,'r')
    verified = f.read()
    f.close()
    return  verified == data and f.closed

# Source - https://stackoverflow.com/q/6840711
# Posted by Ken, modified by community. See post 'Timeline' for change history
# Retrieved 2026-02-09, License - CC BY-SA 3.0

def get_partition(dev):
    os.system('fdisk -l %s > output' % dev)
    f = file('output')
    data = f.read()
    print data
    f.close()
    return data.split('\n')[-2].split()[0].strip()

def mount_partition(partition):
    os.system('mount %s /media/mymntpnt' % partition)


def unmount_partition():
    os.system('umount /media/mymntpnt')


#function obtains an array of all Atlas scientific devices connected to the I2C bus
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
    #get array of connected devices
    Out = []
    device_list = get_devices()
    
    #get the first device in the list to be used to get the time delays required.
    DeviceTemplate = device_list[0]
    delaytime = DeviceTemplate.LONG_TIMEOUT


    for dev in device_list:
        dev.write("R")
    time.sleep(delaytime)
    for dev in device_list:
        Out.append(dev.read())
        
    return Out
    
#dummy function to test just values
def dummy():
    
    for i in range(2):
        time.sleep(0.1)
    return ["Success DO ---------- 10.2","Success PTD ---------- 20000"]

def main():
    ms = MediaScanner()
    
    dataRaw = []
    for i in range(10):
        print(i)
        dataRaw.append([time.ctime(), dummy()[0].split(" ")[1], dummy()[0].split(" ")[3]])
        dataRaw.append([time.ctime(), dummy()[1].split(" ")[1], dummy()[1].split(" ")[3]])
    
    
    Drives = ms.scan_media()
    
    if Drives:
        for Drive in Drives:
            mount_partition(get_partition(Drives))
            write_and_verify('/media/mymntpnt/test_Write',dataRaw)
            unmount_partition()
    
    print(dataRaw)
    
    
    
if __name__=='__main__':
    main()
    