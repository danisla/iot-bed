# Device Shadow Controller Script for IoT-Bed

This script connects to the AWS IoT device shadow via MQTT and sends BLE commands using `gatttool` to resolve deltas in the device shadow.

## Overview

Features:

- Bed position presets: Zero-G, Flat, TV/PC
- Massage setting: head and foot 4 levels on and off.

> See the [BLE Control](../../docs/02_BLE_CONTROL.md) guide for details on the BLE protocol.

Sometimes the `gatttool` commands error out so the script tries to send the commands up to 3 times before giving up.

### Faking the Massage 'off' command

Since the massage setting is a single action button to increase massage level, there is no "off" command. The operator has to cycle through all of the massage levels before it turns off.

The state of `massage` is stored as an integer between `0` and `100` that increments by `25` whenever the `massage on` lambda action is fired.

To simulate the "off" command, the Lambda function takes the current value of the massage level, for example `50` and makes it negative, `-50`, the shadow controller script sees that the change is less than 0 so it computes the number of massage levels needed to get back to `0` and sends that many commands in sequence.

```
num_cmds = int((100 - abs(massagePercent)) / 25)
```

### Implementing custom head and foot adjustment angles

Since there is no way to directly command a head or foot angle, adding the ability to control the angle is going to be tricky.

## Running

Install the dependencies:

```
pip install -U AWSIoTPythonSDK
```

Copy the certs and root CA to the same directory as the script before running.

- `device.pem`: IoT certificate
- `device-key.pem`: IoT private key
- `root-CA.crt`: root CA for certificate.

> See the [IoT Device guide](../../docs/03_IOT_DEVICE.md) for how to create the thing and certs.

Export the environment variables:

```
export IOT_ENDPOINT=$(aws iot describe-endpoint | jq -r '.endpointAddress')
export THING_NAME=iot-bed
export BLE_ADDRESS=ADDRESS_OF_BLE_BASE
```

Run the script:

```
python iot-bed.py
```

## Installing as a systemd service

Install script and certs to `/opt/iot-bed` and run as a systemd service:

```
cat > iot-bed.service <<"EOF"
[Unit]
Description=IoT Bed Controller
Wants=network-online.target
After=network-online.target

[Service]
Restart=always
TimeoutStartSec=0
RestartSec=3
Environment=IOT_ENDPOINT=a21frlxo8kxe8s.iot.us-east-1.amazonaws.com
Environment=THING_NAME=iot-bed
Environment=BLE_ADDRESS=F4:B8:5E:B3:20:2B
WorkingDirectory=/opt/iot-bed
ExecStartPre=/bin/bash -c 'until /usr/bin/curl -sf -o /dev/null http://status.aws.amazon.com/data.json; do echo "Waiting for network.."; sleep 5; done'
ExecStart=/usr/bin/python /opt/iot-bed/iot-bed.py

[Install]
WantedBy=multi-user.target
EOF
```

```
sed -i \
  -e s/YOUR_IOT_ENDPOINT/$IOT_ENDPOINT/g \
  -e s/ADDRESS_OF_BLE_BASE/$BLE_ADDRESS/g \
  iot-bed.service
```

```
sudo mv iot-bed.service /etc/systemd/system/
```

```
sudo systemctl daemon-reload
sudo systemctl enable iot-bed
sudo systemctl start iot-bed
```

```
sudo systemctl status iot-bed --no-pager
```

> Remember to copy the certs `device*` and root CA `root-CA.crt` to `/opt/iot-bed/` before starting.

## References

- [aws-iot-device-sdk-python](https://github.com/aws/aws-iot-device-sdk-python)
