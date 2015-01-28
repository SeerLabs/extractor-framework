import xmltodict

class Base(object):
   @staticmethod
   def dependencies():
      return []

   def __init__(self):
      pass

   def check_dep_errors(self, dep_results):
      deps = self.__class__.dependencies()
      filter_deps = [e for e in deps if issubclass(e, Filter)]
      extractor_deps = [e for e in deps if issubclass(e, Extractor)]

      for filter in filter_deps:
         result = dep_results[filter]
         if isinstance(result, RunnableError):
            return RunnableError('Did not run because dependency filter %s errored' % filter.__name__)
         elif not result:
            return RunnableError('Did not run because dependency filter %s failed' % filter.__name__)

      for extractor in extractor_deps:
         result = dep_results[extractor]
         if isinstance(result, RunnableError):
            return RunnableError('Did not run because dependency extractor %s errored' % extractor.__name__)

      return None

class Filter(Base):
   def filter(self, data, dep_results):
      """
      Override this method in Filter subclasses to define custom filtering logic

      This method will be called automatically by the ExtractionRunner during the extraction process

      Arguments passed in:
         data -- the original data the extractor started with
         dep_results -- the results of any declared dependency filters or extractors

      If the filter is successful, this method should:
         return True

      If the filter fails, this method should:
         return False

      If the filters encounters something unexpected, this method should:
         raise RunnableError('Error Description Here')
      """
      return False

   def run(self, data, dep_results):
      dep_error =  self.check_dep_errors(dep_results)
      if dep_error:
         return dep_error

      return self.filter(data, dep_results)


class Extractor(Base):
   def extract(self, data, dep_results):
      """
      Override this method in Extractor subclasses to define custom extraction logic

      This method will be called automatically by the ExtractionRunner during the extraction process

      Arguments passed in:
         data -- the original data the extractor started with
         dep_results -- the results of any declared dependencies 

      If the extractor succeeds, it should either return an:
         xml snippet in string form of the results
            or
         dict object of the results

      If the extract method returns a dict object, it will be passed to other extractors as a dict
      However, it will be converted to xml via the xmltodict library for the final generated xml file
      """
      return 'Nothing'

   def run(self, data, dep_results):
      dep_error = self.check_dep_errors(dep_results)
      if dep_error:
         return dep_error

      return self.extract(data, dep_results)    


class RunnableError(Exception):
   def __init__(self, msg):
      self.msg = msg

   def __unicode__(self):
      return "RunnableError: {0}".format(self.msg)
