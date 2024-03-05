#Importing necessary libraries

import serial
import requests
import json
import datetime
import time
import json
from datetime import datetime, timedelta
from typing import List, Dict

from utils.BufferUtils import BufferUtils
from utils.WiliotHelper import WiliotHelper
from utils.SumoLogicConfig import SumoLogicconfig
from utils.IotHubConfig import IoTHubConfig
from utils.TypeBitSet import BitSet
from utils.SmartLockState import SmartLockState

from azure.iot.device import IoTHubDeviceClient, Message
import paho.mqtt.client as mqtt
 

# Configure the serial port

wiliot_helper = WiliotHelper()
SumoLogicconfig = SumoLogicconfig()
class Data_Processor:
     def __init__(self):
        # Initialize class variables here
        with open('config.json') as f:
            config = json.load(f)
        self.port_name = config.get("port_name",'')
        self.baud_rate = config.get("baud_rate",'')
        self.m_last_bridge_suffix = None
        self.m_last_bridge = None
        self.m_last_tag = None
        self.last_bridge = None
        self.tag = None
        self.payloads = {}
        self.EXPECTED_LENGTH =31
        self. STATUS_PACKET_MARKER = 0xee
        self.IGNORE_PACKET_MARKER = 0xed
        self.SIDE_INFO_PACKET_MARKER = 0xec
    #To process Pixel data
     def process_pixel_data(self,data):
           
            try:
                if data.startswith("AT-PXL_DATA"):
                    packet = self.extract_packet(data)

                    raw = packet['DATA']
                    decoded = BufferUtils.convert_from_hex(raw)
                    if len(decoded) == self.EXPECTED_LENGTH and decoded[1] == 0x16 and decoded[2] == 0xC6 and decoded[3] == 0xFC:
                        suffix = raw[2 * (len(decoded) - 4):]
                        case_value = int(decoded[6])
                        if case_value == self.STATUS_PACKET_MARKER:#0Xee
                            rssi = BufferUtils.convert_from_hex(packet['RSSI'])
                            tag = raw
                            rssi = rssi
                        elif case_value == self.IGNORE_PACKET_MARKER:
                            pass
                        elif case_value == self.SIDE_INFO_PACKET_MARKER:
                            self.m_last_bridge = raw
                            self.m_last_bridge_suffix =suffix
                        else:
                            self.m_lastTag = raw
                            self.m_lastTagSuffix = suffix
                            if self.m_lastTagSuffix is not None and self.m_lastTagSuffix == self.m_last_bridge_suffix:
                                rssi = BufferUtils.convert_from_hex(packet['RSSI'])
                                lastBridge = self.m_last_bridge
                                tag = self.m_lastTag
                                rssi = rssi
                                print(lastBridge)
                                print(tag)
                                wiliot_helper.send_pixel_tag(lastBridge,tag)
                                
                                # time.sleep(2) 
            except Exception as e:
                print("An error occurred while processing the data:", e)
    #To process temperature data
     def process_temp_data(self,data):
            
            try:
                if data.startswith('AT-TRH_ID'):
                        global UnitiD,temperature,humidity,batteryVoltage
                        packet = self.extract_packet(data)
                        UnitiD =packet['ID']
                        temperature = self.extract_hex16_as_float(packet, "T", True) / 100.0 - 100.0
                        humidity = self.extract_hex16_as_float(packet, "H", True) / 100.0
                        batteryVoltage = self.extract_hex16_as_float(packet, "B", True) / 1000.0    
                        json_data = {
                        "UnitID": UnitiD,
                        "Temperature": temperature,
                        "Humidity": humidity,
                        "Battery Voltage": batteryVoltage,
                        "status": 'success'
                        }
                        # Convert the dictionary to a JSON object
                        json_object = json.dumps(json_data, indent=4)
                        print(json_object)
                        self.send_message(json_object)
            except Exception as e:
                print("An error occurred while processing the data:", e)
    #Sending Data to sumo-logic and Azure cloud    
     def send_message(self,json_object):
            SumoLogicconfig.sendMessage(json_object)
            device_client = IoTHubConfig.get_connection()
            message = Message(str(json_object))
            # Set content type and content encoding
            message.content_type = "application/json"
            message.content_encoding = "utf-8"
            device_client.send_message(message)
         
     
     
    #To process Smart-Lock data
     def process_smartlock_data(self,data):

        if data.startswith("AT-SLB"):
            print(data)
            packet = self.extract_packet(data)
            raw = BufferUtils.convert_from_hex(packet["D"])
            bs =  BitSet()
            try:
                for i in range(24):
                    bit = raw[4 + (i // 8)] & (1 << (i % 8))
                    if bit != 0:
                        bs.set(i)
                unitId = packet['ADD']
                # print(unitId)
                lockingCounter = raw[7] & 0xFF
                # print(lockingCounter)
                status = SmartLockState(bs)
                # print(status)
                # Create JSON object
                json_data = {
                    "unitId": unitId,
                    "lockingCounter": lockingCounter,
                    "Lockstatus": str(status),  # Assuming status is a string representation
                    "status" : "success"
                }
        
                # Convert the dictionary to a JSON object
                json_object = json.dumps(json_data, indent=4)
                print(json_object)
                self.send_message(json_object)
            except Exception as e:
                print("An error occurred while processing the data:", e)
        
      #For data other than TRH,Smart-lock and pixels
     def Default_Data_Process(self,data):
        print('Invalid data',data)
 
 
     #Process incoming data based on the case identifier.
     def process_switch(self,data):
        try:
            case  = data[ : 6]
            if case == 'AT-PXL':
                self.process_pixel_data(data)
            elif case == 'AT-TRH':
                self.process_temp_data(data)
            elif case == 'AT-SLB':
                self.process_smartlock_data(data)
            else:
                self. Default_Data_Process(data)

        except Exception as e:
          print("An error occurred while processing the data:", e)
    
     # Extracts a 16-bit hexadecimal value from the fields dictionary and returns it as a floating-point number.
     def extract_hex16(self,fields, key, little_endian):
        val = fields.get(key)
        if val is None:
            return -1
    
        num = int(val, 16)
        if little_endian:
            num = ((num << 8) & 0xFF00) | ((num >> 8) & 0x00FF)
    
        return num & 0xFFFF
     '''
      This method utilizes the `extract_hex16` method to extract a 16-bit hexadecimal value.
       #If the value is found, it is returned as a floating-point number.
       If the value is not found, it returns NaN (Not a Number)
       '''
     def extract_hex16_as_float(self,fields, key, little_endian):
        val = self.extract_hex16(fields, key, little_endian)
        return val if val >= 0 else float('nan')        
    
   
    #For extracting key-value pair from raw data
     def extract_packet(self,data):
      x = data.split('_')
      obj = {}
      for i in x:
       if (':' in i):
        y = i.split(':')
        obj[y[0]] = y[1]
      return obj
 
      '''
        This send_http_post_request method is responsible for sending an HTTP POST request to a specified URL with the provided JSON payload
       '''
     def send_http_post_request(payload_json):
        try:
            # Construct the URL
            url = "http://54.196.192.142:8080/wiliot/v1/push-pixel-data"
    
            # Define headers
            headers = {"Content-Type": "application/json; charset=UTF-8"}
    
            # Make the HTTP POST request
            response = requests.post(url, headers=headers, data=payload_json.encode("utf-8"))
    
            # Print the HTTP response code
            print("HTTP Response Code:", response.status_code)
         # Catch any exceptions that occur during execution
        except Exception as e:
            print("Error sending HTTP POST request:", e)

     #Process the data if serial port is open
     def run(self):
             # Open the serial port
            ser = serial.Serial(self.port_name,self.baud_rate,timeout=10000)
            try:
                 # Check if the serial port is successfully opened
                if ser.is_open:
                    print("Serial port opened successfully.")
                    stop_condition = False
                    # Continuously receive and process data
                    while not stop_condition:
                        # Read a line of data from the serial port and decode it as UTF-8
                        received_data = ser.readline().decode("utf-8").strip()
                        print(received_data)
                         # Process the received data using the process_switch method
                        self.process_switch(received_data)
                else:
                     # Print a message if the serial port failed to open
                    print("Failed to open the serial port.")
            except Exception as e:
                  # Catch any exceptions that occur during execution
                print("Error:", e)
#main function
if __name__ == "__main__":
    data_processor = Data_Processor()
    data_processor.run()
 
 
 
 
 
 