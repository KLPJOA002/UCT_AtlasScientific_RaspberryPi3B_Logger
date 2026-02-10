#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "Enabling I2C"
sudo raspi-config nonint do_i2c 0

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
OnBootSec=30
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