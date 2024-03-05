class BufferUtils:
    s_hexDigits = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F']

    @staticmethod
    #This method converts binary data to hexadecimal representation
    def convert_to_hex(buf, offset, length, chunks, show_ascii, callback):
        cursor = 0
        while cursor < length:
            sb = []
            sb.append("0x%04x: " % cursor)
            BufferUtils.convert_to_hex_helper(sb, buf, offset + cursor, min(chunks, length - cursor), chunks, True, show_ascii)
            callback(''.join(sb))
            cursor += chunks

    @staticmethod
    
     #This is a helper method used by convert_to_hex(). It builds the hexadecimal representation of the binary data in chunks.
    
    def convert_to_hex_helper(sb, buf, offset, length, pad_to_length, add_space_between_digits, show_ascii):
        num_digits = max(length, pad_to_length)
        for i in range(num_digits):
            if add_space_between_digits and i > 0:
                sb.append(' ')
            if i < length:
                b = buf[offset + i]
                sb.append(BufferUtils.to_hex(b >> 4))
                sb.append(BufferUtils.to_hex(b))
            else:
                sb.append(' ')
                sb.append(' ')
        if show_ascii:
            sb.append(" - ")
            for i in range(length):
                c = chr(buf[offset + i])
                sb.append(c if (c < 32 or c > 127) else '.')
    
    @staticmethod
    #This method converts hexadecimal text to binary data.
    def convert_from_hex(text):
        result = bytearray()
        for i in range(0, len(text), 2):
            part_high = BufferUtils.from_hex(text[i])
            part_low = BufferUtils.from_hex(text[i + 1])
            if part_high < 0 or part_low < 0:
                break
            result.append((part_high << 4) | part_low)
        return bytes(result)

    @staticmethod
    #This method converts 16-bit hexadecimal text to an integer.
    def convert_from_hex16(text, offset):
        part_high = 0xFF & BufferUtils.convert_from_hex(text, offset)
        part_low = 0xFF & BufferUtils.convert_from_hex(text, offset + 2)
        return (part_high << 8) | part_low

    @staticmethod
    #This method converts 32-bit hexadecimal text to a 32-bit integer.
    def convert_from_hex32(text, offset):
        part_high = 0xFFFF & BufferUtils.convert_from_hex16(text, offset)
        part_low = 0xFFFF & BufferUtils.convert_from_hex16(text, offset + 4)
        return (part_high << 16) | part_low

    @staticmethod
    #This method converts 64-bit hexadecimal text to a 64-bit integer.
    def convert_from_hex64(text, offset):
        part_high = 0xFFFFFFFF & BufferUtils.convert_from_hex32(text, offset)
        part_low = 0xFFFFFFFF & BufferUtils.convert_from_hex32(text, offset + 8)
        return (part_high << 32) | part_low

    @staticmethod
    #This static method converts a byte (b) to its hexadecimal representation
    def to_hex(b):
        return BufferUtils.s_hexDigits[b & 0xF]

    @staticmethod
    # This static method converts a hexadecimal character (c) to its integer value
    def from_hex(c):
        if '0' <= c <= '9':
            return ord(c) - ord('0')
        if 'a' <= c <= 'f':
            return ord(c) - ord('a') + 10
        if 'A' <= c <= 'F':
            return ord(c) - ord('A') + 10
        return -1
