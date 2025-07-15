import requests
import socket
import hashlib
import random
import os
from utils.bencode_decoder import BencodeDecoder
from typing import Union, Tuple, List, Dict, Any, Optional

class Peer:
    def __init__(self, bencode: Optional[bytes]):
        if bencode is None:
            raise('bencode required')
        if not isinstance(bencode, bytes):
            raise ValueError('bencode must be a bytes')
        
        self.raw_bencode = bencode
        self.bencode = BencodeDecoder(bencode).decode()

    def __str__(self):
        return f'bencode: {self.bencode}'
    
    def discover(self) -> Any:
        bencode_info = BencodeDecoder(self.raw_bencode).decode('info')

        params = {
            'info_hash': bencode_info[b'Bytes Info Hash'],
            'peer_id': '00112233445566778899',
            'port': 6881,
            "uploaded": 0,
            "downloaded": 0,
            'left': bencode_info[b'Length']
        }

        URL = bencode_info[b'Tracker URL'].decode('utf-8')

        request = requests.get(URL, params=params)
        response = request.content
        decoded_response = BencodeDecoder(response).decode()

        peers = decoded_response.get(b'peers')
        decoded_response = dict()

        for peer in peers:
            decoded_response[(peer[b'ip']).decode()] = peer[b'port']

        return decoded_response
    
    def handshake(self, HOST: str | int, PORT: int) -> any:
        decoded_bencode = BencodeDecoder().decode(self.raw_bencode)
        bencode_info_part = decoded_bencode[b'info']
        hashed_info = hashlib.sha1(BencodeDecoder().encode(bencode_info_part)).digest()
        peer_id = os.urandom(20)
        payload = b'\x13BitTorrent protocol' + 8*b'\x00'+ hashed_info + peer_id
        
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                print(f"connecting to {HOST}, {PORT}")
                s.connect((HOST,PORT))
            except Exception as e :
                raise Exception(f'error: {e}')

            print("connected [200 OK]")
            s.send(payload)
            print("payload sent succesfully\n")
            server_response = s.recv(1024)

            info_index = server_response.find(hashed_info)
            if info_index != -1:
 
                peer_id_bytes = server_response[info_index + len(hashed_info): info_index + len(hashed_info) + 20]
                peer_id_hex = peer_id_bytes.hex()
                print(f"server response: {server_response.hex()}\npeer id hex: {peer_id_hex}\n")
            else:
                print("hashed_info not found in server response")

        return