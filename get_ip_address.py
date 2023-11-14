import subprocess

IP_ADDRESS = None

def get_ip_address():
    global IP_ADDRESS
    if IP_ADDRESS:
        return IP_ADDRESS
    try:
        # run the ip addr command and capture the output
        result = subprocess.run(["ip", "addr"], stdout=subprocess.PIPE, text=True)
        # gilter lines that contain 'inet' but not 'inet6' (to exclude IPv6 addresses)
        lines = [line.strip() for line in result.stdout.split('\n') if 'inet ' in line and 'inet6' not in line]
        # extract the IP addresses
        ip_addresses = [line.split(' ')[1].split('/')[0] for line in lines]
        IP_ADDRESS = ip_addresses[1]
        return IP_ADDRESS
    except Exception as e:
        # Handle exceptions (e.g., command not found, permission denied)
        return str(e)

if __name__ == "__main__":
    print(get_ip_address())
    print(get_ip_address())
    print(get_ip_address())