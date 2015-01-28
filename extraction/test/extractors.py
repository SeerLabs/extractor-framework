import extraction.runnables as runnables
import extraction.test.filters as filters

class NothingExtractor(runnables.Extractor):

   def extract(self, data, dep_results):
      return 'This extractor does nothing!'

class FailingDepsExtractor(runnables.Extractor):

   @staticmethod
   def dependencies():
      return [filters.FailFilter]
   def extract(self, data, dep_results):
      return 'This extractor should never run!'
