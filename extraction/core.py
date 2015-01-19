import extraction.xmltodict as xmltodict

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
      dict_results = {}
      for runnable in self.runnables:
         dep_results = dict(filter(lambda (k,v): k in runnable.dependencies(), results.items()))
         dict_dep_results = dict(filter(lambda (k,v): k in runnable.dependencies(), dict_results.items()))

         result = runnable().run(data, dep_results, dict_dep_results)

         results[runnable] = result
         dict_results[runnable] = xmltodict.parse(result)

      doc = '<?xml version="1.0" encoding="utf-8"?>\n'
      doc += '<extraction>\n'
      for key in results:
         doc += results[key]
         doc += '\n'
      doc += '</extraction>'
      return doc

   def run_from_file(self, path):
      return self.run(open(path, 'rb').read())
