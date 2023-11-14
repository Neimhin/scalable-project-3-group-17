from __future__ import annotations
from quart import Quart
from typing import Optional
import slave_emulator
import gateway_port
import asyncio
import json
import get_ip_address
import jsonschema
from quart import jsonify, request
import schema

def slave_server(emulator: Optional[slave_emulator.SlaveEmulator], *args, **kwargs):
    app = Quart(__name__)
    
    
    @app.route('/update_topology' ,methods=['GET'])
    async def update_topology():
        print("update topology")
        my_schema = schema.update_topology
        request_data = await request.get_json()
        print(request_data)
        try:
            jsonschema.validate(instance=request_data, schema=my_schema)
            emulator.get_updated_topology(request_data)
            return jsonify({"message": "topology updated successfully"}), 200
        except jsonschema.ValidationError as e:
            print(str(e))
            return jsonify({"error": str(e)}), 400 
    

    emulator.port = gateway_port.find_free_gateway_port()
    emulator.host = get_ip_address.get_ip_address()
    host = emulator.host
    port = emulator.port
    assert type(port) == int
    task = asyncio.create_task(app.run_task(host=host, port=port, *args, **kwargs))
    return task, port
