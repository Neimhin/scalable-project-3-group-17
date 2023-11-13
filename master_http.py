from __future__ import annotations
import quart
import asyncio
from typing import Optional
import master_emulator
import schema
import jsonschema

async def master_emulator(emulator: Optional[master_emulator.MasterEmulator], *args, **kwargs):
    app = quart.Quart(__name__)
    @app.route('/register' ,methods=['POST'])
    async def register():
        my_schema = schema.register_slave
        request_data = await quart.request.get_json()
        try:
            jsonschema.validate(instance=request_data, schema=my_schema)
            return quart.jsonify({"message": "registratior successful"}), 200
        except jsonschema.ValidationError as e:
            return quart.jsonify({"error": str(e)}), 400
        

    await app.run_task(*args, **kwargs)

if __name__ == "__main__":
    asyncio.run(master_emulator())