'''
contributor: Naman Arora
'''

import json
import random
import argparse

device_readings = ["temperature", "depth", "position", "pressure", "wave", "ADCPs", "radar"]

def create_device_json(num_devices, start_port, pi_ip_address):
    devices = {}

    for i in range(1, num_devices + 1):
        device_id = f"/devices/device{i}"
        devices[device_id] = []

        for dtype in device_readings:
            device_entry = {
                dtype: [
                    {
                        "listen port": start_port,
                        "send port": start_port + 1,
                        "address": pi_ip_address
                    },
                    {
                        "neigbours": random.sample([f"/devices/device{j}" for j in range(1, num_devices + 1) if j != i], random.randint(0, num_devices - 1))
                    }
                ]
            }
            start_port += 2
            devices[device_id].append(device_entry)

    return json.dumps(devices, indent=2)

def main():
    parser = argparse.ArgumentParser(description="Generate a JSON file for device configurations.")
    parser.add_argument("--num_devices", type=int, default=5, help="Number of devices (default: 5)")
    parser.add_argument("--start_port", type=int, default=33333, help="Starting port number (default: 33333)")
    parser.add_argument("--pi_ip_address", type=str, default="192.168.1.1", help="Pi IP address (default: 192.168.1.1)")

    args = parser.parse_args()

    generated_json = create_device_json(args.num_devices, args.start_port, args.pi_ip_address)

    # Save to file
    with open('generated_devices.json', 'w') as file:
        file.write(generated_json)

    print("JSON file generated successfully.")

if __name__ == "__main__":
    main()
