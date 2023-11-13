import json

def create_adjacency_list(json_file):
    with open(json_file, 'r') as file:
        data = json.load(file)

    adjacency_list = {}

    for device, configs in data.items():
        # Initialize a set for each device to avoid duplicate neighbors
        adjacency_list[device] = set()

        for config in configs:
            # Iterate through each configuration (e.g., temperature, depth)
            for config_type, config_details in config.items():
                # Extract the neighbors from the configuration
                neighbors = config_details[1].get("neigbours", [])  # Make sure to use the correct spelling as in your JSON
                for neighbor in neighbors:
                    # Add each neighbor to the adjacency list of the device
                    adjacency_list[device].add(neighbor)

        # Convert the set to a list for consistency
        adjacency_list[device] = list(adjacency_list[device])

    return adjacency_list

def main():
    json_file = 'generated_devices.json'
    adjacency_list = create_adjacency_list(json_file)

    # Print the adjacency list
    for device, neighbors in adjacency_list.items():
        print(f"{device}: {neighbors}")

if __name__ == "__main__":
    main()
