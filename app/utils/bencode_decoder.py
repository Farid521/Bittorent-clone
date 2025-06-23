import hashlib
from typing import Union, Tuple, List, Dict, Any, Optional

class BencodeDecoder:
    """
    A class for encoding and decoding bencode format data.
    Bencode is a simple encoding format used by BitTorrent for storing and transmitting data.
    """
    
    def __init__(self, data: Optional[bytes] = None):
        """
        Initialize the bencode decoder with optional bencoded data.
        
        Args:
            data: Bencoded data as bytes
        """
        self.bencode = data

    def __str__(self) -> str:
        return f'bencode {self.bencode}'

    def encode(self, data: Any = None) -> bytes:
        """
        Encode Python data structures to bencode format.

        Args:
            data: Data to encode (int, str, bytes, list, dict)

        Returns:
            Bencoded data as bytes

        Raises:
            TypeError: If data type is not supported
        """
        raw_data = data if data is not None else self.bencode

        if isinstance(raw_data, int):
            return b'i' + str(raw_data).encode() + b'e'

        elif isinstance(raw_data, bytes):
            return str(len(raw_data)).encode() + b':' + raw_data

        elif isinstance(raw_data, str):
            data_bytes = raw_data.encode('utf-8')
            return str(len(data_bytes)).encode() + b':' + data_bytes

        elif isinstance(raw_data, list):
            result = b'l'
            for item in raw_data:
                result += self.encode(item)
            result += b'e'
            return result

        elif isinstance(raw_data, dict):
            result = b'd'
            sorted_keys = sorted(raw_data.keys())
            for key in sorted_keys:
                if isinstance(key, str):
                    key_bytes = key.encode('utf-8')
                elif isinstance(key, bytes):
                    key_bytes = key
                else:
                    raise TypeError("Dictionary keys must be str or bytes")
                result += self.encode(key_bytes)
                result += self.encode(raw_data[key])
            result += b'e'
            return result

        else:
            raise TypeError(f"Type {type(raw_data)} is not supported in bencode")
        
    def decode(self, *args: Union[bytes, str]) -> Any:
        """
        Decode bencoded data.
        
        Args:
            data: Bencoded data to decode (uses self.bencode if None)
            return_info_hash: If True, return torrent info hash details
            
        Returns:
            Decoded data structure
        """
        raw_bencode = bytes()
        option = list()
        for arg in args:
            if isinstance(arg,bytes):
                raw_bencode = arg
                continue
            elif isinstance(arg, str):
                option.append(arg)

        if len(raw_bencode) == 0:
            raw_bencode = self.bencode

        decoded_value, _ = self._decode_value(raw_bencode, 0)

        if 'info' in option:
            bencode_info = self._get_info(decoded_value)
            return bencode_info

        return decoded_value

    def _decode_value(self, data: bytes, index: int) -> Tuple[Any, int]:
        """
        Decode a single value starting from the given index.
        
        Args:
            data: Bencoded data
            index: Starting index
            
        Returns:
            Tuple of (decoded_value, next_index)
        """
        if index >= len(data):
            raise ValueError("Unexpected end of data")
            
        current_char = chr(data[index])
        
        if current_char.isdigit():
            return self._decode_string(data, index)
        elif current_char == 'i':
            return self._decode_integer(data, index)
        elif current_char == 'l':
            return self._decode_list(data, index)
        elif current_char == 'd':
            return self._decode_dictionary(data, index)
        else:
            raise ValueError(f"Invalid bencode token '{current_char}' at index {index}")

    def _decode_string(self, data: bytes, index: int) -> Tuple[bytes, int]:
        """
        Decode a bencoded string.
        Format: <length>:<string_data>

        """
        # Find the length
        colon_index = index
        while colon_index < len(data) and chr(data[colon_index]) != ':':
            if not chr(data[colon_index]).isdigit():
                raise ValueError(f"Invalid character in string length at index {colon_index}")
            colon_index += 1

        if colon_index >= len(data):
            raise ValueError("Missing ':' in string encoding")

        # Parse length
        length_str = data[index:colon_index].decode('ascii')
        string_length = int(length_str)
        
        # Extract string data
        start_index = colon_index + 1
        end_index = start_index + string_length
        
        if end_index > len(data):
            raise ValueError("String length exceeds data bounds")
            
        string_data = data[start_index:end_index]
        return string_data, end_index

    def _decode_integer(self, data: bytes, index: int) -> Tuple[int, int]:
        """
        Decode a bencoded integer.
        Format: i<integer>e
        """
        index += 1  # Skip 'i'
        end_index = index
        
        # Find the end marker 'e'
        while end_index < len(data) and chr(data[end_index]) != 'e':
            end_index += 1
            
        if end_index >= len(data):
            raise ValueError("Missing 'e' at end of integer")
            
        # Parse integer
        integer_str = data[index:end_index].decode('ascii')
        try:
            integer_value = int(integer_str)
        except ValueError:
            raise ValueError(f"Invalid integer format: {integer_str}")
            
        return integer_value, end_index + 1

    def _decode_list(self, data: bytes, index: int) -> Tuple[List[Any], int]:
        """
        Decode a bencoded list.
        Format: l<elements>e
        """
        result = []
        index += 1  # Skip 'l'
        
        while index < len(data):
            if chr(data[index]) == 'e':
                return result, index + 1
                
            value, index = self._decode_value(data, index)
            result.append(value)
            
        raise ValueError("Missing 'e' at end of list")

    def _decode_dictionary(self, data: bytes, index: int) -> Tuple[Dict[bytes, Any], int]:
        """
        Decode a bencoded dictionary.
        Format: d<key><value>e
        """
        result = {}
        index += 1  # Skip 'd'
        
        while index < len(data):
            if chr(data[index]) == 'e':
                return result, index + 1
                
            # Decode key (must be a string/bytes)
            key, index = self._decode_value(data, index)
            if not isinstance(key, bytes):
                raise ValueError("Dictionary keys must be bytes")
                
            # Decode value
            value, index = self._decode_value(data, index)
            result[key] = value
            
        raise ValueError("Missing 'e' at end of dictionary")

    def _get_info(self, decoded_data: Dict[bytes, Any]) -> Dict:
        """
        Extract torrent info hash and related data.
        
        Args:
            decoded_data: Decoded torrent data
            original_data: Original bencoded data
            
        Returns:
            Tuple of (tracker_url, length, info_hash, piece_length, piece_hashes)
        """
        if not isinstance(decoded_data, dict) or b'info' not in decoded_data:
            raise ValueError("Invalid torrent data: missing 'info' section")

        info_dict = decoded_data[b'info']
        
        # Extract basic info
        tracker_url = decoded_data.get(b'announce','')
        length = info_dict.get(b'length', 0)
        # piece_length = info_dict.get(b'piece length', 0)
        
        # Calculate info hash
        raw_info_bencode = self.encode(info_dict)
        hashed_info_bencode = hashlib.sha1(raw_info_bencode).hexdigest()
        bytes_info_hash = hashlib.sha1(raw_info_bencode).digest()

        # Process pieces
        pieces_length = info_dict.get(b'piece length')


        pieces = info_dict.get(b'pieces', b'')
        piece_hashes = [pieces[i:i+20].hex() for i in range(0, len(pieces), 20)]

        bencode_info = {
            b'Tracker URL': tracker_url,
            b'Length': length,
            b'Info Hash': hashed_info_bencode,
            b'Bytes Info Hash': bytes_info_hash,
            b'Piece Length': pieces_length,
            b'Piece Hashes': piece_hashes
        }
        
        return bencode_info
    