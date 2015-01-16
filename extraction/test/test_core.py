import unittest
from extraction.core import ExtractionRunner

class TestExtractionRunner(unittest.TestCase):
   def setUp(self):
      pass

   def test_create(self):
      runner = ExtractionRunner()
      self.assertFalse(runner is None)

