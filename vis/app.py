from __future__ import annotations
from quart import Quart, request, jsonify, render_template
import pandas as pd
import random
import asyncio
from typing import Optional
import slave_emulator 

async def emulator_vis(emulator: Optional[slave_emulator.SlaveEmulator], *args, **kwargs):
    app = Quart(__name__)
    @app.route('/' ,methods=['GET'])
    async def index():
        return await render_template('index.html')
        
    @app.route('/new_adjacency_matrix', methods=['GET'])
    async def new_adjacency_matrix():
        if not emulator:
            return jsonify(np.ones((10,10)).to_array())
        return jsonify(emulator.adjacency_matrix)

    await app.run_task(*args, **kwargs)
