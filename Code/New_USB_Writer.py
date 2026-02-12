# Python code written for the purpose of writing sensor data to a present USB drive, and writing a local Backup
# Written for the University of Cape Town Research Group
# Written by Joab Gray Kloppers: KLPJOA002
# Disclaimer: Parts of this code were created with the use of AI tools including: ChatGPT, ClaudeAi

import os
import time
from datetime import datetime
import subprocess
import re

MOUNT_BASE = "/media/pi"

def find_usb_mount():
    """Return path to first mounted USB drive, or None."""
    if not os.path.exists(MOUNT_BASE):
        return None

    for name in os.listdir(MOUNT_BASE):
        path = os.path.join(MOUNT_BASE, name)
        if os.path.ismount(path):
            return path

    return None

def Write_USB(data,Name_Modifier):
    #writing the given data to a file modified by the given modifer
    
    timestamp = datetime.now().strftime("%Y-%m-%d__%H-%M-%S")
    filename = f"data_{Name_Modifier}_{timestamp}.csv"
    
    
    #write data to a local folder for backup purposes
    try:
        subfolder = os.path.join(os.getcwd(), "Backup_Data")
        os.makedirs(subfolder, exist_ok=True)  # Creates folder if it doesn't exist
        file_path = os.path.join(subfolder, filename)
        with open(file_path, "a", buffering=1) as fh:
        
            fh.write(data)
            fh.flush()                   # Flush Python buffer
            os.fsync(fh.fileno())        # Force OS to write to disk
        
        subprocess.run(["sync"], check=True)   # Flush ALL kernel buffers to disk
        print(f"Written To Local Storage and synced: {filename}")
    except Exception as e:
        print("Write failed:", e)

    #detect a usb device for usb writing
    mount = find_usb_mount()

    # USB removed
    if not mount:
        print("No USB Media Detected")
        return

    # Write data if USB is present
    try:
        file_path = os.path.join(mount, filename)
        with open(file_path, "a", buffering=1) as fh:
        
            fh.write(data)
            fh.flush()                   # Flush Python buffer
            os.fsync(fh.fileno())        # Force OS to write to disk
        
        subprocess.run(["sync"], check=True)   # Flush ALL kernel buffers to disk
        print(f"Written to USB Storage and synced: {filename}")
    except Exception as e:
        print("Write failed:", e)