# tcdicn-17, group 17's implementation of tcdicn

## Interest Request Format:
```http
HTTP 1.1
x-tcdicn-hop: 0
base64(<jwt-headers>
.{
    "type": "interest",
    "data_name": "/temperature/(129,30)" ,
    "requestor_public_key": "------PUBLIC KEY-----. .....",
    "created_at": 1231234.123,
}.
<signature>)
```

```http
HTTP 1.1
x-tcdicn-hop: 0
base64(<jwt-headers>
.{
    "type": "satisfy",
    "data_name": "/temperature/(129,30)" ,
    "data": {"unit": "celsius", "value": 8},
    "sender_public_key": "------PUBLIC KEY-----. .....",
    "created_at": 1231234.123,
}.
<signature>)
```

## Interest Table Format

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
self.PIT = {}
self.FIB = {}
self.emulation = emulation
self.location="124.0.0" # represented the node location
self.server = HTTPServer()
self.neighbour=[] # represented the node neighbour

## Cache

self.CIS = {}
self.PIT = {}
self.FIB = {}
