
class ExtractionRunner(object):
   def __init__(self):
      self.filters = []
      self.extractors = []
      self.runnables = []

   def add_filter(self, filter):
      #TODO we should construct a graph of filters and extractors
      # then if there are any circular dependencies we can throw an error
      # we can also remove the requirement to add runnables in order
      # these comments also apply to the add_extractor method
      self.filters.append(filter)
      self.runnables.append(filter)

   def add_extractor(self, extractor):
      self.extractors.append(extractor)
      self.runnables.append(extractor)
      
   def run(self, data):
      results = {}
      for runnable in self.runnables:
         dep_results = {k: v for k,v in results if k in runnable.dependencies}
         result = runnable.run(data, dep_results)
         results[runnable] = result

      #TODO return xml string?
      return results

   def run_from_file(self, path):
      self.run(open(path, 'rb').read())
