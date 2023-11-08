# tcdicn-17, group 17's implementation of tcdicn

## Interested Request Format:
{
    "data_name": request_type/(location),
    "public_key": public key value,
    "time_stamp": timevalue,
    "sender_address": sender_address
}

Eg:  {"data_name": "tempture/(129,30)" ,
      "public_key": "slkdjaskldjasldjlas",
      "timeStamp":timeValue,
      "sender_address": ? }

## Interesting Table Format

{
    "data_name":request_type/(location),
    "request_type":flag  # when flag=1 represented this request from other nodes, 0 represented from itself.
    "waiting_list":[]   #nodes index waiting for this request
}

## Neighbour 

neighbour list should include the port number and its location.locals

## Node

self.task_id = task_id  # ?
self.logger = logging.getLogger()
self.jwt = g17jwt.JWT().init_jwt(key_size=32)
self.PIT = {} # 
self.FIB = {}
self.emulation = emulation
self.location="124.0.0" # represented the node location
self.server = HTTPServer()
self.neighbour=[] # represented the node neighbour
