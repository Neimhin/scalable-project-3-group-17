import subprocess

def get_ip_address():
    try:
        # Run the ip addr command and capture the output
        result = subprocess.run(["ip", "addr"], stdout=subprocess.PIPE, text=True)

        # Filter lines that contain 'inet' but not 'inet6' (to exclude IPv6 addresses)
        lines = [line.strip() for line in result.stdout.split('\n') if 'inet ' in line and 'inet6' not in line]

        # Extract the IP addresses
        ip_addresses = [line.split(' ')[1].split('/')[0] for line in lines]
        return ip_addresses[1]
    except Exception as e:
        # Handle exceptions (e.g., command not found, permission denied)
        return str(e)

if __name__ == "__main__":
    print(get_ip_address())