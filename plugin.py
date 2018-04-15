# Basic Python Plugin 
#
# Author: thomas-villagers
#
"""
<plugin key="YamahaPlug" name="Yamaha AV Receiver" author="thomasvillagers" version="1.0.0" wikilink="http://www.domoticz.com/wiki/plugins/plugin.html" externallink="https://yamaha.com/products/audio_visual/av_receivers_amps/">
    <params>
     <param field="Address" label="IP Address" width="200px" required="true" default="127.0.0.1"/>
     <param field="Port" label="Port" width="50px" required="true" default="50000"/>
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
    def __init__(self, inputDeviceUnit, volumeDeviceUnit):
        self.active = False
        self.input = ''
        self.volume = ''
        self.inputDevice = Devices[inputDeviceUnit]
        self.volumeDevice = Devices[volumeDeviceUnit]
        self.inputDeviceUnit = inputDeviceUnit
        self.volumeDeviceUnit = volumeDeviceUnit

    def setActive(self, isActive):
        nValue = 1 if isActive else 0
        UpdateDevice(self.volumeDeviceUnit, nValue, self.volumeDevice.sValue)
        UpdateDevice(self.inputDeviceUnit, nValue, self.inputDevice.sValue)

    def setVolume(self, dB):
        vol = float(dB)
        volume = int(vol*5/4 + 100)  # Min -80 db, max -0 db

        UpdateDevice(self.volumeDeviceUnit, self.inputDevice.nValue, volume)

    def setInput(self, inputName):
        inputDevice = self.inputDevice

        if inputDevice.Options:
            listLevelNames = inputDevice.Options["LevelNames"].split("|")
            count = 0
            for levelName in listLevelNames:
                if (levelName == inputName):
                    self.input = str(int(count))
                    break
                count += 10

        UpdateDevice(self.inputDeviceUnit, inputDevice.nValue, self.input)


class BasePlugin:
    enabled = False
    isConnected = True
    outstandingPings = 0
    nextConnect = 0
    commandArray = ["@MAIN:PWR=?", "@ZONE2:PWR=?", "@MAIN:SOUNDPRG=?", "@MAIN:VOL=?", "@MAIN:INP=?", "@MAIN:MUTE=?", "@ZONE2:VOL=?", "@ZONE2:MUTE=?", "@ZONE2:INP=?", "@SYS:PARTY=?"]

    def __init__(self):
        #self.var = 123
        return

    def onStart(self):
        if Parameters["Mode6"] == "Debug":
           Domoticz.Debugging(1)

        Domoticz.Debug("onStart called")
        inputControlOptions = { 
            "LevelActions" : "||||||||||||||||",
            "LevelNames"   : "Off|HDMI1|HDMI2|HDMI3|HDMI4|HDMI5|HDMI6|HDMI7|Spotify|TUNER|Airplay|AV1|AV2|AV3|AV4|AV5|AV6|NET RADIO",
            "LevelOffHidden" : "true",
            "SelectorStyle" : "1" 
        }

        if 1 not in Devices: 
            Domoticz.Debug("Create Party Status Device")
            Domoticz.Device(Name="Party Status", Unit=1, Type=17,  Switchtype=17, Used=1).Create()          
        if 2 not in Devices: 
            Domoticz.Debug("Create Volume Device - Main")
            Domoticz.Device(Name="Volume Main", Unit=2, Type=244, Subtype=73, Switchtype=7, Image=8, Used=1).Create()
        if 3 not in Devices: 
            Domoticz.Debug("Create Input Device - Main")
            Domoticz.Device(Name="Input Main", Unit=3, TypeName="Selector Switch", Options=inputControlOptions, Used=1).Create()
        if 4 not in Devices: 
            Domoticz.Debug("Create Volume Device - Zone2")
            Domoticz.Device(Name="Volume Zone2", Unit=4, Type=244, Subtype=73, Switchtype=7, Image=8, Used=1).Create()
        if 5 not in Devices: 
            Domoticz.Debug("Create Input Device - Zone2")
            Domoticz.Device(Name="Input Zone2", Unit=5, TypeName="Selector Switch", Options=inputControlOptions, Used=1).Create()        
        if 6 not in Devices: 
            Domoticz.Debug("Create Volume Device - Party")
            Domoticz.Device(Name="Volume Party", Unit=6, Type=244, Subtype=73, Switchtype=7, Image=8, Used=1).Create()
            
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

        mainZone = Zone(3, 2)
        zone2 = Zone(5, 4)

        for line in strData.splitlines():
            arrData = line.split('=')
            if (arrData[0] == "@SYS:PARTY"):
                if (arrData[1] == "On") and (Devices[1].nValue != 1):
                    UpdateDevice(1, 1, "PARTY - " + Devices[1].sValue)
                elif (arrData[1] == "Off") and (Devices[1].nValue != 0):
                    UpdateDevice(1, 0, Devices[1].sValue.replace("PARTY - ", ""))
            elif (arrData[0] == "@MAIN:SOUNDPRG"):
                if (Devices[1].nValue == 0):
                    sValue = arrData[1]
                else:
                    sValue = "PARTY - " + arrData[1]
                if (Devices[1].sValue != sValue):
                    UpdateDevice(1, Devices[1].nValue, sValue)
            elif (arrData[0] == "@MAIN:PWR"):
                mainZone.setActive(arrData[1] == "On")
            elif (arrData[0] == "@MAIN:INP"):
                mainZone.setInput(arrData[1])
            elif (arrData[0] == "@MAIN:VOL"):
                mainZone.setVolume(arrData[1])
            # elif (arrData[0] == "@MAIN:MUTE"):
            #     mainZone.setActive(arrData[1] == "Off")
            elif (arrData[0] == "@ZONE2:PWR"):
                zone2.setActive(arrData[1] == "On")
            elif (arrData[0] == "@ZONE2:INP"):
                zone2.setInput(arrData[1])
            elif (arrData[0] == "@ZONE2:VOL"):
                zone2.setVolume(arrData[1])
            # elif (arrData[0] == "@ZONE2:MUTE"):
            #     zone2.setActive(arrData[1] == "Off")
                
        if (Devices[3].nValue == 0) and (Devices[5].nValue == 0) and (Devices[6].nValue != 0): # If both zones OFF, set Party OFF
            UpdateDevice(6, 0, 0)
                    
    def onCommand(self, Unit, Command, Level, Hue):
        Domoticz.Debug("onCommand called for Unit " + str(Unit) + ": Parameter '" + str(Command) + "', Level: " + str(Level) + "', Hue: " + str(Hue))
        if (self.isConnected == False):
            self.connection.Connect() 
            return
        
        if (Unit == 1):  # Display (Party) Status and switch PARTY on/off
           if (Command == "Off"):
                self.connection.Send("@SYS:PARTY=Off\r\n")
           elif (Command == "On"): 
                self.connection.Send("@SYS:PARTY=On\r\n")
          
        elif (Unit == 2): # Main Volume, mute and ON/OFF
            if (Command == "Set Level"): 
                volume = int(Level)*4/5 - 80   # Min -80 db, max 0 db
                if int(Level) == 0: # Set Mute on if slider at Min
                    self.connection.Send("@MAIN:MUTE=On\r\n")
                else:
                    volumeToSend = round(2*volume)/2  
                    self.connection.Send("@MAIN:VOL="+str(volumeToSend)+"\r\n")
                
            elif (Command == "Off"): 
                 self.connection.Send("@MAIN:PWR=Standby\r\n")
            elif (Command == "On"): 
                 self.connection.Send("@MAIN:PWR=On\r\n")
                 
        elif (Unit == 3): # Main Input selection
            if Devices[Unit].Options:
                listLevelNames = Devices[Unit].Options["LevelNames"].split("|")
                NewLevel = int(int(Level)/10)
                listInput = listLevelNames[NewLevel].split(" ")
                input = str(listInput[0]) #First element (text before space) must be Input
                self.connection.Send("@MAIN:INP=" + input + "\r\n")
                if str(listInput[0]) == "Off": # Also used to turn OFF
                    self.connection.Send("@MAIN:PWR=Standby\r\n")

        elif (Unit == 4): # ZONE2 Volume, mute and ON/OFF 
            if (Command == "Set Level"): 
              #  volume = int(Level)*4/10 - 60 # Min -60 db, max -20 db
                volume = int(Level)*4/5 - 80   # Min -80 db, max 0 db
                if int(Level) == 0: # Set Mute on if slider at Min
                    self.connection.Send("@ZONE2:MUTE=On\r\n")
                else:
                    volumeToSend = round(2*volume)/2  
                    self.connection.Send("@ZONE2:VOL="+str(volumeToSend)+"\r\n")
                
            elif (Command == "Off"): 
                 self.connection.Send("@ZONE2:PWR=Standby\r\n")
            elif (Command == "On"): 
                 self.connection.Send("@ZONE2:PWR=On\r\n")
                 
        elif (Unit == 5): # ZONE2 Input selection
            if Devices[Unit].Options:
                listLevelNames = Devices[Unit].Options["LevelNames"].split("|")
                NewLevel = int(int(Level)/10)
                listInput = listLevelNames[NewLevel].split(" ")
                input = str(listInput[0]) #First element (text before space) must be Input
                self.connection.Send("@ZONE2:INP=" + input + "\r\n")
                if str(listInput[0]) == "Off": # Also used to turn OFF
                    self.connection.Send("@ZONE2:PWR=Standby\r\n")

        elif (Unit == 6): # Dual Volume, mute and ON/ All OFF
            if (Command == "Set Level"): 
                volume = int(Level)*4/5 - 80   # Min -80 db, max 0 db
                if int(Level) == 0: # Set Mute on if slider at Min
                    self.connection.Send("@ZONE2:MUTE=On\r\n")
                    self.connection.Send("@MAIN:MUTE=On\r\n")
                else:
                    volumeToSend = round(2*volume)/2
                    volMain  = round(2*int(Devices[2].sValue)*4/5 - 80)/2
                    volZone2 = round(2*int(Devices[4].sValue)*4/5 - 80)/2
                    volDifference = volMain - volZone2 # Main Vol - Zone2 Vol
                    self.connection.Send("@MAIN:VOL="+str(volumeToSend)+"\r\n")
                    volumeToSend -= volDifference
                    self.connection.Send("@ZONE2:VOL="+str(volumeToSend)+"\r\n")
            elif (Command == "Off"): 
                 self.connection.Send("@MAIN:PWR=Standby\r\n")
                 self.connection.Send("@ZONE2:PWR=Standby\r\n")
                 self.connection.Send("@SYS:PWR=Standby\r\n")
            elif (Command == "On"):
                 self.connection.Send("@MAIN:PWR=On\r\n")
                 
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
                self.outstandingPings = self.outstandingPings + len(self.commandArray)
                for command in self.commandArray:
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

def stringToBase64(s):
    return base64.b64encode(s.encode('utf-8')).decode("utf-8")

def base64ToString(b):
    return base64.b64decode(b).decode('utf-8')
