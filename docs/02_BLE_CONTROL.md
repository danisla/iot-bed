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

We can also dump all of the devices characteristics:

```
> connect
> characteristics

handle: 0x0002, char properties: 0x02, char value handle: 0x0003, uuid: 00002a00-0000-1000-8000-00805f9b34fb
handle: 0x0004, char properties: 0x02, char value handle: 0x0005, uuid: 00002a01-0000-1000-8000-00805f9b34fb
handle: 0x0006, char properties: 0x0a, char value handle: 0x0007, uuid: 00002a02-0000-1000-8000-00805f9b34fb
handle: 0x0008, char properties: 0x08, char value handle: 0x0009, uuid: 00002a03-0000-1000-8000-00805f9b34fb
handle: 0x000a, char properties: 0x02, char value handle: 0x000b, uuid: 00002a04-0000-1000-8000-00805f9b34fb
handle: 0x000d, char properties: 0x20, char value handle: 0x000e, uuid: 00002a05-0000-1000-8000-00805f9b34fb
handle: 0x0011, char properties: 0x02, char value handle: 0x0012, uuid: 00002a23-0000-1000-8000-00805f9b34fb
handle: 0x0013, char properties: 0x02, char value handle: 0x0014, uuid: 00002a24-0000-1000-8000-00805f9b34fb
handle: 0x0015, char properties: 0x02, char value handle: 0x0016, uuid: 00002a28-0000-1000-8000-00805f9b34fb
handle: 0x0017, char properties: 0x02, char value handle: 0x0018, uuid: 00002a29-0000-1000-8000-00805f9b34fb
handle: 0x001a, char properties: 0x10, char value handle: 0x001b, uuid: 0000ffe4-0000-1000-8000-00805f9b34fb
handle: 0x001f, char properties: 0x08, char value handle: 0x0020, uuid: 0000ffe9-0000-1000-8000-00805f9b34fb
handle: 0x0023, char properties: 0x08, char value handle: 0x0024, uuid: 0000ff21-0000-1000-8000-00805f9b34fb
handle: 0x0026, char properties: 0x08, char value handle: 0x0027, uuid: 0000ff22-0000-1000-8000-00805f9b34fb
handle: 0x0029, char properties: 0x08, char value handle: 0x002a, uuid: 0000ff23-0000-1000-8000-00805f9b34fb
handle: 0x002c, char properties: 0x08, char value handle: 0x002d, uuid: 0000ff24-0000-1000-8000-00805f9b34fb
handle: 0x002f, char properties: 0x08, char value handle: 0x0030, uuid: 0000ff25-0000-1000-8000-00805f9b34fb
handle: 0x0032, char properties: 0x08, char value handle: 0x0033, uuid: 0000ff26-0000-1000-8000-00805f9b34fb
handle: 0x0035, char properties: 0x10, char value handle: 0x0036, uuid: 0000ff2f-0000-1000-8000-00805f9b34fb
handle: 0x003a, char properties: 0x0a, char value handle: 0x003b, uuid: 0000ff31-0000-1000-8000-00805f9b34fb
handle: 0x003d, char properties: 0x0a, char value handle: 0x003e, uuid: 0000ff32-0000-1000-8000-00805f9b34fb
handle: 0x0040, char properties: 0x0a, char value handle: 0x0041, uuid: 0000ff33-0000-1000-8000-00805f9b34fb
handle: 0x0043, char properties: 0x0a, char value handle: 0x0044, uuid: 0000ff34-0000-1000-8000-00805f9b34fb
handle: 0x0046, char properties: 0x08, char value handle: 0x0047, uuid: 0000ff35-0000-1000-8000-00805f9b34fb
handle: 0x0049, char properties: 0x0a, char value handle: 0x004a, uuid: 0000ff36-0000-1000-8000-00805f9b34fb
handle: 0x004c, char properties: 0x04, char value handle: 0x004d, uuid: 0000ff37-0000-1000-8000-00805f9b34fb
handle: 0x004f, char properties: 0x10, char value handle: 0x0050, uuid: 0000ff3f-0000-1000-8000-00805f9b34fb
handle: 0x0057, char properties: 0x02, char value handle: 0x0058, uuid: 0000ff41-0000-1000-8000-00805f9b34fb
handle: 0x005a, char properties: 0x02, char value handle: 0x005b, uuid: 0000ff42-0000-1000-8000-00805f9b34fb
handle: 0x005e, char properties: 0x08, char value handle: 0x005f, uuid: 0000ff51-0000-1000-8000-00805f9b34fb
handle: 0x0061, char properties: 0x08, char value handle: 0x0062, uuid: 0000ff52-0000-1000-8000-00805f9b34fb
handle: 0x0064, char properties: 0x02, char value handle: 0x0065, uuid: 0000ff53-0000-1000-8000-00805f9b34fb
handle: 0x0067, char properties: 0x0a, char value handle: 0x0068, uuid: 0000ff54-0000-1000-8000-00805f9b34fb
handle: 0x006a, char properties: 0x10, char value handle: 0x006b, uuid: 0000ff5f-0000-1000-8000-00805f9b34fb
```

Again you can compare these with the [standard GATT characteristics](https://www.bluetooth.com/specifications/gatt/characteristics) and see that ther are some standard ones implemented that start with `00002a` and the rest are custom.

> Note that there are other apps that connect to BLE devices like the [LightBlue Explorer App for iOS](https://itunes.apple.com/us/app/lightblue-explorer-bluetooth/id557428110) that can decode some of the more common characteristics.

Using the `char-write-cmd` you can write one of our captured values to that handle and confirm that it controls the unit:

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
