import os
import time
from datetime import datetime
import subprocess

MOUNT_BASE = "/media/pi"
CHECK_INTERVAL = 2  # seconds

def find_usb_mount():
    """Return path to first mounted USB drive, or None."""
    if not os.path.exists(MOUNT_BASE):
        return None

    for name in os.listdir(MOUNT_BASE):
        path = os.path.join(MOUNT_BASE, name)
        if os.path.ismount(path):
            return path

    return None

def Write_USB(data):
    mount = find_usb_mount()

    # USB inserted
    '''
    if mount and mount != current_mount:
        print(f"USB detected at {mount}")
        current_mount = mount

        try:
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            filename = f"data_{timestamp}.csv"
            file_path = os.path.join(current_mount, filename)
            file_handle = open(file_path, "a", buffering=1)
        except Exception as e:
            print("Failed to open file:", e)
            file_handle = None

    '''
    # USB removed
    if not mount:
        print("No USB Media Detected")
        return

    # Write data if USB is present
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"data_{timestamp}.csv"
        file_path = os.path.join(current_mount, filename)
        with open(file_path, "a", buffering=1) as fh:
        
            fh.write(data)
            fh.flush()                   # Flush Python buffer
            os.fsync(fh.fileno())        # Force OS to write to disk
        
        subprocess.run(["sync"], check=True)   # Flush ALL kernel buffers to disk
        print(f"Written and synced: {filename}")
    except Exception as e:
        print("Write failed:", e)
        file_handle.close()
        file_handle = None
        current_mount = None
