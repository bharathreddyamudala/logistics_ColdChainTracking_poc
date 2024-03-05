#Importing necessary libraries

import time
import json
import requests
import paho.mqtt.client as mqtt
import datetime
from datetime import datetime, timedelta
import random
import ssl
from threading import Timer

class WiliotHelper:
    def __init__(self): 
        with open('config.json') as f:
            config = json.load(f)
         # Initialize WiliotHelper with configurations from config.json
        self.ownerId = config.get('ownerId', '')
        self.gatewayId = config.get('gatewayId', '')
        self.gatewayType = config.get('gatewayType', '')
        self.gatewayName = config.get('gatewayName', '')
        self.baseUrl = config.get('baseUrl')
        self.mqttBroker = config.get('mqttBroker', '')
        self.accessKeyForEdge = config.get('accessKeyForEdge','')
        self.port = 1883
        self.keepalive = 60*30

          # Token information for Wiliot API
        self.token_info = {
            "m_gatewayRegistration": None,
            "creation_time": None
        }
         # Duration after which token expires
        self.TOKEN_EXPIRY_DURATION = timedelta(hours=12)
        self.m_gateway_mqtt_client = None
       # Method to update latitude and longitude
    def update_lat_lng(self):
        self.lat =random.uniform(-90, 90)
        self.lng = random.uniform(-180, 180)

    # Method to send pixel tag data
    def send_pixel_tag(self, bridge: str, tag: str) -> int:
        self.update_lat_lng()

        now = int(time.time() * 1000)
        req = {
            "gatewayId": self.gatewayId,
            "gatewayType":self.gatewayType,
            "location": {
                "lat": self.lat,
                "lng": self.lng
            },
            "timestamp": now,
            "packets": [
                {"timestamp": now, "sequenceId": 0, "payload": bridge},
                {"timestamp": now, "sequenceId": 1, "payload": tag} if tag else None
            ]
        }
        json_payload = json.dumps(req)
        print("JSON Payload:", json_payload)
        # Publish data to MQTT broker
        self.ensure_mqtt_client().publish("data/{}/{}".format(self.ownerId,self.gatewayId),json_payload.encode(), 0, False)
        return json_payload
   
    def record_data(self, data):
        # Record data logic
        return json.dumps(data)
    # Method to get access token from Wiliot API
    def get_token(self):
        url = "{self.baseUrl}/v1/auth/token/api"
        headers = {
            "Authorization": self.accessKeyForEdge,
            "accept": "application/json"
        }
        # Request access token
        response = requests.post(url, headers=headers)

        if response.status_code == 200:
            data = response.json()
            access_token = data.get("access_token")
            # print(f"Access Token for creating gateway:, {access_token}")
            return access_token
        else:
            print("Failed to retrieve access token. Status code:", response.status_code)
            return None
     # Method to register gateway with Wiliot API
    def wiliot_register_gateway(self, request_data, ownerId, gatewayId, token):
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + token
        }
        url = f"{self.baseUrl}/v1/owner/{ownerId}/gateway/{gatewayId}/mobile"
        response = requests.post(url, headers=headers, json=request_data)
        return response
    
    # Method to process response from Wiliot API
    def process_response(self, response):
        if response.status_code == 200:
            json_data = response.json()
            data = json_data.get('data', {})

            return data
        else:
            print(f"Request failed with status code: {response.status_code}")
    # Method to register gateway with Wiliot API if not already registered
    def register_gateway(self):
        json_body = {
            "gatewayType": self.gatewayType,
            "gatewayName": self.gatewayName
            
        }

        if self.token_info["m_gatewayRegistration"] is None or self.is_token_expired(self.token_info["creation_time"]):
            token = self.get_token()
            request_data = json_body
            response = self.wiliot_register_gateway(request_data, self.ownerId, self.gatewayId, token)
            m_gatewayRegistration = self.process_response(response)

            self.token_info["m_gatewayRegistration"] = m_gatewayRegistration
            self.token_info["creation_time"] = datetime.now()
            # print(f'access_token_for_mqttconnect: {self.token_info["m_gatewayRegistration"]["access_token"]}')

            return json.dumps(m_gatewayRegistration)
        else:
            return json.dumps({"message": "Gateway already registered"})
     # Method to ensure MQTT client connection
    def ensure_mqtt_client(self):

        try:                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 
            self.register_gateway()
            if self.m_gateway_mqtt_client is None or not self.m_gateway_mqtt_client.is_connected:

                
                            # Callbacks
                def on_connect(client, userdata, flags, rc):
                    print("Connected with result code "+str(rc))
                    # Subscribe to topics if needed
                    # client.subscribe("topic")
                
                def on_message(client, userdata, msg):

                    pass
                
                def on_disconnect(client, userdata, rc):
                    print("Disconnected with result code "+str(rc))
                
                # Create MQTT client instance
                client = mqtt.Client(client_id=self.gatewayId)
                
                # Set callbacks
                client.on_connect = on_connect
                client.on_message = on_message
                client.on_disconnect = on_disconnect
                
                # Set username and password
                client.username_pw_set(self.ownerId, self.token_info["m_gatewayRegistration"]["access_token"])
                
                # Enable SSL/TLS
                client.tls_set_context(ssl.create_default_context())
                
                # Connect to broker
                client.connect(self.mqttBroker, self.port, self.keepalive)
                
                # Start the loop
                #client.loop_forever()

                self.m_gateway_mqtt_client = client

                return self.m_gateway_mqtt_client
            return self.m_gateway_mqtt_client
        except Exception as e:
            print(f"Error occurred while ensuring MQTT client: {e}")
            return None
      # Method to create MQTT connection options
    def get_mqtt_connect_options(self):         
        conn_opts = mqtt.MosquittoConnectOptions()         
        conn_opts.clean_session = True        
        conn_opts.username_pw_set(username=self.ownerId, password=self.token_info["m_gatewayRegistration"]["access_token"])         
        conn_opts.keep_alive_interval =1800
        
        return conn_opts
    # Method to check if token has expired
    def is_token_expired(self, creation_time):
        """
        Checks if the token has expired based on its creation time.
        """
        if creation_time is None:
            return True
        current_time = datetime.now()
        return (current_time - creation_time) > self.TOKEN_EXPIRY_DURATION

