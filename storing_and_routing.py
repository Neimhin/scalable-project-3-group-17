'''
All the forwarding logic will go here
Will absatract away from the Node file

contributor: <NamaN ArorA TASK>

Define the classes for Interest Packet and Data Packet.

Implement the NDN node with Content Store, PIT, and FIB.

Define the logic for handling incoming Interest packets, including:
- Checking the Content Store for matching data.
- Adding the Interest to the PIT if the data is not available.
- Forwarding the Interest based on the FIB.

Define the logic for handling incoming Data packets, including:
- Forwarding the Data to all faces listed in the matching PIT entry.
- Caching the Data in the Content Store.
- Removing the PIT entry.

'''

# TODO: Update based on packet structure from packet.py
class InterestPacket:
    def __init__(self, data_name, other_parameters):
        self.data_name = data_name
        self.other_parameters = other_parameters

class DataPacket:
    def __init__(self, data_name, content, signature):
        self.data_name = data_name
        self.content = content
        self.signature = signature

class ContentStore:
    def __init__(self):
        self.store = {}

    def add_data(self, data_packet):
        self.store[data_packet.data_name] = data_packet

    def get_data(self, data_name):
        return self.store.get(data_name, None)

class PITEntry:
    def __init__(self, data_name):
        self.data_name = data_name
        self.requesting_devices = []

class PIT:
    def __init__(self):
        self.entries = {}

    def add_interest(self, interest_packet, device_id):
        if interest_packet.data_name not in self.entries:
            self.entries[interest_packet.data_name] = PITEntry(interest_packet.data_name)
        self.entries[interest_packet.data_name].requesting_devices.append(device_id)

    def get_devices(self, data_name):
        return self.entries[data_name].requesting_devices if data_name in self.entries else []

    def remove_entry(self, data_name):
        if data_name in self.entries:
            del self.entries[data_name]

class FIBEntry:
    def __init__(self, prefix):
        self.prefix = prefix
        self.device_list = []

class FIB:
    def __init__(self):
        self.entries = {}

    def add_route(self, prefix, device_id):
        if prefix not in self.entries:
            self.entries[prefix] = FIBEntry(prefix)
        self.entries[prefix].device_list.append(device_id)

    def lookup(self, data_name):
        # Simplified longest prefix matching for now
        for prefix in sorted(self.entries.keys(), reverse=True):
            if data_name.startswith(prefix):
                return self.entries[prefix].device_list
        return []

class Routing:
    def __init__(self):
        self.content_store = ContentStore()
        self.pit = PIT()
        self.fib = FIB()
        # self.devices would be a mapping of device IDs to network interfaces or connections
        # for us it will the ports ??

    def handle_interest(self, interest_packet, incoming_device):
        # Check content store
        data = self.content_store.get_data(interest_packet.data_name)
        if data:
            # Data is available, send it back
            return data
        else:
            # Add to PIT and forward based on FIB
            self.pit.add_interest(interest_packet, incoming_device)
            devices_to_forward = self.fib.lookup(interest_packet.data_name)
            for device in devices_to_forward:
                if device != incoming_device:
                    # Forward interest packet to the device
                    pass  # forward the packet here

    def handle_data(self, data_packet, incoming_device):
        # Forward data to all devices in PIT entry
        devices = self.pit.get_devices(data_packet.data_name)
        for device in devices:
            if device != incoming_device:
                # Forward data packet to the device
                pass  # forward the packet here
        # Remove PIT entry
        self.pit.remove_entry(data_packet.data_name)
        # Add data to content store
        self.content_store.add_data(data_packet)
