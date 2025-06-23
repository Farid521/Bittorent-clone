import requests
import hashlib
from utils.bencode_decoder import BencodeDecoder
from typing import Union, Tuple, List, Dict, Any, Optional
import bencodepy

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
        