import httpx
import json


def emulator_interface(d):
    return '<h2>' + d['host'] + ':' + str(d['port']) + '</h2>'

async def emulator(data):
    html_content = '<div>'
    html_content += '<h1>Device List</h1>'
    html_content += '<ul>'

    html_content += emulator_interface(data['emulator_interface'])

    ei = data['emulator_interface']
    host = ei['host']
    port = ei['port']

    response = None
    async with httpx.AsyncClient() as client:
        response = await client.get(f"http://{host}:{port}/all_dbs")
        response = response.json()

    devices = sorted(data['devices'],key=lambda item: item['key_name'])
    dbs = sorted(response,key=lambda item: item['key_name'])
    print(devices)
    print(dbs)
    for device, db in zip(devices,dbs):
        print(db)
        device_info = f"<ul>"
        device_info += f"<li>key_name: {device['key_name']}</li>"
        device_info += f"<li>host: {device['host']}</li>"
        device_info += f"<li>port: {device['port']}</li>"
        device_info += f"</ul>"
        # device_info += f"<br>public_key:<br><textarea readonly rows='4' cols='50'>{device['public_key']}</textarea>"
        device_info += f"<div>CACHE{db['CACHE']}</div>"
        html_content += f'<li>{device_info}<br></li>'

    html_content += '</ul>'
    html_content += '</div>'

    return html_content
