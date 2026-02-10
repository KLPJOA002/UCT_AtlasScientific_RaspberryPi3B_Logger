# **Atlas Scientific Sensor Logger **
System to automatically log Atlas Scientific sensor data from I4 interLink.
---
This system uses a Raspberry Pi 3 B to read the sensor data using the I2C protocol. The system periodically logs the sensor data over the course of several hours. The code then stores the log data on individual files for each sensor read and for each sensor device.

This repo includes an initilisation file init.sh to automatically configure the Raspberry Pi with the required settings to enable the long term logging.

To use:
install a default edition of Raspberry Pi OS (64 bit) for a Pi 3 B onto a micro sd Card. Use the following OS configuration settings:
1. hostname:pi
2. Default Time configuration
3. Username: pi
4. Password: any
5. Wifi: unrequired
6. SSH: disabled


Connect the Atlas Scientific I4 interLink to the sensor and connect the circuits required for the sensor.
Connect the I4 interLink to the Raspberry Pi 3 board using the 3.3V line as VCC, Ground ans GND, SDA to pin3, SCL to pin 5
This should allow the Pi to communincate to the sensor circuit using the I2C protocol

Boot the install on a raspberry pi 3 (keyboard and monitor required)
Add the files located in the Files to Load directory
using the terminal rooted in the files location, enter the command bash init.sh

Follow the terminal prompts

Once the terminal indicates so, Reboot the Pi

The Pi should now automatically run the logger program every minute and store the resulting data in a connected USB drive.
If the USB drive is removed, the program will continue to run however the log data will be discarded.
Once a USB drive is re-inserted, the program will continue to write the logs to that USB.

