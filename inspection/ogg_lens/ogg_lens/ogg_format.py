from enum import Enum
from numpy import int64
import numpy as np
from typing import Optional

class PageHeader:
    HEADER_SIZE: int = 28
    MAGIC_STRUCTURE: bytearray = bytes.fromhex('4f67675300') # OggS0
    page_size: int = 0
    offset: int = 0
    is_fresh: bool = False
    is_bos: bool = False
    is_eos: bool = False
    absolute_pos: int64 = 0
    stream_serial: int = 0
    page_num: int = 0
    checksum: bytearray = bytes.fromhex('00000000')
    segments: int = 0
    segment_size_table: [int]

    
    def print_me(self):
        print('\033[0m----------')
        
        print(self.format_string(is_printing=True))

    def format_string(self, is_printing: bool = False):
        string = ''
        # if self.sample_rate == compare.sample_rate and self.version == compare.version:
        string += '----------\n'
        # else:
        #     string += '---------- Error\n'

        string += 'offset:      {0}\n'.format(self.offset)
        string += 'size:        {0}\n'.format(self.page_size)
        string += 'fresh:       {0}\n'.format(self.is_fresh)
        string += 'bos:         {0}\n'.format(self.is_bos)
        string += 'eos:         {0}\n'.format(self.is_eos)
        string += 'pos:         {0}\n'.format(self.absolute_pos)
        string += 'serial:      {0}\n'.format(self.stream_serial)
        string += 'page:        {0}\n'.format(self.page_num)
        string += 'chsum:       {0}\n'.format(self.checksum)
        string += 'segments:    {0} ['.format(self.segments)
        for i in range(len(self.segment_size_table)):
            string += '{0}, '.format(self.segment_size_table[i])
        string += ']\n'
        return string

# Parsers

class OggFormat:
    # https://xiph.org/ogg/doc/framing.html
    # 32 bit magic structure: OggS
    # 8 bit version: 0x00
    # 8 bit header type flag
    # 64 bit absolute granule position
    # 32 bit stream serial number
    # 32 bit page sequence number
    # 32 bit page checksum
    # 8 bit segments in page (0-255)
    # X bit segment table (n = page_segments)

    @staticmethod
    def get_all_headers(data: bytearray):
        headers = []
        offset = 0
        while offset < len(data) - PageHeader.HEADER_SIZE:
            if OggFormat.is_magic_structure(data, offset):
                header = OggFormat.get_header(data, offset)
                if header:
                    headers.append(header)
                offset += header.page_size - 1
                continue
            offset += 1
        return headers

    @staticmethod
    def get_page_size(header: PageHeader) -> int:
        page_size = PageHeader.HEADER_SIZE - 1 + len(header.segment_size_table)

        for i in range(len(header.segment_size_table)):
            page_size += header.segment_size_table[i]

        return page_size

    @staticmethod
    def get_header(data: bytearray, offset: int = 0) -> Optional[PageHeader]:
        if len(data) - offset < PageHeader.HEADER_SIZE:
            return None

        header = PageHeader()
        header.offset = offset
        header.is_fresh = OggFormat.get_is_fresh(data, offset)
        header.is_bos = OggFormat.get_is_bos(data, offset)
        header.is_eos = OggFormat.get_is_eos(data, offset)
        header.is_pos = OggFormat.get_absolute_position(data, offset)
        header.stream_serial = OggFormat.get_serial(data, offset)
        header.page_num = OggFormat.get_page_num(data, offset)
        header.checksum = OggFormat.get_checksum(data, offset)
        header.segments = OggFormat.get_segments(data, offset)
        header.segment_size_table = OggFormat.get_segments_table(data, header.segments, offset)
        header.page_size = OggFormat.get_page_size(header)
        
        return header

    @staticmethod
    def is_magic_structure(data: bytearray, offset: int = 0) -> bool:
        return data[offset:offset+5] == PageHeader.MAGIC_STRUCTURE

    @staticmethod
    def get_is_fresh(data: bytearray, offset: int = 0) -> bool: # offset = page offset
        fresh = data[offset+5]
        return (fresh & 0x01) == 0x01
    
    @staticmethod
    def get_is_bos(data: bytearray, offset: int = 0) -> bool: # offset = page offset
        fresh = data[offset+5]
        return (fresh & 0x02) == 0x02
    
    @staticmethod
    def get_is_eos(data: bytearray, offset: int = 0) -> bool: # offset = page offset
        fresh = data[offset+5]
        return (fresh & 0x04) == 0x04
    
    @staticmethod
    def get_absolute_position(data: bytearray, offset: int = 0) -> int64:
        return np.frombuffer(data, int64, count=8, offset=offset+6)
    
    @staticmethod
    def get_serial(data: bytearray, offset: int = 0) -> int:
        data_offset = offset + 14
        return int.from_bytes(data[data_offset:data_offset+4], byteorder='little', signed=False)

    @staticmethod
    def get_page_num(data: bytearray, offset: int = 0) -> int:
        data_offset = offset + 18
        return int.from_bytes(data[data_offset:data_offset+4], byteorder='little', signed=False)

    @staticmethod
    def get_checksum(data: bytearray, offset: int = 0) -> bytearray:
        data_offset = offset + 22
        return data[data_offset:data_offset+4]

    @staticmethod
    def get_segments(data: bytearray, offset: int = 0) -> int:
        data_offset = offset + PageHeader.HEADER_SIZE - 2
        return data[data_offset]

    @staticmethod
    def get_segments_table(data: bytearray, segments: int, offset: int = 0) -> int:
        table = []
        table_offset = offset + PageHeader.HEADER_SIZE - 1
        for i in range (0, segments):
            table.append(data[table_offset+i])
        
        return table

    @staticmethod
    def get_first_segment_offset(header: PageHeader):
        return header.offset + PageHeader.HEADER_SIZE