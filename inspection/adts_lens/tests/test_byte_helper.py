import unittest
import adts_lens
from adts_lens.byte_helper import ByteHelper

class ByteHelperTests(unittest.TestCase):

    # Versions

    def test_value(self):
        data = 1
        value = ByteHelper.get_int_from_bytes(data, 1)
        self.assertEqual(value, 1)

    def test_value_more_bits(self):
        data = 1
        value = ByteHelper.get_int_from_bytes(data, 4)
        self.assertEqual(value, 1)

    def test_value_fail(self):
        data = 1
        value = ByteHelper.get_int_from_bytes(data, 1)
        self.assertNotEqual(value, 2)

    def test_value_shifted(self):
        data = 2
        value = ByteHelper.get_int_from_bytes(data, 2, 1)
        self.assertEqual(value, 1)

    def test_value_shifted_failed(self):
        data = 6
        value = ByteHelper.get_int_from_bytes(data, 2, 1)
        self.assertEqual(value, 3)
    
    def test_value_shifted_failed(self):
        data = 128
        value = ByteHelper.get_int_from_bytes(data, 1, 7)
        self.assertEqual(value, 1)

    