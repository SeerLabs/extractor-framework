import xmltodict
import glob
from extraction.runnables import Extractor, Filter, RunnableError

class ExtractionRunner(object):
   def __init__(self):
      self.filters = []
      self.extractors = []
      self.runnables = []
      self.runnable_props = {}

   def add_runnable(self, runnable, include_in_output=True):
      #TODO we should construct a graph of filters and extractors
      # then if there are any circular dependencies we can throw an error
      # we can also remove the requirement to add runnables in order
      # these comments also apply to the add_extractor method
      self.runnable_props[runnable] = {
            'include_in_output': include_in_output
         }
      self.runnables.append(runnable)

      if issubclass(runnable, Extractor):
         self.extractors.append(runnable)
      if issubclass(runnable, Filter):
         self.filters.append(runnable)


   def run(self, data, pretty=False, filename=None):
      results = {}
      for runnable in self.runnables:
         dep_results = dict(filter(lambda (k,v): k in runnable.dependencies(), results.items()))

         try:
            result = runnable().run(data, dep_results)
         except RunnableError as err:
            result = err

         results[runnable] = result

      doc = u'<?xml version="1.0" encoding="utf-8"?>\n'
      if filename:
         doc += u'<extraction file="{0}">'.format(filename)
      else:
         doc += u'<extraction>'

      doc += u'<filters>'
      for filt in self.filters:
         if not self.runnable_props[filt]['include_in_output']: continue
         doc += u'<{0}>'.format(filt.__name__)
         doc += self._result_to_string(results[filt])
         doc += u'</{0}>'.format(filt.__name__)
      doc += u'</filters>'

      doc += u'<extractors>'
      for extractor in self.extractors:
         if not self.runnable_props[extractor]['include_in_output']: continue
         doc += u'<{0}>'.format(extractor.__name__)
         doc += self._result_to_string(results[extractor])
         doc += u'</{0}>'.format(extractor.__name__)
      doc += u'</extractors>'
         
      doc += u'</extraction>'
      if pretty:
         doc = xmltodict.unparse(xmltodict.parse(doc), pretty=True)
      return doc

   def run_from_file(self, path, pretty=False):
      return self.run(open(path, 'rb').read(), pretty=pretty, filename=path)

   def run_batch(self, list_of_data, pretty=False):
      for data in list_of_data:
         yield self.run(data, pretty=pretty)

   def run_batch_from_glob(self, dir_glob, pretty=False):
      for path in glob.iglob(dir_glob):
         yield (path, self.run_from_file(path, pretty=pretty))

   def _result_to_string(self, result):
      if isinstance(result, dict):
         return u'<result>{0}</result>'.format(xmltodict.unparse(result, full_document=False))
      elif isinstance(result, RunnableError):
         return u'<error>{0}</error>'.format(result.msg)
      else:
         return u'<result>{0}</result>'.format(result)


