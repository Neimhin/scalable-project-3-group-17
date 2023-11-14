device_interface = {
  "type": "object",
  "properties": {
    "key_name": {"type": "string"},
    "public_key": {"type": "string"},
    "host": {"type": "string"},
    "port": {"type": "integer"}
  },
  "required": ["key_name", "public_key", "host", "port"]
}

slave_emulator_interface = {
    "type": "object",
    "properties": {
        "host": {"type": "string"},
        "port": {"type": "integer"}
    },
    "required": ["host", "port"]
}

register_slave = {
    "type": "object",
    "properties": {
        "emulator_interface": slave_emulator_interface,
        "devices": {
            "type": "array",
            "items": device_interface
        }
    },
    "required": ["emulator_interface", "devices"]
}

{
  "type": "object",
  "properties": {
    "devices": {
      "type": "array",
      "items": device_interface
    },
    "connections": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "source": {"type": "string"},
          "target": {"type": "string"}
        },
        "required": ["source", "target"]
      }
    }
  },
  "required": ["devices", "connections"],
}

def create_ring_topology(devices):
    topology = {
        "devices": devices,
        "connections": []
    }

    num_devices = len(devices)
    for i in range(num_devices):
        source = devices[i]["key_name"]
        target = devices[(i + 1) % num_devices]["key_name"]
        source,target = sorted([source, target])
        topology["connections"].append({"source": source, "target": target})

    return topology

if __name__ == "__main__":
    devices = [
        {
            "key_name": "device1",
            "public_key": "public_key_1",
            "host": "192.168.1.1",
            "port": 8080
        },
        {
            "key_name": "device2",
            "public_key": "public_key_2",
            "host": "192.168.1.2",
            "port": 8081
        },
        {
            "key_name": "device3",
            "public_key": "public_key_3",
            "host": "192.168.1.3",
            "port": 8082
        },
        {
            "key_name": "device4",
            "public_key": "public_key_4",
            "host": "192.168.1.4",
            "port": 8083
        }
    ]

    import json
    print(json.dumps(create_ring_topology(devices)))
