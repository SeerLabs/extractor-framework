import glob
import os
import logging
import logging.handlers
import xml.etree.ElementTree as ET
from extraction.runnables import *
import extraction.utils as utils

class ExtractionRunner(object):
   def __init__(self):
      self.filters = []
      self.extractors = []
      self.runnables = []
      self.runnable_props = {}
      self.result_logger = logging.getLogger('result')
      self.runnable_logger = logging.getLogger('runnables')
      self.result_logger.setLevel(logging.INFO)
      self.runnable_logger.setLevel(logging.INFO)
 

   def add_runnable(self, runnable, output_results=True):
      """Adds runnable to the extractor to be run when the extractor is run

      Runnables are ran in the order they are added! So make sure runnables that depend on others
      are run after what they depend on.

      Args:
         runnable: A class that is a subclass of extraction.runnables.Extractor
            or a subclass of extraction.runnables.Filter
         output_results: Optional boolean that indicates if the results from the runnable should be
            written to disk when the extractor runs. If False, the results will not be written and will
            just be used internally during extraction
      """

      self.runnable_props[runnable] = {
            'output_results': output_results
         }
      self.runnables.append(runnable)

      if issubclass(runnable, Extractor):
         self.extractors.append(runnable)
      if issubclass(runnable, Filter):
         self.filters.append(runnable)

   def enable_logging(self, result_log_path, runnable_log_path):
      result_log_path = os.path.abspath(os.path.expanduser(result_log_path))
      runnable_log_path = os.path.abspath(os.path.expanduser(runnable_log_path))

      result_log_handler = utils.ParallelTimedRotatingFileHandler(result_log_path, when='D')
      runnable_log_handler = utils.ParallelTimedRotatingFileHandler(runnable_log_path, when='D')

      formatter = logging.Formatter('%(asctime)s: %(message)s')
      result_log_handler.setFormatter(formatter)
      runnable_log_handler.setFormatter(formatter)

      self.result_logger.addHandler(result_log_handler)
      self.runnable_logger.addHandler(runnable_log_handler)


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
      run_name = kwargs.get('run_name', utils.random_letters(8))

      self.result_logger.info('{0} started'.format(run_name))

      results = {}
      for runnable in self.runnables:
         dep_results = self._select_dependency_results(runnable.dependencies(), results)

         try:
            instance = runnable()
            instance.run_name = run_name
            instance.logger = logging.getLogger('runnables.{0}'.format(runnable.__name__))
            result = instance.run(data, dep_results)
         except RunnableError as err:
            result = err

         results[runnable] = result

      output_dir = os.path.abspath(os.path.expanduser(output_dir))

      if not os.path.exists(output_dir):
         os.makedirs(output_dir)

      any_errors = False
      for runnable in results:
         if self.runnable_props[runnable]['output_results']: 
            result = results[runnable]
            if isinstance(result, RunnableError): any_errors = True
            self._output_result(runnable, result, output_dir, run_name, file_prefix=file_prefix, write_dep_errors=write_dep_errors)
      self.result_logger.info('{0} finished with {1}'.format(run_name, 'no errors' if not any_errors else 'errors'))

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

      return self.run(open(file_path, 'rb').read(), output_dir, run_name=file_path, **kwargs)

   def run_batch(self, list_of_data, output_dir, **kwargs):
      batch_id = utils.random_letters(10)
      self.result_logger.info("Starting Batch {0} Run".format(batch_id))
      for index, data in enumerate(list_of_data):
         run_name = 'Batch {0} Item {1}'.format(batch_id, index)
         self.run(data, os.path.join(output_dir, str(index)), run_name=run_name, **kwargs)
      self.result_logger.info("Finished Batch {0} Run".format(batch_id))

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

   def _output_result(self, runnable, result, output_dir, run_name, file_prefix='', write_dep_errors=False):
      if isinstance(result, RunnableError):
         if isinstance(result, DependencyError) and not write_dep_errors:
            return 

         self.result_logger.info('{0} error: {1}'.format(run_name, result.msg)) 

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
