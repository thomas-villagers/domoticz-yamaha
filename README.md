# Yamaha AV Receiver - Domoticz Python Plugin
Python plugin for Domoticz to control Yamaha AV Receivers (Aventage Series) via TCP/IP 

![devices](images/devices.png?raw=true "Devices")
![devices](images/remote.png?raw=true "Devices")

## Installation

1. Clone repository into your domoticz plugins folder
```
cd domoticz/plugins
git clone https://github.com/thomas-villagers/domoticz-yamaha.git yamaha-av-receiver
```
2. Restart domoticz
3. Go to "Hardware" page and add new item with type "Yamaha AV Receiver"

Please note that this plugin needs the "updated" Plugin System which is currently only available in the beta-branch of Domoticz. If you're using the stable version of Domoticz you have to fix the parameters for "onMessage", "onCommand" etc. 

## Configuration

| Parameter Name | Value                                                                                                              |
| :---           | :---                                                                                                               |
| Adres IP       | IP Address your Yamaha AV Receiver                                                                                 |
| Port           | Port to HTTP YNCA Command (If you don't know anything about port forwarding, leave 50000)                          |
| Zones          | Select zone to control                                                                                             |
| Input names    | List of available inputs separated by a pipe - you can limit or change to other, ones supported by your Yamaha.    | 
| DSP Programs   | List of DSP Programs separated by a pipe - you can limit or change to other, ones supported by your Yamaha.        |

## Devices

Plugin creates 4 devices for Main Zone:

| Name         | Description                                                              |
| :---         | :---                                                                     |
| Media Player | Allows to switch main zone ON/OFF                                        |
| Volume       | Controls the volume of main zone and allows to MUTE/UNMUTE               |
| Input names  | Controls the input of main zone                                          |
| DSP Program  | Allows to set DSP program for main zone                                  |

3 devices for each additional zone (Zone2, Zone3) if selected in options:

| Name         | Description                                                              |
| :---         | :---                                                                     |
| Media Player | Allows to switch zone ON/OFF                                             |
| Volume       | Controls the volume of zone and allows to MUTE/UNMUTE                    |
| Input names  | Controls the input of zone                                               |

If there is at least one additional zone, plugin creates device to control Party Mode (mode, when all zones synchronously play signal from Main Zone)

| Name         | Description                                                              |
| :---         | :---                                                                     |
| Party        | Allows to switch Party Mode ON/OFF                                       |

## TODO

[-] Implement scenes selection support
