from __future__ import annotations
from quart import Quart, request, jsonify, render_template
import pandas as pd
import random
import asyncio
from typing import Optional
import slave_emulator

async def master_emulator(emulator: Optional[slave_emulator.MasterEmulator], *args, **kwargs):
    app = Quart(__name__)
    @app.route('/register' ,methods=['POST'])
    async def register():
        pass

    await app.run_task(*args, **kwargs)

if __name__ == "__main__":
    asyncio.run(master_emulator())