import glob
import sys
import os
import logging
import multiprocessing as mp
import xml.etree.ElementTree as ET
import copy_reg
import types
from extraction.runnables import *
import extraction.utils as utils


def _pickle_method(method):
   func_name = method.im_func.__name__
   obj = method.im_self
   cls = method.im_class
   return _unpickle_method, (func_name, obj, cls)

def _unpickle_method(func_name, obj, cls):
   for cls in cls.mro():
      try:
         func = cls.__dict__[func_name]
      except KeyError:
         pass
      else:
         break
   return func.__get__(obj, cls)

copy_reg.pickle(types.MethodType, _pickle_method, _unpickle_method)

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

      if not self.result_logger.handlers:
         self.result_logger.addHandler(logging.StreamHandler(sys.stdout))
      if not self.runnable_logger.handlers:
         self.runnable_logger.addHandler(logging.StreamHandler(sys.stderr))
 

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
      """Causes the extraction runner to keep logs of what it does
      If a log file from the same day exists, it is used. If not, new logs files are created for the current day
      If this method is not called, by default, info will be printed to stdout and stderr

      Args:
         result_log_path: String file path that indicates where to store the results log.
            This log stores when processing starts and ends for each run. It also notes if any errors occur during the run.
            For example, if this is '/path/to/result' the logs will be stored in files named '/path/to/log.[year]-[month]-[day].log'
         runnable_log_path: String file path that indicates where to store the runnables log.
            This log contains any log messages that runnables log.
            Path and day rotation is handled the same as with the results log
      """

      result_log_path = utils.expand_path(result_log_path)
      runnable_log_path = utils.expand_path(runnable_log_path)

      if not os.path.exists(os.path.dirname(result_log_path)): os.makedirs(os.path.dirname(result_log_path))
      if not os.path.exists(os.path.dirname(runnable_log_path)): os.makedirs(os.path.dirname(runnable_log_path))

      result_log_handler = utils.ParallelTimedRotatingFileHandler(result_log_path, when='D', delay=True)
      runnable_log_handler = utils.ParallelTimedRotatingFileHandler(runnable_log_path, when='D', delay=True)

      formatter = logging.Formatter('%(asctime)s: %(message)s')
      result_log_handler.setFormatter(formatter)
      runnable_log_handler.setFormatter(formatter)

      self.result_logger.handlers = []
      self.runnable_logger.handlers = []

      self.result_logger.addHandler(result_log_handler)
      self.runnable_logger.addHandler(runnable_log_handler)

   def disable_logging(self):
      """Disables logging to files. Instead, info will be printed to stdout and stderr
      """

      self.result_logger.handlers = []
      self.runnable_logger.handlers = []

      self.result_logger.addHandler(logging.StreamHandler(sys.stdout))
      self.runnable_logger.addHandler(logging.StreamHandler(sys.stderr))

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
            run_name: A string used in logs that identifies what data is being processed
               If this argument isn't displayed, a random string will be used

      """
      _real_run(self.runnables, self.runnable_props, data, output_dir, **kwargs)


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

      file_path = utils.expand_path(file_path)

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

   def run_from_file_batch(self, file_paths, output_dirs, **kwargs):
      batch_id = utils.random_letters(10)
      self.result_logger.info("Starting Batch {0} Run".format(batch_id))

      pool = mp.Pool(4)
      for i, (path, dir) in enumerate(zip(file_paths, output_dirs)):
         args = (self.runnables, self.runnable_props, open(path, 'rb').read(), dir)

         kws = {'run_name': path}
         if 'file_prefixes' in kwargs: kws['file_prefix'] = kwargs['file_prefixes'][i]
         if 'file_prefix' in kwargs: kws['file_prefix'] = kwargs['file_prefix']
         if 'write_dep_errors' in kwargs: kws['write_dep_errors'] = kwargs['write_dep_errors']

         pool.apply_async(_real_run, args=args, kwds=kws)

      pool.close()
      pool.join()

      self.result_logger.info("Finished Batch {0} Run".format(batch_id))

def _real_run(runnables, runnable_props, data, output_dir, **kwargs):
   result_logger = logging.getLogger('result')

   write_dep_errors = kwargs.get('write_dep_errors', False)
   file_prefix = kwargs.get('file_prefix', '')
   run_name = kwargs.get('run_name', utils.random_letters(8))

   result_logger.info('{0} started'.format(run_name))

   results = {}
   for runnable in runnables:
      dep_results = _select_dependency_results(runnable.dependencies(), results)

      instance = runnable()
      instance.run_name = run_name
      instance.logger = logging.getLogger('runnables.{0}'.format(runnable.__name__))
      result = instance.run(data, dep_results)

      results[runnable] = result

   output_dir = os.path.abspath(os.path.expanduser(output_dir))

   if not os.path.exists(output_dir):
      os.makedirs(output_dir)

   any_errors = False
   for runnable in results:
      if runnable_props[runnable]['output_results']: 
         result = results[runnable]
         if isinstance(result, RunnableError): any_errors = True
         _output_result(runnable, result, output_dir, run_name, file_prefix=file_prefix, write_dep_errors=write_dep_errors)
   result_logger.info('{0} finished with {1}'.format(run_name, 'no errors' if not any_errors else 'errors'))


def _select_dependency_results(dependencies, results):
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

def _output_result(runnable, result, output_dir, run_name, file_prefix='', write_dep_errors=False):
   logger = logging.getLogger('results')
   if isinstance(result, RunnableError):
      if isinstance(result, DependencyError) and not write_dep_errors:
         return 

      logger.info('{0} error: {1}'.format(run_name, result.msg)) 

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
