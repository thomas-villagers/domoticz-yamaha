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
    commandArray = ["@MAIN:VOL=?", "@MAIN:INP=?", "@MAIN:MUTE=?", "@MAIN:SOUNDPRG=?"]
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
            Other= "LevelOffHidden:ZmFsc2U=;SelectorStyle:MA==" # true is "dHJ1ZQ==", 1 is "MQ=="
            Options=LevelActions+LevelNames+Other
            Domoticz.Device(Name="Source", Unit=3, TypeName="Selector Switch", Options=Options).Create()
        
#        Domoticz.Transport("TCP/IP", Parameters["Address"], Parameters["Port"])  ## obsolete 
#        Domoticz.Protocol("Line")  # obsolete 
#        Domoticz.Connect()  # obsolete 

        self.connection = Domoticz.Connection(Name="Yamaha connection", Transport="TCP/IP", Protocol="Line", Address=Parameters["Address"], Port=Parameters["Port"])
        self.connection.Connect()
        Domoticz.Heartbeat(20)

    def onStop(self):
        Domoticz.Log("onStop called")

    def onConnect(self, Connection, Status, Description):
        Domoticz.Debug("onConnect called. Status: " + str(Status))
        if (Status == 0): 
          self.isConnected = True
          UpdateDevice(1,1,"")
          self.onHeartbeat()
        else: 
          self.isConnected = False

    def onMessage(self, Connection, Data, Status, Extra):
        Domoticz.Debug("onMessage called")
        self.outstandingPings = self.outstandingPings - 1
        strData = Data.decode("utf-8", "ignore")
        arrData = strData.split('=')
        for x in arrData:
            Domoticz.Debug(x)
        if (arrData[0] == "@MAIN:VOL"):
            vol = float(arrData[1])
            sliderValue = int(vol*5/4 + 100)
            UpdateDevice(2, Devices[2].nValue, str(sliderValue))
        elif (arrData[0] == "@MAIN:MUTE"): 
            if (arrData[1] == "Off"):
                UpdateDevice(2, 2, Devices[2].sValue)
            elif (arrData[1] == "On"): 
                UpdateDevice(2, 0, Devices[2].sValue)
        elif (arrData[0] == "@MAIN:INP"): 
            s = arrData[1]
            inp = int(s[-1:])
            UpdateDevice(3,2,str(inp*10))
        elif (arrData[0] == "@MAIN:SOUNDPRG"):
            UpdateDevice(1,1, arrData[1])

    def onCommand(self, Unit, Command, Level, Hue):
        Domoticz.Debug("onCommand called for Unit " + str(Unit) + ": Parameter '" + str(Command) + "', Level: " + str(Level))
        if (self.isConnected == False):
            self.connection.Connect() 
            return
        if (Unit == 1):
            if (Command == "Off"):
                UpdateDevice(1,0,Devices[1].sValue) # TODO remove
                self.connection.Send("@MAIN:PWR=Standby\r\n")
            elif (Command == "On"): 
               self.connection.Send("@MAIN:PWR=On\r\n")
        elif (Unit == 2): 
            if (Command == "Set Level"): 
                volume = int(Level)*4/5 - 80
                volumeToSend = round(2*volume)/2
                self.connection.Send("@MAIN:VOL="+str(volumeToSend)+"\r\n") 
            elif (Command == "Off"): 
                self.connection.Send("@MAIN:MUTE=On\r\n") 
            elif (Command == "On"): 
                self.connection.Send("@MAIN:MUTE=Off\r\n") 
        elif (Unit == 3): 
            input = str(int(int(Level)/10))
            self.connection.Send("@MAIN:INP=HDMI" + input + "\r\n") 

    def onNotification(self, Data):
        Domoticz.Debug("onNotification: " + str(Data))

    def onDisconnect(self, Connection):
        Domoticz.Debug("onDisconnect called")
        self.isConnected = False 
        UpdateDevice(1,0,"")
        UpdateDevice(2,0,Devices[2].sValue)
        UpdateDevice(3,0,Devices[3].sValue)

    def onHeartbeat(self):
        Domoticz.Debug("onHeartbeat called. Connected: " + str(self.isConnected))
        if (self.isConnected == True):
            if (self.outstandingPings > 6):
                Domoticz.Debug("Missed more than 6 pings - disconnect")
                self.connection.Disconnect()  # obsolete 
                self.nextConnect = 0
            else:   
                self.connection.Send(self.commandArray[self.commandIndex] + "\r\n")
                self.commandIndex = (self.commandIndex + 1 ) % len(self.commandArray)
                self.outstandingPings = self.outstandingPings + 1
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

def onMessage(Connection, Data, Status, Extra):
    global _plugin
    _plugin.onMessage(Connection, Data, Status, Extra)

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
