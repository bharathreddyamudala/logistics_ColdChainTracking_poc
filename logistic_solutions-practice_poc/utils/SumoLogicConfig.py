import requests
import json
import time
import random

# HTTP Source endpoint URL
class SumoLogicconfig:

    def __init__(self):
        with open("config.json") as f:
            config = json.load(f)
        self.sumo_logic_endpoint = config.get("sumo_logic_endpoint",'')
        

    # Function to send logs to Sumo Logic
    def sendMessage(self,logs):
        headers = {'Content-Type': 'application/json'}

        try:
            response = requests.post(self.sumo_logic_endpoint, headers=headers, data=logs)
            if response.status_code == 200:
                print("Logs sent successfully to Sumo Logic")
            else:
                print(f"Failed to send logs. Status code: {response.status_code}, Response: {response.text}")
        except Exception as e:
            print(f"Error sending logs to Sumo Logic: {str(e)}")

