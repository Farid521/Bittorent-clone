import requests
import hashlib
from utils.bencode_decoder import BencodeDecoder

class peer:
    def __init__(self, decoded_bencode):
        self.bencode = decoded_bencode

    def discover(self):
        bencode = self.bencode
        data = BencodeDecoder(bencode)
        return data.decode(True)