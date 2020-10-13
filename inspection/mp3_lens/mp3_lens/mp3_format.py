from enum import Enum

class MpegVersion(Enum):
    INVALID = 'Invalid'
    V1 = 'V1'
    V2 = 'V2'
    V2_5 = 'V3'

class MpegLayer(Enum):
    INVALID = 'Invalid'
    L1 = 'L1'
    L2 = 'L2'
    L3 = 'L3'

class ChannelMode(Enum):
    STEREO = 'Stereo'
    JOINT_STEREO = 'Joint'
    DUAL_CHANNEL = 'Dual'
    MONO = 'Mono'

class MpegHeader:
    frame_size: int = 0
    version: MpegVersion = MpegVersion.INVALID
    layer: MpegLayer = MpegLayer.INVALID
    bitrate: int = 0
    sample_rate: int = 0
    channel_mode: ChannelMode = ChannelMode.STEREO
    offset: int = 0 # offset in file

    def print_me(self, compare):
        if self.sample_rate == compare.sample_rate and self.version == compare.version and self.layer == compare.layer:
            print('\033[0m----------')
        else:
            print('\033[1;31m----------')

        print('offset:      ', self.offset)
        print('frame size:  ', self.frame_size)
        print('version:     ', self.version)
        print('layer:       ', self.layer)
        print('bitrate:     ', self.bitrate)
        print('sample rate: ', self.sample_rate)

    def format_string(self, compare):
        string = ''
        if self.sample_rate == compare.sample_rate and self.version == compare.version and self.layer == compare.layer:
            string += '----------\n'
        else:
            string += '---------- Error ({0}-{1}, {2}-{3}, {4}-{5})\n'.format(str(self.sample_rate), str(compare.sample_rate), str(self.version), str(compare.version), str(self.layer), str(compare.layer))

        string += 'offset:      {0}\n'.format(self.offset)
        string += 'frame size:  {0}\n'.format(self.frame_size)
        string += 'version:     {0}\n'.format(self.version)
        string += 'layer:       {0}\n'.format(self.layer)
        string += 'bitrate:     {0}\n'.format(self.bitrate)
        string += 'sample rate: {0}\n'.format(self.sample_rate)
        return string

# Parsers

class Mp3Format:

    @staticmethod
    def get_mpeg_version(data: bytearray, offset: int = 0) -> MpegVersion:
        byte = data[offset + 1]
        shifted = byte >> 3
        mask = bytes.fromhex('03')

        # Return matched value
        if shifted & mask[0] == 0:
            return MpegVersion.V2_5
        if shifted & mask[0] == 2:
            return MpegVersion.V2
        if shifted & mask[0] == 3:
            return MpegVersion.V1
        
        return MpegVersion.INVALID

    @staticmethod
    def get_layer_version(data: bytearray, offset: int = 0) -> MpegLayer:
        byte = data[offset + 1]
        shifted = byte >> 1
        mask = bytes.fromhex('03')

        # Return matched value
        if shifted & mask[0] == 1:
            return MpegLayer.L3
        if shifted & mask[0] == 2:
            return MpegLayer.L2
        if shifted & mask[0] == 3:
            return MpegLayer.L1
        
        return MpegLayer.INVALID

    @staticmethod
    def get_bitrate(data: bytearray, offset: int = 0) -> int:
        version = Mp3Format.get_mpeg_version(data, offset)
        layer = Mp3Format.get_layer_version(data, offset)
        index = Mp3Format.get_bitrate_index(data, offset)

        # Fetch value from arrays
        bitrate = 0
        if version == MpegVersion.V1 and layer == MpegLayer.L1:
            bitrate = Mp3Format.BITRATE_V1_L1[index]
        elif version == MpegVersion.V1 and layer == MpegLayer.L2:
            bitrate = Mp3Format.BITRATE_V1_L2[index]
        elif version == MpegVersion.V1 and layer == MpegLayer.L3:
            bitrate = Mp3Format.BITRATE_V1_L3[index]
        elif (version == MpegVersion.V2 or version == MpegVersion.V2_5) and layer == MpegLayer.L1:
            bitrate = Mp3Format.BITRATE_V2_L1[index]
        elif (version == MpegVersion.V2 or version == MpegVersion.V2_5) and (layer == MpegLayer.L2 or layer == MpegLayer.L3):
            bitrate = Mp3Format.BITRATE_V2_L2_3[index]
        else:
            return -1
        
        return bitrate * 1000

    @staticmethod
    def get_bitrate_index(data: bytearray, offset: int = 0) -> int:
        byte = data[offset + 2]
        shifted = byte >> 4
        mask = bytes.fromhex('0F')
        value = shifted & mask[0]
        return value

    @staticmethod
    def get_sample_rate(data: bytearray, offset: int = 0) -> int:
        version = Mp3Format.get_mpeg_version(data, offset)
        
        byte = data[offset + 2]
        shifted = byte >> 2
        mask = bytes.fromhex('03')
        value = shifted & mask[0]

        index = value

        if version == MpegVersion.V1:
            return Mp3Format.SAMPLE_RATE_V1[index]
        if version == MpegVersion.V2:
            return Mp3Format.SAMPLE_RATE_V2[index]
        if version == MpegVersion.V2_5:
            return Mp3Format.SAMPLE_RATE_V2_5[index]
        
        return -1

    @staticmethod
    def get_frame_size(data: bytearray, offset: int = 0) -> int:
        bitrate = Mp3Format.get_bitrate(data, offset)
        sample_rate = Mp3Format.get_sample_rate(data, offset)
        
        return int(144 * bitrate / (sample_rate + 8))

    @staticmethod
    def is_sync_header(data: bytearray, offset: int = 0) -> bool:
        mask = bytes.fromhex('FFE0')

        index = offset
        for bitmask in mask:
            value = data[index] & bitmask
            index += 1
            if value != bitmask:
                return False

        return True

    @staticmethod
    def is_xing_frame(data: bytearray, offset: int = 0) -> bool:
        mask = bytes.fromhex('58696E67')

        index = offset + 36
        for bitmask in mask:
            value = data[index] & bitmask
            index += 1
            if value != bitmask:
                return False

        return True

    @staticmethod
    def is_info_frame(data: bytearray, offset: int = 0) -> bool:
        mask = bytes.fromhex('496E666F')

        index = offset + 36
        for bitmask in mask:
            value = data[index] & bitmask
            index += 1
            if value != bitmask:
                return False

        return True

    @staticmethod
    def get_lame_tag(data: bytearray, offset: int = 0) -> None:
        lame_tag = ""
        for i in range(39, 177):
            lame_tag += str(data[offset + i])

    @staticmethod
    def get_mpeg_header(data: bytearray, offset: int = 0) -> MpegHeader:
        header = MpegHeader()
        header.version = Mp3Format.get_mpeg_version(data, offset)
        header.layer = Mp3Format.get_layer_version(data, offset)
        header.bitrate = Mp3Format.get_bitrate(data, offset)
        header.sample_rate = Mp3Format.get_sample_rate(data, offset)
        header.frame_size = Mp3Format.get_frame_size(data, offset)
        header.offset = offset
        return header

    # Sample rates

    SAMPLE_RATE_V1 = [44100, 48000, 32000, -1]
    SAMPLE_RATE_V2 = [22050, 24000, 16000, -1]
    SAMPLE_RATE_V2_5 = [11025, 12000, 8000, -1]

    # Bitrates

    BITRATE_V1_L1 = [0, 32, 64, 96, 128, 160, 192, 224, 256, 288, 320, 352, 384, 416, 448, -1]
    BITRATE_V1_L2 = [0, 32, 48, 56, 64, 80, 96, 112, 128, 160, 192, 224, 256, 320, 384, -1]
    BITRATE_V1_L3 = [0, 32, 40, 48, 56, 64, 80, 96, 112, 128, 160, 192, 224, 256, 320, -1]
    BITRATE_V2_L1 = [0, 32, 48, 56, 64, 80, 96, 112, 128, 144, 160, 176, 192, 224, 256, -1]
    BITRATE_V2_L2_3 = [0,  8,  16,  24,  32,  40,  48,  56,  64,  80,  96,  112,  128,  144,  160,  -1]