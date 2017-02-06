# Basic Python Plugin Example
#
# Author: GizMoCuz
#
"""
<plugin key="YamahaPlug" name="Yamaha AV Receiver" author="thomasvillagers" version="1.0.0" wikilink="http://www.domoticz.com/wiki/plugins/plugin.html" externallink="https://www.google.com/">
    <params>
     <param field="Address" label="IP Address" width="200px" required="true" default="127.0.0.1"/>
     <param field="Port" label="Port" width="50px" required="true" default="50000"/>
     <param field="Mode6" label="Debug" width="75px">
       <options>
          <option label="True" value="Debug"/>
          <option label="False" value="Normal"  default="true" />
       </options>
     </param>
    </params>
</plugin>
"""
import Domoticz
import base64


class BasePlugin:
    enabled = False
    isConnected = True
    outstandingPings = 0
    nextConnect = 0
    commandArray = ["@MAIN:VOL=?", "@MAIN:INP=?", "@MAIN:MUTE=?"]
    commandIndex = 0 

    def __init__(self):
        #self.var = 123
        return

    def onStart(self):
        if Parameters["Mode6"] == "Debug":
           Domoticz.Debugging(1)
        Domoticz.Debug("onStart called")
        if (len(Devices) == 0):
            Domoticz.Device(Name="Status",  Unit=1, Type=17,  Switchtype=17).Create()          
            Domoticz.Device(Name="Volume",  Unit=2, Type=244, Subtype=73, Switchtype=7,  Image=8).Create()
            LevelActions= "LevelActions:"+stringToBase64("||||")+";"
            LevelNames= "LevelNames:"+stringToBase64("Off|HDMI1|HDMI2|HDMI3|HDMI4")+";"
            Other= "LevelOffHidden:ZmFsc2U=;SelectorStyle:MA=="
            Options=LevelActions+LevelNames+Other
            Domoticz.Device(Name="Source", Unit=3, TypeName="Selector Switch", Options=Options).Create()
        
        Domoticz.Transport("TCP/IP", Parameters["Address"], Parameters["Port"])
        Domoticz.Protocol("Line")
        Domoticz.Connect()
        Domoticz.Heartbeat(20)

    def onStop(self):
        Domoticz.Log("onStop called")

    def onConnect(self, Status, Description):
        Domoticz.Debug("onConnect called. Status: " + str(Status))
        if (Status == 0): 
          self.isConnected = True
          UpdateDevice(1,1,"")
          self.onHeartbeat()
        else: 
          self.isConnected = False

    def onMessage(self, Data, Status, Extra):
        Domoticz.Debug("onMessage called")
        self.outstandingPings = self.outstandingPings - 1
        strData = Data.decode("utf-8", "ignore")
        arrData = strData.split('=')
        for x in arrData:
            Domoticz.Debug(x)
        if (arrData[0] == "@MAIN:VOL"):
            vol = float(arrData[1])
            sliderValue = int(vol*5/4 + 100)
            UpdateDevice(2, 2, str(sliderValue))
        elif (arrData[0] == "@MAIN:MUTE"): 
            if (arrData[1] == "Off"):
                UpdateDevice(2, 2, Devices[2].sValue)
            elif (arrData[1] == "On"): 
                UpdateDevice(2, 0, Devices[2].sValue)
        elif (arrData[0] == "@MAIN:INP"): 
            s = arrData[1]
            inp = int(s[-1:])
            UpdateDevice(3,2,str(inp*10))

    def onCommand(self, Unit, Command, Level, Hue):
        Domoticz.Debug("onCommand called for Unit " + str(Unit) + ": Parameter '" + str(Command) + "', Level: " + str(Level))
        if (Unit == 1):
            Domoticz.Debug("Todo: Send on/off") 
            if (Command == "Off"):
                UpdateDevice(1,0,Devices[1].sValue)
                Domoticz.Send("@MAIN:PWR=Standby\r\n")
            elif (Command == "On"): 
                UpdateDevice(1,1,Devices[1].sValue)
                Domoticz.Send("@MAIN:PWR=On\r\n")
        elif (Unit == 2): 
            if (Command == "Set Level"): 
                volume = int(Level)*4/5 - 80
                volumeToSend = round(2*volume)/2
                Domoticz.Send("@MAIN:VOL="+str(volumeToSend)+"\r\n")
            elif (Command == "Off"): 
                Domoticz.Send("@MAIN:MUTE=On\r\n")
                UpdateDevice(2,0,Devices[2].sValue)
            elif (Command == "On"): 
                Domoticz.Send("@MAIN:MUTE=Off\r\n")
                UpdateDevice(2,2,Devices[2].sValue)
        elif (Unit == 3): 
            input = str(int(int(Level)/10))
            Domoticz.Send("@MAIN:INP=HDMI" + input + "\r\n")

    def onNotification(self, Data):
        Domoticz.Debug("onNotification: " + str(Data))

    def onDisconnect(self):
        Domoticz.Debug("onDisconnect called")
        self.isConnected = False 
        UpdateDevice(1,0,"0")
        UpdateDevice(2,0,Devices[2].sValue)
        UpdateDevice(3,0,Devices[3].sValue)

    def onHeartbeat(self):
        Domoticz.Debug("onHeartbeat called. Connected: " + str(self.isConnected))
        if (self.isConnected == True):
            if (self.outstandingPings > 6):
                Domoticz.Debug("Missed more than 6 pings - disconnect")
                Domoticz.Disconnect()
                self.nextConnect = 0
            else:   
                Domoticz.Send(self.commandArray[self.commandIndex] + "\r\n")
                self.commandIndex = (self.commandIndex + 1 ) % len(self.commandArray)
                self.outstandingPings = self.outstandingPings + 1
        else: 
            self.outstandingPings = 0
            self.nextConnect = self.nextConnect - 1
            if (self.nextConnect <= 0):
                self.nextConnect = 3
                Domoticz.Connect()

global _plugin
_plugin = BasePlugin()

def onStart():
    global _plugin
    _plugin.onStart()

def onStop():
    global _plugin
    _plugin.onStop()

def onConnect(Status, Description):
    global _plugin
    _plugin.onConnect(Status, Description)

def onMessage(Data, Status, Extra):
    global _plugin
    _plugin.onMessage(Data, Status, Extra)

def onCommand(Unit, Command, Level, Hue):
    global _plugin
    _plugin.onCommand(Unit, Command, Level, Hue)

def onNotification(Data):
    global _plugin
    _plugin.onNotification(Data)

def onDisconnect():
    global _plugin
    _plugin.onDisconnect()

def onHeartbeat():
    global _plugin
    _plugin.onHeartbeat()

def UpdateDevice(Unit, nValue, sValue):
    # Make sure that the Domoticz device still exists (they can be deleted) before updating it 
    if (Unit in Devices):
        if (Devices[Unit].nValue != nValue) or (Devices[Unit].sValue != sValue):
            Devices[Unit].Update(nValue, str(sValue))
            Domoticz.Log("Update "+str(nValue)+":'"+str(sValue)+"' ("+Devices[Unit].Name+")")
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
        Domoticz.Debug("Device nValue:    " + str(Devices[x].nValue))
        Domoticz.Debug("Device sValue:   '" + Devices[x].sValue + "'")
        Domoticz.Debug("Device LastLevel: " + str(Devices[x].LastLevel))
    return


def stringToBase64(s):
    return base64.b64encode(s.encode('utf-8')).decode("utf-8")

def base64ToString(b):
    return base64.b64decode(b).decode('utf-8')
