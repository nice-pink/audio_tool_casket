import unittest
import py_project
from py_project.example import Example

class PyProjectTests(unittest.TestCase):

    # Versions

    def test_init(self):
        Example()