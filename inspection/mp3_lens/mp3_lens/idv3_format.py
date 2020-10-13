class TagRange:

    def __init__(self, offset: int, size: int):
        self.offset = offset
        self.size = size

class IdV3TagFormat:

    HEADER_SIZE = 10
    FOOTER_SIZE = 10

    @staticmethod
    def get_id_v3_tag_range(data: bytearray) -> TagRange:
        data_size = len(data)

        offset = 0
        while not IdV3TagFormat.is_id_v3_tag(data, offset):
            offset += 1

            if offset >= data_size - 1:
                print('No tag', offset)
                return TagRange(-1, -1)

        b_size = data[offset + 7 : offset + 10]
        
        tag_size = IdV3TagFormat.unsyncsave(b_size) + IdV3TagFormat.HEADER_SIZE

        if IdV3TagFormat.has_footer(data, offset):
            tag_size += IdV3TagFormat.FOOTER_SIZE

        return TagRange(offset, tag_size)

    @staticmethod
    def has_footer(data: bytearray, offset: int = 0) -> bool:
        mask = bytes.fromhex('10')

        if data[offset + 5] != mask[0]:
            return False

        return True

    @staticmethod
    def is_id_v3_tag(data: bytearray, offset: int = 0) -> bool:
        # 49 44 33 yy yy xx zz zz zz zz
        # yy < FF
        # xx -> flags
        # zz < 80
        
        mask = bytes.fromhex('494433')

        index = offset
        for bitmask in mask:
            if data[index] != bitmask:
                return False
            index += 1
            
        # yy < FF
        yy = bytes.fromhex('FFFF')
        for bitmask in yy:
            if data[index] >= bitmask:
                return False
            index += 1

        # don't care about flags
        index += 1

        # zz < 80
        zz = bytes.fromhex('80808080')
        for bitmask in zz:
            if data[index] >= bitmask:
                return False
            index += 1

        return True

    @staticmethod
    def unsyncsave(b_size: bytes) -> int:
        mask = bytes.fromhex('7F000000')
        i_mask = int.from_bytes(mask, 'big')

        out = 0
        i_size = int.from_bytes(b_size, 'big')
        
        while i_mask:
            out >>= 1
            out |= i_size & i_mask
            i_mask >>= 8
            
        return out