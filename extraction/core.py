import glob
import os
import xml.etree.ElementTree as ET
from extraction.runnables import *

class ExtractionRunner(object):
   def __init__(self):
      self.filters = []
      self.extractors = []
      self.runnables = []
      self.runnable_props = {}

   def add_runnable(self, runnable, output_results=True):
      self.runnable_props[runnable] = {
            'output_results': output_results
         }
      self.runnables.append(runnable)

      if issubclass(runnable, Extractor):
         self.extractors.append(runnable)
      if issubclass(runnable, Filter):
         self.filters.append(runnable)


   def run(self, data, output_dir, **kwargs):
      """Runs the extractor (with all runnables previously added) on data

      Args:
         data: A string of data. This will be passed as is to all filters and extractors
         output_dir: The directory that the result xml and other files will be written to
         **kwargs: Optional keyword arguments
            write_dep_errors: A Boolean. If True, extractors that fail because dependencies fail
               will still write a short xml file with this error to disk. (Good for clarity)
               If False, extractors with failing dependencies won't write anything to disk
            file_prefix: A string to prepend to all filenames that get written to disk

      """
      write_dep_errors = kwargs.get('write_dep_errors', False)
      file_prefix = kwargs.get('file_prefix', '')

      results = {}
      for runnable in self.runnables:
         dep_results = self._select_dependency_results(runnable.dependencies(), results)

         try:
            result = runnable().run(data, dep_results)
         except RunnableError as err:
            result = err

         results[runnable] = result

      output_dir = os.path.abspath(os.path.expanduser(output_dir))

      if not os.path.exists(output_dir):
         os.makedirs(output_dir)

      for runnable in results:
         if self.runnable_props[runnable]['output_results']: 
            result = results[runnable]
            self._output_result(runnable, result, output_dir, file_prefix=file_prefix, write_dep_errors=write_dep_errors)

   def run_from_file(self, file_path, output_dir=None, **kwargs):
      """Runs the extractor on the file at file_path

      Reads the file at file_path from disk into a string. Then runs the extractors
      on this data string.

      Args:
         file_path: Reads this file and passes its data to the extractors and filters
         output_dir: An optional string that specifies the directory to write the results to
            If this isn't provided, results will be written to the same directory as the file
         **kwargs: Optional keyword arguments
            write_dep_errors: A Boolean. If True, extractors that fail because dependencies fail
               will still write a short xml file with this error to disk. (Good for clarity)
               If False, extractors with failing dependencies won't write anything to disk
            file_prefix: A string to prepend to all filenames that get written to disk

      """

      if not output_dir:
         output_dir = os.path.dirname(file_path)

      return self.run(open(file_path, 'rb').read(), output_dir, **kwargs)

   def run_batch(self, list_of_data, output_dir, **kwargs):
      for index, data in enumerate(list_of_data):
         self.run(data, os.path.join(output_dir, str(index)), **kwargs)

   #TODO figure out what output_dir should be...
   #def run_batch_from_glob(self, dir_glob, output_dir)
      #for path in enumerate(glob.iglob(dir_glob)):
         #self.run_from_file(path, pretty=pretty))

   def _select_dependency_results(self, dependencies, results):
      # N^2 implementation right now, maybe this doesn't matter but could be improved if needed
      dependency_results = {}
      for DependencyClass in dependencies:
         for ResultClass, result in results.items():
            if issubclass(ResultClass, DependencyClass):
               dependency_results[DependencyClass] = result
               break
         else:
            raise LookupError('No runnable satisfies the requirement for a {0}'.format(DependencyClass.__name__))

      return dependency_results

   def _output_result(self, runnable, result, output_dir, file_prefix='', write_dep_errors=False):
      if isinstance(result, RunnableError):

         if isinstance(result, DependencyError) and not write_dep_errors:
            return

         error = ET.Element('error')
         error.text = result.msg
         result = ET.ElementTree(error)
         result_path = os.path.join(output_dir,'{0}{1}.xml'.format(file_prefix, runnable.__name__))
         result.write(result_path, encoding='UTF-8')
      elif isinstance(result, ExtractorResult):
         files_dict = result.files
         xml_result = ET.ElementTree(result.xml_result)

         result_path = os.path.join(output_dir,'{0}{1}.xml'.format(file_prefix, runnable.__name__))

         xml_result.write(result_path, encoding='UTF-8')

         if files_dict:
            for file_name, file_data in files_dict.items():
               file_name = file_prefix + file_name
               f = open(os.path.join(output_dir, file_name), 'wb')
               f.write(file_data)
               f.close()
