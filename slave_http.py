from __future__ import annotations
from quart import Quart
from typing import Optional
import slave_emulator
import gateway_port
import asyncio
import json
import get_ip_address

def slave_server(emulator: Optional[slave_emulator.SlaveEmulator], *args, **kwargs):
    app = Quart(__name__)
    @app.route('/update_topology' ,methods=['POST'])
    async def update_topology():
        # get body of post request, parse as json

        # update emulator adjacency/topology
        pass
    emulator.port = gateway_port.find_free_gateway_port()
    emulator.host = get_ip_address.get_ip_address()
    host = emulator.host
    port = emulator.port
    assert type(port) == int
    task = asyncio.create_task(app.run_task(host=host, port=port, *args, **kwargs))
    return task, port
