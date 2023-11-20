import socket
import netifaces

IP_ADDRESS = None

def get_ip_address():
    global IP_ADDRESS
    if IP_ADDRESS:
        return IP_ADDRESS

    try:
        interfaces = netifaces.interfaces()
        for interface in interfaces:
            addrs = netifaces.ifaddresses(interface)
            if netifaces.AF_INET in addrs:
                ipv4s = addrs[netifaces.AF_INET]
                for ipv4 in ipv4s:
                    ip = ipv4['addr']
                    if ip != "127.0.0.1":  # Exclude localhost
                        IP_ADDRESS = ip
                        return IP_ADDRESS

        return "No public IPv4 address found"
    except Exception as e:
        return str(e)

if __name__ == "__main__":
    print(get_ip_address())
