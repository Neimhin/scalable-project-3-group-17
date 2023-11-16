import json

'''
Packet types

Discover: 

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


'''
Use as:

-------------------------------Create an Interest packet-------------------------------

interest = Interest(data_name="temperature/(129,30)", public_key="slkdjaskldjasldjlas",
                   time_stamp=time.time(), sender_address="192.168.1.100",
                   request_type="get", flag=1, waiting_list=[])

# Create a Data packet
data = Data(data_name="temperature/(129,30)", public_key="slkdjaskldjasldjlas",
                   time_stamp=time.time(), sender_address="192.168.1.100",
                   content="25.5")


                   
--------------------------------------Serialise packet-----------------------------------

interest_json = interest.to_json()
data_json = data.to_json()   

--------------------------------------Deserialise packet-----------------------------------

def deserialize_packet(json_packet):
    packet_type = json_packet["type"]
    if packet_type == "interest":
        return Interest.from_json(json_packet)
    elif packet_type == "data":
        return Data.from_json(json_packet)
    else:
        raise ValueError("Unknown packet type: {}".format(packet_type))

# Deserialize the JSON packets back to packet objects
interest_obj = deserialize_packet(interest_json)
data_obj = deserialize_packet(data_json)

'''