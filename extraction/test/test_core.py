import os
import tempfile
import unittest
import xmltodict
from extraction.test.extractors import *
from extraction.test.filters import *
from extraction.core import ExtractionRunner

class TestExtractionRunner(unittest.TestCase):
   def setUp(self):
      temp_dir = tempfile.mkdtemp()
      self.file_dir = temp_dir

      f1, f1_path = tempfile.mkstemp('.txt', dir=temp_dir)
      f1 = os.fdopen(f1, 'w')
      f1.write('file 1')
      f1.close()
      self.f1_path = f1_path

      f2, f2_path = tempfile.mkstemp('.txt', dir=temp_dir)
      f2 = os.fdopen(f2, 'w')
      f2.write('file 2')
      f2.close()
      self.f2_path = f2_path

      f3, f3_path = tempfile.mkstemp(dir=temp_dir)
      f3 = os.fdopen(f3, 'w')
      f3.write('file 3')
      f3.close()
      self.f3_path = f3_path

   def tearDown(self):
      os.remove(self.f1_path)
      os.remove(self.f2_path)
      os.remove(self.f3_path)
      os.rmdir(self.file_dir)


   def test_nothing_run(self):
      runner = ExtractionRunner()
      xml = runner.run(u'data!')
      result = xmltodict.parse(xml)
      self.assertTrue('extraction' in result)
      self.assertTrue('filters' in result['extraction'])
      self.assertTrue('extractors' in result['extraction'])
      # ensure filename isn't in runs from data
      self.assertTrue('@file' not in result['extraction'])

   def test_run_from_file(self):
      runner = ExtractionRunner()
      runner.add_runnable(SelfExtractor)
      xml = runner.run_from_file(self.f1_path)
      result = xmltodict.parse(xml)
      self.assertTrue('SelfExtractor' in result['extraction']['extractors'])
      self.assertTrue('result' in result['extraction']['extractors']['SelfExtractor'])
      self.assertEqual(result['extraction']['extractors']['SelfExtractor']['result'], 'file 1')

      # ensure filename present
      self.assertTrue('@file' in result['extraction'])

   def test_run_batch(self):
      runner = ExtractionRunner()
      runner.add_runnable(SelfExtractor)
      xmls = list(runner.run_batch(['test 1', 'test 2']))
      results = [xmltodict.parse(x) for x in xmls]
      self.assertEqual(results[0]['extraction']['extractors']['SelfExtractor']['result'], 'test 1')
      self.assertEqual(results[1]['extraction']['extractors']['SelfExtractor']['result'], 'test 2')
      

   def test_run_batch_from_glob(self):
      runner = ExtractionRunner()
      runner.add_runnable(SelfExtractor)

      glob = self.file_dir + '/*.txt'
      xmls = list(runner.run_batch_from_glob(glob))
      results = dict([(x[0], xmltodict.parse(x[1])) for x in xmls])
      self.assertEqual(len(results), 2)
      self.assertTrue('file 1' in results[self.f1_path]['extraction']['extractors']['SelfExtractor']['result'])
      self.assertTrue('file 2' in results[self.f2_path]['extraction']['extractors']['SelfExtractor']['result'])
      self.assertFalse(self.f3_path in results)
      self.assertTrue('@file' in results[self.f1_path]['extraction'])
      self.assertTrue('@file' in results[self.f2_path]['extraction'])

   def test_extractor_errors_cascade(self):
      runner = ExtractionRunner()
      runner.add_runnable(ErrorExtractor)
      runner.add_runnable(DepsOnErrorExtractor)
      runner.add_runnable(DepsOnErrorExtractor2)

      xml = runner.run('data')
      result = xmltodict.parse(xml)
      self.assertTrue('error' in result['extraction']['extractors']['ErrorExtractor'])
      self.assertFalse('result' in result['extraction']['extractors']['ErrorExtractor'])
      self.assertTrue('error' in result['extraction']['extractors']['DepsOnErrorExtractor'])
      self.assertFalse('result' in result['extraction']['extractors']['DepsOnErrorExtractor'])
      self.assertTrue('error' in result['extraction']['extractors']['DepsOnErrorExtractor2'])
      self.assertFalse('result' in result['extraction']['extractors']['DepsOnErrorExtractor2'])
      
   def test_filter_results_cascade(self):
      runner = ExtractionRunner()
      runner.add_runnable(FailFilter)
      runner.add_runnable(FailingDepsExtractor)

      xml = runner.run('data')
      result = xmltodict.parse(xml)
      self.assertTrue('False' in result['extraction']['filters']['FailFilter']['result'])
      self.assertTrue('error' in result['extraction']['extractors']['FailingDepsExtractor'])

      runner = ExtractionRunner()
      runner.add_runnable(PassFilter)
      runner.add_runnable(PassingDepsExtractor)

      xml = runner.run('data')
      result = xmltodict.parse(xml)
      self.assertTrue('True' in result['extraction']['filters']['PassFilter']['result'])
      self.assertTrue('result' in result['extraction']['extractors']['PassingDepsExtractor'])

      
