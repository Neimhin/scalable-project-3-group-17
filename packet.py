# Define the Data packets
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

