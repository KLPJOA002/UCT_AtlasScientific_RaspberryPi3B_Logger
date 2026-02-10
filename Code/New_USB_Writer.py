import os
import time
from datetime import datetime

MOUNT_BASE = "/media/joab"
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
    current_mount = None
    file_handle = None

    # USB inserted
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

    # USB removed
    if not mount and current_mount:
        print("USB removed")
        if file_handle:
            file_handle.close()
        file_handle = None
        current_mount = None

    # Write data if USB is present
    if file_handle:
        try:
            file_handle.write(data)
            file_handle.flush()                   # Flush Python buffer
            os.fsync(file_handle.fileno())        # Force OS to write to disk
        except Exception as e:
            print("Write failed:", e)
            file_handle.close()
            file_handle = None
            current_mount = None

    time.sleep(CHECK_INTERVAL)

    # Cleanup
    if file_handle:
        file_handle.close()
