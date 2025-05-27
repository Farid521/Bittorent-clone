import json
import sys
from bencode_decoder.bencode_decoder import bencode_decoder

def main():
    command = sys.argv[1]
    if command == "decode":
        bencode = sys.argv[2].encode()
        values = bencode_decoder.parse(bencode)
        print(values)
        
    elif command == "file_decode":
        file_path = sys.argv[2]

        with open(file_path,"rb") as file:
            content = file.read()
            decoded_bencode = bencode_decoder.parse(content)
            print(decoded_bencode)
            
if __name__ == "__main__":
    main()