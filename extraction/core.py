import glob
import os
import xml.etree.ElementTree as ET
from extraction.runnables import Extractor, Filter, RunnableError, ExtractorResult

class ExtractionRunner(object):
   def __init__(self):
      self.filters = []
      self.extractors = []
      self.runnables = []
      self.runnable_props = {}

   def add_runnable(self, runnable, output_results=True):
      #TODO we should construct a graph of filters and extractors
      # then if there are any circular dependencies we can throw an error
      # we can also remove the requirement to add runnables in order
      # these comments also apply to the add_extractor method
      self.runnable_props[runnable] = {
            'output_results': output_results
         }
      self.runnables.append(runnable)

      if issubclass(runnable, Extractor):
         self.extractors.append(runnable)
      if issubclass(runnable, Filter):
         self.filters.append(runnable)


   def run(self, data, output_dir):
      results = {}
      for runnable in self.runnables:
         dep_results = dict(filter(lambda (k,v): k in runnable.dependencies(), results.items()))

         try:
            result = runnable().run(data, dep_results)
         except RunnableError as err:
            result = err

         results[runnable] = result

      if not os.path.exists(output_dir):
         os.makedirs(output_dir)

      for runnable in results:
         if self.runnable_props[runnable]['output_results']: 
            result = results[runnable]
            self._output_result(runnable, result, output_dir)

   def run_from_file(self, file_path, output_dir=None):
      if not output_dir:
         output_dir = os.path.dirname(file_path)

      return self.run(open(file_path, 'rb').read(), output_dir)

   def run_batch(self, list_of_data, output_dir):
      for index, data in enumerate(list_of_data):
         self.run(data, os.path.join(output_dir, index))

   #TODO figure out what output_dir should be...
   #def run_batch_from_glob(self, dir_glob, output_dir)
      #for path in enumerate(glob.iglob(dir_glob)):
         #self.run_from_file(path, pretty=pretty))

   def _output_result(self, runnable, result, output_dir):
      if isinstance(result, RunnableError):
         error = ET.Element('error')
         error.text = result.msg
         result = ET.ElementTree(error)
         result_path = os.path.join(output_dir,'{0}.xml'.format(runnable.__name__))
         result.write(result_path, encoding='UTF-8')
      elif isinstance(result, ExtractorResult):
         files_dict = result.files
         xml_result = result.xml_result
         result_path = os.path.join(output_dir,'{0}.xml'.format(runnable.__name__))

         xml_result.write(result_path, encoding='UTF-8')

         if files_dict:
            for file_name, file_data in files_dict.items():
               f = open(os.path.join(output_dir, file_name), 'wb')
               f.write(file_data)
               f.close()
