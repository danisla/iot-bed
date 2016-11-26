# Controlling Serta MP III with BLE

You need a bluetooth adapter with BLE support. The [Raspberry Pi 3](https://www.raspberrypi.org/products/raspberry-pi-3-model-b/) and [CHIP](https://getchip.com/pages/chip) single board computers have an integrated bluetooth LE module that you can use to control the base.

### Scanning for the base

Use the `hcitool` command to scan for LE devices and obtain the MAC address of your base.

```
$ sudo hcitool -i hci0 lescan
LE Scan ...
68:9E:19:12:7E:7F (unknown)
F4:B8:5E:B3:20:2B (unknown)
F4:B8:5E:B3:20:2B base-i4.00001202
06:2E:DE:39:5F:0B (unknown)
68:9E:19:12:7E:7F base-i4.0000052
```

In this case, there are 2 bases named `base-i4.00001202` and `base-i4.0000052` respectively.

If you want to explore the device and it's GATT services run this:

```
gatttool -I
> connect 68:9E:19:12:7E:7F
> primary

attr handle: 0x0001, end grp handle: 0x000b uuid: 00001800-0000-1000-8000-00805f9b34fb
attr handle: 0x000c, end grp handle: 0x000f uuid: 00001801-0000-1000-8000-00805f9b34fb
attr handle: 0x0010, end grp handle: 0x0018 uuid: 0000180a-0000-1000-8000-00805f9b34fb
attr handle: 0x0019, end grp handle: 0x001d uuid: 0000ffe0-0000-1000-8000-00805f9b34fb
attr handle: 0x001e, end grp handle: 0x0021 uuid: 0000ffe5-0000-1000-8000-00805f9b34fb
attr handle: 0x0022, end grp handle: 0x0038 uuid: 0000ff20-0000-1000-8000-00805f9b34fb
attr handle: 0x0039, end grp handle: 0x0055 uuid: 0000ff30-0000-1000-8000-00805f9b34fb
attr handle: 0x0056, end grp handle: 0x005c uuid: 0000ff40-0000-1000-8000-00805f9b34fb
attr handle: 0x005d, end grp handle: 0xffff uuid: 0000ff50-0000-1000-8000-00805f9b34fb
```

> the device appears to broadcast a bunch of notifications after connecting, I'm not sure why. Also the device disconnects shortly after connecting which might be because there are multiple remotes (controllers) connected.

Comparing the UUIDs with the list of [standard GATT services](https://www.bluetooth.com/specifications/gatt/services) we see that only the first 3 (`1800`, `1801`, `180a`) appear on the list and the rest are custom manufacturer services (`ffe0`, `ffe5`, etc).

Notice that the handle that we sniffed is not advertised, I'm not sure why this is but you can still get the UUID of it if you ask:

```
[68:9E:19:12:7E:7F][LE]> char-desc 0x020 0x020
handle: 0x0020, uuid: 0000ffe9-0000-1000-8000-00805f9b34fb
```

You can also write one of our captured values to that handle and confirm that it controls the unit:

```
[68:9E:19:12:7E:7F][LE]> connect
Attempting to connect to 68:9E:19:12:7E:7F
Connection successful
[68:9E:19:12:7E:7F][LE]> char-write-cmd 0x020 e5fe1600000008fe
```

### Commanding from CLI

Try to send some of the captured commands to the device like this:

```
# Flat Preset
gatttool -b 68:9E:19:12:7E:7F --char-write --handle=0x0020 --value e5fe1600000008fe
```

```
# Massage Head Add
gatttool -b 68:9E:19:12:7E:7F --char-write --handle=0x0020 --value e5fe1600080000fe
```

These are the commands we'll use to control the device in a [script for our IoT Device](./03_IOT_DEVICE.md)
