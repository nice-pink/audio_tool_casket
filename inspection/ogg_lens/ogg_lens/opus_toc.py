from enum import Enum

# Toc

class CodecMode(Enum):
    SILK = 0
    HYBRID = 1
    CELT = 2

class Bandwidth(Enum):
    NARROW_BAND = 0
    MID_BAND = 1
    WIDE_BAND = 2
    SUPER_WIDE_BAND = 3
    FULL_BAND = 4

class PacketToc:
    # https://tools.ietf.org/html/rfc6716#section-3.1
    # 5 bit config
    # 1 bit stereo flag
    # 2 bit channel count
    mode: CodecMode
    bandwidth: Bandwidth
    duration: float # [ms]
    channels: int
    is_stereo: bool

    def __init__(self, toc_byte: int):
        self.set_channels(toc_byte)
        self.set_is_stereo(toc_byte)
        self.set_mode(toc_byte)
        self.set_duration_and_bandwidth(toc_byte)

    def set_channels(self, toc_byte: int):
        self.channels = toc_byte & 0xFC

    def set_is_stereo(self, toc_byte: int):
        self.is_stereo = (toc_byte >> 1) & 0xFE

    # mode specific

    def set_mode(self, toc_byte: int):
        config = toc_byte >> 3
        if config < 12:
            self.mode = CodecMode.SILK
        elif config < 16:
            self.mode = CodecMode.HYBRID
        else:
            self.mode = CodecMode.CELT

    def set_duration_and_bandwidth(self, toc_byte: int):
        if self.mode == CodecMode.SILK:
            self.set_duration_silk(toc_byte)
            self.set_bandwidth_silk(toc_byte)
        elif self.mode == CodecMode.HYBRID:
            self.set_duration_hybrid(toc_byte)
            self.set_bandwidth_hybrid(toc_byte)
        else:
            self.set_duration_celt(toc_byte)
            self.set_bandwidth_celt(toc_byte)

    # silk

    def set_duration_silk(self, toc_byte: int):
        if toc_byte % 4 == 0:
            self.duration = 10
        elif toc_byte == 1 or toc_byte == 5 or toc_byte == 9:
            self.duration = 20
        elif toc_byte % 2 == 0:
            self.duration = 40
        else:
            self.duration = 60

    def set_bandwidth_silk(self, toc_byte: int):
        if toc_byte < 4:
            self.bandwidth = Bandwidth.NARROW_BAND
        elif toc_byte < 8:
            self.bandwidth = Bandwidth.MID_BAND
        else:
            self.bandwidth = Bandwidth.WIDE_BAND

    # hybrid

    def set_duration_hybrid(self, toc_byte: int):
        if toc_byte == 12 or toc_byte == 14:
            self.duration = 10
        else:
            self.duration = 20

    def set_bandwidth_hybrid(self, toc_byte: int):
        if toc_byte < 14:
            self.bandwidth = Bandwidth.SUPER_WIDE_BAND
        else:
            self.bandwidth = Bandwidth.FULL_BAND

    # celt

    def set_duration_celt(self, toc_byte: int):
        if toc_byte % 4 == 0:
            self.duration = 2.5
        elif toc_byte == 21 or toc_byte == 25 or toc_byte == 29:
            self.duration = 5
        elif toc_byte % 2 == 0:
            self.duration = 10
        else:
            self.duration = 20

    def set_bandwidth_celt(self, toc_byte: int):
        if toc_byte < 20:
            self.bandwidth = Bandwidth.NARROW_BAND
        elif toc_byte < 24:
            self.bandwidth = Bandwidth.WIDE_BAND
        elif toc_byte < 28:
            self.bandwidth = Bandwidth.SUPER_WIDE_BAND
        else:
            self.bandwidth = Bandwidth.FULL_BAND

    # helper

    def print_me(self):
        print('\033[0m----------')
        
        print(self.format_string(is_printing=True))

    def format_string(self, is_printing: bool = False):
        string = ''
        if not is_printing:
            string += '----------\n'
        
        string += 'mode:        {0}\n'.format(self.mode)
        string += 'band:        {0}\n'.format(self.bandwidth)
        string += 'duration:    {0}\n'.format(self.duration)
        string += 'channels:    {0}\n'.format(self.channels)
        string += 'stereo:      {0}\n'.format(self.is_stereo)
        return string