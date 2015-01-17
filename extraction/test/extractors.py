import extraction.runnables as runnables
import extraction.test.filters as filters

class NothingExtractor(runnables.Extractor):

   def extract(self, data, dependencyResults):
      return self._filter_result_xml('This extractor does nothing!')

class FailingDepsExtractor(runnables.Extractor):

   @staticmethod
   def dependencies():
      return [filters.FailFilter]
   def extract(self, data, dependencyResults):
      return self._extractor_result_xml('This extractor should never run!')
