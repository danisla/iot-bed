#!/bin/bash

echo "Bring hci0 up..."
hciconfig hci0 up
sleep 1
bt-adapter -l
sleep 1
bt-adapter -l

echo "Scanning for BLE devices"
timeout 5s hcitool lescan

echo "Bluetooth initialized"
exit 0
