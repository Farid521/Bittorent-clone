from bencode_decoder.bencode_decoder import bencode_decoder
import bencodepy

with open("./sample.torrent", 'rb') as file:
    content = file.read()
    decoded = bencode_decoder.decode(content)
    print(decoded[0])
