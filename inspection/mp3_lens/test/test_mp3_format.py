import unittest
import mp3_lens
from mp3_lens.mp3_format import Mp3Format, MpegVersion, MpegLayer

class Mp3FormatTests(unittest.TestCase):

    # Versions

    def test_get_mpeg_version_v1(self):
        data = bytes.fromhex('80B8FF24')
        result = Mp3Format.get_mpeg_version(data, 0)
        self.assertEqual(result, MpegVersion.V1)

    def test_get_mpeg_version_v2(self):
        data = bytes.fromhex('80B0FF24')
        result = Mp3Format.get_mpeg_version(data, 0)
        self.assertEqual(result, MpegVersion.V2)

    def test_get_mpeg_version_v2_5(self):
        data = bytes.fromhex('80A0FF24')
        result = Mp3Format.get_mpeg_version(data, 0)
        self.assertEqual(result, MpegVersion.V2_5)

    def test_get_mpeg_version_invalid(self):
        data = bytes.fromhex('80A8FF24')
        result = Mp3Format.get_mpeg_version(data, 0)
        self.assertEqual(result, MpegVersion.INVALID)

    # Layer

    def test_get_layer_version_l1(self):
        data = bytes.fromhex('80A6FF24')
        result = Mp3Format.get_layer_version(data, 0)
        self.assertEqual(result, MpegLayer.L1)

    def test_get_layer_version_l2(self):
        data = bytes.fromhex('80A4FF24')
        result = Mp3Format.get_layer_version(data, 0)
        self.assertEqual(result, MpegLayer.L2)

    def test_get_layer_version_l3(self):
        data = bytes.fromhex('80A2FF24')
        result = Mp3Format.get_layer_version(data, 0)
        self.assertEqual(result, MpegLayer.L3)

    def test_get_layer_version_invalid(self):
        data = bytes.fromhex('80A0FF24')
        result = Mp3Format.get_layer_version(data, 0)
        self.assertEqual(result, MpegLayer.INVALID)

    # Bitrate

    def test_get_bitrate_v2_l3_160k(self):
        data = bytes.fromhex('8012E542')
        result = Mp3Format.get_bitrate(data, 0)
        self.assertEqual(result, 160000)
    
    def test_get_bitrate_v1_l3_320k(self):
        data = bytes.fromhex('801AE542')
        result = Mp3Format.get_bitrate(data, 0)
        self.assertEqual(result, 320000)

    # Sample rate

    def test_get_sample_rate_v1_48k(self):
        data = bytes.fromhex('22185449')
        result = Mp3Format.get_sample_rate(data, 0)
        self.assertEqual(result, 48000)

    def test_get_sample_rate_v2_16k(self):
        data = bytes.fromhex('22105849')
        result = Mp3Format.get_sample_rate(data, 0)
        self.assertEqual(result, 16000)

    # Sync header

    def test_is_sync_header_fail(self):
        data = bytes.fromhex('22185449')
        result = Mp3Format.is_sync_header(data, 0)
        self.assertEqual(result, False)

    def test_is_sync_header_success_1(self):
        data = bytes.fromhex('FFFE')
        result = Mp3Format.is_sync_header(data, 0)
        self.assertEqual(result, True)

    def test_is_sync_header_success_2(self):
        data = bytes.fromhex('FFEE')
        result = Mp3Format.is_sync_header(data, 0)
        self.assertEqual(result, True)

if __name__ == '__main__':
    unittest.main()