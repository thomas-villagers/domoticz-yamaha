# Basic Python Plugin 
#
# Author: thomas-villagers
#
"""
<plugin key="YamahaPlug" name="Yamaha AV Receiver with Kodi Remote" author="thomasvillagers" version="2.0.0" wikilink="http://www.domoticz.com/wiki/plugins/plugin.html" externallink="https://yamaha.com/products/audio_visual/av_receivers_amps/">
    <params>
     <param field="Address" label="IP Address" width="200px" required="true" default="127.0.0.1"/>
     <param field="Port" label="Port" width="50px" required="true" default="50000"/>
     <param field="Mode1" label="Zones" width="200px">
       <options>
          <option label="Main zone" value="1" default="true"/>
          <option label="Main zone + Zone2" value="2"/>
          <option label="Main zone + Zone2 + Zone3" value="3"/>
       </options>
     </param>
     <param field="Mode2" label="Input names" width="400px" required="true" default="Off|SIRIUS|TUNER|HDMI1|HDMI2|HDMI3|HDMI4|HDMI5|HDMI6|HDMI7|AV1|AV2|AV3|AV4|AV5|AV6|V-AUX|AUDIO1|AUDIO2|DOCK|iPod|Bluetooth|UAW|NET|Rhapsody|SIRIUS InternetRadio|Pandora|Napster|PC|NET RADIO|USB|iPod (USB)"/>
     <param field="Mode3" label="DSP Programs" width="400px" required="true" default="Off|Hall in Munich|Hall in Vienna|Chamber|Cellar Club|The Roxy Theatre|The Bottom Line|Sports|Spotify|Action Game|Roleplaying Game|Music Video|Standard|Spectacle|Sci-Fi|Adventure|Drama|Mono Movie|2ch Stereo|7ch Stereo|Surround Decoder"/>
     <param field="Mode6" label="Debug" width="75px">
       <options>
          <option label="True" value="Debug"/>
          <option label="False" value="Normal" default="true" />
       </options>
     </param>
    </params>
</plugin>
"""
import Domoticz
import base64

class Zone:
    def __init__(self, zoneIndex):
        self.zoneIndex = zoneIndex
        self.zoneKey = '@MAIN' if zoneIndex == 1 else '@ZONE' + str(zoneIndex)
        self.zoneName = 'Main' if zoneIndex == 1 else 'Zone' + str(zoneIndex)

        self.mediaDeviceUnit = 10 * zoneIndex
        self.volumeDeviceUnit = 10 * zoneIndex + 1
        self.inputDeviceUnit = 10 * zoneIndex + 2
        self.dspDeviceUnit = 10 * zoneIndex + 3

        self.remoteKEY ={
                         "VolumeUp"       : self.zoneKey + ":VOL=Up",
                         "VolumeDown"     : self.zoneKey + ":VOL=Down",
                         "Mute"           : self.zoneKey + ":MUTE=On/Off",
                         "Stop"           : "@MAIN:PLAYBACK=Stop",
                         "BigStepBack"    : "@MAIN:PLAYBACK=Skip Rev",
                         "Rewind"         : "@MAIN:PLAYBACK=Skip Rev",
                         "PlayPause"      : "@MAIN:PLAYBACK=Play",
                         "FastForward"    : "@MAIN:PLAYBACK=Skip Fwd",
                         "BigStepForward" : "@MAIN:PLAYBACK=Skip Fwd",
                         # This below does not work for my RX-V575, I replace it with remote codes
                         # Please test this on other Yamaha AVs and please fixed it.
                         "Home"           : "@SYS:REMOTECODE=7A85A0DF", #"@MAIN:LISTMENU=Back to home",
                         "ContextMenu"    : "@SYS:REMOTECODE=7A856B14", #"@MAIN:LISTMENU=Menu",
                         "Select"         : "@SYS:REMOTECODE=7A85DE21", #"@MAIN:LISTCURSOR=Sel",
                         "Back"           : "@SYS:REMOTECODE=7A85AA55", #"@MAIN:LISTCURSOR=Back",
                         "Up"             : "@SYS:REMOTECODE=7A859D62", #"@MAIN:LISTCURSOR=Up",
                         "Down"           : "@SYS:REMOTECODE=7A859C63", #"@MAIN:LISTCURSOR=Down",
                         "Left"           : "@SYS:REMOTECODE=7A859F60", #"@MAIN:LISTCURSOR=Left",
                         "Right"          : "@SYS:REMOTECODE=7A859E61"  #"@MAIN:LISTCURSOR=Right",
                         # Not used - does anyone have any idea for this?
                         #"Info"           : "",
                         #"Channels"       : "",
                         #"ChannelUp"      : "",
                         #"ChannelDown"    : "",
                         #"ShowSubtitles"  : "",
                         #"FullScreen"     : ""
                        }

    def checkDevices(self):
        iconName = 'Yamaha'
        iconID = Images[iconName].ID

        inputControlOptions = { 
            "LevelActions" : "",
            "LevelNames"   : Parameters["Mode2"],
            "LevelOffHidden" : "true",
            "SelectorStyle" : "1" 
        }

        dspProgramsOptions = {
            "LevelActions" : "",
            "LevelNames"   : Parameters["Mode3"],
            "LevelOffHidden" : "true",
            "SelectorStyle" : "1"
        }

        if self.mediaDeviceUnit not in Devices:
            Domoticz.Debug("Create Media Device - " + self.zoneName)
            Domoticz.Device(Name=self.zoneName, Unit=self.mediaDeviceUnit, Type=17,  Switchtype=17, Image=iconID, Used=1).Create()    

        if self.volumeDeviceUnit not in Devices: 
            Domoticz.Debug("Create Volume Device - " + self.zoneName)
            Domoticz.Device(Name="Volume " + self.zoneName, Unit=self.volumeDeviceUnit, Type=244, Subtype=73, Switchtype=7, Image=8, Used=1).Create()

        if self.inputDeviceUnit not in Devices: 
            Domoticz.Debug("Create Input Device - " + self.zoneName)
            Domoticz.Device(Name="Input " + self.zoneName, Unit=self.inputDeviceUnit, TypeName="Selector Switch", Options=inputControlOptions, Image=iconID, Used=1).Create()

        if self.zoneIndex == 1 and self.dspDeviceUnit not in Devices:
            Domoticz.Debug("Create DSP Program Device - " + self.zoneName)
            Domoticz.Device(Name="DSP Program " + self.zoneName, Unit=self.dspDeviceUnit, TypeName="Selector Switch", Options=dspProgramsOptions, Image=iconID, Used=1).Create()

    def getMediaDevice(self):
        return Devices[self.mediaDeviceUnit]

    def getInputDevice(self):
        return Devices[self.inputDeviceUnit]

    def getVolumeDevice(self):
        return Devices[self.volumeDeviceUnit]

    def getDspProgramDevice(self):
        return Devices[self.dspDeviceUnit]

    def getLevelName(self, device, level):
        listLevelNames = device.Options["LevelNames"].split("|")
        levelIndex = int(int(level)/10)
        return listLevelNames[levelIndex]

    def handleMessage(self, command, value):
        arrData = command.split(':')
        zoneKey = arrData[0]
        command = arrData[1]

        if (zoneKey != self.zoneKey):
            return

        if (command == "PWR"):
            nValue = 1 if value == "On" else 0
            UpdateDevice(self.mediaDeviceUnit, nValue, self.getMediaDevice().sValue)
        elif (command == "INP"):
            self.setInput(value)
        elif (command == "VOL"):
            self.setVolume(value)
        elif (command == "MUTE"):
            nValue = 1 if value == "Off" else 0
            UpdateDevice(self.volumeDeviceUnit, nValue, self.getVolumeDevice().sValue)
        elif (self.zoneKey == '@MAIN' and command == 'SOUNDPRG'):
             self.setDspProgram(value)

    def getYncaStatusCommands(self):
        yncaCommands = [self.zoneKey + ":PWR=?", self.zoneKey + ":VOL=?", self.zoneKey + ":INP=?", self.zoneKey + ":MUTE=?"]

        if (self.zoneIndex == 1):
            yncaCommands.append(self.zoneKey + ":SOUNDPRG=?")

        return yncaCommands

    def getYncaControlCommands(self, unit, command, level):
        yncaCommands = []

        if (unit == self.mediaDeviceUnit):
            if (command == "Off"): 
                 yncaCommands.append(self.zoneKey + ":PWR=Standby")
            elif (command == "On"): 
                 yncaCommands.append(self.zoneKey + ":PWR=On")
            elif (command in self.remoteKEY):
                 yncaCommands.append(self.remoteKEY[command])

        if (unit == self.volumeDeviceUnit): # Volume, mute and ON/OFF
            if (command == "Set Level"): 
                volume = int(level)*4/5 - 80   # Min -80 db, max 0 db
                if int(level) == 0: # Set Mute on if slider at Min
                    yncaCommands.append(self.zoneKey + ':MUTE=On')
                else:
                    volumeToSend = round(2*volume)/2  
                    yncaCommands.append(self.zoneKey + ":VOL="+str(volumeToSend))
            elif (command == "Off"): 
                 yncaCommands.append(self.zoneKey + ":MUTE=On")
            elif (command == "On"): 
                 yncaCommands.append(self.zoneKey + ":MUTE=Off")
                 
        if (unit == self.inputDeviceUnit): # Input selection
            if (level == 0): # Level "Off"
                yncaCommands.append(self.zoneKey + ":PWR=Standby")
            else:
                device = self.getInputDevice()
                inputName = self.getLevelName(device, level)
                yncaCommands.append(self.zoneKey + ":INP=" + inputName)

        if (unit == self.dspDeviceUnit): # DSP Program selection
            if (level == 0): # Level "Off"
                yncaCommands.append(self.zoneKey + ":PWR=Standby")
            else:
                device = self.getDspProgramDevice()
                programName = self.getLevelName(device, level)
                yncaCommands.append(self.zoneKey + ":SOUNDPRG=" + programName)
        
        return yncaCommands

    def setActive(self, isActive):
        nValue = 1 if isActive else 0
        UpdateDevice(self.mediaDeviceUnit, nValue, self.getVolumeDevice().sValue)

    def setVolume(self, dB):
        vol = float(dB)
        volume = int(vol*5/4 + 100)  # Min -80 db, max -0 db

        UpdateDevice(self.volumeDeviceUnit, self.getVolumeDevice().nValue, volume)

    def setDspProgram(self, programName):
        device = self.getDspProgramDevice()

        if device.Options:
            listLevelNames = device.Options["LevelNames"].split("|")
            count = 0
            for levelName in listLevelNames:
                if (levelName == programName):
                    UpdateDevice(self.dspDeviceUnit, 1, str(int(count)))
                    break
                count += 10

    def setInput(self, inputName):
        device = self.getInputDevice()

        if device.Options:
            listLevelNames = device.Options["LevelNames"].split("|")
            count = 0
            for levelName in listLevelNames:
                if (levelName == inputName):
                    UpdateDevice(self.inputDeviceUnit, 1, str(int(count)))
                    break
                count += 10

class PartyMode:
    def __init__(self):
        self.mediaDeviceUnit = 1

    def checkDevices(self):
        iconName = 'Yamaha'
        iconID = Images[iconName].ID

        if self.mediaDeviceUnit not in Devices: 
            Domoticz.Debug("Create Party Status Device")
            Domoticz.Device(Name="Party", Unit=self.mediaDeviceUnit, Type=17,  Switchtype=17, Image=iconID, Used=1).Create()

    def getMediaDevice(self):
        return Devices[self.mediaDeviceUnit]

    def getYncaStatusCommands(self):
        return ["@SYS:PARTY=?"]

    def getYncaControlCommands(self, unit, command, level):
        yncaCommands = []

        if (unit == self.mediaDeviceUnit):
            if (command == "Off"): 
                 yncaCommands.append("@SYS:PARTY=Off")
            elif (command == "On"): 
                 yncaCommands.append("@SYS:PARTY=On")

        return yncaCommands

    def handleMessage(self, command, value):
        if (command == "@SYS:PARTY"):
            nValue = 1 if value == "On" else 0
            UpdateDevice(self.mediaDeviceUnit, nValue, self.getMediaDevice().sValue)

class BasePlugin:
    enabled = False
    isConnected = True
    outstandingPings = 0
    nextConnect = 0
    iconName = 'Yamaha'

    def onStart(self):
        if Parameters["Mode6"] == "Debug":
           Domoticz.Debugging(1)

        Domoticz.Debug("onStart called")

        if self.iconName not in Images:
            Domoticz.Image('icons.zip').Create()
        
        iconID = Images[self.iconName].ID

        self.zones = []

        for x in range(1, int(Parameters["Mode1"]) + 1):
            self.zones.append(Zone(x))

        if (int(Parameters["Mode1"]) > 1):
            self.zones.append(PartyMode())

        for zone in self.zones:
            zone.checkDevices()        
            
        self.connection = Domoticz.Connection(Name="Yamaha connection", Transport="TCP/IP", Protocol="Line", Address=Parameters["Address"], Port=Parameters["Port"])
        self.connection.Connect()
        Domoticz.Heartbeat(20)

    def onStop(self):
        Domoticz.Log("onStop called")

    def onConnect(self, Connection, Status, Description):
        Domoticz.Debug("onConnect called. Status: " + str(Status))
        if (Status == 0): 
          self.isConnected = True
          self.onHeartbeat()
        else: 
          self.isConnected = False

    def onMessage(self, Connection, Data):
        Domoticz.Debug("onMessage called")
        self.outstandingPings = self.outstandingPings - 1
        strData = Data.decode("utf-8", "ignore")
        Domoticz.Debug(strData)

        for line in strData.splitlines():
            arrData = line.split('=')
            command = arrData[0]
            value = arrData[1]

            for zone in self.zones:
                zone.handleMessage(command, value)

    def onCommand(self, Unit, Command, Level, Hue):
        Domoticz.Debug("onCommand called for Unit " + str(Unit) + ": Parameter '" + str(Command) + "', Level: " + str(Level) + "', Hue: " + str(Hue))
        if (self.isConnected == False):
            self.connection.Connect() 
            return
        
        yncaCommands = []

        for zone in self.zones:
            yncaCommands.extend(zone.getYncaControlCommands(Unit, Command, Level))

        for command in yncaCommands:
            self.connection.Send(command + "\r\n")

    def onNotification(self, Data):
        Domoticz.Debug("onNotification: " + str(Data))

    def onDisconnect(self, Connection):
        Domoticz.Debug("onDisconnect called")
        self.isConnected = False 

    def onHeartbeat(self):
        Domoticz.Debug("onHeartbeat called. Connected: " + str(self.isConnected))
        if (self.isConnected == True):
            if (self.outstandingPings > 6):
                Domoticz.Debug("Missed more than 6 pings - disconnect")
                self.connection.Disconnect()  # obsolete 
                self.nextConnect = 0
            else:   
                yncaCommands = []

                for zone in self.zones:
                    yncaCommands.extend(zone.getYncaStatusCommands())

                self.outstandingPings = self.outstandingPings + len(yncaCommands)
                for command in yncaCommands:
                    self.connection.Send(command + "\r\n")
        else: 
            self.outstandingPings = 0
            self.nextConnect = self.nextConnect - 1
            if (self.nextConnect <= 0):
                self.nextConnect = 3
                self.connection.Connect()  # obsolete 

global _plugin
_plugin = BasePlugin()

def onStart():
    global _plugin
    _plugin.onStart()

def onStop():
    global _plugin
    _plugin.onStop()

def onConnect(Connection, Status, Description):
    global _plugin
    _plugin.onConnect(Connection, Status, Description)

def onMessage(Connection, Data):
    global _plugin
    _plugin.onMessage(Connection, Data)

def onCommand(Unit, Command, Level, Hue):
    global _plugin
    _plugin.onCommand(Unit, Command, Level, Hue)

def onNotification(Data):
    global _plugin
    _plugin.onNotification(Data)

def onDisconnect(Connection):
    global _plugin
    _plugin.onDisconnect(Connection)

def onHeartbeat():
    global _plugin
    _plugin.onHeartbeat()

def UpdateDevice(Unit, nValue, sValue):
    # Make sure that the Domoticz device still exists (they can be deleted) before updating it 
    if (Unit in Devices):
        if (Devices[Unit].nValue != nValue) or (Devices[Unit].sValue != str(sValue)):
            Domoticz.Log("Update " + str(Devices[Unit].nValue) + " -> " + str(nValue)+",'" + Devices[Unit].sValue + "' => '"+str(sValue)+"' ("+Devices[Unit].Name+")")
            Devices[Unit].Update(nValue, str(sValue))
    return

    # Generic helper functions
def DumpConfigToLog():
    for x in Parameters:
        if Parameters[x] != "":
            Domoticz.Debug( "'" + x + "':'" + str(Parameters[x]) + "'")
    Domoticz.Debug("Device count: " + str(len(Devices)))
    for x in Devices:
        Domoticz.Debug("Device:           " + str(x) + " - " + str(Devices[x]))
        Domoticz.Debug("Device ID:       '" + str(Devices[x].ID) + "'")
        Domoticz.Debug("Device Name:     '" + Devices[x].Name + "'")
        Domoticz.Debug("Device DeviceID:  " + str(Devices[x].DeviceID))
        Domoticz.Debug("Device nValue:    " + str(Devices[x].nValue))
        Domoticz.Debug("Device sValue:   '" + Devices[x].sValue + "'")
        Domoticz.Debug("Device LastLevel: " + str(Devices[x].LastLevel)) 
    return
