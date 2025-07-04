import json
import sys
from utils.bencode_decoder import BencodeDecoder
from utils.request import Peer
import hashlib
import bencodepy

def torrent_file_read(path):
    with open(path,'rb') as file:
        return file.read()

def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py <command> [options]")
        sys.exit(1)
        
    command = sys.argv[1]
    
    if command == "decode":
        if len(sys.argv) < 3:
            print("Usage: python main.py decode <bencode_string>")
            sys.exit(1)
        user_input = sys.argv[2]
        if isinstance(user_input, str):
            user_input = user_input.encode()

        values = user_input.decode()
        print(values)
        
    elif command == 'file_decode':
        options = sys.argv[3] if len(sys.argv) > 3 else None 
        raw_bencode = torrent_file_read(sys.argv[2])
        
        if options == 'peer_discover':
            con = Peer(raw_bencode)
            print(con.discover())

        


       


if __name__ == "__main__":
    main()