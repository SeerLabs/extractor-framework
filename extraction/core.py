import xmltodict
from extraction.runnables import Extractor, Filter, RunnableError

class ExtractionRunner(object):
   def __init__(self):
      self.filters = []
      self.extractors = []
      self.runnables = []

   def add_runnable(self, runnable):
      #TODO we should construct a graph of filters and extractors
      # then if there are any circular dependencies we can throw an error
      # we can also remove the requirement to add runnables in order
      # these comments also apply to the add_extractor method
      self.runnables.append(runnable)

      if issubclass(runnable, Extractor):
         self.extractors.append(runnable)
      if issubclass(runnable, Filter):
         self.filters.append(runnable)


   def run(self, data, pretty=False):
      results = {}
      for runnable in self.runnables:
         dep_results = dict(filter(lambda (k,v): k in runnable.dependencies(), results.items()))

         try:
            result = runnable().run(data, dep_results)
         except RunnableError as err:
            result = err

         results[runnable] = result

      doc = '<?xml version="1.0" encoding="utf-8"?>\n'
      doc += '<extraction>'

      doc += '<filters>'
      for filt in self.filters:
         doc += '<{0}>'.format(filt.__name__)
         doc += self._result_to_string(results[filt])
         doc += '</{0}>'.format(filt.__name__)
      doc += '</filters>'

      doc += '<extractors>'
      for extractor in self.extractors:
         doc += '<{0}>'.format(extractor.__name__)
         doc += self._result_to_string(results[extractor])
         doc += '</{0}>'.format(extractor.__name__)
      doc += '</extractors>'
         
      doc += '</extraction>'
      if pretty:
         doc = xmltodict.unparse(xmltodict.parse(doc), pretty=True)
      return doc

   def run_from_file(self, path, pretty=False):
      return self.run(open(path, 'rb').read(), pretty=pretty)

   def _result_to_string(self, result):
      if isinstance(result, dict):
         return '<result>{0}</result>'.format(xmltodict.unparse(result, full_document=False))
      elif isinstance(result, RunnableError):
         return '<error>{0}</error>'.format(result.msg)
      else:
         return '<result>{0}</result>'.format(result)


