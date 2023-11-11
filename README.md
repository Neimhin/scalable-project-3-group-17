# ICN Emulation
CS7NS1 Project 3 asks us to conceive, design, implement, build and prove a robust, secure, sufficient peer-to-peer networking protocol based (mandatorily!) on ICN principles.

We are also meant to conceive of a highly disconnected scenario in which the network runs and emulate various devices.

**Scenario**: Under water networks for climate and biodiversity monitoring and modelling.

**Motivation/Application**: Ocean temperatures, currents, El Niño and La Niña phenomena, are hard to predict and have huge implications for the weather experienced around the world. The increased number of rapidly escalating oceanic tornadoes is attributed to rising ocean temperatures; The New York times reported on "The Daily" an example of rapid escalation on 27th Oct. 2023, noting "Hurricane Otis transformed from a tropical storm to a deadly Category 5 hurricane in a day, defying forecasts."
> Well, to have a hurricane, you need to have warm water. It has to be 80 degrees Fahrenheit or higher to really give it the energy that it needs. So think of a hurricane as like an engine. and that energy, that warm water, is the fuel that’s fueling the hurricane.
> — Judson Jones
Having more realtime data about oceanic temperatures, not only at ocean surfaces but also in the depths, would help meteoroligists such as Judson Jones make more accurate predictions about the escalation of storms. Early warning and accurate prediction can help give vulnerable communities enough time to evacuate, saving lives.

## Interest Request Format:
TODO:
- use hash of public key instead of full public key
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
