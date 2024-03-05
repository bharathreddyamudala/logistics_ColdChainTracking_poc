import json
from azure.iot.device import IoTHubDeviceClient

class IoTHubConfig:
    def __init__(self):
        with open('config.json') as f:
            config = json.load(f)
        self.connectionString = config.get('connectionString','')
    
    @staticmethod
    def get_connection():
        # Create a new device client if it doesn't exist or if it's not connected
        if not hasattr(IoTHubConfig, 'device_client') or not IoTHubConfig.device_client.connected:
            IoTHubConfig.device_client = IoTHubDeviceClient.create_from_connection_string(IoTHubConfig.connectionString)
            IoTHubConfig.device_client.connect()
        return IoTHubConfig.device_client
    

    