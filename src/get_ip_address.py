import netifaces
from typing import Optional

cached_ip_address: Optional[str] = None

def get_ip_address() -> str:
    global cached_ip_address
    if cached_ip_address:
        return cached_ip_address

    try:
        interfaces = netifaces.interfaces()
        for interface in interfaces:
            addrs = netifaces.ifaddresses(interface)
            if netifaces.AF_INET in addrs:
                ipv4s = addrs[netifaces.AF_INET]
                for ipv4 in ipv4s:
                    ip = ipv4['addr']
                    if ip != "127.0.0.1":  # Exclude 127.0.0.1
                        cached_ip_address = ip
                        return ip

        return "No public IPv4 address found"
    except Exception as e:
        return str(e)

if __name__ == "__main__":
    print(get_ip_address())
