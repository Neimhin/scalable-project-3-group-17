register_slave = {
    "type": "object",
    "properties": {
        "emulator_interface": {
            "type": "object",
            "properties": {
                "host": {"type": "string"},
                "port": {"type": "integer"}
            },
            "required": ["host", "port"]
        },
        "devices": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "key_name": {"type": "string"},
                    "public_key": {"type": "string"},
                    "host": {"type": "string"},
                    "port": {"type": "integer"}
                },
                "required": ["key_name", "public_key", "host", "port"]
            }
        }
    },
    "required": ["emulator_interface", "devices"]
}