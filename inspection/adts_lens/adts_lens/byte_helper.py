class ByteHelper:

    @staticmethod
    def get_int_from_bytes(data: int, relevant_bit_count: int, bit_shift: int = 0):
        shifted_data = data >> bit_shift

        mask = 0
        for i in range(0, relevant_bit_count):
            mask |= (1 << i)

        return shifted_data & mask