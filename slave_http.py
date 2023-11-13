from __future__ import annotations
from quart import Quart, request, jsonify, render_template
import pandas as pd
import random
import asyncio
from typing import Optional
import emulator

async def emulator_vis(emulator: Optional[emulator.SlaveEmulator], *args, **kwargs):
    app = Quart(__name__)
    @app.route('/update_topology' ,methods=['POST'])
    async def update_topology():
        pass
    await app.run_task(*args, **kwargs)
