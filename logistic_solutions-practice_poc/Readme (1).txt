Serial Communication and Data Processing Script:

1. Install Python: 

	- If Python is not already installed on your system, you can download and install it from the official Python website.

2. Create virtual environment:
   	- navigate to the directory where project is there.
   	- if you are creating first time python vir env otherwise you can directly activate vir env.
		create and activate python virtual env
		to create vir env: `python3 -m myenv venv`
		vir env name is myenv
   	- to activate vir env: go to directory where vir env created , 
		to activate vir env: `source myenv/bin/activate`
3. Install dependcies:
   	- if dependencies not installed , then install dependencies from requirements.txt.
    		to install dependencies from requirements.txt: `pip install -r requirements.txt`

4. Configuration:
   	- open the config.json in any text editor.
	- Enter the required in config json
	- Serial Port Configuration :Set the port_name and baud_rate variables to configure the serial port settings according to your setup.

	- Wiliot Helper Configuration:set  ownerId, gatewayId, gatewayType, gatewayName, baseUrl, mqttBroker, accessKeyForEdge. 

	- Sumologic Configuration: set sumo_logic_endpoint
 
	- Azure IoT Hub Configuration: set connectionString 


5. Run the Script:

	- Execute the Python script BluetoothGatewayDecoder.py

	- The script will establish communication with the specified serial port and start listening for incoming data.

	- It will process the received data based on its type (pixel data, temperature/humidity data, smart lock data) and perform corresponding actions.

	- The script will continue running until a stop signal (STOP_SIGNAL) is received.


6. Review Output:

	- Check the console output for any log messages or errors generated during script execution.

	- Verify that the data processing and actions performed by the script align with the expected behavior.