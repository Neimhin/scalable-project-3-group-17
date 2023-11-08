import requests
import json


def test_emulation_register():
    data = json.dumps({
        "port":  80801,
        "public_key": "blahblahblah"
    })
    headers = {
        "Content-Type": "application/json",
    }
    response = requests.post("http://localhost:33334/emulation/register",data,headers)
    if response.status_code != 200:
        print("FAIL: /emulation/register")
        print(response.status_code)
    else:
        print("PASS: /emulation/register")


# # Define the URL where you want to send the POST request
# url = 'http://localhost:8080'  # Replace with your target URL

# data = {
#     "name": "meaning of life",
#     "requested_by": "public of key of node interested",
# }

# # Encode the data as JSON
# json_data = json.dumps(data)

# # Set the headers to indicate that you are sending JSON data
# headers = {
#     'Content-Type': 'application/json',
#     'x-tcdicn-17-version': '1',
#     'x-tcdicn-type': 'subscription',
# }

# response = requests.post(url, data=json_data, headers=headers)

# if response.status_code == 200:
#     print("POST request was successful")
#     response_data = response.json()
#     import urllib.parse
#     parsed_url = urllib.parse.urlparse(respone.url)
#     server_ip = parsed_url.hostname
#     print(server_ip, response_data)

if __name__ == "__main__":
    test_emulation_register()
