from __future__ import annotations
from quart import Quart
from typing import Optional
import slave_emulator
import gateway_port
import asyncio

def slave_server(emulator: Optional[slave_emulator.SlaveEmulator], *args, **kwargs):
    app = Quart(__name__)
    @app.route('/update_topology' ,methods=['POST'])
    async def update_topology():
        # get body of post request, parse as json

        # update emulator adjacency/topology
        pass
    emulator.port = gateway_port.find_free_gateway_port()
    port = emulator.port
    assert type(port) == int
    task = asyncio.create_task(app.run_task(port=port, *args, **kwargs))
    return task, port
