from enum import Enum
from typing import Optional
from ogg_lens.opus_toc import PacketToc

class PacketHeader:
    # https://tools.ietf.org/html/rfc7845#section-5.1
    # 8 bit version: 1
    # 8 bit channel count:
    # 16 bit pre-skip:
    # 32 bit input sample rate:
    # 16 bit output gain:
    # 8 bit mapping family: 
    MAGIC_STRUCTURE: bytearray = bytes.fromhex('4F70757348656164') # OpusHead
    MAGIC_STRUCTURE_TAGS: bytearray = bytes.fromhex('4F70757354616773') # OpusTags
    HEADER_SIZE: int = 19
    version: int = 1
    channels: int = 0
    sample_rate: int = 0
    gain: int = 0
    pre_skip: int = 0
    mapping_family: int = 0
    toc: PacketToc
    offset: int = 0 # offset in file

    def print_me(self):
        # if self.sample_rate == compare.sample_rate and self.version == compare.version:
        print('\033[0m----------')
        # else:
        #     print('\033[1;31m----------')

        print(self.format_string(is_printing=True))

    def format_string(self, is_printing: bool = False):
        string = ''
        if not is_printing:
            string += '----------\n'

        string += self.get_codec_name() + '\n'
        string += 'offset:      {0}\n'.format(self.offset)
        string += 'version:     {0}\n'.format(self.version)
        string += 'sample rate: {0}\n'.format(self.sample_rate)
        string += 'channels:    {0}\n'.format(self.channels)
        string += 'gain:        {0}\n'.format(self.gain)
        string += 'pre-skip:    {0}\n'.format(self.pre_skip)
        string += 'mapping:     {0}\n'.format(self.mapping_family)
        return string

    def get_codec_name(self):
        return 'Opus'

# Parsers

class OpusFormat:
    # https://tools.ietf.org/html/rfc7845
    # 64 bit magic structure: OpusHead
    # 8 bit version: 1
    # 8 bit channel count:
    # 16 bit pre-skip:
    # 32 bit input sample rate:
    # 16 bit output gain:
    # 8 bit mapping family: 
    # X bit optional channel mapping table

    @staticmethod
    def get_all_headers(data: bytearray):
        
        headers = []
        offset = 0
        while offset < len(data) - PacketHeader.HEADER_SIZE:
            if OpusFormat.is_magic_structure(data, offset):
                header = OpusFormat.get_header(data, offset)
                if header:
                    headers.append(header)
                offset += PacketHeader.HEADER_SIZE
                continue
            offset += 1
        return headers

    @staticmethod
    def get_header(data: bytearray, offset: int = 0) -> Optional[PacketHeader]:
        if len(data) - offset < 19:
            return None

        header = PacketHeader()
        header.offset = offset
        header.version = OpusFormat.get_version(data, offset)
        header.channels = OpusFormat.get_channels(data, offset)
        header.pre_skip = OpusFormat.get_pre_skip(data, offset)
        header.sample_rate = OpusFormat.get_sample_rate(data, offset)
        header.gain = OpusFormat.get_gain(data, offset)
        header.mapping_family = OpusFormat.get_mapping_family(data, offset)
        header.toc = PacketToc(data[offset])
        
        return header

    @staticmethod
    def get_packet_toc(data: bytearray, offset: int = 0) -> Optional[PacketToc]:
        mode_mask = data[offset] >> 3

    @staticmethod
    def is_magic_structure(data: bytearray, offset: int = 0) -> bool:
        return data[offset:offset+8] == PacketHeader.MAGIC_STRUCTURE

    @staticmethod
    def is_magic_structure_tags(data: bytearray, offset: int = 0) -> bool:
        return data[offset:offset+8] == PacketHeader.MAGIC_STRUCTURE_TAGS

    @staticmethod
    def get_version(data: bytearray, offset: int = 0) -> int: # offset = page offset
        data_offset = offset + 8
        return data[data_offset]
    
    @staticmethod
    def get_channels(data: bytearray, offset: int = 0) -> int:
        data_offset = offset + 9
        return data[data_offset]
    
    @staticmethod
    def get_pre_skip(data: bytearray, offset: int = 0) -> int:
        data_offset = offset + 10
        return int.from_bytes(data[data_offset:data_offset+2], byteorder='little', signed=False)

    @staticmethod
    def get_sample_rate(data: bytearray, offset: int = 0) -> int:
        data_offset = offset + 12
        return int.from_bytes(data[data_offset:data_offset+4], byteorder='little', signed=False)

    @staticmethod
    def get_gain(data: bytearray, offset: int = 0) -> int:
        data_offset = offset + 16
        return int.from_bytes(data[data_offset:data_offset+2], byteorder='little', signed=False)

    @staticmethod
    def get_mapping_family(data: bytearray, offset: int = 0) -> int:
        data_offset = offset + 18
        return data[data_offset]
