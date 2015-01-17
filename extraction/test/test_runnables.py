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
      pass

   def test_extractor_wrap_xml_content(self):
      extractor = extractors.NothingExtractor()
      xml_string = extractor._wrap_xml_content('<tag></tag>')
      dict_result = xmltodict.parse(xml_string)
      self.assertTrue('extractor' in dict_result)
      self.assertTrue('@type' in dict_result['extractor'])
      self.assertEqual(dict_result['extractor']['@type'], 'NothingExtractor')

   def test_extractor_error_xml(self):
      extractor = extractors.NothingExtractor()
      xml_string = extractor._error_xml("Test")
      # using xmltodict is a good way to check that xml is a simple valid format
      # and has the fields we expect regardless of whitespace
      dict_result = xmltodict.parse(xml_string)
      self.assertTrue('error' in dict_result['extractor'])
      self.assertEqual(dict_result['extractor']['error'], 'Test')

   def test_failing_filter_dep_means_extractor_doesnt_run(self):
      extractor = extractors.FailingDepsExtractor()
      filter = filters.FailFilter()
      filter_result = filter.run('nothing', {}, {})
      deps = {filters.FailFilter: filter_result}
      dict_deps = {filters.FailFilter: xmltodict.parse(filter_result)}
      extractor_result = extractor.run('nothing', deps, dict_deps)
      dict_result = xmltodict.parse(extractor_result)
      self.assertTrue('error' in dict_result['extractor'])
      self.assertFalse('result' in dict_result['extractor'])
      

      
