class bencode:
    def __init__(self, bencode):
        self.bencode = bencode

    def single_value_decode(self,bencode,i):
        dispatch = {
            'i': self.integer_decoder,
            'l': self.list_decoder,
            'd': self.dictionaries_decoder
        }

        d = chr(bencode[i])
        if d.isdigit():
            val,i = self.string_decoder(bencode,i)
        elif d in dispatch:
            val,i = dispatch[d](bencode,i)
        return val, i

    def decode(self,*args):
        parsed_bencode = []
        bencode = self.bencode
        options = set()
        i = 0

        for option in args:
            if isinstance(option,str):
                options.add(option)
            elif isinstance(option,int):
                i = option

        discpatch = {
            'i': self.integer_decoder,
            'l': self.list_decoder,
            'd': self.dictionaries_decoder
        }

        while i < len(bencode):
            d = chr(bencode[i])

            if d.isdigit():
                val,i = self.string_decoder(bencode,i)
                parsed_bencode.append(val)
            elif d in discpatch:
                val,i = discpatch[d](bencode,i)
                parsed_bencode.append(val)
            else:
                raise ValueError("invalid bencode format")

        if "with_index" in options:
            return (parsed_bencode, i) if len(parsed_bencode) > 1 else (parsed_bencode[0], i)
        return parsed_bencode if len(parsed_bencode) > 1 else parsed_bencode[0]

    def string_decoder(self,bencode, i=0) -> tuple:
        # Mendapatkan panjang string
        length = []
        while i < len(bencode) and chr(bencode[i]).isdigit():
            length.append(int(bencode[i:i+1]))
            i += 1
        string_length = int(''.join(map(str,length)))
        
        # Validasi format dengan memastikan ada ':' setelah panjang
        if chr(bencode[i]) != ":":
            raise ValueError(f"Missing ':' at index {i}")
        
        i += 1  # lewati ':'
        bencode_string_value = bencode[i:i+string_length]
        end_index = i + string_length
        return bencode_string_value, end_index

    def integer_decoder(self,bencode, i=0) -> tuple:

        i += 1  # lewati 'i'
        bencode_integer_value = b""
        while i < len(bencode) and chr(bencode[i]) != "e":
            bencode_integer_value += bencode[i:i+1]
            i += 1
        end_index = i + 1  # lewati 'e'
        return bencode_integer_value, end_index
        
    def list_decoder(self, bencode, i) -> tuple:

        bencode_list_value = []

        i += 1  # lewati 'l'
        while i < len(bencode):
            if chr(bencode[i]) == "e":
                i += 1  # lewati 'e'
                return bencode_list_value, i

            if i >= len(bencode):
                raise ValueError(f"Unexpected end of data at index {i}")

            value, i = self.single_value_decode(bencode,i)
            bencode_list_value.append(value)

        return bencode_list_value, i
    
    def dictionaries_decoder(self,bencode,i):
        bencode_dictionaries_value = {}
        
        i += 1  # lewati 'd'
        while i < len(bencode) and chr(bencode[i]) != 'e':
            
            key,i = self.single_value_decode(bencode,i)
            val,i = self.single_value_decode(bencode,i)

            bencode_dictionaries_value[key] = val
        if chr(bencode[i]) != "e":
            raise ValueError("Missing 'e' at the end of bencode dictionaries")
        
        end_index = i + 1  # lewati 'e'
        return bencode_dictionaries_value, end_index
    
data = bencode(b'd4:datai8888ee')
print(data.decode())