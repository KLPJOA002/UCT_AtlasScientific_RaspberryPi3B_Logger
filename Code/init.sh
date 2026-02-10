#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

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

# Force sync mount options for ALL USB mass storage devices on insertion
sudo bash -c 'cat > /etc/udev/rules.d/99-usb-sync-mount.rules << EOF
ACTION=="add", SUBSYSTEMS=="usb", SUBSYSTEM=="block", ENV{ID_FS_USAGE}=="filesystem", \
    ENV{UDISKS_MOUNT_OPTIONS_DEFAULTS}="sync,noatime"
EOF'

sudo udevadm control --reload-rules
sudo systemctl restart udisks2

echo "Setup complete. All USB drives will now be mounted with sync."

echo "Enabling I2C"
sudo raspi-config nonint do_i2c 0

echo "Disabling Desktop by switching to console mode"
sudo systemctl set-default multi-user.target

echo "Adding system service to run logger"
sudo tee /etc/systemd/system/logger.service > /dev/null << EOF
[Unit]
Description=Minute Data Logger
After=multi-user.target

[Service]
Type=oneshot
ExecStart=/usr/bin/python3 $SCRIPT_DIR/logger.py
User=pi
WorkingDirectory=$SCRIPT_DIR
EOF

echo "Adding time service to periodically run logger"
sudo tee /etc/systemd/system/logger.timer > /dev/null << EOF
[Unit]
Description=Run data logger every minute

[Timer]
OnBootSec=10
OnUnitActiveSec=60
AccuracySec=1s
Persistent=true

[Install]
WantedBy=timers.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable logger.timer
sudo systemctl start logger.timer

echo "Setup complete. Please reboot now"