class bencode_decoder:
    @staticmethod
    def string_decoder(bval, i) -> tuple:
        # Check the format to ensure the current character is a digit
        if i >= len(bval) and not chr(bval[i]).isdigit():
            raise ValueError("Invalid bencode string format")
        
        # Get the string length
        string_length = 0
        while i < len(bval) and chr(bval[i]).isdigit():
            string_length += int(bval[i:i+1])
            i += 1

        # Validate the format by checking for ':'
        if not chr(bval[i]) == ":":
            raise ValueError(f"Missing ':' at index {i}")

        # Skip the ':'
        i += 1

        # Extract the string value and update the index
        bencode_string_value = bval[i:i+string_length]
        end_index = i + string_length
        
        return bencode_string_value, end_index
    
    @staticmethod
    def integer_decoder(bval, i) -> tuple:
        # Validate the format to ensure it starts with 'i'
        if not chr(bval[i]) == "i":
            raise ValueError(f"Invalid bencode integer format at index: {i}")
        
        # Skip the 'i'
        i += 1

        bencode_integer_value = b""
        # Read until the 'e' character is found
        while i < len(bval) and chr(bval[i]) != "e":
            bencode_integer_value += bval[i:i+1]
            i += 1
        end_index = i + 1
        
        return bencode_integer_value, end_index
        
    @staticmethod
    def list_decoder(bval, i) -> tuple:
        bencode_list_value = []

        # Validate the format by checking for 'l'
        if i >= len(bval) or chr(bval[i]) != "l":
            raise ValueError(f"Invalid format at index {i}")

        i += 1  # Skip the 'l'

        while i < len(bval):
            # If 'e' is found, it marks the end of the list
            if chr(bval[i]) == "e":
                i += 1  # Skip the 'e'
                return bencode_list_value, i

            # Ensure the index does not go out of bounds before processing the next element
            if i >= len(bval):
                raise ValueError(f"Unexpected end of data at index {i}")

            # Parse the element based on its type
            value, i = bencode_decoder.parse_by_type(bval, i)
            bencode_list_value.append(value)

        # If the loop finishes without finding 'e', the format is invalid
        raise ValueError("Missing 'e' at the end of list")

    @staticmethod
    def dictionaries_decoder(bval,i) -> tuple:
        bencode_dictionaries_value = {}
    
        # validating the dictionaries format by ensuring it contains 'd'
        if chr(bval[i]) != "d":
            raise ValueError(f"invalid bencode dictionaries format: missing 'e'\nat index: {i}")
        
        i += 1 # skipping 'd'

        while i < len(bval) and chr(bval[i]) != "e":
            key,i = bencode_decoder.parse_by_type(bval,i)
            value,i = bencode_decoder.parse_by_type(bval,i)
            bencode_dictionaries_value[key] = value
        
        end_index = i + 1

        return bencode_dictionaries_value, end_index


    @staticmethod
    def parse_by_type(bval, i) -> tuple:
        # Parse the data based on its type
        if chr(bval[i]).isdigit():
            return bencode_decoder.string_decoder(bval, i)
        elif chr(bval[i]) == "i":
            return bencode_decoder.integer_decoder(bval, i)
        else:
            raise ValueError(f"Invalid bencode format at index: {i}")

print(bencode_decoder.dictionaries_decoder(b"d4:datai55ee",0))
