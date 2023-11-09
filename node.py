'''
G17 ICN Node
'''

import httpx
import logging
import aiohttp
from aiohttp import web
import asyncio
import datetime

import g17jwt
from http_server import HTTPServer
from cache import CACHEStore


class G17ICNNODE:
    def __init__(self, task_id, emulation):
        self.task_id = task_id
        self.logger = logging.getLogger()
        self.emulation = emulation
        self.HOSTNAME = 'http://localhost:'
        self.CACHE = CACHEStore()

    async def handle_interest_packet(self, packet):
        request_interesting=packet['data_name']
        if packet['location']==self.location:
            request_type=request_interesting.split("/")[0]  # request_type value should be "temperature", "light_intensity" and anything else like this.
            packet["data"]=self.CACHE[request_type]
            return self.jwt.encode( packet)
        else:
            if self.PIT[request_interesting]==None:
                #self.PIT[request_interesting]={}
                sub_dict={}
                sub_dict['flag']=flag
                sub_dict['waiting_list']=[packet['public_key']]
                self.PIT[request_interesting]=sub_dict
            else:
                self.PIT[request_interesting]['waiting_list'].append(packet['public_key'])
            
            message=self.jwt.encode({
                        'data_name':request_interesting,
                        "public_key":self.jwt.public_key,
                        "time_stamp":time,
                        "hop_number":packet['hop_number']+1,
                        "data":packet["data"]
                    })

            if self.FIB[request_interesting]==None:
                min_hop=100000,
                min_port=-1
                time=datetime.now().timestamp()

                for neighbor in self.neighbour:
                    
                    print(f"send intereseting message to {neighbor}")
                    response = send_interest_to(neighbor,message)
                    res=self.jwt.decode(response)
                    if min_hop>res['hop_number']:
                        min_port=neighbor
                port_info={}
                port_info['time_stamp']=datetime.now().timestamp()
                port_info['min_hop']=min_port
                self.FIB[request_interesting]=port_info
                
            else:
                port = self.FIB[request_interesting]
                respond=self.send_interes_to(port,message)
            
            return response

    def discover_neighbours(self):
        '''
        Handle an interest request (whih is a JWT).
        When we get a request from another node, we will first check the self.PIT to find if we have already received this interest request.
        If we have, do not pass this request, and sender to list of nodes waiting for that data.
        When an interest request is received, it should check the time validity, if not valid, discard it.
        If valid respond to the sender with a 200 OK response code.
        It will check its` cache, if there is an entry suitable to satisfy the interest request, respond with the data as a JWT.
        If not, it will use the self.FIB to pass this request to the next hop and save this request to its pit.
        TO BE CONTINUE lol
        '''
        self.neighbour = self.emulation.discover_neighbours(self.task_id)
        self.logger.debug(f"got neighbours {str(self.neighbour)}")
        return self.neighbour
    
    async def handler(self, request):
        '''
        When nodeA gets a request from another nodeB, nodeA will first check the location. 
        If the location point to nodeA then nodeA will check cache to see whether it has the data. 
        If nodeA does not satisfy the requirement of location, 
        it will save this request to its interested table and 
        send this request to next hop follow the entry of Forwarding Infromation Base(FIB)
        If there is another same request coming to nodeA, 
        nodeA will discard this request and put this request sender in waiting list.
        
        Parameters:
            request`s format: disctionary which include:
            "data_name": request_type/(location),
            "public_key": public key value,
            "time_stamp": timevalue,
        '''
        t = await request.text()
        print(t)
        packet = self.jwt.decode(t)
        print(packet)
        # TODO: validate packet format
        asyncio.create_task(self.handle_interest_packet(packet))
        return web.Response(text="ok")


    # send interest to data to the network to satisfy interest
    async def get(self,data_name):
        cached_data = self.CACHE.get(data_name)
        if cached_data:
            return
        for port in self.neigbour_ports:
            await self.send_interest_to(port, data_name)
        pass

    async def send_interest_to(self,port,data_name):
        if not port:
            return
        async with httpx.AsyncClient() as client:
            payload = self.jwt.encode({
                "type": "interest",
                "name": data_name,
                "public_key": self.jwt.public_key.decode('utf-8')
                })
            response = await client.post(self.HOSTNAME + str(port), content=payload)
            # print("RESPONSE", response.text)
            # TODO handle 200 ok response and error responses
    
    # send named data to the network
    '''
    Progate the data 
    '''
    async def send_to_network(self):
        pass


    async def start(self):
        self.jwt = g17jwt.JWT()
        # print(self.jwt)
        self.jwt.init_jwt(key_size=32)        
        self.PIT = {} 
        self.FIB = {}
        self.CACHE = {}
        
        async def handler_async(request):
            return await self.handler(request)
        
        self.server = HTTPServer(handler_async)
        self.desires = ["/port/0", "/port/1", "/port/2"]
        self.neigbour_ports = []
        self.logger.debug(f"starting node {self.task_id}")
        
        await self.server.start()
        
        data_name = f"/port/{self.task_id}"
        # print(self.jwt)
        
        data = self.jwt.encode({data_name: self.server.port})
        self.CACHE[data_name] = data
        
        while True:
            self.neigbour_ports = self.discover_neighbours()
            await asyncio.gather(*[asyncio.create_task(self.get(desire)) for desire in self.desires])
                
            self.logger.debug(f"still running on port {self.server.port}: task_id: {self.task_id}")
            await asyncio.sleep(3)
