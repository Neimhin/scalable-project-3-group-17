from __future__ import annotations
from quart import Quart, request, jsonify, render_template
import pandas as pd
import random
import asyncio
from typing import Optional
import slave_emulator

async def emulator_vis(emulator: Optional[slave_emulator.SlaveEmulator], *args, **kwargs):
    app = Quart(__name__)
    @app.route('/update_topology' ,methods=['POST'])
    async def update_topology():
        # get body of post request, parse as json

        # update emulator adjacency/topology
        pass
    await app.run_task(*args, **kwargs)
