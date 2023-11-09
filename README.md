# tcdicn-17, group 17's implementation of tcdicn

## Interest Packet Format (HTTP with plain text mime consisting of a JWT):
```json
x-tcdicn-hop: 0
{
    "data_name": request_type/(location),
    "requestor_public_key": public key value,
    "time_stamp": timevalue,
}
<signature>
```

Eg:  
```http
x-tcdicn-hop: 3
{
    "data_name": "tempture/(129,30)" ,
    "public_key": "slkdjaskldjasldjlas",
    "time_stamp":datetime.now().timestamp(),
}
<signature>
```

## Interesting Table Format

{
    "data_name":request_type/(location):
    {
        "request_type":flag  # when flag=1 represented this request from other nodes, 0 represented from itself.

        "waiting_list":[]   #nodes index waiting for this request
    }
}

## Neighbour 

neighbour list should include the port number ['port_number']

## CACHE FORMAT

{
    'tempture':value,
    "intensive_value":value,
    "....." : .....
}

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
