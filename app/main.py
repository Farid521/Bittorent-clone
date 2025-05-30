import json
import sys
from bencode_decoder.bencode_decoder import bencode_decoder as bencode

def main():
    command = sys.argv[1]
    if command == "decode":
        user_input = sys.argv[2].encode()
        values = bencode.parse(user_input)
        print(values)
        
    elif command == "file_decode":
        file_path = sys.argv[2]
        try:
            with open(file_path,"rb") as file:
                content = file.read()
                decoded_bencode = bencode.parse(content)
                print(decoded_bencode)
        except FileNotFoundError:
            raise("file not found")
        
if __name__ == "__main__":
    main()