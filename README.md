# TODO
- design devices, enumerate sensors and actuators
- design the "highly disconnected" scenario and use case to test/evaluate against
- create gateway emulators to connect between the pis
- - the master emulator runs a http server on port 34000
  - slave emulators run a http server on port 34000 or another port between 33000 and 34000 optionally
  - the slave emulators decide the connectivity of their own network
  - the slave emulators ask the master emulator about inter-emulator connectivity
  - e.g. POST "http://<master-emulator-ip>:34000/connectivity?node_adresses=<addr>:<port>:<uuid>,<addr>:<port>:<uuid>"
  - in English: "to whom can <uuid> (device 1), <uuid> (device 2), and <uuid> (device 3) connect?"
  - response: Dict(<uuid>, List(Tuple(<host>,<port>,<uuid>)))
  - in English: "the devices with id 'abc' can connect to the device (10.35.70.37, 33000, 'cba'), and (10.35.70.17, 33000, 'acb'), etc.
- improve performance
- improve code
- handshake to swap identities
- preshared trusted list of identities
- metrics and visualization
- run on the pi
- interop with Ted's tcdicn


# Secure ICN: Literature Review

> The power of the NDN architecture comes from **naming data hierarchically**
> with the granularity of network-level packets and sealing named data with public key signatures.
> Producers use **key names** to indicate which public key
> a consumer should retrieve to verify signatures of produced data packets.
> In addition to fetching the specified keys
> and performing signature verification,
> consumers also match data and key names to
> **determine whether the key is authorized to sign**
> each specific data packet.
> 
> — \cite{yu-alexander-clark-schematizing-trust}

A "key name" could be the hash of the public key.

>  Recent growth in e-commerce, digital media, social networking, and smartphone applications has resulted in the Internet primarily being used as a **distribution network**. Distribution networks are fundamentally more general than communication networks and solving distribution problems with a communications network is complex and error prone.
>
> — https://named-data.net/project/execsummary/

Further, Named Data Networking is an approach to networking that is
designed from the outset
to be conducive to building efficient
**distribution networks**.
Our scenario/use-case should ideally be a **distribution network** of some kind,
rather than a **communication network** (endpoint to endpoint).

# ICN Emulation

We name our protocol g17icn.

This document should describe g17icn version 0.1.

CS7NS1 Project 3 asks us to conceive, design, implement, build and prove a robust, secure, sufficient peer-to-peer networking protocol based (mandatorily!) on ICN principles.

We are also meant to conceive of a highly disconnected scenario in which the network runs and emulate various devices.

**Scenario**: Under water networks for climate and biodiversity monitoring and modelling.

**Motivation/Application**: Ocean temperatures, currents, El Niño and La Niña phenomena, are hard to predict and have huge implications for the weather experienced around the world. The increased number of rapidly escalating oceanic tornadoes is attributed to rising ocean temperatures; The New York times [reported on "The Daily"](https://www.nytimes.com/2023/10/27/podcasts/the-daily/hurricane-otis.html?showTranscript=1) an example of rapid escalation on 27th Oct. 2023, noting "Hurricane Otis transformed from a tropical storm to a deadly Category 5 hurricane in a day, defying forecasts."
> Well, to have a hurricane, you need to have warm water. It has to be 80 degrees Fahrenheit or higher to really give it the energy that it needs. So think of a hurricane as like an engine. and that energy, that warm water, is the fuel that’s fueling the hurricane.
> — Judson Jones


Incorporating these sensors into an integrated monitoring system would provide a comprehensive set of data crucial for accurate storm prediction. The data collected can feed into predictive models to forecast storm paths, intensities, and potential impacts, thereby aiding in early warning systems and preparedness efforts. Collaboration with meteorological agencies and leveraging advanced computational models for data analysis and simulation can further enhance the accuracy and reliability of storm predictions.


Having more realtime data about oceanic temperatures, not only at ocean surfaces but also in the depths, would help meteoroligists such as Judson Jones make more accurate predictions about the escalation of storms. Early warning and accurate prediction can help give vulnerable communities enough time to evacuate, saving lives.

**Notes on `g17icn-0.1`**:
- The protocol is built on HTTP and JWTs. Devices run HTTP servers that listen for connections and process both `interest` and `satisfy` packets.
- In version 0.1 we use JSON Web Signatures (JWS) **and not** JSON Web Encryption. See the [JWT RFC 7519](https://datatracker.ietf.org/doc/html/rfc7519).
- Packets are encoded as JWTs, both `interest` and `satisfy` packets, but some additional meta data about the `interest` or `satisfy` packet can be included in HTTP headers.
- All packets are signed by the producer of the packet. In version 0.1 we are using the RS256 algorithm to sign the JWTs. This prevents tampering, but does encrypt the data or keep it private.
- The protocol is lazy, in that data is only sent to the network after positive confirmation that there is interest in the data.
- TODO(optimization): batching. Since a packet is a self-contained JWT/JWS, we can actually send multiple packets in a single HTTP request. We should investigate whether this can be leveraged for performance gains or reduced network utilisation.
- TODO(security): pre-shared list of trusted keys. Whether a packet should be accepted is determined by whether it was signed by a trusted node. In version 0.1 we define a list of trusted nodes at the outset, and nodes can **not** be subsequently added to the list of trusted nodes. Each trusted node has a pub/priv RSA 256 key pair.


**interest packet**: An interest packet is just a signed JWT. We do not define any JWT headers in version 0.1. The payload of the JWT contains the mandatory fields: "type", "data_name", "requestor_id".
The optional fields in the payload are: "created_at", "expires_at"

## Interest Request Format:
In version 0.1 of `g17icn` interest requests are send over HTTP POST requests.
A peer can listen permanently for clients who want to propagate interest requests.
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

## Interfaces (JSON)

We will define all the devices with their particular data. We will also have the port numbers and ip addresses of the RPI on which the device will run on. It will also define all neighbours to the device so we can dynamically parse the information from here when running the devices.
