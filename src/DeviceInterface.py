import ipaddress

# CONTRIBUTOR: NAARORA

class DeviceInterface:
    def __init__(self, host,port,key_name):
        self.host = host
        self.port = port
        self.key_name = key_name

    
    def url(self):
        return f"http://{self.host}:{self.port}"
    
    def to_dict(self):
        return {
            "host": self.host,
            "port": self.port,
            "key_name": self.key_name,
        }
    

    @staticmethod
    def from_dict(d: dict) -> 'DeviceInterface':
        host = d["host"]
        # ip = host.split(".")
        try:
            # Validate IP address
            ipaddress.ip_address(d["host"])
            host = d["host"]
            port = d["port"]
            key_name = d["key_name"]
            return DeviceInterface(host=host, port=port, key_name=key_name)
        except ValueError:
            print("Invalid IP address:", d["host"])
            raise
        except KeyError as e:
            print("Missing host in devices:", e)
        raise

    def __name__(self):
        import json
        return json.dumps(self.to_dict())

    @staticmethod
    # param device: DeviceInterface
    def from_device(device) -> 'DeviceInterface':
        host = device.server.host
        if not host == '127.0.0.1':
            ip = host.split(".")
            try:
                assert len(ip) == 4
                assert int(ip[0]) and int(ip[1]) and int(ip[2]) and int(ip[3])
            except AssertionError:
                print("host is not an ip address", ip, host)
                exit()
        port = device.server.port
        key_name = device.jwt.key_name
        return DeviceInterface(host,port,key_name)

    @staticmethod
    def from_dict(d) -> 'DeviceInterface':
        host:str = d["host"]
        port:int = d["port"]
        key_name = d["key_name"]
        return DeviceInterface(host=host,port=port,key_name=key_name)

    def __str__(self):
        return self.host + ":" + str(self.port) + "  " + self.key_name[:10]