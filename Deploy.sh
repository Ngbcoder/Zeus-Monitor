#!/bin/bash
sudo systemctl stop uno-monitor.service
arduino-cli compile --fqbn arduino:avr:uno uno
arduino-cli upload --fqbn arduino:avr:uno --port /dev/ttyUSB0 uno
sudo systemctl start uno-monitor.service