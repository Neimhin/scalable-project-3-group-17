import json

'''
Packet types

Interest: A consumer puts the name of a desired piece of data into an 
Interest packet and sends it to the network. 
Routers use this name to forward the Interest toward the data producer(s).

Data: Once the Interest reaches a node that has the requested data, 
the node will return a Data packet that contains both the name and the content, 
together with a signature by the producer's key which binds the two. 
This Data packet follows in reverse the path taken by the Interest to 
get back to the requesting consumer.

'''

class Packet:
    def __init__(self, data_name, public_key, time_stamp, sender_address):
        self.data_name = data_name
        self.public_key = public_key
        self.time_stamp = time_stamp
        self.sender_address = sender_address

    def to_json(self):
        return json.dumps({
            "data_name": self.data_name,
            "public_key": self.public_key,
            "time_stamp": self.time_stamp,
            "sender_address": self.sender_address
        })

class Interest(Packet):
    def __init__(self, data_name, public_key, time_stamp, sender_address, request_type, flag, waiting_list):
        super().__init__(data_name, public_key, time_stamp, sender_address)
        self.request_type = request_type
        self.flag = flag
        self.waiting_list = waiting_list

class Data(Packet):
    def __init__(self, data_name, public_key, time_stamp, sender_address, content):
        super().__init__(data_name, public_key, time_stamp, sender_address)
        self.content = content

