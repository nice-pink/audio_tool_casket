from enum import Enum
from typing import Optional
from adts_lens.adts_field_helper import AdtsFieldHelper
from adts_lens.byte_helper import ByteHelper

class FrameHeader:
    # https://wiki.multimedia.cx/index.php/ADTS
    # 8 bit version: 1
    # 8 bit channel count:
    # 16 bit pre-skip:
    # 32 bit input sample rate:
    # 16 bit output gain:
    # 8 bit mapping family: 
    MAGIC_STRUCTURE: bytearray = bytes.fromhex('FFF0')
    MAGIC_STRUCTURE_COMPARATOR: bytearray = bytes.fromhex('FFF6')
    MIN_HEADER_SIZE: int = 7 # if contains crc -> 9
    version: int = 1
    layer: int = 0
    protection_absent: bool = False
    profile_index: int = 0
    sampling_frequency_index: int = 0
    private_bit: int = 0
    channel_config_index: int = 0
    originality: int = 0
    home: int = 0
    copyright_id_bit: int = 0
    copyright_id_start: int = 0
    frame_size: int = 0 #  this value must include 7 or 9 bytes of header length: FrameLength = (ProtectionAbsent == 1 ? 7 : 9) + size(AACFrame)
    bufferfullness: int = 0
    aac_frame_count: int = 0 # -1 is the real amount
    crc: int = 0 # CRC if protection absent is 0

    # help values
    frame_size_data: int = 0
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

        string += 'ADTS Frames\n'
        string += 'offset:      {0}\n'.format(self.offset)
        string += 'profile:     {0}\n'.format(AdtsFieldHelper.get_profile_name(self.profile_index))
        string += 'version:     {0}\n'.format(self.version)
        string += 'layer:       {0}\n'.format(self.layer)
        string += 'frame size:  {0}\n'.format(self.frame_size)
        string += 'data size:   {0}\n'.format(self.frame_size_data)
        string += 'sample rate: {0}\n'.format(AdtsFieldHelper.get_sample_rate(self.sampling_frequency_index))
        string += 'channels:    {0}\n'.format(AdtsFieldHelper.get_channel_config(self.channel_config_index))
        string += 'aac frames:  {0}\n'.format(self.aac_frame_count)
        string += 'crc:         {0}\n'.format(self.crc)
        return string

# Parsers

class AdtsFormat:
    # https://wiki.multimedia.cx/index.php/ADTS
    #
    #     Structure
    # AAAAAAAA AAAABCCD EEFFFFGH HHIJKLMM MMMMMMMM MMMOOOOO OOOOOOPP (QQQQQQQQ QQQQQQQQ)
    #
    # Header consists of 7 or 9 bytes (without or with CRC).
    #
    # Letter	Length (bits)	Description
    # A	        12              syncword 0xFFF, all bits must be 1
    # B	        1	            MPEG Version: 0 for MPEG-4, 1 for MPEG-2
    # C	        2	            Layer: always 0
    # D	        1	            protection absent, Warning, set to 1 if there is no CRC and 0 if there is CRC
    # E	        2	            profile, the MPEG-4 Audio Object Type minus 1
    # F	        4	            MPEG-4 Sampling Frequency Index (15 is forbidden)
    # G	        1	            private bit, guaranteed never to be used by MPEG, set to 0 when encoding, ignore when decoding
    # H	        3	            MPEG-4 Channel Configuration (in the case of 0, the channel configuration is sent via an inband PCE)
    # I	        1	            originality, set to 0 when encoding, ignore when decoding
    # J	        1	            home, set to 0 when encoding, ignore when decoding
    # K	        1	            copyrighted id bit, the next bit of a centrally registered copyright identifier, set to 0 when encoding, ignore when decoding
    # L	        1	            copyright id start, signals that this frame's copyright id bit is the first bit of the copyright id, set to 0 when encoding, ignore when decoding
    # M	        13	            frame length, this value must include 7 or 9 bytes of header length: FrameLength = (ProtectionAbsent == 1 ? 7 : 9) + size(AACFrame)
    # O	        11          	Buffer fullness
    # P	        2           	Number of AAC frames (RDBs) in ADTS frame minus 1, for maximum compatibility always use 1 AAC frame per ADTS frame
    # Q	        16          	CRC if protection absent is 0

    @staticmethod
    def get_all_headers(data: bytearray):
        headers = []
        offset = 0
        while offset < len(data) - FrameHeader.MIN_HEADER_SIZE:
            if AdtsFormat.is_magic_structure(data, offset):
                header = AdtsFormat.get_header(data, offset)
                if header:
                    headers.append(header)
                offset += header.frame_size
                continue
            offset += 1
        return headers

    @staticmethod
    def get_header(data: bytearray, offset: int = 0) -> Optional[FrameHeader]:
        if len(data) - offset < 19:
            return None

        header = FrameHeader()
        header.offset = offset
        header.version = AdtsFormat.get_version(data, offset)
        header.layer = AdtsFormat.get_layer(data, offset)
        header.protection_absent = AdtsFormat.get_protection(data, offset)
        header.profile_index = AdtsFormat.get_profile_index(data, offset)
        header.sampling_frequency_index = AdtsFormat.get_sample_rate_index(data, offset)
        header.private_bit = AdtsFormat.get_private_bit(data, offset)
        header.channel_config_index = AdtsFormat.get_channel_config_index(data, offset)
        header.originality = AdtsFormat.get_originality_bit(data, offset)
        header.home = AdtsFormat.get_home_bit(data, offset)
        header.copyright_id_bit = AdtsFormat.get_copyright_id_bit(data, offset)
        header.copyright_id_start = AdtsFormat.get_copyright_id_start(data, offset)
        header.frame_size = AdtsFormat.get_frame_size(data, offset)
        header.bufferfullness = AdtsFormat.get_buffer_fullness(data, offset)
        header.aac_frame_count = AdtsFormat.get_aac_frames_count(data, offset)
        header.crc = AdtsFormat.get_crc(data, offset)
        
        return header

    @staticmethod
    def is_magic_structure(data: bytearray, offset: int = 0) -> bool:
        first = int.from_bytes(data[offset: offset + 2], 'big')
        comp = int.from_bytes(FrameHeader.MAGIC_STRUCTURE_COMPARATOR, 'big')
        magic = int.from_bytes(FrameHeader.MAGIC_STRUCTURE, 'big')
        # print('f', first, 'comp', comp, 'migic', magic)
        return (first & comp ) == magic

    @staticmethod
    def get_header_size(data: bytearray, offset: int = 0) -> bool:
        if AdtsFormat.get_protection(data, offset) == 0:
            return FrameHeader.MIN_HEADER_SIZE + 2
        return FrameHeader.MIN_HEADER_SIZE

    @staticmethod
    def get_frame_size_data(data: bytearray, offset: int = 0) -> bool:
        frame_size = AdtsFormat.get_frame_size(data, offset)
        header_size = AdtsFormat.get_header_size(data, offset)
        return frame_size - header_size

    @staticmethod
    def get_version(data: bytearray, offset: int = 0) -> int: # offset = frame offset
        data_offset = offset + 1
        value = ByteHelper.get_int_from_bytes(data[data_offset], 1, 3)
        return value
    
    @staticmethod
    def get_layer(data: bytearray, offset: int = 0) -> int: # offset = frame offset
        data_offset = offset + 1
        value = ByteHelper.get_int_from_bytes(data[data_offset], 2, 1)
        return value

    @staticmethod
    def get_protection(data: bytearray, offset: int = 0) -> int: # offset = frame offset
        data_offset = offset + 1
        value = ByteHelper.get_int_from_bytes(data[data_offset], 1)
        return value

    @staticmethod
    def get_profile_index(data: bytearray, offset: int = 0) -> int: # offset = frame offset
        data_offset = offset + 2
        value = ByteHelper.get_int_from_bytes(data[data_offset], 2, 6)
        return value

    @staticmethod
    def get_sample_rate_index(data: bytearray, offset: int = 0) -> int: # offset = frame offset
        data_offset = offset + 2
        value = ByteHelper.get_int_from_bytes(data[data_offset], 4, 2)
        return value

    @staticmethod
    def get_private_bit(data: bytearray, offset: int = 0) -> int: # offset = frame offset
        data_offset = offset + 2
        value = ByteHelper.get_int_from_bytes(data[data_offset], 1, 1)
        return value

    @staticmethod
    def get_channel_config_index(data: bytearray, offset: int = 0) -> int: # offset = frame offset
        data_offset = offset + 2
        value = ByteHelper.get_int_from_bytes(int.from_bytes(data[data_offset : data_offset + 2], 'big'), 3, 6)
        return value

    @staticmethod
    def get_originality_bit(data: bytearray, offset: int = 0) -> int: # offset = frame offset
        data_offset = offset + 3
        value = ByteHelper.get_int_from_bytes(data[data_offset], 1, 5)
        return value

    @staticmethod
    def get_home_bit(data: bytearray, offset: int = 0) -> int: # offset = frame offset
        data_offset = offset + 3
        value = ByteHelper.get_int_from_bytes(data[data_offset], 1, 4)
        return value

    @staticmethod
    def get_copyright_id_bit(data: bytearray, offset: int = 0) -> int: # offset = frame offset
        data_offset = offset + 3
        value = ByteHelper.get_int_from_bytes(data[data_offset], 1, 3)
        return value

    @staticmethod
    def get_copyright_id_start(data: bytearray, offset: int = 0) -> int: # offset = frame offset
        data_offset = offset + 3
        value = ByteHelper.get_int_from_bytes(data[data_offset], 1, 2)
        return value

    @staticmethod
    def get_frame_size(data: bytearray, offset: int = 0) -> int: # offset = frame offset
        data_offset = offset + 3
        value = ByteHelper.get_int_from_bytes(int.from_bytes(data[data_offset : data_offset + 3], 'big'), 13, 5)
        return value

    @staticmethod
    def get_buffer_fullness(data: bytearray, offset: int = 0) -> int: # offset = frame offset
        data_offset = offset + 5
        value = ByteHelper.get_int_from_bytes(int.from_bytes(data[data_offset : data_offset + 2], 'big'), 11, 2)
        return value

    @staticmethod
    def get_aac_frames_count(data: bytearray, offset: int = 0) -> int: # offset = frame offset
        data_offset = offset + 6
        value = ByteHelper.get_int_from_bytes(data[data_offset], 2)
        return value + 1

    @staticmethod
    def get_crc(data: bytearray, offset: int = 0) -> int: # offset = frame offset
        if AdtsFormat.get_protection(data, offset) == 1:
            return -1

        data_offset = offset + 7
        value = ByteHelper.get_int_from_bytes(int.from_bytes(data[data_offset : data_offset + 2], 'big'), 16)
        return value
