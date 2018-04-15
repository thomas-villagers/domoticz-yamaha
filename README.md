# Yamaha AV Receiver - Domoticz Python Plugin
Python plugin for Domoticz to control Yamaha AV Receivers (Aventage Series) via TCP/IP 
![devices](images/devices.png?raw=true "Devices")

## Installation

1. Clone repository into your domoticz plugins folder
```
cd domoticz/plugins
git clone https://github.com/stas-demydiuk/domoticz-yamaha-plugin yamaha-av-receiver
```
2. Restart domoticz
3. Go to "Hardware" page and add new item with type "Yamaha AV Receiver"

## Devices

Plugin creates 6 devices:
| Name         | Description                                                              |
|--------------|--------------------------------------------------------------------------|
| Volume Main  | Controls the volume of main zone and allows to switch it ON/OFF          |
| Input Main   | Controls the input of main zone                                          |
| Volume Zone2 | Controls the volume of zone2 and allows to switch it ON/OFF              |
| Input Zone2  | Controls the input of zone2                                              |
| Party Status | Shows and switches Party mode ON/Off and shows Surround decode           |
| Volume Party | Controls the volume of both zones and allows to switch Party mode ON/OFF |
