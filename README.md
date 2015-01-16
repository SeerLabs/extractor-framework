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
class HasContentFilter(runnables.Filter):

   # override the filter method to define the actual logic
   # filters should return a boolean for success
   def filter(self, data, dependency_results):
      return len(data) > 0

# All extractors extend the runnables.Extractor class
class TrimmedTextExtractor(runnables.Extractor):
   # If an extractor/filter depends on a previous result
   # define a staticmethod that returns an array of dependencies
   @staticmethod
   def dependencies():
      return [HasContentFilter]

   # override the extract method to define extraction logic
   # the extract method will probably return an xml string (TODO)
   def extract(self, data, dependency_results):
      return data[:-1]

# Create and run the whole extraction process
runner = ExtractionRunner()
runner.add_filter(HasContentFilter)
runner.add_extractor(TrimmedTextExtractor)

xmlResults = runner.run_from_file('/path/to/pdf')

```


## Running the unittests ##

Run, from the project root directory:

    python -m extraction.test.__main__

If using Python 2.7 you can run more simply:

    python -m extraction.test
