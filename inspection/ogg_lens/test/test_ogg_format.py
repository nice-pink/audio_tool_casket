import unittest
import ogg_lens
from ogg_lens.ogg_format import OggFormat, PageHeader

class OggFormatTests(unittest.TestCase):

    # Sync header

    def test_is_magic_structure_fail(self):
        data = bytes.fromhex('2218544009')
        result = OggFormat.is_magic_structure(data, 0)
        self.assertEqual(result, False)

    def test_is_magic_structure_ok_1(self):
        data = bytes.fromhex('4f67675300')
        result = OggFormat.is_magic_structure(data, 0)
        self.assertEqual(result, True)

    def test_is_magic_structure_ok_2(self):
        data = bytes.fromhex('4f676753001122')
        result = OggFormat.is_magic_structure(data, 0)
        self.assertEqual(result, True)

if __name__ == '__main__':
    unittest.main()