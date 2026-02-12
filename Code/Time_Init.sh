#!/bin/bash
#SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

#Script written for the purpose of initilising and setting a DS3231 RTC a Raspberry Pi 3B or Pi Zero 2 W
# Written for the University of Cape Town Research Group
# Written by Joab Gray Kloppers: KLPJOA002
# Disclaimer: Parts of this code were created with the use of AI tools including: ChatGPT, ClaudeAi

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
echo "System time update complete. you can shutdown the pi now"