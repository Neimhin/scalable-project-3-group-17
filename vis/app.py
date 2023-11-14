from __future__ import annotations
from quart import Quart, request, jsonify, render_template
import asyncio
from typing import Optional
import master_emulator
import numpy as np

def emulator_vis(emulator: Optional[master_emulator.MasterEmulator], *args, **kwargs) -> asyncio.Task:
    app = Quart(__name__)
    @app.route('/' ,methods=['GET'])
    async def index():
        return await render_template('index.html')
        
    @app.route('/new_adjacency_matrix', methods=['GET'])
    async def new_adjacency_matrix():
        if not emulator:
            return jsonify("no emulator"), 500
        return jsonify(emulator.adjacency_matrix)

    return asyncio.create_task(app.run_task(*args, **kwargs))
