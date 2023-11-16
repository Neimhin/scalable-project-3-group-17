def emulator_interface(d):
    return '<h2>' + d['host'] + ':' + str(d['port']) + '</h2>'

def emulator(data):
    html_content = '<div>'
    html_content += '<h1>Device List</h1>'
    html_content += '<ul>'

    html_content += emulator_interface(data['emulator_interface'])

    for device in data['devices']:
        device_info = f"key_name: {device['key_name']}<br>host: {device['host']}<br>port: {device['port']}<br>public_key:<br><textarea readonly rows='4' cols='50'>{device['public_key']}</textarea>"
        html_content += f'<li>{device_info}<br><button onclick="load_cache_of_device(\'{device["key_name"]}\')">load cache</button></li>'

    html_content += '</ul>'
    html_content += '</div>'

    return html_content
