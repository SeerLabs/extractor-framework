import extraction.xmltodict as xmltodict

class Base(object):
   @staticmethod
   def dependencies():
      return []

   def __init__(self):
      pass

   def check_dep_errors(self, dependency_results):
      deps = self.__class__.dependencies()
      filter_deps = [e for e in deps if issubclass(e, Filter)]
      extractor_deps = [e for e in deps if issubclass(e, Extractor)]

      for filter in filter_deps:
         dict_result = xmltodict.parse(dependency_results[filter])
         if 'error' in dict_result['filter']:
            return self._error_xml('Dependency %s errored' % filter.__name__)
         elif dict_result['filter']['result'] == 'fail':
            return self._error_xml('Data failed filter %s' % filter.__name__)

      for extractor in extractor_deps:
         dict_result = xmltodict.parse(dependency_results[extractor])
         if 'error' in dict_result['extractor']:
            return self._error_xml('Dependency %s errored' % extractor.__name__)

      return None

   def _error_xml(self, error_message):
      return self._wrap_xml_content('<error>%s</error>' % error_message)


class Filter(Base):
   def filter(self, data, dependency_results):
      return self._filter_fail_xml()

   def run(self, data, dependency_results):
      dep_errors =  self.check_dep_errors(dependency_results)
      if dep_errors:
         return dep_errors

      return self.filter(data, dependency_results)

   def _filter_pass_xml(self):
      return self._wrap_xml_content('<result>pass</result>')

   def _filter_fail_xml(self):
      return self._wrap_xml_content('<result>fail</result>')

   def _wrap_xml_content(self, xml_string):
      return '<filter type="%s">%s</filter>' % (self.__class__.__name__, xml_string)

class Extractor(Base):
   def extract(self, data, dependency_results):
      return self._extractor_result_xml('Nothing')

   def run(self, data, dependency_results):
      dep_errors = self.check_dep_errors(dependency_results)
      if dep_errors:
         return dep_errors

      return self.extract(data, dependency_results)   

   def _extractor_result_xml(self, result_xml):
      return self._wrap_xml_content('<result>%s</result>' % result_xml)

   def _wrap_xml_content(self, xml_string):
      return '<extractor type="%s">%s</extractor>' % (self.__class__.__name__, xml_string)
      
