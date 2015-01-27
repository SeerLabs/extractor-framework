'''This module contains a sample use case for the library.

It's just a demo, so for example, the EmailExtractor is quite simplistic.
'''

from extraction.core import ExtractionRunner
from extraction.runnables import Filter, Extractor
import xmltodict
import extraction.utils as utils
import re
import subprocess

class HasNumbersFilter(Filter):
   def filter(self, data, deps, dict_deps):
      success = re.search(r'[0-9]', data, re.UNICODE)
      return self._filter_result_xml(success)

class EmailExtractor(Extractor):
   @staticmethod
   def dependencies():
      return [HasNumbersFilter]

   def extract(self, data, deps, dict_deps):
      emails = re.findall(r'\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,4}\b',
                        data,
                        re.IGNORECASE | re.UNICODE)
      return self._extractor_result_xml_from_dict({'email': emails})

class LinesStartWithNumberExtractor(Extractor):
   @staticmethod
   def dependencies():
      return [HasNumbersFilter]

   def extract(self, data, deps, dict_deps):
      (stdout, stderr) = utils.external_process(data, ['awk', '/^[0-9]/ {print;}', '-'])
      lines = [line for line in stdout.split("\n") if line]
      return self._extractor_result_xml_from_dict({'line': lines})

extraction_runner = ExtractionRunner()
extraction_runner.add_filter(HasNumbersFilter)
extraction_runner.add_extractor(EmailExtractor)
extraction_runner.add_extractor(LinesStartWithNumberExtractor)

print extraction_runner.run(u'''Random data inputted with some emails bob@example.com
523 And some more text with @ signs now and then. Meet you@home@2p.m.
      And some more stuff. howie009@yahoo.com
      jones@gmail.com fredie@emerson.retail.com
123 bobbie@ist.psu.edu and that's all the text here.''')

print '\n\n\n'


print extraction_runner.run(u'Silly texy with email email@example.com but no numbers')


print '\n\n\n'
print extraction_runner.run_from_file('extraction/test/file_sample.txt')

      
      
