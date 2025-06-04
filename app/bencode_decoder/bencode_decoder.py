import hashlib
import bencodepy

class bencode_decoder:
    def __init__(self, bencode):
        """
        Initializes the bencode decoder with the provided bencoded data.
        """
        self.bencode = bencode

    def single_value_decode(self, bencode, i):
        """
        Helper method to decode a single value (integer, list, dictionary, or string)
        starting from index i.
        """
        dispatch = {
            'i': self.integer_decoder,
            'l': self.list_decoder,
            'd': self.dictionaries_decoder
        }

        current_char = chr(bencode[i])
        if current_char.isdigit():
            value, i = self.string_decoder(bencode, i)
        elif current_char in dispatch:
            value, i = dispatch[current_char](bencode, i)
        else:
            raise ValueError(f"Invalid token '{current_char}' at index {i}")

        return value, i

    def decode(self, *args):
        """
        Main function to decode the entire bencoded data.
        Additional arguments may specify options (e.g., "with_index") or starting index.
        """
        parsed_values = []
        bencode = self.bencode
        options = set()
        i = 0

        # Determine options and starting index
        for option in args:
            if isinstance(option, str):
                options.add(option)
            elif isinstance(option, int):
                i = option

        dispatch = {
            'i': self.integer_decoder,
            'l': self.list_decoder,
            'd': self.dictionaries_decoder
        }

        while i < len(bencode):
            current_char = chr(bencode[i])
            if current_char.isdigit():
                # Decode string
                value, i = self.string_decoder(bencode, i)
                parsed_values.append(value)
            elif current_char in dispatch:
                # Decode integer, list, or dictionary
                value, i = dispatch[current_char](bencode, i)
                parsed_values.append(value)
            else:
                raise ValueError(f"Invalid bencode format at index {i} content: {chr(bencode[i])}")

        # Return with index if requested, otherwise just return the value(s)
        if "with_index" in options:
            return (parsed_values, i) if len(parsed_values) > 1 else (parsed_values[0], i)
        elif "info" in options:
            info = self.info_hash(parsed_values[0])
            return info
        return parsed_values if len(parsed_values) > 1 else parsed_values[0]

    def info_hash(self,decoded_bencode):

        tracker_url = decoded_bencode.get(b'announce')
        length = decoded_bencode.get(b'info').get(b'length')
        piece_length = decoded_bencode.get(b'info').get(b'piece length')

        '''
        we're currently using "Trick" because we don't have the encode method yet
        
        '''
        info_index = self.bencode.find(b'info') + 4
        hashed = hashlib.sha1(self.bencode[info_index:-1]).hexdigest()

        # hashed pieces
        pieces = decoded_bencode.get(b'info').get(b'pieces')
        parts_of_pieces = [pieces[i:i+20] for i in range(0,len(pieces),20)]
        hashed_pieces_part = []
        
        for part in parts_of_pieces:
            hashed_pieces_part.append(part.hex())

        return tracker_url, length, hashed, piece_length,hashed_pieces_part

    def string_decoder(self, bencode, i=0) -> tuple:
        """
        Decodes a bencoded string starting at index i.
        The format is: <length>:<string_data>
        """
        length_digits = []
        while i < len(bencode) and chr(bencode[i]).isdigit():
            # Convert byte to integer digit and store
            length_digits.append(int(bencode[i:i+1]))
            i += 1

        # Determine the length of the string
        string_length = int(''.join(map(str, length_digits)))

        # Check for the colon separator
        if chr(bencode[i]) != ":":
            raise ValueError(f"Missing ':' at index {i}")
        i += 1  # Skip the colon

        # Extract the string data based on the specified length
        bencode_string_value = bencode[i:i+string_length]
        end_index = i + string_length
        return bencode_string_value, end_index

    def integer_decoder(self, bencode, i=0) -> tuple:
        """
        Decodes a bencoded integer starting at index i.
        The format is: i<integer>e
        """
        i += 1  # Skip 'i'
        integer_bytes = b""  # Buffer for number bytes
        while i < len(bencode) and chr(bencode[i]) != "e":
            integer_bytes += bencode[i:i+1]
            i += 1

        end_index = i + 1  # Skip 'e'
        return integer_bytes, end_index

    def list_decoder(self, bencode, i) -> tuple:
        """
        Decodes a bencoded list starting at index i.
        The format is: l<elements>e
        """
        bencode_list_value = []
        i += 1  # Skip 'l'

        while i < len(bencode):
            if chr(bencode[i]) == "e":
                i += 1  # Skip 'e'
                return bencode_list_value, i

            if i >= len(bencode):
                raise ValueError(f"Unexpected end of data at index {i}")

            # Decode each element recursively
            value, i = self.single_value_decode(bencode, i)
            bencode_list_value.append(value)

        return bencode_list_value, i

    def dictionaries_decoder(self, bencode, i) -> tuple:
        """
        Decodes a bencoded dictionary starting at index i.
        The format is: d<key><value>e
        """
        bencode_dictionaries_value = {}
        i += 1  # Skip 'd'

        while i < len(bencode) and chr(bencode[i]) != 'e':
            # Decode key and value recursively
            key, i = self.single_value_decode(bencode, i)
            val, i = self.single_value_decode(bencode, i)
            bencode_dictionaries_value[key] = val

        if chr(bencode[i]) != "e":
            raise ValueError("Missing 'e' at the end of bencoded dictionary")

        end_index = i + 1  # Skip 'e'
        return bencode_dictionaries_value, end_index