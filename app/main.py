import json
import sys
from bencode_decoder.bencode_decoder import bencode_decoder 
import hashlib

def torrent_file_read(path):
    with open(path,'rb') as file:
        content = file.read()
        return content

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
        
    elif command == "file_decode":
        if len(sys.argv) < 3:
            print("Usage: python main.py file_decode <file_path> [info]")
            sys.exit(1)

        file_path = sys.argv[2]
        # Periksa apakah sys.argv[3] diberikan
        bencode_specified_value = sys.argv[3] if len(sys.argv) > 3 else None

        if bencode_specified_value == 'info':
            content = torrent_file_read(file_path)

            decoded_bencode = bencode_decoder(content).decode(bencode_specified_value)
            # print(f'tracker_url: {decoded_bencode[0].decode()}\nlength: {decoded_bencode[1].decode()}\ninfo hash: {decoded_bencode[2]}\npieces length: {int(decoded_bencode[3])}\npiece hash: {decoded_bencode[4]}')
            print(
                f'tracker url: {decoded_bencode[0].decode()}\nlength: {decoded_bencode[1].decode()}\ninfo hash: {decoded_bencode[2]}\npiece length: {decoded_bencode[3].decode()}\npiece hashes: {decoded_bencode[4]}'

            )
            return

        content = torrent_file_read(file_path)

        decoded_bencode = bencode_decoder(content).decode()
        print(decoded_bencode)


if __name__ == "__main__":
    main()