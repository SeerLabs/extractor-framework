from extraction.runnables import Extractor
import extraction.test.filters as filters

class NothingExtractor(Extractor):
   def extract(self, data, dep_results):
      return 'This extractor does nothing!'

class SelfExtractor(Extractor):
   def extract(self, data, dep_results):
      return data

class FailingDepsExtractor(Extractor):
   @staticmethod
   def dependencies():
      return [filters.FailFilter]
   def extract(self, data, dep_results):
      return 'This extractor should never run!'

class EmailExtractor(Extractor):
   def extract(self, data, deps):
      emails = re.findall(r'\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,4}\b',
                        data,
                        re.IGNORECASE | re.UNICODE)
      return {'email': emails}


