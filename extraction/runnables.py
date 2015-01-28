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
         dep_results -- the results of any declared dependencies in xml form
         dict_dep_results -- the same results as the previous argument, except in dict form

      This method should return a string in xml format like one of the three examples:
        <filter type="FilterClassName"><result>fail</result></filter>
        <filter type="FilterClassName"><result>pass</result></filter>
        <filter type="FilterClassName"><error>Error message</error></filter>

      There are various helper methods to generate these strings:
      >>> self._filter_fail_xml()
      <filter type="FilterClassName"><result>fail</result></filter>
      
      >>>  self._filter_pass_xml()
      <filter type="FilterClassName"><result>pass</result></filter>

      >>> self._error_xml('Error message')
      <filter type="FilterClassName"><error>Error message</error></filter>
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
         dep_results -- the results of any declared dependencies in xml form
         dict_dep_results -- the same results as the previous argument, except in dict form

      This method should return a string in xml format like one of the two examples:
        <extractor type="ExtractorClassName"><result>result body as xml</result></extractor>
        <extractor type="ExtractorClassName"><error>Error message</error></extractor>

      There are various helper methods to generate these results.
      >>> self._error_xml('Error message') will generate a string like the second example
      <extractor type="ExtractorClassName"><error>Error message</error></extractor>
      
      >>> self._extractor_result_xml('<author>Joe</author><author>James</author>')
      <extractor type="ExtractorClassName><result>
         <author>Joe</author><author>James</author>
      </result></extractor>

      >>> self._extractor_result_xml_from_dict({'author': ['Joe', 'James']})
      <extractor type="ExtractorClassName><result>
         <author>Joe</author><author>James</author>
      </result></extractor>
      """
      return self._extractor_result_xml('Nothing')

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
