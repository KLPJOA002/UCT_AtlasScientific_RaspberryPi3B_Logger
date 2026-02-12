import os
import time
from datetime import datetime
import subprocess
import re

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



'''
def find_usb_mount():
    usb_bases = ["/media/pi", "/media/root", "/media"]
    with open("/proc/mounts", "r") as f:
        for line in f:
            parts = line.split()
            if len(parts) < 2:
                continue
            device, mountpoint = parts[0], parts[1]
            # Decode octal sequences e.g. \040 -> space
            mountpoint = re.sub(
                r'\\0([0-7]{2})',
                lambda m: chr(int(m.group(1), 8)),
                mountpoint
            )
            if any(mountpoint.startswith(base) for base in usb_bases):
                return mountpoint
    return None
'''
'''
def find_usb_mount():
    """
    Parse /proc/mounts and return the first mountpoint under MOUNT_BASE.
    Works in both console and desktop mode, no D-Bus required.
    """
    try:
        with open("/proc/mounts", "r") as f:
            for line in f:
                parts = line.split()
                if len(parts) < 2:
                    continue
                mountpoint = parts[1]
                # Decode octal escape sequences (e.g. \040 -> space)
                mountpoint = re.sub(
                    r'\\0([0-7]{2})',
                    lambda m: chr(int(m.group(1), 8)),
                    mountpoint
                )
                if mountpoint.startswith(MOUNT_BASE):
                    return mountpoint
    except Exception as e:
        print(f"Error reading /proc/mounts: {e}")
    return None
'''
def Write_USB(data,Name_Modifier):
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
        timestamp = datetime.now().strftime("%Y-%m-%d__%H-%M-%S")
        filename = f"data_{Name_Modifier}_{timestamp}.csv"
        file_path = os.path.join(mount, filename)
        with open(file_path, "a", buffering=1) as fh:
        
            fh.write(data)
            fh.flush()                   # Flush Python buffer
            os.fsync(fh.fileno())        # Force OS to write to disk
        
        subprocess.run(["sync"], check=True)   # Flush ALL kernel buffers to disk
        print(f"Written and synced: {filename}")
    except Exception as e:
        print("Write failed:", e)
        #file_handle.close()
        #file_handle = None
        #current_mount = None
