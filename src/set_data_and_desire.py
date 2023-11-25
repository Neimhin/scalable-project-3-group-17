'''
set data for one device within the slave
set a desire for the above data from some other device (mayber in some other slave emulator?)
'''
import argparse
import requests
import sensor_data_generation as sdg

parser = argparse.ArgumentParser(description="Set Data on Random Device & Set Desire on Random Device")
parser.add_argument("--data_emulator_port", type=int, required=True, help="Port number of the slave emulator to set the data.")
parser.add_argument("--desire_emulator_port", type=int, required=True, help="Port number of the slave emulator to set the desire for.")

args = parser.parse_args()
data_port = args.data_emulator_port
desire_port = args.desire_emulator_port

data_name = '/sensor/measurements'
data = sdg.get_measurements()


set_data_url=f"http://127.0.0.1:{data_port}/give_data_to_random_device?data_name={data_name}&data={data}"
response_data = requests.get(set_data_url)
print(f"Response from giving data: {response_data.text}")


desire_url=f"http://127.0.0.1:{desire_port}/set_desire_for_one?data_name={data_name}"
response_desire = requests.get(desire_url)
print(f"Response from setting desire: {response_desire.text}")
