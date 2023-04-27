#===============================================================================
# Python example for weCat3D
#
# The example shows how the DLL from the weCat3D can be used in a Pyhton script.
# The DLL is part of the weCat3D SDK.
# https://www.wenglor.com/en/Interfaces-of-2D-3D-Profile-Sensors/s/Themenwelt+weCat3D+Schnittstellen
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# 
# wenglor sensoric elektronische Ger�te GmbH
# wenglor Stra�e 3
# 88069 Tettnang
# Germany
# 
# Phone:    +49 7542 5399 0
# Fax:    +49 7542 5399 988
# E-Mail:    info(at)wenglor.com
#
# Year 2021
# Version 1.0
#===============================================================================

from ctypes import*
from ctypes.wintypes import *
import xml.etree.ElementTree as ET
import time
import configparser
from time import sleep
import os, sys
import numpy as np


#===============================================================================
# Function to read settings from weCat3D sensor
#===============================================================================
def ReadFromSensor(ScannerHandle, Command, DllHandle):  
    CommandToSend = Command.encode()
    cmdlen = len(CommandToSend)
    SendBuffer = create_string_buffer(CommandToSend, cmdlen)
    ReturnValue = create_string_buffer(50)
    iRet = DllHandle.EthernetScanner_ReadData(ScannerHandle, SendBuffer, ReturnValue, c_int(50), 0)    
    if  iRet == 0:        
        return str(ReturnValue.value.decode())
    else:    
        return "Error"    

#===============================================================================
# Function to write settings to weCat3D sensor
#===============================================================================
def WriteToSensor(ScannerHandle, DllHandle, Command):   
    CommandToSend = Command.encode()
    cmdlen = len(CommandToSend)
    iRet = DllHandle.EthernetScanner_WriteData(Scanner, CommandToSend, cmdlen)
    if iRet != cmdlen: 
        print("Could not send command "+CommandToSend)
        return 0
    else:     
        return 1

#===============================================================================
# Default sensor IP is 192.168.100.1 can should be adapted if changed. 
# Port is always 32001.
# Path to the DLL library
#===============================================================================
ip = "169.254.58.130".encode() 
port = "32001".encode()
dll_path = "C:/Users/maria/OneDrive/Documentos/sensor_MLSL276/"

XArray = (c_double * 2048)(0)
ZArray = (c_double * 2048)(0)
Intensity = (c_int * 2048)(0)
PeakWidth = (c_int * 2048)(0)
BufferSize = c_int(2048)
Encoder = c_int(0)
UserIO = c_int(0)
PicCnt = c_int(0)

#===============================================================================
# Load DLL library
#===============================================================================
Dll = cdll.LoadLibrary(dll_path+"EthernetScanner.dll")
if Dll:
    print("Dll loaded")
else:
    print("Error: could not load dll")
    exit()

#===============================================================================
# Connect to sensor.
#===============================================================================
EthernetScanner_Connect = Dll.EthernetScanner_Connect
EthernetScanner_Connect.restype = c_void_p
Scanner = c_void_p(EthernetScanner_Connect(ip, port, 0))

if not Scanner:
    print("Could not get scanner pointer, exit the program")
    exit()

ConnectStatusPointer = c_int()
ConnectionStatus = c_bool()
TimeStart = time.time()
while time.time() < TimeStart + 3:
    getCheckConnection = Dll.EthernetScanner_GetConnectStatus(Scanner, byref(ConnectStatusPointer))
    ConnectionStatus = (ConnectStatusPointer.value==3)
    if ConnectionStatus:    
        print("Connection status: %d Successfull" % ConnectStatusPointer.value)   
        break
        
if not ConnectionStatus:
    print("Connection status: %d Error, exit the program" % ConnectStatusPointer.value)
    exit() 

#===============================================================================
# If succesful connection start acquisition
#===============================================================================
if not WriteToSensor(Scanner, Dll, "SetAcquisitionStart\r"):
    exit()
    
#===============================================================================
# Read current exposure time and set new one increased by either by 100 �s
# or set to 100 �s if longer than 1000 �s.
#===============================================================================
ReturnedString = ReadFromSensor(Scanner, "GetExposureTime", Dll)
print("Current exposure time: %s" % ReturnedString)
if ReturnedString != "Error":        
    CurrentExposureTime = int(ReturnedString)
    NewExposureTime = CurrentExposureTime+100  
    if NewExposureTime > 1000:
        NewExposureTime = 100
    print("Writing exposure time: %d" % NewExposureTime)
    if not WriteToSensor(Scanner, Dll, "SetExposureTime="+str(NewExposureTime)+"\r"):
        print("Could not set exposure time")
#===================================================================================
# Read profiles and evalute the intensity average, encoder value and picture counter
#===================================================================================
TimeStart = time.time()
AmountOfReadedScanns = int(0)
while time.time() < TimeStart + 3 and AmountOfReadedScanns < 10: 
    Result = Dll.EthernetScanner_GetXZIExtended(Scanner, byref(XArray), byref(ZArray), byref(Intensity), byref(PeakWidth), BufferSize, byref(Encoder), byref(UserIO), 500, None, None, byref(PicCnt))
    if Result <= 0:        
        sleep(0.1)            
        continue
    AmountOfReadedScanns+=1  
    IntensityAverage = 0
    IntensityCounter = 0
    for current_intensity in Intensity:
        if current_intensity>0:
            IntensityAverage+=current_intensity
            IntensityCounter+=1            
    if IntensityCounter > 0:
        IntensityAverage=IntensityAverage/IntensityCounter    
    sys.stdout.write("Intensity average %d " % IntensityAverage)        
    sys.stdout.write("Encoder %d " % Encoder.value)    
    sys.stdout.write("Picture counter %d\n" % PicCnt.value)
    #sys.stdout.flush()
print("Amount of readed scanns: %d" % AmountOfReadedScanns)        

