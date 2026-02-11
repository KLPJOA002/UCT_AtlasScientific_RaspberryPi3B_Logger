#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

sudo apt install util-linux-extra

# Ask user for date and time
echo "Enter current date and time (format: YYYY-MM-DD HH:MM:SS)"
read USER_DATETIME

# Validate basic format (optional, simple regex)
if [[ ! $USER_DATETIME =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}\ [0-9]{2}:[0-9]{2}:[0-9]{2}$ ]]; then
    echo "Invalid format. Please use YYYY-MM-DD HH:MM:SS"
    exit 1
fi

# Set the system date and time
sudo date -s "$USER_DATETIME"

# Optional: update hardware clock to persist after reboot
sudo hwclock -w

echo "System time updated to $USER_DATETIME"

# Force sync mount options for USB mass storage via udev
#sudo bash -c 'cat > /etc/udev/rules.d/99-usb-sync-mount.rules << EOF
#ACTION=="add", SUBSYSTEMS=="usb", SUBSYSTEM=="block", ENV{ID_FS_USAGE}=="filesystem", \
#    ENV{UDISKS_MOUNT_OPTIONS_DEFAULTS}="sync,noatime"
#EOF'

#sudo udevadm control --reload-rules
#sudo systemctl restart udisks2

# Create a udev rule that calls a mount helper script on USB block device insertion
echo Enabling automatic USB Mount
sudo bash -c 'cat > /etc/udev/rules.d/99-usb-automount.rules << EOF
ACTION=="add",    SUBSYSTEMS=="usb", SUBSYSTEM=="block", ENV{ID_FS_USAGE}=="filesystem", RUN+="/usr/local/bin/usb-mount.sh add %k"
ACTION=="remove", SUBSYSTEMS=="usb", SUBSYSTEM=="block",                                 RUN+="/usr/local/bin/usb-mount.sh remove %k"
EOF'

# Create the mount helper script
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

echo "Enabling I2C"
sudo raspi-config nonint do_i2c 0

#echo "Disabling Desktop by switching to console mode"
#sudo systemctl set-default multi-user.target

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
OnUnitActiveSec=60
AccuracySec=1s
Persistent=true
Unit=logger.service

[Install]
WantedBy=timers.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable logger.timer
#sudo systemctl enable logger.service
sudo systemctl start logger.timer

echo "Setup complete. Please reboot now"