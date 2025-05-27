class bencode_decoder:
    @staticmethod
    def concat_int(a):
        return int(''.join(map(str, a)))
    
    @staticmethod
    def string_decoder(bval, i) -> tuple:
        # Check the format untuk memastikan karakter pertama berupa digit
        if i >= len(bval) or not chr(bval[i]).isdigit():
            raise ValueError("Invalid bencode string format")
        
        # Mendapatkan panjang string
        length = []
        while i < len(bval) and chr(bval[i]).isdigit():
            length.append(int(bval[i:i+1]))
            i += 1
        string_length = bencode_decoder.concat_int(length)
        
        # Validasi format dengan memastikan ada ':' setelah panjang
        if chr(bval[i]) != ":":
            raise ValueError(f"Missing ':' at index {i}")
        
        i += 1  # lewati ':'
        bencode_string_value = bval[i:i+string_length]
        end_index = i + string_length
        return bencode_string_value, end_index

    @staticmethod
    def integer_decoder(bval, i) -> tuple:
        if chr(bval[i]) != "i":
            raise ValueError(f"Invalid bencode integer format at index: {i}")
        
        i += 1  # lewati 'i'
        bencode_integer_value = b""
        while i < len(bval) and chr(bval[i]) != "e":
            bencode_integer_value += bval[i:i+1]
            i += 1
        end_index = i + 1  # lewati 'e'
        return bencode_integer_value, end_index
        
    @staticmethod
    def list_decoder(bval, i) -> tuple:
        bencode_list_value = []
        if i >= len(bval) or chr(bval[i]) != "l":
            raise ValueError(f"Invalid format at index {i} value: {chr(bval[i])}")
        
        i += 1  # lewati 'l'
        while i < len(bval):
            if chr(bval[i]) == "e":
                i += 1  # lewati 'e'
                return bencode_list_value, i
            if i >= len(bval):
                raise ValueError(f"Unexpected end of data at index {i}")
            value, i = bencode_decoder.parse_by_type(bval, i)
            bencode_list_value.append(value)
        
        raise ValueError("Missing 'e' at the end of list")

    @staticmethod
    def dictionaries_decoder(bval, i) -> tuple:
        bencode_dictionaries_value = {}
        if chr(bval[i]) != "d":
            raise ValueError(f"Invalid bencode dictionaries format: missing 'd' at index {i}")
        
        i += 1  # lewati 'd'
        while i < len(bval) and chr(bval[i]) != "e":
            key, i = bencode_decoder.parse_by_type(bval, i)
            if chr(bval[i]) == "e":
                raise ValueError("dictionaries must be in <key:value> format")
            value, i = bencode_decoder.parse_by_type(bval, i)
            bencode_dictionaries_value[key] = value        
    
        if chr(bval[i]) != "e":
            raise ValueError("Missing 'e' at the end of bencode dictionaries")
        
        end_index = i + 1  # lewati 'e'
        return bencode_dictionaries_value, end_index

    @staticmethod
    def parse_by_type(bval, i) -> tuple:
        if chr(bval[i]).isdigit():
            return bencode_decoder.string_decoder(bval, i)
        elif chr(bval[i]) == "i":
            return bencode_decoder.integer_decoder(bval, i)
        elif chr(bval[i]) == "l":
            return bencode_decoder.list_decoder(bval, i)
        elif chr(bval[i]) == "d":
            return bencode_decoder.dictionaries_decoder(bval, i)
        else:
            raise ValueError(f"Invalid bencode format at index: {i} value: {chr(bval[i])}")

    @staticmethod
    def parse(bval, i=0):
        if not isinstance(bval, bytes):
            raise ValueError("Input data bencode harus berupa byte string (bytes)")
        results = []
        while i < len(bval):
            val, i = bencode_decoder.parse_by_type(bval, i)
            results.append(val)
        return results