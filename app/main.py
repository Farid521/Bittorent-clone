import json
import sys
from utils.bencode_decoder import BencodeDecoder
from utils.request import Peer
import hashlib
import bencodepy

def torrent_file_read(path: str) -> bytes:
    try:
        with open(path,'rb') as file:
            return file.read()
    except FileNotFoundError:
        raise FileExistsError(f'file at path: {path} cannot be found')
    except:
        raise (f'error at finding bencode file at: {path}')

def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python main.py <command> [options]")
        sys.exit(1)

    command: str = sys.argv[1]
    
    if command == "decode":
        if len(sys.argv) < 3:
            print("Usage: python main.py decode <bencode_string>")
            sys.exit(1)
        user_input: str = sys.argv[2]

        if isinstance(user_input, str):
            user_input: bytes = user_input.encode()

        values = user_input.decode()
        print(values)
        
    elif command == 'file_decode':
        options: str = sys.argv[3] if len(sys.argv) > 3 else None 
        raw_bencode: bytes = torrent_file_read(sys.argv[2])
        decoded_bencode = BencodeDecoder(raw_bencode).decode()

        if options == 'peer_discover':
            con: object = Peer(raw_bencode)
            con.handshake('165.232.38.164', 51433)
            return
        
        decoded_bencode = BencodeDecoder(raw_bencode).decode()
        print(decoded_bencode)

if __name__ == "__main__":
    main()