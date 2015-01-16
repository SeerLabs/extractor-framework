import unittest
import extraction.runnables as runnables
import extraction.test.filters as filters
import extraction.test.extractors as extractors
import extraction.xmltodict as xmltodict


class TestRunnables(unittest.TestCase):
   def setUp(self):
      pass

   def test_defining_dependencies(self):
      self.assertTrue(hasattr(filters.FilterWithoutDeps, 'dependencies'))
      self.assertEqual(len(filters.FilterWithoutDeps.dependencies()), 0)
      self.assertEqual(len(filters.FilterWithDeps.dependencies()), 1)
      self.assertTrue(filters.FilterWithoutDeps in filters.FilterWithDeps.dependencies())

   def test_filter_method_gets_run(self):
      self.assertTrue(filters.TrueFilter().run("some_data", {}))
      self.assertFalse(filters.FalseFilter().run("some_data", {}))

   def test_extractor_wrap_xml_content(self):
      extractor = extractors.NothingExtractor()
      xml_string = extractor._wrap_xml_content('<tag></tag>')
      dict = xmltodict.parse(xml_string)
      self.assertTrue('extractor' in dict)
      self.assertTrue('@type' in dict['extractor'])
      self.assertEqual(dict['extractor']['@type'], 'NothingExtractor')

   def test_extractor_xml_string_from_error(self):
      extractor = extractors.NothingExtractor()
      xml_string = extractor._xml_string_from_error("Test")
      # using xmltodict is a good way to check that xml is a simple valid format
      # and has the fields we expect regardless of whitespace
      dict = xmltodict.parse(xml_string)
      self.assertTrue('error' in dict['extractor'])
      self.assertEqual(dict['extractor']['error'], 'Test')
