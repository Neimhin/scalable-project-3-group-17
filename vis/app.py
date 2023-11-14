from __future__ import annotations
from quart import Quart, request, jsonify, render_template
import asyncio
from typing import Optional
import master_emulator
import numpy as np

def emulator_vis(emulator: Optional[master_emulator.MasterEmulator], *args, **kwargs) -> asyncio.Task:
    app = Quart(__name__)


    return asyncio.create_task(app.run_task(*args, **kwargs))
