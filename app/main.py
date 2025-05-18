import json
import sys
from bencode_deoder.bencode_decoder import bencode_decoder


def main():
    command = sys.argv[1]
    if command == "decode":
        bencode = sys.argv[2].encode()

        values = bencode_decoder.decode(bencode)
        print(values)

if __name__ == "__main__":
    main()