# Extraction Framework #

## Prerequisites ##
* Python 2.6 (or Python 2.7 should work probably)
* [xmltodict package](https://github.com/martinblech/xmltodict)
* [subprocess32 package](https://pypi.python.org/pypi/subprocess32)

## Installation ##
Clone this repo to your local machine anywhere
From the project root directory, run:

    python setup.py install --user

(The --user option is optional, I just like to 
install packages only for my user account personally)

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
   # filters should return True for passing or False for failing
   def filter(self, data, dep_results, dict_dep_results):
      success = len(data) > 50
      return success

# All extractors extend the runnables.Extractor class
class TrimmedTextExtractor(runnables.Extractor):
   # If an extractor/filter depends on a previous result
   # define a staticmethod that returns an array of dependencies
   @staticmethod
   def dependencies():
      return [HasContentFilter]

   # override the extract method to define extraction logic
   # the extract method should return a string, xml string, or dict
   # if there's a failure along the way, it can raise a RunnableError('with a message')
   def extract(self, data, dep_results, dict_dep_results):
      return data[:-1]

# Create and run the whole extraction process
runner = ExtractionRunner()
runner.add_runnable(HasContentFilter)
runner.add_runnable(TrimmedTextExtractor)

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
