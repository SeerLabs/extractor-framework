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

   def test_filter_result_methods(self):
      filt = filters.FailFilter()

      result = filt._filter_fail_xml()
      # using xmltodict is a good way to check that xml is a simple valid format
      # and has the fields we expect regardless of whitespace
      result_dict = xmltodict.parse(result)
      self.assertTrue('FailFilter' in result)
      self.assertTrue('filter' in result_dict)
      self.assertTrue('result' in result_dict['filter'])
      self.assertTrue('fail' in result_dict['filter']['result'])

      result = filt._filter_pass_xml()
      result_dict = xmltodict.parse(result)
      self.assertTrue('FailFilter' in result)
      self.assertTrue('filter' in result_dict)
      self.assertTrue('result' in result_dict['filter'])
      self.assertTrue('pass' in result_dict['filter']['result'])

      result = filt._filter_result_xml(True)
      result_dict = xmltodict.parse(result)
      self.assertTrue('FailFilter' in result)
      self.assertTrue('filter' in result_dict)
      self.assertTrue('result' in result_dict['filter'])
      self.assertTrue('pass' in result_dict['filter']['result'])

      result = filt._filter_result_xml(False)
      result_dict = xmltodict.parse(result)
      self.assertTrue('FailFilter' in result)
      self.assertTrue('filter' in result_dict)
      self.assertTrue('result' in result_dict['filter'])
      self.assertTrue('fail' in result_dict['filter']['result'])
   

   def test_wrap_xml_content(self):
      extractor = extractors.NothingExtractor()
      xml_string = extractor._wrap_xml_content('<tag></tag>')
      dict_result = xmltodict.parse(xml_string)
      self.assertTrue('extractor' in dict_result)
      self.assertTrue('@type' in dict_result['extractor'])
      self.assertEqual(dict_result['extractor']['@type'], 'NothingExtractor')

      filter = filters.PassFilter()
      xml_string = filter._wrap_xml_content('<tag></tag>')
      dict_result = xmltodict.parse(xml_string)
      self.assertTrue('filter' in dict_result)
      self.assertTrue('@type' in dict_result['filter'])
      self.assertEqual(dict_result['filter']['@type'], 'PassFilter')

   def test_error_xml(self):
      extractor = extractors.NothingExtractor()
      xml_string = extractor._error_xml("Test")
      dict_result = xmltodict.parse(xml_string)
      self.assertTrue('error' in dict_result['extractor'])
      self.assertEqual(dict_result['extractor']['error'], 'Test')

      filter = filters.PassFilter()
      xml_string = filter._error_xml("Test")
      dict_result = xmltodict.parse(xml_string)
      self.assertTrue('error' in dict_result['filter'])
      self.assertEqual(dict_result['filter']['error'], 'Test')

   def test_extractor_result_xml_from_dict(self):
      extractor = extractors.NothingExtractor()
      results = {'a':{'b': 5}, 'c': ['a', 'b']}
      xml_string = extractor._extractor_result_xml_from_dict(results)
      dict_result = xmltodict.parse(xml_string)
      self.assertTrue('result' in dict_result['extractor'])
      self.assertEqual(dict_result['extractor']['result']['c'], ['a', 'b'])
      self.assertTrue('b' in dict_result['extractor']['result']['a'])
      

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
      

      
