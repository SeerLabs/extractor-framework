'''This module contains a sample use case for the library.

It's just a demo, so for example, the EmailExtractor is quite simplistic.
'''

from extraction.core import ExtractionRunner
from extraction.runnables import Filter, Extractor
import extraction.xmltodict as xmltodict
import re

class HasNumbersFilter(Filter):
   def filter(self, data, deps, dict_deps):
      if re.search(r'[0-9]', data, re.UNICODE):
         return self._filter_pass_xml()
      else:
         return self._filter_fail_xml()

class EmailExtractor(Extractor):
   @staticmethod
   def dependencies():
      return [HasNumbersFilter]

   def extract(self, data, deps, dict_deps):
      emails = re.findall(r'\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,4}\b',
                        data,
                        re.IGNORECASE | re.UNICODE)

      xml_result = xmltodict.unparse({'result': {'email': emails}}, full_document=False)
      xml_result = self._wrap_xml_content(xml_result)
      return xml_result

extraction_runner = ExtractionRunner()
extraction_runner.add_filter(HasNumbersFilter)
extraction_runner.add_extractor(EmailExtractor)
print extraction_runner.run(u'''Random data inputted with some emails bob@example.com
      And some more text with @ signs now and then. Meet you@home@2p.m.
      And some more stuff. howie009@yahoo.com
      jones@gmail.com fredie@emerson.retail.com
      bobbie@ist.psu.edu and that's all the text here.''')


print extraction_runner.run(u'Silly texy with email email@example.com but no numbers')


      
      
