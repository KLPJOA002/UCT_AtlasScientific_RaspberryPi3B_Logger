#!/bin/bash

#Script written for the purpose of initilising a Raspberry Pi 3B or Pi Zero 2 W to perform automatic and periodic data logging and motor control
# Written for the University of Cape Town Research Group
# Written by Joab Gray Kloppers: KLPJOA002
# Disclaimer: Parts of this code were created with the use of AI tools including: ChatGPT, ClaudeAi

#get the directory of the current location of the script
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

#installing packages required for RTC initilisation
echo "installing required packages"
sudo apt install util-linux-extra

#add the required configuration text to the config file to use the DS3231 RTC
echo "dtoverlay=i2c-rtc,ds3231" | sudo tee -a /boot/firmware/config.txt
echo "Added DS3231 driver for RTC"

# Create a udev rule that calls a mount helper script on USB block device insertion
echo Enabling automatic USB Mount
sudo bash -c 'cat > /etc/udev/rules.d/99-usb-automount.rules << EOF
ACTION=="add",    SUBSYSTEMS=="usb", SUBSYSTEM=="block", ENV{ID_FS_USAGE}=="filesystem", RUN+="/usr/local/bin/usb-mount.sh add %k"
ACTION=="remove", SUBSYSTEMS=="usb", SUBSYSTEM=="block",                                 RUN+="/usr/local/bin/usb-mount.sh remove %k"
EOF'

# Create the mount helper script: Currently unused 
sudo bash -c 'cat > /usr/local/bin/usb-mount.sh << '"'"'MOUNTSCRIPT'"'"'
#!/bin/bash
# /usr/local/bin/usb-mount.sh
# Called by udev with: add <devname>  OR  remove <devname>
# <devname> is the kernel name e.g. sda1

ACTION="$1"
DEVNAME="$2"
DEVPATH="/dev/${DEVNAME}"
MOUNT_BASE="/media/usb"

log() { logger -t usb-mount "$*"; }

case "$ACTION" in
  add)
    # Wait briefly for the device node to be fully ready
    sleep 2

    # Read the filesystem label; fall back to device name
    LABEL=$(blkid -s LABEL -o value "$DEVPATH" 2>/dev/null)
    MOUNT_POINT="${MOUNT_BASE}/${LABEL:-$DEVNAME}"

    mkdir -p "$MOUNT_POINT"

    # Mount with sync so every write goes straight to flash
    if mount -o sync,noatime "$DEVPATH" "$MOUNT_POINT"; then
        log "Mounted $DEVPATH at $MOUNT_POINT"
    else
        log "Failed to mount $DEVPATH"
        rmdir "$MOUNT_POINT" 2>/dev/null
    fi
    ;;

  remove)
    # Find and unmount any mountpoint using this device
    MOUNT_POINT=$(grep "^${DEVPATH} " /proc/mounts | awk "{print \$2}" | head -1)
    if [ -n "$MOUNT_POINT" ]; then
        umount -l "$MOUNT_POINT" && log "Unmounted $MOUNT_POINT" || log "Failed to unmount $MOUNT_POINT"
        rmdir "$MOUNT_POINT" 2>/dev/null
    fi
    ;;
esac
MOUNTSCRIPT'

sudo chmod +x /usr/local/bin/usb-mount.sh
sudo mkdir -p /media/usb

sudo udevadm control --reload-rules
echo "USB automount configured (no desktop required)"


echo "Setup complete. All USB drives will now be mounted with sync."

#enable I2C interfacing
echo "Enabling I2C"
sudo raspi-config nonint do_i2c 0

#echo "Disabling Desktop by switching to console mode"
#sudo systemctl set-default multi-user.target

#add service and timer to run the logging program every 20 seconds
echo "Adding system service to run logger"
sudo tee /etc/systemd/system/logger.service > /dev/null << EOF
[Unit]
Description=Minute Data Logger
After=multi-user.target

[Service]
Type=oneshot
ExecStart=/usr/bin/python3 $SCRIPT_DIR/AutomatedLogger.py
User=root
WorkingDirectory=$SCRIPT_DIR

[Install]
WantedBy=multi-user.target
EOF

echo "Adding time service to periodically run logger"
sudo tee /etc/systemd/system/logger.timer > /dev/null << EOF
[Unit]
Description=Run data logger every minute
After=local-fs.target sysinit.target

[Timer]
OnBootSec=60
OnUnitActiveSec=20
AccuracySec=1s
Persistent=true
Unit=logger.service

[Install]
WantedBy=timers.target
EOF

#Motor control service
echo "Adding system service to run motor control"
sudo tee /etc/systemd/system/MotorControl.service >/dev/null << EOF
 [Unit]
 Description=Program to Control the Motor
 After=multi-user.target

 [Service]
 Type=idle
 ExecStart=/usr/bin/python3 $SCRIPT_DIR/Motor_Controller.py 

 [Install]
 WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable logger.timer
#sudo systemctl enable logger.service
sudo systemctl start logger.timer
sudo systemctl enable MotorControl.service

echo "Setup complete. Please reboot now"