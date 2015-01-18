# Extraction Framework #

## Using the framework ##

Example usage:

```
#!python

# import require modules
import extraction.runnables as runnables
from extraction.core import ExtractionRunner

# define extractors and filters

# All filters extend the runnables.Filter class
class HasLongContentFilter(runnables.Filter):

   # override the filter method to define the actual logic
   # filters should return an xml string indictating their result
   # there are three helper functions to generate this string
   # _filter_fail_result(), _filter_pass_result(), and _error_result(error_message)
   def filter(self, data, dep_results, dict_dep_results):
      success = len(data) > 50
      return self._filter_result_xml(success)

# All extractors extend the runnables.Extractor class
class TrimmedTextExtractor(runnables.Extractor):
   # If an extractor/filter depends on a previous result
   # define a staticmethod that returns an array of dependencies
   @staticmethod
   def dependencies():
      return [HasContentFilter]

   # override the extract method to define extraction logic
   # the extract method should return an xml string
   # there are two helper functions to do this
   # _extractor_result(result_xml) and _error_result(error_message)
   def extract(self, data, dep_results, dict_dep_results):
      return self._extractor_result(data[:-1])

# Create and run the whole extraction process
runner = ExtractionRunner()
runner.add_filter(HasContentFilter)
runner.add_extractor(TrimmedTextExtractor)

xmlResults = runner.run_from_file('/path/to/pdf')

```

## Sample Framework Usage ##
For another example of usage, see extraction/test/sample.py

Or, from the project root, you can run:

    python -m extraction.test.sample


## Running the unittests ##

Run, from the project root directory:

    python -m extraction.test.__main__

If using Python 2.7 you can run more simply:

    python -m extraction.test
